# MACRO LEDGER

The Macro Desk's memory. Rendered by `tools/macro_ledger.py` from `state/macro-ledger.json` — do not edit by hand.
Last fetch: 2026-11-17T02:26:34Z.

## Rates

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| us2y | US 2-year Treasury yield (%) | 4.88 | 2026-11-13 | +0.37 | +0.14 | +0.71 | +1.30 | up 1 week running; 97% of its 1-year range | FRED DGS2 |
| us10y | US 10-year Treasury yield (%) | 5.15 | 2026-11-13 | +0.29 | +0.06 | +0.47 | +1.04 | up 1 week running; 88% of its 1-year range | FRED DGS10 |
| real10y | US 10-year real yield (TIPS) (%) | 2.91 | 2026-11-13 | +0.28 | +0.17 | +0.50 | +1.08 | up 2 weeks running; 97% of its 1-year range | FRED DFII10 |
| breakeven10 | US 10-year breakeven inflation (%) | 2.20 | 2026-11-16 | -0.02 | -0.15 | -0.08 | -0.08 | down 4 weeks running; 6% of its 1-year range | FRED T10YIE |
| curve2s10s | US 10-year minus 2-year (pp) | 0.29 | 2026-11-16 | -0.03 | -0.09 | -0.24 | -0.23 | down 1 week running; 17% of its 1-year range | FRED T10Y2Y |
| termprem10 | US 10-year term premium (Kim-Wright) (pp) | 0.87 | 2026-11-06 | -0.04 | -0.20 | +0.05 | +0.38 | down 5 weeks running; 66% of its 1-year range | FRED THREEFYTP10 |

## Liquidity

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| fed_bs | Federal Reserve balance sheet (US$tn) | 6.76 | 2026-11-11 | +0.01 | +0.00 | -0.00 | +0.19 | up 2 weeks running; at its 1-year high | FRED WALCL |
| rrp | Fed overnight reverse repo (US$bn) | 0.18 | 2026-11-16 | -0.07 | -0.15 | -0.07 | -1.38 | down 2 weeks running; at its 1-year low | FRED RRPONTSYD |
| tga | US Treasury General Account (US$bn) | 914.40 | 2026-11-11 | -42.80 | +31.00 | -49.60 | -26.60 | down 2 weeks running; 64% of its 1-year range | FRED WTREGEN |
| sofr | Secured Overnight Financing Rate (%) | 3.90 | 2026-11-13 | +0.01 | +0.02 | +0.28 | -0.10 | up 1 week running; 65% of its 1-year range | FRED SOFR |
| nfci | Chicago Fed financial conditions (above 0 = tight) (index) | -0.46 | 2026-11-06 | +0.00 | +0.03 | +0.08 | +0.05 | up 11 weeks running; at its 1-year high | FRED NFCI |
| dollar | Broad trade-weighted US dollar (index) | 122.65 | 2026-11-13 | +0.77 | +1.25 | +3.75 | +1.88 | up 3 weeks running; at its 1-year high | FRED DTWEXBGS |

## Credit

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| hy_oas | US high-yield credit spread (pp) | 3.23 | 2026-11-13 | -0.19 | -0.08 | +0.56 | +0.14 | down 2 weeks running; 72% of its 1-year range | FRED BAMLH0A0HYM2 |
| ig_oas | US investment-grade credit spread (pp) | 0.89 | 2026-11-13 | -0.04 | +0.04 | +0.09 | +0.05 | down 2 weeks running; 76% of its 1-year range | FRED BAMLC0A0CM |
| vix | VIX equity volatility (index) | 19.30 | 2026-11-13 | -6.34 | -0.69 | +5.05 | -0.70 | down 1 week running; 33% of its 1-year range | FRED VIXCLS |

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
| gdpnow | Atlanta Fed GDPNow, current quarter (% saar) | 3.48 | 2026-10-01 | — | — | +0.21 | -0.76 | up 1 week running | FRED GDPNOW |
| eps_growth | S&P 500 blended earnings growth, current quarter | — | — | — | — | — | — | NO READING — read at: FactSet Earnings Insight (weekly PDF) | |
| fwd_eps | S&P 500 forward 12-month earnings per share | — | — | — | — | — | — | NO READING — read at: FactSet Earnings Insight (weekly PDF) | |

## Valuation

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| fwd_pe | S&P 500 forward price/earnings | — | — | — | — | — | — | NO READING — read at: FactSet Earnings Insight | |
| cape | Shiller cyclically adjusted P/E | — | — | — | — | — | — | NO READING — read at: Shiller data / multpl.com | |
| vwra_us | All-world index: United States weight | — | — | — | — | — | — | NO READING — read at: Vanguard VWRA factsheet or FTSE All-World factsheet | |
| vwra_top10 | All-world index: top-ten holdings weight | — | — | — | — | — | — | NO READING — read at: Vanguard VWRA factsheet or FTSE All-World factsheet | |

## Flows

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| cftc_ust10 | Speculative net position, 10-year Treasury futures | — | — | — | — | — | — | NO READING — read at: CFTC Commitments of Traders (weekly) | |
| equity_flows | US equity fund and ETF flows, latest week | — | — | — | — | — | — | NO READING — read at: Investment Company Institute weekly flows | |
| bond_flows | US bond fund and ETF flows, latest week | — | — | — | — | — | — | NO READING — read at: Investment Company Institute weekly flows | |
| cb_gold | Central-bank net gold purchases, latest month | — | — | — | — | — | — | NO READING — read at: World Gold Council monthly central-bank statistics | |
| btc_etf_flows | US spot bitcoin ETF net flows, latest week | — | — | — | — | — | — | NO READING — read at: Farside Investors or issuer filings | |

## Asia

| Key | Indicator | Latest | As of | 1 week | 4 weeks | 13 weeks | 1 year | Trend | Source |
|---|---|---|---|---|---|---|---|---|---|
| usdjpy | US dollar / Japanese yen (yen) | 159.93 | 2026-11-13 | +1.70 | +1.93 | +0.72 | +5.53 | up 3 weeks running; 65% of its 1-year range | FRED DEXJPUS |
| usdcny | US dollar / Chinese yuan (yuan) | 6.67 | 2026-11-13 | -0.01 | -0.01 | -0.07 | -0.42 | down 1 week running; 5% of its 1-year range | FRED DEXCHUS |
| jgb10 | Japan 10-year government bond yield | — | — | — | — | — | — | NO READING — read at: Japan Ministry of Finance JGB yield table | |
| china_tsf | China total social financing, year on year | — | — | — | — | — | — | NO READING — read at: People's Bank of China monthly financial statistics | |

