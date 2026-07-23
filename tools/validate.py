#!/usr/bin/env python3
"""MERIDIAN pre-flight validator — catches the manual-bookkeeping errors that
hand-assembled editions are prone to, before render:

  * Footnote integrity per page: every .fnref marker 1..k has a matching source
    entry, numbering starts at 1 and has no gaps/dups. (I had to hand-renumber
    page 3's sources after cutting a paragraph — this catches that.)
  * Cross-reference sanity: 'p<NN>' / 'Page <NN>' references point to pages that
    exist (1..pagecount).
  * Structural: exactly one <link rel="stylesheet" href="meridian.css"> (print
    build) or an inline <style> (photo edition); page count sane.

Usage:  python3 tools/validate.py build/meridianNN.html
Exit non-zero on any error so the build can stop. Warnings don't stop the build.
"""
import sys, re, pathlib

html = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/meridian.html").read_text()

# split into page sections (each <section ... class="page ...">...)
sections = re.split(r'(?=<section[^>]*\bclass="page)', html)
pages = [s for s in sections if re.match(r'<section[^>]*\bclass="page', s)]
errors, warns = [], []

npages = len(pages)
if not (20 <= npages <= 32):
    warns.append(f"page count {npages} outside the usual 23-28")

for idx, sec in enumerate(pages, 1):
    # footnote markers actually rendered in the body
    markers = [int(m) for m in re.findall(r'<sup class="fnref">(\d+)</sup>', sec)]
    # source list: leading "1 ... 2 ... 3 ..." inside the .fn block
    fnblock = re.search(r'<div class="fn">(.*?)</div>', sec, re.S)
    src_nums = []
    if fnblock:
        # numbers that start a source entry: after "SOURCES ·" then "1 ... 2 ..."
        src_nums = [int(m) for m in re.findall(r'(?<![\d.])\b(\d{1,2})\s', fnblock.group(1))]
    if markers:
        uniq = sorted(set(markers))
        # numbering should be 1..max with no gaps
        expected = list(range(1, max(uniq) + 1))
        if uniq != expected:
            errors.append(f"page {idx}: footnote markers {uniq} are not a gapless 1..{max(uniq)} sequence")
        # every marker should have a source entry number
        missing = [m for m in uniq if m not in set(src_nums)]
        if missing and fnblock:
            warns.append(f"page {idx}: markers {missing} have no obvious matching SOURCES entry (verify)")

