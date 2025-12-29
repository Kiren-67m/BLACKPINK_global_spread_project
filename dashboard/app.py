# app.py
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# -----------------------------
# Global Plotly Theme: BLACKPINK (Light Background)
# -----------------------------
BLACKPINK_COLORWAY = [
    "#0B0B0B",  # black
    "#FF4FA3",  # BP pink
    "#B5179E",  # magenta-purple accent
    "#7A7A7A",  # gray
]

pio.templates["blackpink_light"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#0B0B0B"),
        title=dict(font=dict(color="#0B0B0B")),
        colorway=BLACKPINK_COLORWAY,

        # Lock continuous colors (prevents Viridis yellow/green)
        coloraxis=dict(
            colorscale=[
                [0.0, "#0B0B0B"],   # black
                [0.5, "#B5179E"],   # purple
                [1.0, "#FF4FA3"],   # pink
            ],
            cmin=0,
            cmax=1,
        ),

        xaxis=dict(
            title=dict(font=dict(size=14, color="#0B0B0B")),
            tickfont=dict(size=12, color="#0B0B0B"),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            zeroline=False,
            linecolor="rgba(0,0,0,0.20)",
        ),
        yaxis=dict(
            title=dict(font=dict(size=14, color="#0B0B0B")),
            tickfont=dict(size=12, color="#0B0B0B"),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            zeroline=False,
            linecolor="rgba(0,0,0,0.20)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="rgba(0,0,0,0.12)",
            borderwidth=1,
            font=dict(color="#0B0B0B"),
        ),
    )
)
pio.templates.default = "blackpink_light"

# -----------------------
# Streamlit setup
# -----------------------
st.set_page_config(
    page_title="BLACKPINK Spotify Diffusion Dashboard",
    layout="wide"
)

st.title("BLACKPINK — Early Diffusion Dashboard (ERR-6 Baseline)")
st.caption("7-day window (Day0–Day6) • Core markets: Global / US / Indonesia • Metric: ERR-6 = Day6 / Peak within 7 days")

# -----------------------
# Data paths (works in Streamlit)
# -----------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

FILES = {
    "metrics": os.path.join(DATA_DIR, "metrics_with_era.csv"),
    "era_summary": os.path.join(DATA_DIR, "era_market_anchor_summary.csv"),
    "gap": os.path.join(DATA_DIR, "main_vs_pre_gap.csv"),
}

missing = [k for k, p in FILES.items() if not os.path.exists(p)]
if missing:
    st.error(
        f"Missing files in dashboard/data: {missing}\n\nExpected:\n"
        "- metrics_with_era.csv\n- era_market_anchor_summary.csv\n- main_vs_pre_gap.csv"
    )
    st.stop()

metrics = pd.read_csv(FILES["metrics"])
era_summary = pd.read_csv(FILES["era_summary"])
gap = pd.read_csv(FILES["gap"])

# Ensure numeric
for col in ["retention_day6_vs_peak", "peak_streams_calc", "day6_streams"]:
    if col in metrics.columns:
        metrics[col] = pd.to_numeric(metrics[col], errors="coerce")

# Orders
MARKET_ORDER = ["Global", "US", "ID"]
ANCHOR_ORDER = ["Main", "Pre"]

# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.header("Filters")

market_opts = sorted(
    metrics["market"].dropna().unique().tolist(),
    key=lambda x: MARKET_ORDER.index(x) if x in MARKET_ORDER else 999
)
sel_markets = st.sidebar.multiselect("Market", options=market_opts, default=[m for m in MARKET_ORDER if m in market_opts])

anchor_opts = metrics["anchor_type"].dropna().unique().tolist()
anchor_default = [x for x in ANCHOR_ORDER if x in anchor_opts]
sel_anchor = st.sidebar.multiselect("Anchor Type", options=anchor_opts, default=anchor_default)

era_opts = metrics["era"].dropna().unique().tolist()
sel_era = st.sidebar.multiselect("Era", options=era_opts, default=era_opts)

