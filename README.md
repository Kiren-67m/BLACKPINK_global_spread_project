BLACKPINK Global Spotify Diffusion Analysis

This project analyzes early-stage streaming diffusion patterns of BLACKPINK releases on Spotify and examines whether the structure of diffusion stability shifts across historical eras.

Rather than measuring total scale or long-term popularity, the study focuses on early post-release retention behavior within a fixed 7-day window (Day 0–Day 6).
The core metric used is ERR-6 (Early Retention Ratio):

ERR-6 = Streams on Day 6 / Peak streams within the first 7 days

This metric serves as a proxy for early diffusion durability, capturing whether initial attention stabilizes or decays rapidly after peak exposure.

⸻

Research Motivation

For globally dominant artists like BLACKPINK, releases often peak immediately upon launch.
Under such conditions, the analytical question shifts from:

“Can attention be generated?”

to:

“Does attention stabilize after the initial burst?”

This project explores whether diffusion behavior evolves from event-driven volatility toward structure-supported stability, as BLACKPINK’s global presence matures across platforms, markets, and release strategies.

⸻

Scope & Design

Anchor-Based Analysis

The analysis is deliberately restricted to a small, theoretically motivated set of anchor tracks rather than the full discography.
Each anchor represents a structural role within a release cycle (Main vs Pre-release) and is mapped to a broader historical era.
	•	Time window: Day 0 – Day 6 post-release
	•	Markets analyzed: Global, United States, Indonesia
	•	Unit of analysis: Track × Market × Release

Historical Eras (Interpretive Framework)

Era labels are used for structural interpretation, not causal inference:
	•	Early Globalization (2017–2019)
	•	Streaming Expansion (2020–2021)
	•	Born Pink Upgrade (2022)
	•	Post-Tour Maintenance (2025)

⸻

Core Metric

ERR-6 (Early Retention Ratio)
	•	Captures early-stage diffusion durability
	•	Normalizes across vastly different streaming scales
	•	Enables cross-era and cross-market comparison

Interpretation note:
Higher ERR-6 values indicate slower post-peak normalization, not necessarily higher popularity.

⸻

Key Outputs

1. Interactive Dashboard (Primary Deliverable)

A Streamlit dashboard enabling interactive exploration of:
	•	ERR-6 distributions by market and anchor type
	•	Era × market retention heatmaps
	•	Main vs Pre-release retention gaps
	•	Scale vs stability relationships (Peak streams vs ERR-6)
	•	Era-level trend comparisons

Location:

dashboard/app.py

2. Static Dashboard Snapshot (PDF)

A fixed visual export for submission, sharing, or archival purposes.

Location:

report/BLACKPINK_Spotify_Diffusion_Dashboard.pdf

3. Research Log (Narrative Layer)

A structured research document explaining:
	•	Metric rationale
	•	Anchor selection logic
	•	Era interpretation
	•	Structural breakpoint discussion

Location:

report/BLACKPINK_Global_Spread_Research_Log.docx


⸻

Project Structure

BLACKPINK_global_spread_project/
│
├─ analysis/                # Computation layer (one-time metric construction)
│   ├─ 01_load_master_timeline.ipynb
│   └─ 02_metrics_ERR6.ipynb
│
├─ dashboard/               # Presentation layer (interactive)
│   ├─ app.py
│   └─ data/                # Exported, dashboard-ready datasets
│
├─ data/                    # Source & intermediate data
│   ├─ spotify_charts/      # Daily Spotify chart CSVs
│   ├─ master_timeline.csv
│   └─ group_release_anchor_config.csv
│
├─ report/                  # Narrative & static outputs
│   ├─ BLACKPINK_Global_Spread_Research_Log.docx
│   └─ BLACKPINK_Spotify_Diffusion_Dashboard.pdf
│
└─ README.md


⸻

Reproducibility (Minimal)

This project is designed with a clean separation between computation and presentation.

To reproduce the dashboard:
	1.	Run the analysis notebooks once to generate dashboard datasets:
	•	metrics_with_era.csv
	•	era_market_anchor_summary.csv
	•	main_vs_pre_gap.csv
	2.	Ensure the files are placed in:

dashboard/data/


	3.	Launch the dashboard:

streamlit run dashboard/app.py



⸻

Methodological Notes
	•	The analysis does not claim causal inference
	•	Era segmentation is used for structural interpretation
	•	Retention patterns are treated as signals of diffusion environment changes
	•	Solo releases and collaborations are used only for contextual interpretation, not metric computation

⸻

Why This Project Matters

This project demonstrates how platform-level diffusion dynamics can evolve independently of scale, and how early retention metrics can reveal structural maturity in global attention systems.

The framework is adaptable to:
	•	Other global artists
	•	Product launches
	•	App adoption events
	•	Viral content diffusion studies

This project was developed with the assistance of AI tools for coding and drafting, while all research design, metric choices, and interpretations were guided and validated by the author.
