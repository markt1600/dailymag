# The Table Ledger

Machine-readable memory for "The Table" — The Diary's standing strip on
Singapore's newest openings. Extracted to `state/table-ledger.json` by
`tools/extract_state.py`, maintained by `tools/table_ledger.py`, and gated by
`tools/validate.py`.

**Why this file exists (editor, 21 Sep 2026 — reader-reported).** Kuro Kare
ran in Nos. 97, 99, 105 and 109. Assaggi was named in eighteen issues, most of
them as "still unreviewed". The spec had said "rotate venues each issue" since
No. 35 and told the desk to track them in the Coverage Ledger, but a Coverage
Ledger row is advice a fresh session may or may not read, and the Issue Log's
own receipts ("Katsu by Kyu, played out" in No. 75) were followed by two more
runs. Exactly the Undercurrent problem: a rotation rule in prose prevents
nothing. A venue's history has to be a *row*, and the row has to be a *gate*.

## The law

* **A venue's Table life is TWO runs**: the opening run (now open / too new to
  call) and ONE verdict run (the first real reviews, a Michelin nod, a second
  outlet). After the second run its Status becomes `SPENT` and the gate bars it.
* **The two runs are at least SEVEN issues apart.** A venue that ran in No. 97
  may not return before No. 104; a run that "revisits" a week later is the
  repetition the reader complained about, whatever the peg.
* **The bar covers the WHOLE Table section** — body, chatter, sceptic and the
  "on the bench" strip — not just the lead paragraph. "Still on the shelf"
  mentions are how the drift happened. The sources block (`.fn`) is exempt, so
  a "not repeated here" note may still name a venue.
* **Only the editor reinstates.** A third run needs Status `REINSTATED` with
  the reason in the note (a closure, a star, a scandal). The build never sets
  it. The gate allows one run under `REINSTATED`, after which the updater
  returns the row to `SPENT`.
* **`CLOSED` bars a venue outright** regardless of run count (the editor's
  call — e.g. a venue that has shut).
* **Mark venues in the markup.** From No. 110 every venue the Table covers is
  written `<b class="venue">Name</b>` on its first mention. The updater reads
  those marks to add new rows; the gate fails a Table with none.

## Maintenance (automatic)

After the build passes validation, run
`python3 tools/table_ledger.py build/meridianNN.html NN` — it records the run
for every venue found in the Table section (known keys anywhere in its text,
plus every new `.venue` mark), adds rows for new venues, and flips Status
(`OPEN`→`SPENT` at two runs, `REINSTATED`→`SPENT` after the reinstated run).
Then `tools/extract_state.py` regenerates the JSON. The build may edit a new
row's Note to record the peg; it may not change a Status.

Columns: Venue (display name) · Key (the string the gate matches on — a
distinctive proper noun, matched case-insensitively on word boundaries,
diacritics folded) · Runs (issue numbers) · Status · Checked · Note.

## Table Venues

