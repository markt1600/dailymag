#!/usr/bin/env python3
"""Derive index.html (the Photo Edition) from the print HTML.

The Photo Edition is the deliverable most readers actually use, so it is not
just the print PDF mirrored — it invests in the screen medium:

  * inlines meridian.css + loads Google Fonts (portable, self-contained)
  * relaxes the fixed-A4 layout so pages flow on screen; footer goes static
  * a slim on-brand PDF download bar (relative href, download attr)
  * a STICKY DESK NAV with jump-links + active-desk highlighting on scroll
  * a reading-PROGRESS bar
  * a PAPER / NIGHT reading toggle (theme-aware, persisted in localStorage)
  * auto-linked in-issue cross-references ("see Macro, p15" -> jumps there)
  * RESPONSIVE scaling so the A4 page fits phone/tablet widths
  * honest up/down arrows on the market strips (direction only, no data added)
  * verified/representative Wikimedia Commons photo heroes (from images.json)

All additions are screen-only (@media screen); the print path is untouched.
Everything is inlined — no external calls except the fonts stylesheet — so the
file works opened from disk or served anywhere.

Usage:  python3 tools/make_photo_edition.py build/meridianNN.html index.html [NN] [DATE]
"""
import re, sys, json, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/meridian.html")
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "index.html")
ISSUE = sys.argv[3] if len(sys.argv) > 3 else "37"
DATE = sys.argv[4] if len(sys.argv) > 4 else "9 July 2026"
# special editions pass "NN.5" — integer comparisons use the base issue
ISSUE_BASE = int(float(ISSUE))
IS_SPECIAL = "." in ISSUE
# special editions also pass their own PDF filename (daily default unchanged)
PDF_HREF = sys.argv[5] if len(sys.argv) > 5 else "meridian-latest.pdf"

html = src.read_text()
css = pathlib.Path("meridian.css").read_text()
root = pathlib.Path(".")
images = {}
img_path = root / "state" / "images.json"
if img_path.exists():
    images = json.loads(img_path.read_text())

manifest = {}
man_path = root / "archive" / "manifest.json"
if man_path.exists():
    manifest = json.loads(man_path.read_text())

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">')

# ---- 1. number the pages and read their desk names from the running header ----
# Tolerate sources that already carry id="pN" (e.g. copied from a prior
# Photo Edition as a template) as well as the raw <section class="page">
# form the brand prompt documents — either way, every page ends up with a
# sequential id and NPAGES reflects the true page count.
counter = {"n": 0}
def add_id(m):
    counter["n"] += 1
    return f'<section id="p{counter["n"]}" class="page' + m.group(1)
if re.search(r'<section id="p\d+" class="page', html):
    NPAGES = len(re.findall(r'<section id="p\d+" class="page', html))
else:
    html = re.sub(r'<section class="page(["\s])', add_id, html)
    NPAGES = counter["n"]

# desk label per page (from .rh left span; cover/contents/back handled specially)
navitems = []  # (page_no, label)
sections = re.split(r'(?=<section id="p\d+" class="page)', html)
seen_labels = set()
for sec in sections:
    mid = re.match(r'<section id="p(\d+)"', sec)
    if not mid:
        continue
    pno = int(mid.group(1))
    if 'class="page dark"' in sec[:80] and pno == 1:
        label = "Cover"
    elif 'Meridian · Contents' in sec:
        label = "Contents"
    elif pno == NPAGES:
        label = "Back"
    else:
        rh = re.search(r'<div class="rh"><span>(?:<span[^>]*>[^<]*</span>\s*)?Meridian\s*·\s*([^<]+)</span>', sec)
        label = rh.group(1).strip() if rh else f"Page {pno}"
    if label in seen_labels and label not in ("Cover", "Contents", "Back"):
        continue  # desk spans multiple pages; link to its first page only
    seen_labels.add(label)
    navitems.append((pno, label))

# One compact dropdown instead of a link per desk (editor, 4 Aug 2026 — the
# nav row had outgrown the bar). The scroll-spy keeps it showing the current
# section; choosing an entry jumps there.
SECT_SELECT = ('<select class="m-toggle" id="msect" style="margin-left:0" aria-label="Jump to a section">'
               + "".join(f'<option value="p{p}">{lbl}</option>' for p, lbl in navitems)
               + '</select>')

# ---- 2. auto-link in-issue cross references (body only) ----
head_end = html.find("</head>")  # linkify only after head to avoid CSS
body_start = html.find("<body>")
def linkify(m):
    lead, n = m.group(1), int(m.group(2))
    if 1 <= n <= NPAGES:
        return f'{lead}<a class="xref" href="#p{n}">p{n}</a>'
    return m.group(0)
body = html[body_start:]
body = re.sub(r'([\s(,])p(\d{1,2})\b', linkify, body)
html = html[:body_start] + body

