"""Build the 28-day Global chart peer comparison and release-age event windows."""

import argparse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median
from zoneinfo import ZoneInfo

from rebuild_release_data import ROOT, read_csv, write_csv


def complete_mean(rows):
    values = [row["streams"] for row in rows]
    return mean(values) if values and all(value is not None for value in values) else None


def build(chart_dir, output_dir):
    releases = read_csv(ROOT / "data/peer_releases.csv")
    stops = read_csv(ROOT / "data/jump_tour_stops.csv")
    if len({row["track_id"] for row in releases}) != len(releases) or sum(row["cohort"] == "target" for row in releases) != 1:
        raise ValueError("Expected unique release IDs and exactly one target.")
    charts = {}
    series = {}
    weekly = []
    for release in releases:
        first = date.fromisoformat(release["release_date"])
        if first.weekday() != 4:
            raise ValueError(f"Expected a Friday release: {release['title']}")
        uris = set(release["uris"].split("|"))
        daily = []
        for age in range(28):
            chart_date = first + timedelta(days=age)
            filename = f"regional-global-daily-{chart_date}.csv"
            if filename not in charts:
                path = chart_dir / filename
                rows = read_csv(path) if path.is_file() else None
                ranks = [int(row["rank"]) for row in rows or []]
                if rows is not None and (
                    not ranks or ranks != sorted(set(ranks)) or ranks[0] < 1 or ranks[-1] > 200
                    or any(int(row["streams"]) <= 0 for row in rows)
                ):
                    raise ValueError(f"Invalid Top 200 rows in {filename}")
                charts[filename] = rows
            rows = charts[filename]
            matches = [row for row in rows or [] if row["uri"] in uris]
            if len(matches) > 1:
                raise ValueError(f"Multiple mapped versions for {release['title']} in {filename}")
            row = matches[0] if matches else None
            status = "snapshot_missing" if rows is None else "off_chart" if len(rows) == 200 else "snapshot_partial"
            if row:
                status = "charted"
            daily.append({
                "track_id": release["track_id"], "artist": release["artist"], "title": release["title"],
                "cohort": release["cohort"], "day": age, "chart_date": str(chart_date),
                "streams": int(row["streams"]) if row else None, "rank": int(row["rank"]) if row else None,
                "status": status,
                "uri": row["uri"] if row else None, "snapshot": filename,
            })
        first_week = complete_mean(daily[:7])
        if first_week is None or first_week <= 0:
            raise ValueError(f"Complete positive week-one baseline required for {release['title']}")
        for row in daily:
            row["week_one_index"] = 100 * row["streams"] / first_week if row["streams"] is not None else None
        series[release["track_id"]] = daily
        for week in range(4):
            days = daily[week * 7:(week + 1) * 7]
            avg = complete_mean(days)
            weekly.append({
                "artist": release["artist"], "title": release["title"], "cohort": release["cohort"],
                "week": week + 1, "days_charted": sum(day["status"] == "charted" for day in days),
                "snapshots": sum(day["status"] != "snapshot_missing" for day in days),
                "total_streams": int(round(7 * avg)) if avg is not None else None,
                "week_one_pct": 100 * avg / first_week if avg is not None else None,
            })

    target = next(release for release in releases if release["cohort"] == "target")
    target_start = date.fromisoformat(target["release_date"])
    windows = []
    for stop in stops:
        def utc_date(field):
            local = datetime.fromisoformat(stop[field]).replace(tzinfo=ZoneInfo(stop["timezone"]))
            return local.astimezone(timezone.utc).date()

        first_utc = utc_date("first_show_local")
        age = (first_utc - target_start).days
        if age < 2 or age + 1 >= 28:
            continue
        changes = {}
        for release in releases:
            daily = series[release["track_id"]]
            before, after = complete_mean(daily[age - 2:age]), complete_mean(daily[age:age + 2])
            if before is not None and after is not None:
                changes[release["track_id"]] = 100 * (after / before - 1)
        near = [changes[r["track_id"]] for r in releases if r["cohort"] == "near" and r["track_id"] in changes]
        extended = [changes[r["track_id"]] for r in releases if r["cohort"] in {"near", "sensitivity"} and r["track_id"] in changes]
        observed = changes[target["track_id"]]
        windows.append({
            "city": stop["city"], "local_first_show": stop["first_show_local"], "event_utc": str(first_utc),
            "last_show_utc": str(utc_date("last_show_local")), "event_day": age,
            "jump_change_pct": observed, "near_count": len(near), "near_median_pct": median(near) if near else None,
            "near_gap_pp": observed - median(near) if len(near) >= 2 else None,
            "extended_count": len(extended), "extended_median_pct": median(extended) if extended else None,
            "extended_gap_pp": observed - median(extended) if len(extended) >= 2 else None,
            "release_in_pre_window": age == 2, "source_url": stop["source_url"],
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    daily_rows = [row for rows in series.values() for row in rows]
    for filename, rows in (
        ("peer_daily.csv", daily_rows), ("peer_weekly.csv", weekly), ("jump_tour_windows.csv", windows),
    ):
        columns = tuple(rows[0])
        write_csv(output_dir / filename, columns, ([row[column] for column in columns] for row in rows))
    print(f"Rebuilt {len(releases)} releases × 28 days and {len(windows)} tour windows.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--charts", type=Path, default=ROOT / "data/spotify_charts")
    parser.add_argument("--output", type=Path, default=ROOT / "dashboard/data")
    args = parser.parse_args()
    build(args.charts, args.output)
