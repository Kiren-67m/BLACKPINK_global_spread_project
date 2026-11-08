"""Package the Streamlit app and its reviewed inputs for GitHub Pages."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
INPUTS = (
    "dashboard/app.py",
    "dashboard/data/era_market_anchor_summary.csv",
    "dashboard/data/jump_city_comparisons.csv",
    "dashboard/data/jump_city_summary.csv",
    "dashboard/data/jump_tour_windows.csv",
    "dashboard/data/main_vs_pre_gap.csv",
    "dashboard/data/metrics_with_era.csv",
    "dashboard/data/peer_daily.csv",
    "dashboard/data/peer_weekly.csv",
    "dashboard/data/release_daily.csv",
    "data/google_trends_daily.csv",
    "data/google_trends_sources.csv",
    "data/jump_city_chart_observations.csv",
    "data/verified_release_events.csv",
)


if __name__ == "__main__":
    config = (ROOT / "dashboard/.streamlit/config.toml").read_text(encoding="utf-8")
    output = ROOT / "docs/dashboard/dashboard.zip"
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as bundle:
        for path in INPUTS:
            bundle.writestr(path, (ROOT / path).read_bytes())
        bundle.writestr(".streamlit/config.toml", config + '\n[client]\ntoolbarMode = "viewer"\n')