# ---- 3. screen assets (CSS) ----
SCREEN_CSS = """
<style>
/* ===== MERIDIAN Photo Edition — screen investment (print untouched) ===== */
@media screen {
  html,body { background:#cfcabf; scroll-behavior:smooth; }
  :root[data-theme="night"] html, :root[data-theme="night"] body { background:#0f0d0a; }

  /* pages flow on screen */
  .page:not(.dark){
    height:auto !important; min-height:297mm; overflow:visible !important;
    box-shadow:0 3px 26px rgba(0,0,0,.20); margin:9mm auto; background:var(--paper);
    zoom:var(--pzoom,1);
  }
  .page.dark{ zoom:var(--pzoom,1); margin:9mm auto; box-shadow:0 3px 26px rgba(0,0,0,.28); }
  .page:not(.dark) .pgfoot{ position:static !important; margin-top:5mm; }

  /* photo heroes */
  .ph-frame{ margin:3mm 0 3mm; width:100%; }
  .ph-frame img{ width:100%; height:44mm; object-fit:cover; display:block;
    background:#e6e1d6; border-radius:2px; }
  .ph-cred{ font-family:'Poppins',sans-serif; font-size:6.5pt; letter-spacing:.02em;
    color:var(--muted); margin-top:3px; text-align:right; }

  /* in-issue cross-reference links */
  a.xref{ color:var(--vermilion); text-decoration:none; border-bottom:1px dotted var(--vermilion); }
  a.xref:hover{ background:var(--vermilion); color:var(--paper); }

  /* direction arrows are added by JS from the number's actual SIGN (not the
     colour class, which the edition sometimes uses for sentiment) — honest. */
  .mchg{ font-size:.72em; }

  /* ---- reading progress ---- */
  #mprog{ position:fixed; top:0; left:0; height:3px; width:0%; z-index:120;
    background:linear-gradient(90deg,var(--gold),var(--vermilion)); transition:width .1s linear; }

  /* ---- sticky chrome: download bar + desk nav ---- */
  .m-chrome{ position:sticky; top:0; z-index:100; }
  .pdf-dl{ display:block; text-decoration:none; text-align:center;
    font-family:'Poppins',sans-serif; font-weight:600; font-size:10pt; letter-spacing:.06em;
    background:var(--vermilion); color:var(--paper); padding:2.6mm 4mm;
    border-bottom:2px solid var(--gold); }
  .pdf-dl:hover{ background:var(--vermilion-d); }
  .pod-bar{ background:var(--ink); border-bottom:1.2pt solid var(--gold); text-align:center; padding:5px 8px; }
  .pod-bar .pod-link{ display:inline-block; font-family:'Poppins',sans-serif;
    font-size:8.5pt; font-weight:600; letter-spacing:.12em; text-transform:uppercase;
    color:var(--gold); border:1.2pt solid var(--gold); border-radius:15px;
    padding:5px 16px; cursor:pointer; text-decoration:none; }
  .pod-bar .pod-link:hover{ background:var(--gold); color:var(--ink); }
  .pod-bar .pod-link:active{ transform:translateY(1px); }
  .pod-bar audio{ width:100%; display:block; height:36px; }
  .pod-bar .pod-row{ display:flex; align-items:center; gap:6px; padding:2px 8px 4px; }
  .pod-bar .pod-row audio{ flex:1; }
  .pod-speed{ flex:0 0 auto; background:none; border:1pt solid var(--gold); color:var(--gold);
    border-radius:10px; font-family:'Poppins',sans-serif; font-size:8pt; font-weight:600;
    padding:3px 9px; cursor:pointer; }
  .pod-speed:hover{ background:var(--gold); color:var(--ink); }
  .mnav{ display:flex; align-items:center; gap:2px; overflow-x:auto; scrollbar-width:thin;
    background:var(--ink); padding:0 8px; -webkit-overflow-scrolling:touch; }
  .mnav::-webkit-scrollbar{ height:0; }
  .mnav-link{ flex:0 0 auto; font-family:'Poppins',sans-serif; font-size:8pt; font-weight:600;
    letter-spacing:.04em; color:var(--blush); text-decoration:none; padding:6px 9px;
    border-bottom:2px solid transparent; white-space:nowrap; }
  .mnav-link:hover{ color:var(--paper); }
  .mnav-link.active{ color:var(--gold); border-bottom-color:var(--gold); }
  .m-toggle{ flex:0 0 auto; margin-left:auto; background:none; border:1px solid #4a443a;
    color:var(--blush); font-family:'Poppins',sans-serif; font-size:8pt; font-weight:600;
    padding:5px 10px; border-radius:12px; cursor:pointer; white-space:nowrap; }
  .m-toggle:hover{ color:var(--gold); border-color:var(--gold); }

  /* ---- NIGHT reading theme (token flip; keep figure/photo cards light so the
     hardcoded-hex SVGs stay legible) ---- */
  :root[data-theme="night"]{
    --paper:#17140f; --paper2:#221e17; --ink:#efe9db; --ink2:#d6cdbe;
    --muted:#918876; --line:#3a342c; --blush:#cdbf8f;
  }
  :root[data-theme="night"] .desk{ background:#221e17; }
  :root[data-theme="night"] .lede-strip{ background:#221e17; }
  :root[data-theme="night"] .figframe{ background:#f4efe4; }        /* light card for SVGs */
  :root[data-theme="night"] .figframe .imgcap{ color:#6d6556; }
  :root[data-theme="night"] .rule{ background:var(--ink); }

  /* ---- Archive overlay + search ---- */
  .march-overlay{ position:fixed; inset:0; z-index:200; background:rgba(20,17,13,.55);
    display:flex; justify-content:center; align-items:flex-start; padding:5vh 4vw; }
  .march-overlay[hidden]{ display:none; }
  .march-panel{ background:var(--paper); color:var(--ink); width:min(760px,100%);
    max-height:90vh; display:flex; flex-direction:column; border-radius:4px;
    box-shadow:0 12px 54px rgba(0,0,0,.5); border-top:4px solid var(--vermilion); }
  .march-head{ display:flex; align-items:baseline; gap:10px; padding:14px 18px 8px; }
  .march-head h2{ font-family:'Poppins',sans-serif; font-size:11pt; letter-spacing:.16em;
    text-transform:uppercase; color:var(--ink); margin:0; }
  .march-head .marchct{ font-family:'Poppins',sans-serif; font-size:8pt; color:var(--muted); }
  .march-close{ margin-left:auto; background:none; border:none; font-size:17pt; cursor:pointer;
    color:var(--muted); line-height:1; padding:0 4px; }
  .march-close:hover{ color:var(--vermilion); }
  .march-search{ margin:0 18px 8px; padding:9px 12px; font-family:'Poppins',sans-serif;
    font-size:10pt; border:1px solid var(--line); border-radius:3px; background:var(--paper2); color:var(--ink); }
  .march-list{ overflow-y:auto; padding:2px 12px 14px; }
  .marchi .hits{ margin:4px 0 2px; display:flex; flex-direction:column; gap:2px; }
  .marchi .hit{ font-family:'Poppins',sans-serif; font-size:11px; line-height:1.45; color:#403a32;
    text-decoration:none; padding:2px 0 2px 10px; border-left:2px solid #b08738; display:block; }
  a.hit:hover{ color:#9c3422; }
  .marchi .hit .hd{ font-weight:600; letter-spacing:.04em; text-transform:uppercase; font-size:9px; color:#7a7264; margin-right:4px; }
  .marchi .hit .pg{ color:#b08738; font-size:9.5px; }

  .marchi{ padding:9px 6px; border-bottom:1px solid var(--line); }
  .marchi:hover{ background:var(--paper2); }
  .marchi .no{ font-family:'Poppins',sans-serif; font-weight:700; font-size:8pt; letter-spacing:.08em; color:var(--vermilion); }
  .marchi .no .mode{ color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.1em; }
  .marchi .ti{ font-family:'Lora',serif; font-weight:700; font-size:12.5pt; line-height:1.1; margin:1px 0; }
  .marchi .sp{ font-family:'Lora',serif; font-style:italic; font-size:9.5pt; color:var(--ink2); }
  .marchi .acts{ margin-top:4px; }
  .marchi .acts a{ font-family:'Poppins',sans-serif; font-size:7.5pt; font-weight:600; letter-spacing:.08em;
    text-transform:uppercase; color:var(--paper); background:var(--ink); padding:2px 9px; border-radius:9px; text-decoration:none; margin-right:5px; }
  .marchi .acts a.pdf{ background:var(--vermilion); }
  .marchi .acts a:hover{ background:var(--gold); color:var(--ink); }
  .marchi .acts .na{ font-family:'Poppins',sans-serif; font-size:7pt; color:var(--muted); letter-spacing:.06em; }
  .march-none{ padding:22px; text-align:center; color:var(--muted); font-family:'Poppins',sans-serif; font-size:9pt; }
}
/* keep the print deliverable pristine */
.fbrow{ display:flex; justify-content:flex-end; align-items:center; gap:6px; margin:-2px 0 4px;
  font-family:'Poppins',sans-serif; font-size:8.4px; color:var(--muted); opacity:.6; transition:opacity .15s ease; }
/* NB: don't dim with opacity on a per-button basis — a parent opacity flattens the
   group, so a child cannot brighten itself. The chosen state uses a filled pill and
   the whole row goes fully opaque once a vote lands, which reads even on emoji. */
.fbrow:hover, .fbrow.voted{ opacity:1; }
/* tap affordance: interactive elements carry a soft blue tint so they read
   as clickable against the paper (editor, 6 Aug 2026) */
.fbrow button{ background:rgba(62,118,180,.12); border:.8pt solid rgba(62,118,180,.45); border-radius:10px;
  padding:1px 8px; cursor:pointer; color:inherit; font:inherit; line-height:1.6;
  transition:background .12s ease, border-color .12s ease, transform .12s ease, box-shadow .12s ease; }
.fbrow button:hover{ background:rgba(62,118,180,.22); border-color:rgba(62,118,180,.8); }
:root[data-theme="night"] .fbrow button{ background:rgba(120,170,225,.16); border-color:rgba(120,170,225,.45); }
.fbrow button.on{ background:var(--vermilion); border-color:var(--vermilion); color:var(--paper);
  transform:scale(1.08); box-shadow:0 1px 5px rgba(193,70,46,.4); }
.fbrow.voted .fbk{ color:var(--vermilion); }
.fbrow .fbk{ letter-spacing:.08em; text-transform:uppercase; align-self:center; }
/* the cover colophon: measured build time + tokens (machine-room honesty) */
.build-colophon{ position:absolute; bottom:4mm; left:0; right:0; text-align:center;
  font-family:'Poppins',sans-serif; font-size:6.5pt; letter-spacing:.18em;
  text-transform:uppercase; color:var(--blush); opacity:.72; }
/* Next Descents: candidates become tappable vote chips on screen */
.nextpick{ cursor:pointer; border-radius:3px; padding-left:6px !important; padding-right:6px !important;
  background:rgba(62,118,180,.09); box-shadow:inset 2px 0 0 rgba(62,118,180,.5); margin:1px 0;
  transition:background .12s ease, box-shadow .12s ease; position:relative; }
.nextpick:hover{ background:rgba(62,118,180,.2); }
:root[data-theme="night"] .nextpick{ background:rgba(120,170,225,.12); }
.nextpick.picked{ background:rgba(193,70,46,.10); box-shadow:inset 3px 0 0 var(--vermilion); }
.nextpick.picked::after{ content:'\\2713 your pick'; font-family:'Poppins',sans-serif; font-size:7px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--vermilion); float:right; margin-top:2px; }
.nexthole .lbl::after{ content:' \\00b7 tap one to choose tomorrow\\2019s descent';
  text-transform:none; letter-spacing:.02em; color:var(--muted); font-weight:400; }
@media print { .ph-frame, #mprog, .m-chrome, .fbrow, .build-colophon{ display:none !important; }
  .nextpick.picked::after, .nexthole .lbl::after{ content:none !important; }
  .nextpick.picked{ background:none; box-shadow:none; } }
</style>
"""

