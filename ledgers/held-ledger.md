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
| H007 | 165 | Daily | fact | the Iranian supertanker, IRGC-via-ISNA only, no vessel named |  | DROPPED | 171 | No. 171: IRGC-via-ISNA claim never named a vessel; seven re-checks to No. 171 found no further report — unverifiable |
| H008 | 165 | Daily | fact | any Apple reply on the flicker |  | OPEN | 172 | re-checked 24 Nov: MacRumors 16 Nov and Notebookcheck carry owner reports only; no Apple statement found |
| H009 | 165 | Daily | fact | the FAA laboratory finding and any GovTech root cause |  | OPEN | 172 | re-checked 24 Nov: FAA paused Juniper installs, root cause still under investigation (Axios/AeroTime 16-17 Nov); no lab finding published |
| H010 | 165 | Daily | date | FOMC 8–9 Dec, CPI 10 Dec, BoJ 17–18 Dec | 2026-12-08 | RESOLVED | 170 | No. 170: Confirmed at source: FOMC 8–9 Dec (Fed FOMC calendar, SEP meeting); November CPI 10 Dec 8:30am (BLS schedule); BoJ MPM 17–18 Dec (BoJ schedule). Also: Japan Nov national CPI 18 Dec, Tokyo Nov CPI 27 Nov (Stat Bureau); US GDP Q3 2nd est + Oct PCE 25 Nov (BEA); SG Oct CPI 23 Nov (MAS calendar); NYSE closed 26 Nov, 1pm close 27 Nov |
| H011 | 158.5 | Special 158.5 | ask | No IMDA determination exists on whether a peer-to-peer LoRa mesh (Meshtastic) is an 'LPWAN end device' under TS SRD; a local user offered to ask in 2024, no reply on record. Worth asking IMDA directly. |  | OPEN | 158.5 |  |
| H012 | 161 | Daily | ask | Whether a receive-only SDR dongle is an IMDA 'scanning receiver' for import purposes — worth asking IMDA directly. |  | OPEN | 161 |  |
| H013 | 141.5 | Special 141.5 | ask | Artisan Acoustics (SB Acoustics distributor for Singapore): two conflicting addresses and no published price list — phone before any Singapore reader acts. |  | OPEN | 141.5 |  |
| H014 | 154.5 | Special 154.5 | ask | Singapore retail prices for cyberdeck parts and local 3D-printing/filament prices: Shopee/Lazada JS-only, element14/RS/Cytron refuse, NLB MakeIT renders empty. |  | OPEN | 154.5 |  |
| H015 | 166 | Daily | date | Secondary 1 posting results: MOE still gives 18 December 2026 only as tentative; SEAB's own page carries no S1 date and every moe.gov.sg page serves an empty body to this desk | 2026-12-10 | OPEN | 172 | MOE press release 17 Nov still gives posting results as tentatively 18 Dec |
| H016 | 166 | Daily | fact | Whether PAHO reconciles the two measles death tolls it published on 17 November — 82 in the news release, 114 in the same-day Q&A, against one identical case count of 58,213 |  | OPEN | 172 | re-checked 24 Nov: PAHO 17 Nov briefing PDF prints 58,213 cases and 82 deaths; no sitrep 16 or reconciliation of the 114 figure yet |
| H017 | 166 | Daily | fact | The condition of the Kerch Bridge span: a Kyiv estimate of a year or more against a Kremlin 'no doubt', and no independent engineering assessment from any party |  | OPEN | 171 | re-checked No. 171, still open |
| H018 | 166 | Daily | date | Nvidia's Q4 FY2027 gross-margin guidance against delivery, and whether a permanent chief executive is named | 2027-02-28 | RESOLVED | 172 | No. 172: Nvidia Q3 FY2027 release 17 Nov: Q4 revenue guide $130.0bn +/-3%, gross margins 71.0-72.0%; board reinstated Jensen Huang as CEO 23 Nov (8-K exhibit 99.1); printed p7, p15 |
| H019 | 166 | Daily | ask | Singapore month-on-month seasonally adjusted NODX: EnterpriseSG publishes no such figure in its release and SingStat's merchandise-trade pages refuse this desk, so the circulating +14.2 per cent could not be read at a primary source |  | RESOLVED | 169 | No. 169: SingStat M451002 (SA): Oct NODX S$29.04bn vs Sep S$25.43bn = +14.2% m/m; EnterpriseSG prints none. Printed p5. |
| H020 | 166 | Daily | fact | Whether Indonesia's Constitutional Court case 399/PUU-XXIV/2026 is XXIV or XXV and whether the first hearing was 3 or 4 November: mkri.id refuses this desk and the outlets disagree |  | RESOLVED | 169 | No. 169: mkri.id's 16 Sep 2026 transcript numbers 2026 cases PUU-XXIV/2026, so 399/PUU-XXIV/2026 is correct (hearing date 3 vs 4 Nov unsettled, immaterial). |
| H021 | 167 | The World | date | Shenzhen outcome: whether the three leaders issue a joint communiqué, and the Putin-Trump readouts | 2026-11-20 | RESOLVED | 168 | No. 168: One joint text, the China-Russia-U.S. Declaration toward Peace, four points, no Ukraine/Iran/Taiwan; Putin-Trump readout from Ushakov (35-40 min, Ukraine main topic). Xinhua full text and Kremlin transcripts, read at source. Printed p3. |
| H022 | 167 | The World | date | Berlin envoy meeting reported for 19 Nov (Kyiv Post, Al Jazeera via an unnamed US official) — no government-published date | 2026-11-20 | RESOLVED | 168 | No. 168: Held 19 Nov in Berlin: Witkoff and Kushner at the Chancellery with Merz, Macron, Burnham, Zelensky and 40+ partners; joint call for a winter energy truce. Kyiv Independent, Ukrinform, TASS, RTE, read at source. Printed p4. |
| H023 | 167 | Singapore | date | Federal Register publication of doc 2026-23529 (RIN 0694-AK50) on 19 Nov — federalregister.gov blocked this desk | 2026-11-20 | RESOLVED | 168 | No. 168: Published 19 Nov 2026 at 91 FR 74970-74999, interim final rule effective 19 Nov; comments to 19 Jan 2027; in-transit shipments by 21 Dec. federalregister.gov API and govinfo PDF, read at source. Printed p5. |
| H024 | 167 | The Macro Desk | fact | Why gold fell 3.25 per cent on 18 Nov on a day the real yield eased — no single cause found |  | RESOLVED | 168 | No. 168: Attributed, one source: Saxo Bank Market Quick Take 19 Nov ties the 3.25% fall to the hawkish minutes and selling of liquid assets to raise dollars; no flow data confirms it. Printed p14. |
| H025 | 167 | The Atelier | fact | Which Hanpin turntable models are sold under Audio-Technica and AlphaTheta badges (customs records show shipments only) |  | OPEN | 171 | re-checked No. 171, still open |
| H026 | 167 | The Atelier | ask | Singapore dealers and SGD prices for Linn and Technics turntables — none confirmed |  | OPEN | 167 |  |
| H027 | 167 | The Diary | date | LONGJING Tampines Mall opening date, hours and prices | 2026-12-15 | OPEN | 171 | re-checked No. 171, still open |
| H028 | 167 | The Long Read | fact | Pharmacists for a Healthy Society's KRW 1.012tn first-half 2026 Mounjaro supply figure — single-sourced |  | RESOLVED | 171 | No. 171: No. 171: KRW 1.012tn is the H1 2026 value of Mounjaro supplied to Korean medical institutions per the Pharmacists for a Healthy Society commentary of 17 Nov 2026 (Dailypharm, Kang Hye-kyung, read at source); underlying dataset unnamed. Printed p2. |
| H029 | 167 | The Rabbit Hole | fact | Whether any hobbyist Raspberry Shake station operates in Singapore — station service returned HTTP 502 |  | RESOLVED | 171 | No. 171: No. 171: Yes - Raspberry Shake public station metadata (data.raspberryshake.org) lists open citizen stations inside Singapore, AM.R1475 since 26 Jan 2026, plus R165D, R14CF, R9273. Printed p2. |
| H030 | 167 | The Kit | fact | GrapheneOS official support for the Motorola Signature 27 — unlisted at press |  | OPEN | 171 | re-checked No. 171, still open |
| H031 | 167 | The Good Life | fact | A second independent outlet for Algorithme du Temps' Rêveries des Secondes (single-sourced to Monochrome) | 2026-11-26 | RESOLVED | 168 | No. 168: Splendore Journal, 19 Nov 2026, independent of Monochrome, confirms release, 40 pieces, SW200-1; says the brand has announced no price, so CHF 16,800 is Monochrome's alone. Printed p10. |
| H032 | 168 | The World | date | Trump's Shenzhen news conference of 20 Nov and any White House readout of the Putin-Trump bilateral | 2026-11-21 | RESOLVED | 169 | No. 169: Trump's news conference was at the White House on 20 Nov, not Shenzhen; Putin wants the war ended 'by diplomatic means'; no White House readout (Reuters, Erickson & Chiacu, 20 Nov). Printed p4. |
| H033 | 168 | The World | fact | Kremlin answer to the Berlin winter energy truce call, and a date or venue for talks including Europeans |  | OPEN | 171 | re-checked No. 171, still open |
| H034 | 168 | Singapore | date | MTI Economic Survey: final Q3 2026 GDP and the 2027 forecast | 2026-11-26 | RESOLVED | 171 | No. 171: No. 171: METI notice of 17 Nov confirms the Economic Survey at 8:00am Tue 24 Nov (meti.gov.sg, read at source); the trade ministry is now METI. Printed p5. |
| H035 | 168 | Singapore | fact | First licence decision or BIS clarification of 'significant volume' under 91 FR 74970 |  | OPEN | 171 | re-checked No. 171, still open |
| H036 | 168 | The Atelier | ask | Singapore S$ price for the Carl Hansen CH24 Wishbone, and whether Carl Hansen publishes an EN 16139 level for it |  | OPEN | 168 |  |
| H037 | 168 | Technology | date | Whether underwriters exercise Anthropic's 147m-share over-allotment option (raise to ~$93.5bn) | 2026-12-21 | RESOLVED | 169 | No. 169: Underwriters took the full 147m-share over-allotment: $93.5bn raised (CNBC 20 Nov citing Anthropic). Printed p7. |
| H038 | 168 | Technology | fact | Hy4 Flash llama.cpp support (PR #32517) merged, and an independent speed test |  | OPEN | 172 | PR 32517 still open 23 Nov; tester reports 8->15 tok/s on unstated hardware |
| H039 | 168 | The Good Life | date | Phillips Hong Kong Watch Auction XXIII result for the first-series Patek 2499 (est. HK$12-24m) | 2026-11-24 | RESOLVED | 170 | No. 170: Phillips HK Watch Auction XXIII lot 958, first-series Patek 2499 yellow gold, sold 21 Nov 2026 for HK$34,175,000 incl. premium vs est HK$12–24m (Phillips lot page HK080426/958, Sold For, read at source) |
| H040 | 168 | The Macro Desk | date | Japan October CPI (not out at press; p15 uses September's 2.1) | 2026-11-21 | RESOLVED | 170 | No. 170: Japan October 2026 core CPI (ex fresh food) +2.2% y/y, from 2.1% in September; energy +2.2% as electricity/gas subsidies cut — MIC via Jiji/Kazinform, 20 Nov 2026, read at source |
| H041 | 168 | The Rabbit Hole | fact | PUB's reservoir swimming ban wording and penalty (pub.gov.sg unreachable) |  | OPEN | 168 |  |
| H042 | 168 | The Diary | fact | Standard Singapore ticket prices for KATSEYE, Kenshi Yonezu, Maroon 5 and Freya Skye (Ticketmaster refused) |  | OPEN | 171 | re-checked No. 171, still open |
| H043 | 168 | The Diary | date | Sapporo Snow Festival 2027 dates (4-11 Feb per Hokkaido Shimbun; organiser site not updated) | 2026-12-15 | RESOLVED | 169 | No. 169: Sapporo Snow Festival 2027: 4-11 Feb at Odori, Susukino, Tsudome (snowfes.com, read 21 Nov). Printed p24. |
| H044 | 169 | The World | fact | Whether The Gambia refers Myanmar to the UN Security Council, or the US sanctions ICJ judges, after the 19 Nov genocide judgment | 2026-12-19 | OPEN | 171 | re-checked No. 171, still open |
| H045 | 169 | The World | date | Whether Estonia's road-border closure starts 07:00 1 Dec as decided, and Russia's response | 2026-12-01 | OPEN | 171 | re-checked No. 171, still open |
| H046 | 169 | The World | date | COP31 Antalya final text: any fossil-fuel language restored | 2026-11-23 | RESOLVED | 171 | No. 171: No. 171: COP31 closed 22 Nov with no overarching decision; final drafts carried no fossil-fuel language from 19 Nov; EU, Panama, Marshall Islands rejected the text (Anadolu, NBC, Reuters, 22 Nov, read at source). Printed p3. |
| H047 | 169 | Singapore | fact | CSFTA 4.0: first negotiating round date, chapters or timetable; JCBC outcome | 2026-11-30 | OPEN | 172 | JCBC 23 Nov: Gan says CSFTA 4.0 will include a digital-economy component; no first-round date |
| H048 | 169 | Technology | fact | SEC inquiry into Nvidia accounting (Reuters, unnamed sources): confirmation by filing or SEC | 2026-12-04 | OPEN | 171 | re-checked No. 171, still open |
| H049 | 169 | Technology | fact | Trump 'tremendous tax' on US firms' overseas data centres: any text, any country named | 2026-12-04 | OPEN | 171 | re-checked No. 171, still open |
| H050 | 169 | The Kit | fact | Teenage Engineering EP/BC-1 Singapore price/stockist and first independent review | 2026-12-05 | OPEN | 171 | re-checked No. 171, still open |
| H051 | 169 | The Atelier | fact | HOPPE Amsterdam E1400Z price class (hoppe.com 403, snippet only) and Croft's Willenhall workshop | 2026-12-05 | OPEN | 169 |  |
| H052 | 169 | The Good Life | date | Phillips HK XXIII lot 958 (Patek 2499) price achieved incl. premium vs the desk's under-HK$20m call | 2026-11-23 | RESOLVED | 170 | No. 170: Lot 958 made HK$34,175,000 incl. premium — No. 169's 'inside the estimate, below HK$20m' call is WRONG (Phillips lot page, read at source 21 Nov) |
| H053 | 169 | Screen & Sound | date | Sunrise on the Reaping actual US opening weekend vs $100m | 2026-11-24 | RESOLVED | 171 | No. 171: No. 171: Sunrise on the Reaping opened to an estimated $120m domestic, $225m global (Box Office Mojo weekend estimates; The Numbers, AP, Variety agree) - above $100m. Printed p11. |
| H054 | 169 | The Family Desk | fact | MEDiA study full text (JAH): exact per-hour minutes and the sex interaction | 2026-12-04 | OPEN | 171 | re-checked No. 171, still open |
| H055 | 169 | Fitness | fact | Deng et al. Obes Rev full text: risk of bias, heterogeneity, how visceral fat was measured (Wiley 403) | 2026-11-27 | OPEN | 171 | re-checked No. 171, still open |
| H056 | 169 | The Macro Desk | date | btc_etf_flows: US spot-bitcoin ETF net flows, week 16-20 Nov (SoSoValue posts Saturday; Farside 403) | 2026-11-24 | RESOLVED | 170 | No. 170: US spot-bitcoin ETF net flows week 16–20 Nov: −US$1.25bn (Farside data via crypto.news, 21 Nov 2026; IBIT −541.1m on 19 Nov, record); recorded btc_etf_flows −1.25 as of 2026-11-20 |
| H057 | 169 | The Diary | ask | YOASOBI CAT 8 price (The Kallang page lists S$288, likely an error) | 2026-12-05 | OPEN | 169 |  |
| H058 | 169 | The Table | fact | Casa Mori: a second independent review before the verdict can be called | 2026-12-31 | RESOLVED | 171 | No. 171: No. 171: Casa Mori second reviews: The Ordinary Patrons 25 Jul 2026 (3 TOPs) and Honeycombers 28 Jul (cheesecake grainy), read at source; venue barred on the Table ledger so not printed. |
| H059 | 169 | The Long Read | date | Does Victoria announce a retail fur-sale ban, and does it exempt pest fur? | 2027-03-31 | OPEN | 171 | re-checked No. 171, still open |
| H060 | 169 | The Rabbit Hole | fact | Samsung Cup 2026 final result (not found at press) | 2026-12-05 | OPEN | 171 | re-checked No. 171, still open |
| H061 | 170 | The Atelier | fact | Share of Wakasa-nuri chopstick blanks turned outside Japan (China) — no primary source found; CAA origin rules (1973 運用細則) have no line for chopsticks/lacquerware |  | OPEN | 170 |  |
| H062 | 170 | The Atelier | ask | Singapore stockist + S$ price for Hyozaemon/Daikokuya/Ichihara chopsticks (MUJI SG page 503; Pinkoi shipping to SG unconfirmed) |  | OPEN | 170 |  |
| H063 | 170 | The Atelier | fact | Edo kibashi grail: Daikokuya blue-black ebony pair price at an authorised retailer (only reseller listings seen); ironwood and chestnut species tiers not read at source |  | OPEN | 171 | re-checked No. 171, still open |
| H064 | 170 | Screen & Sound | date | Sunrise on the Reaping weekend: Sunday studio estimate and Monday actuals vs the ~$120m Friday-based projection (H053 continues) | 2026-11-24 | RESOLVED | 172 | No. 172: The Numbers weekend chart 20-22 Nov: Sunrise on the Reaping $119,318,775 from 4,018 cinemas, just under the $120m Sunday estimate (BOM still showed the estimate); printed p11 |
| H065 | 170 | The Family Desk | fact | El-Shafie et al. JAMA Psychiatry ABCD discordance: full tables (per-diagnosis agreement, kappa) — PMC copy embargoed |  | OPEN | 171 | re-checked No. 171, still open |
| H066 | 170 | Fitness | fact | Yasunaga et al. MSSE: effect sizes for FMD/irisin in the 17-person band trial, and which irisin assay was used |  | OPEN | 171 | re-checked No. 171, still open |
| H067 | 170 | The Diary | fact | Face-value prices for Mahiru (29 Nov, Victoria Theatre), Queens of the Stone Age (2 Dec, Star Theatre) and beabadoobee (4 Apr, Indoor Stadium) — not on Live Nation/The Star pages | 2026-12-01 | OPEN | 171 | re-checked No. 171, still open |
| H068 | 170 | The Diary | fact | Hayley Williams, The Star Theatre 26 Feb 2027 (AEG Presents/AXS): prices and time — only Bandwagon read; AXS 403, not on thestar.sg list yet | 2026-12-05 | OPEN | 171 | re-checked No. 171, still open |
| H069 | 170 | The Table | fact | Alvinology 9 Nov review of Casa Vostra Wisma Atria — page 403, verdict unread |  | DROPPED | 171 | No. 171: Casa Vostra is SPENT/barred on the Table ledger; Alvinology page refused three times — no longer printable |
| H070 | 170 | The Long Read | fact | Weibo hot-search rank/views for Jiangsu education director's 'deeply guilty' remark (27 Oct 2026) — not confirmed at source |  | OPEN | 170 |  |
| H071 | 170 | The Long Read | fact | Name of the British factory inspector behind 'the lights in the window will discover the one but not the other' (unnamed in the source read) |  | OPEN | 171 | re-checked No. 171, still open |
| H072 | 170 | The Macro Desk | fact | WGC Central Bank Gold Statistics for October 2026 (not yet published at 22 Nov; cb_gold stays at Sep 61t) | 2026-12-08 | OPEN | 171 | re-checked No. 171, still open |
| H073 | 170 | The Macro Desk | fact | ICI combined flows for week to 18 Nov (release Wed 25 Nov) — first count covering the rout | 2026-11-27 | OPEN | 171 | re-checked No. 171, still open |
| H074 | 170 | The Rabbit Hole | fact | r/foraging subscriber count (reddit.com not readable from the desk) |  | OPEN | 170 |  |
| H075 | 170 | The Rabbit Hole | fact | Parks and Trees Act section number and penalty text read on SSO (sso.agc.gov.sg returned 403; penalties printed from MND's 2019 answer as reported by Mothership/Must Share News) |  | OPEN | 170 |  |
| H076 | 170 | The Rabbit Hole | fact | Clinical Toxicology 2023 plant-ID app study (58% average, PictureThis 94%, PlantSnap 34%, 5 of 11 toxic species called edible) — tandfonline/scimex 403; not printed |  | OPEN | 170 |  |
| H077 | 170 | The Rabbit Hole | ask | Thomas Smith's Trug Shop direct prices, lead times and commission process (sussextrugs.com not read) |  | OPEN | 170 |  |
| H078 | 170 | The Rabbit Hole | date | Niwaki forged hori-hori price and 14 May 2027 dispatch read at niwaki.com (403; printed via search listing) | 2027-05-14 | OPEN | 170 |  |
| H079 | 170 | Technology | date | TSMC confirmation of the China 16nm order halt, and first US licence decision for Chinese phone chips before the 21 Dec savings-clause deadline | 2026-12-21 | OPEN | 171 | re-checked No. 171, still open |
| H080 | 170 | Technology | fact | Independent tok/s benchmark for Inkling 2 Mini on a 32GB Mac / 24GB GPU (not vendor, not single HN post) |  | OPEN | 172 | no independent Inkling 2 Mini tok/s found 23 Nov |
| H081 | 170 | The Kit | fact | Grado GW200: microphone yes/no (Grado spec sheet says built-in, Gear Patrol says none), first independent review, Singapore price/stockist |  | OPEN | 171 | re-checked No. 171, still open |
| H082 | 170 | The Good Life | date | Phillips HK XXIII sale total and Session 2 results (1518 pink gold HK$8-16m, 3990P-011 HK$12-24m) | 2026-11-23 | RESOLVED | 171 | No. 171: No. 171: Phillips HK XXIII Session 2, 22 Nov: lot 1065 Patek 1518R pink gold (1951) HK$25.1m vs est HK$8-16m; lot 1125 3990P-011 HK$12.7m (Phillips lot pages, read at source). Sale total still unpublished (new item). Printed p10. |
| H083 | 170 | The Travel Desk | fact | Shirakawa-go 2025 visitor total (one Japanese web report says a record ~2.3m, 55.6% foreign) — no village/prefecture release read; tabi-mag 403 |  | OPEN | 170 |  |
| H084 | 170 | The Travel Desk | date | WSI Sydney Metro (St Marys–airport) opening: MileLion says not before Apr 2027, The Star (Apr 2026) says not before Dec 2027 — need Sydney Metro/NSW source |  | OPEN | 170 |  |
| H085 | 170 | The Travel Desk | fact | SQ672 SIN–NGO schedule (01:20/~09:00) — booking-site snippet only; singaporeair.com page 404 |  | OPEN | 170 |  |
| H086 | 170 | The Travel Desk | fact | Nohi Bus Takayama–Shirakawa-go regular fare and which departures need reservation (official fare page not read) |  | OPEN | 170 |  |
| H087 | 170 | The World | fact | Iran nuclear doctrine: any formal NPT-withdrawal step, Majlis bill, or a Mojtaba Khamenei ruling revising the fatwa | 2026-12-15 | OPEN | 171 | re-checked No. 171, still open |
| H088 | 170 | The World | fact | Denmark Kyivstoner case: Russia's 'appropriate response' (tit-for-tat expulsion?) and published evidence of GRU/FSB direction | 2026-12-01 | OPEN | 171 | re-checked No. 171, still open |
| H089 | 170 | Singapore | date | 22nd JCBC: date, Ding Xuexiang visit, the 20+ deliverables and the EdTech/AI education MOU signing | 2026-11-30 | RESOLVED | 171 | No. 171: No. 171: Ding Xuexiang visiting 22-23 Nov, called on PM Wong at the Istana 22 Nov; 22nd JCBC on 23 Nov co-chaired by Gan Kim Yong, 20+ agreements expected (PMO 21 Nov; ST/ANN via The Star 22 Nov). Printed p5. Deliverables held as a new item. |
| H090 | 171 | The World | fact | Whether COP31 talks are reconvened or a cover decision adopted later (Telegraph: 'suspended and reconvened next year'; no official process found) |  | OPEN | 172 | China MFA (Guo Jiakun, 23 Nov) says decisions on just transition, mitigation, adaptation and finance were adopted, no overarching deal; unconfirmed elsewhere; correction printed p4 |
| H091 | 171 | The World | fact | Malaysia to take the ICJ Myanmar ruling to the UN, OIC and Asean (Anadolu briefing headline only, single-sourced) |  | OPEN | 171 |  |
| H092 | 171 | Singapore | date | 22nd JCBC deliverables (20+ agreements), the EdTech/AI education MOU and CSFTA 4.0 first-round date | 2026-11-24 | RESOLVED | 172 | No. 172: PMO list 23 Nov: 29 agreements at the 22nd JCBC (27 in 2025), incl. MAS in PBOC RMB repo facility, CGB collateral and fast-payment link to 'explore', Hainan food accreditation; CSFTA 4.0 first-round date still unset (H047 stays open); printed p5 |
| H093 | 171 | Singapore | date | PM Wong in Australia 23-25 Nov: 11th Annual Leaders' Meeting outcomes; first foreign leader landing at Western Sydney International | 2026-11-25 | OPEN | 172 | Wong landed at Western Sydney 23 Nov (CNA); Annual Leaders' Meeting in Canberra is 24 Nov, after press |
| H094 | 171 | Fitness | fact | Meernik et al. MSSE (Cooper Center, 28,612 men) full text: cohort make-up and adjustments (abstract only, single-sourced) |  | OPEN | 171 |  |
| H095 | 171 | The Atelier | fact | Prada's own price for its Kolhapuri-inspired sandals and whether sales began Feb 2026 (prada.com 503; ~EUR800 reported by Business Today) |  | OPEN | 171 |  |
| H096 | 171 | The Atelier | fact | Whether LIDCOM retail Kolhapuri pairs are bark-tanned (UmedMart says only 'naturally tanned') |  | OPEN | 171 |  |
| H097 | 171 | Technology | fact | Whether Megaspeed itself is charged; Li Ming's Singapore case (WSJ 22 Nov) |  | OPEN | 171 |  |
| H098 | 171 | Technology | fact | NYT 21 Nov original on China's MSS chip hunt (nytimes.com refused) and Beijing's reply |  | OPEN | 171 |  |
| H099 | 171 | The Kit | date | Xreal Aura Singapore availability and price | 2027-03-31 | OPEN | 171 |  |
| H100 | 171 | The Good Life | date | Phillips HK XXIII sale total and sell-through (no press release, results file 404) | 2026-11-25 | OPEN | 171 |  |
| H101 | 171 | The Good Life | date | Christie's HK Iconic 40 (25 Nov) lot 4021 Patek 6104/12G-010 result vs HK$12-24m | 2026-11-26 | OPEN | 171 |  |
| H102 | 171 | The Family Desk | fact | Current text of AAPM position statement PS 4-B (2023); page quoted superseded 2018 PS 4-A |  | OPEN | 171 |  |
| H103 | 171 | The Family Desk | ask | Independent expert reaction to the JAMA head-CT/brain-tumour paper (Miglioretti, 19 Nov) |  | OPEN | 171 |  |
| H104 | 171 | The Macro Desk | fact | MAS SGD-US short-rate gap for the PIMCO Income hedge cost (MAS data service in maintenance) |  | OPEN | 171 |  |
| H105 | 171 | The Rabbit Hole | fact | Mokuhanga Sisters met at MI-LAB 2017-19 (Kentler Gallery robot check; listings only) |  | OPEN | 171 |  |
| H106 | 171 | The Rabbit Hole | date | 6th International Mokuhanga Conference, Lawrence KS: exact days (26-29 May 2027 per listing) | 2027-05-26 | OPEN | 171 |  |
| H107 | 171 | The Rabbit Hole | ask | STPI: any 2027 mokuhanga class date (2026 class was mokulito) |  | OPEN | 171 |  |
| H108 | 171 | The Diary | date | SIX60 *SCAPE Ground Theatre 10 Dec ticket prices (Ticketmaster only, 403) | 2026-12-08 | OPEN | 171 |  |
| H109 | 171 | The Table | fact | Second independent review of Warmhouse Nasi Lemak (SETHLUI 403) |  | OPEN | 171 |  |
| H110 | 171 | The Long Read | fact | Final 2027 Suneung device-cheating count (111 suspected reported 20 Nov; printed same-day 98) |  | OPEN | 171 |  |
| H111 | 171 | The Long Read | fact | Cho Kuk 2019 admissions plan (16 universities, nine at 40%) read only via Asia Economy 2020, not the ministry document |  | OPEN | 171 |  |
| H112 | 172 | The World | fact | Merkury strike: confirmed death toll, true drone count, launch site, and whether Angara is the Maltese-flagged ship |  | OPEN | 172 |  |
| H113 | 172 | Technology | fact | Nvidia 23 Nov official close (Yahoo panel 165.09-165.38, unlabelled) and Rene Haas's Arm contract to 2033 (NBC only) |  | OPEN | 172 |  |
| H114 | 172 | Technology | date | Huang closed-door House session 1 Dec and Senate Banking hearing ~3 Dec: what is disclosed | 2026-12-03 | OPEN | 172 |  |
| H115 | 172 | The Home Lab | fact | Names of the three inference hosts Dragos found breached and of the Chinese lab; Together AI's June-July notice |  | OPEN | 172 |  |
| H116 | 172 | The Long Read | date | Japan 2026 New Words and Buzzwords Award top ten and grand prize: is gengoka in, does it win (our call: top ten, not the prize) | 2026-12-01 | OPEN | 172 |  |
| H117 | 172 | The Diary | fact | Wonder Festival 2027 Winter venue; Westlife 16-17 Jan sold-out status (secondary only); Disney On Ice category prices |  | OPEN | 172 |  |
| H118 | 172 | The Table | fact | Stamford Social opening date and first independent review; British Hainan Tiong Bahru second review |  | OPEN | 172 |  |
| H119 | 172 | Screen & Sound | fact | I Play Rocky Singapore release date |  | OPEN | 172 |  |
| H120 | 172 | The Macro Desk | date | FactSet 20 Nov Mag 7 Q4 growth: 24.1% (A PDF) vs 22.6% (other PDF); other-493 Q3 printed both 32.6 and 34.7 - re-read the 4 Dec edition | 2026-12-04 | OPEN | 172 |  |
