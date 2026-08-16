# Task 2 Report: P5 Geologist Method Pack

## 1. Each Diagnostic and BigQuery Validation

### model_bias.sql
Desurvey join: desurveyed sample midpoints matched to nearest block centroid within a cubic `@radius_m` tolerance.

```
cat method/sql/p5/model_bias.sql | bq query --use_legacy_sql=false --format=csv \
  --parameter=radius_m:INT64:25
```

Result:
```
paired_samples,modelled_grade,assayed_grade,variance,variance_pct
142,0.9121,0.8959,-0.0162,-1.8
```

142 paired samples at 25 m radius (>= 100, integration test gate passes). The test pins `paired_samples >= 100` as a floor, not an exact equality, per the brief's instruction.

### bias_by_lithology.sql
Groups paired result by `b.lithology_type`. Five domains confirmed non-empty.

```
cat method/sql/p5/bias_by_lithology.sql | bq query --use_legacy_sql=false --format=csv \
  --parameter=radius_m:INT64:25
```

Result:
```
domain,paired_samples,modelled_grade,assayed_grade,variance,variance_pct
OVERBURDEN,14,0.1428,0.2082,0.0654,45.8
CHERT,23,0.3536,0.3876,0.034,9.6
GRANITE,37,0.3916,0.4246,0.033,8.4
BASALT,24,1.2223,1.2227,4.0E-4,0.0
QSP_ORE,44,1.7172,1.5983,-0.1189,-6.9
```

Note: OVERBURDEN (14 pairs) and CHERT (23 pairs) fall below the GEO-GRS-003 clause 4.1 minimum of 30 per domain. The guard states this constraint; the pack does not omit them.

### bias_by_depth.sql
Depth bands by `(depth_start_meters + depth_end_meters) / 2`. Investigated depth distribution first: paired samples max out at ~275 m (not the ~448 m raw assay depth). At `@deep_min=300`, the deep band returned zero rows. Moved `@deep_min` to 200 m, which gives a non-empty three-band result. Did not widen the 25 m radius to paper over the empty band — the fact that deep paired samples are sparse is information.

Investigation query: grouped raw paired samples by depth tiers (lt100 / 100-200 / ge200) and found 56 / 64 / 22 populated.

Final validation with `@shallow_max=100 @deep_min=200`:
```
depth_band,paired_samples,mean_depth_m,modelled_grade,assayed_grade,variance,variance_pct
shallow,56,49.0,0.6887,0.6008,-0.0879,-12.8
mid,64,145.0,1.0479,1.0484,5.0E-4,0.0
deep,22,231.0,1.0855,1.2031,0.1176,10.8
```

### bias_by_elevation.sql
Bands by `b.centroid_z` (range 325-550 m, median 400 m). Cut points `@low_max=375 @high_min=450`.

```
cat method/sql/p5/bias_by_elevation.sql | bq query --use_legacy_sql=false --format=csv \
  --parameter=radius_m:INT64:25 --parameter=low_max:FLOAT64:375 --parameter=high_min:FLOAT64:450
```

Result:
```
elevation_band,paired_samples,mean_elevation_m,modelled_grade,assayed_grade,variance,variance_pct
low,52,351.0,1.1798,1.218,0.0382,3.2
mid,32,413.0,1.0613,1.0494,-0.0119,-1.1
high,58,487.0,0.5897,0.5223,-0.0674,-11.4
```

Three non-empty bands.

### feed_grade_vs_model.sql
Compares `metallurgical_recovery.feed_grade_pct` (167 daily rows) against block-model mean grade. No `@parameter` required because no predicate filtering is applied — the query aggregates all rows from both tables.

```
cat method/sql/p5/feed_grade_vs_model.sql | bq query --use_legacy_sql=false --format=csv
```

Result:
```
day_count,daily_mean_feed_grade,daily_stddev_feed_grade,block_model_mean_grade,feed_vs_model_variance,feed_vs_model_variance_pct
167,1.0929,0.1725,0.7599,0.3331,43.8
```

The 43.8% gap exceeds the +/-10% tolerance in GEO-GRS-003 clause 3.1 by a wide margin. The guard explicitly states this cannot be attributed to model error alone.

