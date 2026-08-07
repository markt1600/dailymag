#!/usr/bin/env python3
"""Build archive/manifest.json — the index the Photo Edition's Archive panel
reads (embedded at build time so it works even from file://).

For every issue in state/issue-log.json it emits searchable metadata (no, date,
mode, spine, Long-Read title, quote/author, a condensed text blob) and, where a
browsable Photo Edition exists (archive/no-NN/index.html, or the current issue at
root), a link + optional PDF. Issues with no recovered file are metadata-only
(searchable, not openable).

Usage:  python3 tools/build_manifest.py [current_no]
"""
import re, sys, json, pathlib

CURRENT = int(sys.argv[1]) if len(sys.argv) > 1 else None
il = json.loads(pathlib.Path("state/issue-log.json").read_text())
if CURRENT is None:
    CURRENT = max((i["no"] for i in il["issues"]), default=0)
arch = pathlib.Path("archive")

TEXT_CAP = 14000   # effectively full note; enables offline full-text search


def clean(s):
    s = re.sub(r'\*\*|\*|`|<[^>]+>', '', s)
    s = re.sub(r'&[a-z]+;', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def from_archive(no):
    """Fallback: pull the essay title + contents headline straight from the
    archived Photo Edition — the pages always carry them, however loosely the
    session wrote its Issue Log row."""
    # Candidates in trust order: the archived Photo Edition; the staged print
    # source (present at build time — build.sh runs this before the new edition
    # reaches root); root itself. Each is only trustworthy if it actually holds
    # THIS issue — for the current issue root may still be the PREVIOUS edition
    # (this is how No. 64 shipped in the archive listing titled as No. 63, and
    # No. 65 shipped with no title at all).
    h = None
    for f in (pathlib.Path(f"archive/no-{no}/index.html"),
              pathlib.Path(f"build/meridian{no}.html"),
              pathlib.Path("index.html")):
        if f.exists():
            t = f.read_text(errors="ignore")
            if re.search(rf'No\.\s*{no}\s*(?:&middot;|·)\s*Singapore', t):
                h = t
                break
    if h is None:
        return "", ""
    title = sub = ""
    secs = re.split(r'(?=<section[^>]*class="page)', h)
    lr = [x for x in secs if 'Meridian · The Long Read' in x[:400]]
    if lr:
        m = re.search(r'<div class="hed[^"]*"[^>]*>(.*?)</div>', lr[0], re.S)
        if m:
            title = clean(re.sub(r'<[^>]+>', '', m.group(1)))
    p2 = [x for x in secs if 'Meridian · Contents' in x[:400]]
    if p2:
        m = re.search(r'<div class="hed[^"]*"[^>]*>(.*?)</div>', p2[0], re.S)
        if m:
            sub = clean(re.sub(r'<[^>]+>', '', m.group(1)))
    if sub.lower() == "contents":   # the fixed page-2 layout heds the page
        sub = ""                    # itself "Contents" — that's not a spine
    return title, sub

def articles_for(no, is_current):
    """Article-level search index: for issues whose pages carry section ids,
    one entry per desk page with a headline — {a: anchor, d: desk, h: headline,
    x: snippet}. Lets the archive search deep-link to the article itself."""
    f = pathlib.Path("index.html") if is_current else pathlib.Path(f"archive/no-{no}/index.html")
    if not f.exists():
        return []
    h = f.read_text(errors="ignore")
    out = []
    for sec in re.split(r'(?=<section[^>]*class="page)', h):
        mid = re.match(r'<section id="(p\d+)"', sec)
        mrh = re.search(r'Meridian · ([^<]+)</span>', sec[:400])
        if not mid or not mrh:
            continue
        desk = clean(mrh.group(1))
        if desk in ("Contents",):
            continue
        mh = re.search(r'<div class="hed[^"]*"[^>]*>(.*?)</div>', sec, re.S)
        if not mh:
            continue
        hed = clean(re.sub(r'<[^>]+>', '', mh.group(1)))
        md = re.search(r'<div class="dek">(.*?)</div>', sec, re.S)
        bodies = re.findall(r'<p class="body[^"]*">(.*?)</p>', sec, re.S)[:2]
        raw = (md.group(1) if md else '') + ' ' + ' '.join(bodies)
        snip = clean(re.sub(r'<[^>]+>', ' ', raw))[:220]
        out.append({"a": mid.group(1), "d": desk, "h": hed, "x": snip})
    return out

def parse(note):
    mode = spine = title = ""
    m = re.match(r'\s*\*\*([^*]+)\*\*', note)
    if m:
        mode = clean(m.group(1))
    m = re.search(r'(?:Issue spine|Editorial theme|Theme tag)\s*:\s*\*([^*]+)\*', note)
    if m:
        spine = clean(m.group(1))
    else:
        # trimmed note style (No. 63+): Spine = **The Unsigned** — the gap …
        m = re.search(r'Spine\s*[=:]\s*\*\*([^*]+)\*\*(?:\s*[—–-]\s*([^.,(]{4,160}))?', note)
        if m:
            spine = clean(m.group(1) + (' — ' + m.group(2) if m.group(2) else ''))
    m = re.search(r'THE LONG READ[^:]*:\s*\*\*[“"”\'‘’]*([^”"”*\'‘’]+)', note)
    if not m:   # trimmed note style: Essay: Type-B historical — "The Fine Print" (…)
        m = re.search(r'Essay:[^"“”]{0,80}[“"]([^”"]{4,80})[”"]', note)
    if not m:   # variant phrasings sessions have used
        m = re.search(r'(?:Essay type|LONG READ|THE ESSAY)[^(“"]*[(]?[“"”]\s*([^”"“]{4,60})[”"]', note)
    if not m:
        m = re.search(r'[“"]([^”"]{4,60})[”"]\s*[—–-]\s*(?:the essay|Type [AB])', note)
    if m:
        title = clean(m.group(1))
    return mode, spine, title


issues = []
for it in sorted(il["issues"], key=lambda x: -x["no"]):
    no = it["no"]
    mode, spine, title = parse(it.get("note", ""))
    if not title or not spine:
        a_title, a_sub = from_archive(no)
        title = title or a_title
        spine = spine or a_sub
    arts = articles_for(no, is_current=(str(no) == str(CURRENT)))
    if no == CURRENT:
        href, pdf = "index.html", "meridian-latest.pdf"
    else:
        d = arch / f"no-{no}"
        href = f"archive/no-{no}/index.html" if (d / "index.html").exists() else None
        pdf = f"archive/no-{no}/meridian-latest.pdf" if (d / "meridian-latest.pdf").exists() else None
    issues.append({
        "no": no, "date": it.get("date", ""), "mode": mode, "spine": spine,
        "title": title, "quote": it.get("quote", ""), "author": clean(it.get("author", "")),
        "articles": arts,
        "href": href, "pdf": pdf, "current": no == CURRENT,
        "text": clean(it.get("note", ""))[:TEXT_CAP],
    })

arch.mkdir(exist_ok=True)
manifest = {"current": CURRENT, "count": len(issues),
            "browsable": sum(1 for i in issues if i["href"]), "issues": issues}
(arch / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
print(f"manifest: {len(issues)} issues, {manifest['browsable']} browsable, current No. {CURRENT}")
