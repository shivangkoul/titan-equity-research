#!/usr/bin/env python3
"""
Phase 5 — Google Trends Alternative Data Layer
Titan Company Ltd (NSE: TITAN) Independent Equity Research
==========================================================

Pipeline:
  1. Fetch "Tanishq" + "Titan watches" weekly search interest (Google Trends, India)
  2. Aggregate to Indian fiscal quarters  (Q1=Apr–Jun | Q2=Jul–Sep | Q3=Oct–Dec | Q4=Jan–Mar)
  3. Align with quarterly jewellery-segment revenue from BSE quarterly filings
  4. Compute Pearson r at lags  –1, 0, +1, +2, +3  (levels AND detrended QoQ growth)
  5. Identify best lead lag; report r + p-value for both series
  6. Produce publication-quality dual-axis chart + correlation bar chart (dark/cosmic theme)
  7. Save correlation JSON for dashboard (Phase 6)

Usage:
  python phase5_trends.py                        # --sample mode  (safe in any environment)
  python phase5_trends.py --live                 # calls pytrends  (run on local machine)
  python phase5_trends.py --live --save-raw      # also saves raw weekly CSV
  python phase5_trends.py --keyword "Titan watches"

IMPORTANT — Google Trends blocks datacenter / server IPs.
  Always verify the pipeline with --sample first, then run --live on your local Windows machine.
  Once fetched, save with --save-raw so future runs load from CSV instead.

Install:
  pip install pytrends pandas numpy scipy matplotlib
"""

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D

warnings.filterwarnings('ignore')

# ─── Configuration ────────────────────────────────────────────────────────────
KEYWORDS       = ['Tanishq', 'Titan watches']
GEO            = 'IN'
OUTPUT_DIR     = Path('outputs')
RAW_TRENDS_CSV = OUTPUT_DIR / 'tanishq_trends_raw.csv'
REV_CSV        = Path('titan_quarterly_rev.csv')

# ─── Quarterly Revenue Reference Data ─────────────────────────────────────────
#
# *** USER: REPLACE THESE WITH ACTUALS FROM BSE QUARTERLY FILINGS ***
#
# Where to get real data:
#   BSE India →  https://www.bseindia.com/corporates/ann.html  (Titan, scrip 500114)
#   Or:          Titan Investor Relations → Quarterly Results → Segment Revenue
#   Or:          Screener.in → Titan → Quarterly → Jewellery Revenue (ex bullion)
#
# Annual anchors (verified, from 3-statement model):
#   FY21 jewellery ex-bullion ≈ ₹18,600 Cr  (COVID-impacted; Q1/Q2 near-zero)
#   FY22 jewellery ex-bullion ≈ ₹26,900 Cr
#   FY23 jewellery ex-bullion ≈ ₹36,500 Cr
#   FY24 jewellery ex-bullion ≈ ₹43,200 Cr  (jewellery ~84.5% of ₹51,084 Cr total)
#   FY25 jewellery ex-bullion ≈ ₹48,500 Cr  (jewellery ~84.6% of ₹57,332 Cr total)
#
# Seasonal split used to build synthetic quarters:
#   Q1 (Apr–Jun)  ≈ 17–19%  (weakest — summer, no major festivals)
#   Q2 (Jul–Sep)  ≈ 18–20%  (off-peak — monsoon, auspicious-days trough)
#   Q3 (Oct–Dec)  ≈ 33–36%  (PEAK — Diwali + Dhanteras + wedding season begins)
#   Q4 (Jan–Mar)  ≈ 26–28%  (strong — wedding season peak, Valentine's)
#
# These quarterly splits are SYNTHETIC (illustrative for pipeline testing).
# Annual totals are consistent with the verified 3-statement model.

QUARTERLY_REV_SYNTHETIC = {
    # FY21 — COVID year; Q1 (Apr–Jun 2020) near-total lockdown
    'FY21-Q1':  1_500,
    'FY21-Q2':  3_400,
    'FY21-Q3':  8_400,
    'FY21-Q4':  5_300,
    # FY22 — recovery; Q1/Q2 still suppressed by second wave
    'FY22-Q1':  4_200,
    'FY22-Q2':  4_800,
    'FY22-Q3':  9_900,
    'FY22-Q4':  8_000,
    # FY23 — normalised demand + premiumisation
    'FY23-Q1':  6_400,
    'FY23-Q2':  7_100,
    'FY23-Q3': 13_500,
    'FY23-Q4':  9_500,
    # FY24 — strong growth; gold-price tailwind
    'FY24-Q1':  7_500,
    'FY24-Q2':  8_000,
    'FY24-Q3': 15_800,
    'FY24-Q4': 11_900,
    # FY25 — gold-duty compression in Q2; Q3 recovery
    'FY25-Q1':  8_200,
    'FY25-Q2':  8_500,
    'FY25-Q3': 17_200,
    'FY25-Q4': 14_600,
}