show_table = st.sidebar.checkbox("Show data tables", value=False)

df = metrics[
    metrics["market"].isin(sel_markets) &
    metrics["anchor_type"].isin(sel_anchor) &
    metrics["era"].isin(sel_era)
].copy()

# -----------------------
# KPI row
# -----------------------
def safe_mean(s):
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.mean()) if len(s) else np.nan

def safe_median(s):
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float(s.median()) if len(s) else np.nan

def safe_max_row(dataframe, col):
    d = dataframe.dropna(subset=[col])
    if d.empty:
        return None
    return d.loc[d[col].idxmax()]

kpi_cols = st.columns(5)

track_key = "track_id" if "track_id" in df.columns else "track_name"
n_tracks = int(df[track_key].nunique()) if not df.empty else 0

avg_err6 = safe_mean(df["retention_day6_vs_peak"]) if "retention_day6_vs_peak" in df.columns else np.nan
med_err6 = safe_median(df["retention_day6_vs_peak"]) if "retention_day6_vs_peak" in df.columns else np.nan

best = safe_max_row(df, "retention_day6_vs_peak") if not df.empty else None
best_label = f"{best['track_name']} ({best['market']})" if best is not None else "—"
best_val = float(best["retention_day6_vs_peak"]) if best is not None else np.nan

jump_df = df[
    (df.get("track_id", "").astype(str).str.upper() == "BP10") |
    (df.get("track_name", "").astype(str).str.upper() == "JUMP")
].copy()
jump_avg = safe_mean(jump_df["retention_day6_vs_peak"]) if (not jump_df.empty and "retention_day6_vs_peak" in jump_df.columns) else np.nan

kpi_cols[0].metric("Anchor Tracks (filtered)", f"{n_tracks}")
kpi_cols[1].metric("Avg ERR-6", f"{avg_err6:.3f}" if np.isfinite(avg_err6) else "—")
kpi_cols[2].metric("Median ERR-6", f"{med_err6:.3f}" if np.isfinite(med_err6) else "—")
kpi_cols[3].metric("Best ERR-6 (track)", f"{best_val:.3f}" if np.isfinite(best_val) else "—", help=best_label)
kpi_cols[4].metric("Jump (avg ERR-6)", f"{jump_avg:.3f}" if np.isfinite(jump_avg) else "—")

st.divider()

# -----------------------
# Layout grid
# -----------------------
row1 = st.columns([2, 2, 2])
row2 = st.columns([2, 2, 2])
row3 = st.columns([3, 3])

# 1) Boxplot — ERR-6 by Market × Anchor Type
with row1[0]:
    st.subheader("ERR-6 Distribution by Market × Type")
    if df.empty:
        st.info("No data under current filters.")
    else:
        fig = px.box(
            df,
            x="market",
            y="retention_day6_vs_peak",
            color="anchor_type",
            category_orders={"market": MARKET_ORDER, "anchor_type": ANCHOR_ORDER},
            points="all",
        )
        fig.update_traces(line=dict(width=1.2), marker=dict(size=6, opacity=0.7))
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        fig.update_yaxes(range=[0, 1.05], title="ERR-6 (Day6 / Peak)")
        st.plotly_chart(fig, use_container_width=True)

# 2) Heatmap — avg ERR-6 (Era × Market)
with row1[1]:
    st.subheader("Avg ERR-6 Heatmap (Era × Market)")
    if df.empty:
        st.info("No data under current filters.")
    else:
        pivot = (
            df.groupby(["era", "market"], as_index=False)
              .agg(avg_err6=("retention_day6_vs_peak", "mean"))
        )
        heat_df = (
            pivot.pivot(index="era", columns="market", values="avg_err6")
                 .reindex(columns=MARKET_ORDER)
        )

        fig = px.imshow(
            heat_df,
            text_auto=True,
            zmin=0.0,
            zmax=1.0,
            aspect="auto",
        )

        # ✅ 强制黑→紫→粉，避免黄绿（Plotly 默认 Viridis）
        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=40, b=10),
            coloraxis=dict(
                colorscale=[
                    [0.0, "#0B0B0B"],   # black
                    [0.5, "#B5179E"],   # purple
                    [1.0, "#FF4FA3"],   # pink
                ],
                cmin=0.0,
                cmax=1.0,
            )
        )

        st.plotly_chart(fig, use_container_width=True)
