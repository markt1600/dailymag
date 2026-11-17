#!/usr/bin/env python3
"""The Held Ledger — close the loop on what the desk could not verify.

    python3 tools/held_ledger.py list [--issue NN]        # open items, oldest first, with what is due
    python3 tools/held_ledger.py add NN "<desk>" "<item>" [--kind fact|date|ask] [--due YYYY-MM-DD]
    python3 tools/held_ledger.py check ID NN ["note"]      # re-checked this issue, still open
    python3 tools/held_ledger.py resolve ID NN "<what the answer turned out to be, and the source>"
    python3 tools/held_ledger.py drop ID NN "<why it will never be answered or no longer matters>"

Editor, 17 Nov 2026 (reader-approved): every Issue Log note ends with a HELD
list, and almost nothing on it was ever revisited — Christmas Wonderland's
price was "held" for seven issues in a row, and the Singapore radio-law
question from No. 154.5 was answered only because the reader happened to
commission No. 158.5. A held item has to be a ROW with an age, not a clause
in a note. kinds: fact (unverified claim — re-research it), date (a scheduled
release — check on or after --due), ask (only a human phone call will settle
it; listed for the reader, never silently dropped).

Source of truth: ledgers/held-ledger.md ("## Held Items" table);
tools/extract_state.py mirrors it to state/held-ledger.json.
"""
import datetime
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ledgers" / "held-ledger.md"
COLS = ["ID", "Held since", "Desk", "Kind", "Item", "Due", "Status", "Last checked", "Outcome"]


def load():
    lines = LEDGER.read_text().splitlines()
    rows = []
    on = False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            on = line.strip() == "## Held Items"
            continue
        if not on or not line.startswith("|"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < len(COLS) or c[0] == "ID" or set(c[0]) <= {"-", ":"}:
            continue
        rows.append((i, dict(zip(COLS, c))))
    return lines, rows


def save(lines):
    tmp = LEDGER.with_suffix(".md.tmp")
    tmp.write_text("\n".join(lines) + "\n")
    os.replace(tmp, LEDGER)


def fmt(r):
    return "| " + " | ".join(str(r[c]).replace("|", "/").replace("\n", " ") for c in COLS) + " |"


def issue_no(s):
    m = re.search(r"\d+(?:\.\d)?", str(s))
    return float(m.group(0)) if m else 0.0


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    lines, rows = load()
    opts = {}
    pos = []
    it = iter(a[1:])
    for x in it:
        if x.startswith("--"):
            opts[x[2:]] = next(it, "")
        else:
            pos.append(x)

    if cmd == "list":
        cur = issue_no(opts.get("issue", 0))
        today = datetime.date.today().isoformat()
        open_rows = [r for _, r in rows if r["Status"] == "OPEN"]
        open_rows.sort(key=lambda r: issue_no(r["Held since"]))
        print(f"{len(open_rows)} open held item(s); {sum(r['Status'] == 'RESOLVED' for _, r in rows)} resolved, "
              f"{sum(r['Status'] == 'DROPPED' for _, r in rows)} dropped all-time\n")
        for r in open_rows:
            age = f"{int(cur - issue_no(r['Held since']))} issues" if cur else ""
            flags = []
            if r["Due"] and r["Due"] <= today:
                flags.append("DUE — check now")
            if cur and cur - issue_no(r["Held since"]) >= 14 and r["Kind"] != "ask":
                flags.append("STALE — resolve, convert to ask, or drop with a reason")
            if r["Kind"] == "ask":
                flags.append("needs a human")
            print(f"  {r['ID']:6s} since No. {r['Held since']:6s} {age:10s} [{r['Kind']:4s}] {r['Desk'][:16]:16s} "
                  f"{r['Item'][:90]}{'  <-- ' + '; '.join(flags) if flags else ''}")
        return

    if cmd == "add":
        nn, desk, item = pos[0], pos[1], pos[2]
        nxt = max([int(re.sub(r"\D", "", r["ID"]) or 0) for _, r in rows] + [0]) + 1
        r = dict(zip(COLS, [f"H{nxt:03d}", nn, desk, opts.get("kind", "fact"), item, opts.get("due", ""),
                            "OPEN", nn, ""]))
        at = (rows[-1][0] + 1) if rows else len(lines)
        lines[at:at] = [fmt(r)]
        save(lines)
        print("added", r["ID"])
        return

    if cmd in ("check", "resolve", "drop"):
        hid, nn = pos[0], pos[1]
        note = pos[2] if len(pos) > 2 else ""
        for i, r in rows:
            if r["ID"] == hid:
                r["Last checked"] = nn
                if cmd == "check":
                    if note:
                        r["Outcome"] = note
                else:
                    if not note:
                        sys.exit(f"{cmd} needs the outcome in words")
                    r["Status"] = "RESOLVED" if cmd == "resolve" else "DROPPED"
                    r["Outcome"] = f"No. {nn}: {note}"
                lines[i] = fmt(r)
                save(lines)
                print(cmd, hid, "ok")
                return
        sys.exit(f"no such held item: {hid}")

    sys.exit(__doc__)


if __name__ == "__main__":
    main()
