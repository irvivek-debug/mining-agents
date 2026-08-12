"""Tests for the three-account tier model.

Ruled 2026-08-12: every agent runs as one of three shared service accounts
rather than one account each. The reasoning is in the module docstring of
infra/iam/service_accounts.py. These tests pin both the model and the two
things it costs, so neither can become invisible:

  - the coordinator account over-grants dataEditor to S03, S06, and S12
  - biometric access is no longer restricted at the IAM layer at all
"""
import pathlib

import pytest
from mining_agents.catalog.definitions import ALL_AGENTS
from mining_agents.patterns.deep import BIOMETRIC_TABLES
from infra.iam import service_accounts
from infra.iam.service_accounts import (
    TIER_ACCOUNT_ID, TIER_ROLES, plan, sa_email, sa_id, tier_of, tier_roles,
)

HITL = {"S01", "S02", "S04", "S05", "S07", "S08", "S09", "S10", "S11",
        "D07", "D14", "D25", "D30", "D37"}

# The three coordinators that are NOT HITL. They share an account with nine
# that are, so they inherit dataEditor they do not need.
OVER_GRANTED = {"S03", "S06", "S12"}


def _by_id(agent_id):
    return next(a for a in ALL_AGENTS if a.agent_id == agent_id)


# ---------------------------------------------------------------------------
# The model
# ---------------------------------------------------------------------------

def test_all_one_hundred_agents_share_exactly_three_accounts():
    """The whole point of the ruling: 100 agents, 3 identities.

    The population is pinned first — a catalog that failed to load would
    otherwise satisfy "at most three distinct accounts" trivially.
    """
    assert len(ALL_AGENTS) == 100
    assert {sa_id(a) for a in ALL_AGENTS} == {
        "mag-agent-base", "mag-agent-approver", "mag-agent-coordinator",
    }


def test_every_agent_maps_to_a_tier_that_exists():
    unmapped = [a.agent_id for a in ALL_AGENTS if tier_of(a) not in TIER_ACCOUNT_ID]
    assert len(ALL_AGENTS) == 100
    assert unmapped == []


def test_the_tier_populations_partition_the_catalog():
    """83 base + 5 approver + 12 coordinator = 100, with no agent counted twice."""
    counts = {tier: 0 for tier in TIER_ACCOUNT_ID}
    for agent in ALL_AGENTS:
        counts[tier_of(agent)] += 1
    assert counts == {"base": 83, "approver": 5, "coordinator": 12}
    assert sum(counts.values()) == len(ALL_AGENTS) == 100


def test_the_approver_tier_is_the_five_hitl_deep_agents():
    approvers = {a.agent_id for a in ALL_AGENTS if tier_of(a) == "approver"}
    assert approvers == {"D07", "D14", "D25", "D30", "D37"}


def test_coordinators_outrank_hitl_when_an_agent_is_both():
    """S01 is a HITL coordinator, so both branches of `tier_of` match it and
    the order of the checks decides the answer.

    This no longer changes S01's privileges — the two accounts carry identical
    roles — but it decides which identity its calls are attributed to, and the
    catalog's coordinators should be recognisable as such in an audit trail."""
    s01 = _by_id("S01")
    assert s01.hitl_required is True
    assert s01.swarm_role == "coordinator"
    assert tier_of(s01) == "coordinator"


def test_every_account_id_fits_the_thirty_character_limit():
    too_long = [aid for aid in TIER_ACCOUNT_ID.values() if len(aid) > 30]
    assert len(TIER_ACCOUNT_ID) == 3
    assert too_long == []


def test_emails_resolve_to_the_argolis_project():
    assert sa_email(_by_id("D27")) == (
        "mag-agent-base@genial-union-475913-i7.iam.gserviceaccount.com"
    )


# ---------------------------------------------------------------------------
# Roles per account
# ---------------------------------------------------------------------------

def test_read_only_analysts_get_exactly_three_roles():
    assert set(tier_roles(_by_id("D01"))) == {
        "roles/bigquery.dataViewer", "roles/bigquery.jobUser",
        "roles/aiplatform.user",
    }


