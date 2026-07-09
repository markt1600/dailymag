#!/usr/bin/env bash
# MERIDIAN one-command build driver for a staged edition.
# Assumes build/meridianNN.html already assembled (+ meridian.css copied beside it).
# Runs: validate -> render PDF -> QA gate -> derive Photo Edition.
# On a clean QA pass, place deliverables with:
#     cp build/meridianNN.pdf meridian-latest.pdf && cp build/index.html index.html
# then update the ledgers, run tools/extract_state.py, and commit.
set -eu
NN="${1:?usage: tools/build.sh <NN> [date]}"
DATE="${2:-}"
H="build/meridian${NN}.html"
P="build/meridian${NN}.pdf"

cp -f meridian.css build/meridian.css 2>/dev/null || true
echo "== validate =="            ; python3 tools/validate.py "$H"
echo "== render =="              ; python3 tools/render.py "$H" "$P"
echo "== QA gate =="             ; python3 tools/qa.py "$H" "$P"      # non-zero exit blocks on collision
echo "== photo edition =="       ; python3 tools/make_photo_edition.py "$H" build/index.html "$NN" "$DATE"
echo
echo "OK — review build/sheet-*.png, then place deliverables and commit."
