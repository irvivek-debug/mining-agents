"""Generate apps/frontend/data.js from the agent catalogue.

WHY GENERATED, NOT PASTED
The five-screen front end was handed over as two HTML files whose agent data
had been injected at runtime by the deployed frontend service. Snapshotting
that injected blob would freeze a copy that drifts from the registry the moment
anyone edits an agent. `catalog_definitions.CATALOG` is the registry's own
source of truth -- 101 AgentCards -- so the screens are built from it directly.

The catalogue and manifest are read from `vendor/agent_registry/`, which holds
verbatim copies of the vault originals. See that directory's README for why
they are vendored and how to refresh them.

The persona and node datasets have no such upstream: they are presentation
content that ships with the design. They live in data-static.js and are edited
by hand, which is stated here so nobody looks for a generator that isn't there.

WHAT IS DERIVED AND WHAT IS AUTHORED
Every per-agent field below is read from the catalogue or the manifest. Two
lookup tables are editorial and marked as such: DEPARTMENT_STAKE (why a board
cares about a department) and the plain-English glosses on value class,
authority and fallback. They are exhaustive over the catalogue's closed enums
-- there is no default branch -- so a new enum value fails here loudly instead
of rendering an empty card on a sales screen.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "agent_registry"
sys.path.insert(0, str(VENDOR))

import catalog_definitions as C  # noqa: E402

OUT = ROOT / "apps" / "frontend" / "data.js"
MANIFEST = VENDOR / "agent_manifest.json"

#: The Gemini Enterprise workspace the agent estate is published into. This is
#: ONE workspace shared by all 101 agents -- it is not a per-agent address. The
#: per-agent address is `interface_url` in the manifest, surfaced as
#: `invokeUrl`, and the two are shown side by side on the screens so a click
#: that says "this agent" actually reaches that agent.
GEMINI_ENTERPRISE_URL = (
    "https://vertexaisearch.cloud.google.com/home/cid/"
    "af13d38d-d69f-4dce-9076-f12625444a86?hl=en_US"
)

#: The four architectural tiers the screens group by, keyed off the catalogue's
#: own `pattern` enum so a new pattern surfaces as a KeyError here rather than
#: silently vanishing from the topology view.
TIER_OF = {
    "L0_STRATEGIC": "L0",
    "A_COORDINATOR": "L2",
    "A_SPECIALIST": "L2",
    "A_CRITIC": "L2",
    "B_DEEP": "L3",
}

# --------------------------------------------------------------------------
# Editorial lexicons. Exhaustive over closed enums -- no default branch.
# --------------------------------------------------------------------------

#: What the agent's role means as a decision right, in the language an
#: executive uses. `{dept}` interpolates the department's own label.
PATTERN_OWNS = {
    "L0_STRATEGIC": "Sets the {dept} envelope every other agent optimises inside.",
    "A_COORDINATOR": "Owns the {dept} call end to end: commissions its specialists, weighs what they return, and puts a single recommendation forward.",
    "A_SPECIALIST": "Answers one question inside {dept} and hands the answer up. It evidences; it does not decide.",
    "A_CRITIC": "Tries to break the recommendation before a human sees it. A claim it cannot trace to a cited table does not ship.",
    "B_DEEP": "Computes the {dept} number the rest of the estate argues about — deterministically, the same answer every time.",
}

#: Why the board cares about this department. Editorial framing, one line each.
DEPARTMENT_STAKE = {
    "Commercial/Finance/Strategy": "Where the capital goes and what the plan is worth.",
    "Exploration/Geology": "What is actually in the ground, and how confident we are.",
    "Mine Planning/Operations": "Whether the plan we committed to is the plan being mined.",
    "Fleet/Haulage": "The largest single line of operating cost that moves every day.",
    "Mineral Processing/Plant": "Where recovery is won or lost — a point of recovery is a point of revenue.",
    "Asset Integrity/Maintenance": "Unplanned downtime, and the capital we spend avoiding it.",
    "Supply Chain/Logistics": "Whether what we produce reaches a buyer on time and on spec.",
    "Safety/OHSE/ESG": "Licence to operate. The one column that cannot be traded off.",
}

#: How a value class reads on the P&L.
VALUE_CLASS_PL = {
    "Class A (Cash)": "Moves cash directly — its output changes what the business spends or banks this period.",
    "Class B (Metric)": "Moves an operating metric — throughput, recovery, availability — that converts to cash through the plan.",
    "Class C (Risk)": "Moves exposure rather than revenue. The return is the incident, breach or penalty that does not happen.",
}

#: What the agent is structurally unable to do, from authority level and HITL.
AUTHORITY_CANNOT = {
    ("L1_ADVISORY", True): "Recommends only. It cannot execute its own conclusion — the recommendation is held until a named human releases it.",
    ("L1_ADVISORY", False): "Recommends only. Its output is evidence for another agent or a person to act on; it carries no authority to act.",
    ("L2_BOUNDED_ACTION", True): "Acts inside a bounded envelope, and every action leaves that envelope through a dual-key human release. No write access to plant control.",
    ("L2_BOUNDED_ACTION", False): "Acts inside a bounded envelope its coordinator sets. It cannot widen that envelope, and holds no write access to plant control.",
}

#: What happens when the agent cannot reach a grounded answer.
FALLBACK_PLAIN = {
    "DETERMINISTIC_PHYSICS_FALLBACK": "Hands the question to the deterministic physics solver and returns that answer. It does not guess to fill a gap.",
}


def trigger_line(a) -> str:
    """How this agent gets invoked, from endpoint type and caller allowlist."""
    if a.endpoint_type.value == "in_process":
        parent = a.parent_coordinator_id
        return (f"Dispatched in-process by {parent}." if parent
                else "Dispatched in-process by its swarm coordinator.")
    callers = [c for c in (a.caller_allowlist or []) if c]
    if a.is_externally_callable and callers:
        return "Called over HTTPS by " + ", ".join(callers) + "."
    if a.is_externally_callable:
        return "Called over HTTPS by the swarm orchestrator."
    return "Called over HTTPS by the swarm orchestrator only — not externally reachable."


def approval_line(a) -> str:
    if a.hitl_required:
        return "Dual-key human release. A named operator and a second approver must both sign."
    return "No human gate. The output is advisory and returns to the agent that asked for it."


def lands_line(a) -> str:
    if a.hitl_required:
        return "An ERP staging buffer, held pending release. Never a PLC, never SCADA."
    return "Its coordinator's evidence set, cited and timestamped. Nothing reaches plant control."


def business(a) -> dict:
    dept = a.department.value
    return {
        "owns": PATTERN_OWNS[a.pattern.value].format(dept=dept),
        "boardStake": DEPARTMENT_STAKE[dept],
        "answersTo": f"{a.persona} — {dept}",
        "plMove": VALUE_CLASS_PL[a.value_class.value],
        "cannot": AUTHORITY_CANNOT[(a.authority_level.value, bool(a.hitl_required))],
        "onFailure": FALLBACK_PLAIN[a.fallback_strategy],
    }


def flow(a) -> list[dict]:
    """The five-stage decision flow, every stage read from a catalogue field."""
    tables = list(a.source_tables)
    tools = list(a.tools)
    return [
        {"key": "trigger", "label": "Trigger",
         "value": "Invoked via " + a.endpoint_type.value.replace("_", "-"),
         "detail": trigger_line(a)},
        {"key": "reads", "label": "Reads",
         "value": f"{len(tables)} grounding " + ("table" if len(tables) == 1 else "tables"),
         "detail": ", ".join(tables)},
        {"key": "decides", "label": "Decides",
         "value": a.governing_equation,
         "detail": ("Applied through " + ", ".join(tools) + "."
                    if tools else "Applied directly by the agent — no external solver in the path.")},
        {"key": "approval", "label": "Approval",
         "value": "Human release required" if a.hitl_required else "Advisory — no gate",
         "detail": approval_line(a)},
        {"key": "lands", "label": "Lands in",
         "value": "ERP staging buffer" if a.hitl_required else "Coordinator evidence set",
         "detail": lands_line(a)},
    ]


def card(a, manifest: dict) -> dict:
    m = manifest.get(a.agent_id, {})
    return {
        "id": a.agent_id,
        "name": a.name,
        "tierKey": TIER_OF[a.pattern.value],
        "pattern": a.pattern.value,
        "apqc": f"APQC {a.apqc_code}",
        "department": a.department.value,
        "persona": a.persona,
        "process": a.persona,
        "authority": a.authority_level.value.replace("_", " "),
        "valueClass": a.value_class.value,
        "hitl": a.hitl_required,
        "endpoint": a.endpoint_type.value,
        "parent": a.parent_coordinator_id,
        "governingEquation": a.governing_equation,
        "mechanism": a.description,
        "provenance": [
            {"name": t, "type": "SAP" if "erp" in t.lower() else "BQ"}
            for t in a.source_tables
        ],
        "tools": list(a.tools),
        "model": a.model_id,
        # Two different addresses, deliberately both present. See
        # GEMINI_ENTERPRISE_URL above for why one is not a substitute for the
        # other.
        "geminiUrl": GEMINI_ENTERPRISE_URL,
        "invokeUrl": m.get("interface_url", ""),
        "urn": m.get("urn", ""),
        "business": business(a),
        "flow": flow(a),
    }


def main() -> None:
    manifest = {
        r["agent_id"]: r
        for r in json.loads(MANIFEST.read_text())["registered_agents"]
    }

    cat = sorted(C.CATALOG, key=lambda a: (TIER_OF[a.pattern.value], a.agent_id))
    agents = {a.agent_id: card(a, manifest) for a in cat}

    missing = [k for k, v in agents.items() if not v["invokeUrl"]]
    if missing:
        raise SystemExit(
            f"{len(missing)} agents have no interface_url in the manifest: "
            f"{missing[:5]}. A launch button that points nowhere is worse than "
            f"no launch button, so this is a hard failure."
        )

    counts: dict[str, int] = {}
    for a in agents.values():
        counts[a["tierKey"]] = counts.get(a["tierKey"], 0) + 1

    body = (
        "/* GENERATED by scripts/build_frontend_data.py -- do not edit by hand.\n"
        " * Source: the agent registry's own catalogue (101 AgentCards) plus\n"
        " * agent_manifest.json for per-agent invoke URLs. Regenerate after any\n"
        " * catalogue change; a stale copy here is the failure this generator\n"
        " * exists to prevent. */\n"
        f"window.geminiEnterpriseUrl = {json.dumps(GEMINI_ENTERPRISE_URL)};\n\n"
        f"window.agentCatalogData = {json.dumps(agents, indent=1)};\n\n"
        f"window.agentTierCounts = {json.dumps(counts, indent=1)};\n"
    )
    OUT.write_text(body)
    print(f"wrote {OUT.relative_to(ROOT)}  {len(agents)} agents  tiers={counts}  "
          f"invoke URLs={len(agents) - len(missing)}/{len(agents)}")


if __name__ == "__main__":
    main()