def test_the_approver_account_adds_dataeditor_and_nothing_else():
    assert set(tier_roles(_by_id("D07"))) == {
        "roles/bigquery.dataViewer", "roles/bigquery.jobUser",
        "roles/aiplatform.user", "roles/bigquery.dataEditor",
    }


def test_every_agent_can_reach_a_model():
    """Without aiplatform.user an agent cannot call Gemini, so it cannot
    answer anything — a total failure, not a degraded one.

    This role used to be granted to the 12 coordinators alone, on the stated
    rationale that they needed it to invoke sub-agents. There is no such call
    to authorise: a swarm's specialists are nodes in the coordinator's own
    Workflow graph, in the coordinator's process. The 88 non-coordinators were
    left unable to reach a model at all, and the live project masked it because
    the role had been granted by hand outside this module. Asserted across all
    100 rather than a sample, because the old bug was exactly a per-tier gap.
    """
    assert len(ALL_AGENTS) == 100
    missing = [
        a.agent_id for a in ALL_AGENTS
        if "roles/aiplatform.user" not in tier_roles(a)
    ]
    assert missing == []


def test_the_coordinator_and_approver_accounts_now_hold_identical_roles():
    """A consequence worth stating out loud rather than leaving to be noticed.

    The coordinator account is retained for attribution — it is the identity
    that logs, traces and BigQuery job history show — but it is no longer a
    privilege boundary. Anyone reading `tier_of` as a security control needs
    to see that the top two tiers grant exactly the same thing.
    """
    assert set(tier_roles(_by_id("S03"))) == set(tier_roles(_by_id("D07")))


def test_the_coordinator_account_over_grants_dataeditor_to_three():
    """The accepted cost of three accounts instead of four.

    S03, S06, and S12 are not HITL, but they share the coordinator account
    with nine coordinators that are, so they can write to agent_approvals.
    Pinned rather than tolerated silently: if a fourth account is ever added,
    or if one of these three becomes HITL, this test fails and forces the
    decision back into the open.
    """
    over_granted = {
        a.agent_id
        for a in ALL_AGENTS
        if "roles/bigquery.dataEditor" in tier_roles(a)
        and not a.hitl_required
        and a.swarm_role == "coordinator"
    }
    assert over_granted == OVER_GRANTED


def test_no_agent_that_should_write_has_lost_that_ability():
    """Every one of the 14 HITL agents still reaches dataEditor.

    The tier collapse must not have *removed* access — only added it. The 14
    are pinned by ID, so a catalog change that drops one fails here.
    """
    writers = {a.agent_id for a in ALL_AGENTS
               if "roles/bigquery.dataEditor" in tier_roles(a)}
    assert HITL <= writers
    # And the only extras are the three known over-grants.
    assert writers - HITL == OVER_GRANTED


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

def test_the_plan_has_one_row_per_account():
    entries = plan()
    assert len(entries) == 3
    assert {e["account_id"] for e in entries} == set(TIER_ACCOUNT_ID.values())


def test_the_plan_accounts_for_every_agent_exactly_once():
    """The plan carries the agent list so it can be audited without re-deriving it."""
    listed = [aid for entry in plan() for aid in entry["agents"]]
    assert len(listed) == 100
    assert set(listed) == {a.agent_id for a in ALL_AGENTS}


def test_no_account_receives_project_level_dataeditor():
    editor_bindings = [
        b for entry in plan() for b in entry["bindings"]
        if b["role"] == "roles/bigquery.dataEditor"
    ]
    assert len(editor_bindings) == 2      # approver + coordinator
    misscoped = [b for b in editor_bindings
                 if not b["resource"].endswith("agent_approvals")]
    assert misscoped == []


def test_job_user_is_bound_at_project_scope_never_the_dataset():
    """roles/bigquery.jobUser authorises running a query against the project's
    billing account. It has no BigQuery dataset ACL form — writing it into the
    dataset ACL is rejected with a 400, and the binding that pays for every
    query would silently never be applied.

    All three accounts carry jobUser, so the count assertion also proves this
    loop inspected a populated plan rather than passing vacuously.
    """
    job_user_bindings = [
        binding
        for entry in plan()
        for binding in entry["bindings"]
        if binding["role"] == "roles/bigquery.jobUser"
    ]
    assert len(job_user_bindings) == 3
    misscoped = [b for b in job_user_bindings if b["resource_kind"] != "project"]
    assert misscoped == []
    assert {b["resource"] for b in job_user_bindings} == {"genial-union-475913-i7"}