# ─── Dark / Cosmic Chart Theme  (matches Phase 3 Monte Carlo) ─────────────────
T = {
    'bg':     '#0a0e1a',
    'panel':  '#111827',
    'grid':   '#1f2937',
    'border': '#374151',
    'text':   '#e5e7eb',
    'dim':    '#6b7280',
    'gold':   '#f59e0b',
    'teal':   '#14b8a6',
    'purple': '#8b5cf6',
    'pink':   '#ec4899',
    'green':  '#10b981',
    'red':    '#ef4444',
    'blue':   '#3b82f6',
    'orange': '#f97316',
}


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def fiscal_quarter_label(date: pd.Timestamp) -> str:
    """
    Map any calendar date to its Indian fiscal quarter label.

    Indian FY runs April → March.  FY25 = April 2024 – March 2025.

    Apr 2024 → FY25-Q1   |   Jul 2024 → FY25-Q2
    Oct 2024 → FY25-Q3   |   Jan 2025 → FY25-Q4
    """
    m, y = date.month, date.year
    if m >= 4:
        fy = y + 1               # Apr 2024 → FY = 2025
        q  = (m - 4) // 3 + 1   # Apr,May,Jun=1  Jul,Aug,Sep=2  Oct,Nov,Dec=3
    else:
        fy = y                   # Jan,Feb,Mar 2025 → FY = 2025
        q  = 4
    return f'FY{str(fy)[-2:]}-Q{q}'


def quarter_sort_key(label: str) -> pd.Timestamp:
    """'FY25-Q3' → 2024-10-01  (for chronological sorting)"""
    fy    = int('20' + label[2:4])      # 'FY25' → 2025
    q     = int(label[-1])
    month = {1: 4, 2: 7, 3: 10, 4: 1}[q]
    year  = fy - 1 if month >= 4 else fy
    return pd.Timestamp(year, month, 1)


def first_difference(series: pd.Series) -> pd.Series:
    """Quarter-on-quarter absolute change; removes secular trend."""
    return series.diff().dropna()


def qoq_growth(series: pd.Series) -> pd.Series:
    """Quarter-on-quarter percentage growth; removes secular trend."""
    return series.pct_change().dropna() * 100


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHETIC SAMPLE DATA  (--sample mode)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sample_trends() -> pd.DataFrame:
    """
    Produce synthetic weekly Google Trends data that plausibly mimics Tanishq
    and Titan watches search behaviour in India.

    Design principles:
      • Diwali peak (week ~42, mid-Oct) — primary annual peak for both keywords
      • Wedding-season secondary peak (week ~5, early-Feb) — stronger for Tanishq
      • Positive secular trend over FY21–FY25 (+20% cumulative uplift, Tanishq)
      • Gaussian random noise  σ ≈ 5–7 index points
      • Values rescaled so whole-period max = 100, matching pytrends output

    These values are SYNTHETIC — run --live on your local machine for real data.
    """
    rng   = np.random.default_rng(seed=42)
    dates = pd.date_range('2020-04-06', '2025-03-30', freq='W-MON')
    n     = len(dates)
    t     = np.arange(n)   # sequential week index

    def build_series(diwali_amp, wedding_amp, secular_uplift, base, noise_std):
        woy = np.array([d.isocalendar()[1] for d in dates])   # week-of-year 1–53

        # Gaussian bumps centred on festival weeks
        diwali      = diwali_amp  * np.exp(-0.5 * ((woy - 42) / 3.5) ** 2)
        wedding     = wedding_amp * np.exp(-0.5 * ((woy -  5) / 3.0) ** 2)
        # Wrap-around for weddings near year boundary (woy 53/1)
        wedding_wrap = wedding_amp * np.exp(-0.5 * ((woy - 57) / 3.0) ** 2)

        secular = secular_uplift * t / n        # linear secular growth
        noise   = rng.normal(0, noise_std, n)

        raw = base + secular + diwali + wedding + wedding_wrap + noise
        raw = np.clip(raw, 1, None)
        return (raw / raw.max() * 100).round(1)  # rescale: max → 100

    tanishq       = build_series(diwali_amp=36, wedding_amp=16, secular_uplift=20,
                                  base=42, noise_std=5)
    titan_watches = build_series(diwali_amp=30, wedding_amp= 8, secular_uplift=12,
                                  base=28, noise_std=6)

    return pd.DataFrame({
        'date':          dates,
        'Tanishq':       tanishq,
        'Titan watches': titan_watches,
        'isPartial':     False,
    })


