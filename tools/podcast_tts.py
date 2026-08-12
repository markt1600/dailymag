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
import json, os, re, subprocess, sys, time, urllib.request

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
        if attempt < 3:
            wait = 15 * (attempt + 1)
            print(f"  retry in {wait}s after: {e} {detail}")
            time.sleep(wait)
            return tts(batch, voices, key, attempt + 1)
        raise SystemExit(f"TTS failed after retries: {e} {detail}")


def render(issue):
    path = f"podcast/script-{issue}.json"
    if lint(path):
        raise SystemExit("script fails lint; fix before rendering")
    d, turns = load(path)
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY not set")
    voices = {"A": os.environ.get("ELEVEN_VOICE_A", "").strip() or VOICE_DEFAULTS["A"],
              "B": os.environ.get("ELEVEN_VOICE_B", "").strip() or VOICE_DEFAULTS["B"]}
    batches = chunk(turns)
    print(f"rendering {len(turns)} turns in {len(batches)} dialogue requests…")
    os.makedirs("build/pod", exist_ok=True)
    parts = []
    for i, b in enumerate(batches):
        p = f"build/pod/part-{i:03d}.mp3"
        audio = tts(b, voices, key)
        with open(p, "wb") as f:
            f.write(audio)
        parts.append(p)
        print(f"  part {i + 1}/{len(batches)} ({sum(len(t['t']) for t in b)} chars, "
              f"{len(audio) // 1024}kB)")
    listing = "build/pod/list.txt"
    with open(listing, "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    out = f"podcast/meridian-{issue}.mp3"
    os.makedirs("podcast", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", listing, "-c:a", "libmp3lame", "-b:a", "128k", out], check=True)
    dur = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                          "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
    print(f"wrote {out} ({float(dur or 0) / 60:.1f} min)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--check"]:
        sys.exit(lint(args[1]))
    elif args[:1] == ["--issue"]:
        render(args[1])
    else:
        sys.exit(__doc__)
