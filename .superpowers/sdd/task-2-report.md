# Task 2 Report: Column Semantics for Asset, Telemetry, and Maintenance Tables

## Tables and columns described

### Section 1 (continued): Asset and Telemetry, APQC 11.0.3

#### mining_data.assets (8 columns)
- `current_state` — JSON object with the latest operating snapshot, keys and units asset-type-specific (vibration_hz, temperature_c, load_pct, rotational_speed_rpm for PUMP; rotational_speed_rpm, weight_tons, power_draw_mw, temperature_c for MILL; rotational_torque_nm, feed_rate_tph, gap_size_setting_mm, bypass_valve_open, temperature_c for CRUSHER; speed_kmh, payload_tons, engine_temp_c for TRUCK; speed_mps, belt_tension_kn, load_pct for CONVEYOR)
- `location_gis` — WKT POINT geometry (longitude, latitude) in decimal degrees, e.g. POINT(116.8510 -23.1205)
- `physics_parameters` — JSON of digital-twin calibration coefficients: friction_mu (dimensionless), alpha (wear/heat-generation rate, dimensionless), cooling_k (cooling rate constant, dimensionless)
- `criticality_rating` — Operational criticality class; values: CRITICAL, HIGH
- `asset_id` — Primary key; joins telemetry_stream, erp_work_orders, maintenance_logs, asset_dependencies, simulation_runs
- `installation_date` — Commission date, DATE type
- `asset_type` — Equipment category: PUMP, GRINDING_MILL, CRUSHER, HAUL_TRUCK, CONCONVEYOR
- `asset_name` — Human-readable display name

**Evidence:** Live BigQuery query — all 5 rows read in full, every column value inspected verbatim. No generator of record. Catalog: `supply_chain.py` `load_assets()` reads asset_id, asset_type, criticality_rating confirming those three columns' purposes. Catalog S01/S02 comment blocks name assets as the asset-registry backing cascading-failure and stockout traversals.

#### mining_data.asset_dependencies (4 columns)
- `impact_score` — Fraction of downstream feed supplied by the upstream asset, 0.0–1.0, dimensionless
- `dependency_type` — Class of dependency; only value: PHYSICAL_FEED (upstream delivers material directly to downstream)
- `target_id` — Downstream asset; joins assets.asset_id
- `source_id` — Upstream asset; joins assets.asset_id

**Evidence:** Live BigQuery query — all 3 rows read in full: CONVEYOR-02→CRUSHER-03 (score 0.9), CRUSHER-03→MILL-01 (score 0.95), MILL-01→PUMP-104A (score 0.8). All values inspected directly. Catalog: S01 comment block names asset_dependencies as the table the blast-radius traversal walks. No generator of record.

#### mining_data.simulation_runs (6 columns)
- `projected_cooling_curve` — JSON array of {time_sec, temp_c} points at 0, 30, 60, 90, 120 seconds post-action (temperature in degrees Celsius)
- `asset_id` — Asset this simulation ran for; only CRUSHER-03, MILL-01, PUMP-104A have rows
- `recalculated_parameters` — JSON with friction_mu (dimensionless) updated by the simulation
- `nba_executed` — Next-best-action recorded: CLEAR_APERTURE_OBSTRUCTION, INJECT_LUBRICANT, SLOW_FEED_RATE, SHUTDOWN_CIRCUIT
- `timestamp` — Instant the simulation run was triggered, UTC; the table's only time column
- `run_id` — Primary key, e.g. SIM-110001

**Evidence:** Live BigQuery queries — 150 rows profiled; `DISTINCT nba_executed` (4 values confirmed), `DISTINCT asset_id` (3 assets), 3 sample rows with full JSON values inspected, timestamp range confirmed 2026-01-01 to 2026-06-17. No generator of record. Catalog: D06 "Digital Twin Simulation Replay Analyst" names simulation_runs as its sole source table.

---

### Section 2: Maintenance and Work Management, APQC 11.0.3 and 4.1.2

#### mining_data.erp_work_orders (7 columns)
- `created_at` — Timestamp the work order was raised, UTC; spans 2026-01-01 to 2026-06-17; the table's only time column
- `repair_cost` — Total cost in USD: labour ($150/h × crew × duration) + parts + mobilisation ($150 × crew). Range $630–$17,730
- `description` — Operator-authored free text (in FREE_TEXT_FIELDS); treated as untrusted input by the agent runtime
- `work_order_id` — Primary key, e.g. WO-990001; joins maintenance_logs and work_order_parts_edge
- `priority` — Urgency class: CRITICAL, HIGH, MEDIUM, LOW; drives crew size and therefore labour cost
- `status` — Lifecycle state: OPEN, IN_PROGRESS, COMPLETED, CANCELLED; only COMPLETED orders have a matching maintenance_logs row
- `asset_id` — Asset this work order is raised against; joins assets.asset_id

**Evidence:** `data/generator/maintenance.py` is the authority — LABOUR_RATE=150, MOB_BASE=150, CREW_SIZE dict (CRITICAL 6, HIGH 4, MEDIUM 3, LOW 2) are design parameters stated explicitly in module docstring and code (lines 79–90). Cost formula in `generate_work_orders()` (lines 488–495). Distinct priority and status values confirmed by live BigQuery `DISTINCT` queries. Cost range ($630 min, $17,730 max) confirmed by `MIN`/`MAX` query. `mining_agents/safety/untrusted.py` `FREE_TEXT_FIELDS` lists `erp_work_orders.description`.