# ══════════════════════════════════════════════════════════════════════════════
# LIVE pytrends FETCH  (--live mode)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_live_trends(save_raw: bool = False) -> pd.DataFrame:
    """
    Fetch weekly Google Trends data for KEYWORDS via pytrends.

    Fetches in 2-year chunks (pytrends returns weekly granularity for ≤2-year
    windows; monthly for longer windows — weekly is needed for quarterly agg).

    Retry logic: up to 3 attempts with exponential backoff on 429 responses.
    After fetching, re-normalises each keyword so whole-period max = 100
    (each chunk is independently scaled; re-normalisation makes them comparable).

    Requirements:
      • pip install pytrends
      • Residential / local IP  (Google blocks datacenter IPs)
    """
    try:
        from pytrends.request import TrendReq
    except ImportError:
        sys.exit('[ERROR] pytrends not installed.\n'
                 '        Run: pip install pytrends\n'
                 '        Then re-run with --live on your local machine.')

    print('[INFO] Connecting to Google Trends …')
    # NOTE: pytrends builds a urllib3 Retry with method_whitelist=..., which was
    # REMOVED in urllib3>=2.0 (renamed to allowed_methods) -> TypeError on construct.
    # pytrends only builds that Retry when retries>0 OR backoff_factor>0, so we set
    # both to 0 to skip the broken code path. The script's own retry loop (below)
    # already handles retries/backoff, so no retry behaviour is lost.
    pt = TrendReq(hl='en-US', tz=330, retries=0, backoff_factor=0,
                  requests_args={'verify': True})

    # Chunk timeframes  → weekly granularity
    chunks = [
        ('2020-04-01 2022-03-31', 'FY21–22'),
        ('2022-04-01 2024-03-31', 'FY23–24'),
        ('2024-04-01 2025-03-31', 'FY25'),
    ]
    frames = []
    for timeframe, label in chunks:
        for attempt in range(3):
            try:
                print(f'  Fetching {label} (attempt {attempt + 1}/3) …')
                pt.build_payload(KEYWORDS, cat=0, timeframe=timeframe,
                                 geo=GEO, gprop='')
                chunk = pt.interest_over_time()
                if chunk.empty:
                    print(f'  [WARN] Empty response for {label}')
                    break
                frames.append(chunk.reset_index())
                time.sleep(3 + attempt * 4)   # polite delay between requests
                break
            except Exception as e:
                wait = 15 * (2 ** attempt)
                print(f'  [WARN] {e!r} — waiting {wait}s then retrying …')
                time.sleep(wait)
        else:
            sys.exit(
                f'[ERROR] Failed to fetch {label} after 3 attempts.\n'
                f'  Possible causes:\n'
                f'    • Not a residential IP (try on your home Wi-Fi)\n'
                f'    • Google temporarily blocking — wait 30 min then retry\n'
                f'    • pytrends version issue — try: pip install --upgrade pytrends'
            )

    df = (pd.concat(frames, ignore_index=True)
            .drop_duplicates(subset='date')
            .sort_values('date')
            .reset_index(drop=True))

    # Re-normalise across full period so all chunks share same scale
    for kw in KEYWORDS:
        if kw in df.columns and df[kw].max() > 0:
            df[kw] = (df[kw] / df[kw].max() * 100).round(1)

    if save_raw:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(RAW_TRENDS_CSV, index=False)
        print(f'[INFO] Raw weekly data saved → {RAW_TRENDS_CSV}')
        print('[INFO] Future runs can load from this file instead of re-fetching.')

    return df


# ══════════════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ══════════════════════════════════════════════════════════════════════════════

