WITH cs AS (
  SELECT DATE(timestamp) AS d, AVG(gap_size_setting_mm) AS gap
  FROM `mining_data.crusher_states` GROUP BY d
),
m AS (
  SELECT DATE(timestamp) AS d, AVG(recovery_rate_pct) AS rec,
         AVG(feed_grade_pct) AS feed
  FROM `mining_data.metallurgical_recovery` GROUP BY d
),
j AS (
  SELECT m.d, m.rec, m.feed, cs.gap,
         NTILE(3) OVER (ORDER BY m.feed) AS feed_tercile
  FROM m JOIN cs USING (d)
)
SELECT
  feed_tercile,
  ROUND(MIN(feed), 3) AS feed_lo,
  ROUND(MAX(feed), 3) AS feed_hi,
  COUNTIF(gap <= @tight_max) AS tight_days,
  ROUND(AVG(IF(gap <= @tight_max, rec, NULL)), 2) AS recovery_tight,
  COUNTIF(gap >= @wide_min) AS wide_days,
  ROUND(AVG(IF(gap >= @wide_min, rec, NULL)), 2) AS recovery_wide
FROM j
GROUP BY feed_tercile
ORDER BY feed_tercile
