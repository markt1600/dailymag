#!/usr/bin/env python3
"""MERIDIAN render — HTML -> PDF via headless Chromium (Playwright).

Usage:  python3 tools/render.py build/meridianNN.html build/meridianNN.pdf

Render parameters are fixed by the brand spec and must not change:
print media, prefer_css_page_size, print_background, networkidle + settle,
zero margins, absolute path. Uses whatever Chromium the local Claude Code
environment provides (PW_CHROMIUM env override, else the pinned sandbox path,
else Playwright's default).
"""
import os, sys, time, pathlib
from playwright.sync_api import sync_playwright

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/meridian.html").resolve()
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else src.with_suffix(".pdf"))

# Prefer an explicit path; fall back to the pinned sandbox browser; else default.
exe = os.environ.get("PW_CHROMIUM")
if not exe and os.path.exists("/opt/pw-browsers/chromium"):
    exe = "/opt/pw-browsers/chromium"

with sync_playwright() as p:
    launch = {"executable_path": exe} if exe else {}
    b = p.chromium.launch(**launch)
    page = b.new_page()
    page.emulate_media(media="print")
    page.goto(f"file://{src}", wait_until="networkidle")
    time.sleep(2.5)  # settle fonts/layout
    page.pdf(path=str(out), prefer_css_page_size=True, print_background=True,
             margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print("rendered", out)
