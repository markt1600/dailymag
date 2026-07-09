#!/usr/bin/env python3
"""MERIDIAN full-book QA gate.

The old detector measured trailing whitespace and was structurally BLIND to the
failure mode that actually ships bad books: content overrunning the
absolutely-positioned footer (it read those pages as "0.1% - perfectly full").
This version measures the DOM directly in the browser — exact, not heuristic —
so it flags the real defect: a page whose content box extends into, or past, its
own .pgfoot.

For every interior page it prints:
  * overflow  — mm the content bottom pushes PAST the top of the footer block.
                > -TOL  => OVERSET (collision). This is the gate.
  * gap       — mm of clear space between the last content and the footer.
                large => UNDERFILL candidate (add sourced material).

It also rasterises the book and writes 6-up contact sheets, because the eyeball
is still the gate and the numbers are the smoke alarm. Cover (page 1) and back
cover (last page) are exempt — they are allowed to breathe.

Usage:  python3 tools/qa.py build/meridianNN.html [build/meridianNN.pdf]
Exit non-zero if any interior page is OVERSET, so the build refuses to finalize.
"""
import os, sys, glob, subprocess, pathlib
from playwright.sync_api import sync_playwright

# Calibrated against a real book: genuine collisions (body text printing through
# the footnote) measure ~ -15mm gap; hairline-tight-but-legible pages measure
# ~ -3..+3mm; comfortable pages >= +8mm. So:
OVERSET_FAIL_MM = 4.0    # content pushes > this far past the footer top => hard FAIL (overlap)
TIGHT_WARN_MM = 4.0      # clear gap below this (but not failing) => advisory TIGHT
UNDERFILL_MM = 40        # clear gap larger than this => underfill candidate (advisory)
DPI = 100

MEASURE_JS = r"""
() => {
  const pages = [...document.querySelectorAll('.page')];
  return pages.map((pg, i) => {
    const r = pg.getBoundingClientRect();
    const pxPerMm = r.height / 297;                 // .page is 297mm tall
    const foot = pg.querySelector('.pgfoot');
    let cbottom = r.top;
    pg.querySelectorAll('*').forEach(el => {
      if (foot && (el === foot || foot.contains(el))) return;
      if (el.classList && el.classList.contains('ph-frame')) return; // screen-only, print-hidden
      const b = el.getBoundingClientRect().bottom;
      if (b > cbottom) cbottom = b;
    });
    const footTop = foot ? foot.getBoundingClientRect().top : (r.bottom - 16 * pxPerMm);
    return {
      page: i + 1,
      dark: pg.classList.contains('dark'),
      hasFoot: !!foot,
      overflow_mm: (cbottom - footTop) / pxPerMm,   // >~0 => content hits the footer
      gap_mm: (footTop - cbottom) / pxPerMm          // clear space before the footer
    };
  });
}
"""


def main():
    html = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "build/meridian.html").resolve()
    pdf = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else html.with_suffix(".pdf")

    exe = os.environ.get("PW_CHROMIUM")
    if not exe and os.path.exists("/opt/pw-browsers/chromium"):
        exe = "/opt/pw-browsers/chromium"

    with sync_playwright() as p:
        launch = {"executable_path": exe} if exe else {}
        b = p.chromium.launch(**launch)
        page = b.new_page()
        page.emulate_media(media="print")
        page.goto(f"file://{html}", wait_until="networkidle")
        page.wait_for_timeout(1500)
        data = page.evaluate(MEASURE_JS)
        b.close()

    n = len(data)
    print(f"{n} pages measured (DOM, print media)\n")
    flagged, tight = [], []
    for d in data:
        i = d["page"]
        exempt = d["dark"] or not d["hasFoot"] or i == 1 or i == n
        tags = []
        if not exempt:
            if d["overflow_mm"] > OVERSET_FAIL_MM:
                tags.append(f"OVERSET (+{d['overflow_mm']:.1f}mm — footer collision)")
                flagged.append(i)
            elif d["gap_mm"] < TIGHT_WARN_MM:
                tags.append(f"tight ({d['gap_mm']:.1f}mm clear — aim >= 4mm)")
                tight.append(i)
            elif d["gap_mm"] > UNDERFILL_MM:
                tags.append(f"UNDERFILL ({d['gap_mm']:.0f}mm clear — add sourced material)")
        flag = "   <-- " + " · ".join(tags) if tags else ""
        note = "  [cover/exempt]" if exempt else ""
        print(f"page {i:2d}: gap {d['gap_mm']:6.1f}mm{note}{flag}")

    # rasterise for the eyeball + contact sheets
    if pdf.exists():
        d = pdf.parent
        for f in glob.glob(str(d / "allp-*.png")) + glob.glob(str(d / "sheet-*.png")):
            os.remove(f)
        subprocess.run(["pdftoppm", "-png", "-r", str(DPI), str(pdf), str(d / "allp")], check=True)
        pages = sorted(glob.glob(str(d / "allp-*.png")))
        print()
        for s in range(0, len(pages), 6):
            outn = str(d / f"sheet-{s // 6 + 1}.png")
            subprocess.run(["montage", *pages[s:s + 6], "-tile", "3x2", "-geometry", "+4+4", outn], check=True)
            print("wrote", outn)

    if tight:
        print(f"\nADVISORY: {len(tight)} tight page(s) (<4mm clear, legible): {tight} — open up if convenient.")
    if flagged:
        print(f"\nFAIL: {len(flagged)} interior page(s) overset (real footer collision): {flagged}")
        sys.exit(1)
    print("\nOK: no footer collisions. Confirm fill visually on the contact sheets.")


if __name__ == "__main__":
    main()