## 2. Drivers That Could Not Be Instrumented

**tonnage_reconciliation** — not instrumented. No tonnage column exists in `geological_block_models` or `drill_assay_logs` in this dataset. GEO-GRS-003 clause 7.2 notes that tonnage reconciliation is governed by a separate standard (GEO-TRC-004), which is not in the corpus. Declared `not_instrumented` with no `sql` and no `compare`.

**qaqc_bias** — not instrumented. The `drill_assay_logs` table has no QA/QC flag column. GEO-GRS-003 clause 4.3(a) specifies that samples with failed duplicate, blank or standard checks must be excluded, but the flag needed to apply that exclusion is absent from this dataset. Declared `not_instrumented`.

## 3. Final Test Command and Output

```
PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python \
  -m pytest tests/method/ tests/tools/test_method_lookup.py tests/patterns/ -q
```

```
79 passed, 4 warnings in 19.35s
```

All 7 P5 pack tests pass (including the integration test `test_the_model_bias_diagnostic_pairs_samples_to_blocks` which asserts `paired_samples >= 100`).

## 4. doc_query Strings and Evidence of Retrieval

All five instrumented drivers carry `doc_query` strings drawn from the vocabulary of `method/sop/grade-reconciliation-standard.md` (GEO-GRS-003, indexed under `folder = "site-standards"`).

| Driver | doc_query |
|--------|-----------|
| model_bias | `reconciliation variance tolerance paired sample count search radius grade` |
| bias_by_lithology | `domain reconciliation variance lithology geological resource model reporting` |
| bias_by_depth | `depth estimation uncertainty drill spacing resource model interpolation` |
| bias_by_elevation | `elevation weathering oxidation domain boundary grade model variance` |
| feed_grade_vs_model | `reconciliation variance delivered feed grade model prediction plant` |

Evidence that these retrieve GEO-GRS-003: the standard contains the exact terms "reconciliation variance" (clause 2.3), "paired sample" (clause 2.5), "search radius" (clause 5.1), "domain" (clause 2.4), and "indicative" (clause 2.6, clause 4.2). The doc_query for `model_bias` assembles the five most diagnostic terms from clauses 3, 4 and 5 — the clauses whose thresholds the guard fences against (+/-10% tolerance, 30-pair minimum, 15 m standard radius). The `bias_by_lithology` guard explicitly cites GEO-GRS-003 clause 4.1; the `feed_grade_vs_model` guard cites clause 7.1.

## 5. Ambiguity Resolutions and Concerns

**Depth band empty at brief's default**: The brief's depth range states "10-448 m" but at `@deep_min=300` the deep band returns zero paired samples (the desurvey join exhausts block coverage above 275 m depth). Default parameters changed to `@shallow_max=100 @deep_min=200` to produce three non-empty bands. This is reported, not papered over.

**feed_grade_vs_model has no @parameters**: The query aggregates all rows with no predicate filtering, so there are no interpolation targets. `assert_no_interpolation` passes. `params: {}` is valid in the YAML.

**test_method_lookup.py no change needed**: That test uses P4 as the "no pack" persona. P4 still has no pack. The brief's ambiguity resolution (update to P4 or P7) was pre-empted by the existing code already naming P4.

**bq CLI workaround**: The bq CLI crashes with a RecursionError when SQL containing backticks is passed as a shell argument. Queries were validated by piping SQL via stdin (`cat file.sql | bq query ...`).

## 6. Files Changed

- Created: `method/p5-geologist.yaml`
- Created: `method/sql/p5/model_bias.sql`
- Created: `method/sql/p5/bias_by_lithology.sql`
- Created: `method/sql/p5/bias_by_depth.sql`
- Created: `method/sql/p5/bias_by_elevation.sql`
- Created: `method/sql/p5/feed_grade_vs_model.sql`
- Created: `tests/method/test_p5_pack.py`
- Modified: `mining_agents/tools/method_lookup.py` (PACKS dict + comment)
- Modified: `mining_agents/catalog/definitions.py` (S06-SP1 tools and source_tables)

Commit SHA: `7a53225`
