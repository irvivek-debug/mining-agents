import pytest
from agents.envelope import Envelope
from agents.tools.graph_traverse import TRAVERSALS, make_graph_traverse


def test_all_four_graphs_are_covered():
    assert set(TRAVERSALS) == {
        "blast_radius", "stockout_exposure", "fatigue_to_incident", "ontology_related",
    }


@pytest.mark.parametrize("name", sorted(TRAVERSALS))
def test_traversals_use_edge_labels_not_table_names(name):
    sql = TRAVERSALS[name].sql
    for table_name in ("asset_dependencies", "work_order_parts_edge",
                       "operator_vehicle_assignments", "incident_involvements"):
        assert f"[:{table_name}" not in sql
    assert "GRAPH_TABLE" in sql


def test_blast_radius_returns_the_verified_row_count():
    gt = make_graph_traverse(["blast_radius"])
    env = gt("blast_radius", {"asset_id": "CONVEYOR-02"})
    Envelope.model_validate(env)
    assert env["success"] is True
    assert len(env["data"]["rows"]) == 3


def test_stockout_exposure_returns_the_verified_row_count():
    gt = make_graph_traverse(["stockout_exposure"])
    env = gt("stockout_exposure", {
        "below_rop_parts": ["SKU-BELT-SPLICE-G2", "SKU-LUBE-HEAVY-T2"],
        "asset_id": None,
    })
    assert env["success"] is True
    assert len(env["data"]["rows"]) == 101


def test_fatigue_to_incident_returns_the_verified_row_count():
    gt = make_graph_traverse(["fatigue_to_incident"])
    env = gt("fatigue_to_incident", {"operator_id": "OP-103"})
    assert env["success"] is True
    assert len(env["data"]["rows"]) == 167


def test_ontology_related_returns_the_verified_row_count():
    gt = make_graph_traverse(["ontology_related"])
    env = gt("ontology_related", {"concept": "CONVEYOR-02"})
    assert env["success"] is True
    assert len(env["data"]["rows"]) == 4


def test_a_sentinel_key_returns_zero_rows_but_still_succeeds():
    """Negative control: proves the row counts above are real matches."""
    gt = make_graph_traverse(["blast_radius"])
    env = gt("blast_radius", {"asset_id": "NO-SUCH-ASSET-ZZZ"})
    assert env["success"] is True
    assert env["data"]["rows"] == []


def test_an_unallowed_traversal_is_refused_inside_the_envelope():
    gt = make_graph_traverse(["blast_radius"])
    env = gt("fatigue_to_incident", {"operator_id": "OP-103"})
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "TRAVERSAL_NOT_PERMITTED"
    assert env["meta"]["tables_read"]
