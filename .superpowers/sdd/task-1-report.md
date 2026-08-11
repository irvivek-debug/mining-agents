# Task 1 Report — Foundations (agents-phase-5)

**Status:** DONE  
**Date:** 2026-08-11  

---

## What was created

| File | Notes |
|---|---|
| `requirements.txt` | google-adk>=1.0.0, pydantic>=2.7,<3, google-cloud-bigquery>=3.25, db-dtypes>=1.2, pytest>=8.0 |
| `references/model-policy.md` | The only file in the repo permitted to contain raw model IDs |
| `agents/__init__.py` | Empty package marker |
| `agents/config.py` | Settings dataclass + settings() + model_for_tier() |
| `infra/__init__.py` | Empty package marker (required for `python3 -m infra.apply_ddl`) |
| `infra/apply_ddl.py` | Applies DDL idempotently via bq CLI stdin, verifies all 4 objects |
| `infra/ddl/agent_tables.sql` | DDL for agent_approvals, agent_run_log, agent_catalog + ALTER TABLE retention |
| `infra/ddl/v_fatigue_scored.sql` | Authorised view over biometric_fatigue_logs |
| `tests/test_config.py` | 4 tests for config module and model-policy guard |
| `tests/test_infra_ddl.py` | 2 tests for BigQuery object existence and view safety |

---

## DDL Applied

### agent_approvals (PARTITION BY DATE(decided_at) CLUSTER BY agent_id, action_type)

```sql
CREATE TABLE IF NOT EXISTS `genial-union-475913-i7.mining_data.agent_approvals` (
  approval_id              STRING  NOT NULL,
  agent_id                 STRING  NOT NULL,
  action_type              STRING  NOT NULL,
  target_entity            STRING,
  decision                 STRING  NOT NULL,
  approver_principal       STRING  NOT NULL,
  decided_at               TIMESTAMP NOT NULL,
  hold_duration_ms         INT64,
  agent_reasoning_snapshot STRING  NOT NULL,
  unverified_flags         ARRAY<STRING>,
  source_tables            ARRAY<STRING>
) PARTITION BY DATE(decided_at) CLUSTER BY agent_id, action_type;
```

### agent_run_log (PARTITION BY DATE(started_at) CLUSTER BY agent_id, status)

```sql
CREATE TABLE IF NOT EXISTS `genial-union-475913-i7.mining_data.agent_run_log` (
  run_id        STRING NOT NULL,
  agent_id      STRING NOT NULL,
  parent_run_id STRING,
  pattern       STRING NOT NULL,
  status        STRING NOT NULL,
  blocked_reason STRING,
  started_at    TIMESTAMP NOT NULL,
  ended_at      TIMESTAMP,
  tables_read   ARRAY<STRING>,
  rows_scanned  INT64
) PARTITION BY DATE(started_at) CLUSTER BY agent_id, status;
```

### agent_catalog (no partitioning)

```sql
CREATE TABLE IF NOT EXISTS `genial-union-475913-i7.mining_data.agent_catalog` (
  agent_id      STRING NOT NULL,
  display_name  STRING NOT NULL,
  pattern       STRING NOT NULL,
  swarm_id      STRING,
  swarm_role    STRING,
  apqc_code     STRING NOT NULL,
  persona       STRING NOT NULL,
  value_branch  STRING NOT NULL,
  model_tier    STRING NOT NULL,
  hitl_required BOOL   NOT NULL,
  source_tables ARRAY<STRING>
);
```

**Deviation from brief:** `source_tables ARRAY<STRING> NOT NULL` was rejected by BigQuery — `NOT NULL` cannot be applied to an ARRAY column. The constraint was removed from the DDL. This does NOT preserve the semantic requirement: BigQuery cannot store a NULL array (omitting the value yields `[]`), but it happily stores an empty array `[]`, which is precisely the silent failure mode this constraint was meant to prevent. The non-emptiness requirement cannot be expressed in BigQuery DDL; enforcement must live in the catalog loader, which will validate that `source_tables` contains at least one entry before writing any row to `agent_catalog`.

### v_fatigue_scored

```sql
CREATE OR REPLACE VIEW `mining_data.v_fatigue_scored` AS
SELECT
  operator_id,
  DATE(timestamp) AS log_date,
  CASE
    WHEN sleep_deficit_hours >= 3.0 OR microsleep_events_detected >= 3 THEN 'HIGH'
    WHEN sleep_deficit_hours >= 1.5 OR microsleep_events_detected >= 1 THEN 'ELEVATED'
    ELSE 'LOW'
  END AS fatigue_band
FROM `mining_data.biometric_fatigue_logs`;
```

### Retention (§6.3)

```sql
ALTER TABLE `mining_data.agent_approvals`  SET OPTIONS (partition_expiration_days = 90);
ALTER TABLE `mining_data.agent_run_log`    SET OPTIONS (partition_expiration_days = 90);
```

---

## Column names that differed from the brief's assumptions

**`biometric_fatigue_logs` has no `log_date` column.**  
The actual schema has: `operator_id`, `timestamp` (TIMESTAMP, partition key), `heart_rate_bpm`, `sleep_deficit_hours`, `microsleep_events_detected`, `fatigue_alert_triggered`.

The view uses `DATE(timestamp) AS log_date` to materialise a date column with the expected name. The view correctly exposes `operator_id`, `log_date` (derived), and `fatigue_band`, and hides `heart_rate_bpm`, `sleep_deficit_hours`, `microsleep_events_detected`.

---

## pip install outcome

`google-adk` installed successfully: version **2.6.3** (satisfies >=1.0.0).  
All other packages either already existed or were installed as transitive dependencies.  
No errors.

