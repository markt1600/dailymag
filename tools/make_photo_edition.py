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

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">')

# ---- 1. number the pages and read their desk names from the running header ----
counter = {"n": 0}
def add_id(m):
    counter["n"] += 1
    return f'<section id="p{counter["n"]}" class="page' + m.group(1)
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
}
/* keep the print deliverable pristine */
@media print { .ph-frame, #mprog, .m-chrome{ display:none !important; } }
</style>
"""

# ---- 4. assemble the head ----
html = html.replace('<link rel="stylesheet" href="meridian.css">',
                    FONTS + '\n<style>\n' + css + '\n</style>')
html = html.replace('</head>', SCREEN_CSS + '\n</head>')

# ---- 5. body-top chrome ----
CHROME = ('<body>\n'
          '<div id="mprog"></div>\n'
          '<div class="m-chrome">\n'
          f'  <a class="pdf-dl" href="meridian-latest.pdf" download>⤓ Download the print edition (PDF) — No. {ISSUE} · {DATE}</a>\n'
          f'  <nav class="mnav">{nav_links}'
          '<button class="m-toggle" id="mtheme" type="button">☾ Night</button></nav>\n'
          '</div>')
html = html.replace('<body>', CHROME, 1)

# ---- 6. photo heroes from images.json (subject-verified / representative) ----
def hero(entry):
    fn = entry["file"]
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + fn.replace(' ', '%20') + "?width=1600"
    cred = entry["caption"] + ' Source: Wikimedia Commons — "File:' + fn + '" · ' + entry["license"]
    if entry.get("author"):
        cred += " · " + entry["author"]
    cred += ". " + ("Subject verified from the Commons file page." if entry.get("specific") else "Representative image; subject class verified from the Commons file page.")
    alt = entry["caption"].split(" — ")[0]
    return (f'  <div class="ph-frame"><img src="{url}" alt="{alt}" loading="lazy">'
            f'<div class="ph-cred">{cred}</div></div>\n')

count = 0
for entry in images.get("heroes", []):
    if entry.get("issue") and str(entry["issue"]) != str(ISSUE):
        continue
    anchor = entry["anchor"]
    idx = html.find(anchor)
    if idx == -1:
        print("  (skip hero, anchor not found:", anchor, ")")
        continue
    rule = html.find('<div class="rule"></div>', idx)
    end = rule + len('<div class="rule"></div>')
    html = html[:end] + '\n' + hero(entry) + html[end:]
    count += 1

# ---- 7. behaviour (inline, CSP-safe) ----
JS = """
<script>
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
