#!/usr/bin/env python3
"""Emit feed.json — a compact, machine-readable feed of the edition's top
stories, derived by PARSING the finished Photo Edition (index.html). Nothing
about the research or writing changes; the feed falls out of the edition, the
way the archive manifest falls out of the ledger.

Downstream (marktan.ai) fetches this from raw.githubusercontent and maps the
desk leads into its Stories & Briefs — so it reuses MERIDIAN's already-done
research instead of running its own web search. Each story carries the desk's
`#pN` anchor so the site can deep-link back to that desk.

Usage:  python3 tools/build_feed.py [index.html] [feed.json]
"""
import re, sys, json, pathlib, datetime

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "feed.json")
html = src.read_text()

# desk -> a marktan-friendly category label
CATEGORY = {
    "The World": "World", "Singapore": "Asia", "Property": "Property",
    "Technology": "Tech", "The Kit": "Gadgets", "The Connected Home": "Smart Home",
    "The Good Life": "Design", "Screen & Sound": "Culture", "The Family Desk": "Family",
    "The Macro Desk": "Markets", "Curiosities": "Science", "Love & Life": "Life",
    "Fitness": "Health", "The Diary": "Events", "The Travel Desk": "Travel",
    "The Long Read": "Essay",
}


def strip(s):
    s = re.sub(r'<sup class="fnref">\d+</sup>', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'&amp;', '&', s).replace('&nbsp;', ' ').replace('&middot;', '·')
    return re.sub(r'\s+', ' ', s).strip()


# issue number + date from the download bar or cover topbar
issue = date = None
m = re.search(r'No\.\s*(\d{1,3})\s*·\s*(\d{1,2}\s+\w+\s+\d{4})', html)
if m:
    issue, date = int(m.group(1)), m.group(2)
else:
    m = re.search(r'No\.?\s*(\d{1,3})\s*(?:&middot;|·)\s*Singapore', html)
    issue = int(m.group(1)) if m else None
    m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', html)
    date = m.group(1) if m else None

# "From the Desk" quote (contents page)
quote = None
qm = re.search(r'From the Desk</div>\s*<p[^>]*>(.*?)</p>\s*<p class="src">(.*?)</p>', html, re.S)
if qm:
    quote = {"text": strip(qm.group(1)).strip('"“”'), "author": strip(qm.group(2)).lstrip('—- ')}

# one lead story per desk, in page order (first page of each desk)
stories, seen = [], set()
for sec in re.split(r'(?=<section id="p\d+" class="page)', html):
    mid = re.match(r'<section id="p(\d+)" class="page(\s+dark)?"', sec)
    if not mid:
        continue
    anchor, dark = "p" + mid.group(1), bool(mid.group(2))
    if dark:                       # cover / back cover
        continue
    rh = re.search(r'<div class="rh"><span>(?:<span[^>]*>[^<]*</span>\s*)?Meridian\s*·\s*([^<]+)</span><span>([^<]*)</span>', sec)
    if not rh:                     # contents page has an .rh too, but no .hed lead we want
        continue
    desk = strip(rh.group(1))
    sub = strip(rh.group(2))
    if desk in seen or desk in ("Contents",):
        continue
    hed = re.search(r'<div class="hed[^"]*">(.*?)</div>', sec, re.S)
    dek = re.search(r'<div class="dek">(.*?)</div>', sec, re.S)
    kicker = re.search(r'<div class="kicker[^"]*">(.*?)</div>', sec, re.S)
    if not hed:
        continue
    seen.add(desk)
    stories.append({
        "desk": desk, "sub": sub,
        "category": CATEGORY.get(desk, desk),
        "kicker": strip(kicker.group(1)) if kicker else "",
        "headline": strip(hed.group(1)),
        "dek": strip(dek.group(1)) if dek else "",
        "anchor": anchor,
    })

# cover teasers = the editor's top-3 pick; mark those desks featured and sort first.
# The cover is the first page, so the first three .lbl in document order are its teasers.
tlabels = [strip(t) for t in re.findall(r'<div class="lbl"[^>]*>([^<]+)</div>', html)[:3]]
def is_featured(desk):
    for t in tlabels:
        tl = t.lower()
        if tl in desk.lower() or desk.lower() in tl or any(w in desk.lower() for w in tl.split(" & ")):
            return True
    return False
for s in stories:
    s["featured"] = is_featured(s["desk"])
stories.sort(key=lambda s: (not s["featured"],))       # featured first, stable otherwise

feed = {
    "publication": "MERIDIAN",
    "issue": issue,
    "date": date,
    "generated": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="seconds"),
    "quote": quote,
    "stories": stories,
}
out.write_text(json.dumps(feed, ensure_ascii=False, indent=1))
print(f"feed.json: No. {issue} · {date} — {len(stories)} desk leads, quote={'yes' if quote else 'no'}")
