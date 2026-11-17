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
| H001 | 165 | Daily | date | Nvidia Q3, 18 Nov 05:20 SGT | 2026-11-18 | OPEN | 165 |  |
| H002 | 165 | Daily | fact | Oct NODX, due 08:30 today, unpublished at press (EnterpriseSG 500s) |  | OPEN | 165 |  |
| H003 | 165 | Daily | fact | Federal Register publication and effective date of RIN 0694-AK50 |  | OPEN | 165 |  |
| H004 | 165 | Daily | fact | whether Shenzhen and Berlin happen |  | OPEN | 165 |  |
| H005 | 165 | Daily | date | Anthropic prices 18 Nov, lists 19 Nov as ANT | 2026-11-18 | OPEN | 165 |  |
| H006 | 165 | Daily | date | PSLE still tentative 24/25 Nov; S1 posting 18 Dec still NOT MOE-confirmed — every moe.gov.sg page returns an empty body | 2026-11-25 | OPEN | 165 |  |
| H007 | 165 | Daily | fact | the Iranian supertanker, IRGC-via-ISNA only, no vessel named |  | OPEN | 165 |  |
| H008 | 165 | Daily | fact | any Apple reply on the flicker |  | OPEN | 165 |  |
| H009 | 165 | Daily | fact | the FAA laboratory finding and any GovTech root cause |  | OPEN | 165 |  |
| H010 | 165 | Daily | date | FOMC 8–9 Dec, CPI 10 Dec, BoJ 17–18 Dec | 2026-12-08 | OPEN | 165 |  |
| H011 | 158.5 | Special 158.5 | ask | No IMDA determination exists on whether a peer-to-peer LoRa mesh (Meshtastic) is an 'LPWAN end device' under TS SRD; a local user offered to ask in 2024, no reply on record. Worth asking IMDA directly. |  | OPEN | 158.5 |  |
| H012 | 161 | Daily | ask | Whether a receive-only SDR dongle is an IMDA 'scanning receiver' for import purposes — worth asking IMDA directly. |  | OPEN | 161 |  |
| H013 | 141.5 | Special 141.5 | ask | Artisan Acoustics (SB Acoustics distributor for Singapore): two conflicting addresses and no published price list — phone before any Singapore reader acts. |  | OPEN | 141.5 |  |
| H014 | 154.5 | Special 154.5 | ask | Singapore retail prices for cyberdeck parts and local 3D-printing/filament prices: Shopee/Lazada JS-only, element14/RS/Cytron refuse, NLB MakeIT renders empty. |  | OPEN | 154.5 |  |
