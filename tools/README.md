# MERIDIAN build tools

Reusable, committed build infrastructure. (`build/` is scratch and git-ignored;
these live here so they persist and version.) The brand brief in
`../meridian-brand-prompt.md` remains the authoritative editorial spec.

## Pipeline

Assemble the edition into `build/meridianNN.html` (one `<section class="page">`
per page, linking `meridian.css`), then:

```bash
tools/build.sh 38 "10 July 2026"     # validate -> render -> QA gate -> photo edition
```

On a clean QA pass, place the deliverables and refresh state:

```bash
cp build/meridian38.pdf  meridian-latest.pdf
cp build/index.html      index.html
# ...edit the ledgers in meridian-brand-prompt.md, then:
python3 tools/extract_state.py       # regenerate state/*.json
git add index.html meridian-latest.pdf meridian-brand-prompt.md state/ && git commit …
```

## Scripts

| script | does |
|---|---|
| `setup.sh` | Idempotent toolchain install (Playwright+Chromium, poppler, ImageMagick, Lora/Poppins). Runs at SessionStart via `.claude/settings.json`. |
| `render.py` | `meridianNN.html → PDF` via headless Chromium with the fixed brand render params. |
| `qa.py` | **Full-book QA gate.** Measures each page's real content overflow **in the DOM** (not pixel heuristics) so it catches content colliding with the absolutely-positioned footer — the failure the old trailing-white detector was blind to. Hard-fails a real collision (blocks the build); flags *tight* (<4mm clear) and *underfill* as advisories. Also writes 6-up contact sheets for the mandatory eyeball pass. |
| `validate.py` | Pre-flight lint: per-page footnote numbering is a gapless 1..k with matching sources; cross-references (`p15`) point to pages that exist. |
| `make_photo_edition.py` | Derives `index.html` (the Photo Edition). Inlines CSS + fonts; adds the sticky desk-nav, reading-progress bar, Paper/Night reading toggle, auto-linked in-issue cross-references, responsive page scaling, honest sign-based market arrows, and verified photo heroes from `state/images.json`. All screen-only; print untouched. |
| `extract_state.py` | Parses the brand-prompt ledger tables into `state/*.json` (issue log w/ next-number + used-quotes, coverage subjects, destinations) for fast, reliable dedup. |
| `build.sh` | Runs validate → render → QA → photo-edition in order. |

## `state/`

Generated, machine-readable state (regenerate with `extract_state.py` after
editing the ledgers). `images.json` is hand-maintained: the verified-image
library + per-issue photo-hero assignments (only add a file after confirming its
subject/licence on the Commons page from a network-connected session).

## Notes

- The tight-footer advisories from `qa.py` are a **print-only** concern; on
  screen the Photo Edition uses `height:auto` with a static footer, so there is
  no collision there.
- `pypdf` is intentionally not used (a system cryptography/cffi conflict crashes
  its import); page counts come from `pdfinfo`.
