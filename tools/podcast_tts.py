#!/usr/bin/env python3
"""Render a Meridian Briefing script to audio via ElevenLabs Text-to-Dialogue.

Usage:
  python3 tools/podcast_tts.py --check podcast/script-NN.json   # lint only (no API)
  python3 tools/podcast_tts.py --issue NN                        # render podcast/meridian-NN.mp3

The build session runs --check; only .github/workflows/generate-podcast.yml
runs a render (it holds the ELEVENLABS_API_KEY secret). Dialogue is batched
into <=1,800-char requests (the API's reliable ceiling is ~2,000), each batch
keeping whole consecutive turns, then stitched with ffmpeg.

Env (render mode): ELEVENLABS_API_KEY (required); ELEVEN_VOICE_A / ELEVEN_VOICE_B
(voice IDs for hosts A/B; defaults: Rachel / George premades).
"""
import json, os, re, shutil, subprocess, sys, time, urllib.request

MAX_CHUNK = 1800
MODEL = "eleven_v3"
OUT_FMT = "mp3_44100_128"
ALLOWED_TAGS = {"laughs", "chuckles", "sighs", "curious", "excited", "whispers", "pause"}
VOICE_DEFAULTS = {"A": "21m00Tcm4TlvDq8ikWAM",   # Rachel — CLAIRE
                  "B": "JBFqnCBsd6RMkjVDRZzb"}   # George — THEO


def load(path):
    with open(path) as f:
        d = json.load(f)
    turns = d.get("turns") or []
    assert d.get("show") == "The Meridian Briefing", "show name drifted"
    assert d.get("issue") and d.get("hosts"), "missing issue/hosts"
    assert all(t.get("s") in ("A", "B") and t.get("t", "").strip() for t in turns), "bad turn"
    return d, turns


def lint(path):
    d, turns = load(path)
    words = sum(len(t["t"].split()) for t in turns)
    problems = []
    if not (2600 <= words <= 3900):
        problems.append(f"word count {words} outside 2600-3900 (~17-24 min)")
    if not (100 <= len(turns) <= 200):
        problems.append(f"{len(turns)} turns outside 100-200")
    tags = re.findall(r"\[([^\]]+)\]", " ".join(t["t"] for t in turns))
    bad = [g for g in tags if g not in ALLOWED_TAGS]
    if bad:
        problems.append(f"disallowed audio tags: {sorted(set(bad))}")
    if len(tags) > 30:
        problems.append(f"{len(tags)} audio tags (> 30) — use them sparingly")
    digits = [t["t"] for t in turns if re.search(r"\d", t["t"])]
    if digits:
        problems.append(f"{len(digits)} turn(s) contain digits — spell numbers out "
                        f"(first: {digits[0][:70]!r})")
    long_turns = [t["t"] for t in turns if len(t["t"]) > MAX_CHUNK]
    if long_turns:
        problems.append(f"{len(long_turns)} turn(s) exceed {MAX_CHUNK} chars")
    opener = turns[0]["t"] if turns else ""
    if "Meridian Briefing" not in opener:
        problems.append("cold open is missing the standing show line")
    for p in problems:
        print("LINT:", p)
    print(f"{'FAIL' if problems else 'OK'}: {len(turns)} turns, {words} words, {len(tags)} tags")
    return 1 if problems else 0


def chunk(turns):
    batches, cur, size = [], [], 0
    for t in turns:
        n = len(t["t"])
        if cur and size + n > MAX_CHUNK:
            batches.append(cur)
            cur, size = [], 0
        cur.append(t)
        size += n
    if cur:
        batches.append(cur)
    return batches