# ---- 4. assemble the head ----
html = html.replace('<link rel="stylesheet" href="meridian.css">',
                    FONTS + '\n<style>\n' + css + '\n</style>')

# Special editions are owner-only: the page hides itself immediately and only
# reveals after the shared .marktan.ai owner cookie (set by marktan.ai's
# Google login) verifies against marktan.ai/api/login. Anyone else — no
# cookie, stale cookie, or the API unreachable — gets a plain "Not found",
# so to visitors the special simply doesn't exist. Fail closed.
GATE_HEAD = ('\n<meta name="robots" content="noindex,nofollow">'
             '\n<style id="mgateCss">html{visibility:hidden}</style>'
             '\n<script>(function(){'
             "function deny(){var f=function(){document.head.innerHTML='<title>Not found</title>';"
             "document.body.innerHTML='<p style=\"font-family:system-ui,sans-serif;padding:48px 24px;color:#333\">Not found.</p>';"
             "document.documentElement.style.visibility='visible';};"
             "if(document.body)f();else document.addEventListener('DOMContentLoaded',f);}"
             "var m=document.cookie.match(/(?:^|;\\s*)mt_owner=([^;]+)/);"
             "if(!m){deny();return;}"
             "fetch('https://www.marktan.ai/api/login',{method:'POST',headers:{'content-type':'application/json'},"
             "body:JSON.stringify({session:decodeURIComponent(m[1])})})"
             ".then(function(r){if(r.ok){var s=document.getElementById('mgateCss');"
             "if(s)s.parentNode.removeChild(s);document.documentElement.style.visibility='visible';}else{deny();}})"
             ".catch(function(){deny();});"
             '})();</script>') if IS_SPECIAL else ''
html = html.replace('</head>', SCREEN_CSS + GATE_HEAD + '\n</head>')

# ---- 4b. reader feedback: subtle thumbs on each desk's lead article ----
# One row per desk (main articles only, per the editor), right-aligned and
# muted; votes POST to marktan.ai/api/feedback and land in the mainpage repo,
# which tomorrow's build session reads. Screen-only; print never sees it.
import re as _re
_secs = _re.split(r'(?=<section[^>]*class="page)', html)
_seen_desks, _out = set(), []
for _sec in _secs:
    _m = _re.search(r'<div class="rh"><span><span class="dot">●</span> Meridian · ([^<]+)</span>', _sec)
    if _m:
        _desk = _m.group(1).strip()
        _hand_placed = 'class="fbrow"' in _sec
        if _hand_placed:
            # A hand-authored row on this page claims the desk: mark it seen so
            # the desk's CONTINUATION pages don't get an injected second row
            # (No. 75 shipped duplicates on the 4 multi-page desks otherwise).
            _seen_desks.add(_desk)
        if _desk not in _seen_desks and _desk not in ('Contents',) and not _hand_placed:
            # (the fbrow check: a session that hand-authored its voting rows
            # already has one on this page — injecting again stacks two rows,
            # the No. 64.5 bug. Hand-placed wins.)
            _seen_desks.add(_desk)
            _dek = _sec.find('</div>', _sec.find('<div class="dek">')) if '<div class="dek">' in _sec else -1
            _kick = _re.search(r'<div class="kicker[^"]*">(.*?)</div>', _sec, _re.S)
            _topic = _re.sub(r'<[^>]+>', '', _kick.group(1)).strip() if _kick else _desk
            if _dek != -1:
                _end = _dek + len('</div>')
                _fb = ('\n  <div class="fbrow" data-desk="' + _desk.replace('"','') + '" data-topic="' + _topic.replace('"','') + '">'
                       '<span class="fbk">this story</span>'
                       '<button type="button" data-v="1" aria-label="More like this">👍</button>'
                       '<button type="button" data-v="-1" aria-label="Less like this">👎</button></div>')
                _sec = _sec[:_end] + _fb + _sec[_end:]
    _out.append(_sec)
html = ''.join(_out)

# ---- 4c. local asset paths -> absolute URLs (cover photo et al.) ----
# Sessions reference cover/interior photos by local repo path so the print
# render (Chromium, local file) sees them; on screen the same tags must load
# from the repo's raw URL so they work on the site, in archives, anywhere.
html = html.replace('src="assets/heroes/', 'src="https://raw.githubusercontent.com/markt1600/dailymag/main/assets/heroes/')

# ---- 4d. the Destinations picker: past Grand Tours, deep-linked ----
# A dropdown in the menu bar listing every covered Travel Desk destination,
# each linking to its back issue's Grand Tour pages in the archive (anchor
# found by scanning the archived photo edition for the Grand Tour running
# header). Data: state/destination-ledger.json.
def _grand_tour_url(issue_no, current_issue, html_now):
    import pathlib as _plh
    if str(issue_no) == str(current_issue):
        m = _re.search(r'<section id="(p\d+)"[^>]*>(?:(?!</section>).)*?The Grand Tour', html_now, _re.S)
        return '#' + m.group(1) if m else None
    f = _plh.Path(f'archive/no-{issue_no}/index.html')
    if not f.exists():
        return None
    ah = f.read_text(errors='ignore')
    _mrh = _re.search(r'Meridian · The Travel Desk</span><span>[^<]*Grand Tour', ah)
    anchor = ''
    i = _mrh.start() if _mrh else -1
    if i != -1:
        ids = _re.findall(r'<section id="(p\d+)"', ah[:i])
        anchor = '#' + ids[-1] if ids else ''
    return f'archive/no-{issue_no}/index.html{anchor}'

dest_options = []
try:
    with open('state/destination-ledger.json') as _fh:
        _dl = json.load(_fh)
    _rows = []
    for _d in _dl.get('destinations', []):
        _m = _re.search(r'No\.\s*(\d+)', _d.get('issue', ''))
        if not _m:
            continue
        _no = int(_m.group(1))
        _url = _grand_tour_url(_no, ISSUE, html)
        if _url:
            _rows.append((_no, _d['destination'].replace('\\&', '&'), _url))
    for _no, _name, _url in sorted(_rows, reverse=True):
        dest_options.append(f'<option value="{_url}">{_name} · No. {_no}</option>')
except Exception as _e:
    print('  (destinations picker skipped:', _e, ')')
DEST_SELECT = ('<select class="m-toggle" id="mdest" aria-label="Past Grand Tour destinations">'
               '<option value="">✈ Destinations</option>' + ''.join(dest_options) + '</select>') if dest_options else ''
print(f'  destinations picker: {len(dest_options)} entries')

def _rabbit_hole_url(issue_no, current_issue, html_now):
    import pathlib as _plh
    if str(issue_no) == str(current_issue):
        m = _re.search(r'<section id="(p\d+)"[^>]*>\s*<div class="rh"><span>(?:(?!</section>).)*?Meridian · The Rabbit Hole', html_now, _re.S)
        return '#' + m.group(1) if m else None
    f = _plh.Path(f'archive/no-{issue_no}/index.html')
    if not f.exists():
        return None
    ah = f.read_text(errors='ignore')
    _mrh = _re.search(r'Meridian · The Rabbit Hole</span>', ah)
    anchor = ''
    i = _mrh.start() if _mrh else -1
    if i != -1:
        ids = _re.findall(r'<section id="(p\d+)"', ah[:i])
        anchor = '#' + ids[-1] if ids else ''
    return f'archive/no-{issue_no}/index.html{anchor}'

