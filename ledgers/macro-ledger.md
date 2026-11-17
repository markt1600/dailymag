# MACRO LEDGER

The Macro Desk's memory. Rendered by `tools/macro_ledger.py` from `state/macro-ledger.json` — do not edit by hand.
Last fetch: 2026-11-17T21:07:32Z.

## The Call

**A real-rate shock: the Federal Reserve tightening into an energy supply shock** — held since No. 162, last stated No. 166 (2026-11-18).

What would change it:
- The 10-year real yield closes below 2.60 per cent (2.91 on 13 November, up from 1.75 in September 2025)
- The Federal Reserve does not raise rates on 9 December
- The high-yield credit spread closes above 4.0 points (3.34 on 16 November), which would make it a growth scare rather than a rate shock

## Rates

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| us2y | US 2-year Treasury yield (%) | 4.88 | 2026-11-13 | +0.37 | +0.14 | +0.71 | +1.30 | up 1 week running; 97% of its 1-year range | FRED DGS2 |
| us10y | US 10-year Treasury yield (%) | 5.15 | 2026-11-13 | +0.29 | +0.06 | +0.47 | +1.04 | up 1 week running; 88% of its 1-year range | FRED DGS10 |
| real10y | US 10-year real yield (TIPS) (%) | 2.91 | 2026-11-13 | +0.28 | +0.17 | +0.50 | +1.08 | up 2 weeks running; 97% of its 1-year range | FRED DFII10 |
| breakeven10 | US 10-year breakeven inflation (%) | 2.20 | 2026-11-16 | -0.02 | -0.15 | -0.08 | -0.08 | down 4 weeks running; 6% of its 1-year range | FRED T10YIE |
| curve2s10s | US 10-year minus 2-year (pp) | 0.29 | 2026-11-16 | -0.03 | -0.09 | -0.24 | -0.23 | down 1 week running; 17% of its 1-year range | FRED T10Y2Y |
| termprem10 | US 10-year term premium (Kim-Wright) (pp) | 0.99 | 2026-11-13 | +0.11 | +0.00 | +0.15 | +0.49 | up 1 week running; 83% of its 1-year range | FRED THREEFYTP10 |

## Liquidity

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| fed_bs | Federal Reserve balance sheet (US$tn) | 6.76 | 2026-11-11 | +0.01 | +0.00 | -0.00 | +0.19 | up 2 weeks running; at its 1-year high | FRED WALCL |
| rrp | Fed overnight reverse repo (US$bn) | 0.35 | 2026-11-17 | +0.20 | +0.12 | +0.20 | -2.82 | up 1 week running; at its 1-year low | FRED RRPONTSYD |
| tga | US Treasury General Account (US$bn) | 914.40 | 2026-11-11 | -42.80 | +31.00 | -49.60 | -26.60 | down 2 weeks running; 64% of its 1-year range | FRED WTREGEN |
| sofr | Secured Overnight Financing Rate (%) | 3.93 | 2026-11-16 | +0.05 | +0.06 | +0.27 | -0.02 | up 1 week running; 69% of its 1-year range | FRED SOFR |
| nfci | Chicago Fed financial conditions (above 0 = tight) (index) | -0.46 | 2026-11-06 | +0.00 | +0.03 | +0.08 | +0.05 | up 11 weeks running; at its 1-year high | FRED NFCI |
| dollar | Broad trade-weighted US dollar (index) | 122.65 | 2026-11-13 | +0.77 | +1.25 | +3.75 | +1.88 | up 3 weeks running; at its 1-year high | FRED DTWEXBGS |

## Credit

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| hy_oas | US high-yield credit spread (pp) | 3.34 | 2026-11-16 | 0.00 | +0.05 | +0.64 | +0.27 | 84% of its 1-year range | FRED BAMLH0A0HYM2 |
| ig_oas | US investment-grade credit spread (pp) | 0.90 | 2026-11-16 | -0.01 | +0.03 | +0.09 | +0.07 | down 2 weeks running; 81% of its 1-year range | FRED BAMLC0A0CM |
| vix | VIX equity volatility (index) | 22.91 | 2026-11-16 | +2.99 | +4.47 | +7.72 | +3.08 | up 1 week running; 54% of its 1-year range | FRED VIXCLS |

