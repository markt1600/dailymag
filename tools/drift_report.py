#!/usr/bin/env python3
"""The weekly drift report — measure the week's books against the house rules.

    python3 tools/drift_report.py [--issues 7] [--out reports/drift-YYYY-MM-DD.md]

Editor, 17 Nov 2026 (reader-approved). Every style fix between September and
November began with the reader noticing something: paragraph-length headlines,
boxes cutting through articles, riddle headlines, a 12pt box, a broken grid,
boxes about a different story. The gates catch what we thought to gate. This
report is the look across a week that nobody was taking: it re-runs EVERY
current gate over each of the last N issues as if it were tomorrow's (so a
rule added on Friday is applied to Monday's book too), counts failures by
rule, and prints the plain measurements beside the reference issues — so a
slow slide shows up as a row of numbers before it shows up at breakfast.

It measures; it does not judge prose. The Sunday routine that runs it adds a
short cold read of the week on top.
"""
import datetime
import html as H
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES = ["STYLE LOCK", "NEWS REGISTER", "BOX LAW", "LAY OPENING", "DEEP-DIVE OPENING", "PROSE BLOCK LAW",
         "TYPE SCALE LOCK", "TAG BALANCE", "TABLE REPEAT", "UNDERCURRENT REPEAT", "house style", "voice"]
# once-only ledgers always fire when a shipped issue is re-validated against ledgers that now contain it
SELF_REFERENCE = ("was already covered", "TABLE REPEAT", "RETIRED SUGGESTION", "UNDERCURRENT REPEAT",
                  "no <b class=\"venue\">", "quote", "already used", "recycled from the last", "Held, Now Resolved")


def plain(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def issue_files(n):
    arch = sorted((ROOT / "archive").glob("no-*/index.html"),
                  key=lambda p: int(re.search(r"no-(\d+)", str(p)).group(1)))
    out = [(int(re.search(r"no-(\d+)", str(p)).group(1)), p) for p in arch]
    live = (ROOT / "index.html").read_text()
    m = re.search(r"No\.\s*(\d{1,3})\s*(?:·|&middot;)\s*Singapore", live)
    if m and (not out or int(m.group(1)) != out[-1][0]):
        out.append((int(m.group(1)), ROOT / "index.html"))
    return out[-n:]


def measure(no, path):
    t = path.read_text()
    body = re.sub(r"<script.*?</script>", "", t, flags=re.S)
    secs = re.findall(r'<section[^>]*class="page[^"]*"[^>]*>(.*?)</section>', body, re.S)
    heds = [plain(h) for h in re.findall(r'<div class="hed[^"]*"[^>]*>(.*?)</div>', body, re.S)]
    hw = [len(h.split()) for h in heds] or [0]
    m = {"issue": no, "pages": len(secs), "hed_avg": round(sum(hw) / len(hw), 1), "hed_max": max(hw),
         "heroes": len(re.findall(r'class="ph-frame', body)), "footnotes": len(re.findall(r'class="fnref"', body)),
         "chatter": len(re.findall(r'class="chatter', body)), "pulls": len(re.findall(r'class="pull', body))}
    c = re.search(r"assembled in ([^·<]+)·[^≈]*≈\s*US\$([\d,.]+)", plain(secs[0]) if secs else "")
    m["build"] = c.group(1).strip() if c else ""
    m["cost"] = c.group(2) if c else ""
    # re-run every current gate as if this were a future issue
    renum = re.sub(r"No\.\s*\d+(\s*(?:·|&middot;)\s*Singapore)", r"No. 999\1", t, count=1)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=str(ROOT / "build") if (ROOT / "build").exists() else None) as f:
        f.write(renum)
        tmp = f.name
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "validate.py"), tmp], capture_output=True, text=True, cwd=ROOT)
    pathlib.Path(tmp).unlink(missing_ok=True)
    errs = [l for l in r.stdout.splitlines() if l.startswith("ERROR")]
    errs = [e for e in errs if not any(s in e for s in SELF_REFERENCE)]
    warns = [l for l in r.stdout.splitlines() if l.startswith("WARN")]
    m["rules"] = {k: sum(1 for e in errs if k in e) for k in RULES}
    m["rules"]["other"] = sum(1 for e in errs if not any(k in e for k in RULES))
    m["errors"] = len(errs)
    m["warnings"] = len(warns)
    m["examples"] = [e[7:160] for e in errs[:3]]
    ep = ROOT / "state" / "editor-pass" / f"{no:03d}.json"
    if ep.exists():
        try:
            d = json.loads(ep.read_text())
            sc = [p.get("recheck", p.get("keep_reading", 0)) for p in d.get("pages", [])]
            m["editor"] = round(sum(sc) / len(sc), 2) if sc else None
            m["sent_back"] = sum(1 for p in d.get("pages", []) if p.get("verdict") == "rework")
        except Exception:
            m["editor"] = None
    return m