hob_options = []
try:
    with open('state/hobby-ledger.json') as _fh:
        _hl = json.load(_fh)
    _hrows = []
    for _hb in _hl.get('covered', []):
        _m = _re.search(r'(\d+)', str(_hb.get('issue', '')))
        if not _m:
            continue
        _no = int(_m.group(1))
        _url = _rabbit_hole_url(_no, ISSUE, html)
        if _url:
            _hrows.append((_no, _hb['hobby'].replace('\\&', '&'), _url))
    for _no, _name, _url in sorted(_hrows, reverse=True):
        hob_options.append(f'<option value="{_url}">{_name} · No. {_no}</option>')
except Exception as _e:
    print('  (hobbies picker skipped:', _e, ')')
HOB_SELECT = ('<select class="m-toggle" id="mhob" aria-label="Past Rabbit Hole hobbies">'
              '<option value="">🕳 Hobbies</option>' + ''.join(hob_options) + '</select>') if hob_options else ''
print(f'  hobbies picker: {len(hob_options)} entries')

# special editions (one-topic NN.5 deep dives): OWNER-ONLY. The select ships
# empty and hidden — no special titles in the markup at all — and is populated
# at page load from state/specials.json only after the shared .marktan.ai
# owner cookie verifies against marktan.ai/api/login. Everyone else never
# sees a dropdown, so to them the specials don't exist.
SPEC_SELECT = ('<select class="m-toggle" id="mspec" aria-label="Special editions" hidden>'
               '<option value="">★ Specials</option></select>')
print('  specials picker: emitted empty (owner-gated, populated at runtime)')

# ---- 4e. the cover colophon: build time + tokens + list-price cost ----
# Time comes from build/.session-start (setup.sh stamps it at SessionStart);
# tokens are summed from the session's own transcript files (~/.claude/projects/
# */*.jsonl carry per-request usage, including subagents). Both are measured,
# never estimated; if either can't be measured it is omitted, not invented.
def _build_stats():
    import os as _os, glob as _glob, time as _time, datetime as _dt
    st = {}
    _t0 = None
    try:
        _t0dt = _dt.datetime.fromisoformat(open('build/.session-start').read().strip())
        _t0 = _t0dt.timestamp()
        _mins = (_time.time() - _t0) / 60
        if 0 < _mins < 600:
            st['minutes'] = round(_mins)
    except Exception:
        pass
    tot = 0; in_toks = 0; cache_toks = 0; out_toks = 0; cw_toks = 0
    # Theoretical cost at Anthropic API list prices, USD per MTok (input,
    # output); cache reads bill at 0.1x input, cache writes at 1.25x (5-min
    # TTL). Priced per request against that request's own model (subagents may
    # run a different tier than the main loop). First substring match wins,
    # so keep the more specific keys above the generic ones.
    _PRICES = [('fable-5', (10.0, 50.0)), ('mythos-5', (10.0, 50.0)),
               ('opus-4-1', (15.0, 75.0)), ('opus-4-2025', (15.0, 75.0)),
               ('opus', (5.0, 25.0)), ('sonnet', (3.0, 15.0)),
               ('haiku', (1.0, 5.0))]
    cost = 0.0; _models = {}
    _earliest = None
    try:
        for f in _glob.glob(_os.path.expanduser('~/.claude/projects/*/*.jsonl')):
            if _t0 and _os.path.getmtime(f) < _t0 - 300:
                continue  # stale transcript from another session in this container
            # first record's embedded timestamp = when this transcript began
            # (ctime is useless here: Linux updates it on every append)
            try:
                import datetime as _dt2
                _first = json.loads(open(f, errors='ignore').readline())
                _ts = _dt2.datetime.fromisoformat(str(_first.get('timestamp', '')).replace('Z', '+00:00')).timestamp()
                _earliest = _ts if _earliest is None else min(_earliest, _ts)
            except Exception:
                pass
            with open(f, errors='ignore') as fh:
                for line in fh:
                    if '"usage"' not in line:
                        continue
                    try:
                        _msg = json.loads(line).get('message') or {}
                        _u = _msg.get('usage') or {}
                    except Exception:
                        continue
                    if not isinstance(_u, dict):
                        continue
                    _raw = _u.get('input_tokens') or 0
                    _cw = _u.get('cache_creation_input_tokens') or 0
                    _cr = _u.get('cache_read_input_tokens') or 0
                    _ot = _u.get('output_tokens') or 0
                    in_toks += _raw + _cw; cw_toks += _cw
                    cache_toks += _cr; out_toks += _ot
                    tot += _raw + _cw + _cr + _ot
                    _mdl = str(_msg.get('model') or '')
                    for _k, (_pi, _po) in _PRICES:
                        if _k in _mdl:
                            cost += (_raw * _pi + _cw * _pi * 1.25
                                     + _cr * _pi * 0.1 + _ot * _po) / 1e6
                            _models[_mdl] = _models.get(_mdl, 0) + _ot
                            break
    except Exception:
        pass
    # diagnostic: say WHY the primary clock failed (Nos. 63-64 shipped without
    # a build time and the container is gone before anyone can ask it)
    if 'minutes' not in st:
        try:
            _raw = open('build/.session-start').read().strip()
            print(f"  (clock: stamp present but unusable: {_raw!r})")
        except OSError:
            print("  (clock: build/.session-start missing — SessionStart hook did not stamp)")
    # fallback clock: if the session-start stamp was missing/invalid, the
    # transcripts' first-record timestamps give the session's real start
    if 'minutes' not in st and _earliest:
        _mins = (_time.time() - _earliest) / 60
        if 0 < _mins < 600:
            st['minutes'] = round(_mins)
    if tot > 10000:
        st['tokens'] = tot
        st['tokens_input'] = in_toks       # fresh input (incl. cache writes)
        st['tokens_cached'] = cache_toks   # cache reads
        st['tokens_output'] = out_toks
        st['tokens_cache_write'] = cw_toks # subset of tokens_input, billed 1.25x
        if cost > 0:
            st['cost_usd'] = round(cost, 2)
            _dominant = max(_models, key=_models.get)
            st['model'] = _dominant
            # display form: claude-opus-4-8-20260115 -> opus-4-8
            st['model_short'] = re.sub(r'-\d{8}$', '',
                                       _dominant.replace('claude-', ''))
    return st

