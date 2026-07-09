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


def parse(note):
    mode = spine = title = ""
    m = re.match(r'\s*\*\*([^*]+)\*\*', note)
    if m:
        mode = clean(m.group(1))
    m = re.search(r'(?:Issue spine|Editorial theme|Theme tag)\s*:\s*\*([^*]+)\*', note)
    if m:
        spine = clean(m.group(1))
    m = re.search(r'THE LONG READ[^:]*:\s*\*\*[“"”\'‘’]*([^”"”*\'‘’]+)', note)
    if m:
        title = clean(m.group(1))
    return mode, spine, title


issues = []
for it in sorted(il["issues"], key=lambda x: -x["no"]):
    no = it["no"]
    mode, spine, title = parse(it.get("note", ""))
    if no == CURRENT:
        href, pdf = "index.html", "meridian-latest.pdf"
    else:
        d = arch / f"no-{no}"
        href = f"archive/no-{no}/index.html" if (d / "index.html").exists() else None
        pdf = f"archive/no-{no}/meridian-latest.pdf" if (d / "meridian-latest.pdf").exists() else None
    issues.append({
        "no": no, "date": it.get("date", ""), "mode": mode, "spine": spine,
        "title": title, "quote": it.get("quote", ""), "author": clean(it.get("author", "")),
        "href": href, "pdf": pdf, "current": no == CURRENT,
        "text": clean(it.get("note", ""))[:TEXT_CAP],
    })

arch.mkdir(exist_ok=True)
manifest = {"current": CURRENT, "count": len(issues),
            "browsable": sum(1 for i in issues if i["href"]), "issues": issues}
(arch / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
print(f"manifest: {len(issues)} issues, {manifest['browsable']} browsable, current No. {CURRENT}")
