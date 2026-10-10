#!/usr/bin/env python3
"""Early-warning phrase-recycling meter — the same computation validate.py's
hard gate uses, runnable on a partial draft so recycling is caught while the
page is being written instead of at the gate.

Usage: python3 tools/_recycle.py build/pages/p*.html          (or a built file)
Ceiling for No. 129 is 30 (max(30, 70-(NN-52))).
"""
import re, sys, pathlib, html as H

ISSNO = 129
CEILING = max(30, 70 - max(0, ISSNO - 52))

def prose(h):
    parts  = re.findall(r'<p class="body[^"]*">(.*?)</p>', h, re.S)
    parts += re.findall(r'<div class="dek">(.*?)</div>', h, re.S)
    parts += re.findall(r'<div class="pull">(.*?)</div>', h, re.S)
    return re.sub(r'<[^>]+>', ' ', ' '.join(parts)).lower()

STOP = set('the a an of to in on for and or but with as at by from is are was were be it its this that'.split())

def grams(text):
    words = re.findall(r"[a-z']+", text)
    return {' '.join(words[i:i+4]) for i in range(len(words)-3)
            if sum(1 for w in words[i:i+4] if w not in STOP) >= 3}

arch = sorted(pathlib.Path('archive').glob('no-*/index.html'),
              key=lambda f: int(re.search(r'no-(\d+)', str(f)).group(1)))
arch = [f for f in arch if int(re.search(r'no-(\d+)', str(f)).group(1)) < ISSNO][-3:]
prev = ' '.join(prose(f.read_text()) for f in arch)
prev_grams = grams(prev)
print(f"comparing against: {', '.join(f.parent.name for f in arch)}  ({len(prev_grams)} distinctive 4-grams)")

draft = ' '.join(prose(pathlib.Path(p).read_text()) for p in sys.argv[1:])
mine = grams(draft)
hits = sorted(mine & prev_grams)
print(f"\nrecycled: {len(hits)} / ceiling {CEILING}   (warn band starts at {CEILING-15})")
for g in hits:
    print("  ·", g)
