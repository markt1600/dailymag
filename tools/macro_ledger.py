#!/usr/bin/env python3
"""The Macro Ledger — the Macro Desk's memory.

    python3 tools/macro_ledger.py fetch                      # pull every FRED-backed indicator, with history
    python3 tools/macro_ledger.py record KEY VALUE --asof YYYY-MM-DD --source "<where read>" [--issue NN]
    python3 tools/macro_ledger.py show [--theme four|liquidity|growth|inflation|credit|asia|valuation|flows|rates]
    python3 tools/macro_ledger.py call NN "<regime in a phrase>" "<trigger 1>" "<trigger 2>" ["<trigger 3>"]
    python3 tools/macro_ledger.py hold KEY NN "<why it could not be read at source today>"
    python3 tools/macro_ledger.py check NN                   # gate: fresh data, manual indicators in cadence, a call on record
    python3 tools/macro_ledger.py theme [YYYY-MM-DD]         # which Trend theme runs on that Singapore date

Editor, 17 Nov 2026 (reader-approved). The Macro Desk was a daily recap: three
issues running (Nos. 162, 164, 165) led on the same priced December hike, read
off the Treasury curve, a futures monitor and sell-side quotes, and nothing on
the page looked back further than a week. A desk cannot write "the third week
of widening" unless something remembers the first two. This ledger is that
memory: about thirty indicators with their history, and the desk's standing
regime call with the conditions that would change it.

Source of truth: state/macro-ledger.json. ledgers/macro-ledger.md is a rendered
view, rewritten on every change — never edit it by hand.

Two kinds of indicator:
  * FRED-backed — fetched automatically from the St. Louis Fed's public CSV
    endpoint, with a year and a half of history. Never typed by hand.
  * manual — read at source by the build (FactSet, CFTC, ICI, the World Gold
    Council, Vanguard, the People's Bank of China, Shiller) and entered with
    `record`, which requires the as-of date and the source. A number nobody
    read at source does not go in.
"""
import concurrent.futures
import csv
import datetime
import io
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "macro-ledger.json"
VIEW = ROOT / "ledgers" / "macro-ledger.md"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}&cosd={since}"

