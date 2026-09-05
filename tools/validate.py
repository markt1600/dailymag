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
import sys, re, json, pathlib

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

# COLUMN DISCIPLINE + READING ORDER (rebuilt, editor 31 Aug 2026, after a
# reader report on No. 88: p4 crushed the lead into ~38mm columns beside a
# rail, p6 ran the Sceptic, a brief and Next-on-the-Bench as full-width bands,
# p13 left ~90mm of dead white bottom-left in an unbalanced furniture grid.
#
# THE READING-ORDER LAW: an article reads DOWN the left column, then DOWN the
# right. One continuous .cols2 per article at full live-area width; furniture
# flows INSIDE that stream. The previous gate was a regex needing class="grid"
# as the FIRST attribute and .cols2 as its immediate child, so
# <div style="..." class="grid g-12"> with a kicker/hed before the .cols2 sailed
# straight through. This walks the tree instead and cannot be dodged.
# Escape hatch for a deliberate feature opener: class="body fullmeasure".
from html.parser import HTMLParser
class _FlowScan(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.page=0; self.cid=0
        self.fullwidth={}; self.colsingrid={}; self.bodyingrid={}
        self.fragmented={}; self.widefurniture={}; self.furngrid={}
        self._flow=None; self._sawhead=True
    def _bump(self, d): d[self.page]=d.get(self.page,0)+1
    def handle_starttag(self, tag, attrs):
        cls=(dict(attrs).get('class','') or ''); c=set(cls.split())
        if tag=='section' and 'page' in c:
            self.page+=1; self._flow=None; self._sawhead=True
        anc=[set(cc.split()) for _,cc,_ in self.stack]
        incol=any(a & {'cols2','cols3'} for a in anc)
        ingrid=any('grid' in a for a in anc)
        exempt=self.page in (1,2)          # cover + fixed contents layout
        cid=None
        if c & {'cols2','cols3'}:
            self.cid+=1; cid=self.cid
            if ingrid and not exempt: self._bump(self.colsingrid)
        if c & {'hed','kicker','dek'}: self._sawhead=True
        self.stack.append((tag,cls,cid))
        isbody = tag=='p' and 'body' in c and 'fullmeasure' not in c
        isprose = isbody or (tag=='div' and 'brief-item' in c)
        if isprose and self.page!=1:
            if not incol: self._bump(self.fullwidth)
            if ingrid and isbody and not exempt: self._bump(self.bodyingrid)
        if isbody and incol and not exempt:
            own=[ci for _,_,ci in self.stack[:-1] if ci]
            own=own[-1] if own else None
            if own is not None and own!=self._flow:
                if self._flow is not None and not self._sawhead:
                    self._bump(self.fragmented)
                self._flow=own; self._sawhead=False
        if (c & {'stat','chatter','figframe','nexthole'}) and ingrid and not exempt:
            self._bump(self.furngrid)
        if (c & {'nexthole','nextpick'}) and not incol and self.page!=1:
            self._bump(self.widefurniture)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag: del self.stack[i]; break
_fs=_FlowScan(); _fs.feed(html)
def _pl(d): return ", ".join(f"{k} ({v}x)" for k,v in sorted(d.items()))
if _fs.fullwidth:
    errors.append("full-width running prose (not inside .cols2/.cols3) on page(s) " + _pl(_fs.fullwidth)
                  + " — interior copy is set in columns; mark a deliberate opener class=\"body fullmeasure\"")
if _fs.colsingrid:
    errors.append("BODY-MEASURE LAW: .cols2/.cols3 nested inside a .grid track on page(s) " + _pl(_fs.colsingrid)
                  + " — body text is .cols2 at FULL live-area width, never squeezed beside a sidebar rail")
if _fs.bodyingrid:
    errors.append("BODY-MEASURE LAW: running body copy inside a .grid track on page(s) " + _pl(_fs.bodyingrid)
                  + " — grids carry FURNITURE only, never the article")
if _fs.fragmented:
    errors.append("READING-ORDER LAW: article body restarts in a second column flow with no new headline on page(s) "
                  + _pl(_fs.fragmented) + " — one .cols2 per article; it reads down the left column, then down the right")
if _fs.furngrid:
    errors.append("furniture parked in a .grid rail on page(s) " + _pl(_fs.furngrid)
                  + " — stats, chatters and figures flow INSIDE the column stream; a two-track rail cannot balance and blows a hole in the page (No. 88 p13)")
if _fs.widefurniture:
    errors.append("Next-on-the-Bench / .nextpick set at full page width on page(s) " + _pl(_fs.widefurniture)
                  + " — it closes the desk INSIDE the column flow, not as a full-measure band")

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
_issm = re.search(r'No\.\s*(\d{1,3})(?:\.\d)?\s*·\s*Singapore', html)
_issno = int(_issm.group(1)) if _issm else 0
# SPECIAL EDITIONS (No. NN.5): one-topic 24pp deep dives keep the full visual
# system and quality floors but not the daily desk structure — desk-structure
# gates are skipped for them below.
# a special is any decimal issue (NN.5 normally; NN.6+ when a second
# special is commissioned off the same daily — first case: 74.6, the
# Kelly bag, after 74.5 took the .5 slot)
_special = bool(re.search(r'No\.\s*\d+\.\d\s*·\s*Singapore', html))
_daym = re.search(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b', pages[0] if pages else '')
_day = _daym.group(1) if _daym else ''
if _issno >= 51 and not _special:
    if _day == 'Friday' and 'The Meridian Index' not in html:
        errors.append("Friday issue is missing 'The Meridian Index' page-two feature (see THE PAGE-TWO FEATURE)")
    if _day == 'Saturday' and 'The Scoreboard' not in html:
        errors.append("Saturday issue is missing 'The Scoreboard' page-two feature (see PREDICTIONS PROTOCOL)")

if re.search(r'class="cols3"', html):
    errors.append(".cols3 used for body copy — three columns are never the body measure (body-measure law)")

# one vote row per desk/chapter (from No. 74.5): the feedback row is a
# per-SUBJECT vote, so a desk spanning several pages carries exactly one.
# 74.5 shipped a duplicate row on the continuation page of 9 chapters.
_fbd = re.findall(r'class="fbrow" data-desk="([^"]+)"', html)
_fbdup = sorted({d for d in _fbd if _fbd.count(d) > 1})
if _fbdup:
    errors.append(f"{len(_fbdup)} desk(s) carry more than one feedback row ({', '.join(_fbdup[:4])}"
                  f"{'…' if len(_fbdup) > 4 else ''}) — one .fbrow per desk/chapter, on its FIRST page only")

# photographic cover (from No. 52, editor's directive): page 1 must carry a real <img>
if _issno >= 52 and pages and '<img' not in pages[0]:
    errors.append("cover has no photograph — covers are photographic from No. 52 (see the cover brief; SVG fallback must be declared in the Issue Log)")

# voice card: banned-tic counts (warn) + phrase recycling vs archived issues (warn)
# (strip <script> blocks first: the Photo Edition embeds the archive-search
# manifest — old issues' text — inside scripts, which is not this book's prose)
_noscript = re.sub(r'<script\b.*?</script>', ' ', html, flags=re.S | re.I)
_text = re.sub(r'<[^>]+>', ' ', _noscript).lower()
for _tic in ('is the story', 'the arithmetic', 'writes itself', 'the tell is', 'in one sentence', 'quietly became', 'does the pre-selling'):
    _n = _text.count(_tic)
    if _n > 1:
        warns.append(f"voice: banned tic '{_tic}' used {_n}× (max 1) — rewrite per the VOICE CARD")
# retired boilerplate — HARD errors (reader directive, 3 Aug / No. 61): the
# Macro desk must never restate which instruments the reader holds; the daily
# "the two you hold stay VWRA and global bonds; gold and BTC are read for
# sensitivity" recital is banned outright (it also misstated the holdings —
# the reader owns BTC). Analyse the instruments; skip the ownership commentary.
if _issno >= 62:
    for _ban in ('the two you hold', 'you hold stay', 'the reader holds',
                 'read for sensitivity', 'read for their macro sensitivity',
                 'not a recommendation to hold', 'anchors the reader actually holds'):
        if _ban in _text:
            errors.append(f"voice: retired boilerplate '{_ban}' — never restate the reader's holdings in print (reader directive, No. 61)")

# THE CLOSED-SUBJECT GATE (editor, 4 Aug 2026; hard from No. 63): a Coverage
# Ledger subject whose ruling says CLOSED or SATURATED may not appear at
# HEADLINE level (hed/dek/kicker). Body-copy one-line deltas stay legal. To
# legitimately reopen a subject on a genuinely major new peg, UPDATE ITS
# LEDGER ROW FIRST (replace the ruling with the new peg) — this gate reads
# the current row, so an updated ledger clears it; that is the point.
# (Specials are exempt: an ultra-deep-dive request IS the editor reopening it.)
if _issno >= 63 and not _special:
    import json as _json
    try:
        _cov = _json.load(open('state/coverage-ledger.json'))['subjects']
    except (OSError, ValueError, KeyError):
        _cov = []
    _headline = ' '.join(re.findall(
        r'<div class="(?:hed|dek|kicker)[^"]*"[^>]*>(.*?)</div>', html, re.S))
    _headline = re.sub(r'<[^>]+>', ' ', _headline).lower()
    _seen_keys = set()
    for _s in _cov:
        if not re.search(r'^\s*(\*\*)?(CLOSED|SATURATED)\b', _s.get('next_peg', '')):
            continue
        _key = re.sub(r'\s*\(.*?\)', '', _s['subject']).replace('*', '').strip()
        if len(_key) < 6 or _key.lower() in _seen_keys:
            continue
        _seen_keys.add(_key.lower())
        if _key.lower() in _headline:
            errors.append(f"coverage: CLOSED/SATURATED subject '{_key}' at headline level — ruling: "
                          f"{_s['next_peg'][:90]}… To reopen on a genuinely major new peg, update the "
                          "subject's Coverage Ledger row first (ledgers/coverage-ledger.md), then rebuild state")

# THE ATELIER (editor, 15 Aug 2026; from No. 74): the daily maker deep dive
# replaces Property — the retired desk may not reappear; the desk closes with
# exactly 3 "Next on the Bench" vote chips; a category is covered ONCE, ever.
if _issno >= 74 and not _special:
    if 'Property' in _desk_pages or 'Bricks & Mortar' in html or 'Bricks &amp; Mortar' in html:
        errors.append("retired desk 'Property' is in the book — replaced by The Atelier (editor, 15 Aug 2026)")
    _at = _desk_pages.get('The Atelier', [])
    if not _at:
        errors.append("The Atelier is missing — the maker deep dive runs every edition (replaces Property from No. 74)")
    else:
        _atblob = ''.join(_at)
        _atp = re.findall(r'class="nextpick"[^>]*data-votedesk="Atelier Next"', _atblob)
        if len(_atp) != 3:
            errors.append(f"The Atelier: {len(_atp)} Next-on-the-Bench candidates (need exactly 3 .nextpick chips with data-votedesk=\"Atelier Next\" in a .nexthole box)")
        import json as _json3
        try:
            _atcov = _json3.load(open('state/atelier-ledger.json'))['covered']
        except (OSError, ValueError, KeyError):
            _atcov = []
        _atheads = ' '.join(re.findall(r'<div class="(?:hed|dek|kicker)[^"]*"[^>]*>(.*?)</div>', _atblob, re.S))
        _atheads = re.sub(r'<[^>]+>', ' ', _atheads).lower()
        for _ac in _atcov:
            _am2 = re.search(r'(\d+)', str(_ac.get('issue', '')))
            if _am2 and int(_am2.group(1)) == _issno:
                continue
            _akey = re.sub(r'\s*\(.*?\)', '', _ac['category']).split('&')[0].strip().lower()
            if len(_akey) >= 5 and _akey in _atheads:
                errors.append(f"The Atelier: category '{_ac['category']}' was already covered (No. {_ac.get('issue')}) — a category is covered ONCE, ever; pick from ledgers/atelier-ledger.md")

# THE RABBIT HOLE (editor, 4 Aug 2026; from No. 63): the 3-page hobby deep
# dive replaces The Connected Home, Curiosities and Love & Life — retired
# desks may not reappear; the desk runs EVERY edition at exactly 3 pages
# with deep-research footnote density; a hobby is covered ONCE, ever.
if _issno >= 63:
    for _dead in ('The Connected Home', 'Curiosities', 'Love & Life', 'Love &amp; Life'):
        if _dead in _desk_pages:
            errors.append(f"retired desk '{_dead}' is in the book — replaced by The Rabbit Hole (editor, 4 Aug 2026)")
if _issno >= 63 and not _special:
    _rh = _desk_pages.get('The Rabbit Hole', [])
    if len(_rh) != 3:
        errors.append(f"The Rabbit Hole: {len(_rh)} page(s) — the hobby deep dive is a fixed 3-page desk, every edition")
    if _rh:
        _rhblob = ''.join(_rh)
        _rhfn = len(re.findall(r'<sup class="fnref">', _rhblob))
        if _rhfn < 12:
            errors.append(f"The Rabbit Hole: only {_rhfn} footnote markers (floor 12) — the deepest desk in the book must carry its research residue")
        # Next Descents: the desk must close with exactly 3 vote-able candidates
        _np = re.findall(r'class="nextpick"[^>]*data-hobby="([^"]+)"', _rhblob)
        if len(_np) != 3:
            errors.append(f"The Rabbit Hole: {len(_np)} Next-Descents candidates (need exactly 3 .nextpick items with data-hobby attrs in a .nexthole box) — the reader picks tomorrow's hobby from these")
        elif 'class="nexthole"' not in _rhblob:
            errors.append("The Rabbit Hole: .nextpick items found but no .nexthole wrapper — use the standing box (see the desk brief)")
        # once-only rule: a Covered hobby from an EARLIER issue must not headline again
        import json as _json2
        try:
            _hob = _json2.load(open('state/hobby-ledger.json'))['covered']
        except (OSError, ValueError, KeyError):
            _hob = []
        _rhheads = ' '.join(re.findall(r'<div class="(?:hed|dek|kicker)[^"]*"[^>]*>(.*?)</div>', _rhblob, re.S))
        _rhheads = re.sub(r'<[^>]+>', ' ', _rhheads).lower()
        for _hb in _hob:
            _hm = re.search(r'(\d+)', str(_hb.get('issue', '')))
            if _hm and int(_hm.group(1)) == _issno:
                continue  # this issue's own row, logged before validation
            _hkey = re.sub(r'\s*\(.*?\)', '', _hb['hobby']).strip().lower()
            if len(_hkey) >= 5 and _hkey in _rhheads:
                errors.append(f"The Rabbit Hole: hobby '{_hb['hobby']}' was already covered (No. {_hb.get('issue')}) — a hobby is covered ONCE, ever; pick from the pipeline in ledgers/hobby-ledger.md")
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
    _ceiling = max(30, 70 - max(0, _issno - 52)) if _issno >= 52 else 999
    _ex = ', '.join(f'"{g}"' for g in _recycled[:5])
    if len(_recycled) > _ceiling:
        errors.append(f"voice: {len(_recycled)} distinctive 4-word prose phrases recycled from the last 3 issues (ceiling {_ceiling}, tightening by 1 per issue toward 30; e.g. {_ex}) — rewrite per the VOICE CARD")
    elif len(_recycled) > _ceiling - 15:
        warns.append(f"voice: {len(_recycled)} recycled prose phrases (ceiling {_ceiling} — headroom {_ceiling - len(_recycled)}; e.g. {_ex})")

# AI-tell scan: phrases that read as generated filler, not house prose.
# Calibrated: Nos. 38 and 51 score zero. Any hit is a warning; >4 total fails.
_TELLS = ['delve', 'tapestry', 'testament to', 'serves as a reminder', 'underscores the',
 'seamlessly', 'game-changer', "in today's fast-paced", 'at the intersection of',
 "isn't just about", 'navigate the complexities', 'dive deep', 'stands as a',
 'ever-evolving', 'in a world where', 'the humble', 'elevate your', 'a deep dive into',
 'rich history', 'nestled', 'vibrant', 'crucial role', 'plays a pivotal']
_pl_ = _prose(html)
_tellhits = {t: _pl_.count(t) for t in _TELLS if _pl_.count(t)}
for _t, _n in _tellhits.items():
    warns.append(f"voice/AI-tell: '{_t}' ×{_n} — generated-filler phrasing; rewrite in the house register")
if sum(_tellhits.values()) > 4:
    errors.append(f"voice/AI-tell: {sum(_tellhits.values())} generated-filler phrases across the issue (max 4) — the prose needs a human-register pass")

# issue-local classes: any class used in the body MUST have CSS defined —
# No. 55 shipped .tbl/.lede-strip/.brief-h/.mini markup with no styles at all
# (rendered as bare stacked text). The issue-local style block is mandatory.
_stylepart = html[html.find('<style'):html.rfind('</style>')] if '<style' in html else ''
for _cls in ('tbl', 'lede-strip', 'brief-h', 'brief-item', 'mini', 'cap-note', 'byline', 'figcluster'):
    _used = f'class="{_cls}"' in html or f'class="{_cls} ' in html
    _defined = f'.{_cls}{{' in _stylepart or f'.{_cls} {{' in _stylepart
    if _used and not _defined:
        errors.append(f"class '{_cls}' is used but has NO CSS defined — copy the issue-local style block from the previous issue (it is part of the fixed design system)")

# contents page (p2) layout is FIXED: two-column grid; From the Desk + The
# Strip live in the RIGHT column, never full-width below the list.
if len(pages) >= 2:
    _p2 = pages[1]
    _g = max(_p2.find('grid g-21'), _p2.find('grid g-12'))
    _f = _p2.find('From the Desk')
    _t = max(_p2.find('class="tbl'), _p2.find('lede-strip'))
    if _g == -1:
        errors.append("contents page: missing the two-column grid (g-21/g-12) layout — p2's structure is FIXED (list one side; From the Desk + The Strip the other)")
    # descendant check: the From-the-Desk chatter must live INSIDE the grid
    class _P2Scan(HTMLParser):
        def __init__(self):
            super().__init__(); self.stack=[]; self.in_grid_quote=False; self.grid_depth=None
        def handle_starttag(self, tag, attrs):
            cls = dict(attrs).get('class','') or ''
            self.stack.append((tag, cls))
            if 'grid' in cls.split() and self.grid_depth is None:
                self.grid_depth = len(self.stack)
        def handle_endtag(self, tag):
            if self.grid_depth is not None and len(self.stack) < self.grid_depth:
                self.grid_depth = None
            for _i in range(len(self.stack)-1, -1, -1):
                if self.stack[_i][0] == tag:
                    if self.grid_depth is not None and _i+1 <= self.grid_depth-1 and 'grid' in self.stack[_i][1].split():
                        self.grid_depth = None
                    del self.stack[_i]; break
        def handle_data(self, d):
            if 'From the Desk' in d and self.grid_depth is not None and len(self.stack) >= self.grid_depth:
                self.in_grid_quote = True
    _sc2 = _P2Scan(); _sc2.feed(_p2)
    if _f != -1 and not _sc2.in_grid_quote:
        errors.append("contents page: 'From the Desk' sits OUTSIDE the two-column grid (full-width below the list) — it belongs INSIDE the grid, in its own column, per the fixed p2 design")
    if _t == -1:
        errors.append("contents page: no market strip (.tbl table or .lede-strip) found — The Strip is standing p2 furniture")
    if 'class="cols2' not in _p2:
        errors.append("contents page: the desks list is not in .cols2 — one-entry-per-row full-width lists are the reported drift; the list runs as two columns of .mini entries inside the grid (No. 38 is the reference)")
    if _p2.count('class="mini') < 12:
        _nmini = _p2.count('class="mini')
        errors.append(f"contents page: only {_nmini} .mini desk entries — the contents list covers all desks (floor 12)")

# Diary furniture discipline: .agenda-h is a SECTION header (a geography or
# strip name + .sub note), never a spreadsheet column header; events run as
# .evt rows. (No. 55 shipped "Date | Event · Venue" column headers.)
if re.search(r'agenda-h[^>]*"><span>\s*Date\s*</span>', html, re.I):
    errors.append("The Diary: .agenda-h repurposed as a Date/Event/Venue column header — it is a SECTION header (e.g. 'Singapore <span class=\"sub\">book now · plan ahead</span>'); events are .evt rows, not table rows")
_diary = _desk_pages.get('The Diary', [])
if _diary:
    # THE DIARY FIXED LAYOUT (editor, 30 Jul 2026 — No. 38 / archive/no-38 is
    # the mandatory reference, exactly like the contents page):
    #   Diary page 1 — the events agenda: the Singapore section AND the
    #     Japan/Region section TOGETHER on ONE page, side by side in a
    #     two-column .grid of .evt rows. No 'The Table' content here.
    #   Diary page 2 — The Table gets its OWN full page: prose reviews
    #     (p.body + buzz chatter + tags), ZERO .evt rows, no geography headers.
    if len(_diary) != 2:
        errors.append(f"The Diary: {len(_diary)} Diary page(s) — the Diary is a fixed 2-page desk (agenda page + The Table page, No. 38 layout)")
    # page blobs run to the next <section, so trailing inter-page comments
    # (e.g. "P20 THE DIARY — The Table") would false-positive — cut at </section>
    _d1 = _diary[0].split('</section>')[0]
    _d2 = _diary[1].split('</section>')[0] if len(_diary) > 1 else ''
    _d1_heads = re.findall(r'class="agenda-h[^"]*"[^>]*>([^<]*)', _d1)
    if not any('Singapore' in _h for _h in _d1_heads):
        errors.append("The Diary p1: no 'Singapore' agenda-h — the agenda page carries the Singapore section (left column, No. 38 layout)")
    if not any('Japan' in _h for _h in _d1_heads):
        errors.append("The Diary p1: no 'Japan' agenda-h — Singapore AND Japan & the Region sit TOGETHER on the first Diary page, side by side (No. 38 layout); Japan on its own page is the reported drift")
    if 'class="grid' not in _d1:
        errors.append("The Diary p1: agenda sections are not in a two-column .grid (g-12) — Singapore left, Japan & the Region right, per No. 38")
    _n1 = _d1.count('class="evt"')
    if _n1 < 10:
        errors.append(f"The Diary p1: only {_n1} .evt rows (floor 10; No. 38 carries 11) — the agenda uses the standing .evt/.evt-date/.evt-meta furniture, both geographies on this page")
    if 'The Table' in _d1:
        errors.append("The Diary p1: 'The Table' appears on the agenda page — The Table gets its OWN separate page (Diary p2), never shares with the agenda (No. 38 layout)")
    # date-box typography (No. 38 idiom): a single date is '25<span class="mo">SEP</span>'
    # (big day, tiny month); a range/phrase uses class 'rng' (smaller face) with a <br>;
    # a marquee pick is marked by the red .star BACKGROUND, never a '★' glyph in the box.
    # No. 57 shipped '★ 17–22 Dec' as full-size text — oversized dates, the reported drift.
    for _db_cls, _db_in in re.findall(r'<div class="(evt-date[^"]*)">(.*?)</div>', _d1, re.S):
        _txt = re.sub(r'<[^>]+>', '', re.sub(r'<span class="mo">.*?</span>', '', _db_in)).strip()
        if '★' in _db_in:
            errors.append(f"The Diary p1: '★' glyph inside a date box ('{_txt}') — marquee picks are marked by the .star class (red box), not a star character (No. 38 idiom)")
        if 'rng' not in _db_cls and len(_txt) > 4:
            errors.append(f"The Diary p1: date box '{_txt}' is long text at full size — use '25<span class=\"mo\">SEP</span>' for single dates or class 'rng' (smaller face, <br> line break) for ranges (No. 38 idiom)")
    if _d2:
        if 'The Table' not in _d2:
            errors.append("The Diary p2: 'The Table' not found — the second Diary page IS The Table, full page (No. 38 layout)")
        _p2body = _d2.count('<p class="body')
        if _p2body < 3:
            errors.append(f"The Diary p2 (The Table): only {_p2body} prose paragraphs (floor 3) — reviews are PROSE (p.body + buzz chatter + tags), never rows")
        if 'class="evt"' in _d2:
            errors.append("The Diary p2 (The Table): contains .evt rows — the Table page carries prose reviews only; all dated events belong on Diary p1")
        if re.search(r'class="agenda-h[^"]*"[^>]*>[^<]*(Singapore|Japan)', _d2):
            errors.append("The Diary p2 (The Table): carries a geography agenda-h — the Singapore/Japan agenda lives on Diary p1 only")

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

# NOTE (editor, 5 Sep 2026): the WARN/ERROR print loop used to sit HERE, above
# the dead-events, undefined-class and Undercurrent-repeat gates — so anything
# those three appended was counted in the summary and never shown. Printing now
# happens once, immediately before the summary, after every gate has run.
# DEAD EVENTS (editor, 31 Aug 2026 — reader-reported). The Diary is
# re-researched from scratch every build, so a cancelled show reappears
# forever unless something machine-readable stops it: a Post Malone Singapore
# date ran in No. 84, was corrected as postponed in No. 85, and kept coming
# back because the correction was prose in an Issue Log note. Barred events
# live in ledgers/events-ledger.md -> state/events-ledger.json. The bar
# applies to LISTINGS (.evt rows) only — a correction notice may still name
# the event in prose, which is how a retraction is supposed to read.
try:
    _ev = json.loads(pathlib.Path("state/events-ledger.json").read_text())
    _barred = [b for b in _ev.get("barred", []) if b.strip()]
except Exception:
    _barred = []
if _barred:
    class _EvtScan(HTMLParser):
        def __init__(self):
            super().__init__(); self.depth=0; self.buf=[]; self.rows=[]
        def handle_starttag(self, tag, attrs):
            cls=(dict(attrs).get('class','') or '')
            if self.depth: self.depth+=1
            elif 'evt' in cls.split(): self.depth=1; self.buf=[]
        def handle_endtag(self, tag):
            if self.depth:
                self.depth-=1
                if self.depth==0: self.rows.append(' '.join(self.buf))
        def handle_data(self, d):
            if self.depth: self.buf.append(d.strip())
    _es=_EvtScan(); _es.feed(html)
    _blob=' | '.join(_es.rows).lower()
    _hits=[b for b in _barred if b.lower() in _blob]
    if _hits:
        errors.append("DEAD EVENT listed in The Diary: " + ", ".join(_hits)
                      + " — these are cancelled/postponed in ledgers/events-ledger.md and must not be listed;"
                      + " if one has been reinstated, set its Status to REINSTATED with the confirming source first")


# UNDEFINED CLASSES (editor, 31 Aug 2026 — reader-reported on No. 92's back
# cover). The spec has always said a class with no CSS "renders as plain text
# and is a build failure", but nothing checked it: .backcover, .bc-mark,
# .bc-lastword and .bc-foot shipped for months with no rule anywhere, so
# .page.dark's padding:0 went unopposed and the closing page rendered flush to
# the left edge with two-thirds of it empty. Every class used must have a rule
# in meridian.css or in the issue's own <style> block.
_ALLOW = {"fbrow", "fbk", "build-colophon"}   # Photo-Edition hooks, styled downstream
_defrx = re.compile(r"\.([A-Za-z][\w-]*)")
_cssblob = ""
_cssf = pathlib.Path("meridian.css")
if _cssf.exists():
    _cssblob += _cssf.read_text()
for _blk in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S):
    _cssblob += "\n" + _blk
_cssblob = re.sub(r"/\*.*?\*/", "", _cssblob, flags=re.S)
_defined = set(_defrx.findall(_cssblob))
_used = set()
for _a in re.findall(r'class="([^"]+)"', html):
    _used |= set(_a.split())
_undef = sorted(_used - _defined - _ALLOW)
if _undef:
    errors.append("class(es) used with no CSS rule anywhere: " + ", ".join(_undef)
                  + " — an undefined class renders as unstyled text; define it in meridian.css"
                  + " (standing component) or in the issue's <style> block (issue-local furniture)")


# UNDERCURRENT REPEATS (editor, 4 Sep 2026 — reader-reported). The closing
# long read had been rotating by GEOGRAPHY only, which stops the same country
# running twice in a row and stops nothing else: India astrology ran in No. 68
# and again in No. 72, Vietnam's idol economy in No. 67 and again in No. 75.
# Same once-only discipline as the Hobby Ledger — a covered subject's key term
# may not reappear in a later Undercurrent's kicker, headline or dek.
try:
    _uc = json.loads(pathlib.Path("state/undercurrent-ledger.json").read_text())
    _uckeys = [k for k in _uc.get("keys", []) if len(k.strip()) >= 4]
except Exception:
    _uckeys = []
if _uckeys:
    _uctext = ""
    for _sec in pages:
        if "Meridian &middot; The Undercurrent" in _sec or "Meridian · The Undercurrent" in _sec:
            for _m in re.finditer(r'<div class="(?:kicker|hed|dek)[^"]*"[^>]*>(.*?)</div>', _sec, re.S):
                _uctext += " " + re.sub(r"<[^>]+>", " ", _m.group(1))
    _uctext = _uctext.lower()
    _rep = [k for k in _uckeys if k.lower() in _uctext]
    if _rep:
        errors.append("UNDERCURRENT REPEAT: " + ", ".join(_rep)
                      + " already ran (see ledgers/undercurrent-ledger.md) — a covered subject is never covered again;"
                      + " rotating the country is not enough, the SUBJECT must be new")


for w in warns:
    print("WARN:", w)
for e in errors:
    print("ERROR:", e)

if errors:
    print(f"\nvalidate: {len(errors)} error(s), {len(warns)} warning(s) — FAILED")
    sys.exit(1)
print(f"\nvalidate: OK ({npages} pages, {len(warns)} warning(s))")
