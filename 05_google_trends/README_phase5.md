# Phase 5 — Google Trends Alternative Data Layer
## Titan Company Ltd (NSE: TITAN) | Independent Equity Research

---

## What this does and why it matters

This module adds a **real-time alternative-data layer** to the Titan equity research project by testing whether Google search interest for "Tanishq" is a *leading indicator* of Titan's jewellery segment revenue.

**The hypothesis:** Consumers search for jewellery *before* they purchase it — particularly ahead of Diwali and wedding season. If search volume in quarter Q predicts revenue in Q+1, that is a genuine leading indicator with practical use:
- Validates Q3 (Oct–Dec) seasonality assumption embedded in the 3-statement model
- Provides an independent, real-time signal corroborating the Q3/Q4 growth forecasts
- Adds data-science differentiation that is rare in standard student equity research

**The honest version:** We quantify the relationship and report it exactly as found — no overclaiming. A high contemporaneous correlation (lag 0) means people search *while* shopping. A significant lag +1 correlation would be a genuinely novel finding. If the signal is weak, we say so.

---

## Files

```
05_google_trends/
├── phase5_trends.py            ← Main script (this is the one to run)
├── titan_quarterly_rev.csv     ← Revenue template (auto-generated; fill with BSE actuals)
├── README_phase5.md
└── outputs/
    ├── titan_phase5_trends_tanishq_sample.png      ← Chart (synthetic, pipeline test)
    ├── titan_phase5_trends_tanishq_live.png         ← Chart (after --live run)
    └── phase5_correlation_results.json              ← For Phase 6 dashboard
```

---

## How to run

### Step 1 — Pipeline verification (safe in any environment)
```powershell
cd "path\to\05_google_trends"
python phase5_trends.py
```
Uses synthetic data. Verifies the full pipeline: aggregation → correlation → chart. No external API calls. Run this first.

### Step 2 — Live data (on your local Windows machine only)
```powershell
python phase5_trends.py --live --save-raw
```
- `--live` : calls Google Trends via pytrends
- `--save-raw` : saves the raw weekly CSV to `outputs/tanishq_trends_raw.csv` so you don't need to re-fetch

**Important:** Google Trends blocks datacenter/server IPs. You must run this on your local machine (home Wi-Fi or hotspot), not in any cloud/sandbox environment. This is the same pattern as the Groq sentiment script in Phase 4.

### Step 3 — Titan watches keyword
```powershell
python phase5_trends.py --live --save-raw --keyword "Titan watches"
```
Produces a separate chart for the watches segment as a supplementary signal.

---

## Getting real quarterly revenue data

The script uses synthetic quarterly splits on first run (written to `titan_quarterly_rev.csv`). Replace with actuals before publishing.

