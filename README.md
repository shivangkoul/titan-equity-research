# Titan Company Ltd. — Independent Equity Research & DCF Valuation

> A ground-up equity research project on **NSE: TITAN**, built to replicate the workflow of a buy-side analyst — from raw financial statements to a final investment memo.

---

## Project Structure

This project runs across four phases:

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Financial Statement Fundamentals | ✅ Complete |
| 2 | 3-Statement Excel Model (historical + projections) | ✅ Complete |
| 3 | DCF Valuation, Monte Carlo Simulation & Scenario Analysis | ✅ Complete |
| 4 | Differentiator Layer + Investment Memo | ✅ Complete |

---

## What's Inside

### 📊 Excel Model
- Consolidated Income Statement, Balance Sheet, and Cash Flow Statement
- Historical data sourced from **BSE filings** and **Screener.in**
- Careful handling of Titan's bullion revenue reclassification (material impact on reported top-line)
- Assumptions tab with documented drivers for revenue growth, margins, capex, and working capital

### 🐍 Python (Monte Carlo DCF)
- Probabilistic valuation using Monte Carlo simulation
- Key inputs modelled as distributions (WACC, terminal growth rate, revenue CAGR)
- Output: intrinsic value range with confidence intervals

### 🤖 LLM-Powered Sentiment Analysis
- Earnings call transcripts scored for management tone using the **Groq API**
- Tracks sentiment trends across quarters as a qualitative overlay to the model

### 📈 Google Trends Correlation
- Consumer demand proxy using **pytrends**
- Correlates search interest in Titan / Tanishq with revenue seasonality

### 📊 Interactive Dashboard
- **Power BI** dashboard for financial KPIs and valuation outputs
- Built for non-technical audiences; designed to accompany the investment memo

---

## Repository Structure

| Folder | Contents |
|---|---|
| `excel/` | 3-statement financial model with historical data and projections |
| `python/` | Monte Carlo DCF simulation script and JSON summary output |
| `outputs/` | Simulation chart (distribution + tornado) |
| `memo/` | Sell-side format investment memo |

## Data Sources

| Source | Usage |
|--------|-------|
| BSE Filings / Titan Press Releases | Primary financial data |
| Screener.in | Consolidated historical view |
| Groq API | LLM inference for sentiment scoring |
| pytrends | Google Trends data |

---

## Key Findings

| Metric | Value |
|---|---|
| FY24 Revenue (Consolidated) | ₹51,617 Cr |
| FY24 EBITDA Margin | 11.3% (compressed from 12.7% in FY23) |
| FY24 Free Cash Flow | ₹1,004 Cr |
| Base-case DCF implied price | ₹558 / share |
| Monte Carlo median (P50) | ₹1,206 / share |
| Monte Carlo 90% CI | ₹766 – ₹1,992 |
| CMP at time of analysis | ₹4,450 |
| Rating | HOLD — accumulate below ₹3,800 |
| Primary value driver | Revenue CAGR (Pearson r = +0.72) |
| Primary risk factor | WACC sensitivity (r = −0.55) |

**Interpretation:** The gap between ₹824 (DCF median) and ₹4,450 (CMP) reflects
franchise optionality — Tanishq's long-run market share journey in a ₹6L Cr
jewellery market with only 7% organised penetration, which a 5-year DCF
cannot adequately price. Reverse DCF implies the market expects ~22% FCF
CAGR over 10 years, consistent with Titan's historical trajectory.

---

## Tech Stack

`Python` · `Excel` · `Power BI` · `Groq LLM API` · `pytrends` · `React/Vercel`

---

## About

Built by **Shivang Koul**, B.Com (Hons), Hansraj College, University of Delhi.

This project is an independent initiative — not affiliated with any institution or employer. All data is sourced from public filings. This is not investment advice.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/shivangkoul)
