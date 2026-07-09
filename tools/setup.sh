#!/usr/bin/env bash
# MERIDIAN build-environment setup — idempotent; safe to run every session.
# Verifies/install the render + QA toolchain so a fresh web session is
# build-ready without manual steps. Wired to run at SessionStart (see
# .claude/settings.json). Prints a one-line readiness summary.
set -u
log(){ printf '  %s\n' "$*"; }

need_py=0
python3 - <<'PY' 2>/dev/null || need_py=1
import playwright, PIL  # noqa (pypdf omitted: system cryptography conflict; we use pdfinfo)
PY
if [ "$need_py" = 1 ]; then
  log "installing python deps (playwright, pillow)…"
  pip install --quiet playwright pillow >/dev/null 2>&1 || pip install --quiet --break-system-packages playwright pillow >/dev/null 2>&1
fi

# poppler (pdftoppm/pdfinfo) + imagemagick (montage) for the QA raster/contact sheets
if ! command -v pdftoppm >/dev/null 2>&1 || ! command -v montage >/dev/null 2>&1; then
  log "installing poppler-utils + imagemagick…"
  (sudo apt-get update -qq && sudo apt-get install -y -qq poppler-utils imagemagick) >/dev/null 2>&1 || true
fi

# Lora + Poppins (local fonts so the render matches the brand exactly)
if [ "$(fc-list 2>/dev/null | grep -ciE 'lora|poppins')" -lt 4 ]; then
  log "fetching Lora + Poppins…"
  d=/usr/local/share/fonts/meridian; mkdir -p "$d" 2>/dev/null || d="$HOME/.fonts/meridian"; mkdir -p "$d"
  base=https://raw.githubusercontent.com/google/fonts/main/ofl
  for f in "lora/Lora%5Bwght%5D.ttf" "lora/Lora-Italic%5Bwght%5D.ttf" \
           "poppins/Poppins-Regular.ttf" "poppins/Poppins-Medium.ttf" \
           "poppins/Poppins-SemiBold.ttf" "poppins/Poppins-Bold.ttf" "poppins/Poppins-Italic.ttf"; do
    curl -sfL "$base/$f" -o "$d/$(basename "$f")" 2>/dev/null || true
  done
  fc-cache -f >/dev/null 2>&1 || true
fi

# Chromium: prefer the pre-installed sandbox browser; export for render.py/qa.py
if [ -x /opt/pw-browsers/chromium ]; then export PW_CHROMIUM=/opt/pw-browsers/chromium; fi

# Stamp when this session began (≈ when the Routine fired and research started).
# build_status.py reads it to report the wall-clock build time in status.json;
# write-once so re-running setup mid-session doesn't shrink the number.
mkdir -p build
[ -f build/.session-start ] || date -u +%Y-%m-%dT%H:%M:%S+00:00 > build/.session-start

# readiness summary
ok_py=$(python3 -c 'import playwright,PIL;print("ok")' 2>/dev/null || echo "MISSING")
ok_pop=$(command -v pdftoppm >/dev/null 2>&1 && echo ok || echo MISSING)
ok_im=$(command -v montage  >/dev/null 2>&1 && echo ok || echo MISSING)
ok_ft=$([ "$(fc-list 2>/dev/null | grep -ciE 'lora|poppins')" -ge 4 ] && echo ok || echo MISSING)
ok_cr=$([ -x "${PW_CHROMIUM:-/opt/pw-browsers/chromium}" ] && echo ok || echo "default")
echo "MERIDIAN toolchain — python:$ok_py poppler:$ok_pop imagemagick:$ok_im fonts:$ok_ft chromium:$ok_cr"
