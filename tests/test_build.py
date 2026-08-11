"""Gate: build all 52 entrypoints and prove every agent resolves to a real table.

Ruling 6 corrections applied:
- test_building_twice_is_stable: asserts key set equals expected 52 agent_ids
  AND that both calls produce the same types per key, not a trivial self-comparison.
- test_all_fifty_two_entrypoints_build: also asserts the built key set equals
  {a.agent_id for a in registrable()} — cross-task coherence check.

Ruling 2 & 3 tests for scripts/deploy.py:
- deploy(dry_run=False) must raise NotImplementedError.
- deploy(dry_run=True) must never call subprocess.run.
- DOMAIN_BINDING_COMMAND must never be subprocess-executed by any code path.
"""
import inspect
import os
import subprocess
from unittest.mock import patch

import pytest

from agents.build import build_all
from agents.catalog.definitions import ALL_AGENTS
from agents.registry import registrable
import scripts.deploy as deploy_module
from scripts.deploy import DOMAIN_BINDING_COMMAND, deploy


def test_all_fifty_two_entrypoints_build():
    built = build_all()
    assert len(built) == 52
    # Cross-task coherence: the registry advertises exactly what the build produces.
    expected_ids = {a.agent_id for a in registrable()}
    assert set(built.keys()) == expected_ids


def test_building_twice_is_stable():
    """Two calls produce the same key set (with correct expected value) and same types.

    Ruling 6: the original set(build_all()) == set(build_all()) is a trivial
    self-comparison that passes on any non-empty dict. We pin the expected key
    set and verify type consistency per key.
    """
    expected_ids = {a.agent_id for a in registrable()}
    first = build_all()
    second = build_all()
    assert set(first.keys()) == expected_ids
    assert set(second.keys()) == expected_ids
    # Both calls produce the same type per key (Workflow for swarms, LlmAgent for deep).
    type_mismatches = [
        agent_id
        for agent_id in expected_ids
        if type(first[agent_id]) is not type(second[agent_id])
    ]
    assert type_mismatches == []


def test_every_one_of_the_hundred_agents_resolves_to_a_real_table():
    """PRD success metric: 100 of 100 agents resolve to a real table.

    The population is pinned before the offender list, not after: `unresolved
    == []` is only meaningful once the loop is known to have iterated 100
    agents rather than an empty catalog.
    """
    assert len(ALL_AGENTS) == 100
    unresolved = [a.agent_id for a in ALL_AGENTS if not a.source_tables]
    assert unresolved == []


# ---------------------------------------------------------------------------
# Ruling 2: deploy(dry_run=False) must raise NotImplementedError
# ---------------------------------------------------------------------------

def test_deploy_dry_run_false_raises_not_implemented():
    """Ruling 2: deploying without the 52 per-agent packages must be refused."""
    with pytest.raises(NotImplementedError) as exc_info:
        deploy(dry_run=False)
    # The error message must name what is missing.
    msg = str(exc_info.value)
    assert "per-agent" in msg or "package" in msg or "directory" in msg


# ---------------------------------------------------------------------------
# Ruling 3: deploy(dry_run=True) must never call subprocess.run,
# and no code path in scripts/deploy.py may execute DOMAIN_BINDING_COMMAND.
# ---------------------------------------------------------------------------

def test_deploy_dry_run_calls_no_subprocess(capsys):
    """Ruling 3: dry_run=True must never invoke a subprocess.

    Patching the attributes on the subprocess and os module objects is global,
    so this catches `import subprocess; subprocess.run(...)` added to deploy.py
    later. It does NOT catch `from subprocess import run`, so the second half
    asserts the module imports no execution machinery at all — the durable
    guarantee, of which "calls nothing today" is only a consequence.
    """
    with patch.object(subprocess, "run") as mock_run, \
         patch.object(subprocess, "call") as mock_call, \
         patch.object(subprocess, "check_call") as mock_check_call, \
         patch.object(subprocess, "check_output") as mock_check_output, \
         patch.object(os, "system") as mock_system, \
         patch.object(os, "popen") as mock_popen:
        deploy(dry_run=True)
        called = {
            name: mock.call_count
            for name, mock in [
                ("subprocess.run", mock_run),
                ("subprocess.call", mock_call),
                ("subprocess.check_call", mock_check_call),
                ("subprocess.check_output", mock_check_output),
                ("os.system", mock_system),
                ("os.popen", mock_popen),
            ]
            if mock.call_count
        }
        assert called == {}, f"dry run executed: {called}"

    # scripts/deploy.py must hold no execution capability whatsoever. This is
    # what makes the mock assertions above durable: a `from subprocess import
    # run` would slip past the patches, but not past this.
    source = inspect.getsource(deploy_module)
    forbidden_imports = [
        "import subprocess",
        "from subprocess",
        "import os",
        "from os import",
    ]
    present = [i for i in forbidden_imports if i in source]
    assert present == [], (
        f"scripts/deploy.py imports execution machinery: {present}. "
        f"The deploy path is human-gated; it must be unable to run anything."
    )


def test_deploy_module_source_never_subprocess_executes_domain_binding_command():
    """Ruling 3: assert no code path in scripts/deploy.py executes DOMAIN_BINDING_COMMAND.

    We verify this structurally: read the module source and confirm that
    DOMAIN_BINDING_COMMAND (or its resolved gcloud form) never appears as an
    argument to subprocess.run / subprocess.call / os.system / os.popen.
    The print_domain_binding_warning function may print it — that is required —
    but must not pass it to any execution function.
    """
    source = inspect.getsource(deploy_module)

    # The command string starts with "gcloud projects add-iam-policy-binding".
    # We assert this literal never appears inside a subprocess call.
    # We do this by checking: subprocess.run|call|check_call|check_output must
    # not appear on lines that also reference DOMAIN_BINDING_COMMAND or
    # "gcloud projects add-iam-policy-binding".
    lines = source.splitlines()
    trigger_terms = [
        "gcloud projects add-iam-policy-binding",
        "DOMAIN_BINDING_COMMAND",
    ]
    exec_terms = [
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "os.system",
        "os.popen",
    ]

    # Check no single line has both an exec term and the domain binding command.
    bad_lines = []
    for lineno, line in enumerate(lines, 1):
        has_exec = any(et in line for et in exec_terms)
        has_binding = any(tt in line for tt in trigger_terms)
        if has_exec and has_binding:
            bad_lines.append((lineno, line.strip()))

    assert bad_lines == [], (
        f"Found line(s) that may execute DOMAIN_BINDING_COMMAND: {bad_lines}"
    )

    # Also confirm DOMAIN_BINDING_COMMAND is defined (it must exist for the audit).
    assert DOMAIN_BINDING_COMMAND
    assert "gcloud projects add-iam-policy-binding" in DOMAIN_BINDING_COMMAND