# 3) Bar — Main vs Pre gap
with row1[2]:
    st.subheader("Main − Pre Gap (avg ERR-6)")
    if gap.empty or "main_minus_pre" not in gap.columns:
        st.info("Gap table not available (main_vs_pre_gap.csv).")
    else:
        gap_f = gap.copy()
        if "era" in gap_f.columns and "market" in gap_f.columns:
            gap_f = gap_f[gap_f["market"].isin(sel_markets) & gap_f["era"].isin(sel_era)].copy()

        fig = px.bar(
            gap_f,
            x="era",
            y="main_minus_pre",
            color="market",
            barmode="group",
            category_orders={"market": MARKET_ORDER},
        )
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        fig.update_yaxes(title="Main − Pre (avg ERR-6)")
        st.plotly_chart(fig, use_container_width=True)

# 4) Line — Era trend by Market
with row2[0]:
    st.subheader("Era Trend (Avg ERR-6)")
    if df.empty:
        st.info("No data under current filters.")
    else:
        trend = (
            df.groupby(["era", "market"], as_index=False)
              .agg(avg_err6=("retention_day6_vs_peak", "mean"), n=(track_key, "nunique"))
        )
        fig = px.line(
            trend,
            x="era",
            y="avg_err6",
            color="market",
            markers=True,
            category_orders={"market": MARKET_ORDER},
        )
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        fig.update_yaxes(range=[0, 1.05], title="Avg ERR-6")
        st.plotly_chart(fig, use_container_width=True)

# 5) Scatter — Peak vs ERR-6 (size by Day6 streams if available)
with row2[1]:
    st.subheader("Scale vs Stability (Peak vs ERR-6)")
    if df.empty or "peak_streams_calc" not in df.columns:
        st.info("Need peak_streams_calc in metrics_with_era.csv")
    else:
        plot_df = df.dropna(subset=["peak_streams_calc", "retention_day6_vs_peak"]).copy()
        size_col = "day6_streams" if "day6_streams" in plot_df.columns else None

        fig = px.scatter(
            plot_df,
            x="peak_streams_calc",
            y="retention_day6_vs_peak",
            color="market",
            symbol="anchor_type",
            size=size_col,
            hover_data=["track_name", "era", "market", "anchor_type"],
            category_orders={"market": MARKET_ORDER, "anchor_type": ANCHOR_ORDER},
        )
        fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
        fig.update_yaxes(range=[0, 1.05], title="ERR-6")
        fig.update_xaxes(title="Peak streams (within Day0–Day6)")
        st.plotly_chart(fig, use_container_width=True)

# 6) Table or extra summary
with row2[2]:
    st.subheader("Quick Summary (Era × Market)")
    if df.empty:
        st.info("No data under current filters.")
    else:
        summary = (
            df.groupby(["era", "market"], as_index=False)
              .agg(
                  n_tracks=(track_key, "nunique"),
                  avg_err6=("retention_day6_vs_peak", "mean"),
                  med_err6=("retention_day6_vs_peak", "median"),
              )
        )
        # Optional style: keep it clean
        st.dataframe(summary, use_container_width=True)

# -----------------------
# Optional tables
# -----------------------
if show_table:
    st.divider()
    st.subheader("Filtered Data (metrics_with_era.csv)")
    st.dataframe(df, use_container_width=True)

    st.subheader("Era Summary (era_market_anchor_summary.csv)")
    st.dataframe(era_summary, use_container_width=True)

    st.subheader("Main vs Pre Gap (main_vs_pre_gap.csv)")
    st.dataframe(gap, use_container_width=True)