---

## apply_ddl.py modification from brief template

The `infra/apply_ddl.py` was modified from the brief's template for two reasons:

1. **bq CLI recursion bug**: `bq query` triggers a RecursionError in its flag parser when SQL is passed as a long positional argument. Fixed by passing SQL via stdin (`input=` kwarg to `subprocess.run`).

2. **Single-statement limit**: `bq query` processes one SQL statement at a time. The DDL files are split on `;` and each statement is sent in a separate invocation.

3. **Semicolons in SQL comments**: Two comment lines in `agent_tables.sql` from §1.4 contained semicolons (`Backs SC-4;` and `Single source of truth;`). These were replaced with em-dashes to prevent incorrect splitting. This is purely cosmetic — no SQL semantics changed.

---

## Test command and output

```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/test_config.py tests/test_infra_ddl.py -v
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /Users/amritharajendran/.local/pythons/py312/bin/python3
cachedir: .pytest_cache
rootdir: /Users/amritharajendran/VivekWork/src/mining-agents
plugins: anyio-4.14.2
collected 6 items

tests/test_config.py::test_settings_defaults_to_the_argolis_project PASSED
tests/test_config.py::test_model_for_tier_resolves_both_tiers PASSED
tests/test_config.py::test_model_for_tier_rejects_pattern_c_tier PASSED
tests/test_config.py::test_no_raw_model_id_outside_model_policy PASSED
tests/test_infra_ddl.py::test_all_additive_objects_exist PASSED
tests/test_infra_ddl.py::test_v_fatigue_scored_never_exposes_raw_heart_rate PASSED

6 passed in 3.27s
```

---

## Things I was unsure about / decisions made

1. **`source_tables NOT NULL` on ARRAY**: Removed per BigQuery's hard constraint. Application-level validation is the appropriate enforcement mechanism.

2. **`log_date` vs `timestamp`**: The brief assumes a `log_date` column. The real table uses `timestamp` (TIMESTAMP). The view derives `log_date` via `DATE(timestamp)`.

3. **`bq query` stdin vs argument**: Brief template passes SQL as positional arg; this fails for long SQL. Stdin is the documented workaround.

4. **Multi-statement DDL**: `bq query` is single-statement. The apply_ddl splits on `;` internally.

---

## Fix round 1

**Date:** 2026-08-11

### Findings fixed

| Finding | File | Change |
|---|---|---|
| 1 | `infra/ddl/agent_tables.sql` | ALTER TABLE paths made fully qualified to `genial-union-475913-i7.mining_data.*` |
| 2 | `tests/test_infra_ddl.py` | DLP assertion extended to cover `sleep_deficit_hours` and `microsleep_events_detected` in addition to `heart_rate_bpm` |
| 3a | `infra/ddl/agent_tables.sql` | Comment added above `agent_catalog.source_tables` documenting enforcement requirement and BigQuery limitation |
| 3b | `.superpowers/sdd/task-1-report.md` | Corrected the misleading "semantics are preserved" paragraph — empty-array acceptance is the failure mode, enforcement must be in the loader |
| 4 | `tests/test_config.py` | `test_model_for_tier_resolves_both_tiers` strengthened: both returned values must begin `gemini-` |
| 5 | `tests/test_config.py` | `test_no_raw_model_id_outside_model_policy` extended to glob `infra/**/*.py` |

### Test command and output

```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/test_config.py tests/test_infra_ddl.py -v
```

```
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /Users/amritharajendran/.local/pythons/py312/bin/python3
cachedir: .pytest_cache
rootdir: /Users/amritharajendran/VivekWork/src/mining-agents
plugins: anyio-4.14.2
collected 6 items

tests/test_config.py::test_settings_defaults_to_the_argolis_project PASSED [ 16%]
tests/test_config.py::test_model_for_tier_resolves_both_tiers PASSED     [ 33%]
tests/test_config.py::test_model_for_tier_rejects_pattern_c_tier PASSED  [ 50%]
tests/test_config.py::test_no_raw_model_id_outside_model_policy PASSED   [ 66%]
tests/test_infra_ddl.py::test_all_additive_objects_exist PASSED          [ 83%]
tests/test_infra_ddl.py::test_v_fatigue_scored_never_exposes_raw_heart_rate PASSED [100%]

============================== 6 passed in 6.36s ===============================
```

### apply_ddl output (Finding 1 validation)

```
Waiting on bqjob_r7418bc08555686d3_0000019fef5c5514_1 ... (0s) Current status: DONE
Skipped genial-union-475913-i7.mining_data.agent_approvals

Waiting on bqjob_r6251799a27670bf9_0000019fef5c5bd6_1 ... (0s) Current status: DONE
Skipped genial-union-475913-i7.mining_data.agent_run_log

Waiting on bqjob_r67ba967b3645d9a2_0000019fef5c62cc_1 ... (0s) Current status: DONE
Skipped genial-union-475913-i7.mining_data.agent_catalog

Waiting on bqjob_r66bba4c966a03218_0000019fef5c6fc4_1 ... (0s) Current status: DONE
Altered genial-union-475913-i7.mining_data.agent_approvals

Waiting on bqjob_r84f234076dd782a_0000019fef5c6fc4_1 ... (0s) Current status: DONE
Altered genial-union-475913-i7.mining_data.agent_run_log

Waiting on bqjob_r5c26df0f21bbd771_0000019fef5c7668_1 ... (0s) Current status: DONE
Replaced genial-union-475913-i7.mining_data.v_fatigue_scored

applying agent_tables.sql ...
applying v_fatigue_scored.sql ...
verified: agent_catalog, agent_approvals, agent_run_log, v_fatigue_scored
```