def aggregate_to_quarters(trends_df: pd.DataFrame) -> pd.DataFrame:
    """
    Average weekly search index values into Indian fiscal quarters.

    Weekly → Quarterly mean preserves the relative amplitude of seasonal peaks
    while reducing noise.  Returns one row per quarter for each keyword.
    """
    df       = trends_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['fq']   = df['date'].apply(fiscal_quarter_label)

    cols      = [k for k in KEYWORDS if k in df.columns]
    quarterly = (df.groupby('fq')[cols]
                   .mean()
                   .round(1)
                   .reset_index()
                   .rename(columns={'fq': 'quarter'}))

    quarterly['_sort'] = quarterly['quarter'].apply(quarter_sort_key)
    return (quarterly.sort_values('_sort')
                     .drop(columns='_sort')
                     .reset_index(drop=True))


def load_quarterly_revenue() -> pd.DataFrame:
    """
    Load Titan jewellery segment quarterly revenue.

    Priority:
      1. titan_quarterly_rev.csv  (if exists and has required columns)
      2. QUARTERLY_REV_SYNTHETIC  (hardcoded illustrative values)

    On first run the synthetic dict is written to CSV as a template the user
    can populate with real BSE data.
    """
    if REV_CSV.exists():
        df = pd.read_csv(REV_CSV)
        if {'quarter', 'jewellery_rev_cr'}.issubset(df.columns):
            df = df.dropna(subset=['jewellery_rev_cr'])
            if not df.empty:
                print(f'[INFO] Revenue loaded from {REV_CSV}  ({len(df)} quarters)')
                return df

    # Fallback to synthetic
    print('[INFO] Using SYNTHETIC quarterly revenue (pipeline testing)')
    print('[WARN] ──────────────────────────────────────────────────────')
    print('[WARN] Replace jewellery_rev_cr values in titan_quarterly_rev.csv')
    print('[WARN] with actuals from BSE quarterly segment results before')
    print('[WARN] including this analysis in your published research.')
    print('[WARN] ──────────────────────────────────────────────────────')

    rows = [{'quarter': k, 'jewellery_rev_cr': v, 'is_synthetic': True}
            for k, v in QUARTERLY_REV_SYNTHETIC.items()]
    df = pd.DataFrame(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(REV_CSV, index=False)
    print(f'[INFO] Template written → {REV_CSV}  (fill in column jewellery_rev_cr)')
    return df


# ══════════════════════════════════════════════════════════════════════════════
# CORRELATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def compute_lagged_correlations(
    trends_q: pd.Series,
    rev_q:    pd.Series,
    max_lag:  int = 3,
) -> dict:
    """
    Compute Pearson r between Trends[t] and Revenue[t + lag].

    Positive lag  →  Trends LEADS Revenue  (leading indicator hypothesis)
    Negative lag  →  Revenue leads Trends  (reverse-causality test)
    Lag = 0       →  Contemporaneous  (people search while shopping)

    Returns dict keyed by lag integer, plus 'best_lead_lag' key.
    Each entry: {'r', 'p', 'n', 'interpretation', 'sig'}
    """
    results = {}
    for lag in range(-1, max_lag + 1):
        if lag > 0:
            x = trends_q.values[:-lag]
            y = rev_q.values[lag:]
        elif lag < 0:
            x = trends_q.values[-lag:]
            y = rev_q.values[:lag]
        else:
            x = trends_q.values
            y = rev_q.values

        n = min(len(x), len(y))
        x, y = x[:n], y[:n]

        if n < 4:
            results[lag] = dict(r=np.nan, p=np.nan, n=n,
                                interpretation='insufficient data', sig='–')
            continue

        r, p = stats.pearsonr(x, y)
        interp = (f'Revenue leads Trends by {abs(lag)}Q' if lag < 0 else
                  'Contemporaneous'                       if lag == 0 else
                  f'Trends leads Revenue by {lag}Q')
        sig = ('***' if p < 0.01 else
               '**'  if p < 0.05 else
               '*'   if p < 0.10 else 'ns')

        results[lag] = dict(r=round(r, 4), p=round(p, 4),
                            n=n, interpretation=interp, sig=sig)

    # Best lead lag = highest r at lag ≥ 0
    valid_lead = [k for k in results if isinstance(k, int) and k >= 0
                  and not np.isnan(results[k]['r'])]
    results['best_lead_lag'] = max(valid_lead, key=lambda k: results[k]['r'])
    return results


