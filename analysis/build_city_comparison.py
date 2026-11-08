"""Compare JUMP's City Top Songs rank around three DEADLINE tour stops."""

import argparse
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

from rebuild_release_data import ROOT, read_csv, write_csv


STOPS = ("Chicago", "New York", "Paris")
PERIODS = ("before", "show", "after")


def chart_week_end(local_time, zone):
    utc_day = datetime.fromisoformat(local_time).replace(tzinfo=ZoneInfo(zone)).astimezone(timezone.utc).date()
    return utc_day + timedelta(days=(3 - utc_day.weekday()) % 7)


def build(output):
    observations = read_csv(ROOT / "data/jump_city_chart_observations.csv")
    stops = {
        row["city"]: row for row in read_csv(ROOT / "data/jump_tour_stops.csv") if row["city"] in STOPS
    }
    jump = [row for row in read_csv(output / "peer_daily.csv") if row["track_id"] == "jump"]
    global_totals = defaultdict(list)
    for row in jump:
        chart_date = date.fromisoformat(row["chart_date"])
        end = chart_date + timedelta(days=(3 - chart_date.weekday()) % 7)
        global_totals[end].append(int(row["streams"]) if row["streams"] else None)

    by_stop = defaultdict(dict)
    for row in observations:
        city_rows = by_stop[row["stop"]].setdefault(row["city"], {})
        if row["period"] in city_rows or int(row["chart_rows"]) != 100:
            raise ValueError(f"Invalid chart observation for {row['city']} {row['week_end']}")
        city_rows[row["period"]] = row

    details = []
    summary = []
    for stop in STOPS:
        event = stops[stop]
        end = chart_week_end(event["first_show_local"], event["timezone"])
        if end != chart_week_end(event["last_show_local"], event["timezone"]):
            raise ValueError(f"{stop} shows span multiple chart weeks")
        dates = {period: end + timedelta(weeks=i - 1) for i, period in enumerate(PERIODS)}
        control_moves = []
        local_move = None
        local_ranks = None
        for city, periods in by_stop[stop].items():
            if set(periods) != set(PERIODS) or any(
                periods[period]["week_end"] != dates[period].isoformat() for period in PERIODS
            ):
                raise ValueError(f"Unexpected chart weeks for {city}")
            roles = {row["role"] for row in periods.values()}
            if roles not in ({"tour"}, {"control"}, {"backup"}):
                raise ValueError(f"Unexpected roles for {city}: {roles}")
            role = next(iter(roles))
            ranks = [int(periods[period]["rank"]) if periods[period]["rank"] else None for period in PERIODS]
            if any(rank is not None and not 1 <= rank <= 100 for rank in ranks):
                raise ValueError(f"Out-of-range rank for {city}")
            for i in (1, 2):
                prior = periods[PERIODS[i]]["previous_rank"]
                if ranks[i] is not None and prior.isdigit() and int(prior) != ranks[i - 1]:
                    raise ValueError(f"Previous rank disagrees with prior week for {city}")
            move = ranks[0] - ranks[1] if ranks[0] is not None and ranks[1] is not None else None
            if role == "tour":
                if local_ranks is not None:
                    raise ValueError(f"Multiple tour cities for {stop}")
                local_move, local_ranks = move, ranks
            elif move is not None:
                control_moves.append(move)
            details.append((stop, city, role, *ranks, move))
        if local_ranks is None:
            raise ValueError(f"No tour city observations for {stop}")

        before = global_totals[dates["before"]]
        during = global_totals[end]
        if len(before) != 7 or len(during) != 7 or None in before + during:
            raise ValueError(f"Expected two complete Global chart weeks for {stop}")
        reference = median(control_moves) if control_moves else None
        gap = local_move - reference if local_move is not None and reference is not None else None
        summary.append((
            stop, event["first_show_local"][:10], event["last_show_local"][:10],
            *(str(dates[period]) for period in PERIODS), *local_ranks, local_move,
            len(control_moves), reference, gap, sum(before), sum(during),
            100 * (sum(during) / sum(before) - 1),
        ))

    write_csv(
        output / "jump_city_comparisons.csv",
        ("stop", "city", "role", "before_rank", "show_rank", "after_rank", "rank_gain"),
        details,
    )
    write_csv(
        output / "jump_city_summary.csv",
        (
            "stop", "first_show_local", "last_show_local", "before_week_end", "show_week_end",
            "after_week_end", "before_rank", "show_rank", "after_rank", "rank_gain", "control_count",
            "control_median_gain", "gain_vs_controls", "global_before_streams", "global_show_streams",
            "global_week_change_pct",
        ),
        summary,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dashboard/data")
    build(parser.parse_args().output)
