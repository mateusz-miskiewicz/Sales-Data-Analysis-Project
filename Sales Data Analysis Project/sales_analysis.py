#!/usr/bin/env python3
"""
=============================================================================
  Sales Data Analysis — Senior Business Analyst & Data Scientist Report
  Dataset : Sales.csv  (SKU | Date | Sales)
  Period  : Jan 2023 – Jul 2024  |  95,452 transactions  |  1,235 SKUs
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─── Config ──────────────────────────────────────────────────────────────────
DATA_PATH = "Sales.csv"           # change to your path
OUT_DIR   = "./"                  # output charts here
PALETTE   = ["#2D6A4F","#40916C","#52B788","#74C69D","#95D5B2","#B7E4C7"]
ACCENT, RED, GOLD, NEUTRAL = "#2D6A4F","#E63946","#F4A261","#F0F4F8"
sns.set_theme(style="whitegrid")
DOW_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# =============================================================================
# MODULE 1 — DATA LOADING & FEATURE ENGINEERING
# =============================================================================
def load_and_engineer(path: str) -> pd.DataFrame:
    """Load CSV, clean types, remove returns, build derived columns."""
    df = pd.read_csv(path, sep=";", decimal=",", encoding="utf-8-sig")
    df["Date"]  = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df = df.dropna(subset=["Sales"])

    # Business rule: negative sales = returns/refunds → separate analysis
    df["Is_Return"] = df["Sales"] < 0
    df_clean = df[~df["Is_Return"]].copy()

    # Derived time dimensions
    df_clean["Month"]     = df_clean["Date"].dt.to_period("M")
    df_clean["Year"]      = df_clean["Date"].dt.year
    df_clean["DayOfWeek"] = df_clean["Date"].dt.day_name()
    df_clean["WeekNum"]   = df_clean["Date"].dt.isocalendar().week.astype(int)
    df_clean["Quarter"]   = df_clean["Date"].dt.to_period("Q")
    return df_clean

# =============================================================================
# MODULE 2 — KPI SUMMARY
# =============================================================================
def compute_kpis(df: pd.DataFrame) -> dict:
    """Return dict of headline KPIs + monthly trend with MoM growth."""
    monthly = (df.groupby("Month")["Sales"]
                 .sum()
                 .reset_index()
                 .rename(columns={"Sales":"Revenue"}))
    monthly["MoM_Growth_%"] = monthly["Revenue"].pct_change() * 100

    return {
        "gross_revenue" : df["Sales"].sum(),
        "atv"           : df["Sales"].sum() / len(df),   # Avg Transaction Value
        "transactions"  : len(df),
        "unique_skus"   : df["SKU"].nunique(),
        "monthly"       : monthly,
    }

# =============================================================================
# MODULE 3 — SKU-LEVEL RFM SEGMENTATION
# =============================================================================
def run_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recency  = days since last sale (lower = better)
    Frequency = number of transactions
    Monetary  = total revenue
    Segments  : VIP/Champions | Potential Stars | Mid-Tier | At Risk |
                Dormant/Lost  | New
    """
    snapshot = df["Date"].max()
    rfm = df.groupby("SKU").agg(
        Recency   = ("Date",  lambda x: (snapshot - x.max()).days),
        Frequency = ("Date",  "count"),
        Monetary  = ("Sales", "sum"),
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"],  4, labels=[4,3,2,1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"),  4, labels=[1,2,3,4]).astype(int)

    def _seg(row):
        r,f,m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r>=3 and f>=3 and m>=3: return "VIP / Champions"
        elif r>=3 and m>=3:        return "Potential Stars"
        elif r<=2 and f>=3:        return "At Risk"
        elif r==1 and f==1:        return "Dormant / Lost"
        elif f==1 and r>=3:        return "New"
        else:                      return "Mid-Tier"

    rfm["Segment"] = rfm.apply(_seg, axis=1)
    return rfm