def _fmt_tokens(n):
    return f"{n/1e9:.2f}B" if n >= 1e9 else (f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k")

_stats = _build_stats()
_parts = []
if _stats.get('minutes'):
    _m = _stats['minutes']
    _parts.append(f"assembled in {_m//60}h{_m%60:02d}m" if _m >= 60 else f"assembled in {_m} min")
if _stats.get('tokens'):
    _parts.append(f"~{_fmt_tokens(_stats['tokens'])} tokens "
                  f"({_fmt_tokens(_stats['tokens_input'])} in · "
                  f"{_fmt_tokens(_stats['tokens_cached'])} cached · "
                  f"{_fmt_tokens(_stats['tokens_output'])} out)")
if _stats.get('cost_usd'):
    _c = _stats['cost_usd']
    _cs = f"US${_c:,.0f}" if _c >= 20 else f"US${_c:.2f}"
    _mdl = f" ({_stats['model_short']})" if _stats.get('model_short') else ''
    _parts.append(f"≈{_cs} at API list prices{_mdl}")
if _parts:
    _colo = '<div class="build-colophon">' + ' · '.join(_parts) + '</div>\n'
    # a session that hand-authored a colophon placeholder already has one on
    # the cover — stamping a second overprints it (No. 70 shipped the two
    # z-fighting). Replace, never stack.
    html = _re.sub(r'<div class="build-colophon">.*?</div>\s*', '', html, count=1)
    _cend = html.find('</section>')
    if _cend != -1:
        html = html[:_cend] + _colo + html[_cend:]
    try:
        pathlib.Path('build').mkdir(exist_ok=True)
        pathlib.Path('build/colophon.json').write_text(json.dumps(_stats))
    except OSError:
        pass
    print('  colophon:', ' · '.join(_parts))

# ---- 5. body-top chrome ----
CHROME = ('<body>\n'
          '<div id="mprog"></div>\n'
          '<div class="m-chrome">\n'
          f'  <a class="pdf-dl" href="{PDF_HREF}" download>⤓ Download the print edition (PDF) — No. {ISSUE} · {DATE}</a>\n'
          '  <div class="pod-bar" id="mpodbar"><a class="pod-link" id="mpod" role="button" tabindex="0">🎙 The Meridian Briefing · ▶ tap to generate the twenty-minute episode</a></div>\n'
          f'  <nav class="mnav">{SECT_SELECT}'
          '<button class="m-toggle" id="march" type="button">⧉ Archive</button>'
          + DEST_SELECT + HOB_SELECT + SPEC_SELECT +
          '<button class="m-toggle" id="mrm" type="button" title="Send this edition to the reMarkable tablet — editions are delivered only on request">⇥ reMarkable</button>'
          '<button class="m-toggle" id="mnote" type="button">✎ Note</button>'
          '<button class="m-toggle" id="mtheme" type="button">☾ Night</button></nav>\n'
          '</div>')
if manifest:
    CHROME += (
        '\n<div id="marchive" class="march-overlay" hidden><div class="march-panel">'
        '<div class="march-head"><h2>The Archive</h2><span class="marchct"></span>'
        '<button class="march-close" type="button" aria-label="Close">×</button></div>'
        '<input class="march-search" type="search" placeholder="Search past issues — a topic, a desk, a quote…" aria-label="Search past issues">'
        '<div class="march-list"></div></div></div>'
        '\n<script type="application/json" id="marchive-data">'
        + json.dumps(manifest, ensure_ascii=False) + '</script>')
html = html.replace('<body>', CHROME, 1)

# ---- 6. photo heroes: repo-hosted library + standing per-desk fallbacks ----
# Images live IN the repo (assets/heroes/<slug>.jpg, fetched from Commons by
# .github/workflows/fetch-heroes.yml) and are embedded via raw.githubusercontent
# so they load for readers, in archives, and are even testable from the build
# sandbox (the one image host it can reach). Every issue MUST carry photos:
# desks with no issue-specific hero fall back to the standing entry for that
# desk, and the build fails outright if fewer than 3 heroes land.
ASSET_BASE = "https://raw.githubusercontent.com/markt1600/dailymag/main/assets/heroes/"
import os as _os

# The PRINT html must reference repo images by LOCAL relative path
# (src="assets/heroes/x.jpg"): headless Chromium in the build sandbox fails TLS
# to raw.githubusercontent SILENTLY, and Nos. 67-69 shipped PDFs with a
# broken-image glyph where the cover hero belonged. The web build wants the
# absolute raw URL (works from archives and file://) — so rewrite here.
html = html.replace('src="assets/heroes/', 'src="' + ASSET_BASE)
def _asset_ok(slug):
    return _os.path.exists(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "assets", "heroes", slug + ".jpg"))
def hero(entry):
    slug = entry.get("asset")
    if slug and _asset_ok(slug):
        url = ASSET_BASE + slug + ".jpg"
    elif entry.get("url"):
        url = entry["url"]
    else:
        fn = entry["file"]
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + fn.replace(' ', '%20') + "?width=1600"
    if entry.get("source"):
        cred = entry["caption"] + ' Source: ' + entry["source"]
    else:
        cred = entry["caption"] + ' Source: Wikimedia Commons — "File:' + entry.get("file","") + '"'
    if entry.get("license"):
        cred += ' · ' + entry["license"]
    if entry.get("author"):
        cred += " · " + entry["author"]
    cred += ". " + ("Specific subject." if entry.get("specific") else "Representative image, honestly labelled.")
    alt = entry["caption"].split(" — ")[0]
    return (f'  <div class="ph-frame"><img src="{url}" alt="{alt}" loading="lazy">'
            f'<div class="ph-cred">{cred}</div></div>\n')

count, used_anchors, used_assets = 0, set(), set()
def inject(entry):
    global html, count
    anchor = entry["anchor"]
    _slug = entry.get("asset")
    idx = html.find(anchor)
    if idx == -1:
        print("  (skip hero, anchor not found:", anchor, ")")
        return
    if anchor in used_anchors:
        return
    if _slug and _slug in used_assets:
        print(f"  (skip hero '{_slug}' for {anchor[:40]} — same image already ran this issue; one asset, one appearance)")
        return
    # if the source HTML already carries this asset (a session that hand-placed
    # its ph-frames AND registered them in images.json), injecting again would
    # double every image — the No. 64.5 bug. Hand-placed wins; skip.
    if _slug and (ASSET_BASE + _slug + '.jpg') in html:
        print(f"  (skip hero '{_slug}' — already hand-placed in the source; not injecting a duplicate)")
        used_assets.add(_slug); used_anchors.add(anchor); count += 1
        return
    # Insert after the .rule divider that follows the anchor. Some pages (e.g.
    # a Long Read opener) have no rule — fall back to just after the anchor's
    # enclosing element (the running-header close). NEVER trust a raw find()
    # result: -1 + len(needle) silently splices the hero into byte ~23 of the
    # document, splitting the <html> tag (the No. 57 giant-image-at-top bug).
    rule = html.find('<div class="rule"></div>', idx)
    if rule != -1:
        end = rule + len('<div class="rule"></div>')
    else:
        close = html.find('</div>', idx)
        if close == -1:
            print(f"  (skip hero '{_slug}' — no insertion point after anchor)")
            return
        end = close + len('</div>')
    if end <= html.find('<body'):
        print(f"  (skip hero '{_slug}' — computed insertion point precedes <body>; refusing to corrupt the document)")
        return
    html = html[:end] + '\n' + hero(entry) + html[end:]
    used_anchors.add(anchor)
    if _slug: used_assets.add(_slug)
    count += 1

_standing_slugs = {e.get("asset") for e in images.get("standing", [])}
_recent_slugs = {e.get("asset") for e in images.get("heroes", [])
                 if e.get("issue") and e.get("asset")
                 and str(e["issue"]) != str(ISSUE)
                 and str(e["issue"]).isdigit() and int(e["issue"]) >= ISSUE_BASE - 3}
fresh = 0
for entry in images.get("heroes", []):
    if entry.get("issue") and str(entry["issue"]) != str(ISSUE):
        continue
    _slug = entry.get("asset")
    if _slug and _slug not in _standing_slugs and _slug not in _recent_slugs and _asset_ok(_slug):
        fresh += 1
    elif _slug and _slug in _recent_slugs:
        print(f"  (advisory: hero '{_slug}' was used within the last 3 issues — recycled imagery)")
    inject(entry)
# standing fallbacks: guarantee photos even when the session assigned none —
# but a standing asset may NOT run two issues in a row (reader-reported
# fatigue: the same Marina Bay every morning). A skipped fallback lowers the
# hero count toward the floor, which is the point: source something fresh.
_prev_html = ''
try:
    _prevno = ISSUE_BASE - 1
    _pf = _os.path.join('archive', f'no-{_prevno}', 'index.html')
    if _os.path.exists(_pf):
        _prev_html = open(_pf, errors='ignore').read()
except (ValueError, OSError):
    pass
for entry in images.get("standing", []):
    _slug = entry.get("asset", "")
    if _slug and _prev_html and (ASSET_BASE + _slug + '.jpg') in _prev_html:
        print(f"  (standing image '{_slug}' ran in No. {_prevno} — SKIPPED for fatigue; source a fresh image for this desk)")
        continue
    inject(entry)