def tts(batch, voices, key, attempt=0):
    body = json.dumps({
        "inputs": [{"text": t["t"], "voice_id": voices[t["s"]]} for t in batch],
        "model_id": MODEL,
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-dialogue?output_format={OUT_FMT}",
        data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.read()
    except Exception as e:
        detail = getattr(e, "read", lambda: b"")()[:300]
        # Auth/quota/bad-request errors won't fix themselves on retry — fail
        # fast with a clear message instead of burning the backoff budget.
        status = getattr(e, "code", None)
        if status in (400, 401, 403):
            hint = ""
            if b"api_key_id_used_as_api_key" in detail or b"invalid_api_key" in detail:
                hint = ("\n  >>> The ELEVENLABS_API_KEY secret is wrong: it looks like a key ID, "
                        "not the secret key. Create/rotate a key in ElevenLabs and copy the value "
                        "that STARTS WITH 'sk_' (shown only once), then update the GitHub secret.")
            raise SystemExit(f"TTS auth/request error (HTTP {status}) — not retrying: {detail.decode('utf-8','replace')}{hint}")
        if attempt < 3:
            wait = 15 * (attempt + 1)
            print(f"  retry in {wait}s after: {e} {detail}")
            time.sleep(wait)
            return tts(batch, voices, key, attempt + 1)
        raise SystemExit(f"TTS failed after retries: {e} {detail}")


def mock_silence(chars):
    # A valid silent MPEG-1 Layer III frame: 44.1kHz, 128kbps, mono, no padding
    # (frame length 417 bytes). Header FF FB 90 40, then zeroed side-info + data
    # decodes as silence; players concatenate frames happily. Repeat to roughly
    # match real timing (~15 chars/sec => 38.28 frames/sec).
    frame = b"\xff\xfb\x90\x40" + b"\x00" * 413
    seconds = max(2.0, chars / 15.0)
    n = int(seconds * 44100 / 1152) + 1     # 1152 samples per MPEG1-L3 frame
    return frame * n


def render(issue):
    path = f"podcast/script-{issue}.json"
    if lint(path):
        raise SystemExit("script fails lint; fix before rendering")
    d, turns = load(path)
    # MOCK MODE (PODCAST_MOCK=1): render SILENCE locally instead of calling
    # ElevenLabs — proves the whole render->stitch->commit->player chain for
    # ZERO credits. Voice quality is the only thing it can't test, and that's
    # the only part already known to work.
    mock = os.environ.get("PODCAST_MOCK", "").strip() in ("1", "true", "yes")
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key and not mock:
        raise SystemExit("ELEVENLABS_API_KEY not set")
    voices = {"A": os.environ.get("ELEVEN_VOICE_A", "").strip() or VOICE_DEFAULTS["A"],
              "B": os.environ.get("ELEVEN_VOICE_B", "").strip() or VOICE_DEFAULTS["B"]}
    batches = chunk(turns)
    print(f"{'MOCK-' if mock else ''}rendering {len(turns)} turns in {len(batches)} dialogue requests…")
    os.makedirs("build/pod", exist_ok=True)
    parts = []
    for i, b in enumerate(batches):
        p = f"build/pod/part-{i:03d}.mp3"
        audio = mock_silence(sum(len(t["t"]) for t in b)) if mock else tts(b, voices, key)
        with open(p, "wb") as f:
            f.write(audio)
        parts.append(p)
        print(f"  {'MOCK ' if mock else ''}part {i + 1}/{len(batches)} "
              f"({sum(len(t['t']) for t in b)} chars, {len(audio) // 1024}kB)")
    out = f"podcast/meridian-{issue}.mp3"
    os.makedirs("podcast", exist_ok=True)
    # Stitch the parts. Prefer ffmpeg (clean concat), but the parts are all the
    # SAME ElevenLabs mp3 profile (44.1k / 128k CBR), so a raw byte-concat plays
    # fine in every player — use it as the fallback when ffmpeg isn't on the
    # runner (No. 71 rendered all 9 parts then died here on a missing ffmpeg).
    stitched = False
    if shutil.which("ffmpeg"):
        listing = "build/pod/list.txt"
        with open(listing, "w") as f:
            f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                            "-i", listing, "-c:a", "libmp3lame", "-b:a", "128k", out])
        stitched = r.returncode == 0
        if not stitched:
            print("  ffmpeg concat failed — falling back to byte concat")
    if not stitched:
        with open(out, "wb") as o:
            for p in parts:
                with open(p, "rb") as f:
                    o.write(f.read())
        print("  stitched by byte-concat (no ffmpeg re-encode)")
    size = os.path.getsize(out)
    if size < 100_000:
        raise SystemExit(f"stitched file suspiciously small ({size} bytes) — aborting")
    print(f"wrote {out} ({size // 1024}kB from {len(parts)} parts)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--check"]:
        sys.exit(lint(args[1]))
    elif args[:1] == ["--issue"]:
        render(args[1])
    else:
        sys.exit(__doc__)
