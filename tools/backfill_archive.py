#!/usr/bin/env python3
"""One-time (re-runnable) backfill: recover past Photo Editions from git history
into archive/no-NN/. For each commit that touched index.html (newest first), read
that version, identify its issue number from the cover topbar, and keep the
newest/most-complete copy per issue. Best-effort PDF recovery from the same
commit. The current root issue is left where it is (not archived here).

Usage:  python3 tools/backfill_archive.py [current_no]
"""
import re, sys, subprocess, pathlib

CURRENT = sys.argv[1] if len(sys.argv) > 1 else None
arch = pathlib.Path("archive"); arch.mkdir(exist_ok=True)


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True)


def git_bytes(ref):
    r = subprocess.run(["git", "show", ref], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def issue_no(html):
    # cover topbar: "No. NN · Singapore"; fall back to the first "No. NN" in the
    # cover region (first ~4000 chars) — reliably the topbar, before any body callback.
    m = re.search(r'No\.?\s*(\d{1,3})\s*(?:&middot;|&nbsp;|·|\s)*Singapore', html)
    return int(m.group(1)) if m else None


commits = git("log", "--format=%H", "--", "index.html").stdout.split()
seen = set()
recovered = []
for h in commits:
    html = git_bytes(f"{h}:index.html")
    if not html:
        continue
    try:
        text = html.decode("utf-8", "ignore")
    except Exception:
        continue
    no = issue_no(text)
    if not no or no in seen:
        continue
    seen.add(no)
    if CURRENT and str(no) == str(CURRENT):
        continue  # current issue lives at repo root
    d = arch / f"no-{no}"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_bytes(html)
    # best-effort PDF from the same commit
    pdf = None
    for cand in (f"meridian-latest.pdf", f"meridian{no}.pdf", f"meridian-{no}.pdf"):
        b = git_bytes(f"{h}:{cand}")
        if b:
            (d / "meridian-latest.pdf").write_bytes(b)
            pdf = True
            break
    recovered.append((no, bool(pdf)))

recovered.sort(reverse=True)
print(f"recovered {len(recovered)} past issue(s) into archive/:")
for no, pdf in recovered:
    print(f"  No.{no:<3} html{'  + pdf' if pdf else ''}")
