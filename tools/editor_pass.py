#!/usr/bin/env python3
"""The Reader's Editor — an independent cold read of the finished book.

    python3 tools/editor_pass.py text build/meridianNN.html > build/book.txt   # what the reviewer is given
    python3 tools/editor_pass.py check NN [--pages 24]                          # gate the recorded pass

Editor, 17 Nov 2026 (reader-approved). validate.py is a growing pile of
pattern checks, and a desk can satisfy every one of them and still write a
dull or confusing page. The Reader's Editor is a FRESH subagent that has seen
none of the research: it gets the book's text and the brief in
tools/editor_brief.md, reads every interior page as the reader would, and
returns a verdict per page. A page it would stop reading goes back to the
desk, once. The record is state/editor-pass/NNN.json:

  {"issue": 166, "rounds": 2, "reviewer": "fresh subagent, no research context",
   "pages": [{"page": 3, "desk": "The World", "keep_reading": 4,
              "says": "<the reviewer's own one-sentence account of what the page told it>",
              "weakest": "<the sentence it would cut or fix>", "verdict": "pass"},
             {"page": 8, ..., "keep_reading": 2, "verdict": "rework",
              "reason": "...", "fixed": "<what the desk changed>", "recheck": 4}]}

`check` fails when the file is missing, an interior page has no verdict, a
score is not 1-5, a "rework" page records neither a fix-and-recheck nor an
explicit "overruled" with a reason, or a page still stands at keep_reading <= 2.
build_status.py calls it, so no status.json — and no delivery — without it.
"""
import html as H
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def book_text(path):
    t = pathlib.Path(path).read_text()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    out = []
    for i, sec in enumerate(re.findall(r'<section[^>]*class="page[^"]*"[^>]*>(.*?)</section>', t, re.S), 1):
        sec = re.sub(r'<div class="fn">.*?</div>', "", sec, flags=re.S)          # sources are not prose
        sec = re.sub(r"</(p|div|h\d|tr|li)>", "\n", sec)
        txt = H.unescape(re.sub(r"<[^>]+>", " ", sec))
        txt = "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in txt.splitlines() if l.strip())
        out.append(f"\n===== PAGE {i} =====\n{txt}")
    return "\n".join(out)


def check(nn, pages):
    f = ROOT / "state" / "editor-pass" / f"{int(nn):03d}.json"
    if not f.exists():
        return [f"no Reader's Editor record at {f.relative_to(ROOT)} — run the pass (see tools/editor_brief.md)"]
    try:
        d = json.loads(f.read_text())
    except Exception as e:
        return [f"{f.name}: not valid JSON ({e})"]
    errs = []
    got = {int(p.get("page", 0)): p for p in d.get("pages", [])}
    for n in range(3, pages):                      # interior pages: 3 .. last-1
        p = got.get(n)
        if not p:
            errs.append(f"page {n}: no verdict recorded")
            continue
        k = p.get("keep_reading")
        if not isinstance(k, int) or not 1 <= k <= 5:
            errs.append(f"page {n}: keep_reading must be an integer 1-5")
            continue
        if len(str(p.get("says", "")).split()) < 6:
            errs.append(f"page {n}: 'says' must be the reviewer's own sentence on what the page told it")
        final = p.get("recheck", k)
        if p.get("verdict") == "rework" or k <= 2:
            if p.get("overruled"):
                if len(str(p["overruled"]).split()) < 8:
                    errs.append(f"page {n}: overruled without a real reason")
            elif not p.get("fixed") or not isinstance(p.get("recheck"), int):
                errs.append(f"page {n}: sent back (score {k}) but no fix and recheck recorded")
            elif final <= 2:
                errs.append(f"page {n}: still at {final} after the fix — rework it again or overrule with a reason")
    return errs


def main():
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "text":
        print(book_text(a[1]))
        return
    if len(a) >= 2 and a[0] == "check":
        pages = int(a[a.index("--pages") + 1]) if "--pages" in a else 24
        errs = check(a[1], pages)
        if errs:
            print("READER'S EDITOR: FAILED")
            for e in errs:
                print("  " + e)
            sys.exit(1)
        d = json.loads((ROOT / "state" / "editor-pass" / f"{int(a[1]):03d}.json").read_text())
        sc = [p.get("recheck", p["keep_reading"]) for p in d["pages"]]
        print(f"READER'S EDITOR: ok — {len(sc)} pages, mean {sum(sc) / len(sc):.2f}, "
              f"{sum(1 for p in d['pages'] if p.get('fixed'))} sent back and fixed")
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