def held_summary():
    f = ROOT / "state" / "held-ledger.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    items = d.get("items", [])
    op = [i for i in items if i["status"] == "OPEN"]
    return {"open": len(op), "ask": sum(1 for i in op if i["kind"] == "ask"),
            "resolved": sum(1 for i in items if i["status"] == "RESOLVED"),
            "dropped": sum(1 for i in items if i["status"] == "DROPPED"),
            "oldest": min((i["since"] for i in op), default="")}


def main():
    a = sys.argv[1:]
    n = int(a[a.index("--issues") + 1]) if "--issues" in a else 7
    today = datetime.datetime.utcnow().date() + datetime.timedelta(hours=0)
    out = pathlib.Path(a[a.index("--out") + 1]) if "--out" in a else ROOT / "reports" / f"drift-{today.isoformat()}.md"
    rows = [measure(no, p) for no, p in issue_files(n)]
    L = []
    L.append(f"# MERIDIAN drift report — week to No. {rows[-1]['issue']}  ({today.isoformat()})\n")
    L.append("Every current gate re-run over each issue as if it were tomorrow's book. Zero is the target in every rule column.\n")
    L.append("## Rules broken, by issue\n")
    cols = [k for k in RULES + ["other"] if any(r["rules"].get(k) for r in rows)] or ["STYLE LOCK"]
    L.append("| Issue | " + " | ".join(cols) + " | Total | Warnings |")
    L.append("|---|" + "---|" * (len(cols) + 2))
    for r in rows:
        L.append(f"| No. {r['issue']} | " + " | ".join(str(r["rules"].get(k, 0)) for k in cols) + f" | **{r['errors']}** | {r['warnings']} |")
    L.append("\n## Measurements\n")
    L.append("| Issue | Pages | Headline avg / max (words) | Photos | Footnotes | Boxes | Pull quotes | Reader's Editor (mean, sent back) | Build | Cost US$ |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        ed = f"{r['editor']} / {r.get('sent_back', 0)}" if r.get("editor") else "—"
        L.append(f"| No. {r['issue']} | {r['pages']} | {r['hed_avg']} / {r['hed_max']} | {r['heroes']} | {r['footnotes']} | {r['chatter']} | {r['pulls']} | {ed} | {r['build']} | {r['cost']} |")
    L.append("| *reference* | 25 (24 before No. 166) | 7 / 12 (No. 38) | 12–13 | 170–180 | 32–38 | 4–14 | — | — | — |")
    # trend flags
    flags = []
    first, last = rows[0], rows[-1]
    if last["hed_avg"] - first["hed_avg"] >= 2:
        flags.append(f"Headlines lengthened across the week: {first['hed_avg']} → {last['hed_avg']} words on average.")
    if last["hed_avg"] > 10:
        flags.append(f"Headline average is {last['hed_avg']} words against a house average of 7 — the desk is writing to the 14-word ceiling, not to the house length.")
    if last["heroes"] < 9:
        flags.append(f"Only {last['heroes']} photographs in the latest issue (reference 12–13).")
    for k in cols:
        tot = sum(r["rules"].get(k, 0) for r in rows)
        late = sum(r["rules"].get(k, 0) for r in rows[-3:])
        if tot and late >= max(2, tot * 0.6):
            flags.append(f"{k}: {tot} breaches this week, {late} of them in the last three issues — rising.")
    eds = [r["editor"] for r in rows if r.get("editor")]
    if len(eds) >= 3 and eds[-1] < eds[0] - 0.3:
        flags.append(f"Reader's Editor mean fell from {eds[0]} to {eds[-1]}.")
    L.append("\n## Flags\n")
    L += [f"- {f}" for f in flags] or ["- None. No rule column is rising and the measurements sit inside their reference bands."]
    worst = max(rows, key=lambda r: r["errors"])
    if worst["errors"]:
        L.append(f"\n## Worst issue this week: No. {worst['issue']} ({worst['errors']} breaches)\n")
        L += [f"- {e}" for e in worst["examples"]]
    h = held_summary()
    if h:
        L.append("\n## Held items\n")
        L.append(f"- {h['open']} open ({h['ask']} need a human call), oldest held since No. {h['oldest']}; "
                 f"{h['resolved']} resolved and {h['dropped']} dropped to date.")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