def compute_detrended_correlations(
    trends_q: pd.Series,
    rev_q:    pd.Series,
    max_lag:  int = 3,
) -> dict:
    """
    Robustness check: same lagged Pearson analysis but on QoQ GROWTH RATES.

    Why this matters:
      Both search interest and jewellery revenue have trended upward over
      FY21–FY25 (secular growth).  A high Pearson r on raw levels may just
      reflect shared upward trends rather than a genuine cyclical relationship.

      First-differencing (using QoQ % growth) removes the secular component
      and isolates the quarter-to-quarter oscillations.  If Trends is a true
      leading indicator, the correlation should survive detrending.

    Limitation: first-differencing reduces N by 1; with ~20 quarters we end
    up with ~19 observations — interpret p-values cautiously.
    """
    # QoQ percentage change; drop the initial NaN
    t_diff = trends_q.pct_change().dropna().reset_index(drop=True) * 100
    r_diff = rev_q.pct_change().dropna().reset_index(drop=True) * 100

    # Realign to same length after differencing
    n_common = min(len(t_diff), len(r_diff))
    t_diff = t_diff.iloc[:n_common]
    r_diff = r_diff.iloc[:n_common]

    return compute_lagged_correlations(t_diff, r_diff, max_lag=max_lag)


# ══════════════════════════════════════════════════════════════════════════════
# PUBLICATION CHART
# ══════════════════════════════════════════════════════════════════════════════

