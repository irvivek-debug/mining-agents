"""Tests for the METHOD instruction block and the tool bindings that support it.

WHY THIS FILE EXISTS:
Before this task, build_instruction was a retrieval-governance layer: scope,
citation, tool failure, never-invent. The METHOD block is the change the whole
redesign turns on. Without it, the agent is a natural-language-to-SQL service.
With it, the agent is told to work a driver tree and return a diagnosis.

Every test here guards a clause that would silently disappear under a refactor
unless something names it explicitly.
"""
from mining_agents.catalog.definitions import ALL_AGENTS
from mining_agents.patterns.deep import bind_tools, build_instruction

BY_ID = {a.agent_id: a for a in ALL_AGENTS}


def test_an_agent_with_a_pack_is_told_to_work_the_tree():
    # Without this block the agent answers the user's question directly instead
    # of working the driver tree. That is the failure mode the whole redesign
    # exists to prevent.
    said = build_instruction(BY_ID["S07-SP3"])
    assert "METHOD" in said
    assert "method_lookup" in said
    # The five steps that separate a diagnosis from a retrieval.
    for step in ("size", "attribute", "controllable", "why", "guard"):
        assert step in said.lower(), f"the {step!r} step is missing"


def test_an_agent_with_a_pack_is_told_to_use_run_diagnostic():
    # run_diagnostic is the mechanism by which the agent executes each driver's
    # fixed query. Without naming it in the instruction, the agent may fall back
    # to bq_query to implement its own version, defeating the pack entirely.
    said = build_instruction(BY_ID["S07-SP3"])
    assert "run_diagnostic" in said


def test_the_agent_is_told_not_to_drop_a_driver():
    # A silently dropped driver reads as "no problem found". That is the single
    # most dangerous honesty failure in this system — the answer implies full
    # coverage when coverage is partial.
    said = build_instruction(BY_ID["S07-SP3"])
    assert "unevidenced" in said.lower()


def test_the_agent_is_told_to_retrieve_the_constraint_before_recommending():
    # The guard fences the recommendation. Stating the guard after a
    # recommendation reverses the decision logic: the constraint becomes
    # optional context rather than a condition the recommendation must satisfy.
    said = build_instruction(BY_ID["S07-SP3"])
    assert "doc_search" in said
    assert "before" in said.lower()


def test_the_agent_is_told_to_read_the_guard_the_diagnostic_returns():
    # The step-5 clause names doc_search, which retrieves the SITE's documented
    # constraint. That is not the same thing as the 'guard' field run_diagnostic
    # returns, which is the METHOD's own caveat on the finding — and the two are
    # easy to conflate because both are called guards.
    #
    # This matters concretely. The P6 liberation guard says the torque figure is
    # a maximum over daily MEAN torque, so it bounds average duty and cannot
    # evidence headroom under an instantaneous alarm. If the instruction never
    # tells the agent to read the field, that caveat is dead text and the agent
    # will recommend a setting change on torque evidence that does not support
    # one. Without this assertion, the clause can be dropped in a refactor and
    # every other test here still passes.
    said = build_instruction(BY_ID["S07-SP3"])
    assert "'guard' field" in said, "the guard field is never surfaced to the agent"
    assert "run_diagnostic result" in said


def test_the_instruction_distinguishes_run_diagnostic_from_bq_query():
    # bq_query stays on S07-SP3 to size the prize and cover questions the tree
    # does not address. The risk: the agent uses bq_query to re-derive a driver
    # that run_diagnostic already computes, producing an inconsistent or silently
    # different result. This clause is load-bearing: without it, bq_query leaks
    # into diagnostic work and the pack's fixed queries are never run.
    said = build_instruction(BY_ID["S07-SP3"])
    # The instruction must tell the agent that run_diagnostic is the path for
    # any driver in the tree, and bq_query is for sizing and non-tree questions.
    assert "run_diagnostic" in said
    # The clause must positively distinguish the two uses.
    assert "bq_query" in said
    # And it must forbid using bq_query as a substitute for the pack's diagnostics.
    said_lower = said.lower()
    # The word "never" (or an equivalent) must appear near the bq_query / driver
    # distinction — this is the clause that carries the prohibition.
    assert "never" in said_lower


def test_an_agent_without_the_tool_gets_no_method_block():
    # Naming a tool an agent does not hold invites a call that cannot resolve.
    # D22 is a P6 agent that does not carry method_lookup; it must not receive
    # instructions that reference it.
    said = build_instruction(BY_ID["D22"])
    assert "METHOD" not in said


def test_both_new_tools_bind():
    # If any new tool name is missing from builders, bind_tools raises.
    # This catches "I added the catalog entry but forgot the builder" — which
    # leaves the agent with an empty tool list and silent diagnostic failures.
    bound = bind_tools(BY_ID["S07-SP3"])
    assert len(bound) == len(BY_ID["S07-SP3"].tools)


def test_all_three_new_tool_names_resolve():
    # The corrections to the brief add run_diagnostic alongside method_lookup
    # and doc_search. Each must resolve separately: one missing builder silently
    # shrinks the tool list rather than raising in some call paths.
    agent = BY_ID["S07-SP3"]
    assert "method_lookup" in agent.tools
    assert "run_diagnostic" in agent.tools
    assert "doc_search" in agent.tools
    bound = bind_tools(agent)
    tool_names = {t.__name__ for t in bound}
    assert "method_lookup" in tool_names
    assert "run_diagnostic" in tool_names
    assert "doc_search" in tool_names