**Where to get it:**
1. **BSE India** → [www.bseindia.com/corporates/ann.html](https://www.bseindia.com/corporates/ann.html) → search Titan (500114) → Quarterly Results
2. **Titan Investor Relations** → [www.titancompany.in/investors](https://www.titancompany.in/investors) → Quarterly/Annual Reports → Segment Revenue
3. **Screener.in** → Titan → Quarterly tab → Jewellery segment (ex-bullion)
4. **NSE** → [nseindia.com](https://www.nseindia.com) → Company → Financial Results → Segment

**CSV format** (edit `titan_quarterly_rev.csv` directly):
```csv
quarter,jewellery_rev_cr,is_synthetic
FY21-Q1,<actual>,False
FY21-Q2,<actual>,False
...
```
Column `jewellery_rev_cr`: jewellery segment revenue, ₹ Cr, **ex-bullion**, from auditor-reviewed quarterly results.

---

## Interpreting the correlation output

The script runs **two correlation analyses** at lags –1, 0, +1, +2, +3:

| Analysis | What it tests |
|----------|---------------|
| **Levels** | Pearson r on raw quarterly series | 
| **Detrended (QoQ growth)** | Pearson r on quarter-on-quarter % changes |

**Why two?**  
Levels correlation can be inflated by the shared secular growth trend (both series trend upward because Titan is a growing business — nothing to do with search causing revenue). Detrended correlation removes this and isolates the *cyclical* signal. If the detrended correlation at lag +1 is still significant, that's a genuinely robust finding.

**Reading the output:**
```
Lag    Interpretation              r       p       Sig    N
────────────────────────────────────────────────────────────
 –1Q   Revenue leads Trends        0.xxx   0.xxxx  **    19   
  0    Contemporaneous             0.xxx   0.xxxx  ***   20  ← usually highest
 +1Q   Trends leads Revenue 1Q     0.xxx   0.xxxx  *     19  ← what we want
 +2Q   Trends leads Revenue 2Q     0.xxx   0.xxxx  ns    18
 +3Q   Trends leads Revenue 3Q     0.xxx   0.xxxx  ns    17
```

Significance codes: `***` p<0.01 | `**` p<0.05 | `*` p<0.10 | `ns` not significant

**Decision rule for the research report:**

| r at best lead lag | What to say |
|--------------------|-------------|
| ≥ 0.60, p < 0.05   | "Google search interest is a statistically significant leading indicator of Titan's jewellery revenue, leading by X quarters (r = X, p = X)." |
| 0.40–0.59 or p < 0.10 | "Moderate positive relationship; useful as a supplementary confirmation signal, not a standalone indicator." |
| < 0.40 or p > 0.10 | "Contemporaneous correlation is strong (lag 0), confirming the Q3 seasonality pattern, but predictive power at lead lags is weak. Trends data serves as a real-time seasonality confirmation rather than a leading indicator." |

---

## Limitations (to include in the research)

State these honestly — they strengthen, not weaken, the analysis by showing rigor:

1. **Small N:** ~20 quarterly data points → low statistical power; p-values should be interpreted with caution, especially at longer lags (N drops to 17 at lag +3)

2. **Relative not absolute:** Google Trends indexes to 100 at the peak of the selected window, not absolute search volume — cross-period comparability is imperfect

3. **Concurrent search bias:** A large share of Tanishq searches may happen during (not before) purchase, suppressing the leading-indicator signal

4. **Secular trend contamination in levels:** Use the detrended analysis as the primary result for rigour; levels as supporting context

5. **COVID distortion:** FY21 Q1/Q2 data is severely distorted (lockdowns → near-zero in-store footfall, but search may have been normal or elevated from boredom). Consider a robustness check excluding FY21

6. **Not a trading signal:** A lag +1 correlation of even 0.65 is not sufficient to trade on — it is an *investor-awareness* tool that flags seasonality confirmation

---

## What to write in the research report

Suggested framing in the Research section (1 paragraph):

> "As a supplementary alternative-data validation, we analysed the relationship between Google search interest for 'Tanishq' (pytrends, India) and Titan's quarterly jewellery segment revenue over FY21–FY25 (n=20 quarters). Contemporaneous Pearson r [at lag 0] was **r = [X], p = [X]**, confirming that consumer search activity closely tracks the well-known Q3 (Diwali/Dhanteras) revenue seasonality. At lag +1 quarter, [Trends leads Revenue / the predictive relationship was weak] (detrended r = [X], p = [X]), suggesting [Google Trends provides a one-quarter early read on demand momentum / the signal is contemporaneous rather than leading]. This is consistent with Titan's own commentary that festive-season demand crystallises within the quarter rather than building measurably ahead of it. We treat Trends as a real-time seasonality confirmation tool rather than a quantitative leading indicator."

---

## Technical notes

- `pytrends` returns weekly data for timeframes ≤ 2 years; monthly for longer. The script fetches in 2-year chunks (FY21–22, FY23–24, FY25) to preserve weekly granularity, then re-normalises across the full period so all chunks share the same scale anchor.
- Detrending uses QoQ % change (`pct_change()`), not HP-filter. HP-filter requires `statsmodels` and the lambda parameter choice is subjective; first-differencing is simpler and transparent.
- Results are saved to `outputs/phase5_correlation_results.json` for direct ingestion by the Phase 6 dashboard.

---

## Dependencies

```
numpy >= 1.24
pandas >= 1.5
scipy >= 1.10
matplotlib >= 3.7
pytrends >= 4.9    ← only needed for --live mode
```

Install: `pip install pytrends pandas numpy scipy matplotlib`
