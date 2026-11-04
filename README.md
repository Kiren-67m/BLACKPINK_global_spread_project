# BLACKPINK Spotify Diffusion Analysis

An exploratory study of early streaming retention across release eras and markets, with a Streamlit dashboard and analysis notebooks.

## Research question

How does listening attention hold up after the initial release peak? The analysis compares selected anchor tracks across Global, US and Indonesia charts within Day 0–Day 6.

**ERR-6 = streams on Day 6 / highest daily streams within Day 0–Day 6.** A higher ratio indicates stronger retention relative to the initial peak; it does not measure total popularity.

The comparison uses four interpretive eras: Early Globalization (2017–2019), Streaming Expansion (2020–2021), Born Pink Upgrade (2022), and Post-Tour Maintenance (2025). Main releases and pre-releases are compared separately.

## Explore the dashboard

The three dashboard-ready CSVs are included, so the dashboard can run without rebuilding the notebooks.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

The dashboard supports market, release-type and era filters; retention distributions; era-by-market heatmaps; Main–Pre gaps; and peak-stream versus retention comparisons.

## Repository map

| Path | Purpose |
| --- | --- |
| `analysis/01_load_master_timeline.ipynb` | Timeline exploration |
| `analysis/02_metrics_ERR6.ipynb` | Metric construction |
| `dashboard/app.py` | Streamlit / Plotly dashboard |
| `dashboard/data/` | Three exported tables used by the dashboard |
| `master_timeline.csv` | Timeline table at the repository root |
| `group_release_anchor_config.csv` | Anchor-track configuration at the repository root |
| [Dashboard PDF](report/BLACKPINK%20Spotify%20Diffusion%20Dashboard.pdf) | Static dashboard snapshot |
| [Research log](report/BLACKPINK_Global_Spread_Research_Log.docx) | Metric rationale, anchor selection and interpretation |

## Reproducibility and limits

- The committed dashboard tables are sufficient to reproduce the dashboard view. The complete raw daily chart collection is not bundled; notebook execution may require the original source files and local-path adjustments.
- Anchor selection is small and deliberate, rather than representative of the full discography. Findings describe this sample.
- Era labels provide context. These comparisons do not identify causal effects of tours, marketing or platform changes.
- ERR-6 depends on the chosen seven-day window and chart coverage; it should be read alongside streaming scale.

This project used AI tools for coding and drafting. Research design, metric choices and interpretations were guided and validated by the author.
