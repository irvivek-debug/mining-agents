# Task 2 Report: Embed the Chunks

## Files Created

- `scripts/build_doc_embeddings.py`
- `tests/test_doc_embeddings.py`

## Deviations from Brief

Both files use the repo convention `bigquery.Client(project=s.project_id, location=s.location)` with `s = settings()` from `mining_agents.config`, rather than the brief's `bigquery.Client(location="US")`. This matches `scripts/build_doc_chunks.py` and prevents silent targeting of a wrong project when ambient ADC defaults differ.

## Commands Run and Output

**Step 2 — failing tests (expected):**
```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python -m pytest tests/test_doc_embeddings.py -v
```
Output: 2 FAILED — `NotFound: 404 Not found: Table genial-union-475913-i7:mining_data.doc_chunks_embedded was not found in location US`

**Step 4 — run the script:**
```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python scripts/build_doc_embeddings.py
```
Output: `embedded 48 chunks`

The `CREATE OR REPLACE MODEL` completed without error (model already existed from design probing; idempotent as expected). The `ML.GENERATE_EMBEDDING` DDL completed without column-name errors; `flatten_json_output=TRUE` produced the column `ml_generate_embedding_result` directly, matching the test expectation.

**Step 5 — passing tests:**
```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python -m pytest tests/test_doc_embeddings.py -v
```
Output: 2 passed in 4.89s

**Verification query:**
```
rows=48, good=48, dims=768
```

## Observed Counts

| Metric | Value |
|---|---|
| Row count in `doc_chunks_embedded` | 48 |
| Rows with 768-dim embedding | 48 (100%) |
| Embedding dimensions confirmed | 768 |
| Source `doc_chunks` rows | 48 |
| Row count match | yes |

## Surprises / Notes

None. The `text_embedding_model` already existed (as the brief warned) — `CREATE OR REPLACE` was idempotent. The `ML.GENERATE_EMBEDDING` with `flatten_json_output=TRUE` produced the column name `ml_generate_embedding_result` without any column-name errors, so no DDL changes were needed.
