#!/usr/bin/env python3
"""Assemble build/meridianNN.html from build/pages/pNN.html fragments + the
head (build/pages/_head.html) and tail (build/pages/_tail.html)."""
import sys, glob, re, os
NN = sys.argv[1]
out = f"build/meridian{NN}.html"
head = open("build/pages/_head.html", encoding="utf-8").read()
frags = sorted(glob.glob("build/pages/p*.html"),
               key=lambda f: int(re.search(r'p(\d+)\.html', f).group(1)))
body = "\n\n".join(open(f, encoding="utf-8").read().rstrip() for f in frags)
tail = open("build/pages/_tail.html", encoding="utf-8").read()
with open(out, "w", encoding="utf-8") as fh:
    fh.write(head + "\n" + body + "\n" + tail)
print(f"assembled {out} ({len(frags)} pages, {os.path.getsize(out)} bytes)")
