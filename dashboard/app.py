# app.py
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# Dashboard colors sampled from official artwork. Raster colors are approximate.
# YG, Pink Venom cover: https://ygfamily.com/en/artists/blackpink/discography/252
INK = "#000000"
DEEP_ROSE = "#B54B62"
LIGHT_PINK = "#FAC6D3"
# YGEX, PINK logo sticker: https://ygex.jp/blackpink/goods/item.php?id=1023862
LOGO_PINK = "#F1A4B6"
# Official BORN PINK title poster: https://blackpinkofficial.com/music/born-pink/release-bornpink/index.html
BRIGHT_PINK = "#FF9BB4"
BLUSH = "#FDEDF1"
# YG, THE ALBUM cover: https://ygfamily.com/contents/images/2023/04/blackpink-album-thealbum.jpg
COVER_BLACK = "#150A0E"
COMPARISON_GRAY = "#6F7281"

BLACKPINK_COLORWAY = [INK, DEEP_ROSE, COMPARISON_GRAY, LOGO_PINK]
PINK_SCALE = [(0.0, INK), (0.5, DEEP_ROSE), (1.0, LIGHT_PINK)]

pio.templates["blackpink_light"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color=INK),
        title=dict(font=dict(color=INK)),
        colorway=BLACKPINK_COLORWAY,

        # Lock continuous colors (prevents Viridis yellow/green)
        coloraxis=dict(
            colorscale=PINK_SCALE,
            cmin=0,
            cmax=1,
        ),

        xaxis=dict(
            title=dict(font=dict(size=14, color=INK)),
            tickfont=dict(size=12, color=INK),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            zeroline=False,
            linecolor="rgba(0,0,0,0.20)",
        ),
        yaxis=dict(
            title=dict(font=dict(size=14, color=INK)),
            tickfont=dict(size=12, color=INK),
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            zeroline=False,
            linecolor="rgba(0,0,0,0.20)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="rgba(0,0,0,0.12)",
            borderwidth=1,
            font=dict(color=INK),
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

st.html(
    f"<style>:root{{--bp-ink:{INK};--bp-cover:{COVER_BLACK};--bp-rose:{DEEP_ROSE};"
    f"--bp-logo:{LOGO_PINK};--bp-bright:{BRIGHT_PINK};--bp-light:{LIGHT_PINK};--bp-blush:{BLUSH};}}</style>"
    """
<style>
[data-testid="stMainBlockContainer"] {max-width: 80rem; padding-top: 3.75rem;}
.st-key-release_header {
    background: linear-gradient(110deg, var(--bp-ink), var(--bp-cover));
    border-top: 3px solid var(--bp-bright); border-radius: .7rem;
    padding: .65rem clamp(.95rem, 3vw, 1.6rem) 1rem; gap: .3rem;
}
#blackpink-release-performance {
    color: var(--bp-logo); font-size: clamp(1.75rem, 4vw, 3rem); letter-spacing: -.045em;
}
.st-key-release_header [data-testid="stCaptionContainer"] {opacity: .9;}
.st-key-release_header [data-testid="stCaptionContainer"] p {color: var(--bp-light);}
[data-testid="stRadioOption"] {
    border: 1px solid var(--bp-light); border-radius: .55rem; padding: .32rem .62rem;
}
[data-testid="stRadioOption"] > span + div > div:first-child {display: none;}
[data-testid="stRadioOption"][data-selected="true"] {background: var(--bp-ink); border-color: var(--bp-ink);}
[data-testid="stRadioOption"][data-selected="true"] p {color: var(--bp-logo);}
[data-testid="stRadioOption"]:has(input:focus-visible) {outline: 2px solid var(--bp-rose); outline-offset: 2px;}
.st-key-overview_metrics [data-testid="stMetric"] {
    background: linear-gradient(155deg, #fff 24%, var(--bp-blush)); border-color: var(--bp-light);
    border-top: 2px solid var(--bp-rose); border-radius: .65rem; padding: .65rem .85rem;
}
.st-key-overview_metrics [data-testid="stMetricValue"] {font-variant-numeric: tabular-nums;}
.st-key-overview_metrics [data-testid="stMetricLabel"] p {white-space: normal;}
@media (max-width: 640px) {
    .st-key-overview_metrics [data-testid="stHorizontalBlock"] {
        display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .5rem;
    }
    .st-key-overview_metrics [data-testid="stColumn"] {width: 100%; min-width: 0;}
    .st-key-overview_metrics [data-testid="stMetric"] {padding: .5rem;}
    .st-key-overview_metrics [data-testid="stMetricValue"] {font-size: clamp(1.1rem, 4vw, 1.55rem);}
}
</style>
"""
)

with st.container(key="release_header"):
    st.title("BLACKPINK · Release Performance")
    st.caption("Spotify Charts · Release benchmarks, country markets and tour cities")

# -----------------------
# Data paths (works in Streamlit)
# -----------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROJECT_DATA = os.path.join(DATA_DIR, "..", "..", "data")

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

view = st.radio(
    "View", ["Overview", "Release comparison", "Peer benchmark", "City charts", "Market breakdown", "Events & search interest", "Research detail"],
    horizontal=True, label_visibility="collapsed",
)

if view == "Overview":
    tour = pd.read_csv(os.path.join(DATA_DIR, "jump_city_summary.csv"))
    tour = tour.sort_values("gain_vs_controls", ascending=False)
    lead_city = tour.iloc[0]
    weekly = pd.read_csv(os.path.join(DATA_DIR, "peer_weekly.csv"))
    jump = weekly.loc[weekly["cohort"].eq("target")].sort_values("week")
    total = jump["total_streams"].sum()
    after_week_one = jump.loc[jump["week"].gt(1), "total_streams"].sum() / total

    st.subheader("JUMP · Release strategy overview")
    st.caption("First 28 days on Spotify Global Top 200 · July 11–August 7, 2025")
    with st.container(key="overview_metrics"):
        volume, sustained, market = st.columns(3)
        volume.metric("Global chart streams", f"{total / 1e6:.2f}M", border=True)
        sustained.metric("Share after week one", f"{after_week_one:.1%}", border=True)
        market.metric(
            f"{lead_city['stop']} edge",
            f"{lead_city['gain_vs_controls']:+.1f} places",
            help="Places gained in show week minus the median gain in comparison cities ranked in both weeks.",
            border=True,
        )

    timing, geography = st.columns(2, gap="medium")
    with timing:
        st.markdown("#### Global streams by release week")
        trend = go.Figure(go.Bar(
            x=[f"Week {week}" for week in jump["week"]], y=jump["total_streams"],
            marker=dict(color=[DEEP_ROSE] + [LOGO_PINK] * (len(jump) - 1),
                        line=dict(color=DEEP_ROSE, width=1)),
            text=[f"{streams / 1e6:.1f}M" for streams in jump["total_streams"]],
            textposition="outside", hovertemplate="%{x} · %{y:,.0f} chart streams<extra></extra>",
        ))
        trend.update_yaxes(range=[0, jump["total_streams"].max() * 1.18], tickformat="~s")
        trend.update_xaxes(showgrid=False, fixedrange=True)
        trend.update_layout(height=258, margin=dict(t=8, b=8, l=8, r=10))
        st.plotly_chart(trend, width="stretch", config={"displayModeBar": False})
        st.markdown(
            "**Keep day 28 in the review.** Use days 1 and 7 to assess launch scale, "
            "then day 28 to measure how much listening continued after launch week."
        )

    with geography:
        st.markdown("#### Show-week change in city rank")
        cities = go.Figure()
        for name, column, color in (
            ("Tour city", "rank_gain", DEEP_ROSE),
            ("Control median", "control_median_gain", COMPARISON_GRAY),
        ):
            cities.add_bar(
                x=tour[column], y=tour["stop"], name=name, orientation="h", marker_color=color,
                hovertemplate="%{y} · %{x:+g} places<extra>%{fullData.name}</extra>",
            )
        cities.update_xaxes(title_text="Places gained", rangemode="tozero")
        cities.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
        cities.update_layout(
            barmode="group", height=258, margin=dict(t=8, b=8, l=8, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, borderwidth=0),
        )
        st.plotly_chart(cities, width="stretch", config={"displayModeBar": False})
        st.markdown(
            f"**Prioritize {lead_city['stop']} for a follow-up test.** The track rose from #{lead_city['before_rank']:.0f} "
            f"to #{lead_city['show_rank']:.0f} while Global chart streams fell "
            f"{abs(lead_city['global_week_change_pct']):.1f}% that week."
        )
        st.caption("City ranks show chart position only. The comparison cannot establish incremental streams or tour impact.")

    st.stop()

if view == "City charts":
    summary = pd.read_csv(os.path.join(DATA_DIR, "jump_city_summary.csv"))
    cities = pd.read_csv(os.path.join(DATA_DIR, "jump_city_comparisons.csv"))
    sources = pd.read_csv(os.path.join(PROJECT_DATA, "jump_city_chart_observations.csv"))
    stop = st.selectbox("DEADLINE tour stop", summary["stop"])
    event = summary.loc[summary["stop"].eq(stop)].iloc[0]
    details = cities[cities["stop"].eq(stop)].copy()
    st.subheader("JUMP on the Spotify City Top 100")
    st.caption("Three Friday–Thursday chart weeks in UTC. Rank 1 is highest.")

    def display_rank(value):
        return f"#{int(value)}" if pd.notna(value) else "Outside Top 100"

    local_col, global_col, controls_col = st.columns(3)
    gain = event["rank_gain"]
    local_col.metric(
        "Tour city · show week", display_rank(event["show_rank"]),
        f"{gain:+.0f} ranks vs. prior week" if pd.notna(gain) else None,
    )
    global_col.metric("Global chart streams", f"{event['global_show_streams'] / 1e6:.2f}M",
                      f"{event['global_week_change_pct']:+.1f}% vs. prior week")
    reference = event["control_median_gain"]
    controls_col.metric("Control median rank change", f"{reference:+g} ranks" if pd.notna(reference) else "—",
                        f"{event['control_count']:.0f} controls ranked in both weeks", delta_color="off")

    rank_columns = ["before_rank", "show_rank", "after_rank"]
    weeks = [event["before_week_end"], event["show_week_end"], event["after_week_end"]]
    plot = go.Figure()
    for i, row in enumerate(details.itertuples()):
        ranks = [getattr(row, key) for key in rank_columns]
        if all(pd.isna(value) for value in ranks):
            continue
        local = row.role == "tour"
        plot.add_scatter(
            x=[0, 1, 2], y=ranks, name=row.city, mode="lines+markers",
            line={"color": DEEP_ROSE if local else [INK, COMPARISON_GRAY][i % 2],
                  "width": 4 if local else 2, "dash": "solid" if local else "dash"},
            connectgaps=False, hovertemplate=f"{row.city} · Rank %{{y}}<extra></extra>",
        )
    plot.add_vrect(x0=0.65, x1=1.35, fillcolor=BLUSH, opacity=0.65, line_width=0, layer="below")
    plot.update_xaxes(tickvals=[0, 1, 2], ticktext=[f"{label}<br>{week}" for label, week in
                      zip(("Prior week", "Show week", "Next week"), weeks)], range=[-0.2, 2.2])
    plot.update_yaxes(title="City chart rank", range=[103, 0])
    plot.update_layout(height=340, margin={"t": 20}, legend={"orientation": "h"})
    st.plotly_chart(plot, width="stretch")

    details[rank_columns] = details[rank_columns].apply(lambda column: column.map(display_rank))
    details["role"] = details["role"].map({"tour": "Tour city", "control": "Control", "backup": "Backup control"})
    st.dataframe(
        details[["city", "role", *rank_columns, "rank_gain"]], hide_index=True, width="stretch",
        column_config={"city": "City", "role": "Role", "before_rank": "Prior week", "show_rank": "Show week",
                       "after_rank": "Next week", "rank_gain": "Ranks gained in show week"},
    )
    st.caption(
        "City ranks measure position relative to other songs. The city charts supply no stream counts. "
        "Control changes use cities ranked in both weeks. The Global percentage comes from chart streams."
    )
    city_source = sources[sources["stop"].eq(stop) & sources["role"].eq("tour") & sources["period"].eq("show")].iloc[0]
    st.markdown(f"[Open the show-week City Top Songs chart]({city_source['source_url']})")
    st.stop()

if view == "Peer benchmark":
    peers = pd.read_csv(os.path.join(DATA_DIR, "peer_daily.csv"))
    weeks = pd.read_csv(os.path.join(DATA_DIR, "peer_weekly.csv"))
    windows = pd.read_csv(os.path.join(DATA_DIR, "jump_tour_windows.csv"))
    st.subheader("JUMP and comparable Friday releases")
    st.caption("Spotify Global Top 200 · Day 0 is release day · Each track’s first-week daily average equals 100.")
    extended = False
    if peers["cohort"].eq("sensitivity").any():
        extended = st.checkbox("Include the later collaboration as a sensitivity check")
    shown = peers if extended else peers[peers["cohort"].ne("sensitivity")]
    figure = px.line(
        shown, x="day", y="week_one_index", color="title", markers=True,
        labels={"day": "Days since release", "week_one_index": "Week-one index", "title": "Track"},
        hover_data={"artist": True, "chart_date": True, "streams": ":,.0f", "rank": True},
        color_discrete_map={
            "JUMP": INK, "Gabriela": DEEP_ROSE, "Dirty Work": "#8C46A1",
            "THIS IS FOR": COMPARISON_GRAY, "SPAGHETTI": "#256C8D",
        },
    )
    figure.update_traces(connectgaps=False)
    figure.update_traces(line_dash="dash", selector={"name": "SPAGHETTI"})
    event_points = shown[shown["cohort"].eq("target")].merge(windows, left_on="day", right_on="event_day")
    figure.add_scatter(
        x=event_points["day"], y=event_points["week_one_index"], text=event_points["city"],
        mode="markers", name="Tour stop starts",
        marker={"size": 10, "color": DEEP_ROSE, "symbol": "diamond"},
        hovertemplate="%{text} · Day %{x}<extra></extra>",
    )
    figure.update_xaxes(dtick=3, range=[-0.4, 27.4])
    figure.update_yaxes(rangemode="tozero")
    figure.update_layout(height=400, legend_title_text=None, margin=dict(t=18))
    st.plotly_chart(figure, width="stretch")
    st.caption("Gaps mean the track was outside the Top 200 or the source snapshot was unavailable or incomplete. The table shows charted days.")
    week_rows = weeks if extended else weeks[weeks["cohort"].ne("sensitivity")]
    st.dataframe(
        week_rows[["artist", "title", "week", "days_charted", "total_streams", "week_one_pct"]],
        width="stretch", hide_index=True,
        column_config={
            "artist": "Artist", "title": "Track", "week": "Release week",
            "days_charted": "Charted days out of 7",
            "total_streams": st.column_config.NumberColumn("Streams (complete weeks)", format="localized"),
            "week_one_pct": st.column_config.NumberColumn("% of week one", format="%.1f"),
        },
    )
    st.subheader("DEADLINE tour windows")
    st.caption("Change from the two preceding UTC days to the first show’s UTC day and the next day. Peers use the same release ages and weekdays.")
    prefix = "extended" if extended else "near"
    window_rows = windows[[
        "city", "event_utc", "event_day", "jump_change_pct",
        f"{prefix}_count", f"{prefix}_median_pct", f"{prefix}_gap_pp",
    ]]
    st.dataframe(
        window_rows, width="stretch", hide_index=True,
        column_config={
            "city": "Tour stop", "event_utc": "First show (UTC)", "event_day": "Release day",
            "jump_change_pct": st.column_config.NumberColumn("JUMP change (%)", format="%+.1f"),
            f"{prefix}_count": "Eligible peers",
            f"{prefix}_median_pct": st.column_config.NumberColumn("Peer change (%)", format="%+.1f"),
            f"{prefix}_gap_pp": st.column_config.NumberColumn("Gap (percentage points)", format="%+.1f"),
        },
    )
    st.caption(
        "A gap requires at least two peers with all four days charted. The Los Angeles before-window includes release day. "
        "Global daily totals combine many markets and promotions, so these comparisons are descriptive."
    )
    st.stop()

if view == "Events & search interest":
    sources = pd.read_csv(os.path.join(PROJECT_DATA, "google_trends_sources.csv"))
    trends = pd.read_csv(os.path.join(PROJECT_DATA, "google_trends_daily.csv"))
    events = pd.read_csv(os.path.join(PROJECT_DATA, "verified_release_events.csv"))
    case_name = st.selectbox("Case study", sources["case_name"])
    source = sources.loc[sources["case_name"].eq(case_name)].iloc[0]
    interest = trends[trends["case_id"].eq(source["case_id"])].copy()
    event_rows = events[events["track_id"].eq(source["track_id"])].merge(
        interest[["date", "interest"]], left_on="event_date", right_on="date", validate="many_to_one",
    )
    interest["date"] = pd.to_datetime(interest["date"])
    fig = px.line(
        interest, x="date", y="interest", title=f"Search interest · {source['geo']}",
        labels={"date": "UTC date", "interest": "Google Trends index"},
    )
    fig.add_scatter(
        x=pd.to_datetime(event_rows["event_date"]), y=event_rows["interest"],
        mode="markers", name="Verified events", text=event_rows["event_name"],
        marker={"size": 10, "color": DEEP_ROSE, "symbol": "diamond"},
        hovertemplate="%{text}<br>%{x|%b %d}: %{y}<extra></extra>",
    )
    fig.update_yaxes(range=[0, 105], dtick=25)
    fig.update_layout(height=400, margin=dict(t=50))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Google Trends · {source['query']} search term · {source['start_date']} to {source['end_date']}. "
        "Each geography and date window has its own 0–100 scale. The series measures relative search interest."
    )
    for event in event_rows.sort_values("event_date").itertuples():
        local = f" · {event.local_date} local" if event.local_date != event.event_date else ""
        st.markdown(f"**{event.event_date} UTC{local} · {event.interest}** — [{event.event_name}]({event.source_url})")
    st.caption("The series shows timing around events. Several releases and promotions can overlap within the same window.")
    st.markdown(f"[Open the Google Trends series]({source['source_url']})")

    chart_market = {"Worldwide": "Global", "United States": "US"}[source["geo"]]
    daily = pd.read_csv(os.path.join(DATA_DIR, "release_daily.csv"))
    chart = daily[daily["track_id"].eq(source["track_id"]) & daily["market"].eq(chart_market)].copy()
    chart = chart[chart["chart_date"].between(source["start_date"], source["end_date"])]
    available = chart.loc[chart["status"].ne("snapshot_missing"), "chart_date"]
    chart["chart_date"] = pd.to_datetime(chart["chart_date"])
    st.subheader("Spotify chart streams over the same dates")
    if available.empty:
        st.info("There are no Spotify snapshots for this selection.")
    else:
        fig = px.line(
            chart, x="chart_date", y="streams", markers=True,
            labels={"chart_date": "UTC date", "streams": "Chart streams"},
            hover_data={"rank": True, "day_index": True},
        )
        fig.update_traces(connectgaps=False)
        chart_events = chart.dropna(subset=["streams"]).merge(
            event_rows.assign(chart_date=pd.to_datetime(event_rows["event_date"]))[
                ["chart_date", "event_name"]
            ],
            on="chart_date", validate="one_to_one",
        )
        fig.add_scatter(
            x=chart_events["chart_date"], y=chart_events["streams"],
            mode="markers", name="Verified events", text=chart_events["event_name"],
            marker={"size": 10, "color": DEEP_ROSE, "symbol": "diamond"},
            hovertemplate="%{text}<br>%{x|%b %d}: %{y:,.0f}<extra></extra>",
        )
        fig.update_xaxes(range=[source["start_date"], source["end_date"]])
        fig.update_yaxes(rangemode="tozero")
        fig.update_layout(height=340, margin=dict(t=20))
        st.plotly_chart(fig, width="stretch")
        st.caption(
            f"{chart_market} chart snapshots available for {len(available)} dates, "
            f"{available.min()} through {available.max()}. Dates without data appear as gaps. "
            "Search interest and chart streams use separate units."
        )
    st.stop()