#### mining_data.maintenance_logs (6 columns)
- `parts_replaced` — ARRAY<STRING> of SKU codes consumed; empty for 26 of 152 logs; elements match work_order_parts_edge.part_number and inventory_levels.part_number
- `log_entry_id` — Primary key, e.g. LOG-8801
- `actual_duration_hours` — Hours from crew mobilisation to job completion; range 1–19 h, mean ~9.9 h; drives repair_cost in erp_work_orders
- `asset_id` — Asset the maintenance was performed on; joins assets.asset_id
- `technician_notes` — Operator-authored free text (in FREE_TEXT_FIELDS); treated as untrusted input; currently five distinct boilerplate values, one per asset
- `work_order_id` — Joins erp_work_orders.work_order_id; every log row maps to exactly one COMPLETED work order

**Evidence:** `data/generator/maintenance.py` — `generate_maintenance_logs()` docstring (lines 505–543) states actual_duration_hours is an identity passthrough of original values, range [1, 19] h, mean 9.944 h. `_as_parts_list()` (line 206) confirms parts_replaced is a REPEATED STRING column. `_fetch_source_tables()` SQL (lines 188–198) enumerates all six column names in schema order. Live BigQuery: `COUNTIF(ARRAY_LENGTH(parts_replaced) = 0)` = 26, non-empty = 126; MIN/MAX/AVG duration confirmed 1/19/9.944 h; 5 distinct technician_notes values (boilerplate per asset). `mining_agents/safety/untrusted.py` `FREE_TEXT_FIELDS` lists `maintenance_logs.technician_notes`.

#### mining_data.work_order_parts_edge (3 columns)
- `edge_id` — 64-character hex SHA-256 hash of the work-order/part pair; primary key
- `work_order_id` — Work order that consumed the part; joins erp_work_orders.work_order_id
- `part_number` — SKU consumed; joins inventory_levels.part_number; five distinct values: SKU-AIR-FILTER-08, SKU-BEARING-PUMP-G1, SKU-BELT-SPLICE-G2, SKU-LUBE-HEAVY-T2, SKU-VALVE-SEAL-22

**Evidence:** `data/generator/maintenance.py` — `_load_parts_cache()` (lines 213–281) reads work_order_parts_edge, iterates `(work_order_id, part_number)` pairs, prices parts from inventory_levels. `data/generator/supply_chain.py` `load_parts_edge()` (lines 219–223) confirms schema (edge_id, work_order_id, part_number). Supply_chain.py module docstring: "work_order_parts_edge has no backup because no task rewrites it". Live BigQuery: 186 rows, 126 distinct work_order_ids, 5 distinct part_numbers confirmed by `DISTINCT` queries; edge_id is 64 chars confirmed by `LENGTH()` query. `supply_chain.py` `_S08_SQL` graph traversal confirms this is the REPLACED_PART graph edge table.

---

## Columns with uncertain meaning or units

None. Every column's meaning and unit (where applicable) was established by at least one of the three prescribed evidence sources:
- `physics_parameters` and `recalculated_parameters` dimensionless coefficients: confirmed by unit-free keys (friction_mu, alpha, cooling_k) in actual BQ data; simulation_runs data shows friction_mu is the parameter the twin updates after each anomaly event.
- `impact_score` scale (0.0–1.0): confirmed by measured values (0.8, 0.9, 0.95) in the 3-row table.
- `repair_cost` formula and all cost components: fully stated in `data/generator/maintenance.py` module docstring and code (LABOUR_RATE, MOB_BASE, CREW_SIZE constants).

---

## Test commands and output

```
$ cd /Users/amritharajendran/VivekWork/src/mining-agents && \
  /Users/amritharajendran/.local/pythons/py312/bin/python -m pytest \
  tests/context/test_semantics.py -v

============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/amritharajendran/VivekWork/src/mining-agents
configfile: pyproject.toml
plugins: anyio-4.14.2
collected 9 items

tests/context/test_semantics.py::test_agent_tables_is_the_25_table_surface PASSED [ 11%]
tests/context/test_semantics.py::test_yaml_parses_and_declares_only_agent_tables PASSED [ 22%]
tests/context/test_semantics.py::test_every_described_column_exists_in_bigquery PASSED [ 33%]
tests/context/test_semantics.py::test_each_described_table_is_described_completely PASSED [ 44%]
tests/context/test_semantics.py::test_a_short_table_description_is_refused PASSED [ 55%]
tests/context/test_semantics.py::test_a_short_column_description_is_refused PASSED [ 66%]
tests/context/test_semantics.py::test_a_description_of_exactly_the_minimum_length_is_accepted PASSED [ 77%]
tests/context/test_semantics.py::test_a_table_with_no_columns_is_refused PASSED [ 88%]
tests/context/test_semantics.py::test_a_time_column_naming_a_column_that_does_not_exist_is_refused PASSED [100%]

9 passed in 4.64s
```

---

## Deviations from the brief

**Column order:** YAML entries follow BigQuery's schema order (as returned by `client.get_table()`), which differs from the alphabetical listing in the brief's table of column names. The brief says "in the order the columns appear in the table's BigQuery schema", which is the authoritative schema order. This is used rather than the illustrative order in the brief's column lists.

**technician_notes content:** The live data currently contains only boilerplate text ("Maintenance complete for ASSET-ID. Standard procedures followed. System tested and operational.") — five distinct values, one per asset. The description says it is operator-authored free text and flags it as untrusted, which is the correct characterisation based on its `FREE_TEXT_FIELDS` registration and intended purpose. The current data's uniform content is a generator limitation that does not change what the column represents semantically.
