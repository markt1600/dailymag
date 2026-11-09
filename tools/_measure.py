#!/usr/bin/env python3
"""Visible-character meter per page .cols2 — the WRITE-TO-LENGTH check (target 3,200-3,400)."""
import re,sys,html,pathlib
for f in sys.argv[1:]:
    s=pathlib.Path(f).read_text()
    tot=[]
    for m in re.finditer(r'<div class="cols2"[^>]*>', s):
        i=m.end(); depth=1; j=i
        for t in re.finditer(r'<(/?)div\b[^>]*?(/?)>', s[i:]):
            if t.group(2)=='/': continue
            depth += -1 if t.group(1) else 1
            if depth==0: j=i+t.start(); break
        txt=html.unescape(re.sub(r'<[^>]+>',' ',s[i:j]))
        tot.append(len(re.sub(r'\s+',' ',txt).strip()))
    flag=''
    if tot:
        mx=max(tot)
        flag=' <<< OVER' if mx>3320 else (' <<< under' if mx<3050 else ' ok')
    print(f"{pathlib.Path(f).name}: cols2={tot}{flag}")
