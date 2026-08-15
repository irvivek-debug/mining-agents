"""Tests for method_lookup — the tool that hands an agent its driver tree.

The driver tree IS the method: it tells the agent which diagnostics exist, in
what order, and what guard conditions fence each recommendation. These tests
confirm that the contract between the tool and the agent is stable, and that
the tool fails loudly rather than silently when no pack is available.
"""
from mining_agents.tools.method_lookup import make_method_lookup


def test_p6_returns_its_metric_and_every_driver():
    said = make_method_lookup("P6")()
    assert said["success"], said.get("error")
    data = said["data"]
    assert data["metric"] == "unit cost per tonne of contained metal"
    assert len(data["drivers"]) == 5


def test_uninstrumented_drivers_are_returned_not_filtered():
    # The agent must be able to say a driver was not instrumented. Filtering
    # them here would make that impossible and the answer would imply the
    # tree was fully explored.
    drivers = make_method_lookup("P6")()["data"]["drivers"]
    assert {d["status"] for d in drivers} == {
        "evidenced", "unevidenced", "not_instrumented"
    }


def test_the_sql_is_not_exposed_to_the_model():
    # Handing the model raw SQL invites it to paraphrase or mutate the
    # diagnostic. The pack is fixed and auditable; the agent asks for a
    # result by driver id, and the runtime supplies the query.
    for driver in make_method_lookup("P6")()["data"]["drivers"]:
        assert "sql" not in driver, "exposing SQL invites the model to edit the method"


def test_a_persona_with_no_pack_fails_honestly():
    # A missing pack must surface as a known error code, not a crash. An agent
    # with no method has no business returning an answer; it should stop and
    # escalate.
    said = make_method_lookup("P4")()
    assert said["success"] is False
    assert said["error"]["code"] == "NO_METHOD_PACK"


def test_the_tool_reads_no_site_data():
    # method_lookup returns METHOD, not site data. tables_read must be empty so
    # the UX provenance panel does not show a fake table entry. rows_scanned
    # must be zero for the same reason.
    said = make_method_lookup("P6")()
    assert said["meta"]["tables_read"] == []
    assert said["meta"]["rows_scanned"] == 0
