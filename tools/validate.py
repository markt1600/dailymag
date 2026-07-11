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
