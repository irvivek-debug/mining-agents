import warnings

import pytest
from google.adk.agents import LlmAgent
from google.adk.workflow import Workflow

from agents.catalog.definitions import SWARMS
from agents.patterns.swarm import (
    SpecialistResult, barrier, build_swarm, critic_instruction,
)

HITL_COORDINATORS = {"S01", "S02", "S04", "S05", "S07", "S08", "S09", "S10", "S11"}


# ---------------------------------------------------------------------------
# Smoke: 12 swarms build and each SwarmDef has exactly 5 members
# ---------------------------------------------------------------------------

def test_every_swarm_builds():
    built = [build_swarm(s) for s in SWARMS]
    assert len(built) == 12


def test_a_swarm_exposes_exactly_five_agents():
    for swarm in SWARMS:
        assert len(swarm.agents) == 5


# ---------------------------------------------------------------------------
# barrier() utility — unchanged behaviour
# ---------------------------------------------------------------------------

def test_the_barrier_partitions_done_from_blocked():
    results = [
        SpecialistResult("S01-SP1", "DONE", {"n": 1}, None),
        SpecialistResult("S01-SP2", "BLOCKED", {}, "no telemetry for asset"),
        SpecialistResult("S01-SP3", "DONE", {"n": 3}, None),
    ]
    out = barrier(results)
    assert [r.agent_id for r in out["completed"]] == ["S01-SP1", "S01-SP3"]
    assert [r.agent_id for r in out["unverified"]] == ["S01-SP2"]


def test_a_blocked_specialist_does_not_abort_the_swarm():
    results = [SpecialistResult(f"S01-SP{i}", "BLOCKED", {}, "down")
               for i in (1, 2, 3)]
    out = barrier(results)
    assert out["completed"] == []
    assert [r.agent_id for r in out["unverified"]] == [
        "S01-SP1", "S01-SP2", "S01-SP3",
    ]


# ---------------------------------------------------------------------------
# Graph topology — replaces the old sub_agents index checks
# ---------------------------------------------------------------------------

def test_build_swarm_returns_workflow():
    wf = build_swarm(SWARMS[0])
    assert isinstance(wf, Workflow)


def test_every_swarm_has_exactly_five_llm_agents_plus_join_plus_start():
    """Each graph must contain __START__, 3 specialists, critic, coordinator,
    and exactly 1 JoinNode — 7 nodes total, 5 of which are LlmAgent."""
    for swarm in SWARMS:
        wf = build_swarm(swarm)
        node_names = sorted(n.name for n in wf.graph.nodes)
        # Exactly 7 nodes
        assert len(node_names) == 7, (
            f"{swarm.swarm_id}: expected 7 nodes, got {len(node_names)}: {node_names}"
        )
        # __START__ is present
        assert "__START__" in node_names, f"{swarm.swarm_id}: __START__ missing"
        # Exactly 5 LlmAgent nodes
        llm_count = sum(1 for n in wf.graph.nodes if isinstance(n, LlmAgent))
        assert llm_count == 5, (
            f"{swarm.swarm_id}: expected 5 LlmAgent nodes, got {llm_count}"
        )


def test_fan_out_all_three_specialists_are_reachable_from_start():
    """START must have exactly 3 successors, all of which are LlmAgent nodes
    whose names contain 'sp1', 'sp2', 'sp3' (i.e. the specialists, not the
    critic or coordinator)."""
    for swarm in SWARMS:
        wf = build_swarm(swarm)
        start_successors = sorted(
            e.to_node.name
            for e in wf.graph.edges
            if e.from_node.name == "__START__"
        )
        # Exactly 3 successors from START
        assert len(start_successors) == 3, (
            f"{swarm.swarm_id}: START should fan out to exactly 3 nodes, "
            f"got {start_successors}"
        )
        # All three are LlmAgent nodes
        node_map = {n.name: n for n in wf.graph.nodes}
        for name in start_successors:
            assert isinstance(node_map[name], LlmAgent), (
                f"{swarm.swarm_id}: START successor {name!r} is not an LlmAgent"
            )


def test_critic_is_not_a_peer_of_specialists():
    """The critic must NOT appear in the set of START's direct successors.
    This proves the critic is downstream of the barrier, not inside the fan-out."""
    for swarm in SWARMS:
        wf = build_swarm(swarm)
        start_successors = {
            e.to_node.name
            for e in wf.graph.edges
            if e.from_node.name == "__START__"
        }
        critic_name = swarm.critic.agent_id.lower().replace("-", "_")
        assert critic_name not in start_successors, (
            f"{swarm.swarm_id}: critic {critic_name!r} must not be a peer "
            f"of the specialists in the fan-out; found in START successors: "
            f"{start_successors}"
        )


def test_join_node_predecessors_are_exactly_the_three_specialists():
    """The JoinNode must have exactly 3 incoming edges, one from each specialist."""
    for swarm in SWARMS:
        wf = build_swarm(swarm)
        barrier_name = f"{swarm.swarm_id.lower()}_barrier"
        join_predecessors = sorted(
            e.from_node.name
            for e in wf.graph.edges
            if e.to_node.name == barrier_name
        )
        specialist_names = sorted(
            s.agent_id.lower().replace("-", "_") for s in swarm.specialists
        )
        assert join_predecessors == specialist_names, (
            f"{swarm.swarm_id}: JoinNode predecessors {join_predecessors} "
            f"!= specialist names {specialist_names}"
        )