if view != "Research detail":
    daily = pd.read_csv(os.path.join(DATA_DIR, "release_daily.csv"))
    events = pd.read_csv(os.path.join(PROJECT_DATA, "verified_release_events.csv"))
    releases = metrics.sort_values("release_date", ascending=False)["track_name"].unique().tolist()
    market_names = {"Global": "Global", "US": "United States", "ID": "Indonesia"}
    if view == "Release comparison":
        left, center, right = st.columns(3)
        primary = left.selectbox("Release", releases)
        comparison_options = [r for r in releases if r != primary]
        default_comparison = comparison_options.index("Pink Venom") if primary == "Jump" else 0
        comparison = center.selectbox("Compare with", comparison_options, index=default_comparison)
        market = right.selectbox("Chart", MARKET_ORDER, format_func=market_names.get)
        selected = metrics[metrics["track_name"].isin([primary, comparison]) & metrics["market"].eq(market)]
        labels = [primary, comparison]
        series = "track_name"
        st.subheader("First seven days")
    else:
        primary = st.selectbox("Release", releases)
        selected = metrics[metrics["track_name"].eq(primary)]
        labels = MARKET_ORDER
        series = "market"
        st.subheader("Performance by chart")

    def show_number(value, format_spec):
        return format(value, format_spec) if pd.notna(value) else "—"

    for column, label in zip(st.columns(len(labels)), labels):
        row = selected.loc[selected[series].eq(label)].iloc[0]
        with column:
            st.markdown(f"**{market_names.get(label, label)}**")
            st.metric("Seven-day chart streams", show_number(row["first_week_streams"], ",.0f"))
            st.caption(
                f"Best rank {show_number(row['best_rank'], '.0f')} · "
                f"Day 6 vs. peak {show_number(row['retention_day6_vs_peak'], '.1%')} · "
                f"{row['days_charted']}/7 days charted"
            )

    scale = st.radio("Display", ["Chart streams", "% of seven-day peak"], horizontal=True)
    series_data = daily[daily["day_index"].between(0, 6)].merge(
        selected[["track_id", "market", "peak_streams_calc", "days_charted"]],
        on=["track_id", "market"], validate="many_to_one",
    )
    series_data["plot_value"] = series_data["streams"]
    if scale == "% of seven-day peak":
        series_data["plot_value"] = (
            series_data["streams"] / series_data["peak_streams_calc"]
        ).where(series_data["days_charted"].eq(7))
    if view == "Market breakdown":
        series_data["market"] = series_data["market"].map(market_names)
        labels = [market_names[label] for label in labels]
    series_data = series_data.sort_values("day_index")
    fig = px.line(
        series_data, x="day_index", y="plot_value", color=series,
        category_orders={series: labels}, markers=True,
        labels={"day_index": "Days since release", "plot_value": scale, series: "Series"},
        hover_data={"chart_date": True, "rank": True, "streams": ":,.0f"},
    )
    fig.update_traces(connectgaps=False)
    fig.update_xaxes(dtick=1, range=[-0.15, 6.15])
    fig.update_yaxes(rangemode="tozero")
    if scale == "% of seven-day peak":
        fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
    fig.update_layout(height=410, legend_title_text=None, margin=dict(t=16))
    st.plotly_chart(fig, width="stretch")
    st.caption("Seven-day totals and Day 6 vs. peak use complete windows. Gaps indicate dates outside the chart or unavailable snapshots. The Global chart overlaps the country charts.")

    event_rows = events[events["track_id"].isin(selected["track_id"])].merge(
        selected[["track_id", "track_name", "release_date"]].drop_duplicates(),
        on="track_id", validate="many_to_one",
    )
    if not event_rows.empty:
        st.subheader("Verified release events")
        event_rows["day"] = (pd.to_datetime(event_rows["event_date"]) - pd.to_datetime(event_rows["release_date"])).dt.days
        for row in event_rows.sort_values("event_date").itertuples():
            st.markdown(f"**{row.event_date} UTC · Day {row.day:+d}** — [{row.event_name}]({row.source_url}) · {row.market}")
        st.caption("The timeline records event dates. Exposure size and event lift require separate evidence.")
    st.stop()

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

        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=40, b=10),
            coloraxis=dict(
                colorscale=PINK_SCALE,
                cmin=0.0,
                cmax=1.0,
            )
        )

        st.plotly_chart(fig, use_container_width=True)
# 3) Bar — Main vs Pre gap
with row1[2]:
    st.subheader("Main − Pre Gap (avg ERR-6)")
    if not {"Main", "Pre"}.issubset(sel_anchor):
        st.info("Select both release types to compare Main and Pre.")
    elif gap.empty or "main_minus_pre" not in gap.columns:
        st.info("No comparable Main and Pre groups.")
    else:
        gap_f = gap.copy()
        if "era" in gap_f.columns and "market" in gap_f.columns:
            gap_f = gap_f[gap_f["market"].isin(sel_markets) & gap_f["era"].isin(sel_era)].copy()

        if gap_f.empty:
            st.info("No comparable Main and Pre groups for this selection.")
        else:
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
        plot_df = df.dropna(subset=["peak_streams_calc", "retention_day6_vs_peak", "day6_streams"]).copy()
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
