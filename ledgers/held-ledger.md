# The Held Ledger

Machine-readable memory for what the desk could not verify. Maintained with
`tools/held_ledger.py`, mirrored to `state/held-ledger.json` by
`tools/extract_state.py`, read by the Sunday drift report.

**Why this file exists (editor, 17 Nov 2026 — reader-approved).** Every Issue Log
note ends with a HELD list, and almost nothing on those lists was ever
revisited. Christmas Wonderland's ticket price was re-listed as held for seven
issues running; the Singapore radio-law question printed as open in No. 154.5
was answered only because the reader happened to commission No. 158.5. A held
item is a promise to the reader that the desk will come back. A promise has to
be a row with an age, not a clause in a note.

## The protocol

* **Every build opens with `python3 tools/held_ledger.py list --issue NN`** and
  works the list before it researches anything new: every `date` item whose Due
  has passed is checked today; every item flagged STALE (open fourteen issues)
  is resolved, converted to `ask`, or dropped with a reason; and the three
  oldest remaining `fact` items get a fresh attempt at source.
* **An answer goes into print.** A resolved item is printed where its story
  lives, as a one-line "Held since No. NN, now settled" in that desk's brief
  strip, with its source, and the row is closed with
  `held_ledger.py resolve ID NN "<the answer and the source>"`.
* **New holds are rows.** Anything the build could not verify and means to
  return to is added with `held_ledger.py add`. The Issue Log note's HELD
  section then lists the IDs opened, resolved and dropped this issue, not the
  prose again.
* **`ask` is honest.** An item only a human phone call or email can settle is
  kind `ask`. It is never silently dropped and never re-researched in circles;
  it stays listed for the reader.
* **Monday prints the account.** Monday's contents page carries a short strip
  headed "Held, Now Resolved": what was settled in the past week and where,
  what was dropped and why, and the two or three `ask` items most worth a call.
  `validate.py` fails a Monday book without it. If nothing was resolved, the
  strip says so and names what was re-checked.

Kinds: `fact` (an unverified claim), `date` (a scheduled release, checked on or
after Due), `ask` (needs a human). Status: `OPEN`, `RESOLVED`, `DROPPED`.

## Held Items

| ID | Held since | Desk | Kind | Item | Due | Status | Last checked | Outcome |
|---|---|---|---|---|---|---|---|---|
| H001 | 165 | Daily | date | Nvidia Q3, 18 Nov 05:20 SGT | 2026-11-18 | RESOLVED | 166 | No. 166: Nvidia reported Q3 FY2027 on EDGAR at 05:25 SGT on 18 Nov: revenue US$115.8bn, +103% year on year, data centre US$107.6bn (8-K accession 0001045810-26-000088, read at source) — p7 |
| H002 | 165 | Daily | fact | Oct NODX, due 08:30 today, unpublished at press (EnterpriseSG 500s) |  | RESOLVED | 166 | No. 166: EnterpriseSG MR 059/26 published 17 Nov: October NODX +79.8% year on year, electronics +73.9, non-electronics +81.9, shipments to the United States +214.6 (release and 7-page PDF read at source) — p5 |
| H003 | 165 | Daily | fact | Federal Register publication and effective date of RIN 0694-AK50 |  | RESOLVED | 166 | No. 166: RIN 0694-AK50 is on public inspection as Federal Register document 2026-23529, scheduled for publication 19 Nov 2026 and effective on publication, comments due 60 days after (public-inspection PDF read at source) — p5 |
| H004 | 165 | Daily | fact | whether Shenzhen and Berlin happen |  | RESOLVED | 166 | No. 166: Shenzhen confirmed on the record: China's foreign ministry announced on 16 Nov that Xi will hold the China-Russia-US summit with Putin and Trump in Shenzhen on 19 Nov. Berlin agreed in principle at the 17 Nov online talks but carries no date from any government, and Ushakov says Russia has not agreed to widen the format — p4 |
| H005 | 165 | Daily | date | Anthropic prices 18 Nov, lists 19 Nov as ANT | 2026-11-18 | OPEN | 165 |  |
| H006 | 165 | Daily | date | PSLE still tentative 24/25 Nov; S1 posting 18 Dec still NOT MOE-confirmed — every moe.gov.sg page returns an empty body | 2026-11-25 | RESOLVED | 166 | No. 166: PSLE settled: MOE announced on 17 Nov that 2026 results are released at 11am on Tuesday 24 November, with S1 option submission 24-30 November. The S1 POSTING date of 18 December remains tentative and unconfirmed, and is re-opened as H018 — p5 |
| H007 | 165 | Daily | fact | the Iranian supertanker, IRGC-via-ISNA only, no vessel named |  | OPEN | 165 |  |
| H008 | 165 | Daily | fact | any Apple reply on the flicker |  | OPEN | 165 |  |
| H009 | 165 | Daily | fact | the FAA laboratory finding and any GovTech root cause |  | OPEN | 165 |  |
| H010 | 165 | Daily | date | FOMC 8–9 Dec, CPI 10 Dec, BoJ 17–18 Dec | 2026-12-08 | OPEN | 165 |  |
| H011 | 158.5 | Special 158.5 | ask | No IMDA determination exists on whether a peer-to-peer LoRa mesh (Meshtastic) is an 'LPWAN end device' under TS SRD; a local user offered to ask in 2024, no reply on record. Worth asking IMDA directly. |  | OPEN | 158.5 |  |
| H012 | 161 | Daily | ask | Whether a receive-only SDR dongle is an IMDA 'scanning receiver' for import purposes — worth asking IMDA directly. |  | OPEN | 161 |  |
| H013 | 141.5 | Special 141.5 | ask | Artisan Acoustics (SB Acoustics distributor for Singapore): two conflicting addresses and no published price list — phone before any Singapore reader acts. |  | OPEN | 141.5 |  |
| H014 | 154.5 | Special 154.5 | ask | Singapore retail prices for cyberdeck parts and local 3D-printing/filament prices: Shopee/Lazada JS-only, element14/RS/Cytron refuse, NLB MakeIT renders empty. |  | OPEN | 154.5 |  |
| H015 | 166 | Daily | date | Secondary 1 posting results: MOE still gives 18 December 2026 only as tentative; SEAB's own page carries no S1 date and every moe.gov.sg page serves an empty body to this desk | 2026-12-10 | OPEN | 166 |  |
| H016 | 166 | Daily | fact | Whether PAHO reconciles the two measles death tolls it published on 17 November — 82 in the news release, 114 in the same-day Q&A, against one identical case count of 58,213 |  | OPEN | 166 |  |
| H017 | 166 | Daily | fact | The condition of the Kerch Bridge span: a Kyiv estimate of a year or more against a Kremlin 'no doubt', and no independent engineering assessment from any party |  | OPEN | 166 |  |
| H018 | 166 | Daily | date | Nvidia's Q4 FY2027 gross-margin guidance against delivery, and whether a permanent chief executive is named | 2027-02-28 | OPEN | 166 |  |
| H019 | 166 | Daily | ask | Singapore month-on-month seasonally adjusted NODX: EnterpriseSG publishes no such figure in its release and SingStat's merchandise-trade pages refuse this desk, so the circulating +14.2 per cent could not be read at a primary source |  | OPEN | 166 |  |
| H020 | 166 | Daily | fact | Whether Indonesia's Constitutional Court case 399/PUU-XXIV/2026 is XXIV or XXV and whether the first hearing was 3 or 4 November: mkri.id refuses this desk and the outlets disagree |  | OPEN | 166 |  |
