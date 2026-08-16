# Task 1 Report — Site Standards for P2, P3 and P5 Guards

## Status: DONE

---

## What changed and why

### New files
- `method/sop/fatigue-management-standard.md` — covers biometric alert thresholds (2 alerts/shift or 1 + microsleep triggers stand-down), sleep-deficit stand-down level (≥2 h in 24 h, ≥6 h in 7 days), microsleep removal rule (any single event; 3 events/30 days triggers occupational health referral), and authorising role for return to work (Health and Safety Manager or shift superintendent delegate). Clause 3.2 explicitly states a biometric alert is an exposure indicator and not, on its own, evidence of an incident cause.
- `method/sop/work-order-prioritisation-standard.md` — covers 4 priority categories with response times (P1 ≤8 h, P2 ≤48 h, P3 within 4-week cycle, P4 reviewed every 90 days), age-based review thresholds (P3 at 30 days, P4 at 90 days, auto-escalation at 60/180 days), lead-time procurement rule (>14 days: order before scheduling; >45 days: notify superintendent), and explicit prohibition on raising priority to obtain parts.
- `method/sop/grade-reconciliation-standard.md` — covers acceptable variance tolerance (±10% relative per domain; ±15% in two consecutive quarters triggers model review), minimum paired-sample count (30 pairs per domain; below that the result is designated indicative only), search radius convention (15 m isotropic; domain-specific radius requires Chief Geologist approval in writing before the exercise), and requirement to report by domain rather than in aggregate.
- `tests/scripts/test_build_doc_chunks.py` — 5 TDD tests verifying: all three standards are picked up, folder is "site-standards", each chunk contains at least one digit, chunk indexes are contiguous per file, and SOP_DIR points to the correct path.

### Modified files
- `scripts/build_doc_chunks.py` — added `from pathlib import Path`, `SOP_DIR`, `SOP_FOLDER` constants, and `sop_rows()` function. Updated `main()` to call `rows() + sop_rows()` so one run loads both sources.

### Why tests/scripts/ has no __init__.py
The existing `tests/method/` subdirectory has no `__init__.py` and works correctly with `--import-mode=importlib` (pyproject.toml). Adding `__init__.py` caused pytest to name the test module under a `tests.scripts` namespace, which broke the `from scripts.build_doc_chunks import …` import. Removing it matched the pattern of `tests/method/` and the tests passed immediately.

---

## Real doc_chunks row schema and reconciliation

The schema defined in `build_doc_chunks.py` (pinned via `SCHEMA`) has exactly 5 fields:

| field | BQ type |
|---|---|
| `doc_id` | STRING |
| `folder` | STRING |
| `file_name` | STRING |
| `chunk_index` | INT64 |
| `chunk_text` | STRING |

The brief's `sop_rows()` snippet produces rows with exactly the same 5 keys. No reconciliation was needed — the schemas are identical.

The GCS path produces rows with the same keys: `doc_id` = `blob.name` (e.g. `oem-equipment-manuals/Caterpillar_793F.pdf`), `folder` = the prefix before the last `/`, `file_name` = the part after the last `/`.

---

## Embedding build: full rebuild vs incremental

`build_doc_embeddings.py` executes:
```sql
CREATE OR REPLACE TABLE `mining_data.doc_chunks_embedded` AS ...
```

This is a **full rebuild**: it replaces the entire table on every run. It is not incremental. This means every run of `build_doc_embeddings.py` re-embeds all rows in `doc_chunks`, which is correct provided `doc_chunks` itself is always fully loaded (which it is — `build_doc_chunks.py` also uses `WRITE_TRUNCATE`).

---

## Test command and full output

Command:

```
PYTHONPATH=/Users/amritharajendran/VivekWork/src/mining-agents \
  /Users/amritharajendran/.local/pythons/py312/bin/python \
  -m pytest /Users/amritharajendran/VivekWork/src/mining-agents/tests/scripts/test_build_doc_chunks.py \
  -q --rootdir=/Users/amritharajendran/VivekWork/src/mining-agents
```

Red phase output (before implementation):
```
ERROR collecting tests/scripts/test_build_doc_chunks.py
ImportError while importing test module '…test_build_doc_chunks.py'.
    from scripts.build_doc_chunks import SOP_DIR, sop_rows
E   ModuleNotFoundError: No module named 'scripts.build_doc_chunks'
1 error in 0.06s
```
(The real failure was `cannot import name 'SOP_DIR'`; pytest's importlib mode surfaced it as a ModuleNotFoundError due to the `__init__.py` presence — see note below.)

Green phase output (after implementation):
```
.....                                                                    [100%]
5 passed in 0.73s
```

---

## BigQuery folder counts after loading

```
bq query --use_legacy_sql=false --format=csv \
  'SELECT folder, COUNT(*) AS chunk_count
   FROM `genial-union-475913-i7.mining_data.doc_chunks_embedded`
   GROUP BY folder ORDER BY folder'
```

Result:
```
folder,chunk_count
capital-works-archives,4
exploration-legacy-reports,5
field-progress-reports,25
legal-procurement-policies,2
macroeconomic-analyst-reports,6
oem-equipment-manuals,6
site-standards,30
```

Original 6 folders are unchanged at 48 total chunks. The new `site-standards` folder holds 30 chunks across 3 documents. Total: 78 chunks from 43 documents.

---

## Uncertainties and notes

1. **Pytest error message was misleading during TDD red phase.** pytest reported `ModuleNotFoundError: No module named 'scripts.build_doc_chunks'` rather than the brief's anticipated `ImportError: cannot import name 'SOP_DIR'`. Investigation confirmed: the real cause was the missing `SOP_DIR` name (verified by running the importlib loader directly in Python). The misleading message arose because `tests/scripts/__init__.py` caused pytest's importlib mode to resolve `scripts` as the `tests.scripts` package rather than the top-level `scripts` package. Removing `__init__.py` from `tests/scripts/` (matching the `tests/method/` pattern) resolved both the error and restored the correct error message.

2. **Standards word count.** Fatigue: ~750 words; Work-order: ~720 words; Grade reconciliation: ~760 words. All within the 400–900 word target.

3. **No verdict words** (`too few`, `too many`, `unevidenced`, `no signal`, `insufficient`) appear in any of the three documents.

4. **No metal names** appear in any of the authored documents.

5. **The previous task-1-report.md** described an earlier task (corpus extraction) and has been overwritten with this report for the current task.