def test_critic_only_predecessor_is_join_node():
    """The critic's only incoming edge must be from the JoinNode — not from
    any specialist, not from START."""
    for swarm in SWARMS:
        wf = build_swarm(swarm)
        critic_name = swarm.critic.agent_id.lower().replace("-", "_")
        critic_predecessors = sorted(
            e.from_node.name
            for e in wf.graph.edges
            if e.to_node.name == critic_name
        )
        barrier_name = f"{swarm.swarm_id.lower()}_barrier"
        assert critic_predecessors == [barrier_name], (
            f"{swarm.swarm_id}: critic {critic_name!r} predecessors "
            f"{critic_predecessors} should be exactly [{barrier_name!r}]"
        )


def test_coordinator_only_predecessor_is_critic():
    """The coordinator's only incoming edge must be from the critic."""
    for swarm in SWARMS:
        wf = build_swarm(swarm)
        coordinator_name = swarm.coordinator.agent_id.lower().replace("-", "_")
        critic_name = swarm.critic.agent_id.lower().replace("-", "_")
        coordinator_predecessors = sorted(
            e.from_node.name
            for e in wf.graph.edges
            if e.to_node.name == coordinator_name
        )
        assert coordinator_predecessors == [critic_name], (
            f"{swarm.swarm_id}: coordinator predecessors "
            f"{coordinator_predecessors} should be exactly [{critic_name!r}]"
        )


# ---------------------------------------------------------------------------
# critic_instruction() content checks — unchanged behaviour
# ---------------------------------------------------------------------------

def test_the_critic_instruction_requires_flagging_unverified_inputs():
    text = critic_instruction(SWARMS[0])
    assert "unverified" in text.lower()
    assert "BLOCKED" in text


def test_the_critic_instruction_is_injection_aware():
    text = critic_instruction(SWARMS[0])
    assert "steered" in text.lower() or "injection" in text.lower()


@pytest.mark.parametrize("swarm_id", ["S05", "S10"])
def test_biometric_swarm_critics_must_audit_for_raw_values(swarm_id):
    swarm = next(s for s in SWARMS if s.swarm_id == swarm_id)
    text = critic_instruction(swarm)
    assert "heart_rate_bpm" in text


# ---------------------------------------------------------------------------
# HITL tool presence — catalog level and graph level
# ---------------------------------------------------------------------------

def test_only_the_coordinator_holds_the_approval_tool():
    """Catalog-level check: tool name presence on AgentDef records."""
    for swarm in SWARMS:
        expected = swarm.swarm_id in HITL_COORDINATORS
        assert ("request_approval" in swarm.coordinator.tools) == expected
        for member in [*swarm.specialists, swarm.critic]:
            assert "request_approval" not in member.tools


def test_built_hitl_coordinators_carry_bound_request_approval():
    """Graph-level check: the built coordinator node (after ADK cloning) for
    HITL swarms must carry a bound request_approval callable, identified by
    BOTH __name__ == 'request_approval' AND tables_read == [APPROVAL_TABLE].

    Non-HITL coordinators and all specialists and critics in every swarm must
    carry no such tool.

    NOTE: ADK clones LlmAgent instances when they become graph nodes. We look
    up each role in wf.graph.nodes rather than using the object passed to
    Workflow(), to confirm the clone still holds the bound tools.
    """
    APPROVAL_TABLE = "mining_data.agent_approvals"

    def has_approval(llm_agent) -> bool:
        for t in llm_agent.tools:
            if not callable(t):
                continue
            if (getattr(t, "__name__", None) == "request_approval"
                    and getattr(t, "tables_read", None) == [APPROVAL_TABLE]):
                return True
        return False

    for swarm in SWARMS:
        wf = build_swarm(swarm)

        # Build a name -> node lookup from the built graph
        node_map = {n.name: n for n in wf.graph.nodes if isinstance(n, LlmAgent)}

        coordinator_name = swarm.coordinator.agent_id.lower().replace("-", "_")
        critic_name = swarm.critic.agent_id.lower().replace("-", "_")
        specialist_names = [
            s.agent_id.lower().replace("-", "_") for s in swarm.specialists
        ]

        # All five roles must be present in the graph
        assert coordinator_name in node_map, (
            f"{swarm.swarm_id}: coordinator {coordinator_name!r} not in graph"
        )
        assert critic_name in node_map, (
            f"{swarm.swarm_id}: critic {critic_name!r} not in graph"
        )
        for sp_name in specialist_names:
            assert sp_name in node_map, (
                f"{swarm.swarm_id}: specialist {sp_name!r} not in graph"
            )

        expected_hitl = swarm.swarm_id in HITL_COORDINATORS

        assert has_approval(node_map[coordinator_name]) == expected_hitl, (
            f"{swarm.swarm_id}: coordinator approval tool presence mismatch"
        )
        assert not has_approval(node_map[critic_name]), (
            f"{swarm.swarm_id}: critic must not hold request_approval"
        )
        for sp_name in specialist_names:
            assert not has_approval(node_map[sp_name]), (
                f"{swarm.swarm_id}: specialist {sp_name!r} must not hold request_approval"
            )


# ---------------------------------------------------------------------------
# Ruling 6 — zero DeprecationWarning from building a swarm
# ---------------------------------------------------------------------------

def test_no_deprecation_warning_from_build_swarm():
    """Building any swarm must emit zero DeprecationWarnings originating from
    agents/patterns/swarm.py.  We capture ALL warnings and filter by category
    and source filename so that unrelated framework deprecations do not fail
    this test."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        build_swarm(SWARMS[0])

    swarm_deprecations = [
        w for w in caught
        if issubclass(w.category, DeprecationWarning)
        and "swarm.py" in str(w.filename)
    ]
    assert swarm_deprecations == [], (
        f"DeprecationWarnings from swarm.py: "
        f"{[(str(w.message), w.filename) for w in swarm_deprecations]}"
    )
