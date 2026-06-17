// Phase 6 dashboard data — bound to the saved Phase 1-5 outputs.
// Raw provenance JSON lives in ./data/  (montecarlo_summary_v3.json,
// phase5_correlation_results.json, sentiment_results.json). Values transcribed
// here so the component renders both as a Vite app and as a single-file preview.

export const dcf = {
  cmp: 4363, fairValue: 1017, ev: 101522, equity: 90299,
  tvPct: 0.654, wacc: 0.122, impliedG: 0.1133, gdp: 0.055,
  netDebt: 11223, shares: 88.8,
};

export const mc = {
  nValid: 10000, median: 1005, mean: 1034,
  p10: 718, p25: 849, p75: 1185, p90: 1387,
  pBelowCmp: 1.0, central: "₹1,013 (sim) vs ₹1,017 (deterministic)",
  drivers: [
    { name: "EBITDA margin", r: 0.607 }, { name: "WACC", r: -0.557 },
    { name: "Terminal growth", r: 0.339 }, { name: "Revenue growth", r: 0.277 },
    { name: "Capex %", r: -0.215 }, { name: "Inventory days", r: -0.113 },
    { name: "Tax rate", r: -0.08 }, { name: "D&A %", r: 0.029 },
  ],
};

export const trends = {
  keyword: "Tanishq", lags: [-1, 0, 1, 2, 3],
  levels:    [0.4383, 0.7003, 0.5975, 0.4622, 0.5944],
  levelsSig: ["*", "***", "***", "*", "**"],
  detrended:    [0.0782, 0.478, -0.1005, -0.3559, 0.1607],
  detrendedSig: ["ns", "**", "ns", "ns", "ns"],
};

export const sentiment = {
  latestMci: 0.10, overlayPp: 0.15, fvBase: 1013, fvAdj: 1018,
  dims: ["Demand", "Margin", "Growth", "Execution", "Hedging"],
  quarters: [
    { q: "FY25Q3", mci: 0.20, s: [1, 0, 1, 1, -1] },
    { q: "FY25Q4", mci: 0.00, s: [0, -1, 1, 1, -1] },
    { q: "FY26Q1", mci: 0.00, s: [0, -1, 1, 1, -1] },
    { q: "FY26Q2", mci: 0.10, s: [1, -1, 1, 1, -1] },
    { q: "FY26Q3", mci: 0.20, s: [1, 0, 1, 1, -1] },
    { q: "FY26Q4", mci: 0.10, s: [1, -1, 1, 1, -1] },
  ],
};

// Simplified central FCFF engine (mirrors 03_llm_sentiment/groq_sentiment.py
// central_fv). Anchors to ₹1,013 at terminal g = 5.5%, stage-1 adj = 0 —
// consistent with the Monte Carlo central-case check. Used by the interactive
// sentiment + reverse-DCF sliders so they move the model, not a static number.
export function centralFV(stage1Adj = 0, tgr = 0.055) {
  const CORE = 57332, INV = 28184, REC = 1068, PAY = 1963, OCL = 4441, GOLD = 7810;
  const NETDEBT = 11223, SH = 88.8, DA = 0.012, CX = 0.013, TAX = 0.255, W = 0.122;
  let g = [0.306, 0.16, 0.14, 0.125, 0.115, 0.10, 0.085, 0.07, 0.055];
  g = g.map((gx, i) => (i >= 1 && i <= 4 ? gx + stage1Adj : gx));
  const m = [0.109, 0.111, 0.113, 0.114, 0.115, 0.115, 0.115, 0.115, 0.115];
  const invd = [165, 163, 161, 159, 157, 156, 155, 154, 153];
  let nwcPrev = INV + REC - PAY - OCL - GOLD, prev = CORE, sumpv = 0, last = 0;
  for (let t = 0; t < 9; t++) {
    const core = prev * (1 + g[t]);
    const ebit = core * m[t] - core * DA;
    const nopat = ebit * (1 - TAX);
    const inv = (core / 365) * invd[t];
    const nwc = inv + (core / 365) * 7 - (core / 365) * 12 - core * 0.08 - inv * 0.28;
    const fcff = nopat + core * DA - core * CX - (nwc - nwcPrev);
    sumpv += fcff / Math.pow(1 + W, t + 0.5);
    last = fcff; nwcPrev = nwc; prev = core;
  }
  const tv = (last * (1 + tgr)) / (W - tgr);
  const ev = sumpv + tv / Math.pow(1 + W, 8.5);
  return (ev - NETDEBT) / SH;
}

export const theme = {
  bg: "#0a0e1a", panel: "#111827", grid: "#1f2937", border: "#374151",
  text: "#e5e7eb", dim: "#6b7280", gold: "#f59e0b", teal: "#14b8a6",
  purple: "#8b5cf6", pink: "#ec4899", green: "#10b981", red: "#ef4444",
  blue: "#3b82f6", orange: "#f97316",
};
