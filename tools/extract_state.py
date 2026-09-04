#!/usr/bin/env python3
"""Derive machine-readable state from the brand-prompt markdown tables.

The brand-prompt.md stays the authoritative human narrative; this generates
state/*.json so the next build can do fast, reliable lookups the prose can't:
  * issue-log.json      — every issue's no/date/quote/author (dedup "From the Desk"
                          quotes; auto-set the next number)
  * coverage-ledger.json— discrete subjects + last-covered + next-peg (run the
                          New-Peg Test against real data, not a 380KB read)
  * destination-ledger.json — Grand Tour covered + on-deck (weekend Travel Desk)

Run after editing the ledgers each issue:  python3 tools/extract_state.py
"""
import re, json, pathlib

# The ledgers live in their own files since 3 Aug 2026 (the tables outgrew the
# brand prompt — 570KB of a 650KB file). Concatenate spec + ledgers so the
# section-scanning below sees one document either way; rows_under() anchors on
# the LAST occurrence of each heading, so the pointer stubs left in the brand
# prompt never shadow the real tables.
md = pathlib.Path("meridian-brand-prompt.md").read_text()
for _lf in ("ledgers/issue-log-archive.md", "ledgers/issue-log.md",
            "ledgers/coverage-ledger-archive.md", "ledgers/coverage-ledger.md",
            "ledgers/destination-ledger.md", "ledgers/hobby-ledger.md",
            "ledgers/atelier-ledger.md", "ledgers/events-ledger.md",
            "ledgers/undercurrent-ledger.md"):
    _p = pathlib.Path(_lf)
    if _p.exists():
        md += "\n" + _p.read_text()
state = pathlib.Path("state"); state.mkdir(exist_ok=True)


def rows_under(title):
    """Yield the cells of each markdown table row from EVERY '## <title>'
    section in the concatenated document (each section runs to the next '## '
    heading). Aggregating all same-titled sections lets a ledger live in
    several files — the working file plus an archive of trimmed rows — while
    the pointer stub in the brand prompt (no table rows) contributes nothing.
    Requires the exact H2 heading on its own line, so a '### <title> PROTOCOL'
    subheading never matches."""
    for m in re.finditer(r"(?m)^## " + re.escape(title) + r"\s*$", md):
        j = md.find("\n## ", m.end())
        block = md[m.start(): j if j != -1 else len(md)]
        for line in block.splitlines():
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} for c in cells):   # separator row
                continue
            yield cells


# ---- Issue Log ----
issues = []
for cells in rows_under("ISSUE LOG"):
    if len(cells) < 4 or not re.match(r"^\d+$", cells[0]):
        continue
    issues.append({
        "no": int(cells[0]),
        "date": cells[1],
        "quote": cells[2].strip('"'),
        "author": cells[3],
        "note": (cells[4] if len(cells) > 4 else ""),   # full note: build_manifest parses title + search text from it
    })
issues.sort(key=lambda x: x["no"])
next_no = (max((i["no"] for i in issues), default=0) + 1) if issues else 1
(state / "issue-log.json").write_text(json.dumps(
    {"next_issue": next_no,
     "used_quotes": sorted({i["quote"] for i in issues}),
     "issues": issues}, indent=2, ensure_ascii=False))

# ---- Coverage Ledger ----
coverage = []
for cells in rows_under("COVERAGE LEDGER"):
    if len(cells) < 5 or cells[0] in ("Subject",):
        continue
    coverage.append({
        "subject": cells[0], "type": cells[1],
        "last_covered": cells[2], "last_peg": cells[3][:400],
        "next_peg": cells[4][:400],
    })
(state / "coverage-ledger.json").write_text(json.dumps(
    {"count": len(coverage), "subjects": coverage}, indent=2, ensure_ascii=False))

# ---- Destination Ledger (Covered table has: Destination|Issue|Angle|Next eligible) ----
dest = []
for cells in rows_under("DESTINATION LEDGER"):
    if len(cells) < 3 or cells[0] in ("Destination",):
        continue
    dest.append({"destination": cells[0].strip("*"), "issue": cells[1],
                 "angle": cells[2][:300], "next_eligible": cells[3] if len(cells) > 3 else ""})
(state / "destination-ledger.json").write_text(json.dumps(
    {"count": len(dest), "destinations": dest}, indent=2, ensure_ascii=False))

# ---- Hobby Ledger (The Rabbit Hole). Parsed by SUBSECTION because Covered
# (|Hobby|Issue|Angle|) and Queued (|Hobby|Run order|Focus|) share a 3-cell
# shape: '### Covered', '### Queued …', '### On-deck pipeline'. ----
hob_cov, hob_queue, hob_pipe = [], [], []
for _hm in re.finditer(r"(?m)^## HOBBY LEDGER\s*$", md):
    _hend = md.find("\n## ", _hm.end())
    _hblock = md[_hm.start(): _hend if _hend != -1 else len(md)]
    for _sub in re.split(r"(?m)^### ", _hblock)[1:]:
        _rows = []
        for line in _sub.splitlines()[1:]:
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} for c in cells) or cells[0] == "Hobby":
                continue
            _rows.append(cells)
        _title = _sub.splitlines()[0].lower()
        if _title.startswith("covered"):
            hob_cov += [{"hobby": c[0].strip("*"), "issue": c[1], "angle": c[2][:300]}
                        for c in _rows if len(c) >= 3]
        elif _title.startswith("queued"):
            hob_queue += [{"hobby": c[0].strip("*"), "order": c[1], "focus": c[2][:500]}
                          for c in _rows if len(c) >= 3]
        elif _title.startswith("on-deck"):
            hob_pipe += [{"hobby": c[0].strip("*"), "category": c[1],
                          "communities": c[2][:300], "fit": c[3][:300]}
                         for c in _rows if len(c) >= 4]
