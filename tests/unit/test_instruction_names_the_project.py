"""Every agent must be told where its data lives.

No agent instruction named the BigQuery project, so each query began by
guessing: passing the dataset `mining_data` as a project id (400, invalid
project), calling search_catalog without its mandatory project_id, trying a
project named `test` (refused -- the toolset is locked to one project). All
95 agents did this on every run. Most recovered after burning three or four
tool calls; S11-2-LEADTIME exhausted its budget and returned nothing.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor" / "agent_registry"))

import catalog_definitions as C  # noqa: E402
import register_agents as R  # noqa: E402


def build(agent) -> str:
    """The instruction as register_agents composes it, without touching cloud."""
    tables = ", ".join(agent.source_tables) or "your declared sources"
    data_access = (
        f"Your data lives in BigQuery project `{R.PROJECT}`, dataset "
        f"`{R.DATASET}`. Fully qualified, a table is "
        f"`{R.PROJECT}.{R.DATASET}.<table>`.\n"
        f"`{R.DATASET}` is the dataset, never the project. Tools that require a "
        f"project_id take `{R.PROJECT}`. Do not guess a project name and do not "
        f"omit project_id -- both fail, and the retries cost you the answer.\n"
    )
    return data_access + (agent.system_instruction or f"You are {agent.name}.")


@pytest.mark.parametrize("agent", C.CATALOG, ids=lambda a: a.agent_id)
def test_every_agent_is_told_its_project(agent):
    assert R.PROJECT in build(agent)


@pytest.mark.parametrize("agent", C.CATALOG, ids=lambda a: a.agent_id)
def test_every_agent_is_told_its_dataset(agent):
    assert R.DATASET in build(agent)


def test_agents_with_their_own_instruction_still_get_it():
    """The `or` branch skipped the composed text entirely, so the two agents
    carrying a custom system_instruction would have kept guessing."""
    custom = [a for a in C.CATALOG if (a.system_instruction or "").strip()]
    assert custom, "fixture assumption broken: no agent carries a custom instruction"
    for a in custom:
        built = build(a)
        assert R.PROJECT in built
        assert a.system_instruction[:40] in built, "custom instruction was dropped"


def test_the_instruction_distinguishes_dataset_from_project():
    """The actual failure was using the dataset name as a project id."""
    built = build(C.CATALOG[0])
    assert "never the project" in built


def test_source_is_wired_not_just_this_test_file():
    """Guards the real composition path, not this file's copy of it."""
    src = (ROOT / "scripts" / "register_agents.py").read_text()
    assert "data_access" in src
    assert "instruction = data_access + (" in src, \
        "preamble is no longer prepended to both branches"
