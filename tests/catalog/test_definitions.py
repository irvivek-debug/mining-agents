import pytest
from agents.catalog.definitions import ALL_AGENTS, DEEP, SWARMS
from agents.tools.bqml_predict import list_models
from agents.tools.graph_traverse import TRAVERSALS

HITL_COORDINATORS = {"S01", "S02", "S04", "S05", "S07", "S08", "S09", "S10", "S11"}
HITL_DEEP = {"D07", "D14", "D25", "D30", "D37"}


@pytest.fixture(scope="module")
def live_models() -> set[str]:
    """The BQML models that actually exist, so a renamed or dropped one fails.

    A fixture rather than a module-level constant, deliberately. At module
    level the BigQuery call runs at COLLECTION time, and anything that makes it
    fail — expired credentials, a fork run against a project with no models yet
    — takes all twenty tests in this file down as a collection error. That
    reads as "the catalog is broken" when the truth is "I am not
    authenticated", and it hides nineteen assertions that need no credentials
    at all. As a fixture, the blast radius is the one test that needs it.
    """
    return set(list_models())


def test_the_build_has_exactly_one_hundred_agents():
    assert len(ALL_AGENTS) == 100


def test_the_pattern_split_is_sixty_forty():
    assert len([a for a in ALL_AGENTS if a.pattern == "A"]) == 60
    assert len([a for a in ALL_AGENTS if a.pattern == "B"]) == 40


def test_there_are_twelve_swarms_of_five():
    assert len(SWARMS) == 12
    for swarm in SWARMS:
        assert len(swarm.specialists) == 3
        assert swarm.coordinator.swarm_role == "coordinator"
        assert swarm.critic.swarm_role == "critic"
        assert all(s.swarm_role == "specialist" for s in swarm.specialists)


def test_there_are_forty_deep_agents_numbered_d01_to_d40():
    assert len(DEEP) == 40
    assert {a.agent_id for a in DEEP} == {f"D{n:02d}" for n in range(1, 41)}


def test_agent_ids_are_unique():
    ids = [a.agent_id for a in ALL_AGENTS]
    assert len(ids) == len(set(ids))


def test_model_tiers_follow_the_role_rule():
    for agent in ALL_AGENTS:
        expected = "reasoning" if agent.swarm_role in ("coordinator", "critic") \
            else "balanced"
        assert agent.model_tier == expected, agent.agent_id


def test_the_tier_counts_match_the_design_table():
    tiers = [a.model_tier for a in ALL_AGENTS]
    assert tiers.count("reasoning") == 24   # 12 coordinators + 12 critics
    assert tiers.count("balanced") == 76    # 36 specialists + 40 deep


def test_no_pattern_c_tier_exists():
    assert all(a.model_tier in ("reasoning", "balanced") for a in ALL_AGENTS)


def test_exactly_fourteen_agents_are_hitl():
    hitl = {a.agent_id for a in ALL_AGENTS if a.hitl_required}
    assert hitl == HITL_COORDINATORS | HITL_DEEP
    assert len(hitl) == 14


def test_specialists_and_critics_are_never_hitl():
    for agent in ALL_AGENTS:
        if agent.swarm_role in ("specialist", "critic"):
            assert agent.hitl_required is False, agent.agent_id


def test_every_agent_declares_at_least_one_source_table():
    """PRD success metric: 100 of 100 agents resolve to a real table.

    Bare truthiness would pass on [""] — a list that is structurally non-empty
    and semantically void, which is the exact shape of this project's known
    array-loss failure. Pin the count and the qualification of every entry.
    """
    for agent in ALL_AGENTS:
        assert len(agent.source_tables) >= 1, agent.agent_id
        for table in agent.source_tables:
            assert table.startswith("mining_data."), (agent.agent_id, table)
            assert len(table) > len("mining_data."), (agent.agent_id, table)


@pytest.mark.parametrize("agent_id,fragment", [
    ("D27", "Safety Stock"),
    ("D37", "Radio Sentiment"),
    ("S01-SP2", "Blast-Radius"),
    ("S12", "Shift Handover"),
])
def test_display_names_are_transcribed_from_the_prd(agent_id, fragment):
    by_id = {a.agent_id: a for a in ALL_AGENTS}
    assert agent_id in by_id
    assert fragment in by_id[agent_id].display_name


def test_agents_reading_biometrics_declare_the_base_table():
    """D35 and D36 drive the DLP controls for biometric data.

    D40 (Operator Exposure Profile Analyst) does NOT declare
    biometric_fatigue_logs — least-privilege: it profiles operator exposure
    from incidents and assignments only, not from raw biometric readings.
    """
    by_id = {a.agent_id: a for a in ALL_AGENTS}
    for agent_id in ("D35", "D36"):
        assert "mining_data.biometric_fatigue_logs" in by_id[agent_id].source_tables, \
            f"{agent_id} should declare biometric_fatigue_logs"
    # D40 must NOT have biometric access — it uses incident_involvements ×
    # operator_vehicle_assignments only.
    assert "mining_data.biometric_fatigue_logs" not in by_id["D40"].source_tables, \
        "D40 must not declare biometric_fatigue_logs (least-privilege)"


def test_agents_reading_free_text_declare_the_source_table():
    """Drives the untrusted-content notice in the instruction."""
    by_id = {a.agent_id: a for a in ALL_AGENTS}
    assert "mining_data.radio_communications" in by_id["D37"].source_tables
    assert "mining_data.maintenance_logs" in by_id["D10"].source_tables


def test_bqml_predict_is_never_granted_without_a_model(live_models):
    """make_bqml_predict([]) would raise: a tool must declare tables_read."""
    granted = [a for a in ALL_AGENTS if "bqml_predict" in a.tools]
    assert granted, "no agent has bqml_predict — the loop below proves nothing"
    for agent in granted:
        assert len(agent.models) >= 1, agent.agent_id
        assert all(m in live_models for m in agent.models), agent.agent_id


def test_graph_traverse_is_never_granted_without_a_traversal():
    granted = [a for a in ALL_AGENTS if "graph_traverse" in a.tools]
    assert granted, "no agent has graph_traverse — the loop below proves nothing"
    for agent in granted:
        assert len(agent.traversals) >= 1, agent.agent_id
        assert all(t in TRAVERSALS for t in agent.traversals), agent.agent_id
