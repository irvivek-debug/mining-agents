-- radio_communications records one row per transmission. The query groups by
-- an operational shift bucket derived from the timestamp hour so the caller
-- can assess whether emergency traffic concentrates in a particular part of
-- the day. The shift bucket boundaries (06:00, 14:00, 22:00) reflect a
-- standard three-shift roster; if the site uses a different roster boundary,
-- the buckets should be adjusted before drawing any shift-pattern conclusion.
-- mean_sentiment_score is the mean of the sentiment_score column for all
-- transmissions in each bucket; it is a mean over recorded transcripts, not
-- a human-assessed distress rating. transmission_count and emergency_count
-- are reported so the caller can assess the cell size in each bucket.
SELECT
  CASE
    WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 6 AND 13  THEN 'day'
    WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 14 AND 21 THEN 'afternoon'
    ELSE                                                      'night'
  END AS shift_bucket,
  COUNT(*) AS transmission_count,
  COUNT(CASE WHEN emergency_keyword_flag = true THEN 1 END) AS emergency_count,
  ROUND(AVG(sentiment_score), 4) AS mean_sentiment_score
FROM `mining_data.radio_communications`
GROUP BY shift_bucket
ORDER BY shift_bucket
