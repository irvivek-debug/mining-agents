"""Deploy the 52 entrypoints to Agent Engine and attach their runtime identity.

Ruling 1: the ADK 2.6.3 deploy verb takes an agent DIRECTORY, not an agent id:
  python -m google.adk.cli deploy agent_engine \\
    --project=<PROJECT> --region=<REGION> --display_name=<NAME> <AGENT_DIRECTORY>
It has no --service-account flag, so the runtime identity is attached in a
second step (see `attach_service_account`).

Ruling 3: DOMAIN_BINDING_COMMAND is NEVER executed by this module. It is
printed with a warning and the caller is required to run it manually if approved.

The dry run prints the exact argv the real run executes, because both come from
`deploy_command`. A dry run that renders a command by hand is worse than no dry
run at all: it reads as evidence while being free to drift from what actually
happens. This module had that defect once already.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile

import google.auth
import google.auth.transport.requests
import requests

from mining_agents.config import settings
from mining_agents.registry import registrations

# Agent Engine has its own regions; `settings().location` is the BigQuery
# dataset location ("US") and is not one of them.
REGION = "us-central1"

# Directories that must travel to the container alongside the agent package.
#
# ADK copies each entry to /app/<basename> and puts /app on PYTHONPATH, so the
# container reproduces the repo's top-level layout. That is what makes
# `config._repo_root()` — which is `parents[1]` of the config module — resolve
# to /app in the container exactly as it resolves to the checkout locally.
#
# `references` is here because it is read at RUNTIME, not just by tooling:
# `model_for_tier` parses references/model-policy.md on every agent build. Omit
# it and the deploy still succeeds, the container still builds, and the agent
# then dies on its first query with FileNotFoundError — a failure that costs a
# full container build to discover. `test_deploy.py` pins this.
EXTRA_PACKAGES = ("./mining_agents", "./references")

# Passing dry_run=False is not enough to deploy; the caller must also pass this
# phrase. A boolean is too easy to reach by accident, and the accident is
# expensive: a unit test that asserted `deploy(dry_run=False)` raised — written
# when it did — kept calling it after the implementation landed, and spent
# twenty-six minutes creating eight billable Agent Engine instances before
# anyone noticed. Nothing about the call site looked dangerous.
CONFIRM_PHRASE = "yes-deploy-for-real"

_API = f"https://{REGION}-aiplatform.googleapis.com/v1beta1"

# ---------------------------------------------------------------------------
# The single copy of this command lives in docs/phase-3-design.md §5.5.
# This module NEVER executes it — see Ruling 3.
# ---------------------------------------------------------------------------
DOMAIN_BINDING_COMMAND = (
    "gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \\\n"
    '  --member="domain:${GOOGLE_DOMAIN}" \\\n'
    '  --role="roles/aiplatform.user"'
)


def print_domain_binding_warning() -> None:
    """Print the resolved domain-binding command and an explicit warning.

    Ruling 3: this function exists to make the command auditable. It is
    NEVER called from a code path that executes it.
    """
    s = settings()
    resolved = DOMAIN_BINDING_COMMAND.replace(
        "${GOOGLE_CLOUD_PROJECT}", s.project_id
    )
    print("=" * 72)
    print("DOMAIN-WIDE IAM BINDING — REQUIRES EXPLICIT HUMAN APPROVAL")
    print(resolved)
    print()
    print("This grants access to EVERY user in the domain in one action.")
    print("Acceptable only because this is an Argolis sandbox.")
    print("DO NOT copy this binding into a production project.")
    print("This script will NOT run it. Run it yourself if you approve.")
    print("=" * 72)


def deploy_command(
    agent_id: str, display_name: str, engine_id: str | None = None
) -> list[str]:
    """The argv that deploys one entrypoint.

    *engine_id*, when given, makes the deploy UPDATE that instance instead of
    creating another one. Without it a second run of this script would leave
    two instances per agent, each billing, with nothing naming which is live.
    """
    s = settings()
    argv = [
        # The interpreter running this script, not whatever `python` resolves
        # to on PATH — the ADK CLI and its deps live in this one.
        sys.executable,
        "-m",
        "google.adk.cli",
        "deploy",
        "agent_engine",
        f"--project={s.project_id}",
        f"--region={REGION}",
        f"--display_name={display_name}",
    ]
    if engine_id:
        argv.append(f"--agent_engine_id={engine_id}")
    argv += [f"--extra_packages={pkg}" for pkg in EXTRA_PACKAGES]
    # Without this, ADK stages into a timestamped folder under its working
    # directory, which is `packages/` — the tree this repo regenerates and
    # scans. An interrupted deploy then leaves a half-copy of the repo sitting
    # inside it, which the model-policy scan reads as a stray model id.
    argv.append(f"--temp_folder={tempfile.gettempdir()}/adk-stage-{agent_id}")
    argv.append(f"./packages/{agent_id}")
    return argv


def _auth_headers() -> dict[str, str]:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }


def existing_engines() -> dict[str, str]:
    """Map display name -> engine id for every deployed instance.

    Deployment state is read back from the API rather than cached in a local
    file, so re-running from a different machine — or after a `git clean` —
    still updates the live instances instead of duplicating them.

    The identity key is the DISPLAY NAME, because a reasoningEngine carries no
    other field this repo controls: the API returns only name, displayName,
    spec, contextSpec, trafficConfig and timestamps, and the ADK deploy verb
    exposes no way to set a label. So the guarantee above holds exactly as long
    as `registrations()` keeps returning the same display name for an agent.
    Rename one in the catalog and the next deploy will not recognise its live
    instance: it creates a second one and the old keeps running and billing
    under the old name. Renaming an already-deployed agent therefore means
    deleting its old instance by hand.
    """
    s = settings()
    parent = f"projects/{s.project_id}/locations/{REGION}"
    response = requests.get(f"{_API}/{parent}/reasoningEngines", headers=_auth_headers())
    response.raise_for_status()
    return {
        engine["displayName"]: engine["name"].rsplit("/", 1)[1]
        for engine in response.json().get("reasoningEngines", [])
        if engine.get("displayName")
    }


def attach_service_account(engine_id: str, service_account: str) -> None:
    """Point one deployed engine at its tier service account.

    The deploy verb has no flag for this, and an engine left unpatched runs as
    the shared Vertex service agent — which holds none of the per-tier limits
    the access model is built on, so the whole tiering would be decorative.
    """
    s = settings()
    name = f"projects/{s.project_id}/locations/{REGION}/reasoningEngines/{engine_id}"
    response = requests.patch(
        f"{_API}/{name}",
        headers=_auth_headers(),
        params={"updateMask": "spec.service_account"},
        data=json.dumps({"spec": {"serviceAccount": service_account}}),
    )
    response.raise_for_status()


def deploy(
    dry_run: bool = True,
    only: tuple[str, ...] | None = None,
    confirm: str = "",
) -> None:
    """Deploy the externally-callable agents and attach their identities.

    dry_run=True (default) prints the argv and the full registration payload
    per agent and touches no cloud state. dry_run=False runs each deploy, then
    patches the runtime service account onto the resulting instance — but only
    when *confirm* is CONFIRM_PHRASE, so that reaching this by accident takes
    two deliberate arguments rather than one flipped boolean.

    *only* restricts the run to the given agent ids, which is what makes a
    representative-subset demo possible without editing the catalog.

    Ruling 3: DOMAIN_BINDING_COMMAND is printed and never executed.
    """
    if not dry_run and confirm != CONFIRM_PHRASE:
        raise PermissionError(
            "deploy(dry_run=False) creates billable, always-on Agent Engine "
            f"instances. Pass confirm={CONFIRM_PHRASE!r} to proceed. If you are "
            "reading this from a test, the test should be calling dry_run=True."
        )

    entries = list(registrations())
    if only:
        wanted = set(only)
        unknown = wanted - {e["agent_id"] for e in entries}
        if unknown:
            raise KeyError(f"not externally-callable entrypoints: {sorted(unknown)}")
        entries = [e for e in entries if e["agent_id"] in wanted]

    deployed = {} if dry_run else existing_engines()

    for entry in entries:
        agent_id = entry["agent_id"]
        display_name = entry["display_name"]
        service_account = entry["service_account"]
        argv = deploy_command(agent_id, display_name, deployed.get(display_name))

        print(f"# --- {agent_id} ---")
        print(" \\\n  ".join(argv))
        print(f"# Runtime service account: {service_account}")

        if dry_run:
            # Print the full payload — no truncation — so an auditor can read
            # caller_allowlist and guardrails (Ruling 6).
            print("Registration payload:")
            print(json.dumps(entry, indent=2))
            print()
            continue

        subprocess.run(argv, check=True)
        engine_id = existing_engines()[display_name]
        attach_service_account(engine_id, service_account)
        print(f"# deployed {agent_id} as {engine_id}, running as {service_account}")
        print()

    if dry_run:
        print_domain_binding_warning()


if __name__ == "__main__":
    deploy(dry_run=True)
