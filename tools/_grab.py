#!/usr/bin/env python3
"""Fetch a hero image straight into assets/heroes/<slug>.jpg (sandbox has egress).
usage: python3 tools/_grab.py <slug> <url|commons:File Name.jpg> [width]
Prints the saved path + dimensions so the build session can eyeball it.
"""
import sys, os, subprocess, urllib.request, urllib.parse, pathlib
UA = {"User-Agent": "MeridianHeroFetch/1.1 (https://github.com/markt1600/dailymag; bakery-issue-images)",
      "Accept": "image/*,*/*;q=0.8"}
slug, src = sys.argv[1], sys.argv[2]
width = sys.argv[3] if len(sys.argv) > 3 else "1600"
if src.startswith("commons:"):
    fn = src[len("commons:"):]
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fn.replace("_", " ")) + "?width=" + width
else:
    url = src
root = pathlib.Path(__file__).resolve().parent.parent
out = root / "assets" / "heroes" / (slug + ".jpg")
import time
data = None
last = None
for attempt in range(6):
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
        break
    except Exception as e:
        last = e
        code = getattr(e, "code", None)
        if code in (429, 503) or code is None:
            time.sleep(4 * (attempt + 1))
            continue
        raise
if data is None:
    raise SystemExit(f"FETCH FAILED {slug}: {last}")
tmp = root / "build" / ("_" + slug + ".bin")
tmp.parent.mkdir(exist_ok=True)
tmp.write_bytes(data)
# normalise to baseline jpeg, cap width
subprocess.run(["convert", str(tmp) + "[0]", "-auto-orient", "-resize", "1800x1800>",
                "-quality", "88", "-strip", str(out)], check=True)
tmp.unlink()
d = subprocess.run(["identify", "-format", "%wx%h %b", str(out)], capture_output=True, text=True).stdout
print(f"OK {out.relative_to(root)}  {d}")
