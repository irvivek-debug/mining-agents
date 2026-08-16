-- Parts whose stock_level is strictly below their reorder_point_limit.
-- stock_level = reorder_point_limit means the part is exactly at the trigger
-- boundary, not below it, and is not reported here; the site's standard
-- (MAINT-WOP-002 clause 4) specifies the procurement action required when
-- a lead time exceeds 14 days or 45 days respectively.
-- Columns are named for what each number actually is.
SELECT
  part_number,
  part_description,
  stock_level,
  reorder_point_limit,
  lead_time_days,
  unit_price_usd
FROM `mining_data.inventory_levels`
WHERE stock_level < reorder_point_limit
ORDER BY stock_level ASC, lead_time_days DESC
