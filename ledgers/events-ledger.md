# The Events Ledger

Machine-readable memory for The Diary. Extracted to `state/events-ledger.json`
by `tools/extract_state.py` and gated by `tools/validate.py`.

**Why this file exists (editor, 31 Aug 2026 — reader-reported).** A Post Malone
Singapore date ran as a marquee pick in No. 84. No. 85 printed a correction
saying it had been postponed. It kept reappearing anyway, because each build
researches The Diary from scratch and the correction lived only as prose in an
Issue Log note — nothing a later session reads before it picks events. A
cancellation has to be a *fact in a table*, not a sentence in a footnote.

## Dead Events

Events that have been cancelled, postponed without a new date, or moved out of
the listing window. **A row here is a hard bar: `validate.py` fails the build if
the event name appears in any `.evt` row.** If an event is genuinely reinstated
with a confirmed new date, change its Status to `REINSTATED` (the gate ignores
those) and record the source that confirmed it — never delete the row, because
the history is the point.

| Event | Where | Was listed | Status | Checked | Source / note |
|---|---|---|---|---|---|
| Post Malone | Singapore | No. 84, as a 25 Sep marquee pick | CANCELLED | 31 Aug 2026 | Reader-reported cancelled. No. 85 printed a correction calling it POSTPONED; the reader reports the show is off entirely. Do not list again unless a promoter or venue announcement confirms a new date — and if it is confirmed, set Status to REINSTATED with that source. |

## Verification Log

Optional running note of the still-on checks (see THE STILL-ON CHECK in the
spec). Not gated — this is for the editor's eye, so a later session can see
when an event was last confirmed rather than re-litigating it.

| Date | Events re-checked | Outcome |
|---|---|---|
| 31 Aug 2026 | Post Malone (SG) | Pulled to Dead Events on the reader's report. |
| 6 Sep 2026 | The Weeknd (2–3 Oct); F1 SG GP + Padang (9–11 Oct); BIGBANG (17–18 Oct); Guns N' Roses (25 Nov); MCR (10–11 Nov); Babymonster (28–29 Nov); Deepavali light-up (19 Sep–22 Nov); Kyushu Basho (8–22 Nov, on-sale 19 Sep); Orsay @ Tokyo Met (14 Nov–28 Mar) | All still on against live ticketer/venue/official listings (Ticketmaster SG, thekallang.com.sg, RacingNews365, VisitSingapore, tobikan.jp, Ticket Oosumo). Post Malone NOT listed (remains CANCELLED). |