(state / "hobby-ledger.json").write_text(json.dumps(
    {"covered": hob_cov, "queued": hob_queue, "pipeline": hob_pipe}, indent=2, ensure_ascii=False))

# ---- Atelier Ledger (The Atelier — one purchase category per edition).
# Same subsection shape as the hobby ledger. ----
at_cov, at_queue, at_pipe = [], [], []
for _am in re.finditer(r"(?m)^## ATELIER LEDGER\s*$", md):
    _aend = md.find("\n## ", _am.end())
    _ablock = md[_am.start(): _aend if _aend != -1 else len(md)]
    for _sub in re.split(r"(?m)^### ", _ablock)[1:]:
        _rows = []
        for line in _sub.splitlines()[1:]:
            s = line.strip()
            if not s.startswith("|"):
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= {"-", ":", " "} for c in cells) or cells[0] == "Category":
                continue
            _rows.append(cells)
        _title = _sub.splitlines()[0].lower()
        if _title.startswith("covered"):
            at_cov += [{"category": c[0].strip("*"), "issue": c[1], "angle": c[2][:300]}
                       for c in _rows if len(c) >= 3]
        elif _title.startswith("queued"):
            # 3,000 chars: an editor's Atelier brief carries the whole angle
            # (mechanism, makers, tiers, white-label truth, sceptic) and a
            # 600-char slice cut it mid-sentence — the queue is 1-3 rows, so
            # the state file stays small either way.
            at_queue += [{"category": c[0].strip("*"), "order": c[1], "focus": c[2][:3000]}
                         for c in _rows if len(c) >= 3]
        elif _title.startswith("on-deck"):
            at_pipe += [{"category": c[0].strip("*"), "rotation": c[1],
                         "fit": c[2][:300], "sources": c[3][:300]}
                        for c in _rows if len(c) >= 4]
(state / "atelier-ledger.json").write_text(json.dumps(
    {"covered": at_cov, "queued": at_queue, "pipeline": at_pipe}, indent=2, ensure_ascii=False))

# ---- events ledger (editor, 31 Aug 2026): dead events, so a cancelled show
# cannot be re-researched back into The Diary by a later build. Status is the
# gate: CANCELLED / POSTPONED / PULLED bar the event, REINSTATED clears it.
dead = []
for c in rows_under("Dead Events"):
    if len(c) < 4 or c[0].lower().startswith("event"):
        continue
    dead.append({"event": c[0], "where": c[1], "was_listed": c[2],
                 "status": c[3].strip().upper(),
                 "checked": c[4] if len(c) > 4 else "",
                 "note": c[5] if len(c) > 5 else ""})
_barred = [d for d in dead if d["status"].split()[0] in ("CANCELLED", "POSTPONED", "PULLED")]
(state / "events-ledger.json").write_text(json.dumps(
    {"dead": dead, "barred": [d["event"] for d in _barred]}, indent=2, ensure_ascii=False))

# ---- undercurrent ledger (editor, 4 Sep 2026): subjects, not just geography.
# Rotating the country stopped the same flag twice running and nothing else —
# India astrology ran in 68 and again in 72, Vietnam idols in 67 and again 75.
uc = []
for c in rows_under("Undercurrents Covered"):
    if len(c) < 3 or c[0].lower().startswith("issue"):
        continue
    uc.append({"issue": c[0], "country": c[1], "subject": c[2],
               "key": (c[3] if len(c) > 3 else "").strip()})
(state / "undercurrent-ledger.json").write_text(json.dumps(
    {"covered": uc, "keys": [u["key"] for u in uc if u["key"]]},
    indent=2, ensure_ascii=False))

print(f"state written: {len(issues)} issues (next = No. {next_no}), "
      f"{len(coverage)} coverage subjects, {len(dest)} destinations, "
      f"{len(hob_cov)} hobbies covered / {len(hob_pipe)} on deck, "
      f"{len(_barred)} barred event(s), {len(uc)} undercurrents")

# ---- note-discipline nudges (editor, 4 Aug 2026; soft warnings, never fail) ----
# The newest note should be working memory (<=3,000 chars target) and must end
# with the "Ledger check:" receipt proving the pre-selection New-Peg pass ran.
# Applies from No. 63 (older rows are history, kept verbatim).
if issues:
    _newest = issues[-1]
    _note = str(_newest.get("note", ""))
    if int(str(_newest.get("no", 0)) or 0) >= 63:
        if len(_note) > 4000:
            print(f"  WARNING: No. {_newest['no']}'s note is {len(_note):,} chars (target <=3,000) — "
                  "the note is working memory, not a transcript; see THE NOTE FORMAT in the spec")
        if "Ledger check:" not in _note:
            print(f"  WARNING: No. {_newest['no']}'s note has no 'Ledger check:' receipt — "
                  "the pre-selection New-Peg pass must name what it demoted (or 'none demoted')")