def plot_phase5(
    trends_q:    pd.DataFrame,
    rev_q:       pd.DataFrame,
    corr_levels: dict,
    corr_detrend:dict,
    keyword:     str = 'Tanishq',
    is_synthetic:bool = True,
) -> Path:
    """
    Produce a 3-panel publication-quality chart:

    Panel A (top, 55%)   Dual-axis: quarterly search index (bars) vs revenue (line)
    Panel B (mid, 23%)   Levels correlation bar chart (lags –1 to +3)
    Panel C (bot, 22%)   Detrended (QoQ growth) correlation bar chart — robustness check

    Theme: dark/cosmic, consistent with Phase 3 Monte Carlo chart.
    """
    # ── Merge + sort ────────────────────────────────────────────────────────
    merged = (pd.merge(trends_q[['quarter', keyword]],
                       rev_q[['quarter', 'jewellery_rev_cr']],
                       on='quarter', how='inner')
                .sort_values('quarter')
                .reset_index(drop=True))

    quarters   = merged['quarter'].tolist()
    search_idx = merged[keyword].values
    revenue    = merged['jewellery_rev_cr'].values
    n_q        = len(quarters)
    x          = np.arange(n_q)

    # ── Figure ──────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 12.5), facecolor=T['bg'])
    gs  = gridspec.GridSpec(3, 1,
                            height_ratios=[2.6, 1.0, 1.0],
                            hspace=0.52,
                            top=0.90, bottom=0.08,
                            left=0.065, right=0.94)
    ax_main  = fig.add_subplot(gs[0])
    ax_lvl   = fig.add_subplot(gs[1])
    ax_detr  = fig.add_subplot(gs[2])

    # ── Shared style helper ─────────────────────────────────────────────────
    def style_ax(ax):
        ax.set_facecolor(T['panel'])
        ax.tick_params(colors=T['text'], labelsize=8.5)
        for sp in ax.spines.values():
            sp.set_edgecolor(T['border'])
        ax.grid(True, color=T['grid'], linewidth=0.45, alpha=0.7, axis='y')

    for ax in [ax_main, ax_lvl, ax_detr]:
        style_ax(ax)

    # ══════════════════════════════════════════════════════════════════════
    # PANEL A — dual-axis: search bars + revenue line
    # ══════════════════════════════════════════════════════════════════════
    bar_w = 0.6
    # Q3 bars in gold (Diwali peak); rest in teal
    bar_colors = [T['gold'] if q.endswith('Q3') else T['teal'] for q in quarters]
    ax_main.bar(x, search_idx, width=bar_w,
                color=bar_colors, alpha=0.72, zorder=2)

    # Revenue on twin axis
    ax_rev = ax_main.twinx()
    ax_rev.set_facecolor('none')
    ax_rev.plot(x, revenue / 1_000, color=T['purple'],
                linewidth=2.4, marker='o', markersize=5.5,
                zorder=3, label='Revenue')
    ax_rev.tick_params(colors=T['text'], labelsize=8.5)
    for sp in ax_rev.spines.values():
        sp.set_edgecolor(T['border'])
    ax_rev.set_ylabel('Jewellery Revenue (₹000 Cr)', color=T['text'], fontsize=9)
    ax_rev.yaxis.label.set_color(T['text'])

    # Axis labels
    ax_main.set_xticks(x)
    ax_main.set_xticklabels(quarters, rotation=50, ha='right', fontsize=7.5)
    ax_main.set_xlim(-0.7, n_q - 0.3)
    ax_main.set_ylim(0, 122)
    ax_main.set_ylabel('Google Search Index (0–100)', color=T['text'], fontsize=9)
    ax_main.yaxis.label.set_color(T['text'])

    # Best-lag callout box
    bl = corr_levels['best_lead_lag']
    br = corr_levels[bl]['r']
    bp = corr_levels[bl]['p']
    bs = corr_levels[bl]['sig']
    lead_text = (f'Best lead lag: {bl}Q ahead   r = {br:.2f}   p = {bp:.3f} {bs}'
                 if bl > 0 else
                 f'Contemporaneous peak   r = {br:.2f}   p = {bp:.3f} {bs}')
    ax_main.text(
        0.015, 0.965, lead_text,
        transform=ax_main.transAxes,
        color=T['gold'], fontsize=9, va='top',
        bbox=dict(boxstyle='round,pad=0.45', facecolor='#181e30',
                  edgecolor=T['gold'], alpha=0.9)
    )

    # Legend
    leg_elems = [
        Line2D([0],[0], color=T['teal'],   linewidth=0, marker='s',
               markersize=10, label=f'{keyword} Search (off-peak quarters)'),
        Line2D([0],[0], color=T['gold'],   linewidth=0, marker='s',
               markersize=10, label=f'{keyword} Search (Q3 — Diwali peak)'),
        Line2D([0],[0], color=T['purple'], linewidth=2.4, marker='o',
               markersize=5.5, label='Jewellery Segment Revenue'),
    ]
    ax_main.legend(handles=leg_elems, loc='upper left',
                   fontsize=8, facecolor='#1a1f35',
                   edgecolor=T['border'], labelcolor=T['text'],
                   framealpha=0.92)

    # ══════════════════════════════════════════════════════════════════════
    # HELPER — draw a correlation bar sub-panel
    # ══════════════════════════════════════════════════════════════════════
    def draw_corr_panel(ax, corr_dict, title, subtitle=''):
        lags   = sorted(k for k in corr_dict if isinstance(k, int))
        r_vals = [corr_dict[k]['r'] for k in lags]
        p_vals = [corr_dict[k]['p'] for k in lags]
        sigs   = [corr_dict[k]['sig'] for k in lags]
        best   = corr_dict['best_lead_lag']

        colors = []
        for k, r in zip(lags, r_vals):
            if np.isnan(r): colors.append(T['dim'])
            elif k == best: colors.append(T['gold'])
            elif r > 0:     colors.append(T['teal'])
            else:           colors.append(T['red'])

        x_c = np.arange(len(lags))
        ax.bar(x_c, r_vals, color=colors, alpha=0.85, width=0.55, zorder=2)

        # Reference lines
        for ref_val, ls, alpha in [(0.6, '--', 0.55), (0.4, ':', 0.45), (0.0, '-', 0.6)]:
            ax.axhline(ref_val, color=T['dim'], linewidth=0.75,
                       linestyle=ls, alpha=alpha, zorder=1)
            if ref_val > 0:
                ax.text(len(lags) - 0.05, ref_val + 0.02,
                        f'r={ref_val:.1f}', color=T['dim'],
                        fontsize=7, ha='right', va='bottom')

        # Significance stars above bars
        for i, (r, p, sig) in enumerate(zip(r_vals, p_vals, sigs)):
            if not np.isnan(r):
                offset = 0.02 if r >= 0 else -0.06
                ax.text(i, r + offset, sig, ha='center', va='bottom',
                        color=T['text'], fontsize=9, fontweight='bold')

        # X labels
        xlabels = []
        for k in lags:
            if k < 0:
                xlabels.append(f'Lag {k:+d}Q\n(rev.)')
            elif k == 0:
                xlabels.append('Lag 0\n(contemp.)')
            else:
                xlabels.append(f'Lag +{k}Q\n(fwd.)')

        ax.set_xticks(x_c)
        ax.set_xticklabels(xlabels, fontsize=8, color=T['text'])
        ax.set_ylabel('Pearson r', color=T['text'], fontsize=8.5)
        ax.yaxis.label.set_color(T['text'])

        y_max = max((r for r in r_vals if not np.isnan(r)), default=0.8)
        y_min = min((r for r in r_vals if not np.isnan(r)), default=-0.1)
        ax.set_ylim(min(-0.15, y_min - 0.05), max(0.95, y_max + 0.12))

        ax.set_title(f'{title}  |  {subtitle}',
                     color=T['text'], fontsize=9.5, pad=5)

    # ══════════════════════════════════════════════════════════════════════
    # PANELS B & C
    # ══════════════════════════════════════════════════════════════════════
    draw_corr_panel(
        ax_lvl, corr_levels,
        'Lagged Correlation — Levels',
        'Raw search index vs revenue (shared secular trend not removed)'
    )
    draw_corr_panel(
        ax_detr, corr_detrend,
        'Lagged Correlation — Detrended (QoQ % Growth)',
        'First-differenced: removes secular trend; isolates cyclical signal ← robustness check'
    )

    # ── Figure title & footnotes ────────────────────────────────────────────
    synth_flag = '   ⚠ SYNTHETIC DATA — pipeline test only' if is_synthetic else ''
    fig.suptitle(
        f'TITAN COMPANY LTD (NSE: TITAN)   —   Google Trends Alternative-Data Layer\n'
        f'"{keyword}" Search Interest vs Jewellery Segment Revenue (India, FY21–FY25)'
        f'{synth_flag}',
        color=T['text'], fontsize=12.5, fontweight='bold', y=0.965
    )

    fig.text(
        0.50, 0.01,
        'Source: Google Trends (pytrends) · BSE Quarterly Segment Filings   |   '
        'Significance: *** p<0.01  ** p<0.05  * p<0.10  ns = not significant   |   '
        'Shivang Koul — Titan Equity Research FY25',
        ha='center', va='bottom', color=T['dim'], fontsize=7
    )

    # ── Save ────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mode = 'sample' if is_synthetic else 'live'
    kw_slug = keyword.lower().replace(' ', '_')
    out = OUTPUT_DIR / f'titan_phase5_trends_{kw_slug}_{mode}.png'
    fig.savefig(out, dpi=160, bbox_inches='tight', facecolor=T['bg'])
    plt.close(fig)
    print(f'[INFO] Chart saved → {out}')
    return out


