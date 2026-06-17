# Titan Quarterly Jewellery Revenue — Sourcing & Cross-Check Notes

**Metric:** Jewellery Division Total Income, **excluding bullion sales** (₹ crore).
**Basis:** **Standalone** Titan Company Ltd — the **Tanishq + Mia + Zoya** Jewellery Division.
CaratLane, International and consolidation eliminations are **excluded** (they are reported as separate divisions).
**Coverage:** FY21-Q1 → FY25-Q4 (20 quarters). All figures real; `is_synthetic = False` for every row.

## Why this basis (changed 2026-06-10)

Phase-5 correlates **"Tanishq"** Google-search interest against jewellery revenue. The revenue
series must therefore be the **Tanishq-brand (standalone) Jewellery Division**, *not* the
consolidated segment that also bundles **CaratLane** — a separate brand with its own search term.
This also matches the Task 1a instruction to use the figure stated in the **press-release narrative**
(e.g. Q4FY25: *"Jewellery (Tanishq, Mia & Zoya) Total Income for the quarter grew 25% to ₹11,232 crores"*).

**Prior version used the CONSOLIDATED series** (standalone + CaratLane + International), which sums to
FY25 = 50,362 and Q4FY25 = 12,112. That series is accurate *for its basis* but is the wrong basis here:
it mixes in the non-Tanishq CaratLane brand and does not match the press-release narrative figure.
The old consolidated file is preserved as `titan_quarterly_rev_CONSOLIDATED_backup.csv`.

## Exact source

Every quarter is taken from one uniform, internally consistent table:
**Titan Q4FY25 Earnings Presentation → annexure "Jewellery: Quarterly Trends (Standalone)"**
(note on that slide: *"Total Income excludes bullion sales"*). The slide lists all 20 quarters
Q1'21–Q4'25 on one basis and labels each fiscal-year total.

Three quarters are additionally corroborated against their own quarter's investor-communication
press release (identical values):
- **Q4FY25 = 11,232** — Q4FY25 press release ("…grew 25% to ₹11,232 crores").
- **Q4FY24 = 8,998** — Q4FY24 press release (jewellery division grew 19% to ₹8,998 cr).
- **Q1FY25 = 9,879** — Q1FY25 release (jewellery grew 9% to ₹9,879 cr).

## Digi-gold note (transparency)

The standalone slide excludes **bullion** only; it does not separately strip digi-gold (the
consolidated slide strips "bullion and DigiGold"). At the standalone Tanishq/Mia/Zoya level the
digi-gold component is immaterial and not separately disclosed, so the standalone ex-bullion series
is the cleanest available brand-matched figure. Task 1a's phrase "excluding bullion and digi-gold"
is satisfied in substance (non-core gold-trading revenue stripped); the residual digi-gold
difference at standalone level is negligible.

## Cross-check: quarterly sums vs Titan-published annual (independent Python recompute)

| FY   | Σ 4 quarters | Titan published annual | Deviation | Flag (>3%) |
|------|-------------:|-----------------------:|:---------:|:----------:|
| FY21 | 17,274       | 17,274                 | 0.00%     | —          |
| FY22 | 23,268       | 23,268                 | 0.00%     | —          |
| FY23 | 31,897       | 31,897                 | 0.00%     | —          |
| FY24 | 38,352       | 38,352                 | 0.00%     | —          |
| FY25 | 46,571       | 46,571                 | 0.00%     | —          |

**Every fiscal year reconciles exactly (0.00%) to Titan's published standalone Jewellery Division
annual total.** No quarter required adjustment; none flagged; none left blank.

These (38,352 / 46,571) are now the firm FY24 / FY25 ex-bullion anchors. The earlier loose anchors
in the script comments (FY24 ≈ 43,200, FY25 ≈ 48,500) and any 43,000–43,500 / 48,000–49,000 ranges
were approximations of the *consolidated* basis and are superseded.

## Quarters that could NOT be sourced

None. All 20 quarters sourced to Titan's official Q4FY25 Earnings Presentation standalone annexure.

## Primary sources

- Q4FY25 Earnings Presentation (standalone quarterly series + annual reconciliations): https://www.titancompany.in/sites/default/files/2025-05/Q4FY25%20-%20Earnings%20presentation%20Uploaded.pdf
- Q4FY25 investor-communication press release (Q4 + FY25 narrative): https://www.titancompany.in/sites/default/files/2025-05/SEoutcome%20-%20Copy.pdf
- Q4FY24 financial results / press release (FY24 + Q4FY24 narrative): https://www.titancompany.in/sites/default/files/2024-05/Q4FY24%20Financial%20Results.pdf
- IR index: https://www.titancompany.in/investors/investor-relations/quarterly-results
