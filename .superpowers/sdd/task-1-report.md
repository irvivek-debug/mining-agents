# Task 1 Report: Extract the Document Corpus into BigQuery

## Status: DONE

---

## What was created / modified

| File | Action |
|---|---|
| `pyproject.toml` | Added `markers` key to `[tool.pytest.ini_options]` block |
| `requirements.txt` | Appended `pypdf>=5.0` and `google-cloud-storage>=2.18` |
| `scripts/build_doc_chunks.py` | Created (exact transcript of brief) |
| `tests/test_doc_chunks.py` | Created (exact transcript of brief) |

---

## Pre-flight dependency check

Both `pypdf` and `google-cloud-storage` were already installed in the target Python at
`/Users/amritharajendran/.local/pythons/py312/bin/python`. No `pip install` was needed.

---

## Test commands and exact output

### Step 4 — Expected failure before script existed

```
$ PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python \
    -m pytest tests/test_doc_chunks.py -v

============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /Users/amritharajendran/.local/pythons/py312/bin/python
cachedir: .pytest_cache
rootdir: /Users/amritharajendran/VivekWork/src/mining-agents
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... collected 0 items / 1 error

==================================== ERRORS ====================================
__________________ ERROR collecting tests/test_doc_chunks.py ___________________
ImportError while importing test module '...tests/test_doc_chunks.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
tests/test_doc_chunks.py:2: in <module>
    from scripts.build_doc_chunks import chunk_text
E   ModuleNotFoundError: No module named 'scripts.build_doc_chunks'
=========================== short test summary info ============================
ERROR tests/test_doc_chunks.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.06s ===============================
```

Failure was exactly as specified in the brief.

### Step 6 — All 3 tests pass after script was written

```
$ PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python \
    -m pytest tests/test_doc_chunks.py -v

============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /Users/amritharajendran/.local/pythons/py312/bin/python
cachedir: .pytest_cache
rootdir: /Users/amritharajendran/VivekWork/src/mining-agents
configfile: pyproject.toml
plugins: anyio-4.14.2
collecting ... collected 3 items

tests/test_doc_chunks.py::test_short_text_is_one_chunk PASSED            [ 33%]
tests/test_doc_chunks.py::test_long_text_splits_with_overlap PASSED      [ 66%]
tests/test_doc_chunks.py::test_empty_text_yields_no_chunks PASSED        [100%]

============================== 3 passed in 0.78s ===============================
```

---

## Real table build output

```
$ PYTHONPATH=. /Users/amritharajendran/.local/pythons/py312/bin/python \
    scripts/build_doc_chunks.py

loaded 48 chunks from 40 documents
```

- **Chunks:** 48
- **Documents:** 40
- **Within spec range (30–80):** Yes
- **Target table:** `mining_data.doc_chunks` on project `genial-union-475913-i7`, loaded with `WRITE_TRUNCATE`

---

## Surprises / notes

1. **Both dependencies already installed.** `pypdf` and `google-cloud-storage` were present in the py312 environment before any install step, so `requirements.txt` was updated for correctness but no `pip install` was needed.

2. **Chunk count is 48, not "roughly 38" as the inline comment in the script states.** The comment is verbatim from the brief (`chunk_count sums to 3,392 against a real corpus of roughly 38 chunks`) and was transcribed faithfully. The actual extraction produced 48 chunks — still well within the spec's acceptable window of 30–80. The discrepancy between the comment and the live result is in the brief itself; no change was made.

3. **`pyproject.toml` `markers` key placement.** The key was added inside the existing `[tool.pytest.ini_options]` block immediately after the `testpaths` line, exactly as required by the brief and the controller's context notes.

4. **`mining_data.unstructured_docs_metadata` was not consulted** at any point, consistent with the task constraint.