| Venue | Key | Runs | Status | Checked | Note |
|---|---|---|---|---|---|
| Assaggi (Neil Road) | Assaggi | 66, 67, 68, 70, 72, 75, 76, 78, 82, 85, 87, 89, 91, 92, 95, 101, 103, 109 | SPENT | 21 Sep 2026 (archive scan) | Eighteen mentions since No. 66, most as "still unreviewed" — the definition of drift. Do not list again until a review exists AND the editor reinstates. |
| Kuro Kare (Havelock II) | Kuro Kare | 97, 99, 105, 109 | SPENT | 21 Sep 2026 (archive scan) | The reader-reported repeat: four runs in thirteen issues. Verdict spent — Eatbook, Time Out both quoted in No. 109. |
| Le Ju Xuan (Marina Bay Sands) | Le Ju Xuan | 95, 99, 102, 105, 109 | SPENT | 21 Sep 2026 (archive scan) | Five mentions, never reviewed, no published price. |
| Tian Tian (Jewel flagship) | Tian Tian | 75, 76, 92, 99, 102, 103, 109 | SPENT | 21 Sep 2026 (archive scan) | Verdict printed in No. 109 — peg spent. |
| Árō (Mohamed Sultan Road) | Árō | 107 | OPEN | 21 Sep 2026 (archive scan) | Ran once, No. 107, as TOO NEW. Second run allowed from No. 114 with a real review. |
| Foura (Gardens by the Bay) | Foura | 50, 51, 52, 55, 59, 68, 74, 79, 93, 96, 97, 101, 106 | SPENT | 21 Sep 2026 (archive scan) |  |
| Hikiniku to Come | Hikiniku to Come | 17, 20, 27, 28, 32, 34, 93, 106 | SPENT | 21 Sep 2026 (archive scan) | Retired in No. 28; re-used in No. 32 (corrected in No. 33); back again in 93 and 106. |
| Unagi Yondaime Kikukawa | Kikukawa | 99, 106 | SPENT | 21 Sep 2026 (archive scan) |  |
| Casa Lola | Casa Lola | 88, 97, 105 | SPENT | 21 Sep 2026 (archive scan) |  |
| Katsu by Kyu | Katsu by Kyu | 64, 66, 67, 70, 73, 75, 79, 84, 102, 105 | SPENT | 21 Sep 2026 (archive scan) | Issue Log No. 75 already called it "played out" — it ran twice more. |
| Noor (River Valley) | Noor | 104, 112 | SPENT | 21 Sep 2026 (archive scan) |  |
| Osteria Mozza | Osteria Mozza | 95, 98, 103, 104 | SPENT | 21 Sep 2026 (archive scan) |  |
| Sushidan | Sushidan | 54, 57, 59, 84, 93, 96, 104 | SPENT | 21 Sep 2026 (archive scan) |  |
| Toriei (Cuppage Plaza) | Toriei | 96, 100, 104 | SPENT | 21 Sep 2026 (archive scan) |  |
| Mom's Touch (South Bridge Road) | Mom's Touch | 87, 92, 95, 97, 101, 103 | SPENT | 21 Sep 2026 (archive scan) |  |
| Tembusu (Botanic Gardens) | Tembusu | 81, 82, 86, 87, 91, 92, 101, 103 | SPENT | 21 Sep 2026 (archive scan) |  |
| Behind Clay | Behind Clay | 47, 50, 51, 53, 57, 101 | SPENT | 21 Sep 2026 (archive scan) |  |
| LINKUS 临家 | LINKUS | 65, 66, 69, 70, 98, 101 | SPENT | 21 Sep 2026 (archive scan) |  |
| The City Bakery (Mandarin Gallery) | The City Bakery | 76, 80, 85, 89, 100 | SPENT | 21 Sep 2026 (archive scan) |  |
| Torikizoku | Torikizoku | 27, 28, 57, 59, 100 | SPENT | 21 Sep 2026 (archive scan) |  |
| ASIN | ASIN | 17, 34, 96 | SPENT | 21 Sep 2026 (archive scan) |  |
| POP Bakery by POP MART | POP Bakery | 54, 60, 62, 63, 69, 70, 71, 73, 77, 83, 86, 92 | SPENT | 21 Sep 2026 (archive scan) |  |
| Sushi Ryujiro | Sushi Ryujiro | 67, 77, 78, 81, 82, 86, 88, 91 | SPENT | 21 Sep 2026 (archive scan) |  |
| Loulouca (Ann Siang) | Loulouca | 61, 69, 70, 86, 88 | SPENT | 21 Sep 2026 (archive scan) |  |
| Xava Skybar (National Gallery) | Xava | 61, 63, 65, 66, 73, 75, 81, 82, 85, 88 | SPENT | 21 Sep 2026 (archive scan) | No food verdict across ten mentions. |
| Chin Mee Chin (Nex) | Chin Mee Chin | 87 | OPEN | 21 Sep 2026 (archive scan) |  |
| IM QALB (Tampines Mall) | IM QALB | 85 | OPEN | 21 Sep 2026 (archive scan) |  |
| Blue Box Café by Tiffany & Co. | Blue Box | 47, 49, 50, 51, 52, 55, 60, 62, 84 | SPENT | 21 Sep 2026 (archive scan) |  |
| Charcoal Grill Shinpachi | Shinpachi | 64, 68, 70, 72, 75, 76, 78, 80, 83 | SPENT | 21 Sep 2026 (archive scan) |  |
| Liora | Liora | 65, 66, 68, 72, 73, 75, 76, 79, 83 | SPENT | 21 Sep 2026 (archive scan) | No critical verdict across nine mentions. |
| Butter Town Breakfast Club | Butter Town | 80 | OPEN | 21 Sep 2026 (archive scan) |  |
| Chimichanga | Chimichanga | 80 | OPEN | 21 Sep 2026 (archive scan) |  |
| Niku Niku Oh!! Kome | Niku Niku | 77 | OPEN | 21 Sep 2026 (archive scan) |  |
| Jing Studio | Jing Studio | 67, 73 | SPENT | 21 Sep 2026 (archive scan) |  |
| Rituel | Rituel | 71, 112 | SPENT | 21 Sep 2026 (archive scan) |  |
| Tavola Aperta | Tavola Aperta | 60, 62, 71 | SPENT | 21 Sep 2026 (archive scan) |  |
| 1887 by André | 1887 by André | 69 | OPEN | 21 Sep 2026 (archive scan) |  |
| Milli (Sky Dining) | Milli | 17, 27, 28, 32, 34, 56, 59, 68 | SPENT | 21 Sep 2026 (archive scan) |  |
| Seroja | Seroja | 63 | OPEN | 21 Sep 2026 (archive scan) |  |
| Sio Pasta | Sio Pasta | 28, 63 | SPENT | 21 Sep 2026 (archive scan) |  |
| Tonkatsu Daiki | Tonkatsu Daiki | 26, 63 | SPENT | 21 Sep 2026 (archive scan) |  |
| Sushi Tenrai | Sushi Tenrai | 61 | OPEN | 21 Sep 2026 (archive scan) |  |
| Yi Man Fen Dessert (313 Somerset) | Yi Man Fen | 47, 51, 55, 58, 60 | SPENT | 21 Sep 2026 (archive scan) |  |
| Mensho X (Raffles Place) | Mensho X | 41, 47, 49, 50, 52, 55, 59 | SPENT | 21 Sep 2026 (archive scan) |  |
| Ginza Sushi Arai | Ginza Sushi Arai | 58 | OPEN | 21 Sep 2026 (archive scan) |  |
| Jiin Omakase | Jiin | 24, 27, 58 | SPENT | 21 Sep 2026 (archive scan) |  |
| Visitors Café | Visitors Café | 58 | OPEN | 21 Sep 2026 (archive scan) |  |
| FreakyNoods | FreakyNoods | 51, 52, 54, 56 | SPENT | 21 Sep 2026 (archive scan) |  |
| NoMad @ Hilton | NoMad | 56 | OPEN | 21 Sep 2026 (archive scan) |  |
| Rolls Izakaya | Rolls Izakaya | 56 | OPEN | 21 Sep 2026 (archive scan) |  |
| Sam Sam Sam | Sam Sam Sam | 47, 50, 51, 54 | SPENT | 21 Sep 2026 (archive scan) |  |
| Bouillon Gavroche | Bouillon Gavroche | 17, 28, 34, 47, 53 | SPENT | 21 Sep 2026 (archive scan) |  |
| Sukiyaki Jin (Les Amis Group) | Sukiyaki Jin | 17, 47, 49, 50, 53 | SPENT | 21 Sep 2026 (archive scan) |  |
| Hi Stranger (Neil Road) | Hi Stranger | 37 | OPEN | 21 Sep 2026 (archive scan) | Ran in No. 37. |
| Jellyfish | Jellyfish | 33, 34 | SPENT | 21 Sep 2026 (archive scan) |  |
| People People Brewing | People People Brewing | 33 | OPEN | 21 Sep 2026 (archive scan) |  |
| Souper Tang | Souper Tang | 33 | OPEN | 21 Sep 2026 (archive scan) |  |
| Keming Bing Sat | Keming Bing Sat | 31 | OPEN | 21 Sep 2026 (archive scan) |  |
| Mozmoji | Mozmoji | 31 | OPEN | 21 Sep 2026 (archive scan) |  |
| Park Side | Park Side | 31 | OPEN | 21 Sep 2026 (archive scan) |  |
| Steak Gatz | Steak Gatz | 31 | OPEN | 21 Sep 2026 (archive scan) |  |
| Amor (Amoy Street) | Amor | 26 | OPEN | 21 Sep 2026 (archive scan) |  |
| Centro | Centro | 24 | OPEN | 21 Sep 2026 (archive scan) |  |
| Dumpling Darlings | Dumpling Darlings | 24 | OPEN | 21 Sep 2026 (archive scan) |  |
| Satori | Satori | 24 | OPEN | 21 Sep 2026 (archive scan) |  |
| Geumdwaeji Sikdang | Geumdwaeji | 23 | OPEN | 21 Sep 2026 (archive scan) |  |
| Mukai | Mukai | 110 | OPEN | No. 110 build | opening run — record the peg here |
| Bari Bari Grand | Bari Bari Grand | 110 | OPEN | No. 110 build | opening run — record the peg here |
| Les Canons | Les Canons | 110 | OPEN | No. 110 build | opening run — record the peg here |
| Yamamoto’s Hamburg | Yamamoto’s Hamburg | 111 | OPEN | No. 111 build | opening run — record the peg here |
| Decker Barbecue | Decker Barbecue | 111 | OPEN | No. 111 build | opening run — record the peg here |
| Jeju Haenyeo | Jeju Haenyeo | 111 | OPEN | No. 111 build | opening run — record the peg here |
| Miura | Miura | 111 | OPEN | No. 111 build | opening run — record the peg here |
| Kimpson’s Table | Kimpson’s Table | 112 | OPEN | No. 112 build | opening run — record the peg here |
| Kappo Suguru | Kappo Suguru | 112 | OPEN | No. 112 build | opening run — record the peg here |
| Cloudmills | Cloudmills | 113 | OPEN | No. 113 build | opening run — record the peg here |
| GAMJA | GAMJA | 113 | OPEN | No. 113 build | opening run — record the peg here |
| Marymount Bakehouse | Marymount Bakehouse | 113 | OPEN | No. 113 build | opening run — record the peg here |
| Kali Kali | Kali Kali | 113 | OPEN | No. 113 build | opening run — record the peg here |
| OJEJE | OJEJE | 113 | OPEN | No. 113 build | opening run — record the peg here |
