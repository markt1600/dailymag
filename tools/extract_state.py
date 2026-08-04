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
            "ledgers/destination-ledger.md"):
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

print(f"state written: {len(issues)} issues (next = No. {next_no}), "
      f"{len(coverage)} coverage subjects, {len(dest)} destinations")

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
