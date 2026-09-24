#!/usr/bin/env python3
"""Visible-character meter per page. Measures the .cols2 body stream (what sets
page height) separately from the header block and the sources footer.
Target: ~3,200-3,400 visible chars in .cols2. Usage: tools/_chars.py <file.html>"""
import re, sys, html as H

def vis(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', H.unescape(s)).strip()

src = open(sys.argv[1], encoding='utf-8').read()
for sec in re.split(r'(?=<section id="p\d+")', src)[1:]:
    pid = re.match(r'<section id="(p\d+)"', sec).group(1)
    # the .cols2 stream: from the first <div class="cols2"> to the <div class="pgfoot">
    m = re.search(r'<div class="cols2"[^>]*>(.*?)(?=<div class="pgfoot")', sec, re.S)
    body = vis(m.group(1)) if m else ''
    foot = vis(re.search(r'<div class="pgfoot">(.*)', sec, re.S).group(1)) if 'pgfoot' in sec else ''
    head = vis(sec.split('<div class="cols2"')[0]) if m else vis(sec)
    n = len(body)
    flag = ''
    if 'class="page dark"' in sec[:80]: flag = ' (cover-type)'
    elif not m: flag = ' (no .cols2)'
    elif n > 3500: flag = '  <-- OVER'
    elif n < 2900: flag = '  <-- UNDER'
    print(f"{pid:>4}  cols2={n:5d}  head={len(head):4d}  foot={len(foot):4d}{flag}")
