#!/usr/bin/env python3
"""Map QA overflow back to source page files and print the exact character cut
each page needs. Usage: tools/_fit.py <built.html> <built.pdf> [chars_per_mm]"""
import re, sys, subprocess, json, os
html_path, pdf_path = sys.argv[1], sys.argv[2]
CPM = float(sys.argv[3]) if len(sys.argv) > 3 else 19.0
out = subprocess.run([sys.executable, "tools/qa.py", html_path, pdf_path],
                     capture_output=True, text=True).stdout
gaps = {}
for m in re.finditer(r'page\s+(\d+):\s+gap\s+(-?[\d.]+)mm(.*)', out):
    gaps[int(m.group(1))] = (float(m.group(2)), m.group(3))
src = open(html_path, encoding='utf-8').read()
secs = re.split(r'(?=<section id="p\d+")', src)[1:]
print(f"{'pdf':>4} {'file':>6} {'gap':>8}  action  (chars/mm={CPM})")
for i, sec in enumerate(secs, 1):
    pid = re.match(r'<section id="(p\d+)"', sec).group(1)
    gap, note = gaps.get(i, (0.0, ' (not measured)'))
    if 'exempt' in note:
        act = 'exempt'
    elif gap < 0:
        act = f"CUT ~{int((-gap + 5) * CPM)} chars"
    elif gap < 4:
        act = 'tight — ok'
    elif gap > 22:
        act = f"ADD ~{int((gap - 8) * CPM)} chars"
    else:
        act = 'fits'
    print(f"{i:>4} {pid:>6} {gap:>7.1f}mm  {act}")
