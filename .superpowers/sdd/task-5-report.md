# Task 5 Report — P3 HSE Lead driver tree for incident exposure

## Files created / modified

| File | Action | Purpose |
|---|---|---|
| `method/p3-hse.yaml` | created | P3 pack: 6 drivers, metric, root |
| `method/sql/p3/location_concentration.sql` | created | Incident count by location + severity breakdown |
| `method/sql/p3/severity_mix.sql` | created | Incident count and share by severity level |
| `method/sql/p3/fatigue_exposure.sql` | created | Fatigue log stats banded by @deficit_hours |
| `method/sql/p3/radio_distress.sql` | created | Emergency transmission count by shift bucket |
| `tests/method/test_p3_pack.py` | created | 10 tests (6 unit + 4 integration) |
| `mining_agents/tools/method_lookup.py` | modified | Added `"P3": "p3-hse.yaml"` to PACKS |
| `mining_agents/catalog/definitions.py` | modified | S05-SP2: added radio_communications to tables; updated tools |

---

## Diagnostics — exact bq query and real numbers

### location_concentration.sql

```sql
SELECT
  location_description, severity_level, COUNT(*) AS incident_count
FROM `mining_data.safety_incidents`
GROUP BY location_description, severity_level
ORDER BY SUM(COUNT(*)) OVER (PARTITION BY location_description) DESC,
  location_description, incident_count DESC
```

Real output (21 rows):
- Crusher Feeding Deck 17 total: HAZARD 6, FATALITY 6, NEAR_MISS 4, MTI 1
- Pit Floor Bench 4 12 total: NEAR_MISS 5, MTI 3, FATALITY 3, LTI 1
- Maintenance Shed 2 12 total: MTI 5, HAZARD 4, FATALITY 3
- Processing Plant Bay A 10 total: HAZARD 3, LTI 3, MTI 2, NEAR_MISS 1, FATALITY 1
- Tailings Dam Gate 9 total: HAZARD 3, MTI 3, LTI 1, NEAR_MISS 1, FATALITY 1

Agrees with brief (17/12/12/10/9). Structural difference from brief: the brief described a pivot with severity columns per row. The final SQL returns (location, severity_level, count) rows to avoid string-literal predicates (`= 'HAZARD'` etc.) that fail `assert_no_interpolation`. The non-pivot form is strictly correct: every severity cell count is directly readable.

### severity_mix.sql

```sql
SELECT severity_level, COUNT(*) AS incident_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS share_pct
FROM `mining_data.safety_incidents`
GROUP BY severity_level ORDER BY incident_count DESC
```

Real output: HAZARD 16 (26.7%), MTI 14 (23.3%), FATALITY 14 (23.3%), NEAR_MISS 11 (18.3%), LTI 5 (8.3%). Agrees with brief exactly.

### fatigue_exposure.sql (default @deficit_hours = 2.0)

```sql
SELECT
  CASE WHEN sleep_deficit_hours >= @deficit_hours THEN 'above_threshold'
       ELSE 'below_threshold' END AS deficit_band,
  COUNT(*) AS log_count,
  COUNT(CASE WHEN fatigue_alert_triggered = true THEN 1 END) AS alert_count,
  ROUND(AVG(sleep_deficit_hours), 2) AS mean_sleep_deficit_hours,
  ROUND(MAX(sleep_deficit_hours), 2) AS max_sleep_deficit_hours,
  SUM(microsleep_events_detected) AS microsleep_event_total,
  COUNT(DISTINCT operator_id) AS distinct_operators
FROM `mining_data.biometric_fatigue_logs`
GROUP BY deficit_band ORDER BY deficit_band
```

Real output:
- above_threshold: 1728 logs, 115 alerts, mean deficit 3.19h, max 7.98h, 268 microsleeps, 20 operators
- below_threshold: 1612 logs, 2 alerts, mean deficit 1.0h, max 1.99h, 2 microsleeps, 20 operators
- Total: 3,340 logs, 117 alerts

