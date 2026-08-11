# Task 2 Report: SOP Tool Envelope and @tool Decorator

## Completion Summary

Task 2 completed successfully following TDD as specified in the brief. All files created exactly as detailed in the requirements with no deviations or additional features.

## Files Created

1. **agents/envelope.py** — Tool envelope models and factory functions
   - `ToolError` pydantic model (RFC 7807 shape)
   - `Meta` model with timestamp, tables_read, rows_scanned
   - `Envelope` model (success, data, error, meta)
   - `ok()` and `fail()` factory functions
   - Internal `_now()` helper for ISO-8601 UTC timestamps

2. **agents/tools/__init__.py** — Empty package init file

3. **agents/tools/base.py** — Decorator and exception
   - `ToolFailure` exception class with code, message, and keyword details
   - `@tool()` decorator that wraps functions returning (data, rows_scanned) tuples
   - Decorator enforces non-empty tables_read declaration at decoration time
   - Handles ToolFailure exceptions as RFC 7807 errors
   - Catches all other exceptions and converts to "INTERNAL" error envelopes
   - Preserves tables_read in all failure envelopes

4. **tests/test_envelope.py** — Test suite (6 tests)
   - test_ok_produces_a_valid_envelope
   - test_fail_uses_rfc7807_shape
   - test_decorator_wraps_a_successful_call
   - test_decorator_converts_toolfailure_to_rfc7807
   - test_failure_envelope_still_carries_tables_read
   - test_tool_requires_a_nonempty_tables_read_declaration

## Test Execution

### Step 2: Initial test run (expected failure with ModuleNotFoundError)
```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/test_envelope.py -v
```
**Result:** ModuleNotFoundError: No module named 'agents.envelope' (expected) ✓

### Step 5: Test suite after implementation
```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/test_envelope.py -v
```
**Result:** 6 passed in 0.45s ✓

### Full regression test (Task 1 suite + Task 2)
```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/ -v
```
**Output:**
```
tests/test_config.py::test_settings_defaults_to_the_argolis_project PASSED
tests/test_config.py::test_model_for_tier_resolves_both_tiers PASSED
tests/test_config.py::test_model_for_tier_rejects_pattern_c_tier PASSED
tests/test_config.py::test_no_raw_model_id_outside_model_policy PASSED
tests/test_envelope.py::test_ok_produces_a_valid_envelope PASSED
tests/test_envelope.py::test_fail_uses_rfc7807_shape PASSED
tests/test_envelope.py::test_decorator_wraps_a_successful_call PASSED
tests/test_envelope.py::test_decorator_converts_toolfailure_to_rfc7807 PASSED
tests/test_envelope.py::test_failure_envelope_still_carries_tables_read PASSED
tests/test_envelope.py::test_tool_requires_a_nonempty_tables_read_declaration PASSED
tests/test_infra_ddl.py::test_all_additive_objects_exist PASSED
tests/test_infra_ddl.py::test_v_fatigue_scored_never_exposes_raw_heart_rate PASSED
============================= 12 passed in 3.94s ==============================
```

## Commit

**Branch:** feat/agents-phase-5  
**SHA:** ce6d1ec  
**Message:** feat(agents): SOP tool envelope and @tool decorator

## Fix round 1

### Changes made

**Finding 1 — `agents/tools/base.py`:** Restructured `wrapper` into two phases inside a nested try/except. Phase 1 (inner try) calls `fn(*args, **kwargs)` and handles `ToolFailure` and general `Exception`. Phase 2 (`return ok(...)`) is outside the inner try but inside the outer try, so any `ValidationError` or `TypeError` thrown by `ok()` or `fail()` is caught by the outer `except Exception` arm. The outer arm hand-builds a literal dict with `success: False`, `error.code: ENVELOPE_ERROR`, and `meta.tables_read` from the decorator's declared list — without calling `ok()` or `fail()`. The inner `except Exception` carries a comment recording the deliberate choice not to catch `BaseException`.

**Finding 2 — `tests/test_envelope.py`:** Added three tests:
- `test_envelope_error_when_ok_cannot_build_envelope` — returns `"not-an-int"` as `rows_scanned`, asserts result is a valid Envelope with `success=False` and correct `tables_read`.
- `test_envelope_error_code_is_envelope_error` — same trigger, asserts `error["code"] == "ENVELOPE_ERROR"`.
- `test_keyboard_interrupt_propagates` — asserts `KeyboardInterrupt` propagates through the boundary (`pytest.raises`).

Trailing newline on `agents/tools/base.py` was already present; no change needed.

### Test commands and output

```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/test_envelope.py -v
```
```
collected 9 items
tests/test_envelope.py::test_ok_produces_a_valid_envelope PASSED
tests/test_envelope.py::test_fail_uses_rfc7807_shape PASSED
tests/test_envelope.py::test_decorator_wraps_a_successful_call PASSED
tests/test_envelope.py::test_decorator_converts_toolfailure_to_rfc7807 PASSED
tests/test_envelope.py::test_failure_envelope_still_carries_tables_read PASSED
tests/test_envelope.py::test_tool_requires_a_nonempty_tables_read_declaration PASSED
tests/test_envelope.py::test_envelope_error_when_ok_cannot_build_envelope PASSED
tests/test_envelope.py::test_envelope_error_code_is_envelope_error PASSED
tests/test_envelope.py::test_keyboard_interrupt_propagates PASSED
9 passed in 0.06s
```

```
/Users/amritharajendran/.local/pythons/py312/bin/python3 -m pytest tests/ -v
```
```
collected 15 items
tests/test_config.py::test_settings_defaults_to_the_argolis_project PASSED
tests/test_config.py::test_model_for_tier_resolves_both_tiers PASSED
tests/test_config.py::test_model_for_tier_rejects_pattern_c_tier PASSED
tests/test_config.py::test_no_raw_model_id_outside_model_policy PASSED
tests/test_envelope.py::test_ok_produces_a_valid_envelope PASSED
tests/test_envelope.py::test_fail_uses_rfc7807_shape PASSED
tests/test_envelope.py::test_decorator_wraps_a_successful_call PASSED
tests/test_envelope.py::test_decorator_converts_toolfailure_to_rfc7807 PASSED
tests/test_envelope.py::test_failure_envelope_still_carries_tables_read PASSED
tests/test_envelope.py::test_tool_requires_a_nonempty_tables_read_declaration PASSED
tests/test_envelope.py::test_envelope_error_when_ok_cannot_build_envelope PASSED
tests/test_envelope.py::test_envelope_error_code_is_envelope_error PASSED
tests/test_envelope.py::test_keyboard_interrupt_propagates PASSED
tests/test_infra_ddl.py::test_all_additive_objects_exist PASSED
tests/test_infra_ddl.py::test_v_fatigue_scored_never_exposes_raw_heart_rate PASSED
15 passed in 3.54s
```

## Notes

- No model IDs were placed in any file (complies with repo-wide guard pattern)
- Pydantic v2 and google-adk 2.6.3 were already installed from Task 1
- Python interpreter: /Users/amritharajendran/.local/pythons/py312/bin/python3 (3.12.13)
- All code transcribed verbatim from brief requirements
- No features added beyond specification
- No ambiguities encountered; brief was complete and clear
