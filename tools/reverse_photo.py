#!/usr/bin/env python3
"""Reverse the Photo-Edition transform: index.html -> a print-clean build source.
Strips injected chrome/CSS/JS/heroes/feedback so the result links meridian.css
and is a valid print HTML to edit for the next issue. Not perfect, but exact on
structure. Usage: python3 tools/reverse_photo.py index.html build/out.html"""
import re, sys, pathlib
src = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
h = src.read_text()

# 1. head: replace preconnect+inlined-style+screen-css block up to </head>
i = h.find('<link rel="preconnect" href="https://fonts.googleapis.com">')
j = h.find('</head>')
head = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<link rel="stylesheet" href="meridian.css">\n')
h = h[:i] + head + h[j:]

# 2. body chrome: from <body> to first <section ...class="page"
b = h.find('<body>')
s = h.find('<section', b)
h = h[:b] + '<body>\n' + h[s:]

# 3. trailing JS: from the make_photo script to </body>
e = h.rfind('</section>')
tail = h.find('<script>', e)
if tail != -1:
    h = h[:tail].rstrip() + '\n</body>\n</html>\n'

# 4. strip injected in-section artefacts
h = re.sub(r'\s*<div class="fbrow"[^>]*>.*?</div>', '', h, flags=re.S)
h = re.sub(r'\s*<div class="ph-frame">.*?</div>\s*(?=<div class="ph-cred")', '', h, flags=re.S)  # safety
h = re.sub(r'\s*<div class="ph-frame">.*?</div>', '', h, flags=re.S)
h = re.sub(r'<a class="xref" href="#p\d+">(p\d+)</a>', r'\1', h)
h = re.sub(r'<section id="p\d+" class="page', '<section class="page', h)

out.write_text(h)
print(f"wrote {out} ({len(h)} bytes); sections:", h.count('<section class="page'))
