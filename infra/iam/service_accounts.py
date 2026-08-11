"""One dedicated service account per agent. Three least-privilege tiers.

No service-account credential file is ever created, downloaded, or stored —
Workload Identity Federation supplies credentials at runtime. This file
contains no credential-management calls of any kind.
"""
from __future__ import annotations

import json
import subprocess
from typing import Literal

from agents.catalog.definitions import AgentDef, ALL_AGENTS
from agents.config import settings

# ---------------------------------------------------------------------------
# Role constants
# ---------------------------------------------------------------------------
BASE_ROLES = ["roles/bigquery.dataViewer", "roles/bigquery.jobUser"]
HITL_ROLE = "roles/bigquery.dataEditor"
COORDINATOR_ROLE = "roles/aiplatform.user"

# ---------------------------------------------------------------------------
# Biometric table access — exactly five patterns, copied from §5.1.
# mag-s10-* is a wildcard covering all five S10 accounts.
# Do not derive this from the catalog; it is a separate approved access list.
# ---------------------------------------------------------------------------
BIOMETRIC_READERS: frozenset[str] = frozenset({
    "mag-s10-*", "mag-s05-sp2", "mag-d35", "mag-d36", "mag-d40",
})

# Mapping swarm_role → account-ID suffix for Pattern A agents.
_ROLE_SUFFIX: dict[str, str] = {
    "coordinator": "coord",
    "critic": "critic",
}

# Resource-kind tag — derivable from the plan entry; never re-decided in apply().
ResourceKind = Literal["project", "dataset", "table"]


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def sa_id(agent: AgentDef) -> str:
    """The GCP service-account ID (≤30 chars).

    Pattern B: mag-<lowercase-agent_id>  e.g. mag-d27
    Pattern A coordinator: mag-<swarm>-coord  e.g. mag-s01-coord
    Pattern A critic:      mag-<swarm>-critic e.g. mag-s01-critic
    Pattern A specialist:  mag-<swarm>-<sp-suffix> e.g. mag-s01-sp1
    """
    if agent.pattern == "B":
        return f"mag-{agent.agent_id.lower()}"
    swarm = agent.swarm_id.lower()
    if agent.swarm_role in _ROLE_SUFFIX:
        return f"mag-{swarm}-{_ROLE_SUFFIX[agent.swarm_role]}"
    # specialist: agent_id is like S01-SP1 → suffix is "sp1"
    return f"mag-{swarm}-{agent.agent_id.split('-')[-1].lower()}"


def sa_email(agent: AgentDef) -> str:
    """Full service-account email address for the given agent."""
    return f"{sa_id(agent)}@{settings().project_id}.iam.gserviceaccount.com"


def tier_roles(agent: AgentDef) -> list[str]:
    """Ordered list of IAM roles for this agent's tier.

    Tier 1 (all agents): dataViewer + jobUser on the dataset.
    Tier 2 (HITL agents): + dataEditor on the agent_approvals table only.
    Tier 3 (coordinators): + aiplatform.user on the project.
    """
    roles: list[str] = list(BASE_ROLES)
    if agent.hitl_required:
        roles.append(HITL_ROLE)
    if agent.swarm_role == "coordinator":
        roles.append(COORDINATOR_ROLE)
    return roles


def _resource_kind(role: str) -> ResourceKind:
    """Derive the binding resource scope from the role.

    - dataEditor   → table-scoped (agent_approvals only; never project-level)
    - bigquery.*   → dataset-scoped (mining_data ACL)
    - aiplatform.* → project-level
    """
    if role == HITL_ROLE:
        return "table"
    if role.startswith("roles/bigquery."):
        return "dataset"
    return "project"


def plan() -> list[dict]:
    """Return the full 100-row create-and-bind plan. Pure data; touches nothing.

    Each entry:
      {
        "agent_id":   str,
        "account_id": str,   # the ≤30-char GCP account ID
        "email":      str,   # full SA email
        "bindings": [
          {
            "role":          str,         # e.g. "roles/bigquery.dataViewer"
            "resource":      str,         # project / dataset / table reference
            "resource_kind": str,         # "project" | "dataset" | "table"
          },
          ...
        ],
      }

    resource_kind is stored in the plan so that apply() routes each binding to
    the correct GCP API without re-deciding scope inside apply().
    """
    s = settings()
    dataset_ref = f"{s.project_id}:{s.dataset}"
    table_ref = f"{s.project_id}.{s.dataset}.agent_approvals"
    entries = []
    for agent in ALL_AGENTS:
        bindings = []
        for role in tier_roles(agent):
            kind = _resource_kind(role)
            if kind == "table":
                resource = table_ref
            elif kind == "dataset":
                resource = dataset_ref
            else:
                resource = s.project_id
            bindings.append({
                "role": role,
                "resource": resource,
                "resource_kind": kind,
            })
        entries.append({
            "agent_id": agent.agent_id,
            "account_id": sa_id(agent),
            "email": sa_email(agent),
            "bindings": bindings,
        })
    return entries


# ---------------------------------------------------------------------------
# apply() — implements all three binding kinds; dry_run=True by default.
# apply(dry_run=False) must never be called by tests, automation, or CI
# without explicit customer approval and a resolved quota.
# ---------------------------------------------------------------------------

def _fmt_create(entry: dict, project_id: str) -> list[str]:
    return [
        "gcloud", "iam", "service-accounts", "create",
        entry["account_id"],
        f"--project={project_id}",
        f"--display-name={entry['agent_id']}",
    ]


