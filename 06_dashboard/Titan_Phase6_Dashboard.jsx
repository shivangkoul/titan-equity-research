import React, { useState, useMemo } from "react";
import {
  LineChart, Line, BarChart, Bar, ComposedChart, XAxis, YAxis, Tooltip,
  ReferenceLine, Cell, ResponsiveContainer,
} from "recharts";
// --- data inlined (mirrors ./data/*.json provenance) ---
// Phase 6 dashboard data — bound to the saved Phase 1-5 outputs.
// Raw provenance JSON lives in ./data/  (montecarlo_summary_v3.json,
// phase5_correlation_results.json, sentiment_results.json). Values transcribed
// here so the component renders both as a Vite app and as a single-file preview.

const dcf = {
  cmp: 4363, fairValue: 1017, ev: 101522, equity: 90299,
  tvPct: 0.654, wacc: 0.122, impliedG: 0.1133, gdp: 0.055,
  netDebt: 11223, shares: 88.8,
};

const mc = {
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

const trends = {
  keyword: "Tanishq", lags: [-1, 0, 1, 2, 3],
  levels:    [0.4383, 0.7003, 0.5975, 0.4622, 0.5944],
  levelsSig: ["*", "***", "***", "*", "**"],
  detrended:    [0.0782, 0.478, -0.1005, -0.3559, 0.1607],
  detrendedSig: ["ns", "**", "ns", "ns", "ns"],
};

const sentiment = {
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
function centralFV(stage1Adj = 0, tgr = 0.055) {
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

const T = {
  bg: "#0a0e1a", panel: "#111827", grid: "#1f2937", border: "#374151",
  text: "#e5e7eb", dim: "#6b7280", gold: "#f59e0b", teal: "#14b8a6",
  purple: "#8b5cf6", pink: "#ec4899", green: "#10b981", red: "#ef4444",
  blue: "#3b82f6", orange: "#f97316",
};

// --- end inlined data ---

const inr = (n) => "₹" + Math.round(n).toLocaleString("en-IN");
const pct = (n, d = 1) => (n * 100).toFixed(d) + "%";

function Card({ title, tag, icon, children, takeaway }) {
  return (
    <div style={{ background: T.panel, border: `1px solid ${T.border}`, borderRadius: 14, padding: "18px 20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <span style={{ fontSize: 15, fontWeight: 500, color: T.text }}>{icon} {title}</span>
        {tag && <span style={{ fontSize: 10.5, color: T.dim, border: `1px solid ${T.border}`, borderRadius: 6, padding: "2px 7px" }}>{tag}</span>}
      </div>
      {children}
      {takeaway && <p style={{ margin: "12px 0 0", fontSize: 12.5, color: T.dim, lineHeight: 1.5 }}>{takeaway}</p>}
    </div>
  );
}

function Stat({ label, value, color }) {
  return (
    <div style={{ background: "#0d1424", borderRadius: 10, padding: "10px 12px", minWidth: 0 }}>
      <div style={{ fontSize: 11.5, color: T.dim, marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 21, fontWeight: 600, color: color || T.text, lineHeight: 1.1 }}>{value}</div>
    </div>
  );
}

const tip = { background: "#0d1424", border: `1px solid ${T.border}`, borderRadius: 8, color: T.text, fontSize: 12 };

export default function App() {
  return (
    <div style={{ background: T.bg, minHeight: "100vh", color: T.text, fontFamily: "Inter, system-ui, sans-serif", padding: "28px 20px" }}>
      <div style={{ maxWidth: 1080, margin: "0 auto" }}>
        <Header />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(440px, 1fr))", gap: 16, marginTop: 16 }}>
          <ValuationPanel />
          <MonteCarloPanel />
          <SentimentPanel />
          <TrendsPanel />
        </div>
        <Footer />
      </div>
    </div>
  );
}

function Header() {
  const downside = dcf.fairValue / dcf.cmp - 1;
  return (
    <div style={{ background: T.panel, border: `1px solid ${T.border}`, borderRadius: 14, padding: "20px 22px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 600 }}>Titan Company Ltd</h1>
        <span style={{ fontSize: 13, color: T.dim }}>NSE: TITAN · independent equity research · FY25-reanchored</span>
        <span style={{ marginLeft: "auto", background: "#3a2a08", color: T.gold, border: `1px solid ${T.gold}`, fontSize: 13, fontWeight: 600, padding: "5px 16px", borderRadius: 8, letterSpacing: "0.06em" }}>HOLD</span>
      </div>
      <p style={{ margin: "10px 0 16px", fontSize: 14.5, color: "#cbd5e1" }}>A superb business priced for perfection — no margin of safety.</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: 10 }}>
        <Stat label="Current price" value={inr(dcf.cmp)} />
        <Stat label="DCF fair value" value={inr(dcf.fairValue)} color={T.teal} />
        <Stat label="Downside" value={pct(downside, 0)} color={T.red} />
        <Stat label="Implied perpetual growth" value={pct(dcf.impliedG)} color={T.gold} />
        <Stat label="WACC" value={pct(dcf.wacc)} />
      </div>
    </div>
  );
}

function ValuationPanel() {
  const [g, setG] = useState(dcf.gdp);
  const fv = useMemo(() => centralFV(0, g), [g]);
  const curve = useMemo(() => {
    const a = [];
    for (let x = 0.02; x <= 0.118; x += 0.004) a.push({ g: +(x * 100).toFixed(1), fv: Math.round(centralFV(0, x)) });
    return a;
  }, []);
  const justifies = fv >= dcf.cmp;
  return (
    <Card title="Valuation · DCF" tag="3-statement model" icon={<span style={{ color: T.teal }}>◆</span>}
      takeaway={`Two-stage 10-yr FCFF, WACC ${pct(dcf.wacc)}, TV ${pct(dcf.tvPct)} of EV. The market implies ~${pct(dcf.impliedG)} perpetual FCFF growth vs ~${pct(dcf.gdp)} nominal GDP — that is what you must believe to pay ${inr(dcf.cmp)}.`}>
      <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
        <Stat label="Enterprise value" value={inr(dcf.ev) + " Cr"} />
        <Stat label="Equity value" value={inr(dcf.equity) + " Cr"} />
        <Stat label="TV % of EV" value={pct(dcf.tvPct)} />
      </div>
      <div style={{ fontSize: 12.5, color: T.dim, marginBottom: 6 }}>Reverse-DCF · drag terminal growth to see implied fair value</div>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={curve} margin={{ top: 6, right: 10, bottom: 0, left: -8 }}>
          <XAxis dataKey="g" stroke={T.dim} tick={{ fontSize: 10, fill: T.dim }} tickFormatter={(v) => v + "%"} />
          <YAxis stroke={T.dim} tick={{ fontSize: 10, fill: T.dim }} tickFormatter={(v) => v >= 1000 ? (v/1000).toFixed(1)+"k" : v} />
          <Tooltip contentStyle={tip} formatter={(v) => [inr(v), "Fair value"]} labelFormatter={(l) => "Terminal g " + l + "%"} />
          <ReferenceLine y={dcf.cmp} stroke={T.red} strokeDasharray="4 3" label={{ value: "CMP", fill: T.red, fontSize: 10, position: "insideTopRight" }} />
          <ReferenceLine x={+(g * 100).toFixed(1)} stroke={T.gold} strokeDasharray="3 3" />
          <Line type="monotone" dataKey="fv" stroke={T.teal} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 6 }}>
        <input type="range" min="2.0" max="11.8" step="0.1" value={g * 100} onChange={(e) => setG(e.target.value / 100)} style={{ flex: 1 }} />
        <span style={{ fontSize: 12.5, color: T.dim, minWidth: 150, textAlign: "right" }}>
          g {(g * 100).toFixed(1)}% → <b style={{ color: justifies ? T.gold : T.teal }}>{inr(fv)}</b>
        </span>
      </div>
    </Card>
  );
}

function MonteCarloPanel() {
  const [x, setX] = useState(mc.median);
  const pts = [[mc.p10, 10], [mc.p25, 25], [mc.median, 50], [mc.p75, 75], [mc.p90, 90]];
  const pctlAt = (v) => {
    if (v <= pts[0][0]) return Math.max(1, 10 - (pts[0][0] - v) / 12);
    if (v >= pts[4][0]) return Math.min(99, 90 + (v - pts[4][0]) / 12);
    for (let i = 0; i < pts.length - 1; i++) {
      const [v0, p0] = pts[i], [v1, p1] = pts[i + 1];
      if (v >= v0 && v <= v1) return p0 + ((v - v0) / (v1 - v0)) * (p1 - p0);
    }
    return 50;
  };
  const drivers = [...mc.drivers].sort((a, b) => Math.abs(b.r) - Math.abs(a.r));
  const lo = mc.p10, hi = mc.p90, span = hi - lo;
  const posOf = (v) => Math.max(0, Math.min(100, ((v - lo) / span) * 100));
  return (
    <Card title="Monte Carlo · 10,000 trials" tag="montecarlo_summary_v3.json" icon={<span style={{ color: T.purple }}>◆</span>}
      takeaway={`Median ${inr(mc.median)}, 80% CI ${inr(mc.p10)}–${inr(mc.p90)}. P(fair value < CMP) = 100% — every single trial lands below ${inr(dcf.cmp)}.`}>
      <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
        <Stat label="Median" value={inr(mc.median)} color={T.purple} />
        <Stat label="P10 / P90" value={inr(mc.p10) + " / " + inr(mc.p90)} />
        <Stat label="P(FV < CMP)" value={pct(mc.pBelowCmp, 0)} color={T.red} />
      </div>
      <div style={{ position: "relative", height: 46, marginBottom: 4 }}>
        <div style={{ position: "absolute", top: 18, left: 0, right: 0, height: 10, background: "#0d1424", borderRadius: 5 }} />
        <div style={{ position: "absolute", top: 18, left: posOf(mc.p25) + "%", width: (posOf(mc.p75) - posOf(mc.p25)) + "%", height: 10, background: T.purple, opacity: 0.5, borderRadius: 5 }} />
        {[["P10", mc.p10], ["P25", mc.p25], ["P75", mc.p75], ["P90", mc.p90]].map(([l, v]) => (
          <div key={l} style={{ position: "absolute", top: 0, left: posOf(v) + "%", transform: "translateX(-50%)", fontSize: 9.5, color: T.dim }}>{l}</div>
        ))}
        <div style={{ position: "absolute", top: 14, left: posOf(mc.median) + "%", transform: "translateX(-50%)", width: 3, height: 18, background: T.gold }} />
        <div style={{ position: "absolute", top: 32, left: posOf(x) + "%", transform: "translateX(-50%)", width: 2, height: 14, background: T.teal }} />
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <input type="range" min={mc.p10} max={mc.p90} step="1" value={x} onChange={(e) => setX(+e.target.value)} style={{ flex: 1 }} />
        <span style={{ fontSize: 12.5, color: T.dim, minWidth: 168, textAlign: "right" }}>
          P(FV &lt; <b style={{ color: T.teal }}>{inr(x)}</b>) ≈ <b style={{ color: T.teal }}>{Math.round(pctlAt(x))}%</b>
        </span>
      </div>
      <div style={{ fontSize: 12.5, color: T.dim, marginBottom: 4 }}>Sensitivity · rank corr. of driver vs fair value</div>
      <ResponsiveContainer width="100%" height={150}>
        <BarChart data={drivers} layout="vertical" margin={{ top: 0, right: 12, bottom: 0, left: 70 }}>
          <XAxis type="number" domain={[-0.7, 0.7]} stroke={T.dim} tick={{ fontSize: 9, fill: T.dim }} />
          <YAxis type="category" dataKey="name" stroke={T.dim} tick={{ fontSize: 10, fill: T.dim }} width={68} />
          <Tooltip contentStyle={tip} formatter={(v) => [v.toFixed(3), "corr"]} />
          <ReferenceLine x={0} stroke={T.border} />
          <Bar dataKey="r" radius={2}>
            {drivers.map((d, i) => <Cell key={i} fill={d.r >= 0 ? T.teal : T.red} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

function SentimentPanel() {
  const [mci, setMci] = useState(sentiment.latestMci);
  const fv = useMemo(() => centralFV(mci * 0.015, 0.055), [mci]);
  const base = sentiment.fvBase;
  const trend = sentiment.quarters.map((q) => ({ q: q.q, mci: q.mci }));
  const latest = sentiment.quarters[sentiment.quarters.length - 1];
  const dimData = sentiment.dims.map((d, i) => ({ dim: d, v: latest.s[i] }));
  return (
    <Card title="Management sentiment · Groq LLM" tag="sentiment_results.json" icon={<span style={{ color: T.pink }}>◆</span>}
      takeaway={`${sentiment.quarters.length} real concalls scored on 5 analyst dimensions. Confidence is mildly positive and stable (MCI ${sentiment.latestMci.toFixed(2)}), capped by margin caution + heavy hedging. Bounded overlay (±1.5pp) moves FV only ${inr(sentiment.fvBase)}→${inr(sentiment.fvAdj)} — it cannot move the thesis.`}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div>
          <div style={{ fontSize: 12, color: T.dim, marginBottom: 4 }}>MCI trend</div>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={trend} margin={{ top: 6, right: 8, bottom: 0, left: -16 }}>
              <XAxis dataKey="q" stroke={T.dim} tick={{ fontSize: 9, fill: T.dim }} />
              <YAxis domain={[-0.3, 0.4]} stroke={T.dim} tick={{ fontSize: 9, fill: T.dim }} />
              <Tooltip contentStyle={tip} formatter={(v) => [v.toFixed(2), "MCI"]} />
              <ReferenceLine y={0} stroke={T.border} />
              <Line type="monotone" dataKey="mci" stroke={T.pink} strokeWidth={2} dot={{ r: 3, fill: T.pink }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div>
          <div style={{ fontSize: 12, color: T.dim, marginBottom: 4 }}>FY26Q4 dimensions</div>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={dimData} layout="vertical" margin={{ top: 4, right: 8, bottom: 0, left: 12 }}>
              <XAxis type="number" domain={[-2, 2]} stroke={T.dim} tick={{ fontSize: 9, fill: T.dim }} />
              <YAxis type="category" dataKey="dim" stroke={T.dim} tick={{ fontSize: 9, fill: T.dim }} width={56} />
              <ReferenceLine x={0} stroke={T.border} />
              <Bar dataKey="v" radius={2}>
                {dimData.map((d, i) => <Cell key={i} fill={d.v >= 0 ? T.teal : T.red} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8 }}>
        <span style={{ fontSize: 11.5, color: T.dim }}>MCI</span>
        <input type="range" min="-1" max="1" step="0.05" value={mci} onChange={(e) => setMci(+e.target.value)} style={{ flex: 1 }} />
        <span style={{ fontSize: 12.5, color: T.dim, minWidth: 184, textAlign: "right" }}>
          {mci.toFixed(2)} → overlay {(mci * 1.5).toFixed(2)}pp → <b style={{ color: T.pink }}>{inr(fv)}</b> <span style={{ color: fv >= base ? T.green : T.red }}>({fv >= base ? "+" : ""}{inr(fv - base)})</span>
        </span>
      </div>
    </Card>
  );
}

function TrendsPanel() {
  const data = trends.lags.map((lag, i) => ({
    lag: lag === 0 ? "0" : (lag > 0 ? "+" + lag : "" + lag),
    levels: trends.levels[i], detrended: trends.detrended[i],
    dSig: trends.detrendedSig[i],
  }));
  return (
    <Card title="Google Trends · &quot;Tanishq&quot;" tag="phase5_correlation_results.json" icon={<span style={{ color: T.gold }}>◆</span>}
      takeaway={`Lead-lag of search vs jewellery revenue. Raw levels look predictive (lag+1 r 0.60) but that is shared trend + Diwali seasonality. Detrended, only lag 0 survives (r 0.48) — and lag+1 collapses to −0.10 (ns). Search is coincident, NOT a leading indicator.`}>
      <div style={{ display: "flex", gap: 14, fontSize: 11.5, color: T.dim, marginBottom: 6 }}>
        <span><span style={{ color: T.blue }}>■</span> levels (raw)</span>
        <span><span style={{ color: T.gold }}>■</span> detrended (QoQ growth)</span>
        <span style={{ marginLeft: "auto" }}>lag &gt; 0 = search leads revenue</span>
      </div>
      <ResponsiveContainer width="100%" height={228}>
        <ComposedChart data={data} margin={{ top: 8, right: 10, bottom: 26, left: -14 }}>
          <XAxis dataKey="lag" stroke={T.dim} tick={{ fontSize: 11, fill: T.dim }} label={{ value: "lag (quarters)", fill: T.dim, fontSize: 10, position: "insideBottom", dy: 12 }} />
          <YAxis domain={[-0.5, 0.8]} stroke={T.dim} tick={{ fontSize: 10, fill: T.dim }} />
          <Tooltip contentStyle={tip} formatter={(v, n) => [v.toFixed(3), n]} />
          <ReferenceLine y={0} stroke={T.border} />
          <ReferenceLine y={0.6} stroke={T.dim} strokeDasharray="3 3" label={{ value: "strong 0.6", fill: T.dim, fontSize: 9, position: "insideTopRight" }} />
          <Bar dataKey="levels" fill={T.blue} radius={2} barSize={18} />
          <Bar dataKey="detrended" radius={2} barSize={18}>
            {data.map((d, i) => <Cell key={i} fill={d.lag === "+1" ? T.red : T.gold} />)}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
      <div style={{ fontSize: 12, color: T.dim, textAlign: "center", marginTop: 12 }}>detrended lag +1 (red) = <b style={{ color: T.red }}>−0.10, ns</b> → the honest verdict</div>
    </Card>
  );
}

function Footer() {
  return (
    <div style={{ marginTop: 16, padding: "16px 20px", background: T.panel, border: `1px solid ${T.border}`, borderRadius: 14, fontSize: 12, color: T.dim, lineHeight: 1.6 }}>
      <b style={{ color: T.text }}>Methodology &amp; sources.</b> Locked: FY25-reanchored 3-statement model (balances every year FY21–34); bullion ex-revenue; full Ind-AS 116 leases; two-stage 10-yr DCF; WACC {pct(dcf.wacc)} (Rf 7.0%, ERP 6.5%, β 0.85). Conclusion is HOLD by analysis, never reverse-engineered to market price — the reverse-DCF shows what the price implies.
      Sources: DCF — 01_model/Titan_Model_v2_FY25.xlsx · Monte Carlo — 02_montecarlo/montecarlo_summary_v3.json (n=10,000) · Sentiment — 03_llm_sentiment ({sentiment.quarters.length} real concalls, Groq llama-3.3-70b) · Trends — 05_google_trends (live pytrends, Tanishq, India, FY21–25). Shivang Koul · independent research.
    </div>
  );
}