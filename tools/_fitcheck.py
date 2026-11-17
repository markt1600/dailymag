#!/usr/bin/env python3
"""Rough pre-render fit check: visible characters in a page's column stream,
any full-width table/strip, and the sources block. Calibrated on No. 165:
cols2 3000-3300 + sources 1300-1700, total <= ~5000, fits an A4 interior page."""
import re, html, sys, pathlib, glob
def measure(t):
    try: i = t.index('<div class="cols2">')
    except ValueError: return None
    j = t.index('<div class="pgfoot">')
    mid = t[i:j]
    mid = re.sub(r'<svg.*?</svg>', ' ', mid, flags=re.S)
    mid = re.sub(r'<div class="ph-frame">.*?</div>\s*</div>', ' ', mid, flags=re.S)
    k = mid.find('<div class="tbl-wrap">')
    cols = mid if k < 0 else mid[:k]
    rest = '' if k < 0 else mid[k:]
    def vis(s): return len(' '.join(html.unescape(re.sub('<[^>]+>', ' ', s)).split()))
    fn = re.search(r'<div class="fn">(.*?)</div>', t, re.S)
    return vis(cols), vis(rest), vis(fn.group(1)) if fn else 0
for f in sorted(sys.argv[1:] or glob.glob('build/pages/p*.html'),
                key=lambda x: int(re.search(r'p(\d+)', x).group(1))):
    t = pathlib.Path(f).read_text()
    m = measure(t)
    if not m: print(f"{f}: no .cols2"); continue
    c, d, s = m
    tot = c + d + s
    flag = "OVER " if tot > 5050 else ("thin " if tot < 4100 else "ok   ")
    print(f"{flag}{f}: cols2={c} fullwidth={d} sources={s} total={tot}")