Agrees with brief (3,340 logs, 117 alerts). Column `fatigue_alert_triggered` confirmed from INFORMATION_SCHEMA before writing the SQL (brief's description said "alert count" without naming the column; the table holds `fatigue_alert_triggered`, not `alert_triggered`).

### radio_distress.sql

```sql
SELECT
  CASE WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 6 AND 13  THEN 'day'
       WHEN EXTRACT(HOUR FROM timestamp) BETWEEN 14 AND 21 THEN 'afternoon'
       ELSE 'night' END AS shift_bucket,
  COUNT(*) AS transmission_count,
  COUNT(CASE WHEN emergency_keyword_flag = true THEN 1 END) AS emergency_count,
  ROUND(AVG(sentiment_score), 4) AS mean_sentiment_score
FROM `mining_data.radio_communications`
GROUP BY shift_bucket ORDER BY shift_bucket
```

Real output:
- afternoon: 191 transmissions, 57 emergency, mean sentiment -0.0963
- day: 191 transmissions, 44 emergency, mean sentiment -0.0387
- night: 191 transmissions, 63 emergency, mean sentiment -0.1152
- Total: 573 transmissions, 164 emergency

Agrees with brief (573 total, 164 emergency). Shift bucket boundaries (06:00, 14:00, 22:00) are a standard three-shift assumption stated in the SQL comment and the guard; a site with different roster boundaries must adjust before drawing a shift-pattern conclusion.

---

## Verification of not_instrumented claims

### fatigue_to_incident

```sql
SELECT COUNT(DISTINCT si.incident_id) as incidents_with_operator_link
FROM `mining_data.safety_incidents` si
JOIN `mining_data.incident_involvements` ii USING (incident_id)
WHERE ii.operator_id IS NOT NULL
```

Result: **5 of 60 incidents** carry an operator link. Brief's claim confirmed. `not_instrumented` is correct.

### shift_pattern

```sql
-- Incidents
SELECT COUNT(*) as total, COUNT(CASE WHEN TIME(timestamp) = TIME(0,0,0) THEN 1 END) as midnight
FROM `mining_data.safety_incidents`

-- Fatigue logs
SELECT COUNT(*) as total, COUNT(CASE WHEN TIME(timestamp) = TIME(0,0,0) THEN 1 END) as midnight
FROM `mining_data.biometric_fatigue_logs`
```

Results: 60/60 incident timestamps at 00:00; 3,340/3,340 fatigue log timestamps at 00:00. Zero variance in both tables. `not_instrumented` is correct.

---

## Discrepancy against the brief

None on counts. The location_concentration SQL structure differs from the brief's implied pivot layout (see above) — that is a correct change, not a discrepancy.

---

## S05-SP2 declared tables vs SQL coverage

Before this task S05-SP2 declared 7 tables. My diagnostics read:
- `mining_data.safety_incidents` — location_concentration.sql, severity_mix.sql (declared ✓)
- `mining_data.biometric_fatigue_logs` — fatigue_exposure.sql (declared ✓)
- `mining_data.radio_communications` — radio_distress.sql (**missing — added in this task**)

The brief correctly identified radio_communications as the gap. Added to S05-SP2's tables. Also updated S05-SP2's tools from `["graph_traverse"]` to `["graph_traverse", "bq_query", "method_lookup", "run_diagnostic", "doc_search"]` as specified.

---

## doc_query strings and retrieval evidence

The fatigue management standard is indexed as:
- `folder = "site-standards"`
- `doc_id = "repo://method/sop/fatigue-management-standard.md"`
- 9 chunks (indices 0–8), confirmed by:

```sql
SELECT doc_id, chunk_index, LEFT(chunk_text, 120) as text_preview
FROM `mining_data.doc_chunks_embedded`
WHERE folder = "site-standards" AND doc_id LIKE "%fatigue%"
ORDER BY chunk_index
```

doc_query strings chosen per driver:

| driver | doc_query | retrieves |
|---|---|---|
| location_concentration | `OPS-FMS-001 safety incident location exposure indicator risk concentration` | clause 2.5 (exposure indicator definition), clause 3.2 (alert is exposure indicator) |
| severity_mix | `OPS-FMS-001 severity fatality LTI MTI HAZARD near miss incident classification exposure` | OPS-FMS-001 plus any site severity classification standard |
| fatigue_exposure | `OPS-FMS-001 biometric alert sleep deficit hours fatigue exposure indicator stand-down threshold` | clauses 3–5 (biometric monitoring, sleep-deficit thresholds, microsleep thresholds) |
| radio_distress | `OPS-FMS-001 radio emergency alert control room supervisor contact response checklist` | clause 3.3 (supervisor 2-minute radio contact requirement), clause 7.3 (reportable fatigue events) |

Guards cite OPS-FMS-001 by clause number where they reference thresholds, so the model retrieves authoritative text rather than relying on pack prose alone.

---

## Final test command and output

```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python -m pytest tests/method/ tests/tools/ tests/patterns/ -q
```

```
199 passed, 4 warnings in 120.72s (0:02:00)
```

4 warnings are pre-existing `BaseAgentConfig is deprecated` warnings from the ADK runtime, unrelated to this task.

P3-specific test output:
```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python -m pytest tests/method/test_p3_pack.py -q
10 passed in 12.13s
```

---

## Uncertainties and decisions

1. **`assert_no_interpolation` and boolean literals**: `= true` does not trigger the regex (it only catches quoted strings and bare numbers). Boolean literals in CASE WHEN conditions (`fatigue_alert_triggered = true`, `emergency_keyword_flag = true`) are safe.

2. **Shift bucket boundaries**: Treated as a documented assumption in the SQL comment and guard, not as parameters. Making them parameters would require parameterising the CASE labels too, adding complexity without improving the method. The guard requires a site with different roster boundaries to adjust before drawing a conclusion.

3. **Non-pivot form for location_concentration**: A strictly more informative representation that exposes every cell count directly. The test was updated to aggregate to location totals before asserting the [17, 12, 12, 10, 9] counts.

4. **`fatigue_exposure` counts note**: The `above_threshold` band shows 115 alerts, `below_threshold` shows 2, totalling 117. Both bands include the same 20 distinct operators (all operators appear in both bands across different sessions). This is expected — the same operator can have sessions both above and below the threshold over time.

---

## Fix round 1

### Test command and output

```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python -m pytest -q tests/method/ tests/tools/ tests/patterns/
```

```
200 passed, 4 warnings in 136.23s (0:02:16)
```

(4 warnings are pre-existing `BaseAgentConfig is deprecated` ADK runtime warnings, unrelated to this task.)

---

### CRITICAL 3 — "in this dataset" assertion: before/after

**Before fix (original YAML text contained):**
- `location_concentration` guard: "the severity cells **in this dataset** are small — each location's severity breakdown spans the full range of three to seventeen"
- `severity_mix` guard: "the LTI cell **in this dataset** is particularly small, and a share derived from five or fewer incidents carries high variance"

Running the new `test_no_guard_describes_the_data` test against the original YAML would have **FAILED** with messages identifying `location_concentration` and `severity_mix` as containing "in this dataset" — describing the data rather than the measurement.

**After fix:** Both guards were rewritten to state the methodological concern without referencing the data. The test now **PASSES**.

---

### Final text of every rewritten guard

**location_concentration guard (CRITICAL 1 — wrong number + guard doctrine violation):**
> incident_count is a count of recorded incidents at each location in the log; it is not a rate normalised against hours worked, equipment-hours, or personnel exposure at that location. A higher count at a location may reflect higher exposure rather than weaker controls. Report the incident count and each severity-level cell count beside any location finding; a conclusion drawn from a severity cell without its count stated cannot be distinguished from random variation. A biometric alert, as defined in OPS-FMS-001 clause 3.2, is an exposure indicator and is not on its own evidence of an incident cause; that clause applies equally here: a high incident count at a location is a signal that warrants review, not evidence of a specific control failure.

**severity_mix guard (CRITICAL 2 — named LTI and stated its size before measurement):**
> incident_count and share_pct are derived from the recorded incident log. share_pct is each level's proportion of recorded incidents, not a rate against hours worked or exposure. Report the incident_count for each severity level alongside its share; a share derived from a small cell carries high variance and must be read with its count stated. Severity classification is applied at investigation close; reclassification during investigation means that the distribution at any point in time reflects the current status of open investigations, not a settled record. A shift in the mix over time is observable only if the dataset spans multiple reporting periods.

**radio_distress guard (CRITICAL 2 + IMPORTANT 7 — stated bucket size as result + hardcoded boundaries):**
> emergency_count is the count of transmissions flagged by the emergency_keyword_flag field; the flag is applied by the transcription system and may not match a human assessment of distress. mean_sentiment_score is the mean of a continuous score derived from transcript text; it is a statistical summary of recorded language, not a direct measurement of operator state or incident proximity. The shift buckets are parameterised (@day_start_hour, @afternoon_start_hour, @night_start_hour); the site's own roster boundaries must be supplied before a concentration finding is read as a shift finding. Report transmission_count and emergency_count for each bucket beside any finding about concentration; a finding about a specific hour within a bucket requires the hourly data to be examined directly before a conclusion can rest on it. OPS-FMS-001 clause 3.3 requires the control-room supervisor to contact the worker by radio within 2 minutes of a biometric alert; a concentration of emergency traffic in a shift bucket is consistent with both genuine distress events and with the response protocol generating secondary radio activity.

*(fatigue_exposure guard was not rewritten — the reviewer finding about that guard was adjudicated as a legitimate methodological caveat and left unchanged.)*

---

### YAML file header (lines 10-16 after fix)

```yaml
# Thin cells are the defining constraint for this persona. Safety incident
# corpora in operations of this scale are bounded — any cross-tabulation
# produces cells small enough that a single event can shift a rate materially.
# Every guard for an instrumented driver therefore requires the count to be
# reported beside the finding; a finding read off a thin cell without the
# count stated is uninterpretable. That requirement is a methodological
# obligation, not a formatting convention.
```

---

### Summary of all changes

| Finding | File | Change |
|---|---|---|
| CRITICAL 1 | `method/p3-hse.yaml` | `location_concentration` guard: removed wrong range "three to seventeen" and "in this dataset"; restated as methodological requirement |
| CRITICAL 2a | `method/p3-hse.yaml` | `severity_mix` guard: removed "LTI cell … particularly small" and "in this dataset"; generalised to "small cell" with no level named |
| CRITICAL 2b | `method/p3-hse.yaml` | `radio_distress` guard: removed "approximately 190 transmissions"; replaced with param references and requirement to report counts |
| CRITICAL 2c | `method/p3-hse.yaml` | File header: removed "60 incidents" and "three to five" corpus-specific figures; rewritten to explain WHY thin cells are the constraint |
| CRITICAL 3 | `tests/method/test_p3_pack.py` | Added `test_no_guard_describes_the_data`: asserts "in this dataset" absent from all guards |
| CRITICAL 4 | `tests/method/test_p3_pack.py` | `test_fatigue_exposure_…`: replaced `max(distinct_operators) >= 20` with per-band `== 20` assertions; pinned per-band log_count/alert_count splits; raised `max_deficit >= 6.0` |
| IMPORTANT 5 | `tests/method/test_p3_pack.py` | `test_radio_distress_…`: removed false docstring claim about emergency sentiment; asserted `len(rows) == 3` exactly; pinned per-bucket transmission and emergency counts |
| IMPORTANT 6 | `tests/method/test_p3_pack.py` | `test_location_concentration_…`: added `len(rows) == 21` assertion; added per-row non-null `severity_level` check |
| IMPORTANT 7 | `method/sql/p3/radio_distress.sql` | Replaced `BETWEEN 6 AND 13` / `BETWEEN 14 AND 21` with `>= @day_start_hour < @afternoon_start_hour` etc. |
| IMPORTANT 7 | `method/p3-hse.yaml` | Added `params: {day_start_hour: 6, afternoon_start_hour: 14, night_start_hour: 22}` to `radio_distress` driver |
| Docstring cleanup | `tests/method/test_p3_pack.py` | Removed all references to "seeded generator" and "seeded and pinnable"; replaced with "deterministic for a given corpus" |

### Commit SHA

See git log — committed as: fix(p3-hse): remove data-specific claims from guards and strengthen test discriminability
