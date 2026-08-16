# Task 6 Report: Carry four more metrics to the screens

## Status: DONE

---

## Commands run and their output

### 1. Initial JS test state

```
node --test 'tests/js/*.test.js'
# Result: 169 pass, 1 fail
# Failing: "every driver in every shipped method pack has a phrase"
# AssertionError: p1-reliability.yaml: driver "cost_concentration" has no reader-facing phrase
```

### 2. Personas.json before changes

```
{'P1': None, 'P2': None, 'P3': None, 'P4': None, 'P5': None, 'P6': {'metric': 'unit cost per tonne of contained metal'}, 'P7': None, 'P8': None}
```

### 3. Rebuilt personas.json (no BigQuery needed)

```
PYTHONPATH=. python -m scripts.build_app_data
# wrote apps/shared/data/catalog.json (77,149 bytes)
# wrote apps/shared/data/personas.json (28,761 bytes)
# wrote apps/shared/data/graph.json (172,118 bytes)
# wrote apps/shared/data/facts.json (2,625 bytes)
# ... (full local build)
# agent nodes 100, entrypoints 52, swarms 12, HITL 14
# personas 8
```

### 4. Personas.json after changes

```
{'P1': {'metric': 'unplanned repair cost per asset'},
 'P2': {'metric': 'maintenance cost per completed work order'},
 'P3': {'metric': 'severity-weighted incident exposure'},
 'P4': None,
 'P5': {'metric': 'contained-metal variance between the block model and realised grade'},
 'P6': {'metric': 'unit cost per tonne of contained metal'},
 'P7': None, 'P8': None}
```

### 5. Python tests

```
PYTHONPATH=. python -m pytest -q tests/scripts/test_build_app_data.py
# 5 passed in 0.07s
```

### 6. JS tests (final)

```
node --test 'tests/js/*.test.js'
# tests 172, pass 172, fail 0
```

---

## build_app_data.py and BigQuery

The build script does NOT require BigQuery. Its `main()` reads only:
- Python catalog definitions (in-memory)
- `docs/persona-profiles.yaml`
- `method/*.yaml` pack files
- `data/profile/stats.json`
- `data/generated/*.parquet`

The rebuild ran successfully without credentials. No reauthentication is needed for this task.

---

## fatigue_to_incident collision — resolution and justification

`fatigue_to_incident` exists in two maps:

1. **`TRAVERSALS`**: `"how crew fatigue connects to incidents"` — phrase for `graph_traverse`, describing the graph edge walk in `MiningOperationsSafetyGraph`.

2. **`METHOD_DRIVERS`** (new): `"whether fatigue readings can be reliably linked to specific incidents in the data"` — phrase for `run_diagnostic` on the P3 driver declared `not_instrumented`.

**They do NOT interfere:** `_noun()` dispatches on the tool name. `run_diagnostic` checks `METHOD_DRIVERS`; `graph_traverse` scans `TRAVERSALS`. Completely separate dispatch paths.

**They must have DIFFERENT phrasings:** The traversal walks a graph edge — it executes against `MiningOperationsSafetyGraph`. The driver asks a data-coverage question: only 5 of 60 incidents carry an operator link (as noted in the P3 pack comments), so attribution cannot be done at usable scale. The driver phrase names the coverage gap. A reader who sees "Checking how crew fatigue connects to incidents" (the traversal phrasing) would not know whether an agent is walking a graph or reporting a data limitation.

**Test added:** `tests/js/plain.test.js` now pins this with `assert.notEqual(traversalPhrase, driverPhrase)`. A future edit that collapses them fails the test.

---

## The 26 new phrases added to METHOD_DRIVERS

### P1 — Reliability Engineer (metric: unplanned repair cost per asset)

- `cost_concentration`: "whether a handful of assets are carrying most of the repair bill"
- `criticality_load`: "whether the highest-consequence assets are also the costliest to repair"
- `excursion_rate`: "whether telemetry is flagging which assets are running outside their normal range"
- `repair_duration`: "whether repair time varies enough across assets to explain the cost spread"
- `condition_precursors`: "whether telemetry excursions reliably precede a work order on the same asset"
- `availability`: "whether uptime is being tracked and which assets are running the fewest operating hours"
- `mtbf`: "whether mean time between failures is trending in the right direction per asset"

### P2 — Maintenance Planner (metric: maintenance cost per completed work order)

- `priority_cost_escalation`: "whether higher-priority work orders consistently cost more to close"
- `backlog_aging`: "whether stale work orders are sitting in the backlog long enough to inflate cost"
- `parts_stockout`: "which parts are below their reorder point and how long it takes to restock them"
- `parts_demand_cover`: "whether parts on hand are enough to cover what open work orders need"
- `schedule_compliance`: "what proportion of work orders were closed within their scheduled window"
- `planned_ratio`: "whether preventive work is growing as a share of the total maintenance programme"

### P3 — HSE Lead (metric: severity-weighted incident exposure)

- `location_concentration`: "whether incident burden is concentrated in specific operational areas"
- `severity_mix`: "whether the distribution of incident severity levels signals any pattern worth acting on"
- `fatigue_exposure`: "whether the biometric monitoring record shows sleep-deficit exposure across the workforce"
- `radio_distress`: "whether emergency radio traffic concentrates in any particular operational period"
- `fatigue_to_incident`: "whether fatigue readings can be reliably linked to specific incidents in the data"
- `shift_pattern`: "whether incidents or fatigue alerts concentrate in a particular shift window"

### P5 — Geologist (metric: contained-metal variance between the block model and realised grade)

- `model_bias`: "whether the block model differs systematically from assayed grade across the dataset"
- `bias_by_lithology`: "whether the grade variance is concentrated in one or more geological domains"
- `bias_by_depth`: "whether grade variance changes with depth, pointing to a depth-dependent model error"
- `bias_by_elevation`: "whether grade variance changes with elevation, suggesting a weathering or structural control"
- `feed_grade_vs_model`: "whether the grade arriving at the plant matches what the block model predicted"
- `tonnage_reconciliation`: "whether modelled tonnage matches the tonnes actually mined and delivered"
- `qaqc_bias`: "whether laboratory QA/QC failures are introducing a systematic assay bias"

### P6 — Metallurgist — existing phrase changed

- `bypass`: changed from "whether bypass events are costing recovery" to "whether ore routed around the grinding circuit is costing recovery"

Reason: the test `!line.includes(id)` requires phrases not contain the raw driver id. "bypass" appeared in the old phrase. The existing pinned test at line 329 was updated to match.

---

## Files changed

- `apps/shared/plain.js` — 26 phrases added to `METHOD_DRIVERS`; `bypass` phrase updated; `fatigue_to_incident` collision documented in comment
- `apps/shared/data/personas.json` — rebuilt; P1/P2/P3/P5 carry `method.metric`
- `apps/shared/data/bundle.js` — rebuilt
- `apps/shared/data/{catalog,facts,graph,signals,workspace,benchmarks}.json` — rebuilt (timestamps only)
- `tests/js/plain.test.js` — added collision test, fixture-based coverage test; updated `bypass` pin
- `tests/fixtures/driver-ids.json` — 31 driver ids, generated from method/*.yaml
- `tests/scripts/test_build_app_data.py` — new, 5 tests
- `scripts/gen_driver_ids.py` — new, regenerates the fixture when packs change

---

## Nothing blocked on reauthentication

`build_app_data.py` uses only local files. No reauthentication is needed.

---

## Commit SHA

See git log — committed as "feat: carry four more governing metrics to the persona pages".
