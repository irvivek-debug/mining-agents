"""Gate: what the deploy sends is what the agents actually need at runtime.

The expensive failure this file guards against is a deploy that succeeds, a
container that builds, and an agent that then dies on its first query because a
file it reads at runtime never travelled. That round trip costs a full container
build to discover and the error surfaces as an empty `FAILED_PRECONDITION` from
the query API, nowhere near its cause. It has happened once: `references/`
was omitted and every agent crashed on `model-policy.md`.
"""
import pathlib

import pytest

from mining_agents.config import model_for_tier, settings
from mining_agents.registry import registrations
from scripts.deploy import (
    EXTRA_PACKAGES,
    REGION,
    deploy,
    deploy_command,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _extra_package_roots() -> set[pathlib.Path]:
    return {(_REPO_ROOT / pkg).resolve() for pkg in EXTRA_PACKAGES}


def test_the_model_policy_file_travels_to_the_container():
    """model_for_tier() opens this file every time an agent is built, so a
    container without it cannot construct a single agent."""
    policy = settings().model_policy_path.resolve()
    assert policy.is_file(), f"{policy} does not exist — this test proves nothing"
    roots = _extra_package_roots()
    assert any(root in policy.parents for root in roots), (
        f"{policy} is read at runtime but lives outside {sorted(roots)}, "
        f"so it will not exist in the container"
    )


def test_every_extra_package_exists():
    for root in _extra_package_roots():
        assert root.exists(), f"{root} is declared in EXTRA_PACKAGES but is absent"


def test_the_shared_package_travels():
    """Without this the shim's `from mining_agents.build import build_one`
    cannot resolve and no agent module imports at all."""
    assert (_REPO_ROOT / "mining_agents").resolve() in _extra_package_roots()


def test_extra_packages_cannot_collide_with_the_adk_staging_root():
    """ADK stages every deployment into /app/agents/<name> and rejects any
    extra package whose basename collides. `agents` is therefore permanently
    unusable as a top-level name here — this is why the package is
    `mining_agents`."""
    names = [pathlib.PurePath(pkg).name for pkg in EXTRA_PACKAGES]
    assert "agents" not in names
    assert len(names) == len(set(names)), f"duplicate basenames collide: {names}"


def test_model_policy_resolves_every_tier_the_catalog_uses():
    """A tier absent from model-policy.md raises at build time, which in a
    container means the same opaque runtime failure as a missing file."""
    from mining_agents.catalog.definitions import ALL_AGENTS

    tiers = {a.model_tier for a in ALL_AGENTS}
    assert tiers, "no tiers found — the loop below would prove nothing"
    for tier in sorted(tiers):
        assert model_for_tier(tier)


def test_deploy_command_targets_an_agent_engine_region_not_the_bq_location():
    """`settings().location` is 'US', a BigQuery location. Passing it as
    --region deploys nowhere."""
    assert REGION != settings().location
    argv = deploy_command("D01", "D01")
    assert f"--region={REGION}" in argv


def test_deploy_command_passes_every_extra_package():
    argv = deploy_command("D01", "D01")
    for pkg in EXTRA_PACKAGES:
        assert f"--extra_packages={pkg}" in argv


def test_deploy_command_points_at_the_generated_package_directory():
    """The ADK verb takes a directory, not an agent id (Ruling 1)."""
    assert deploy_command("D01", "D01")[-1] == "./packages/D01"


def test_deploy_command_updates_in_place_when_an_instance_already_exists():
    """Without --agent_engine_id a second run creates a duplicate instance,
    which bills separately and leaves nothing naming which one is live."""
    assert "--agent_engine_id=123" in deploy_command("D01", "D01", "123")
    assert not any(
        a.startswith("--agent_engine_id") for a in deploy_command("D01", "D01")
    )


def test_deploy_refuses_an_id_that_is_not_an_entrypoint():
    """`only` is a filter, not an escape hatch: a typo must fail loudly rather
    than silently deploying nothing."""
    with pytest.raises(KeyError):
        deploy(dry_run=True, only=("S01", "not-an-agent"))


def test_dry_run_prints_the_argv_the_real_run_would_execute(capsys):
    """The two must come from one function. A dry run that renders the command
    separately reads as evidence while being free to drift from what happens."""
    deploy(dry_run=True, only=("D01",))
    printed = capsys.readouterr().out
    for token in deploy_command("D01", _display_name("D01")):
        assert token in printed, token


def test_dry_run_names_a_service_account_for_every_agent(capsys):
    entries = list(registrations())
    assert entries, "no registrations — the assertions below would prove nothing"
    deploy(dry_run=True)
    printed = capsys.readouterr().out
    for entry in entries:
        assert entry["service_account"] in printed, entry["agent_id"]


def _display_name(agent_id: str) -> str:
    return next(e["display_name"] for e in registrations() if e["agent_id"] == agent_id)
