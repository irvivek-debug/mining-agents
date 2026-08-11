import pathlib

import pytest
from agents.catalog.definitions import ALL_AGENTS
from agents.patterns.deep import BIOMETRIC_TABLES
from infra.iam import service_accounts
from infra.iam.service_accounts import (
    BIOMETRIC_READERS, plan, sa_email, sa_id, tier_roles,
)

HITL = {"S01", "S02", "S04", "S05", "S07", "S08", "S09", "S10", "S11",
        "D07", "D14", "D25", "D30", "D37"}


def _by_id(agent_id):
    return next(a for a in ALL_AGENTS if a.agent_id == agent_id)


def test_there_are_one_hundred_service_accounts():
    assert len({sa_id(a) for a in ALL_AGENTS}) == 100


def test_the_naming_scheme_matches_the_design():
    assert sa_id(_by_id("S01")) == "mag-s01-coord"
    assert sa_id(_by_id("S01-CRITIC")) == "mag-s01-critic"
    assert sa_id(_by_id("S01-SP1")) == "mag-s01-sp1"
    assert sa_id(_by_id("D27")) == "mag-d27"


def test_every_account_id_fits_the_thirty_character_limit():
    too_long = [sa_id(a) for a in ALL_AGENTS if len(sa_id(a)) > 30]
    assert too_long == []


def test_emails_resolve_to_the_argolis_project():
    assert sa_email(_by_id("D27")) == (
        "mag-d27@genial-union-475913-i7.iam.gserviceaccount.com"
    )


def test_read_only_analysts_get_exactly_two_roles():
    roles = tier_roles(_by_id("D01"))
    assert set(roles) == {"roles/bigquery.dataViewer", "roles/bigquery.jobUser"}


def test_hitl_agents_add_dataeditor_and_nothing_else():
    roles = set(tier_roles(_by_id("D07")))
    assert "roles/bigquery.dataEditor" in roles
    assert roles == {"roles/bigquery.dataViewer", "roles/bigquery.jobUser",
                     "roles/bigquery.dataEditor"}


def test_coordinators_add_aiplatform_user():
    roles = set(tier_roles(_by_id("S03")))     # non-HITL coordinator
    assert "roles/aiplatform.user" in roles
    assert "roles/bigquery.dataEditor" not in roles


def test_exactly_fourteen_accounts_can_write():
    writers = {a.agent_id for a in ALL_AGENTS
               if "roles/bigquery.dataEditor" in tier_roles(a)}
    assert writers == HITL


def test_no_agent_receives_project_level_dataeditor():
    for entry in plan():
        for binding in entry["bindings"]:
            if binding["role"] == "roles/bigquery.dataEditor":
                assert binding["resource"].endswith("agent_approvals"), entry


def test_job_user_is_bound_at_project_scope_never_the_dataset():
    """roles/bigquery.jobUser authorises running a query against the project's
    billing account. It has no BigQuery dataset ACL form — writing it into the
    dataset ACL is rejected with a 400, and the binding that pays for every
    query would silently never be applied.

    All 100 accounts carry jobUser, so the count assertion also proves this loop
    inspected a populated plan rather than passing vacuously.
    """
    job_user_bindings = [
        binding
        for entry in plan()
        for binding in entry["bindings"]
        if binding["role"] == "roles/bigquery.jobUser"
    ]
    assert len(job_user_bindings) == 100
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


def test_the_biometric_allowlist_is_exactly_five_patterns():
    assert BIOMETRIC_READERS == frozenset({
        "mag-s10-*", "mag-s05-sp2", "mag-d35", "mag-d36", "mag-d40",
    })


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
# Ruling 4 — Biometric allowlist / agent-catalog mismatch (deliberately pinned)
# ---------------------------------------------------------------------------

def _allowlist_covers(sid: str) -> bool:
    """Return True if sid is covered by any BIOMETRIC_READERS pattern."""
    for pattern in BIOMETRIC_READERS:
        if pattern.endswith("*"):
            if sid.startswith(pattern[:-1]):
                return True
        elif sid == pattern:
            return True
    return False


def test_biometric_allowlist_gap_is_exactly_the_known_unreconciled_set():
    """Document and pin the known mismatch between BIOMETRIC_READERS and the catalog.

    Agents whose source_tables intersect BIOMETRIC_TABLES but whose sa_id is NOT
    covered by the BIOMETRIC_READERS allowlist are a known, deliberately-pinned gap
    awaiting a customer decision — not an accident.  This test fails loudly if
    anyone changes either side without updating the other.

    The unreconciled set at the time of Task 14:
      mag-s05-coord  — S05 coordinator reads biometric_fatigue_logs and fatigue_logs_node
      mag-s05-critic — S05 critic reads biometric_fatigue_logs
      mag-s11-coord  — S11 coordinator reads fatigue_logs_node
      mag-s11-sp2    — S11-SP2 reads fatigue_logs_node
      mag-s12-coord  — S12 coordinator reads biometric_fatigue_logs
      mag-s12-sp3    — S12-SP3 reads biometric_fatigue_logs
    These agents are in the catalog and read biometric data, but are not in the
    allowlist.  Granting them direct table access vs. routing them through
    v_fatigue_scored is pending explicit customer sign-off.
    """
    bio_agent_sa_ids = {
        sa_id(a)
        for a in ALL_AGENTS
        if set(a.source_tables) & BIOMETRIC_TABLES
    }
    unreconciled = {sid for sid in bio_agent_sa_ids if not _allowlist_covers(sid)}
    assert unreconciled == {
        "mag-s05-coord",
        "mag-s05-critic",
        "mag-s11-coord",
        "mag-s11-sp2",
        "mag-s12-coord",
        "mag-s12-sp3",
    }


def test_biometric_allowlist_has_no_phantom_entries():
    """Assert every allowlist entry corresponds to at least one agent that reads a
    biometric table — and pin the one known phantom.

    mag-d40 is in the allowlist but D40 reads only incident_involvements and
    operator_vehicle_assignments (per the catalog comment: 'no biometric_fatigue_logs
    access').  This phantom entry is a known discrepancy pending a customer decision
    on whether D40 should be granted biometric access or removed from the allowlist.
    This test fails loudly if the catalog changes (D40 gains biometric tables) or the
    allowlist changes, so neither side can drift silently.
    """
    bio_agent_sa_ids = {
        sa_id(a)
        for a in ALL_AGENTS
        if set(a.source_tables) & BIOMETRIC_TABLES
    }

    phantoms = set()
    for pattern in BIOMETRIC_READERS:
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            if not any(sid.startswith(prefix) for sid in bio_agent_sa_ids):
                phantoms.add(pattern)
        else:
            if pattern not in bio_agent_sa_ids:
                phantoms.add(pattern)

    assert phantoms == {"mag-d40"}
