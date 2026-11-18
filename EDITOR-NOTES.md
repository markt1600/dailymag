# EDITOR'S STANDING NOTES — read after the routine prompt, before the spec

Dated notes from the reader and the editor that are NEWER than the routine prompt. Where a note
conflicts with the prompt, **the note wins**; the spec (`meridian-brand-prompt.md`) carries the full
rule and `validate.py` / `qa.py` enforce it. Newest first. Notes are removed once the prompt says the same.

## 18 Nov 2026 — THE FOUR is the point of the Macro Desk (gated from No. 167)
The reader, on No. 166: "I found no mention of VWRA, PIMCO Income, Gold or BTC. The core of the macro
desk, after all the analysis, is to apply it to these investments and explain / predict movement."
* The four instruments are **VWRA**, **PIMCO Income** (the PIMCO GIS Income Fund — it replaces the
  generic "global bonds / AGGU" proxy everywhere), **gold** and **bitcoin**. Name them; never write
  "shares, bonds, gold and bitcoin" in their place, and never say the reader holds them.
* Page one of the desk carries a `.chatter` box labelled **"The Four · … VWRA, PIMCO Income, Gold And
  Bitcoin"**. It REPLACES The Verdict, and The Levels table is optional (drop it if the page is tight —
  the yields, the dollar and oil are in the prose). Four paragraphs, in that order, each opening with
  the instrument's name in bold: its level or return read at source, what moved it in plain words,
  and **"Lean:"** — which way the desk expects it to move over the coming week and what would prove
  that wrong. About 30 words each. The live No. 166 p14 is the worked example.
* **PIMCO Income is tracked in BOTH currencies (the reader, 18 Nov: "PIMCO GIS Income Fund in SGD and
  USD").** Print the SGD-hedged class and the US-dollar class side by side in the PIMCO Income
  paragraph — 1-week, 1-month and 3-month total return and the 12-month dividend yield for each — and
  say in a clause why they differ when they do (the hedge's cost is the gap between Singapore and US
  short rates). One Lean covers the fund; add a second clause only if the two classes should diverge.
* Sources that work from the sandbox: VWRA's NAV from the Vanguard product page. PIMCO Income from the
  POEMS fund finder, which shows returns and dividend yield but no price and no date (say so):
  SGD-hedged — poems.com.sg/fund-finder/pimco-gis-inc-admin-sgd-hedged-income-ie00b91rq825-556842/ ;
  USD — poems.com.sg/fund-finder/pimco-gis-inc-e-usd-inc-ie00b8k7v925-556231/ . PIMCO's own pages do
  not render a price; try them once for a NAV, then use POEMS. Monthly, read the fund's duration and
  yield from PIMCO's factsheet and say what they imply. Gold from a named spot quote; bitcoin is
  fetched (`macro_ledger.py fetch`). Record them: `python3 tools/macro_ledger.py record
  vwra|pimco_income_1w|pimco_income_usd_1w|gold VALUE --asof … --source …`.
* Log each Lean in `state/predictions.json` with a check-by a week out. Four leans from No. 166 fall
  due on 25 November: grade them in print that day and on Saturday's Scoreboard, right or wrong.

## 18 Nov 2026 — THE DIARY ROW and THE TYPE WEIGHT AUDIT (gated from No. 167)
The reader, on No. 166: "there is drift in the font, and the calendar entries look a bit strange."
Each agenda row is a date chip, a short bold `.evt-name` (the event and its series, at most twelve
words, ★ first on a starred pick) and an `.evt-meta` line with everything else. Never the whole entry
in `.evt-name`. `qa.py` fails any page where more than 40 per cent of reading-size text is bold serif.
The repaired No. 166 p20 is the form.

## 17 Nov 2026 — THE WEEK IN REVIEW, every Sunday (gated from No. 170)
The weekly drift report is the last page of Sunday's book before the back cover, headed
"Meridian · The Reader's Editor / The Week in Review". See THE WEEKLY DRIFT REPORT in the spec.
