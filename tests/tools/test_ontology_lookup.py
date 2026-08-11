"""Tests for ontology_lookup tool."""
from agents.envelope import Envelope
from agents.tools.ontology_lookup import ontology_lookup


def test_a_known_concept_returns_its_related_concepts():
    env = ontology_lookup("CONVEYOR-02")
    Envelope.model_validate(env)
    assert env["success"] is True
    assert len(env["data"]["related"]) == 4
    assert all({"subject", "predicate", "object"} <= set(r)
               for r in env["data"]["related"])


def test_meta_names_both_sources():
    env = ontology_lookup("CONVEYOR-02")
    assert "mining_data.ontology_concepts" in env["meta"]["tables_read"]
    assert "mining_data.unstructured_docs_metadata" in env["meta"]["tables_read"]


def test_documents_can_be_suppressed():
    env = ontology_lookup("CONVEYOR-02", include_docs=False)
    assert env["success"] is True
    assert env["data"]["documents"] == []


def test_an_unknown_concept_succeeds_with_empty_results():
    env = ontology_lookup("NO-SUCH-CONCEPT-ZZZ")
    Envelope.model_validate(env)
    assert env["success"] is True
    assert env["data"]["related"] == []
