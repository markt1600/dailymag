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
| H005 | 165 | Daily | date | Anthropic prices 18 Nov, lists 19 Nov as ANT | 2026-11-18 | RESOLVED | 168 | No. 168: Priced 18 Nov at $83 (range $70-78), 980m shares, $81.34bn gross; listed Nasdaq ANT 19 Nov, opened $111.50, closed $97.17 (+17.1%). 424B4 accession 0001628280-26-074944 on EDGAR, read at source; CNBC. Printed p7. |
| H006 | 165 | Daily | date | PSLE still tentative 24/25 Nov; S1 posting 18 Dec still NOT MOE-confirmed — every moe.gov.sg page returns an empty body | 2026-11-25 | RESOLVED | 166 | No. 166: PSLE settled: MOE announced on 17 Nov that 2026 results are released at 11am on Tuesday 24 November, with S1 option submission 24-30 November. The S1 POSTING date of 18 December remains tentative and unconfirmed, and is re-opened as H018 — p5 |
| H007 | 165 | Daily | fact | the Iranian supertanker, IRGC-via-ISNA only, no vessel named |  | OPEN | 169 | nothing new from ISNA |
| H008 | 165 | Daily | fact | any Apple reply on the flicker |  | OPEN | 169 | no Apple reply |
| H009 | 165 | Daily | fact | the FAA laboratory finding and any GovTech root cause |  | OPEN | 168 | re-checked No. 168, still open (see the No. 168 notes) |
| H010 | 165 | Daily | date | FOMC 8–9 Dec, CPI 10 Dec, BoJ 17–18 Dec | 2026-12-08 | OPEN | 165 |  |
| H011 | 158.5 | Special 158.5 | ask | No IMDA determination exists on whether a peer-to-peer LoRa mesh (Meshtastic) is an 'LPWAN end device' under TS SRD; a local user offered to ask in 2024, no reply on record. Worth asking IMDA directly. |  | OPEN | 158.5 |  |
| H012 | 161 | Daily | ask | Whether a receive-only SDR dongle is an IMDA 'scanning receiver' for import purposes — worth asking IMDA directly. |  | OPEN | 161 |  |
| H013 | 141.5 | Special 141.5 | ask | Artisan Acoustics (SB Acoustics distributor for Singapore): two conflicting addresses and no published price list — phone before any Singapore reader acts. |  | OPEN | 141.5 |  |
| H014 | 154.5 | Special 154.5 | ask | Singapore retail prices for cyberdeck parts and local 3D-printing/filament prices: Shopee/Lazada JS-only, element14/RS/Cytron refuse, NLB MakeIT renders empty. |  | OPEN | 154.5 |  |
| H015 | 166 | Daily | date | Secondary 1 posting results: MOE still gives 18 December 2026 only as tentative; SEAB's own page carries no S1 date and every moe.gov.sg page serves an empty body to this desk | 2026-12-10 | OPEN | 169 | MOE still says tentative 18 Dec |
| H016 | 166 | Daily | fact | Whether PAHO reconciles the two measles death tolls it published on 17 November — 82 in the news release, 114 in the same-day Q&A, against one identical case count of 58,213 |  | OPEN | 169 | PAHO SitRep 15 latest; no reconciliation |
| H017 | 166 | Daily | fact | The condition of the Kerch Bridge span: a Kyiv estimate of a year or more against a Kremlin 'no doubt', and no independent engineering assessment from any party |  | OPEN | 169 | no independent assessment |
| H018 | 166 | Daily | date | Nvidia's Q4 FY2027 gross-margin guidance against delivery, and whether a permanent chief executive is named | 2027-02-28 | OPEN | 169 | Q4 GM guide 71-72%; no permanent CEO |
| H019 | 166 | Daily | ask | Singapore month-on-month seasonally adjusted NODX: EnterpriseSG publishes no such figure in its release and SingStat's merchandise-trade pages refuse this desk, so the circulating +14.2 per cent could not be read at a primary source |  | RESOLVED | 169 | No. 169: SingStat M451002 (SA): Oct NODX S$29.04bn vs Sep S$25.43bn = +14.2% m/m; EnterpriseSG prints none. Printed p5. |
| H020 | 166 | Daily | fact | Whether Indonesia's Constitutional Court case 399/PUU-XXIV/2026 is XXIV or XXV and whether the first hearing was 3 or 4 November: mkri.id refuses this desk and the outlets disagree |  | RESOLVED | 169 | No. 169: mkri.id's 16 Sep 2026 transcript numbers 2026 cases PUU-XXIV/2026, so 399/PUU-XXIV/2026 is correct (hearing date 3 vs 4 Nov unsettled, immaterial). |
| H021 | 167 | The World | date | Shenzhen outcome: whether the three leaders issue a joint communiqué, and the Putin-Trump readouts | 2026-11-20 | RESOLVED | 168 | No. 168: One joint text, the China-Russia-U.S. Declaration toward Peace, four points, no Ukraine/Iran/Taiwan; Putin-Trump readout from Ushakov (35-40 min, Ukraine main topic). Xinhua full text and Kremlin transcripts, read at source. Printed p3. |
| H022 | 167 | The World | date | Berlin envoy meeting reported for 19 Nov (Kyiv Post, Al Jazeera via an unnamed US official) — no government-published date | 2026-11-20 | RESOLVED | 168 | No. 168: Held 19 Nov in Berlin: Witkoff and Kushner at the Chancellery with Merz, Macron, Burnham, Zelensky and 40+ partners; joint call for a winter energy truce. Kyiv Independent, Ukrinform, TASS, RTE, read at source. Printed p4. |
| H023 | 167 | Singapore | date | Federal Register publication of doc 2026-23529 (RIN 0694-AK50) on 19 Nov — federalregister.gov blocked this desk | 2026-11-20 | RESOLVED | 168 | No. 168: Published 19 Nov 2026 at 91 FR 74970-74999, interim final rule effective 19 Nov; comments to 19 Jan 2027; in-transit shipments by 21 Dec. federalregister.gov API and govinfo PDF, read at source. Printed p5. |
| H024 | 167 | The Macro Desk | fact | Why gold fell 3.25 per cent on 18 Nov on a day the real yield eased — no single cause found |  | RESOLVED | 168 | No. 168: Attributed, one source: Saxo Bank Market Quick Take 19 Nov ties the 3.25% fall to the hawkish minutes and selling of liquid assets to raise dollars; no flow data confirms it. Printed p14. |
| H025 | 167 | The Atelier | fact | Which Hanpin turntable models are sold under Audio-Technica and AlphaTheta badges (customs records show shipments only) |  | OPEN | 167 |  |
| H026 | 167 | The Atelier | ask | Singapore dealers and SGD prices for Linn and Technics turntables — none confirmed |  | OPEN | 167 |  |
| H027 | 167 | The Diary | date | LONGJING Tampines Mall opening date, hours and prices | 2026-12-15 | OPEN | 169 | not re-checked |
| H028 | 167 | The Long Read | fact | Pharmacists for a Healthy Society's KRW 1.012tn first-half 2026 Mounjaro supply figure — single-sourced |  | OPEN | 167 |  |
| H029 | 167 | The Rabbit Hole | fact | Whether any hobbyist Raspberry Shake station operates in Singapore — station service returned HTTP 502 |  | OPEN | 167 |  |
| H030 | 167 | The Kit | fact | GrapheneOS official support for the Motorola Signature 27 — unlisted at press |  | OPEN | 169 | GrapheneOS lists Pixels only |
| H031 | 167 | The Good Life | fact | A second independent outlet for Algorithme du Temps' Rêveries des Secondes (single-sourced to Monochrome) | 2026-11-26 | RESOLVED | 168 | No. 168: Splendore Journal, 19 Nov 2026, independent of Monochrome, confirms release, 40 pieces, SW200-1; says the brand has announced no price, so CHF 16,800 is Monochrome's alone. Printed p10. |
| H032 | 168 | The World | date | Trump's Shenzhen news conference of 20 Nov and any White House readout of the Putin-Trump bilateral | 2026-11-21 | RESOLVED | 169 | No. 169: Trump's news conference was at the White House on 20 Nov, not Shenzhen; Putin wants the war ended 'by diplomatic means'; no White House readout (Reuters, Erickson & Chiacu, 20 Nov). Printed p4. |
| H033 | 168 | The World | fact | Kremlin answer to the Berlin winter energy truce call, and a date or venue for talks including Europeans |  | OPEN | 169 | Kremlin still at Putin's 19 Nov 'no negotiations'; no date/venue |
| H034 | 168 | Singapore | date | MTI Economic Survey: final Q3 2026 GDP and the 2027 forecast | 2026-11-26 | OPEN | 169 | METI Q3 Economic Survey dated Tue 24 Nov 8am |
| H035 | 168 | Singapore | fact | First licence decision or BIS clarification of 'significant volume' under 91 FR 74970 |  | OPEN | 169 | no licence decision or clarification |
| H036 | 168 | The Atelier | ask | Singapore S$ price for the Carl Hansen CH24 Wishbone, and whether Carl Hansen publishes an EN 16139 level for it |  | OPEN | 168 |  |
| H037 | 168 | Technology | date | Whether underwriters exercise Anthropic's 147m-share over-allotment option (raise to ~$93.5bn) | 2026-12-21 | RESOLVED | 169 | No. 169: Underwriters took the full 147m-share over-allotment: $93.5bn raised (CNBC 20 Nov citing Anthropic). Printed p7. |
| H038 | 168 | Technology | fact | Hy4 Flash llama.cpp support (PR #32517) merged, and an independent speed test |  | OPEN | 169 | PR 32517 ready for review, not merged |
| H039 | 168 | The Good Life | date | Phillips Hong Kong Watch Auction XXIII result for the first-series Patek 2499 (est. HK$12-24m) | 2026-11-24 | OPEN | 169 | lot 958 sells Sat 21 Nov after press |
| H040 | 168 | The Macro Desk | date | Japan October CPI (not out at press; p15 uses September's 2.1) | 2026-11-21 | OPEN | 168 |  |
| H041 | 168 | The Rabbit Hole | fact | PUB's reservoir swimming ban wording and penalty (pub.gov.sg unreachable) |  | OPEN | 168 |  |
| H042 | 168 | The Diary | fact | Standard Singapore ticket prices for KATSEYE, Kenshi Yonezu, Maroon 5 and Freya Skye (Ticketmaster refused) |  | OPEN | 169 | no standard prices; Ticketmaster 403 |
| H043 | 168 | The Diary | date | Sapporo Snow Festival 2027 dates (4-11 Feb per Hokkaido Shimbun; organiser site not updated) | 2026-12-15 | RESOLVED | 169 | No. 169: Sapporo Snow Festival 2027: 4-11 Feb at Odori, Susukino, Tsudome (snowfes.com, read 21 Nov). Printed p24. |
| H044 | 169 | The World | fact | Whether The Gambia refers Myanmar to the UN Security Council, or the US sanctions ICJ judges, after the 19 Nov genocide judgment | 2026-12-19 | OPEN | 169 |  |
| H045 | 169 | The World | date | Whether Estonia's road-border closure starts 07:00 1 Dec as decided, and Russia's response | 2026-12-01 | OPEN | 169 |  |
| H046 | 169 | The World | date | COP31 Antalya final text: any fossil-fuel language restored | 2026-11-23 | OPEN | 169 |  |
| H047 | 169 | Singapore | fact | CSFTA 4.0: first negotiating round date, chapters or timetable; JCBC outcome | 2026-11-30 | OPEN | 169 |  |
| H048 | 169 | Technology | fact | SEC inquiry into Nvidia accounting (Reuters, unnamed sources): confirmation by filing or SEC | 2026-12-04 | OPEN | 169 |  |
| H049 | 169 | Technology | fact | Trump 'tremendous tax' on US firms' overseas data centres: any text, any country named | 2026-12-04 | OPEN | 169 |  |
| H050 | 169 | The Kit | fact | Teenage Engineering EP/BC-1 Singapore price/stockist and first independent review | 2026-12-05 | OPEN | 169 |  |
| H051 | 169 | The Atelier | fact | HOPPE Amsterdam E1400Z price class (hoppe.com 403, snippet only) and Croft's Willenhall workshop | 2026-12-05 | OPEN | 169 |  |
| H052 | 169 | The Good Life | date | Phillips HK XXIII lot 958 (Patek 2499) price achieved incl. premium vs the desk's under-HK$20m call | 2026-11-23 | OPEN | 169 |  |
| H053 | 169 | Screen & Sound | date | Sunrise on the Reaping actual US opening weekend vs $100m | 2026-11-24 | OPEN | 169 |  |
| H054 | 169 | The Family Desk | fact | MEDiA study full text (JAH): exact per-hour minutes and the sex interaction | 2026-12-04 | OPEN | 169 |  |
| H055 | 169 | Fitness | fact | Deng et al. Obes Rev full text: risk of bias, heterogeneity, how visceral fat was measured (Wiley 403) | 2026-11-27 | OPEN | 169 |  |
| H056 | 169 | The Macro Desk | date | btc_etf_flows: US spot-bitcoin ETF net flows, week 16-20 Nov (SoSoValue posts Saturday; Farside 403) | 2026-11-24 | OPEN | 169 |  |
| H057 | 169 | The Diary | ask | YOASOBI CAT 8 price (The Kallang page lists S$288, likely an error) | 2026-12-05 | OPEN | 169 |  |
| H058 | 169 | The Table | fact | Casa Mori: a second independent review before the verdict can be called | 2026-12-31 | OPEN | 169 |  |
| H059 | 169 | The Long Read | date | Does Victoria announce a retail fur-sale ban, and does it exempt pest fur? | 2027-03-31 | OPEN | 169 |  |
| H060 | 169 | The Rabbit Hole | fact | Samsung Cup 2026 final result (not found at press) | 2026-12-05 | OPEN | 169 |  |