# THE GENUINE-PRODUCT RULE — now a HARD GATE for the two pure-product desks.
# The Kit and The Good Life write about named products; their heroes must be
# the actual product (specific:true, press/official image). The one escape:
# the hero entry carries a "no_image" attestation describing the FAILED hunt
# ("searched Breitling newsroom, official page, launch coverage — none
# usable"), which prints into the log as a deliberate, visible exception.
_PRODUCT_HARD = ('The Kit', 'The Good Life')
_violations = []
for entry in images.get("heroes", []):
    if entry.get("issue") and str(entry["issue"]) != str(ISSUE):
        continue
    for _pd in _PRODUCT_HARD:
        if _pd in entry.get("anchor", "") and not entry.get("specific"):
            _att = str(entry.get("no_image") or "")
            # An attestation is only valid if it documents a WEBSEARCH hunt that
            # came up empty. Sandbox reachability is irrelevant (the sandbox can
            # reach no image host by design; the fetch-heroes Action does the
            # download with full internet) — an attestation blaming the sandbox
            # is the No. 57 failure mode and does NOT satisfy the gate.
            _bogus = [w for w in ('sandbox', '403', '429', 'blocked', 'unreachable',
                                  'could not fetch', "couldn't fetch", 'fetch failed')
                      if w in _att.lower()]
            if _att and not _bogus:
                print(f"  ({_pd}: representative image ATTESTED — {_att[:100]})")
            elif _att:
                _violations.append(f"{_pd} (attestation blames the sandbox: {', '.join(_bogus)} — "
                                   "invalid; the hunt is WebSearch, the download is the fetch-heroes Action)")
            else:
                _violations.append(_pd)
for entry in images.get("standing", []):
    for _pd in _PRODUCT_HARD:
        if _pd in entry.get("anchor", "") and entry["anchor"] in used_anchors:
            _violations.append(_pd + " (standing fallback)")
# OMISSION is not an escape either (the No. 57 dodge: no Kit/Good Life entry at
# all, so the per-entry checks above never fired). If the desk's page is in the
# book, it needs a current-issue hero entry — specific:true or a valid no_image
# attestation. Original SVG artwork "kept" is not attested compliance.
for _pd in _PRODUCT_HARD:
    if f'Meridian · {_pd}<' in html or f'Meridian · {_pd}</span>' in html:
        _has = any(str(e.get("issue")) == str(ISSUE) and _pd in e.get("anchor", "")
                   for e in images.get("heroes", []))
        if not _has:
            _violations.append(f"{_pd} (NO hero entry at all — omission is not compliance; "
                               "hunt via WebSearch, add {{slug,url}} to assets/heroes/manifest.json, "
                               "push, let the fetch-heroes Action download it, or attest a genuinely empty hunt)")
if _violations:
    print("FAIL: the genuine-product rule — these desks shipped generic imagery with no attestation:")
    for _v in _violations:
        print("      -", _v)
    print("      Source the actual product's press image (maker newsroom -> official page -> credited")
    print("      launch coverage -> agency), or add a 'no_image' attestation to the hero entry.")
    raise SystemExit(1)
if fresh < 2:
    print(f"FAIL: only {fresh} FRESH story-specific hero image(s) this issue (min 2; aim for one per desk lead).")
    print("      Add press/product/agency images via assets/heroes/manifest.json (fetch-heroes Action),")
    print("      then assign them in state/images.json — standing images are an emergency fallback, not the plan.")
    raise SystemExit(1)
if fresh < 6:
    print(f"  (advisory: {fresh} fresh story-specific heroes — the editor wants one per desk lead)")
if count < 3:
    print(f"FAIL: only {count} photo hero(s) landed — the Photo Edition must carry images every issue.")
    print("      Check state/images.json anchors vs the running headers, and assets/heroes/.")
    raise SystemExit(1)
if count < 5:
    print(f"  (advisory: only {count} heroes — consider assigning issue-specific picks)")