def test_a_role_with_no_acl_equivalent_cannot_reach_the_dataset_acl():
    """_bq_acl_role must refuse rather than pass an unmapped role through.

    A passthrough would append `{"role": "roles/bigquery.jobUser"}` to the ACL
    document; BigQuery rejects the whole update, naming the document rather than
    the offending entry.
    """
    assert service_accounts._bq_acl_role("roles/bigquery.dataViewer") == "READER"
    with pytest.raises(ValueError, match="jobUser"):
        service_accounts._bq_acl_role("roles/bigquery.jobUser")


def test_no_code_path_creates_a_service_account_key():
    """The module must contain no service-account credential-file call at all.

    The path is taken from the imported module rather than the cwd: a relative
    path would raise FileNotFoundError when pytest runs from anywhere but the
    repo root, turning a security assertion into a collection error.
    """
    source = pathlib.Path(service_accounts.__file__).read_text()
    assert "keys create" not in source
    assert "keys" not in source


# ---------------------------------------------------------------------------
# What the three-account model dissolved
# ---------------------------------------------------------------------------

def test_biometric_access_is_not_restricted_at_the_iam_layer():
    """Pin the consequence: IAM can no longer gate biometric data.

    Under one-account-per-agent, a BIOMETRIC_READERS allowlist could grant the
    raw fatigue tables to named accounts. With three shared accounts, the
    agents that read biometric data and the agents that must not now share an
    identity, so no IAM binding can separate them — every account holds
    dataViewer across the whole dataset, biometric tables included.

    This test asserts that absence deliberately. Biometric masking is enforced
    in the application layer instead: assert_reads_only_declared_tables gates
    which agents may reach the tables at all, and mask_rows plus
    redact_model_response (mining_agents/safety/output_filter.py) limit what leaks
    from the 14 that may.

    If someone reintroduces an IAM-level biometric control, this test fails and
    sends them here to read why it cannot work.
    """
    bio_readers = {a.agent_id for a in ALL_AGENTS
                   if set(a.source_tables) & BIOMETRIC_TABLES}
    assert bio_readers, "catalog has no biometric readers — check BIOMETRIC_TABLES"

    # Agents that read biometric tables share accounts with agents that do not.
    bio_accounts = {sa_id(_by_id(aid)) for aid in bio_readers}
    non_bio_accounts = {
        sa_id(a) for a in ALL_AGENTS
        if not set(a.source_tables) & BIOMETRIC_TABLES
    }
    assert bio_accounts & non_bio_accounts, (
        "biometric and non-biometric agents no longer share an account — "
        "an IAM-level control may now be possible; revisit this test"
    )

    # Every account reads the whole dataset; none is scoped to a table subset.
    dataset_reads = [
        b for entry in plan() for b in entry["bindings"]
        if b["role"] == "roles/bigquery.dataViewer"
    ]
    assert len(dataset_reads) == 3
    assert {b["resource_kind"] for b in dataset_reads} == {"dataset"}


def test_the_module_no_longer_exposes_a_biometric_allowlist():
    """BIOMETRIC_READERS was removed, not renamed.

    Leaving a per-account allowlist in a module where accounts are shared would
    read as an active control while restricting nothing.
    """
    assert not hasattr(service_accounts, "BIOMETRIC_READERS")


def test_tier_roles_is_the_single_source_of_account_privilege():
    """tier_roles(agent) must be exactly TIER_ROLES[tier_of(agent)].

    If the two ever diverge, the plan and the per-agent view disagree about
    what an account can do, and only one of them provisions GCP.
    """
    mismatches = [
        a.agent_id for a in ALL_AGENTS
        if tier_roles(a) != TIER_ROLES[tier_of(a)]
    ]
    assert len(ALL_AGENTS) == 100
    assert mismatches == []