# ══════════════════════════════════════════════════════════════════════════════
# TEXT REPORT
# ══════════════════════════════════════════════════════════════════════════════

def print_report(
    corr_levels:  dict,
    corr_detrend: dict,
    is_synthetic: bool = True,
    keyword:      str  = 'Tanishq',
) -> None:
    mode = 'SYNTHETIC (pipeline test)' if is_synthetic else 'LIVE Google Trends'
    w    = 72

    print('\n' + '═' * w)
    print(f'  Phase 5 — Google Trends Lagged Correlation   [{mode}]')
    print(f'  Keyword: {keyword}')
    print('═' * w)

    for label, corr in [('LEVELS (raw series)', corr_levels),
                         ('DETRENDED  (QoQ % growth — robustness check)', corr_detrend)]:
        print(f'\n  ── {label} ──')
        print(f'  {"Lag":>6}  {"Interpretation":<35} {"r":>7} {"p":>8} {"Sig":>4} {"N":>4}')
        print('  ' + '─' * (w - 2))
        for lag in sorted(k for k in corr if isinstance(k, int)):
            d = corr[lag]
            flag = '  ◀ best lead' if lag == corr['best_lead_lag'] else ''
            print(f'  {lag:>+6}Q  {d["interpretation"]:<35} '
                  f'{d["r"]:>7.3f} {d["p"]:>8.4f} {d["sig"]:>4} {d["n"]:>4}{flag}')

    print('\n' + '═' * w)
    print('  SUMMARY')
    bl = corr_levels['best_lead_lag']
    print(f'  Levels  best lead   : lag +{bl}Q  '
          f'r={corr_levels[bl]["r"]:.3f}  '
          f'p={corr_levels[bl]["p"]:.4f}  {corr_levels[bl]["sig"]}')
    bd = corr_detrend['best_lead_lag']
    print(f'  Detrend best lead   : lag +{bd}Q  '
          f'r={corr_detrend[bd]["r"]:.3f}  '
          f'p={corr_detrend[bd]["p"]:.4f}  {corr_detrend[bd]["sig"]}')
    print()
    print('  Interpretation guide:')
    print('    r ≥ 0.60 + sig  →  strong leading indicator')
    print('    r 0.40–0.59     →  moderate; useful supplementary signal')
    print('    r < 0.40 or ns  →  weak; use only qualitative (seasonality confirmation)')
    print()
    if is_synthetic:
        print('  ⚠  Synthetic data — correlations are ILLUSTRATIVE only.')
        print('     Run --live on your local machine for real results.')
    print('═' * w + '\n')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Phase 5 — Google Trends alt-data layer for Titan equity research'
    )
    parser.add_argument(
        '--live', action='store_true',
        help='Fetch real data from Google Trends via pytrends. '
             'MUST run on a residential/local IP (not server/datacenter).'
    )
    parser.add_argument(
        '--save-raw', action='store_true',
        help='Save raw weekly trends CSV after a live fetch (avoids re-fetching later).'
    )
    parser.add_argument(
        '--keyword', default='Tanishq', choices=['Tanishq', 'Titan watches'],
        help='Primary keyword for the dual-axis chart (default: Tanishq).'
    )
    parser.add_argument(
        '--max-lag', type=int, default=3,
        help='Max lead lag to test in quarters (default: 3).'
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Get trends data ──────────────────────────────────────────────
    if args.live:
        print('\n[PHASE 5] LIVE mode — calling Google Trends API')
        trends_raw   = fetch_live_trends(save_raw=args.save_raw)
        is_synthetic = False
    else:
        print('\n[PHASE 5] SAMPLE mode — using synthetic data (safe in any environment)')
        print('[INFO]    To get real data: python phase5_trends.py --live')
        print('[INFO]    (Run on your local Windows machine, not a server)\n')
        trends_raw   = generate_sample_trends()
        is_synthetic = True

    # ── Step 2: Aggregate to fiscal quarters ─────────────────────────────────
    trends_q = aggregate_to_quarters(trends_raw)
    print(f'[INFO] Trends aggregated → {len(trends_q)} fiscal quarters '
          f'({trends_q["quarter"].iloc[0]} – {trends_q["quarter"].iloc[-1]})')

    # ── Step 3: Load quarterly revenue ───────────────────────────────────────
    rev_q = load_quarterly_revenue()

    # ── Step 4: Align on common quarters ─────────────────────────────────────
    merged = (pd.merge(trends_q[['quarter', args.keyword]],
                       rev_q[['quarter', 'jewellery_rev_cr']],
                       on='quarter', how='inner')
                .sort_values('quarter')
                .reset_index(drop=True))

    print(f'[INFO] Aligned dataset → {len(merged)} quarters matched '
          f'({merged["quarter"].iloc[0]} – {merged["quarter"].iloc[-1]})')

    if len(merged) < 8:
        sys.exit('[ERROR] Fewer than 8 aligned quarters.  Check that titan_quarterly_rev.csv '
                 'covers the same date range as the trends data (FY21–FY25).')

    # ── Step 5: Lagged correlations (levels + detrended) ─────────────────────
    print('[INFO] Computing lagged correlations …')
    corr_lvl   = compute_lagged_correlations(
        merged[args.keyword], merged['jewellery_rev_cr'], max_lag=args.max_lag
    )
    corr_detr  = compute_detrended_correlations(
        merged[args.keyword], merged['jewellery_rev_cr'], max_lag=args.max_lag
    )
    print_report(corr_lvl, corr_detr, is_synthetic=is_synthetic, keyword=args.keyword)

    # ── Step 6: Chart ─────────────────────────────────────────────────────────
    chart_path = plot_phase5(
        trends_q=trends_q, rev_q=rev_q,
        corr_levels=corr_lvl, corr_detrend=corr_detr,
        keyword=args.keyword, is_synthetic=is_synthetic,
    )

    # ── Step 7: Save JSON for Phase 6 dashboard ───────────────────────────────
    def _serialisable(d):
        return {str(k): {kk: (float(vv) if isinstance(vv, (np.floating, float)) else vv)
                         for kk, vv in v.items()}
                if isinstance(v, dict) else v
                for k, v in d.items()}

    payload = {
        'keyword':          args.keyword,
        'is_synthetic':     is_synthetic,
        'generated_at':     pd.Timestamp.now().isoformat(),
        'n_quarters':       int(len(merged)),
        'levels':           _serialisable(corr_lvl),
        'detrended_qoq':    _serialisable(corr_detr),
    }
    json_path = OUTPUT_DIR / 'phase5_correlation_results.json'
    with open(json_path, 'w') as f:
        json.dump(payload, f, indent=2, default=str)
    print(f'[INFO] Correlation JSON saved → {json_path}  (ready for Phase 6 dashboard)')

    print('\n[DONE] Phase 5 complete.')
    if is_synthetic:
        print('       ─────────────────────────────────────────────────────────')
        print('       Next step: run the script live on your local machine')
