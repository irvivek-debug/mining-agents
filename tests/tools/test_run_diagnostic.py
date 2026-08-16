"""Tests for run_diagnostic — the tool that executes a driver's fixed query.

`method_lookup` hands the agent its driver tree but withholds each driver's
SQL, on the reasoning that a model handed a query will paraphrase or mutate the
diagnostic.  `run_diagnostic` closes the loop: the agent names a driver, the
runtime resolves the SQL, runs it, and returns the result.  The diagnostic that
ships is the diagnostic that runs.

The guard travels with every result, because a result that arrives without its
guard invites an unguarded recommendation.  The SQL text and the file path do
not — returning them would undo the withholding that `method_lookup` enforces.
"""
import json

import pytest

from mining_agents.tools.run_diagnostic import make_run_diagnostic


def test_an_unknown_driver_id_fails_with_the_valid_ids_listed():
    # A model that guessed an id needs to see the real ones so it can self-
    # correct without calling method_lookup again.
    run = make_run_diagnostic("P6")
    env = run("no_such_driver")
    assert env["success"] is False
    assert env["error"]["code"] == "NO_SUCH_DRIVER"
    # The message must name the real ids so the model can self-correct.
    for real_id in ("liberation", "feed_variability", "bypass"):
        assert real_id in env["error"]["message"], (
            f"real id {real_id!r} missing from error message: {env['error']['message']}"
        )


def test_a_not_instrumented_driver_fails_with_driver_status_and_question():
    # The agent must be able to report that a driver exists but is not
    # instrumented.  DRIVER_NOT_INSTRUMENTED is a first-class answer: the agent
    # says "the driver exists; the data is not available", not "no driver found".
    run = make_run_diagnostic("P6")
    env = run("reagent_regime")
    assert env["success"] is False
    assert env["error"]["code"] == "DRIVER_NOT_INSTRUMENTED"
    details = env["error"]["details"]
    assert details["status"] == "not_instrumented"
    assert details["question"]  # non-empty; proves the driver's context travels


def test_a_persona_with_no_pack_fails_with_no_method_pack():
    # A persona that has no pack must fail loudly.  An agent with no method
    # must stop and escalate, not return an improvised answer.
    env = make_run_diagnostic("P4")("liberation")
    assert env["success"] is False
    assert env["error"]["code"] == "NO_METHOD_PACK"


def test_no_failure_envelope_carries_the_sql_text_or_a_sql_path():
    # Returning the SQL text would undo the withholding that method_lookup
    # enforces.  Assert against the full JSON dump so a field added anywhere
    # in the envelope is caught, not just in the obvious places.
    run = make_run_diagnostic("P6")
    for driver_id in ("no_such_driver", "reagent_regime"):
        dumped = json.dumps(run(driver_id))
        assert ".sql" not in dumped, f"{driver_id!r}: a .sql path leaked: {dumped}"
        assert "WITH cs AS" not in dumped, f"{driver_id!r}: SQL text leaked: {dumped}"


@pytest.mark.integration
def test_the_success_envelope_carries_results_without_the_query_behind_them():
    # The failure paths above never touch the SQL file, so on their own they
    # would still pass if the success path returned the whole query. This is
    # the path that actually reads the file, so it is the one where a leak is
    # possible — and the one an agent sees on every real call.
    env = make_run_diagnostic("P6")("liberation")
    assert env["success"] is True, env.get("error")
    dumped = json.dumps(env)
    assert "WITH cs AS" not in dumped, f"SQL text leaked into the result: {dumped}"
    assert "sql/p6" not in dumped, f"the SQL file path leaked: {dumped}"
    # meta.tables_read legitimately names the tables, so a bare table name is
    # not evidence of a leak. A bound parameter marker is: it appears in
    # liberation.sql and has no reason to appear in a result. (NTILE was the
    # obvious second sentinel but lives only in feed_variability.sql, so
    # asserting it here would have passed no matter what leaked.)
    assert "@tight_max" not in dumped, f"a query parameter leaked: {dumped}"


@pytest.mark.integration
def test_liberation_returns_three_bands_and_a_non_empty_guard():
    # The magnitudes are pinned to match test_the_liberation_diagnostic_
    # reproduces_the_design_finding in tests/method/test_p6_pack.py.
    # Two tests pinning the same data cannot silently drift apart.
    run = make_run_diagnostic("P6")
    env = run("liberation")
    assert env["success"] is True, env.get("error")
    data = env["data"]
    assert data["driver"] == "liberation"
    assert data["guard"]  # non-empty; the constraint the agent must honour
    rows = data["rows"]
    bands = {r["band"]: r for r in rows}
    assert set(bands) == {"tight", "mid", "wide"}
    assert [bands[b]["days"] for b in ("tight", "mid", "wide")] == [23, 116, 28]


@pytest.mark.integration
def test_liberation_meta_names_both_source_tables():
    # The provenance panel must show the real sources.  Deriving the declared
    # list from the SQL text via the _TABLE_REF regex is what makes this true:
    # if the regex under-extracts, the dry run refuses the query loudly.
    run = make_run_diagnostic("P6")
    env = run("liberation")
    assert env["success"] is True, env.get("error")
    tables = env["meta"]["tables_read"]
    assert "mining_data.crusher_states" in tables
    assert "mining_data.metallurgical_recovery" in tables
