# Sales Data Analysis — Business Intelligence Report

> **Dataset:** `Sales.csv` · 95,452 transactions · 1,235 unique SKUs · Jan 2023 – Jul 2024
> **Stack:** Python · pandas · matplotlib · seaborn · RFM modelling

---

## Project Structure

```
├── sales_analysis.py          # Modular analysis pipeline
├── Sales.csv                  # Raw input data
├── chart1_monthly_trend.png   # Monthly revenue + rolling average
├── chart2_dow_heatmap.png     # Week × day-of-week heatmap
├── chart3_rfm_pareto.png      # RFM donut + Pareto concentration curve
├── rfm_segments.csv           # RFM scores and segments per SKU
└── sku_performance.csv        # Full SKU performance ranking
```

---

## Key Performance Indicators

| Metric | Value |
|---|---|
| **Gross Revenue** | £325,190,277 |
| **Net Revenue** (after returns) | £323,550,607 |
| **Average Transaction Value** | £3,421 |
| **Total Transactions** | 95,057 |
| **Active SKUs** | 1,235 |
| **Return Rate** | 0.4% |

---

## Monthly Revenue Highlights

| Best Month | £58.8M (Dec 2023) |
|---|---|
| Worst Month | £1.3M (Jul 2024 — partial) |
| Biggest MoM Gain | +378% (Jan → Mar 2023) |
| Biggest MoM Drop | −91% (Dec 2023 → Jan 2024) |

> **Pattern:** The business exhibits strong **seasonal cyclicality** with major spikes in Mar, Jun, Sep/Nov/Dec. This aligns with procurement/contract cycles typical of B2B wholesale or industrial supply.

---

## RFM Segmentation Results

| Segment | SKUs | Revenue | Avg Days Since Last Sale |
|---|---|---|---|
| **VIP / Champions** | 377 | £248.6M (76.4%) | 2 days |
| Mid-Tier | 515 | £48.5M (14.9%) | 104 days |
| At Risk | 110 | £24.9M (7.6%) | 200 days |
| Potential Stars | 40 | £2.2M | 19 days |
| Dormant / Lost | 174 | £1.0M | 325 days |
| New | 19 | £0.05M | 14 days |

> **Key finding:** Just **377 SKUs (30%)** are responsible for **76.4% of all revenue** — a highly concentrated portfolio requiring focused inventory management.

---

## Product Assortment Analysis

### Top 5 Bestsellers (by Revenue)
| Rank | SKU | Revenue | Share |
|---|---|---|---|
| 1 | 3e64781a | £83.6M | 25.7% |
| 2 | 5f0f394f | £35.9M | 11.0% |
| 3 | f4b57eb5 | £23.9M | 7.3% |
| 4 | 0bffeb60 | £13.3M | 4.1% |
| 5 | 33f6c7fc | £8.0M | 2.5% |

### Pareto Finding
> **4.1% of SKUs (51 products) generate 80% of revenue.** Classic Pareto concentration.

### Reorder Candidates (High Frequency + Recent Activity)
SKUs with 350+ transactions and last sale within 30 days — prioritise for stock replenishment.

### Long Tail (Consider Rationalising)
174 dormant SKUs with ≤2 lifetime sales — evaluate for discontinuation or clearance pricing.

---

## Executive Summary — 3 Strategic Recommendations

### 1. Win Back "At Risk" SKUs Before They Go Dormant
**110 SKUs** with historically high frequency are now 200 days without a sale (£24.9M at risk).
- Run targeted **reactivation campaigns** for buyers of these products
- Offer volume-discount bundles or early-renewal incentives
- Set automated alerts at day 60/90/120 of no sales activity

### 2. Scale VIP Champions — Protect the Revenue Core
**377 SKUs drive 76.4% of revenue** and are actively selling (avg 2 days ago).
- Ensure **100% stock availability** for all Champion-tier SKUs at all times
- Negotiate **priority supply agreements** with manufacturers of these lines
- Introduce a loyalty/rebate programme for buyers purchasing Champion products

### 3. Leverage Seasonality — Pre-Position Inventory for Peak Months
Revenue spikes **3–5× in March, June, and December** — but the business appears caught under-stocked in Jan/Aug (post-spike drops of −91% and −69%).
- Build **inventory buffers 6–8 weeks ahead** of historically high-demand months
- Pre-book logistics capacity in Oct–Nov for December peak
- Run demand-forecasting on the top 51 Pareto SKUs to reduce stockout risk during spikes

---

## Technical Notes

- **RFM model** uses quartile scoring (1–4) across Recency, Frequency, and Monetary dimensions
- **Returns** (0.4% of transactions) are excluded from gross revenue but tracked separately
- All charts saved as high-resolution PNG (150 dpi) for reporting use
- Modular code design — each analytical function is independently callable

---


