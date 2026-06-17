# Titan Company Ltd (NSE: TITAN) — AI Decision Intelligence Case Study

A self-directed equity research project that treats valuation as a **decision under uncertainty** — taking one recommendation and pressure-testing it from four independent analytical angles rather than trusting a single model.

> **Educational project. Not investment advice.**
> Working standard throughout: correctness over speed. No fabricated numbers — every figure is verified against source filings and cross-checked with an independent Python recompute.

---

## Bottom Line

**Recommendation: HOLD.** A superb business priced for perfection.

| Metric | Value |
|---|---|
| DCF fair value | **₹1,017 / share** |
| Market price (CMP) | ~₹4,363 |
| Implied downside | ~77% |
| WACC | 12.2% (Rf 7.0%, ERP 6.5%, β 0.85) |
| Monte Carlo median | ₹1,005 (80% CI: ₹718–₹1,387) |
| P(fair value < CMP) | 100% |

The conclusion was reached by analysis — never reverse-engineered to the market price. A reverse-DCF shows the current price implies **~11.3% perpetual FCFF growth**, against ~5.5% nominal GDP.

---

## One Thesis, Four Independent Angles

**1. DCF Valuation**
A fully integrated 3-statement model (FY21–FY34, reanchored to FY25 audited actuals, balancing every year with real linkage — no plug). Two-stage 10-year DCF; jewellery modelled on a standalone ex-bullion basis that reconciles 0.00% to Titan's published filings; full Ind-AS 116 lease treatment.

**2. Monte Carlo Simulation (10,000 trials)**
Quantifies the uncertainty around the point estimate. Median fair value ₹1,005; 80% CI ₹718–₹1,387; P(fair value < CMP) = 100%. Sensitivity analysis isolates **EBITDA margin (r = +0.61)** and **WACC (r = −0.56)** as the dominant value drivers.

**3. LLM Management Sentiment**
Six real, SEBI-filed earnings-call transcripts (FY25Q3 → FY26Q4) scored via Groq/LLaMA into a Management Confidence Index. A deliberately **bounded** overlay moves fair value only ₹1,013 → ₹1,018 — proving by construction that sentiment cannot rescue the thesis.

**4. Alternative Data (Google Trends)**
Tested whether "Tanishq" search traffic leads jewellery revenue. Raw levels looked predictive (lag+1 r = 0.60), but after detrending (removing shared trend + Diwali seasonality) the signal is **coincident, not leading** (lag+1 r = −0.10, not significant). The null result is reported honestly.

---

## Repository Structure

    excel/      3-statement model + DCF, incl. interactive Dashboard tab
    python/     Monte Carlo, Groq LLM sentiment scoring, Google Trends analysis
    outputs/    simulation outputs, charts, and summary data
    memo/       investment memo + investor one-pager (PDF)
    README.md

---

## Tech Stack

Python (NumPy, SciPy, Matplotlib) · Monte Carlo Simulation · Groq LLM API · pytrends · React + Vite + Recharts · Advanced Excel (openpyxl) · Git/GitHub

---

## Running It

Dashboard:

​```
cd excel
npm install
npm run dev
​```

Simulations & analysis (Python 3.12):

​```
pip install numpy scipy matplotlib pandas pytrends groq openpyxl
​```

---

## A Note on Method

Two decisions in this project matter more than any single output:

- The LLM sentiment overlay was **bounded on purpose** — to demonstrate that a model output shouldn't count just because it exists. Knowing when to distrust your own pipeline is the point.
- The Google Trends signal was tested and **reported as null**. Forcing a positive finding would have been easy and dishonest. It isn't here.

---

*Author: Shivang Koul · Built for finance / strategy-consulting applications · Educational use only, not investment advice.*