# ---- 7. behaviour (inline, CSP-safe) ----
JS = """
<script>
(function(){
  var API='https://www.marktan.ai/api/feedback', ISS=document.querySelector('.pdf-dl');
  var issue=(ISS&&(ISS.textContent.match(/No\\.\\s*(\\d+)/)||[])[1])||'';
  function post(p){ try{ fetch(API,{method:'POST',headers:{'Content-Type':'text/plain'},body:JSON.stringify(p)}); }catch(e){} }
  // Owner check for owner-only chrome (the Specials picker, deep-dive
  // requests): reads the .marktan.ai cookie set by marktan.ai's Google
  // login and verifies it server-side. Memoized; false on any failure.
  function mOwner(cb){
    if(!window.__mOwnerP){ window.__mOwnerP=new Promise(function(res){
      var mm=document.cookie.match(/(?:^|;\\s*)mt_owner=([^;]+)/);
      if(!mm){ res(false); return; }
      fetch('https://www.marktan.ai/api/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({session:decodeURIComponent(mm[1])})}).then(function(r){ res(r.ok); }).catch(function(){ res(false); });
    }); }
    window.__mOwnerP.then(cb);
  }
  window.mOwner = mOwner; // the chrome IIFE below uses it too — must be global
  document.querySelectorAll('.fbrow').forEach(function(row){
    var key='mfb-'+issue+'-'+row.dataset.desk;
    var prev=null; try{ prev=localStorage.getItem(key); }catch(e){}
    var fbk=row.querySelector('.fbk');
    function mark(){ row.classList.add('voted'); if(fbk) fbk.textContent='\\u2713 noted'; }
    row.querySelectorAll('button').forEach(function(b){
      if(prev===b.dataset.v){ b.classList.add('on'); mark(); }
      b.addEventListener('click',function(){
        row.querySelectorAll('button').forEach(function(x){x.classList.remove('on');});
        b.classList.add('on'); mark();
        try{ localStorage.setItem(key,b.dataset.v); }catch(e){}
        post({type:'vote',issue:issue,desk:row.dataset.desk,topic:row.dataset.topic,vote:+b.dataset.v});
      });
    });
    mOwner(function(ok){ if(!ok) return; // deep-dive requests are owner-only
    var gd=document.createElement('button');
    gd.type='button'; gd.textContent='\u2921'; gd.title='Request an ULTRA DEEP DIVE — a dedicated special edition on this topic';
    gd.setAttribute('aria-label', gd.title);
    gd.addEventListener('click',function(){
      if(!confirm('Request a dedicated SPECIAL EDITION (a full ultra-deep-dive issue) on:\\n\\n\u201c'+row.dataset.topic+'\u201d?\\n\\nIt will be researched and published as No. '+issue+'.5.')) return;
      post({type:'note',issue:issue,text:'SPECIAL EDITION REQUEST: '+row.dataset.topic+' (desk: '+row.dataset.desk+')'});
      gd.textContent='\u2713'; gd.disabled=true;
      if(fbk) fbk.textContent='deep dive requested';
    });
    row.appendChild(gd);
    });
  });
  var picks=[].slice.call(document.querySelectorAll('.nextpick'));
  if(picks.length){
    // vote chips are grouped by their target desk (data-votedesk; the Rabbit
    // Hole's chips predate the attribute and default to 'Rabbit Hole Next')
    var groups={};
    picks.forEach(function(p){
      var dsk=p.dataset.votedesk||'Rabbit Hole Next';
      (groups[dsk]=groups[dsk]||[]).push(p);
    });
    Object.keys(groups).forEach(function(dsk){
      var g=groups[dsk];
      var pkey='mfb-'+issue+'-next-'+dsk.toLowerCase().replace(/[^a-z]+/g,'');
      var chosen=null; try{ chosen=localStorage.getItem(pkey); }catch(e){}
      g.forEach(function(p){
        if(chosen===p.dataset.hobby) p.classList.add('picked');
        p.addEventListener('click',function(){
          g.forEach(function(x){x.classList.remove('picked');});
          p.classList.add('picked');
          try{ localStorage.setItem(pkey,p.dataset.hobby); }catch(e){}
          post({type:'vote',issue:issue,desk:dsk,topic:p.dataset.hobby,vote:1});
        });
      });
    });
  }
  var md=document.getElementById('mdest');
  if(md) md.addEventListener('change',function(){ if(md.value){ location.href=md.value; md.selectedIndex=0; } });
  var mn=document.getElementById('mnote');
  if(mn) mn.addEventListener('click',function(){
    var t=prompt('Note to the editor — lands in tomorrow\\'s build:');
    if(t&&t.trim()){ post({type:'note',issue:issue,text:t.trim().slice(0,1000)}); mn.textContent='✓ Sent'; setTimeout(function(){mn.textContent='✎ Note';},2500); }
  });
})();
""" + """
(function(){
  var root=document.documentElement;
  var prog=document.getElementById('mprog');
  var chrome=document.querySelector('.m-chrome');
  var pages=[].slice.call(document.querySelectorAll('.page'));

  // honest direction arrows on the market strips: read the number's SIGN,
  // not the colour class. A "+5.2%" always gets an up-arrow even if styled red.
  document.querySelectorAll('.tbl td .up, .tbl td .dn, .lede-strip .up, .lede-strip .dn').forEach(function(el){
    var t=el.textContent||'';
    var up=/[+]|\\bup\\b/i.test(t), dn=/[-\\u2212]|\\bfell\\b|\\bdown\\b/i.test(t);
    if(up===dn) return;                        // ambiguous or neither -> no arrow
    var s=document.createElement('span'); s.className='mchg';
    s.textContent=up?' \\u25B2':' \\u25BC'; el.appendChild(s);
  });

  // responsive: shrink the fixed-A4 page to fit narrow viewports
  function fit(){
    var pw=210*96/25.4;                       // 210mm in css px
    var avail=Math.min(window.innerWidth-24, pw);
    root.style.setProperty('--pzoom', (avail/pw).toFixed(4));
  }
  fit(); window.addEventListener('resize', fit);

  // reading progress
  function onScroll(){
    var h=document.documentElement.scrollHeight-window.innerHeight;
    prog.style.width=(h>0?(window.scrollY/h*100):0)+'%';
  }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();

  // scroll-spy: the Sections dropdown always shows the section being read
  var msel=document.getElementById('msect');
  var sectIds={};
  if(msel) [].forEach.call(msel.options,function(o){ sectIds[o.value]=true; });
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(e.isIntersecting && msel && sectIds[e.target.id]) msel.value=e.target.id;
    });
  },{rootMargin:'-45% 0px -50% 0px'});
  pages.forEach(function(p){ if(sectIds[p.id]) io.observe(p); });

  // offset smooth-scroll so the sticky chrome doesn't cover the target
  function chromeH(){ return chrome?chrome.getBoundingClientRect().height:0; }
  if(msel) msel.addEventListener('change', function(){
    var t=document.getElementById(msel.value);
    if(t) window.scrollTo({top:t.getBoundingClientRect().top+window.scrollY-chromeH()-6, behavior:'smooth'});
  });
  // on-demand reMarkable delivery: editions no longer auto-upload (the tablet
  // was silting up) \u2014 the reader presses the button, the marktan.ai endpoint
  // fires the repo's deliver workflow_dispatch. GitHub Actions is the fallback.
  function deliver(type,label,after){
    if(!confirm('Send '+label+' to the reMarkable tablet?')) return;
    fetch('https://www.marktan.ai/api/deliver',{method:'POST',headers:{'Content-Type':'text/plain'},body:JSON.stringify({type:type})})
      .then(function(r){ if(!r.ok) throw 0; after(true); })
      .catch(function(){ after(false);
        if(confirm('Could not reach the delivery service. Open GitHub Actions to run it by hand?'))
          window.open('https://github.com/markt1600/dailymag/actions/workflows/deliver-'+(type==='special'?'special':'remarkable')+'.yml','_blank');
      });
  }
  // The Meridian Briefing: on-demand podcast. If the episode mp3 exists on
  // main, the bar becomes a player; otherwise a click fires the render
  // workflow (via the deliver endpoint) and polls until the audio lands.
  var podbar=document.getElementById('mpodbar'), podlink=document.getElementById('mpod');
  if(podbar&&podlink){
    var pdl=document.querySelector('.pdf-dl');
    var piss=(pdl&&(pdl.textContent.match(/No\\.\\s*(\\d+)/)||[])[1])||'';
    var PODURL='https://raw.githubusercontent.com/markt1600/dailymag/main/podcast/meridian-'+piss+'.mp3';
    function podPlayer(){
      podbar.innerHTML='<div class="pod-row"><audio controls preload="none" src="'+PODURL+'"></audio><button class="pod-speed" type="button" title="Playback speed"></button></div>';
      var au=podbar.querySelector('audio'), sb=podbar.querySelector('.pod-speed');
      var speeds=[1,1.15,1.3,1.5,1.75,2];
      var sp=1.3; try{ var st=parseFloat(localStorage.getItem('mpod-speed')); if(speeds.indexOf(st)>-1) sp=st; }catch(e){}
      function apply(){ au.playbackRate=sp; sb.textContent=sp+'\u00d7'; }
      au.addEventListener('loadedmetadata',function(){ au.playbackRate=sp; });
      au.addEventListener('play',function(){ au.playbackRate=sp; });
      sb.addEventListener('click',function(){ sp=speeds[(speeds.indexOf(sp)+1)%speeds.length]; try{ localStorage.setItem('mpod-speed',sp); }catch(e){} apply(); });
      apply();
    }
    function podCheck(cb){ fetch(PODURL,{method:'HEAD',cache:'no-store'}).then(function(r){cb(r.ok);}).catch(function(){cb(false);}); }
    podCheck(function(ok){ if(ok) podPlayer(); });
    var podBusy=false;
    podlink.addEventListener('click',function(){
      if(podBusy) return;
      if(!confirm('Generate the twenty-minute episode of The Meridian Briefing for this issue? Recording takes a few minutes.')) return;
      fetch('https://www.marktan.ai/api/deliver',{method:'POST',headers:{'Content-Type':'text/plain'},body:JSON.stringify({type:'podcast',issue:piss})})
        .then(function(r){ if(!r.ok) throw 0;
          podBusy=true; podlink.textContent='⏳ Recording — usually three to eight minutes. This bar becomes a player when the episode is ready.';
          var tries=0; var iv=setInterval(function(){
            tries++;
            if(tries>60){ clearInterval(iv); podBusy=false; podlink.textContent='🎙 Still recording — reload in a few minutes'; return; }
            podCheck(function(ok){ if(ok){ clearInterval(iv); podPlayer(); } });
          },20000);
        })
        .catch(function(){
          if(confirm('Could not reach the generator service. Open GitHub Actions to run it by hand?'))
            window.open('https://github.com/markt1600/dailymag/actions/workflows/generate-podcast.yml','_blank');
        });
    });
  }
  var mrm=document.getElementById('mrm');
  if(mrm) mrm.addEventListener('click',function(){
    var dl=document.querySelector('.pdf-dl');
    var no=(dl&&(dl.textContent.match(/No\\.\\s*\\d+[^\u00b7]*(\u00b7[^\u00b7]*)?/)||[])[0])||'this edition';
    deliver('edition', no.trim(), function(ok){
      if(ok){ mrm.textContent='\u2713 On its way'; setTimeout(function(){ mrm.textContent='\u21e5 reMarkable'; }, 5000); }
    });
  });
  var ms=document.getElementById('mspec');
  if(ms){
    ms.addEventListener('change', function(){
      if(!ms.value) return;
      if(ms.value==='!deliver'){ deliver('special', ms.dataset.newest||'the newest special', function(){}); ms.selectedIndex=0; return; }
      location.href=ms.value; ms.selectedIndex=0;
    });
    // Specials are owner-only: populate (and reveal) the picker only
    // after the shared .marktan.ai cookie verifies. Everyone else keeps
    // an empty, hidden select \u2014 the specials don't exist for them.
    mOwner(function(ok){ if(!ok) return;
    fetch('https://raw.githubusercontent.com/markt1600/dailymag/main/state/specials.json',{cache:'no-store'})
      .then(function(r){ return r.json(); })
      .then(function(d){
        var list=(d&&d.specials)||[]; if(!list.length) return;
        while(ms.options.length>1) ms.remove(1);
        list.slice().reverse().forEach(function(s){
          var o=document.createElement('option'); o.value='https://www.marktan.ai/api/special?file='+encodeURIComponent(s.path); o.textContent='No. '+s.no+' \u00b7 '+s.topic;
          ms.appendChild(o);
        });
        var last=list[list.length-1];
        ms.dataset.newest='the newest special \u2014 No. '+last.no+' \u00b7 '+last.topic;
        var dv=document.createElement('option'); dv.value='!deliver'; dv.textContent='\u21e5 Send newest special to tablet';
        ms.appendChild(dv);
        ms.hidden=false;
      }).catch(function(){});
    });
  }
  var mh=document.getElementById('mhob');
  if(mh) mh.addEventListener('change', function(){
    if(!mh.value) return;
    if(mh.value.charAt(0)==='#'){
      var t=document.getElementById(mh.value.slice(1));
      if(t) window.scrollTo({top:t.getBoundingClientRect().top+window.scrollY-chromeH()-6, behavior:'smooth'});
      mh.selectedIndex=0;
    } else { location.href=mh.value; }
  });
  document.querySelectorAll('a[href^="#p"]').forEach(function(a){
    a.addEventListener('click', function(ev){
      var t=document.getElementById(a.getAttribute('href').slice(1));
      if(t){ ev.preventDefault();
        window.scrollTo({top:t.getBoundingClientRect().top+window.scrollY-chromeH()-6, behavior:'smooth'}); }
    });
  });

  // Archive + search overlay (data embedded at build time; works from file://)
  var mdata=document.getElementById('marchive-data');
  var march=document.getElementById('march');
  if(mdata && march){
    var data=JSON.parse(mdata.textContent);
    var ov=document.getElementById('marchive');
    var listEl=ov.querySelector('.march-list');
    var searchEl=ov.querySelector('.march-search');
    var ctEl=ov.querySelector('.marchct');
    function esc(s){var d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
    function artHits(it,q){
      if(!q) return [];
      return (it.articles||[]).filter(function(a){
        return (a.d+' '+a.h+' '+a.x).toLowerCase().indexOf(q)>=0;
      }).slice(0,5);
    }
    function render(q){
      q=(q||'').toLowerCase().trim();
      var nArts=0;
      var items=data.issues.map(function(it){
        var hits=artHits(it,q);
        var selfMatch=!q || (it.no+' '+it.date+' '+it.mode+' '+it.spine+' '+it.title+' '+it.quote+' '+it.author+' '+it.text).toLowerCase().indexOf(q)>=0;
        if(!selfMatch && !hits.length) return null;
        nArts+=hits.length;
        return {it:it, hits:hits};
      }).filter(Boolean);
      ctEl.textContent=q ? items.length+' issues'+(nArts?' \\u00b7 '+nArts+' articles':'') : items.length+' of '+data.issues.length+' issues';
      if(!items.length){ listEl.innerHTML='<div class="march-none">No issues match \\u201c'+esc(q)+'\\u201d.</div>'; return; }
      listEl.innerHTML=items.map(function(row){
        var it=row.it;
        var acts= it.href ? '<a href="'+it.href+'">'+(it.current?'Read · current':'Read')+'</a>' : '<span class="na">git history only</span>';
        if(it.pdf) acts+='<a class="pdf" href="'+it.pdf+'" download>PDF</a>';
        var hitsHtml='';
        if(row.hits.length){
          hitsHtml='<div class="hits">'+row.hits.map(function(a){
            var url=it.current?('#'+a.a):(it.href?it.href+'#'+a.a:null);
            var label='<span class="hd">'+esc(a.d)+'</span> '+esc(a.h);
            return url?'<a class="hit" href="'+url+'">'+label+' <span class="pg">'+a.a.replace('p','p. ')+' \\u2192</span></a>'
                      :'<span class="hit">'+label+'</span>';
          }).join('')+'</div>';
        }
        return '<div class="marchi"><div class="no">No. '+it.no+' &middot; '+esc(it.date)+(it.mode?' <span class="mode">&middot; '+esc(it.mode)+'</span>':'')+'</div>'+
          (it.title?'<div class="ti">'+esc(it.title)+'</div>':'')+
          (it.spine?'<div class="sp">'+esc(it.spine)+'</div>':'')+
          hitsHtml+
          '<div class="acts">'+acts+'</div></div>';
      }).join('');
    }
    listEl.addEventListener('click', function(e){
      var t=e.target;
      while(t && t!==listEl && !(t.tagName==='A' && t.className==='hit')) t=t.parentNode;
      if(t && t!==listEl && t.getAttribute('href') && t.getAttribute('href').charAt(0)==='#') closeA();
    });
    function openA(){ ov.hidden=false; render(searchEl.value); setTimeout(function(){searchEl.focus();},30); }
    function closeA(){ ov.hidden=true; }
    march.addEventListener('click', openA);
    ov.querySelector('.march-close').addEventListener('click', closeA);
    ov.addEventListener('click', function(e){ if(e.target===ov) closeA(); });
    searchEl.addEventListener('input', function(){ render(this.value); });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape' && !ov.hidden) closeA(); });
  }

  // Paper / Night reading theme, persisted
  var btn=document.getElementById('mtheme');
  function apply(t){ if(t==='night'){root.setAttribute('data-theme','night'); btn.innerHTML='\\u2600 Paper';}
    else{root.removeAttribute('data-theme'); btn.innerHTML='\\u263e Night';} }
  try{ apply(localStorage.getItem('meridian-theme')||'paper'); }catch(e){}
  btn.addEventListener('click', function(){
    var t=root.getAttribute('data-theme')==='night'?'paper':'night';
    apply(t); try{ localStorage.setItem('meridian-theme',t); }catch(e){}
  });
})();
</script>
</body>"""
html = html.replace('</body>', JS, 1)

