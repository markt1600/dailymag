#!/usr/bin/env python3
"""Emit status.json — a tiny build-health beacon for the edition.

marktan.ai fetches this from raw.githubusercontent and shows a one-line
pipeline tile: "MERIDIAN No. 38 · built 06:47 · 24pp · QA clean" — and turns
amber/red when today's issue hasn't appeared by the dashboard's 07:15 refresh.
So the mere existence of a *today-dated* status.json is the "the Routine ran"
signal the site keys on.

Runs at the END of build.sh, i.e. strictly after the QA gate — if QA had
failed, the build would have aborted and this file would never be written.
That's why qa is always "pass" here; a red tile means "no build landed",
not "a bad build landed".

Usage:  python3 tools/build_status.py [index.html] [pdf] [status.json] [built_at_iso]
        built_at_iso is for backfills only; defaults to now (SGT).
"""
import re, sys, json, pathlib, datetime, subprocess

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
pdf = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "meridian-latest.pdf")
out = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else "status.json")
built_at = sys.argv[4] if len(sys.argv) > 4 else None

html = src.read_text()

# issue number + human date (same anchors as build_feed.py)
issue = date = None
m = re.search(r'No\.\s*(\d{1,3})\s*·\s*(\d{1,2}\s+\w+\s+\d{4})', html)
if m:
    issue, date = int(m.group(1)), m.group(2)
else:
    m = re.search(r'No\.?\s*(\d{1,3})\s*(?:&middot;|·)\s*Singapore', html)
    issue = int(m.group(1)) if m else None
    m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', html)
    date = m.group(1) if m else None

iso_date = None
if date:
    try:
        iso_date = datetime.datetime.strptime(date, "%d %B %Y").date().isoformat()
    except ValueError:
        pass

# page count from pdfinfo (pypdf intentionally unused — see tools/README.md)
pages = None
try:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, timeout=30)
    pm = re.search(r'^Pages:\s+(\d+)', info.stdout, re.M)
    pages = int(pm.group(1)) if pm else None
except Exception:
    pass

SGT = datetime.timezone(datetime.timedelta(hours=8))
status = {
    "publication": "MERIDIAN",
    "issue": issue,
    "date": date,
    "isoDate": iso_date,
    "builtAt": built_at or datetime.datetime.now(SGT).isoformat(timespec="seconds"),
    "pages": pages,
    "qa": "pass",
    "url": "https://dailymag.marktan.ai",
}
out.write_text(json.dumps(status, ensure_ascii=False, indent=1) + "\n")
print(f"status.json: No. {issue} · {date} ({iso_date}) — {pages}pp, qa=pass")
