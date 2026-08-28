#!/usr/bin/env node
// Encrypt a special edition for the public repo. Specials are OWNER-ONLY and
// stored encrypted at rest; the plaintext files are never committed.
//
//   node tools/encrypt_special.mjs 85-5        # encrypts special-85-5.html + .pdf
//   node tools/encrypt_special.mjs special-85-5.html special-85-5.pdf
//
// Scheme: X25519 sealed box (ephemeral-static ECDH → HKDF-SHA256 → AES-256-GCM),
// Node stdlib only. Encryption needs ONLY the committed public key
// (state/specials-pubkey.b64) — no secret ever enters the build sandbox.
// Decryption happens with the private key held solely by marktan.ai
// (env MERIDIAN_SPECIALS_KEY serves the web copies at /api/special) and the
// deliver-special workflow (same value as a GitHub Actions secret, for the
// reMarkable upload). Blob layout: "MSE1" | epk(32) | iv(12) | tag(16) | ct.
//
// HTML is pre-processed before encryption so it works when served from
// marktan.ai: the special's own PDF link points at the /api/special endpoint,
// and embedded archive-manifest paths become absolute dailymag URLs.
// The plaintext file is DELETED after its .enc is written.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const ROOT = path.join(path.dirname(new URL(import.meta.url).pathname), "..");
const PUB = crypto.createPublicKey({
  key: Buffer.from(fs.readFileSync(path.join(ROOT, "state/specials-pubkey.b64"), "utf8").trim(), "base64"),
  type: "spki",
  format: "der",
});

export function seal(plain, publicKey = PUB) {
  const eph = crypto.generateKeyPairSync("x25519");
  const shared = crypto.diffieHellman({ privateKey: eph.privateKey, publicKey });
  const epk = eph.publicKey.export({ type: "spki", format: "der" }).subarray(-32); // raw 32-byte key
  const key = crypto.hkdfSync("sha256", shared, Buffer.alloc(0), Buffer.concat([Buffer.from("meridian-special-v1"), epk]), 32);
  const iv = crypto.randomBytes(12);
  const c = crypto.createCipheriv("aes-256-gcm", Buffer.from(key), iv);
  const ct = Buffer.concat([c.update(plain), c.final()]);
  return Buffer.concat([Buffer.from("MSE1"), epk, iv, c.getAuthTag(), ct]);
}

function prepHtml(name, html) {
  const pdf = name.replace(/\.html$/, ".pdf");
  return html
    .replaceAll(`href="${pdf}"`, `href="https://www.marktan.ai/api/special?file=${pdf}"`)
    .replaceAll('"archive/no-', '"https://dailymag.marktan.ai/archive/no-');
}

function run(files) {
  for (const f of files) {
    const p = path.join(ROOT, f);
    if (!fs.existsSync(p)) { console.error(`  missing: ${f} — skipped`); continue; }
    let data = fs.readFileSync(p);
    if (f.endsWith(".html")) data = Buffer.from(prepHtml(f, data.toString("utf8")), "utf8");
    fs.writeFileSync(p + ".enc", seal(data));
    fs.unlinkSync(p);
    console.log(`  encrypted ${f} -> ${f}.enc (${fs.statSync(p + ".enc").size} bytes), plaintext removed`);
  }
}

const args = process.argv.slice(2);
if (import.meta.url === `file://${process.argv[1]}`) {
  if (!args.length) { console.error("usage: encrypt_special.mjs <NN-5 | special-NN-5.html [special-NN-5.pdf]>"); process.exit(1); }
  const files = /^\d+-\d+$/.test(args[0])
    ? [`special-${args[0]}.html`, `special-${args[0]}.pdf`]
    : args;
  run(files);
}
