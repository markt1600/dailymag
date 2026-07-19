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
built_dt = (datetime.datetime.fromisoformat(built_at) if built_at
            else datetime.datetime.now(SGT))

# Wall-clock build time: setup.sh stamps build/.session-start when the session
# opens (≈ when the Routine fired and research began). Sanity-bounded so a
# stale stamp from a long-lived interactive session can't report nonsense.
started_at = build_minutes = None
stamp = pathlib.Path("build/.session-start")
if stamp.exists():
    try:
        t0 = datetime.datetime.fromisoformat(stamp.read_text().strip())
        mins = (built_dt - t0).total_seconds() / 60
        if 0 < mins < 360:
            started_at = t0.astimezone(SGT).isoformat(timespec="seconds")
            build_minutes = round(mins)
    except ValueError:
        pass

status = {
    "publication": "MERIDIAN",
    "issue": issue,
    "date": date,
    "isoDate": iso_date,
    "builtAt": built_dt.isoformat(timespec="seconds"),
    "startedAt": started_at,
    "buildMinutes": build_minutes,
    "pages": pages,
    "qa": "pass",
    "url": "https://dailymag.marktan.ai",
}
out.write_text(json.dumps(status, ensure_ascii=False, indent=1) + "\n")
dur = f", {build_minutes}m build" if build_minutes else ""
print(f"status.json: No. {issue} · {date} ({iso_date}) — {pages}pp, qa=pass{dur}")
