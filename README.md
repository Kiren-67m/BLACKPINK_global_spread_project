# BLACKPINK Release Performance

An independent music analytics case study. Compare the first seven days of eight selected BLACKPINK releases, then examine relative search interest around the 2019 Coachella performances and the 2025 JUMP rollout.

[Open the interactive dashboard](https://kiren-67m.github.io/BLACKPINK_global_spread_project/dashboard/) · [Read the English report](https://kiren-67m.github.io/BLACKPINK_global_spread_project/?view=1)

## Run the dashboard

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The dashboard runs from its reviewed data tables. It includes a release comparison, a 28-day peer benchmark, a city chart comparison, a market breakdown, two event case studies, and the original era and release-type views under **Research detail**. The [English HTML brief](docs/index.html) can be saved and opened offline.

GitHub Pages serves both views from `docs/`. The public dashboard runs the same `dashboard/app.py` in the browser with Stlite. After changing the dashboard or its reviewed inputs, run `python3 analysis/build_dashboard_bundle.py` to rebuild the Pages bundle.

## Rebuild the chart data

```bash
python3 analysis/rebuild_release_data.py --days 28 --charts /path/to/snapshots
python3 analysis/build_peer_benchmark.py --charts /path/to/snapshots
python3 analysis/build_city_comparison.py
```

The first two builders read daily Spotify Charts snapshots. Download the chart CSVs to a local directory and pass it to both builders. The builders expect filenames such as `regional-us-daily-2019-04-05.csv`. The historic notebooks preserve the original exploratory work. The dashboard and report use the reviewed exports included here.

| File | Grain and purpose |
| --- | --- |
| `group_release_anchor_config.csv` | One row per selected release |
| `data/release_track_uris.csv` | Maps project release IDs to observed Spotify track URIs |
| `dashboard/data/release_daily.csv` | Release × chart × UTC date, including out-of-chart and missing-snapshot states |
| `analysis/release_metrics.sql` | Week-one chart volume, peak, best rank, coverage and ERR-6 |
| `data/verified_release_events.csv` | Sourced events with UTC and local dates |
| `data/google_trends_daily.csv` | Daily relative search interest by case study |
| `data/google_trends_sources.csv` | Exact query, geography, window and source link for each search series |

The original 168 snapshots cover Day 0–6 for eight releases and three chart scopes. There are 152 charted release–chart–days and 21 complete seven-day windows out of 24. An additional 36 official snapshots extend Kill This Love in the U.S. through April 26, 2019, and JUMP on the Global chart through August 7, 2025. The event view plots those observations alongside Google Trends using separate scales. `Kill This Love` and `How You Like That` each use two observed URIs across their release windows. The builder raises an error if two mapped versions appear on the same chart date, so that case can be reviewed before any aggregation.

**ERR-6** is Day 6 chart streams divided by the highest daily chart streams in Day 0–6. The rebuilt dashboard reports ERR-6 and seven-day totals for complete windows. Global includes country activity, so treat the chart scopes as overlapping. Spotify Charts reports chart-eligible streams. Google Trends reports relative interest on its own 0–100 scale for each query and window. [Spotify Charts methodology](https://support.spotify.com/bn-en/artists/article/understanding-spotify-charts/) · [Google Trends methodology](https://support.google.com/trends/answer/4365533?hl=en)

## Compare release decay and tour windows

The near-release sample uses aespa, KATSEYE, and TWICE tracks released on Fridays within three weeks of JUMP. The optional sensitivity sample adds a later Friday release, LE SSERAFIM's SPAGHETTI featuring j-hope. The release dates, matching Spotify URIs, and official release references are in [peer_releases.csv](data/peer_releases.csv). Each track is indexed to its own average daily chart streams in Days 0–6. Weekly totals require all seven days on the chart. A missing snapshot, a partial snapshot, and a track outside a complete Top 200 are separate states.

The [official tour schedule](https://artist.ygfamily.com/ARTISTS/BLACKPINK/concert/2025TOUR/index.html) supplies scheduled local show times. The builder converts each to UTC to match [Spotify’s chart day](https://support.spotify.com/bn-en/artists/article/understanding-spotify-charts/). It compares the two days before each stop with its first UTC day and the next day. Peer comparisons use the same release ages, which also aligns weekdays. A median gap requires at least two peers with all four days charted. The Los Angeles baseline includes release day, and the small cohort, overlapping promotions, and global aggregation limit attribution.

## Compare city charts around tour stops

**City charts** compares the Friday–Thursday Spotify City Top 100 week containing each show with the weeks immediately before and after it. The local chart reports rank. The Global reference reports chart stream totals over the same UTC weeks. The [33 city-week observations](data/jump_city_chart_observations.csv) link back to their Spotify pages.

Chicago’s initial Midwest controls were Detroit and Minneapolis. JUMP was outside the Top 100 in both, so Dallas and Houston provide the numerical comparison as large Central Time markets with no scheduled stop. New York uses Philadelphia and Washington as East Coast controls, while Paris uses Lyon and Marseille as French metropolitan controls. The comparison uses the median rank gain among controls observed in both weeks. Ranks are relative to other songs in each city. Differences in the cities’ baseline rank and audiences limit event attribution.

## Next data collection

1. **Extend the market comparison.** Add city-level stream or listener counts for the tour and comparison markets.
2. **Expand the peer sample.** Use a prespecified list of comparable releases by artist, release type, era and market. For the pre-release window, use artist or catalogue activity.
3. **Test event and forecast hypotheses.** Compare event-aligned changes to pre-event trends and matched releases; track overlapping promotions and calendar effects. For forecasting, compare an early-stream baseline against simple decay or regression, holding out entire releases. Audience conversion, playlist attribution and commercial returns require first-party listener, placement or campaign data.

This project used AI tools for coding and drafting. Research design, metric choices and interpretations were guided and validated by the author.