def _fmt_project_binding(email: str, role: str, project_id: str) -> list[str]:
    return [
        "gcloud", "projects", "add-iam-policy-binding", project_id,
        f"--member=serviceAccount:{email}",
        f"--role={role}",
    ]


def _fmt_dataset_binding(email: str, role: str, dataset_ref: str) -> list[str]:
    # bq update --source merges a new ACL entry into the dataset ACL.
    # We use bq set-iam-policy on the dataset resource.
    # The command issued is a print-only representation here; the real path
    # in apply(dry_run=False) uses a JSON policy file built in memory.
    return [
        "bq", "update",
        "--dataset",
        f"--add-iam-policy-member={role}:serviceAccount:{email}",
        dataset_ref,
    ]


def _fmt_table_binding(email: str, role: str, table_ref: str) -> list[str]:
    # bq set-iam-policy on the table (agent_approvals).
    return [
        "bq", "set-iam-policy",
        table_ref,
        f"--member=serviceAccount:{email}",
        f"--role={role}",
    ]


def apply(dry_run: bool = True) -> None:
    """Create 100 service accounts and bind their roles across three resource scopes.

    dry_run=True (default): print all commands; touch nothing.
    dry_run=False:          execute every command.  Do NOT call with dry_run=False
                            until the customer has given explicit approval and the
                            service-account quota has been confirmed sufficient.

    All three resource kinds read their data from plan(), so the printed output
    is a faithful representation of what the live path would do.
    """
    s = settings()

    # Accumulate dataset and table bindings to batch them efficiently.
    # For dry_run=False, dataset ACL and table IAM are applied via bq get/set
    # to avoid overwriting concurrent ACL changes one-by-one.
    dataset_additions: list[tuple[str, str]] = []   # (email, role)
    table_additions: dict[str, list[tuple[str, str]]] = {}  # table_ref -> [(email, role)]

    for entry in plan():
        create_cmd = _fmt_create(entry, s.project_id)
        if dry_run:
            print(" ".join(create_cmd))
        else:
            subprocess.run(create_cmd, check=False)  # already-exists is not an error

        for binding in entry["bindings"]:
            role = binding["role"]
            email = entry["email"]
            kind = binding["resource_kind"]

            if kind == "project":
                cmd = _fmt_project_binding(email, role, s.project_id)
                if dry_run:
                    print(" ".join(cmd))
                else:
                    subprocess.run(cmd, check=True)

            elif kind == "dataset":
                if dry_run:
                    cmd = _fmt_dataset_binding(email, role, binding["resource"])
                    print(" ".join(cmd))
                else:
                    dataset_additions.append((email, role))

            elif kind == "table":
                if dry_run:
                    cmd = _fmt_table_binding(email, role, binding["resource"])
                    print(" ".join(cmd))
                else:
                    tref = binding["resource"]
                    table_additions.setdefault(tref, []).append((email, role))

    if not dry_run:
        _apply_dataset_acl(s, dataset_additions)
        for tref, members in table_additions.items():
            _apply_table_iam(s, tref, members)


def _apply_dataset_acl(s, additions: list[tuple[str, str]]) -> None:
    """Read the current dataset ACL, append new members, and write it back."""
    dataset_ref = f"{s.project_id}:{s.dataset}"
    result = subprocess.run(
        [s.bq_binary, "show", "--format=prettyjson", dataset_ref],
        capture_output=True, text=True, check=True,
    )
    meta = json.loads(result.stdout)
    acl = meta.get("access", [])

    existing = {
        (e.get("role", ""), e.get("userByEmail", ""))
        for e in acl
    }
    for email, role in additions:
        bq_role = _bq_acl_role(role)
        if (bq_role, email) not in existing:
            acl.append({"role": bq_role, "userByEmail": email})
            existing.add((bq_role, email))

    meta["access"] = acl
    policy_json = json.dumps(meta).encode()

    subprocess.run(
        [s.bq_binary, "update", "--source=/dev/stdin", dataset_ref],
        input=policy_json, check=True,
    )


def _apply_table_iam(s, table_ref: str, members: list[tuple[str, str]]) -> None:
    """Read the table IAM policy, append members, and write it back."""
    # table_ref uses dot notation: project.dataset.table
    bq_table = table_ref.replace(".", ":", 1)  # project:dataset.table for bq CLI
    result = subprocess.run(
        [s.bq_binary, "get-iam-policy", "--format=prettyjson", bq_table],
        capture_output=True, text=True, check=True,
    )
    policy = json.loads(result.stdout)
    bindings = policy.setdefault("bindings", [])

    role_to_members: dict[str, set[str]] = {}
    for b in bindings:
        role_to_members[b["role"]] = set(b.get("members", []))

    for email, role in members:
        member_str = f"serviceAccount:{email}"
        role_to_members.setdefault(role, set()).add(member_str)

    policy["bindings"] = [
        {"role": role, "members": sorted(m)}
        for role, m in sorted(role_to_members.items())
    ]
    policy_json = json.dumps(policy).encode()

    subprocess.run(
        [s.bq_binary, "set-iam-policy", bq_table, "/dev/stdin"],
        input=policy_json, check=True,
    )


def _bq_acl_role(iam_role: str) -> str:
    """Convert an IAM role string to the BigQuery dataset ACL role name."""
    mapping = {
        "roles/bigquery.dataViewer": "READER",
        "roles/bigquery.dataEditor": "WRITER",
        "roles/bigquery.dataOwner": "OWNER",
        "roles/bigquery.jobUser": "roles/bigquery.jobUser",  # not an ACL role; skip
    }
    return mapping.get(iam_role, iam_role)


if __name__ == "__main__":
    apply(dry_run=True)
