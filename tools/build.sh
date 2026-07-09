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
echo "== archive manifest =="    ; python3 tools/build_manifest.py "$NN"  # (run extract_state.py first so the new issue is included + searchable)
echo "== photo edition =="       ; python3 tools/make_photo_edition.py "$H" build/index.html "$NN" "$DATE"
echo "== stories feed =="         ; python3 tools/build_feed.py build/index.html build/feed.json  # for marktan.ai
echo "== status beacon =="        ; python3 tools/build_status.py build/index.html "$P" build/status.json  # marktan.ai's "did it run?" tile
echo
echo "OK — review build/sheet-*.png, then place deliverables and commit."
echo "Place: cp build/meridian${NN}.pdf meridian-latest.pdf ; cp build/index.html index.html ; cp build/feed.json feed.json ; cp build/status.json status.json"
echo "Reminder: archive the OUTGOING issue BEFORE overwriting root — run tools/archive.py while root still holds it."
