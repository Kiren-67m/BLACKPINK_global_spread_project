"""Rebuild the release dashboard tables from local Spotify Charts snapshots."""

import argparse
import csv
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
MARKETS = {"Global": "global", "US": "us", "ID": "id"}
ERAS = {
    2017: "Early Globalization",
    2018: "Early Globalization",
    2019: "Early Globalization",
    2020: "Streaming Expansion",
    2021: "Streaming Expansion",
    2022: "Born Pink Upgrade",
    2025: "Post-Tour Maintenance",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, headers, rows):
    temporary = path.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)
    temporary.replace(path)


def release_days(anchors, uri_mapping, chart_dir, days):
    uris_by_track = {}
    uri_owners = {}
    for row in uri_mapping:
        track_id, uri = row["track_id"], row["uri"]
        if not uri.startswith("spotify:track:") or len(uri.removeprefix("spotify:track:")) != 22:
            raise ValueError(f"Invalid Spotify track URI: {uri}")
        if uri in uri_owners:
            raise ValueError(f"Duplicate URI mapping: {uri}")
        uri_owners[uri] = track_id
        uris_by_track.setdefault(track_id, set()).add(uri)

    anchor_ids = [a["track_id"] for a in anchors]
    if len(set(anchor_ids)) != len(anchor_ids) or set(anchor_ids) != set(uris_by_track):
        raise ValueError("Each unique release must have a Spotify URI mapping.")

    snapshots = {}
    for anchor in anchors:
        track_id = anchor["track_id"]
        release_date = date(*(int(part) for part in anchor["release_date"].replace("/", "-").split("-")))
        era = anchor.get("era") or ERAS.get(release_date.year, "Unclassified")
        for market, market_code in MARKETS.items():
            for day_index in range(days):
                chart_date = release_date + timedelta(days=day_index)
                name = f"regional-{market_code}-daily-{chart_date}.csv"
                path = chart_dir / name
                if path not in snapshots:
                    snapshots[path] = read_csv(path) if path.is_file() else None
                    if snapshots[path] == []:
                        raise ValueError(f"{name} is an empty chart snapshot.")
                chart = snapshots[path]
                matches = [row for row in chart or [] if row["uri"] in uris_by_track[track_id]]
                if len(matches) > 1:
                    raise ValueError(f"{name} has multiple mapped rows for {track_id}; review versions before combining.")
                uri = rank = streams = None
                status = "snapshot_missing" if chart is None else "not_charted"
                if matches:
                    row = matches[0]
                    uri, rank, streams = row["uri"], int(row["rank"]), int(row["streams"])
                    if rank <= 0 or streams <= 0:
                        raise ValueError(f"Invalid rank or stream count for {track_id} in {name}.")
                    status = "charted"
                yield (
                    track_id, anchor["track_name"], market, anchor["anchor_type"], era,
                    release_date.isoformat(), chart_date.isoformat(), day_index,
                    uri, rank, streams, status, name,
                )


def build(chart_dir, output_dir, days):
    anchors = read_csv(ROOT / "group_release_anchor_config.csv")
    uri_mapping = read_csv(ROOT / "data/release_track_uris.csv")
    rows = list(release_days(anchors, uri_mapping, chart_dir, days))
    if not any(row[11] == "charted" for row in rows):
        raise ValueError(f"No mapped tracks found in {chart_dir}; exports were not changed.")

    with sqlite3.connect(":memory:") as db:
        db.execute("""
            CREATE TABLE release_daily (
                track_id TEXT, track_name TEXT, market TEXT, anchor_type TEXT, era TEXT,
                release_date TEXT, chart_date TEXT, day_index INTEGER, uri TEXT,
                rank INTEGER, streams INTEGER, status TEXT, source_snapshot TEXT,
                PRIMARY KEY (track_id, market, chart_date)
            )
        """)
        db.executemany("INSERT INTO release_daily VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        db.executescript((ROOT / "analysis/release_metrics.sql").read_text(encoding="utf-8"))
        daily = db.execute("SELECT * FROM release_daily ORDER BY track_id, market, day_index")
        metrics = db.execute("SELECT * FROM release_metrics ORDER BY track_id, market")
        summary = db.execute("""
            SELECT era, market, anchor_type, COUNT(retention_day6_vs_peak),
                   AVG(retention_day6_vs_peak)
            FROM release_metrics
            GROUP BY era, market, anchor_type
            ORDER BY era, market, anchor_type
        """)

        output_dir.mkdir(parents=True, exist_ok=True)
        for name, cursor in (("release_daily.csv", daily), ("metrics_with_era.csv", metrics)):
            write_csv(output_dir / name, [col[0] for col in cursor.description], cursor)

        summary_rows = []
        paired_means = {}
        for era, market, anchor_type, count, average in summary:
            ratios = [
                row[0] for row in db.execute(
                    """SELECT retention_day6_vs_peak FROM release_metrics
                       WHERE era = ? AND market = ? AND anchor_type = ?
                       AND retention_day6_vs_peak IS NOT NULL""", (era, market, anchor_type)
                )
            ]
            summary_rows.append((era, market, anchor_type, count, average, median(ratios) if ratios else None))
            paired_means.setdefault((era, market), {})[anchor_type] = average
        write_csv(
            output_dir / "era_market_anchor_summary.csv",
            ("era", "market", "anchor_type", "n_tracks", "avg_err6", "median_err6"),
            summary_rows,
        )
        write_csv(
            output_dir / "main_vs_pre_gap.csv",
            ("era", "market", "main_minus_pre"),
            (
                (era, market, means["Main"] - means["Pre"])
                for (era, market), means in paired_means.items()
                if means.get("Main") is not None and means.get("Pre") is not None
            ),
        )
        charted, complete = db.execute("""
            SELECT SUM(days_charted), SUM(days_charted = 7) FROM release_metrics
        """).fetchone()
    print(f"First week: {charted} charted release-market-days; {complete} complete windows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--charts", type=Path, default=ROOT / "data/spotify_charts")
    parser.add_argument("--output", type=Path, default=ROOT / "dashboard/data")
    parser.add_argument("--days", type=int, choices=(7, 28), default=7)
    args = parser.parse_args()
    build(args.charts, args.output, args.days)
