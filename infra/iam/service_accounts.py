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

# bigquery.* roles that BigQuery only accepts at project level. A dataset ACL
# accepts READER/WRITER/OWNER (and the IAM roles that map onto them); jobUser
# grants query execution against the project's billing and has no ACL form.
_PROJECT_LEVEL_BQ_ROLES = frozenset({"roles/bigquery.jobUser"})

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

    - dataEditor         → table-scoped (agent_approvals only; never project-level)
    - bigquery.jobUser   → project-level. jobUser authorises *running* a query and
                           is billed to the project; BigQuery rejects it as a
                           dataset ACL entry. It is the one bigquery.* role that
                           cannot be dataset-scoped.
    - other bigquery.*   → dataset-scoped (mining_data ACL)
    - aiplatform.*       → project-level
    """
    if role == HITL_ROLE:
        return "table"
    if role in _PROJECT_LEVEL_BQ_ROLES:
        return "project"
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


def apply(dry_run: bool = True) -> None:
    """Create 100 service accounts and bind their roles across three resource scopes.

    dry_run=True (default): print exactly the operations the live path performs;
                            touch nothing.
    dry_run=False:          execute them. Do NOT call with dry_run=False until the
                            customer has given explicit approval and the
                            service-account quota has been confirmed sufficient.

    Both branches walk plan() and accumulate identically; only the final step
    differs. Dataset and table scopes have no single-command CLI form — they are
    read-modify-write cycles against an existing policy, so batching them once at
    the end is what the live path does and what the dry run reports. Printing an
    invented one-liner per binding would produce an audit that does not match
    execution.
    """
    s = settings()

    # dataset ACL and table IAM are read-modify-write: accumulate every addition,
    # then apply each policy once. Applying per-binding would re-read and
    # overwrite the policy 100 times and lose concurrent edits.
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
                dataset_additions.append((email, role))

            elif kind == "table":
                table_additions.setdefault(binding["resource"], []).append(
                    (email, role)
                )

    if dry_run:
        _print_dataset_acl_plan(s, dataset_additions)
        for tref, members in table_additions.items():
            _print_table_iam_plan(s, tref, members)
    else:
        _apply_dataset_acl(s, dataset_additions)
        for tref, members in table_additions.items():
            _apply_table_iam(s, tref, members)


def _print_dataset_acl_plan(s, additions: list[tuple[str, str]]) -> None:
    """Report the dataset ACL read-modify-write that _apply_dataset_acl performs."""
    dataset_ref = f"{s.project_id}:{s.dataset}"
    print()
    print(f"# dataset ACL patch on {dataset_ref} "
          f"({len(additions)} entries, applied as one read-modify-write):")
    print(f"{s.bq_binary} show --format=prettyjson {dataset_ref}")
    print("#   append to .access, then write the merged document back:")
    for email, role in additions:
        print(f"#     {{\"role\": \"{_bq_acl_role(role)}\", "
              f"\"userByEmail\": \"{email}\"}}")
    print(f"{s.bq_binary} update --source=/dev/stdin {dataset_ref}")


def _print_table_iam_plan(s, table_ref: str, members: list[tuple[str, str]]) -> None:
    """Report the table IAM read-modify-write that _apply_table_iam performs."""
    bq_table = table_ref.replace(".", ":", 1)
    print()
    print(f"# table IAM patch on {bq_table} "
          f"({len(members)} members, applied as one read-modify-write):")
    print(f"{s.bq_binary} get-iam-policy --format=prettyjson {bq_table}")
    print("#   append to .bindings, then write the merged policy back:")
    for email, role in members:
        print(f"#     {role} -> serviceAccount:{email}")
    print(f"{s.bq_binary} set-iam-policy {bq_table} /dev/stdin")


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


_ACL_ROLE_BY_IAM_ROLE = {
    "roles/bigquery.dataViewer": "READER",
    "roles/bigquery.dataEditor": "WRITER",
    "roles/bigquery.dataOwner": "OWNER",
}


def _bq_acl_role(iam_role: str) -> str:
    """Convert an IAM role to its BigQuery dataset ACL role name.

    Raises on any role with no ACL form. Falling back to the IAM string would
    write an entry BigQuery rejects with a 400 — and the rejection would name
    the whole ACL, not the offending role.
    """
    try:
        return _ACL_ROLE_BY_IAM_ROLE[iam_role]
    except KeyError:
        raise ValueError(
            f"{iam_role!r} has no BigQuery dataset ACL equivalent; it must be "
            f"bound at project or table scope. Check _resource_kind()."
        ) from None


if __name__ == "__main__":
    apply(dry_run=True)