## Inflation

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| cpi_yoy | US consumer prices, year on year (%) | 3.72 | 2026-09-01 | — | +0.37 | +0.26 | +0.70 | 75% of its 1-year range | FRED CPIAUCSL |
| core_cpi_yoy | US core consumer prices, year on year (%) | 2.57 | 2026-09-01 | — | +0.12 | 0.00 | -0.45 | 21% of its 1-year range | FRED CPILFESL |
| unemp | US unemployment rate (%) | 4.10 | 2026-10-01 | — | -0.10 | 0.00 | -0.30 | at its 1-year low | FRED UNRATE |
| claims | US initial jobless claims (thousand) | 200.00 | 2026-11-07 | +9.00 | 0.00 | -12.00 | -28.00 | up 1 week running; 24% of its 1-year range | FRED ICSA |
| brent | Brent crude, spot (US$) | 92.14 | 2026-11-11 | +0.30 | -34.41 | -0.38 | +28.28 | up 1 week running; 41% of its 1-year range | FRED DCOILBRENTEU |

## Growth

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| gdpnow | Atlanta Fed GDPNow, current quarter (% saar) | 3.38 | 2026-10-01 | — | — | +0.11 | -0.85 | up 1 week running | FRED GDPNOW |
| eps_growth | S&P 500 blended earnings growth, current quarter (%) | 31.90 | 2026-11-13 | +0.50 | +2.80 | — | — | up 3 weeks running | FactSet Earnings Insight, John Butters, 16 Nov 2026 |
| fwd_eps | S&P 500 forward 12-month earnings per share (US$) | 415.82 | 2026-11-05 | — | — | — | — | — | FactSet Earnings Insight, John Butters, 9 Nov 2026 (forward 12-month EPS) |

## Valuation

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| fwd_pe | S&P 500 forward price/earnings (x) | 17.70 | 2026-11-05 | — | -1.30 | — | — | down 1 week running | FactSet Earnings Insight, John Butters, 9 Nov 2026 |
| cape | Shiller cyclically adjusted P/E (x) | 39.16 | 2026-11-16 | — | — | — | — | — | multpl.com Shiller PE, 16 Nov close |
| vwra_us | All-world index: United States weight (%) | 62.83 | 2026-10-31 | — | — | — | — | — | Vanguard FTSE All-World UCITS ETF product page, portfolio data 31 Oct 2026 |
| vwra_top10 | All-world index: top-ten holdings weight (%) | 23.54 | 2026-10-31 | — | — | — | — | — | Vanguard FTSE All-World UCITS ETF product page, top ten holdings 31 Oct 2026 |

## Flows

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| cftc_ust10 | Speculative net position, 10-year Treasury futures (thousand contracts) | -2,301 | 2026-11-10 | -39.00 | — | — | — | down 1 week running | CFTC Traders in Financial Futures, leveraged funds net (586,834 long, 2,888,161 short), UST 10Y note |
| equity_flows | US equity fund and ETF flows, latest week (US$bn) | 17.43 | 2026-11-04 | +6.35 | +28.55 | — | — | up 1 week running | ICI estimated long-term mutual fund and ETF combined flows, released 11 Nov 2026 |
| bond_flows | US bond fund and ETF flows, latest week (US$bn) | 2.36 | 2026-11-04 | -0.80 | -22.20 | — | — | down 1 week running | ICI estimated long-term mutual fund and ETF combined flows, released 11 Nov 2026 |
| cb_gold | Central-bank net gold purchases, latest month (tonnes) | 61.00 | 2026-09-30 | — | — | — | — | — | World Gold Council, Central Bank Gold Statistics: September 2026, 4 Nov 2026 |
| btc_etf_flows | US spot bitcoin ETF net flows, latest week (US$bn) | -1.28 | 2026-11-06 | -1.08 | — | — | — | down 1 week running | The Block, 7 Nov 2026, SoSoValue data (week of 2 to 6 Nov) |

## Asia

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| usdjpy | US dollar / Japanese yen (yen) | 159.93 | 2026-11-13 | +1.70 | +1.93 | +0.72 | +5.53 | up 3 weeks running; 65% of its 1-year range | FRED DEXJPUS |
| usdcny | US dollar / Chinese yuan (yuan) | 6.67 | 2026-11-13 | -0.01 | -0.01 | -0.07 | -0.42 | down 1 week running; 5% of its 1-year range | FRED DEXCHUS |
| jgb10 | Japan 10-year government bond yield (%) | 2.93 | 2026-11-16 | +0.23 | -0.03 | +0.05 | +1.21 | up 1 week running; 87% of its 1-year range | Japan Ministry of Finance JGB yield table (jgbcme) |
| china_tsf | China total social financing, year on year (%) | 7.10 | 2026-09-30 | — | — | — | — | — | People's Bank of China preliminary statistics via Shanghai Metals Market, 14 Oct 2026 |

