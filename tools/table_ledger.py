#!/usr/bin/env python3
"""Record this issue's Table venues in ledgers/table-ledger.md.

    python3 tools/table_ledger.py build/meridianNN.html NN [--dry-run]

Editor, 21 Sep 2026 (reader-reported): Kuro Kare ran in Nos. 97, 99, 105 and
109 because "rotate venues" lived only in prose. The ledger is the memory,
validate.py is the gate, and this script is the bookkeeping — deterministic,
so a build cannot forget to log a venue.

What it does, idempotently:
  * finds The Table section (the Diary page whose text carries "The Table"),
    minus its sources block;
  * for every existing row whose Key appears in that text, appends NN to Runs
    (once);
  * for every `<b class="venue">Name</b>` not matching an existing Key, adds a
    row (Key = Name, Runs = NN, Status = OPEN);
  * flips Status: OPEN -> SPENT once Runs has two entries; REINSTATED -> SPENT
    after this run. It never sets REINSTATED or CLOSED — those are the
    editor's.
Writes the ledger atomically (tmp + os.replace) and preserves every other line
byte-for-byte.
"""
import html as H
import os
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ledgers" / "table-ledger.md"


def norm(s):
    s = H.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def table_section(html):
    """Return (section_html_without_sources, venue_marks) or (None, [])."""
    body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    for m in re.finditer(r'<section[^>]*class="page[^"]*"[^>]*>(.*?)</section>', body, re.S):
        sec = m.group(1)
        sec_nofn = re.sub(r'<div class="fn">.*?</div>', "", sec, flags=re.S)
        txt = H.unescape(re.sub(r"<[^>]+>", " ", sec_nofn))
        if re.search(r"\bThe Table\b", txt) and "Diary" in txt:
            marks = [H.unescape(re.sub(r"<[^>]+>", "", v)).strip()
                     for v in re.findall(r'<b class="venue"[^>]*>(.*?)</b>', sec_nofn, re.S)]
            return sec_nofn, marks
    return None, []


def parse_rows(lines):
    """Yield (index, cells) for table rows under '## Table Venues'."""
    on = False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            on = line.strip() == "## Table Venues"
            continue
        if not on or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0].lower() == "venue" or all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        yield i, cells


def fmt(cells):
    return "| " + " | ".join(cells) + " |"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if len(args) < 2:
        sys.exit(__doc__)
    html = pathlib.Path(args[0]).read_text()
    issue = int(args[1])
    sec, marks = table_section(html)
    if sec is None:
        print("table_ledger: no Table section found — nothing recorded")
        return
    text = " " + norm(sec) + " "
    lines = LEDGER.read_text().splitlines()
    changed = []
    known = []
    last_row = None
    for i, c in parse_rows(lines):
        last_row = i
        key = H.unescape(c[1])
        known.append(norm(key))
        if not key.strip() or " " + norm(key) + " " not in text:
            continue
        runs = [int(x) for x in re.findall(r"\d+", c[2])]
        status = c[3].strip().upper()
        if issue not in runs:
            runs.append(issue)
            runs.sort()
            c[2] = ", ".join(map(str, runs))
            changed.append(f"recorded No. {issue} for {c[0]} (runs now {c[2]})")
        if status == "REINSTATED" or (status == "OPEN" and len(runs) >= 2):
            c[3] = "SPENT"
            changed.append(f"{c[0]}: {status} -> SPENT")
        lines[i] = fmt(c)
    new_rows = []
    for name in marks:
        n = norm(name)
        if len(n) < 3 or n in known or any(" " + k + " " in " " + n + " " for k in known if k):
            continue
        known.append(n)
        new_rows.append(fmt([name, name, str(issue), "OPEN", f"No. {issue} build", "opening run — record the peg here"]))
        changed.append(f"new row: {name}")
    if new_rows:
        at = (last_row + 1) if last_row is not None else len(lines)
        lines[at:at] = new_rows
    if not changed:
        print(f"table_ledger: No. {issue} — nothing to record")
        return
    print(f"table_ledger: No. {issue}\n  " + "\n  ".join(changed))
    if dry:
        return
    tmp = LEDGER.with_suffix(".md.tmp")
    tmp.write_text("\n".join(lines) + "\n")
    os.replace(tmp, LEDGER)


if __name__ == "__main__":
    main()
