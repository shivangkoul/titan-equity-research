# Titan Phase 6 — Interactive Equity-Research Dashboard

Single-page React dashboard tying together the four analytical layers of the
Titan (NSE: TITAN) research project, on a dark/cosmic theme matching the charts.

## Panels
- **Valuation · DCF** — fair value, EV, TV%, and an interactive **reverse-DCF**
  slider (drag terminal growth → implied fair value; the market implies ~11.3%).
- **Monte Carlo** — median/P10/P90 distribution strip, a **percentile scrubber**
  (P(FV < x)), and the 8-driver sensitivity tornado. P(FV < CMP) = 100%.
- **Management sentiment** — MCI trend across 5 real concalls, the latest
  quarter's 5-dimension scores, and a **bounded overlay slider** (±1.5pp).
- **Google Trends** — lead-lag correlations of "Tanishq" search vs jewellery
  revenue, levels vs detrended. Honest verdict: coincident, not leading.

## Data
Bound to the saved pipeline outputs (also copied into `src/data/` for provenance):
`montecarlo_summary_v3.json`, `phase5_correlation_results.json`,
`sentiment_results.json`. Values are mirrored in `src/data.js` so the component
runs both as this Vite app and as the single-file `Titan_Phase6_Dashboard.jsx`.

## Run / deploy
```bash
npm install
npm run dev        # local
npm run build      # -> dist/  (deploy to Vercel: framework = Vite)
```

Conclusion is **HOLD** by analysis — never reverse-engineered to market price.
Shivang Koul · independent research.
