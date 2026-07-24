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

nav_links = "".join(f'<a class="mnav-link" href="#p{p}" data-target="p{p}">{lbl}</a>' for p, lbl in navitems)

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
  .page:not(.dark) .pgfoot{ position:static !important; margin-top:9mm; }

  /* photo heroes */
  .ph-frame{ margin:5mm 0 4mm; width:100%; }
  .ph-frame img{ width:100%; aspect-ratio:16/8; object-fit:cover; display:block;
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
.fbrow button{ background:none; border:.8pt solid var(--line); border-radius:10px;
  padding:1px 8px; cursor:pointer; color:inherit; font:inherit; line-height:1.6;
  transition:background .12s ease, border-color .12s ease, transform .12s ease, box-shadow .12s ease; }
.fbrow button:hover{ border-color:var(--gold); }
.fbrow button.on{ background:var(--vermilion); border-color:var(--vermilion); color:var(--paper);
  transform:scale(1.08); box-shadow:0 1px 5px rgba(193,70,46,.4); }
.fbrow.voted .fbk{ color:var(--vermilion); }
.fbrow .fbk{ letter-spacing:.08em; text-transform:uppercase; align-self:center; }
@media print { .ph-frame, #mprog, .m-chrome, .fbrow{ display:none !important; } }
</style>
"""

# ---- 4. assemble the head ----
html = html.replace('<link rel="stylesheet" href="meridian.css">',
                    FONTS + '\n<style>\n' + css + '\n</style>')
html = html.replace('</head>', SCREEN_CSS + '\n</head>')

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
        if _desk not in _seen_desks and _desk not in ('Contents',):
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

# ---- 5. body-top chrome ----
CHROME = ('<body>\n'
          '<div id="mprog"></div>\n'
          '<div class="m-chrome">\n'
          f'  <a class="pdf-dl" href="meridian-latest.pdf" download>⤓ Download the print edition (PDF) — No. {ISSUE} · {DATE}</a>\n'
          f'  <nav class="mnav">{nav_links}'
          '<button class="m-toggle" id="march" type="button">⧉ Archive</button>'
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

count, used_anchors = 0, set()
def inject(entry):
    global html, count
    anchor = entry["anchor"]
    idx = html.find(anchor)
    if idx == -1:
        print("  (skip hero, anchor not found:", anchor, ")")
        return
    if anchor in used_anchors:
        return
    rule = html.find('<div class="rule"></div>', idx)
    end = rule + len('<div class="rule"></div>')
    html = html[:end] + '\n' + hero(entry) + html[end:]
    used_anchors.add(anchor); count += 1

_standing_slugs = {e.get("asset") for e in images.get("standing", [])}
_recent_slugs = {e.get("asset") for e in images.get("heroes", [])
                 if e.get("issue") and e.get("asset")
                 and str(e["issue"]) != str(ISSUE)
                 and str(e["issue"]).isdigit() and int(e["issue"]) >= int(ISSUE) - 3}
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
# standing fallbacks: guarantee photos even when the session assigned none
for entry in images.get("standing", []):
    inject(entry)
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
  var API='https://marktan.ai/api/feedback', ISS=document.querySelector('.pdf-dl');
  var issue=(ISS&&(ISS.textContent.match(/No\\.\\s*(\\d+)/)||[])[1])||'';
  function post(p){ try{ fetch(API,{method:'POST',headers:{'Content-Type':'text/plain'},body:JSON.stringify(p)}); }catch(e){} }
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
  });
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
  var links=[].slice.call(document.querySelectorAll('.mnav-link'));
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

  // active desk in the nav via IntersectionObserver
  var byId={}; links.forEach(function(a){ byId[a.dataset.target]=a; });
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(e.isIntersecting){
        var a=byId[e.target.id];
        if(a){ links.forEach(function(l){l.classList.remove('active');}); a.classList.add('active');
          a.scrollIntoView({inline:'center',block:'nearest'}); }
      }
    });
  },{rootMargin:'-45% 0px -50% 0px'});
  pages.forEach(function(p){ if(byId[p.id]) io.observe(p); });

  // offset smooth-scroll so the sticky chrome doesn't cover the target
  function chromeH(){ return chrome?chrome.getBoundingClientRect().height:0; }
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
    function render(q){
      q=(q||'').toLowerCase().trim();
      var items=data.issues.filter(function(it){
        if(!q) return true;
        return (it.no+' '+it.date+' '+it.mode+' '+it.spine+' '+it.title+' '+it.quote+' '+it.author+' '+it.text).toLowerCase().indexOf(q)>=0;
      });
      ctEl.textContent=items.length+' of '+data.issues.length+' issues';
      if(!items.length){ listEl.innerHTML='<div class="march-none">No issues match \\u201c'+esc(q)+'\\u201d.</div>'; return; }
      listEl.innerHTML=items.map(function(it){
        var acts= it.href ? '<a href="'+it.href+'">'+(it.current?'Read · current':'Read')+'</a>' : '<span class="na">git history only</span>';
        if(it.pdf) acts+='<a class="pdf" href="'+it.pdf+'" download>PDF</a>';
        return '<div class="marchi"><div class="no">No. '+it.no+' &middot; '+esc(it.date)+(it.mode?' <span class="mode">&middot; '+esc(it.mode)+'</span>':'')+'</div>'+
          (it.title?'<div class="ti">'+esc(it.title)+'</div>':'')+
          (it.spine?'<div class="sp">'+esc(it.spine)+'</div>':'')+
          '<div class="acts">'+acts+'</div></div>';
      }).join('');
    }
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

out.write_text(html)
print(f"wrote {out}  ({len(html)} bytes)  · {NPAGES} pages · {len(navitems)} nav items · {count} photo heroes")