# key: (name, unit, theme, cadence in days, FRED id or None, transform, where a manual one is read)
INDICATORS = {
    # THE FOUR — the instruments the desk exists to explain (editor, 18 Nov 2026)
    "vwra":        ("VWRA, Vanguard FTSE All-World UCITS ETF, NAV", "US$", "four", 1, None, None,
                    "Vanguard VWRA product page (NAV at the last close, USD)"),
    "pimco_income_1w": ("PIMCO GIS Income Fund, 1-week total return", "%", "four", 1, None, None,
                    "POEMS fund finder (Admin SGD-hedged Income class) or PIMCO's own fund page; name the share class"),
    "gold":        ("Gold, spot", "US$/oz", "four", 1, None, None,
                    "LBMA PM price or a named spot quote (Trading Economics, Kitco)"),
    "btc":         ("Bitcoin, Coinbase", "US$", "four", 1, "CBBTCUSD", None, ""),
    # rates — the price of money
    "us2y":        ("US 2-year Treasury yield", "%", "rates", 1, "DGS2", None, ""),
    "us10y":       ("US 10-year Treasury yield", "%", "rates", 1, "DGS10", None, ""),
    "real10y":     ("US 10-year real yield (TIPS)", "%", "rates", 1, "DFII10", None, ""),
    "breakeven10": ("US 10-year breakeven inflation", "%", "rates", 1, "T10YIE", None, ""),
    "curve2s10s":  ("US 10-year minus 2-year", "pp", "rates", 1, "T10Y2Y", None, ""),
    "termprem10":  ("US 10-year term premium (Kim-Wright)", "pp", "rates", 7, "THREEFYTP10", None, ""),
    # liquidity & funding
    "fed_bs":      ("Federal Reserve balance sheet", "US$tn", "liquidity", 7, "WALCL", "mn_to_tn", ""),
    "rrp":         ("Fed overnight reverse repo", "US$bn", "liquidity", 1, "RRPONTSYD", None, ""),
    "tga":         ("US Treasury General Account", "US$bn", "liquidity", 7, "WTREGEN", "mn_to_bn", ""),
    "sofr":        ("Secured Overnight Financing Rate", "%", "liquidity", 1, "SOFR", None, ""),
    "nfci":        ("Chicago Fed financial conditions (above 0 = tight)", "index", "liquidity", 7, "NFCI", None, ""),
    "dollar":      ("Broad trade-weighted US dollar", "index", "liquidity", 1, "DTWEXBGS", None, ""),
    # credit & stress
    "hy_oas":      ("US high-yield credit spread", "pp", "credit", 1, "BAMLH0A0HYM2", None, ""),
    "ig_oas":      ("US investment-grade credit spread", "pp", "credit", 1, "BAMLC0A0CM", None, ""),
    "vix":         ("VIX equity volatility", "index", "credit", 1, "VIXCLS", None, ""),
    # inflation & labour
    "cpi_yoy":     ("US consumer prices, year on year", "%", "inflation", 31, "CPIAUCSL", "yoy", ""),
    "core_cpi_yoy": ("US core consumer prices, year on year", "%", "inflation", 31, "CPILFESL", "yoy", ""),
    "unemp":       ("US unemployment rate", "%", "inflation", 31, "UNRATE", None, ""),
    "claims":      ("US initial jobless claims", "thousand", "inflation", 7, "ICSA", "to_thousand", ""),
    "brent":       ("Brent crude, spot", "US$", "inflation", 1, "DCOILBRENTEU", None, ""),
    # growth & earnings
    "gdpnow":      ("Atlanta Fed GDPNow, current quarter", "% saar", "growth", 7, "GDPNOW", None, ""),
    "eps_growth":  ("S&P 500 blended earnings growth, current quarter", "%", "growth", 7, None, None,
                    "FactSet Earnings Insight (weekly PDF)"),
    "fwd_eps":     ("S&P 500 forward 12-month earnings per share", "US$", "growth", 7, None, None,
                    "FactSet Earnings Insight (weekly PDF)"),
    # valuation & the fund
    "fwd_pe":      ("S&P 500 forward price/earnings", "x", "valuation", 7, None, None, "FactSet Earnings Insight"),
    "cape":        ("Shiller cyclically adjusted P/E", "x", "valuation", 31, None, None, "Shiller data / multpl.com"),
    "vwra_us":     ("All-world index: United States weight", "%", "valuation", 31, None, None,
                    "Vanguard VWRA factsheet or FTSE All-World factsheet"),
    "vwra_top10":  ("All-world index: top-ten holdings weight", "%", "valuation", 31, None, None,
                    "Vanguard VWRA factsheet or FTSE All-World factsheet"),
    # positioning & flows
    "cftc_ust10":  ("Speculative net position, 10-year Treasury futures", "thousand contracts", "flows", 7, None, None,
                    "CFTC Commitments of Traders (weekly)"),
    "equity_flows": ("US equity fund and ETF flows, latest week", "US$bn", "flows", 7, None, None,
                     "Investment Company Institute weekly flows"),
    "bond_flows":  ("US bond fund and ETF flows, latest week", "US$bn", "flows", 7, None, None,
                    "Investment Company Institute weekly flows"),
    "cb_gold":     ("Central-bank net gold purchases, latest month", "tonnes", "flows", 31, None, None,
                    "World Gold Council monthly central-bank statistics"),
    "btc_etf_flows": ("US spot bitcoin ETF net flows, latest week", "US$bn", "flows", 7, None, None,
                      "Farside Investors or issuer filings"),
    # Asia
    "usdjpy":      ("US dollar / Japanese yen", "yen", "asia", 1, "DEXJPUS", None, ""),
    "usdcny":      ("US dollar / Chinese yuan", "yuan", "asia", 1, "DEXCHUS", None, ""),
    "jgb10":       ("Japan 10-year government bond yield", "%", "asia", 7, None, None,
                    "Japan Ministry of Finance JGB yield table"),
    "china_tsf":   ("China total social financing, year on year", "%", "asia", 31, None, None,
                    "People's Bank of China monthly financial statistics"),
}

# The Trend rotation, by Singapore weekday (Monday = 0)
THEMES = {
    0: ("liquidity", "Liquidity", "Liquidity and funding: the Fed's balance sheet, reserves, the Treasury's cash, the dollar"),
    1: ("growth", "Earnings", "Growth and earnings: what the companies inside the all-world fund are earning, and how estimates are moving"),
    2: ("inflation", "Inflation", "Inflation and labour: prices, wages, jobs and oil, over months not days"),
    3: ("credit", "Credit", "Credit and positioning: spreads, volatility, and how speculators and funds are leaning"),
    4: ("asia", "Asia", "Asia: China's credit cycle, the Bank of Japan and the yen, the region's central banks"),
    5: ("valuation", "Valuation", "Valuation and the long run: what is in the price, on a chart of ten years or more"),
    6: ("flows", "Week Ahead", "The week ahead and the flows: the dated calendar, fund flows, central-bank gold buying"),
}


