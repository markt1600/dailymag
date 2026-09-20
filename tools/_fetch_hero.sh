#!/usr/bin/env bash
# usage: tools/_fetch_hero.sh <slug> <url>
# fetches a hero image directly into assets/heroes/<slug>.jpg (full egress)
set -u
slug="$1"; url="$2"
out="assets/heroes/${slug}.jpg"
tmp="$(mktemp /tmp/hero.XXXXXX)"
code=$(curl -sS -L --max-time 45 \
  -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" \
  -H "Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8" \
  -o "$tmp" -w "%{http_code}" "$url" 2>/dev/null)
ct=$(file -b --mime-type "$tmp")
if [[ "$code" == "200" && "$ct" == image/* ]]; then
  python3 - "$tmp" "$out" <<'PY'
import sys
from PIL import Image
src,dst=sys.argv[1],sys.argv[2]
im=Image.open(src); im.load()
if im.mode not in ("RGB","L"): im=im.convert("RGB")
w,h=im.size
if w<400 or h<250:
    print(f"TOO_SMALL {w}x{h}"); sys.exit(3)
if w>2000: im=im.resize((2000,int(h*2000/w)), Image.LANCZOS)
im.save(dst,"JPEG",quality=88,optimize=True)
print(f"OK {im.size[0]}x{im.size[1]}")
PY
  rc=$?
  rm -f "$tmp"
  [[ $rc -eq 0 ]] && echo "FETCHED $slug" || echo "REJECT $slug (rc=$rc)"
else
  rm -f "$tmp"
  echo "FAIL $slug http=$code type=$ct"
fi