# column discipline: interior body copy must live in columns (.cols2/.cols3 or
# a .grid cell), never run the full A4 measure — full-width paragraphs are the
# single most magazine-breaking layout drift (reader-reported, No. 50 era).
# Escape hatch for a deliberate feature opener: class="body fullmeasure".
from html.parser import HTMLParser
class _ColScan(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.page=0; self.bad={}
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        if tag == 'section' and 'page' in cls.split(): self.page += 1
        self.stack.append((tag, cls))
        if tag == 'p' and 'body' in cls.split() and 'fullmeasure' not in cls.split():
            if self.page in (1,): return  # cover exempt
            in_col = any(any(k in c.split() for k in ('cols2','cols3','grid'))
                         for _, c in self.stack[:-1])
            if not in_col:
                self.bad[self.page] = self.bad.get(self.page, 0) + 1
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag: del self.stack[i]; break
_cs = _ColScan(); _cs.feed(html)
if _cs.bad:
    errors.append("full-width body copy (not in .cols2/.cols3/.grid) on page(s) "
                  + ", ".join(f"{p} ({n}×)" for p, n in sorted(_cs.bad.items()))
                  + " — set interior body in columns like a magazine, or mark a deliberate opener with class=\"body fullmeasure\"")

# house-style regression gate: structural fingerprints of a real MERIDIAN
# (calibrated on No. 38; floors ~50-60% so weekday AND weekend books pass).
# No. 50-era drift shipped 0 figframes and 0 brief strips — these floors
# make that impossible to ship again.
STYLE_FLOORS = [
    ('class="chatter',   18, "chatter boxes"),
    ('chatter slate',     8, "sceptic/contrarian (.chatter.slate) boxes"),
    ('class="stat',      14, ".stat callouts"),
    ('class="pull',       4, ".pull quotes"),
    ('class="desk',       2, "viewpoint (.desk) panels on The World"),
    ('body dropcap',      8, "dropcaps"),
    ('class="figframe',   2, "figframes (original SVG figures)"),
    ('class="brief-h',    8, '"in brief"/"still on the shelf" strips (.brief-h)'),
    ('fnref',            60, "footnote markers"),
]
for needle, floor, label in STYLE_FLOORS:
    n = html.count(needle)
    if n < floor:
        errors.append(f"house style: only {n} {label} (floor {floor}) — the book is under-furnished; add real, sourced material per the density discipline")

# per-desk research receipts: every desk must carry the residue of the
# three-pass protocol — a chatter box (pass 2: the community read), a slate
# sceptic/contrarian box (pass 3: the cross-examination), and real footnote
# density. Cover/contents/back cover exempt; the Long Read is exempt from
# chatter/slate (its furniture is pulls + sources) but not from footnotes.
_desk_pages = {}
for _i, _sec in enumerate(pages, 1):
    _m = re.search(r'<div class="rh"><span><span class="dot">●</span> Meridian · ([^<]+)</span>', _sec)
    if not _m:
        continue
    _desk = _m.group(1).strip()
    if _desk in ('Contents',):
        continue
    _desk_pages.setdefault(_desk, []).append(_sec)
for _desk, _secs in _desk_pages.items():
    _blob = ''.join(_secs)
    _fn = len(re.findall(r'<sup class="fnref">', _blob))
    if _fn < 4:
        errors.append(f"desk '{_desk}': only {_fn} footnote markers across its pages (floor 4) — verification residue missing")
    if _desk == 'The Long Read':
        continue
    if _blob.count('class="chatter') < 1:
        errors.append(f"desk '{_desk}': no Chatter box — the pass-2 community read is missing")
    if _blob.count('chatter slate') < 1:
        errors.append(f"desk '{_desk}': no sceptic/contrarian (.chatter.slate) box — the pass-3 cross-examination is missing")

# page-two feature rotation (from No. 51): Friday needs The Meridian Index,
# Saturday needs The Scoreboard. Weekday read from the cover's date line.
_issm = re.search(r'No\.\s*(\d{1,3})\s*·\s*Singapore', html)
_issno = int(_issm.group(1)) if _issm else 0
_daym = re.search(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', pages[0] if pages else '')
_day = _daym.group(1) if _daym else ''
if _issno >= 51:
    if _day == 'Friday' and 'The Meridian Index' not in html:
        errors.append("Friday issue is missing 'The Meridian Index' page-two feature (see THE PAGE-TWO FEATURE)")
    if _day == 'Saturday' and 'The Scoreboard' not in html:
        errors.append("Saturday issue is missing 'The Scoreboard' page-two feature (see PREDICTIONS PROTOCOL)")

# voice card: banned-tic counts (warn) + phrase recycling vs archived issues (warn)
_text = re.sub(r'<[^>]+>', ' ', html).lower()
for _tic in ('is the story', 'the arithmetic', 'writes itself', 'the tell is', 'in one sentence', 'quietly became', 'does the pre-selling'):
    _n = _text.count(_tic)
    if _n > 1:
        warns.append(f"voice: banned tic '{_tic}' used {_n}× (max 1) — rewrite per the VOICE CARD")
import pathlib as _pl
def _prose(h):
    # editorial prose only: body paragraphs, deks, pulls — not chrome/furniture
    parts = re.findall(r'<p class="body[^"]*">(.*?)</p>', h, re.S)
    parts += re.findall(r'<div class="dek">(.*?)</div>', h, re.S)
    parts += re.findall(r'<div class="pull">(.*?)</div>', h, re.S)
    return re.sub(r'<[^>]+>', ' ', ' '.join(parts)).lower()
_arch = sorted(_pl.Path('archive').glob('no-*/index.html'),
               key=lambda f: int(re.search(r'no-(\d+)', str(f)).group(1)))
_arch = [f for f in _arch if _issno and int(re.search(r'no-(\d+)', str(f)).group(1)) < _issno][-3:]
if _arch:
    _prev = ' '.join(_prose(f.read_text()) for f in _arch if f.exists())
    _words = re.findall(r"[a-z']+", _prose(html))
    _stop = set('the a an of to in on for and or but with as at by from is are was were be it its this that'.split())
    _grams = {' '.join(_words[i:i+4]) for i in range(len(_words)-3)
              if sum(1 for w in _words[i:i+4] if w not in _stop) >= 3}
    _recycled = sorted(g for g in _grams if g in _prev)
    if len(_recycled) > 40:
        _ex = ', '.join(f'"{g}"' for g in _recycled[:5])
        warns.append(f"voice: {len(_recycled)} distinctive 4-word prose phrases recycled from the last 3 issues (e.g. {_ex}) — phrase fatigue; vary the language per the VOICE CARD")

# cross-reference page numbers must exist
for m in re.finditer(r'(?:[,(]\s*(?:see [^,()]{0,40}?,\s*)?p|Page\s)(\d{1,2})\b', html):
    ref = int(m.group(1))
    if ref > npages:
        errors.append(f"cross-reference to p{ref} but the book has only {npages} pages")

# structural
links = html.count('<link rel="stylesheet" href="meridian.css">')
inline = '<style>' in html and ':root{' in html
if not (links == 1 or inline):
    warns.append("neither a single meridian.css <link> (print) nor an inlined stylesheet (photo) found")

for w in warns:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)
if errors:
    print(f"\nvalidate: {len(errors)} error(s), {len(warns)} warning(s) — FAILED")
    sys.exit(1)
print(f"\nvalidate: OK ({npages} pages, {len(warns)} warning(s))")