def today_sg():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).date()


def load():
    if STATE.exists():
        d = json.loads(STATE.read_text())
    else:
        d = {"indicators": {}, "calls": [], "fetched": "", "fetch_errors": {}}
    for k, (name, unit, theme, cad, fred, tr, where) in INDICATORS.items():
        e = d["indicators"].setdefault(k, {"readings": []})
        e.update({"name": name, "unit": unit, "theme": theme, "cadence": cad, "fred": fred or "", "read_at": where})
    return d


def save(d):
    tmp = STATE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    os.replace(tmp, STATE)
    render(d)


def merge(e, date, value, source="", issue=None):
    rs = {r["date"]: r for r in e["readings"]}
    r = {"date": date, "value": value}
    if source:
        r["source"] = source
    if issue:
        r["issue"] = issue
    rs[date] = r
    e["readings"] = [rs[k] for k in sorted(rs)]


def fetch(d):
    since = (today_sg() - datetime.timedelta(days=560)).isoformat()
    errs = {}
    def pull(k):
        fred, tr = INDICATORS[k][4], INDICATORS[k][5]
        start = (today_sg() - datetime.timedelta(days=1000)).isoformat() if tr == "yoy" else since
        last = None
        for _ in range(3):
            try:
                # curl, not urllib: it honours the sandbox's proxy and CA bundle, where urllib hangs
                raw = subprocess.run(["curl", "-sS", "-f", "-m", "25", FRED.format(id=fred, since=start)],
                                     capture_output=True, text=True, timeout=35, check=True).stdout
                return [(r[0], float(r[1])) for r in csv.reader(io.StringIO(raw))
                        if len(r) > 1 and r[1] not in ("", ".") and r[0][:1].isdigit()]
            except Exception as ex:  # a dead endpoint must not stop a build; `check` reports staleness
                last = ex
        return last

    keys = [k for k, v in INDICATORS.items() if v[4]]
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        got = dict(zip(keys, pool.map(pull, keys)))
    for k in keys:
        tr = INDICATORS[k][5]
        rows = got[k]
        if isinstance(rows, Exception) or not rows:
            errs[k] = str(rows)[:120] or "empty"
            continue
        if tr == "yoy":
            by = dict(rows)
            out = []
            for dt, v in rows:
                y = f"{int(dt[:4]) - 1}{dt[4:]}"
                if y in by and by[y]:
                    out.append((dt, round((v / by[y] - 1) * 100, 2)))
            rows = [r for r in out if r[0] >= since]
        elif tr == "mn_to_tn":
            rows = [(a, round(b / 1e6, 3)) for a, b in rows]
        elif tr == "mn_to_bn":
            rows = [(a, round(b / 1e3, 1)) for a, b in rows]
        elif tr == "to_thousand":
            rows = [(a, round(b / 1e3, 1)) for a, b in rows]
        e = d["indicators"][k]
        e["readings"] = [r for r in e["readings"] if r.get("source")]  # FRED revises; replace its history wholesale
        for dt, v in rows:
            merge(e, dt, v)
        print(f"  {k:<13} {len(rows):>4} readings to {rows[-1][0] if rows else '—'}: {rows[-1][1] if rows else ''}")
    d["fetched"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    d["fetch_errors"] = errs
    if errs:
        print("  FETCH ERRORS: " + "; ".join(f"{k}: {v}" for k, v in errs.items()))


def at_or_before(rs, date):
    c = [r for r in rs if r["date"] <= date]
    return c[-1] if c else None


def stats(e):
    """latest, changes over 1w/4w/13w, position in the 1-year range, and the weekly streak"""
    rs = e["readings"]
    if not rs:
        return None
    last = rs[-1]
    ld = datetime.date.fromisoformat(last["date"])
    out = {"date": last["date"], "value": last["value"], "source": last.get("source", "FRED " + e["fred"] if e["fred"] else "")}
    for lbl, days in (("w1", 7), ("w4", 28), ("w13", 91), ("y1", 365)):
        p = at_or_before(rs, (ld - datetime.timedelta(days=days)).isoformat())
        # only count it if the earlier reading is genuinely near that horizon
        if p and (ld - datetime.date.fromisoformat(p["date"])).days <= days * 1.6 + 5 and p["date"] != last["date"]:
            out[lbl] = round(last["value"] - p["value"], 3)
    yr = [r["value"] for r in rs if r["date"] >= (ld - datetime.timedelta(days=365)).isoformat()]
    if len(yr) >= 8 and max(yr) > min(yr):
        out["pct"] = round(100 * (last["value"] - min(yr)) / (max(yr) - min(yr)))
        out["lo"], out["hi"] = min(yr), max(yr)
    # weekly streak: consecutive week-on-week moves in the same direction
    pts, cur = [], ld
    for _ in range(27):
        p = at_or_before(rs, cur.isoformat())
        if not p:
            break
        pts.append(p["value"])
        cur -= datetime.timedelta(days=7)
    streak, sign = 0, 0
    for a, b in zip(pts, pts[1:]):
        s = (a > b) - (a < b)
        if s == 0 or (sign and s != sign):
            break
        sign = s
        streak += 1
    if e["cadence"] <= 7 and streak:
        out["streak"] = streak * sign
    return out


def fmt(v, unit=""):
    if v is None:
        return "—"
    s = f"{v:,.2f}" if abs(v) < 1000 else f"{v:,.0f}"
    return s


def sg(v):
    return "—" if v is None else ("+" if v > 0 else "") + fmt(v)


def trend_words(st):
    if not st:
        return "no reading"
    w = []
    if st.get("streak"):
        n = abs(st["streak"])
        w.append(f"{'up' if st['streak'] > 0 else 'down'} {n} week{'s' if n > 1 else ''} running")
    if "pct" in st:
        w.append("at its 1-year high" if st["pct"] >= 98 else "at its 1-year low" if st["pct"] <= 2 else f"{st['pct']}% of its 1-year range")
    return "; ".join(w) or "—"


def table(d, theme=None):
    L = ["| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k, e in d["indicators"].items():
        if theme and e["theme"] != theme:
            continue
        st = stats(e)
        if not st:
            L.append(f"| {k} | {e['name']} | — | — | — | — | — | — | NO READING — read at: {e['read_at'] or 'FRED ' + e['fred']} | |")
            continue
        L.append(f"| {k} | {e['name']} ({e['unit']}) | {fmt(st['value'])} | {st['date']} | {sg(st.get('w1'))} | {sg(st.get('w4'))} | "
                 f"{sg(st.get('w13'))} | {sg(st.get('y1'))} | {trend_words(st)} | {st['source']} |")
    return L


def render(d):
    L = ["# MACRO LEDGER", "",
         "The Macro Desk's memory. Rendered by `tools/macro_ledger.py` from `state/macro-ledger.json` — do not edit by hand.",
         f"Last fetch: {d.get('fetched') or 'never'}.", ""]
    if d["calls"]:
        c = d["calls"][-1]
        L += ["## The Call", "", f"**{c['regime']}** — held since No. {c['since']}, last stated No. {c['issue']} ({c['date']}).", "",
              "What would change it:"] + [f"- {t}" for t in c["triggers"]] + [""]
        if len(d["calls"]) > 1:
            L += ["### Earlier calls", ""] + [f"- No. {x['since']} to No. {x['issue']}: {x['regime']}" for x in d["calls"][:-1][::-1][:12]] + [""]
    for th in ("four", "rates", "liquidity", "credit", "inflation", "growth", "valuation", "flows", "asia"):
        L += [f"## {th.title()}", ""] + table(d, th) + [""]
    VIEW.write_text("\n".join(L) + "\n")


def check(d, issue):
    errs, warns = [], []
    now = today_sg()
    f = d.get("fetched", "")
    age = (datetime.datetime.utcnow() - datetime.datetime.fromisoformat(f.rstrip("Z"))).total_seconds() / 3600 if f else 1e9
    if age > 36:
        errs.append("no `macro_ledger.py fetch` in the last 36 hours — run it before writing the desk")
    for k, e in d["indicators"].items():
        st = stats(e)
        if e["fred"]:
            if k in d.get("fetch_errors", {}):
                warns.append(f"{k}: FRED fetch failed ({d['fetch_errors'][k]}) — do not print it as fresh")
            continue
        limit = e["cadence"] * 2 + 3
        h = d.get("holds", {}).get(k)
        if h and int(issue) - int(h["issue"]) <= 2 and (not st or (now - datetime.date.fromisoformat(st["date"])).days > limit):
            warns.append(f"{k} held at No. {h['issue']}: {h['reason']} — do not print it; it must be read within three issues")
            continue
        if not st:
            errs.append(f"{k} ({e['name']}) has never been read — read it at {e['read_at']} and `record` it")
        elif (now - datetime.date.fromisoformat(st["date"])).days > limit:
            errs.append(f"{k} ({e['name']}) is stale: as of {st['date']}, older than {limit} days — re-read it at {e['read_at']}")
    c = d["calls"][-1] if d["calls"] else None
    if not c or int(c["issue"]) != int(issue):
        errs.append(f"no regime call on record for No. {issue} — `macro_ledger.py call {issue} \"<regime>\" \"<trigger>\" \"<trigger>\"`")
    elif len(c["triggers"]) < 2:
        errs.append("the regime call needs at least two stated conditions that would change it")
    return errs, warns


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    d = load()
    if a[0] == "fetch":
        fetch(d)
        save(d)
        print(f"wrote {STATE} and {VIEW}")
    elif a[0] == "record" and len(a) >= 3:
        k = a[1]
        if k not in INDICATORS:
            sys.exit(f"unknown indicator {k}; known: {', '.join(INDICATORS)}")
        if INDICATORS[k][4]:
            sys.exit(f"{k} is FRED-backed — it is fetched, never typed")
        if "--asof" not in a or "--source" not in a:
            sys.exit("record needs --asof YYYY-MM-DD and --source \"<where it was read>\"")
        asof = a[a.index("--asof") + 1]
        datetime.date.fromisoformat(asof)
        src = a[a.index("--source") + 1]
        if len(src) < 6:
            sys.exit("--source must name where the figure was read")
        iss = int(a[a.index("--issue") + 1]) if "--issue" in a else None
        merge(d["indicators"][k], asof, float(a[2].replace(",", "")), src, iss)
        save(d)
        print(f"recorded {k} = {a[2]} as of {asof}")
    elif a[0] == "show":
        th = a[a.index("--theme") + 1] if "--theme" in a else None
        print("\n".join(table(d, th)))
        if d["calls"]:
            c = d["calls"][-1]
            print(f"\nTHE CALL: {c['regime']} — held since No. {c['since']} (last stated No. {c['issue']})")
            for t in c["triggers"]:
                print(f"  would change it: {t}")
    elif a[0] == "call" and len(a) >= 3:
        issue, regime, trig = int(a[1]), a[2].strip(), [t.strip() for t in a[3:] if not t.startswith("--")]
        if len(trig) < 2:
            sys.exit("a call needs at least two conditions that would change it, each with a level or a date")
        prev = d["calls"][-1] if d["calls"] else None
        if prev and int(prev["issue"]) == issue:
            d["calls"].pop()
            prev = d["calls"][-1] if d["calls"] else None
        since = prev["since"] if prev and prev["regime"].lower() == regime.lower() else issue
        if prev and prev["regime"].lower() == regime.lower():
            d["calls"].pop()
        d["calls"].append({"issue": issue, "date": today_sg().isoformat(), "regime": regime, "since": since, "triggers": trig})
        save(d)
        print(f"call recorded: {regime} — held since No. {since}")
    elif a[0] == "check" and len(a) >= 2:
        errs, warns = check(d, a[1])
        for w in warns:
            print("WARN  " + w)
        if errs:
            print("MACRO LEDGER: FAILED")
            for e in errs:
                print("  " + e)
            sys.exit(1)
        print(f"MACRO LEDGER: ok — {sum(1 for e in d['indicators'].values() if e['readings'])} indicators with readings, call on record")
    elif a[0] == "hold" and len(a) >= 4:
        if a[1] not in INDICATORS or INDICATORS[a[1]][4]:
            sys.exit("hold applies to manual indicators only")
        if len(a[3]) < 15:
            sys.exit("say why it could not be read at source (which host refused, what was tried)")
        d.setdefault("holds", {})[a[1]] = {"issue": int(a[2]), "reason": a[3]}
        save(d)
        print(f"held {a[1]} at No. {a[2]} — add it to the Held Ledger; it must be read within three issues")
    elif a[0] == "theme":
        dt = datetime.date.fromisoformat(a[1]) if len(a) > 1 else today_sg()
        key, word, desc = THEMES[dt.weekday()]
        print(f"{dt.strftime('%A')}: The Trend · {word} — {desc}\nledger theme: {key}")
    elif a[0] == "render":
        render(d)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