# =============================================================================
# MODULE 4 — PRODUCT ANALYSIS
# =============================================================================
def product_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Return SKU performance table with Pareto ranking."""
    snapshot = df["Date"].max()
    sku = df.groupby("SKU").agg(
        Revenue        = ("Sales", "sum"),
        Transactions   = ("Date",  "count"),
        Avg_Sale       = ("Sales", "mean"),
        Days_Since_Last= ("Date",  lambda x: (snapshot - x.max()).days),
    ).sort_values("Revenue", ascending=False).reset_index()
    sku["Revenue_Rank"]  = range(1, len(sku)+1)
    sku["Revenue_Share"] = sku["Revenue"] / sku["Revenue"].sum() * 100
    sku["Cum_Share"]     = sku["Revenue_Share"].cumsum()
    return sku

# =============================================================================
# MODULE 5 — VISUALISATIONS
# =============================================================================
def plot_monthly_trend(monthly: pd.DataFrame, out: str):
    """Monthly revenue bar chart with 3-month rolling average overlay."""
    monthly["Month_dt"] = monthly["Month"].dt.to_timestamp()
    monthly["MA3"]      = monthly["Revenue"].rolling(3, center=True).mean()
    fig, ax = plt.subplots(figsize=(14,5))
    ax.set_facecolor(NEUTRAL); fig.patch.set_facecolor("white")
    ax.bar(monthly["Month_dt"], monthly["Revenue"]/1e6,
           color=ACCENT, alpha=0.65, width=25, label="Monthly Revenue")
    ax.plot(monthly["Month_dt"], monthly["MA3"]/1e6,
            color=RED, lw=2.5, marker="o", ms=5, label="3-Month Rolling Avg")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"£{x:.0f}M"))
    ax.set_title("📈  Monthly Revenue Trend  |  Jan 2023 – Jul 2024",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10); plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()


def plot_dow_heatmap(df: pd.DataFrame, out: str):
    """Week × Day-of-week sales heatmap + day totals bar chart."""
    pivot = df.pivot_table(values="Sales", index="WeekNum",
                           columns="DayOfWeek", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(columns=DOW_ORDER)
    dow_rev = df.groupby("DayOfWeek")["Sales"].sum().reindex(DOW_ORDER)
    fig, axes = plt.subplots(1, 2, figsize=(16,5),
                              gridspec_kw={"width_ratios":[2.5,1]})
    fig.patch.set_facecolor("white")
    sns.heatmap(pivot/1e3, ax=axes[0], cmap="YlGn", linewidths=0.3,
                linecolor="white", xticklabels=[d[:3] for d in DOW_ORDER],
                cbar_kws={"label":"Revenue (£K)"})
    axes[0].set_title("Sales Heatmap — Week × Day of Week", fontsize=13, fontweight="bold")
    colors = [ACCENT if d not in ["Saturday","Sunday"] else GOLD for d in DOW_ORDER]
    axes[1].barh(DOW_ORDER, dow_rev.values/1e6, color=colors)
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"£{x:.0f}M"))
    axes[1].set_title("Total Revenue by Day", fontsize=12, fontweight="bold")
    axes[1].invert_yaxis(); plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()


def plot_rfm_pareto(rfm: pd.DataFrame, sku: pd.DataFrame, out: str):
    """Donut chart of revenue by RFM segment + Pareto concentration curve."""
    SEG_COLORS = {"VIP / Champions":"#2D6A4F","Mid-Tier":"#74C69D",
                  "At Risk":"#E63946","Potential Stars":"#F4A261",
                  "Dormant / Lost":"#ADB5BD","New":"#48CAE4"}
    seg_rev = rfm.groupby("Segment").agg(Count=("SKU","count"),
               Revenue=("Monetary","sum")).sort_values("Revenue",ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(16,6))
    fig.patch.set_facecolor("white")
    cols = [SEG_COLORS.get(s,"#888") for s in seg_rev.index]
    wedges,_,at = axes[0].pie(seg_rev["Revenue"], colors=cols,
                               autopct="%1.1f%%", startangle=140,
                               pctdistance=0.78, wedgeprops=dict(width=0.55,edgecolor="white",lw=2))
    for x in at: x.set_fontsize(9); x.set_color("white"); x.set_fontweight("bold")
    axes[0].legend(wedges,seg_rev.index,loc="lower left",fontsize=9,
                   title="Segment",framealpha=0.9)
    axes[0].set_title("Revenue by RFM Segment",fontsize=13,fontweight="bold")
    n = len(sku)
    axes[1].set_facecolor(NEUTRAL)
    axes[1].fill_between(sku["Revenue_Rank"],sku["Cum_Share"],alpha=0.25,color=ACCENT)
    axes[1].plot(sku["Revenue_Rank"],sku["Cum_Share"],color=ACCENT,lw=2.5)
    axes[1].axhline(80,color=RED,ls="--",lw=1.5,alpha=0.8)
    p80 = sku[sku["Cum_Share"]<=80].iloc[-1]
    axes[1].axvline(p80["Revenue_Rank"],color=RED,ls="--",lw=1.5,alpha=0.8)
    axes[1].set_title("Pareto Curve — SKU Revenue Concentration",
                      fontsize=13,fontweight="bold")
    axes[1].set_xlabel("SKUs (ranked)"); axes[1].set_ylabel("Cumulative Revenue %")
    axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_:f"{x:.0f}%"))
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight"); plt.close()


# =============================================================================
# MAIN PIPELINE
# =============================================================================
if __name__ == "__main__":
    df     = load_and_engineer(DATA_PATH)
    kpis   = compute_kpis(df)
    rfm    = run_rfm(df)
    sku    = product_analysis(df)

    plot_monthly_trend(kpis["monthly"], OUT_DIR + "chart1_monthly_trend.png")
    plot_dow_heatmap(df,               OUT_DIR + "chart2_dow_heatmap.png")
    plot_rfm_pareto(rfm, sku,          OUT_DIR + "chart3_rfm_pareto.png")

    rfm.to_csv(OUT_DIR + "rfm_segments.csv", index=False)
    sku.to_csv(OUT_DIR + "sku_performance.csv", index=False)
    print("✓ Analysis complete. Check output directory for charts and CSVs.")
