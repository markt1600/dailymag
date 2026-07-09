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

md = pathlib.Path("meridian-brand-prompt.md").read_text()
state = pathlib.Path("state"); state.mkdir(exist_ok=True)


def rows_under(title):
    """Yield the cells of each markdown table row in the '## <title>' section
    (up to the next '## ' heading). Anchors on the real H2 heading so it doesn't
    match a '### <title> PROTOCOL' subheading."""
    head = "\n## " + title
    i = md.find(head)
    if i == -1:
        return
    j = md.find("\n## ", i + len(head))
    block = md[i: j if j != -1 else len(md)]
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
        "note": (cells[4][:300] if len(cells) > 4 else ""),
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
