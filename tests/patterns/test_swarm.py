import pytest
from agents.catalog.definitions import SWARMS
from agents.patterns.swarm import (
    SpecialistResult, barrier, build_swarm, critic_instruction,
)

HITL_COORDINATORS = {"S01", "S02", "S04", "S05", "S07", "S08", "S09", "S10", "S11"}


def test_every_swarm_builds():
    assert len([build_swarm(s) for s in SWARMS]) == 12


def test_a_swarm_exposes_exactly_five_agents():
    for swarm in SWARMS:
        assert len(swarm.agents) == 5


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


def test_the_critic_is_sequential_after_the_parallel_fan_out():
    """Critic must not be a peer of the specialists in the parallel stage.

    Ruling 1 layout: sub_agents[0]=ParallelAgent, sub_agents[1]=critic LlmAgent,
    sub_agents[2]=coordinator LlmAgent.
    """
    swarm_agent = build_swarm(SWARMS[0])
    # The outer container must be a SequentialAgent with exactly 3 sub-agents
    assert len(swarm_agent.sub_agents) == 3

    # Position 0: parallel fan-out
    assert type(swarm_agent.sub_agents[0]).__name__ == "ParallelAgent"

    # Position 1: critic LlmAgent (not inside parallel stage)
    critic_llm = swarm_agent.sub_agents[1]
    assert type(critic_llm).__name__ == "LlmAgent"
    assert critic_llm.name.endswith("critic")

    # Position 2: coordinator LlmAgent
    coordinator_llm = swarm_agent.sub_agents[2]
    assert type(coordinator_llm).__name__ == "LlmAgent"

    # The parallel stage holds exactly 3 specialists — none of which is the critic
    parallel = swarm_agent.sub_agents[0]
    assert len(parallel.sub_agents) == 3
    assert all("critic" not in a.name for a in parallel.sub_agents)


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


def test_only_the_coordinator_holds_the_approval_tool():
    """Catalog-level check: tool name presence on AgentDef records."""
    for swarm in SWARMS:
        expected = swarm.swarm_id in HITL_COORDINATORS
        assert ("request_approval" in swarm.coordinator.tools) == expected
        for member in [*swarm.specialists, swarm.critic]:
            assert "request_approval" not in member.tools


def test_built_hitl_coordinators_carry_bound_request_approval():
    """Graph-level check: built coordinator LlmAgent for HITL swarms must have
    a bound request_approval callable in its .tools list.

    request_approval is identified by BOTH its name and its tables_read
    attribute, which the @tool decorator sets to ["mining_data.agent_approvals"].
    Either alone could match another tool one day; together they cannot.
    Non-HITL coordinators and all specialists and critics in every swarm must
    carry no such tool.
    """
    APPROVAL_TABLE = "mining_data.agent_approvals"

    def has_approval(llm_agent) -> bool:
        """Return True if the LlmAgent holds a bound request_approval callable."""
        for t in llm_agent.tools:
            if not callable(t):
                continue
            if (getattr(t, "__name__", None) == "request_approval"
                    and getattr(t, "tables_read", None) == [APPROVAL_TABLE]):
                return True
        return False

    for swarm in SWARMS:
        built = build_swarm(swarm)
        fan_out = built.sub_agents[0]       # ParallelAgent
        critic_llm = built.sub_agents[1]    # critic LlmAgent
        coordinator_llm = built.sub_agents[2]  # coordinator LlmAgent

        expected_hitl = swarm.swarm_id in HITL_COORDINATORS

        # Coordinator carries approval tool iff this is a HITL swarm
        assert has_approval(coordinator_llm) == expected_hitl, (
            f"{swarm.swarm_id}: coordinator approval tool presence mismatch"
        )

        # Critics never hold request_approval
        assert not has_approval(critic_llm), (
            f"{swarm.swarm_id}: critic must not hold request_approval"
        )

        # Specialists never hold request_approval
        for specialist_llm in fan_out.sub_agents:
            assert not has_approval(specialist_llm), (
                f"{swarm.swarm_id}: specialist {specialist_llm.name} "
                "must not hold request_approval"
            )