# ---- 7b. emitted-JS syntax gate ----
# One bad escape in the JS template silently kills the whole feedback IIFE
# (No. 63: thumbs dead from a literal newline in a string). Refuse to ship
# any page whose script blocks don't parse. Uses node when available.
import subprocess as _sp, tempfile as _tf, shutil as _sh
if _sh.which('node'):
    for _k, _scr in enumerate(re.findall(r'<script>(.*?)</script>', html, re.S)):
        with _tf.NamedTemporaryFile('w', suffix='.js', delete=False) as _fh:
            _fh.write(_scr); _scrpath = _fh.name
        _r = _sp.run(['node', '--check', _scrpath], capture_output=True, text=True)
        if _r.returncode != 0:
            raise SystemExit(f"FAIL: emitted script block {_k} has a JS syntax error — "
                             f"the page's interactivity would be dead:\n{_r.stderr[:500]}")
else:
    print('  (node not found — emitted-JS syntax gate skipped)')

# ---- 8. structural integrity gate ----
# The document must still be a well-formed page: intact doctype + <html> tag,
# and no hero markup before <body>. (No. 57 shipped with a hero spliced into
# the <html lang="en"> tag itself — a giant image above the page chrome.)
if not html.lstrip().startswith('<!DOCTYPE html>'):
    raise SystemExit("FAIL: output does not start with <!DOCTYPE html> — document corrupted")
import re as _re_gate
if not _re_gate.search(r'<html\s+lang="en">', html[:200]):
    raise SystemExit('FAIL: <html lang="en"> tag missing or corrupted in the first 200 bytes')
_bodyat = html.find('<body')
if _bodyat == -1:
    raise SystemExit("FAIL: no <body> tag in output")
_first_hero = html.find('<div class="ph-frame">')
if _first_hero != -1 and _first_hero < _bodyat:
    raise SystemExit("FAIL: a photo hero was injected before <body> — anchor resolution corrupted the document")

out.write_text(html)
print(f"wrote {out}  ({len(html)} bytes)  · {NPAGES} pages · {len(navitems)} nav items · {count} photo heroes")
