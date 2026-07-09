#!/usr/bin/env python3
"""Archive the OUTGOING edition before a new one overwrites the repo root.

Run this at the start of building a new issue, while root still holds the
previous one: it snapshots the current root `index.html` + `meridian-latest.pdf`
into `archive/no-<prev>/` (a self-contained, browsable time capsule), then the
new issue can overwrite root. Rebuild the manifest afterwards with
`build_manifest.py` (once the new issue is in the Issue Log).

The issue number is read from the root index.html's cover topbar unless passed.

Usage:  python3 tools/archive.py [prev_no]
"""
import re, sys, shutil, pathlib

root = pathlib.Path(".")
idx = root / "index.html"
pdf = root / "meridian-latest.pdf"

if not idx.exists():
    sys.exit("no root index.html to archive")

if len(sys.argv) > 1:
    no = int(sys.argv[1])
else:
    html = idx.read_text()
    m = re.search(r'No\.?\s*(\d{1,3})\s*(?:&middot;|&nbsp;|·|\s)*Singapore', html)
    if not m:
        sys.exit("could not read issue number from index.html; pass it explicitly")
    no = int(m.group(1))

d = root / "archive" / f"no-{no}"
d.mkdir(parents=True, exist_ok=True)
shutil.copy2(idx, d / "index.html")
did_pdf = False
if pdf.exists():
    shutil.copy2(pdf, d / "meridian-latest.pdf")
    did_pdf = True
print(f"archived No. {no} -> {d}/index.html" + ("  + meridian-latest.pdf" if did_pdf else "  (no PDF)"))
print("next: build the new issue, update the ledgers, then run tools/build_manifest.py <newno>")
