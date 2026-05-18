# Titan Company Ltd. — Independent Equity Research & DCF Valuation

> A ground-up equity research project on **NSE: TITAN**, built to replicate the workflow of a buy-side analyst — from raw financial statements to a final investment memo.

---

## Project Structure

This project runs across four phases:

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Financial Statement Fundamentals | ✅ Complete |
| 2 | 3-Statement Excel Model (historical + projections) | 🔄 In Progress |
| 3 | DCF Valuation, Monte Carlo Simulation & Scenario Analysis | ⏳ Upcoming |
| 4 | Differentiator Layer + Investment Memo | ⏳ Upcoming |

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

## Data Sources

| Source | Usage |
|--------|-------|
| BSE Filings / Titan Press Releases | Primary financial data |
| Screener.in | Consolidated historical view |
| Groq API | LLM inference for sentiment scoring |
| pytrends | Google Trends data |

---

## Key Findings *(updated as project progresses)*

- FY24 standalone revenue ex-bullion: ~₹47,501 Cr
- FY24 PAT: ₹3,496 Cr
- *Valuation range and investment thesis to be added upon Phase 3 completion*

---

## Tech Stack

`Python` · `Excel` · `Power BI` · `Groq LLM API` · `pytrends` · `React/Vercel`

---

## About

Built by **Shivang Koul**, B.Com (Hons), Hansraj College, University of Delhi.

This project is an independent initiative — not affiliated with any institution or employer. All data is sourced from public filings. This is not investment advice.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/shivangkoul)
