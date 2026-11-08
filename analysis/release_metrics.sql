CREATE VIEW release_metrics AS
WITH week AS (
    SELECT *
    FROM release_daily
    WHERE day_index BETWEEN 0 AND 6
),
rollup AS (
    SELECT track_id, track_name, market, anchor_type, era, release_date,
           COUNT(streams) AS days_charted,
           SUM(status <> 'snapshot_missing') AS snapshots_available,
           COUNT(DISTINCT uri) AS chart_uri_count,
           MIN(rank) AS best_rank,
           MAX(streams) AS peak_streams_calc,
           MAX(CASE WHEN day_index = 6 THEN streams END) AS day6_streams,
           CASE WHEN COUNT(streams) = 7 THEN SUM(streams) END AS first_week_streams
    FROM week
    GROUP BY track_id, track_name, market, anchor_type, era, release_date
),
peaks AS (
    SELECT track_id, market, day_index, uri,
           ROW_NUMBER() OVER (
               PARTITION BY track_id, market ORDER BY streams DESC, day_index
           ) AS peak_order
    FROM week
    WHERE streams IS NOT NULL
)
SELECT r.track_id, p.uri, r.track_name, r.market, r.anchor_type, r.era,
       r.peak_streams_calc, r.day6_streams,
       CASE WHEN r.days_charted = 7
            THEN 1.0 * r.day6_streams / NULLIF(r.peak_streams_calc, 0)
       END AS retention_day6_vs_peak,
       r.release_date, r.days_charted, r.snapshots_available, r.chart_uri_count,
       r.best_rank, p.day_index AS peak_day, r.first_week_streams
FROM rollup r
LEFT JOIN peaks p ON r.track_id = p.track_id AND r.market = p.market AND p.peak_order = 1;
