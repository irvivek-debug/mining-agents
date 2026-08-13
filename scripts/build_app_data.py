"""Export the JSON the two demo applications read.

Both applications must show what is actually deployed, so the catalog export
derives from `mining_agents.catalog.definitions` -- the same module that builds
the agents -- rather than from a hand-maintained copy that would drift the first
time an agent changed.

The graph export has two sources. BigQuery is authoritative when credentials
are available. Without them it falls back to `data/profile/` and the generated
parquet, which hold the same entities. Both paths write the same shape, and the
file records which one produced it, because a graph drawn from a local cache is
a weaker claim than one drawn from the warehouse and the screen says so.

Run: python -m scripts.build_app_data [--out apps/shared/data]
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import re

import yaml

from mining_agents.catalog.definitions import ALL_AGENTS
from mining_agents.tools.graph_traverse import TRAVERSALS
from scripts.build_workspace_data import build_workspace

REPO = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "apps" / "shared" / "data"
PROFILE = REPO / "data" / "profile"
GENERATED = REPO / "data" / "generated"
PERSONA_PROFILES = REPO / "docs" / "persona-profiles.yaml"

# The one dollar figure this repo actually establishes. Everything else is the
# client's to supply; see docs/superpowers/specs/2026-08-13-applications-design.md.
MILL_DOWNTIME_USD_PER_HOUR = 145_000

# APQC code -> the process name this catalog uses it for. Compound codes on
# agents that span two domains are split on "/" and looked up per part.
APQC_NAMES = {
    "2.0.1": "Develop and manage products and services",
    "4.1.2": "Manage inventory and materials",
    "4.2.2": "Manage production operations",
    "4.3.1": "Manage logistics and transportation",
    "5.2.1": "Procure materials and services",
    "9.1.2": "Manage health, safety and environment",
    "11.0.3": "Manage plant and asset maintenance",
}


def _traversal_holders(traversal: str) -> dict:
    """Which agents run a traversal, read off the catalog rather than typed here.

    The graph screen claims "this is the traversal S01 runs". That claim has to
    come from the same definitions that deploy S01, or it becomes a caption that
    quietly goes stale.
    """
    holders = [a for a in ALL_AGENTS if traversal in (getattr(a, "traversals", None) or ())]
    return {
        "agents": sorted(a.agent_id for a in holders),
        "entrypoints": sorted(
            a.agent_id for a in holders if a.swarm_role in (None, "coordinator")
        ),
    }


# The three property graphs that deployed agents actually traverse. A fourth
# exists in code -- MiningOntologyGraph / ontology_related -- but is granted to
# zero agents (tests/test_demo_scenarios.py pins that at exactly zero), so it is
# not exported: a screen showing a graph no agent reads would be showing scenery.
GRAPH_META = {
    "asset": {
        "bigquery_graph": "MiningAssetGraph",
        "traversal": "blast_radius",
        "question": "If this asset fails, what fails behind it?",
    },
    "supply_chain": {
        "bigquery_graph": "MiningSupplyChainGraph",
        "traversal": "stockout_exposure",
        "question": "If this part runs out, which work orders stall?",
    },
    "safety": {
        "bigquery_graph": "MiningOperationsSafetyGraph",
        "traversal": "fatigue_to_incident",
        "question": "Which fatigue readings precede an operator's incident?",
    },
}

def _traversal_sql(traversal: str) -> dict:
    """The deployed SQL, lifted off the tool rather than retyped for the screen.

    The graph screen prints this text and then walks the same pattern in the
    browser. Retyping it here would let the two drift, and the whole claim of
    that screen is that what it runs is what the agent runs. The COLUMNS
    aliases are parsed out of the same string, so a renamed column renames the
    table header instead of silently leaving it stale.
    """
    spec = TRAVERSALS[traversal]
    columns = re.findall(r"\bAS\s+(\w+)", spec.sql)
    if not columns:
        raise SystemExit(f"no COLUMNS aliases parsed out of {traversal!r} SQL")
    return {
        "sql": spec.sql.strip(),
        "params": list(spec.params),
        "columns": columns,
        "tables_read": list(spec.tables_read),
    }


for _name, _meta in GRAPH_META.items():
    _meta.update(_traversal_holders(_meta["traversal"]))
    _meta.update(_traversal_sql(_meta["traversal"]))


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _entrypoints() -> list:
    """The 52 externally callable agents: deep agents and swarm coordinators.

    A specialist or critic is reachable only through its coordinator, so it is
    not an entrypoint even though it is an agent.
    """
    return [a for a in ALL_AGENTS if a.swarm_role in (None, "coordinator")]


def _agent_record(agent) -> dict:
    return {
        "agent_id": agent.agent_id,
        "display_name": agent.display_name,
        "pattern": agent.pattern,
        "swarm_id": agent.swarm_id,
        "swarm_role": agent.swarm_role,
        "apqc_code": agent.apqc_code,
        "apqc_names": [
            APQC_NAMES.get(part.strip(), part.strip())
            for part in agent.apqc_code.split("/")
        ],
        "persona": agent.persona,
        "value_branch": agent.value_branch,
        "model_tier": agent.model_tier,
        "hitl_required": agent.hitl_required,
        "source_tables": list(agent.source_tables),
        "tools": list(agent.tools),
        "traversals": list(getattr(agent, "traversals", ()) or ()),
        "models": list(getattr(agent, "models", ()) or ()),
        "is_entrypoint": agent.swarm_role in (None, "coordinator"),
    }


def build_catalog() -> dict:
    entries = _entrypoints()

    swarms: dict[str, dict] = {}
    for agent in ALL_AGENTS:
        if agent.swarm_id is None:
            continue
        swarm = swarms.setdefault(
            agent.swarm_id, {"coordinator": None, "specialists": [], "critic": None}
        )
        if agent.swarm_role == "coordinator":
            swarm["coordinator"] = agent.agent_id
        elif agent.swarm_role == "critic":
            swarm["critic"] = agent.agent_id
        else:
            swarm["specialists"].append(agent.agent_id)

    return {
        "generated_at": _now(),
        "source": "mining_agents.catalog.definitions",
        "counts": {
            "agent_nodes": len(ALL_AGENTS),
            "entrypoints": len(entries),
            "swarms": len(swarms),
            "deep_agents": sum(1 for a in entries if a.pattern == "B"),
            "hitl_entrypoints": sum(1 for a in entries if a.hitl_required),
        },
        "by_persona": _counted(entries, lambda a: a.persona),
        "by_value_branch": _counted(entries, lambda a: a.value_branch),
        "by_apqc": _counted(entries, lambda a: a.apqc_code),
        # The literal code strings above include seven compound codes, and the
        # catalog spells two pairs both ways round -- "4.3.1 / 9.1.2" and
        # "9.1.2 / 4.3.1" are one process pair filed as two. Rolling up to the
        # atomic code is what makes the process view answer "how much of the
        # estate touches health and safety", which is the question a client
        # asks. An agent spanning two domains counts in both, so these counts
        # sum above the entrypoint total by design.
        "by_apqc_code": _counted_multi(
            entries, lambda a: [p.strip() for p in a.apqc_code.split("/")]
        ),
        "compound_apqc_codes": sorted(
            {a.apqc_code for a in entries if "/" in a.apqc_code}
        ),
        "tool_usage": dict(
            collections.Counter(t for a in entries for t in a.tools).most_common()
        ),
        "apqc_names": APQC_NAMES,
        "swarms": swarms,
        "agents": [_agent_record(a) for a in ALL_AGENTS],
    }


def _counted_multi(entries, keys) -> dict:
    """Like _counted, but an entry may belong to several groups at once."""
    grouped = collections.defaultdict(list)
    for agent in entries:
        for key in keys(agent):
            grouped[key].append(agent.agent_id)
    return {
        k: {"count": len(v), "agents": sorted(v)}
        for k, v in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    }


def _counted(entries, key) -> dict:
    """Group entrypoint ids by a key, ordered by descending group size."""
    grouped = collections.defaultdict(list)
    for agent in entries:
        grouped[key(agent)].append(agent.agent_id)
    return {
        k: {"count": len(v), "agents": sorted(v)}
        for k, v in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    }


def build_personas(catalog: dict) -> dict:
    """Merge the transcribed persona profiles with live catalog counts.

    The quotes and journeys are human-transcribed from
    docs/personas-and-value-tree.md with line citations. The agent lists come
    from the catalog, so a persona's roster cannot drift from what is deployed.
    """
    profiles = yaml.safe_load(PERSONA_PROFILES.read_text())
    by_persona = catalog["by_persona"]

    out = {}
    for code, profile in sorted(profiles.items()):
        catalog_agents = by_persona.get(code, {}).get("agents", [])
        if sorted(profile["agents"]) != sorted(catalog_agents):
            raise SystemExit(
                f"{code}: persona-profiles.yaml lists {sorted(profile['agents'])} "
                f"but the catalog says {sorted(catalog_agents)}. The catalog wins; "
                "fix docs/persona-profiles.yaml."
            )
        entry = dict(profile)
        entry["agents"] = catalog_agents
        entry["agent_count"] = len(catalog_agents)
        entry["hitl_agents"] = sorted(
            a["agent_id"]
            for a in catalog["agents"]
            if a["persona"] == code and a["is_entrypoint"] and a["hitl_required"]
        )
        out[code] = entry
    return {"generated_at": _now(), "source": str(PERSONA_PROFILES.relative_to(REPO)),
            "personas": out}


# --------------------------------------------------------------------------
# Graph export
# --------------------------------------------------------------------------

def build_graph_from_local() -> dict:
    """Build the property graphs from data/profile and the generated parquet.

    Used when BigQuery credentials are unavailable. Every entity here exists in
    the warehouse too; this path just reads the profiled copy.
    """
    import pandas as pd

    stats = json.loads((PROFILE / "stats.json").read_text())

    nodes: list[dict] = []
    edges: list[dict] = []

    # --- MiningAssetGraph: assets and their DEPENDS_ON chain ---
    for asset in stats["assets"]:
        nodes.append({
            "id": asset["asset_id"],
            "label": asset["asset_id"],
            "type": "Asset",
            "graph": "asset",
            "detail": {
                "name": asset["asset_name"],
                "asset_type": asset["asset_type"],
                "criticality": asset["criticality_rating"],
                "installed": asset["installed"],
                "state_keys": sorted(json.loads(asset["current_state"])),
            },
        })
    for dep in stats["asset_dependencies"]:
        edges.append({
            "source": dep["source_id"],
            "target": dep["target_id"],
            "label": "DEPENDS_ON",
            "graph": "asset",
            "weight": dep["impact_score"],
            "detail": {"dependency_type": dep["dependency_type"],
                       "impact_score": dep["impact_score"]},
        })

    # --- MiningSupplyChainGraph: Asset -> WorkOrder -> SparePart ---
    # The same five assets anchor this graph too. They are emitted a second time
    # under graph="supply_chain" rather than shared with the asset graph: every
    # HAS_WORK_ORDER edge needs its source node present in the view the screen
    # renders, and a screen filtering on graph would otherwise draw 126 edges
    # from nodes it never added.
    for asset in stats["assets"]:
        nodes.append({
            "id": asset["asset_id"],
            "label": asset["asset_id"],
            "type": "Asset",
            "graph": "supply_chain",
            "detail": {"name": asset["asset_name"],
                       "criticality": asset["criticality_rating"]},
        })

    work_orders = pd.read_parquet(GENERATED / "erp_work_orders.parquet")
    logs = pd.read_parquet(GENERATED / "maintenance_logs.parquet")
    inventory = pd.read_parquet(GENERATED / "inventory_levels.parquet")

    wo_parts = [
        (row.work_order_id, part)
        for row in logs.itertuples()
        for part in (row.parts_replaced if row.parts_replaced is not None else [])
    ]
    linked_orders = {wo for wo, _ in wo_parts}
    used_parts = {p for _, p in wo_parts}

    wo_by_id = {r.work_order_id: r for r in work_orders.itertuples()}
    for wo_id in sorted(linked_orders):
        row = wo_by_id.get(wo_id)
        nodes.append({
            "id": wo_id,
            "label": wo_id,
            "type": "WorkOrder",
            "graph": "supply_chain",
            "detail": {
                "asset_id": _field(row, "asset_id"),
                "priority": _field(row, "priority"),
                "status": _field(row, "status"),
                "repair_cost": _field(row, "repair_cost"),
                "description": _field(row, "description"),
            } if row is not None else {},
        })
        if row is not None and getattr(row, "asset_id", None):
            edges.append({"source": row.asset_id, "target": wo_id,
                          "label": "HAS_WORK_ORDER", "graph": "supply_chain"})

    stocked = {r.part_number: r for r in inventory.itertuples()}
    for part in sorted(used_parts):
        row = stocked.get(part)
        nodes.append({
            "id": part,
            "label": part,
            "type": "SparePart",
            "graph": "supply_chain",
            "detail": {
                "description": _field(row, "part_description"),
                "stock_level": _field(row, "stock_level"),
                "reorder_point_limit": _field(row, "reorder_point_limit"),
                "lead_time_days": _field(row, "lead_time_days"),
                "unit_price_usd": _field(row, "unit_price_usd"),
                "below_reorder_point": bool(
                    _field(row, "stock_level") <= _field(row, "reorder_point_limit")
                ),
            } if row is not None else {"stocked": False},
        })
    # Direction matters and is not arbitrary: MiningSupplyChainGraph declares
    # WorkOrder -[REPLACED_PART]-> SparePart, which is why stockout_exposure
    # spells the hop as (p:SparePart) <-[:REPLACED_PART]- (wo:WorkOrder). A
    # screen that draws the arrow the other way is drawing an edge the
    # warehouse does not have.
    for wo_id, part in sorted(set(wo_parts)):
        edges.append({"source": wo_id, "target": part,
                      "label": "REPLACED_PART", "graph": "supply_chain"})

    # --- MiningOperationsSafetyGraph: FatigueLog -> Operator -> Vehicle -> Incident ---
    fatigue = pd.read_parquet(GENERATED / "fatigue_logs_node.parquet")
    alerts = fatigue[fatigue["fatigue_alert_triggered"]]
    for row in alerts.itertuples():
        nodes.append({
            "id": row.log_id,
            "label": row.log_id[:8],
            "type": "FatigueLog",
            "graph": "safety",
            "detail": {
                "timestamp": row.timestamp.isoformat(),
                "operator_id": row.operator_id,
                "heart_rate_bpm": _num(row.heart_rate_bpm),
                "sleep_deficit_hours": _num(row.sleep_deficit_hours),
                "microsleep_events_detected": _num(row.microsleep_events_detected),
            },
        })
        edges.append({"source": row.log_id, "target": row.operator_id,
                      "label": "LOGGED_FOR", "graph": "safety"})

    for operator in sorted(fatigue["operator_id"].unique()):
        readings = fatigue[fatigue["operator_id"] == operator]
        nodes.append({
            "id": operator,
            "label": operator,
            "type": "Operator",
            "graph": "safety",
            "detail": {
                "fatigue_readings": int(len(readings)),
                "alerts_triggered": int(readings["fatigue_alert_triggered"].sum()),
                "max_sleep_deficit_hours": _num(readings["sleep_deficit_hours"].max()),
            },
        })

    vehicles = {v["vehicle_id"]: v for v in stats["fleet_vehicles_sample"]}
    seen_vehicles: set[str] = set()
    for assignment in stats["operator_assignments"]:
        vehicle_id = assignment["vehicle_id"]
        if vehicle_id not in seen_vehicles:
            seen_vehicles.add(vehicle_id)
            vehicle = vehicles.get(vehicle_id, {})
            nodes.append({
                "id": vehicle_id, "label": vehicle_id, "type": "Vehicle",
                "graph": "safety",
                "detail": {"model": vehicle.get("model"),
                           "status": vehicle.get("operational_status"),
                           "payload_capacity_tons": vehicle.get("payload_capacity_tons")},
            })
        edges.append({"source": assignment["operator_id"], "target": vehicle_id,
                      "label": "OPERATES", "graph": "safety",
                      "detail": {"shift_date": assignment["shift_date"],
                                 "shift_type": assignment["shift_type"]}})

    # safety_incidents has neither a parquet nor an entry in the calibration
    # profile, so severity_level -- a column fatigue_to_incident selects -- is
    # not locally derivable. It is declared here as an explicit null rather than
    # left absent, so the screen can print "not in local files" in that cell
    # instead of an empty one that reads as a severity of nothing.
    for involvement in stats["incident_involvements"]:
        incident_id = involvement["incident_id"]
        nodes.append({"id": incident_id, "label": incident_id, "type": "Incident",
                      "graph": "safety", "detail": {"severity_level": None}})
        edges.append({"source": involvement["vehicle_id"], "target": incident_id,
                      "label": "INVOLVED_IN", "graph": "safety"})

    # Every graph below shows less than the whole table it draws from. The
    # sentences are built from the same frames that built the nodes, so a screen
    # quoting them cannot claim a ratio the export does not hold.
    assigned_operators = {a["operator_id"] for a in stats["operator_assignments"]}
    scope = {
        "asset": (
            f"All {len(stats['assets'])} assets and all "
            f"{len(stats['asset_dependencies'])} dependency edges. Nothing filtered."
        ),
        "supply_chain": (
            f"Work orders that consumed a part: {len(linked_orders)} of "
            f"{len(work_orders)}. Parts consumed: {len(used_parts)} of "
            f"{len(inventory)} held in inventory."
        ),
        "safety": (
            f"Fatigue logs that raised an alert: {len(alerts)} of {len(fatigue)}. "
            f"Only {len(assigned_operators)} of {fatigue['operator_id'].nunique()} "
            "operators hold a vehicle assignment, so the traversal returns rows "
            "for those and is empty for the rest."
        ),
    }
    # Provenance, stated at the precision a screen can repeat. These are two
    # different vintages of the same site and saying so matters: stats.json
    # self-describes as the calibration profile captured BEFORE the data was
    # regenerated, and it is the only local source for the edge tables, which
    # have no parquet. So the entities come from the older snapshot and the
    # measurements from the current one. BigQuery settles both; re-run this
    # export against it once credentials are back.
    source = (
        "local files, two vintages: asset, vehicle, assignment and incident "
        f"records from {(PROFILE / 'stats.json').relative_to(REPO)} "
        f"({stats['_note'].rstrip('.')}); work orders, parts and fatigue logs "
        f"from {GENERATED.relative_to(REPO)}/*.parquet, the current generated "
        "data. BigQuery is authoritative for both and was unreachable at build "
        "time."
    )
    return _assemble_graph(nodes, edges, source=source, scope=scope)


def _field(row, name):
    """Read a column off an itertuples row, refusing to invent a missing one.

    getattr(row, name, None) is the obvious spelling and the wrong one: it
    returns None for a column that does not exist, which is indistinguishable
    from a column that exists and is null. That is how every SparePart on the
    supply chain screen came to render an empty price -- inventory_levels calls
    the column stock_level, not quantity_on_hand, and nothing said so.
    """
    if not hasattr(row, name):
        raise SystemExit(
            f"column {name!r} is not in this frame; available: "
            f"{sorted(f for f in row._fields if not f.startswith('_'))}"
        )
    return _num(getattr(row, name))


def _num(value):
    """JSON cannot hold numpy scalars or NaN; normalise both away."""
    if value is None:
        return None
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return value
    if as_float != as_float:  # NaN
        return None
    return int(as_float) if as_float.is_integer() else round(as_float, 4)


def _assemble_graph(nodes: list[dict], edges: list[dict], source: str,
                    scope: dict[str, str]) -> dict:
    """Deduplicate, then record per-graph counts so a screen can state its scale.

    Identity is (graph, id), not id: an asset is a node of both the asset graph
    and the supply chain graph, and collapsing the two would strip the supply
    chain view of the endpoints its HAS_WORK_ORDER edges point at.
    """
    unique_nodes = {(n["graph"], n["id"]): n for n in nodes}
    unique_edges = {
        (e["graph"], e["source"], e["target"], e["label"]): e for e in edges
    }
    node_list = sorted(unique_nodes.values(), key=lambda n: (n["graph"], n["type"], n["id"]))
    edge_list = sorted(unique_edges.values(), key=lambda e: (e["graph"], e["source"], e["target"]))

    per_graph = {}
    for name in sorted({n["graph"] for n in node_list}):
        graph_nodes = [n for n in node_list if n["graph"] == name]
        graph_edges = [e for e in edge_list if e["graph"] == name]
        present = {n["id"] for n in graph_nodes}
        dangling = sorted(
            {e["source"] for e in graph_edges if e["source"] not in present}
            | {e["target"] for e in graph_edges if e["target"] not in present}
        )
        if dangling:
            raise SystemExit(
                f"graph {name!r} has edges pointing at {len(dangling)} node(s) it "
                f"does not contain: {dangling[:5]}. A renderer would silently drop "
                "those edges, so the screen would understate the graph."
            )
        per_graph[name] = dict(
            GRAPH_META[name],
            scope=scope.get(name),
            nodes=len(graph_nodes),
            edges=len(graph_edges),
            node_types=dict(collections.Counter(n["type"] for n in graph_nodes)),
            edge_labels=dict(collections.Counter(e["label"] for e in graph_edges)),
        )

    return {
        "generated_at": _now(),
        "source": source,
        "graphs": per_graph,
        "nodes": node_list,
        "edges": edge_list,
    }


# The CEO tree from docs/personas-and-value-tree.md section 1, rooted on AISC
# per tonne, expressed as compositions of the catalog's finer value_branch
# values. The catalog decides membership; this only says which branch a
# value_branch rolls into, and build_value_tree refuses to emit a tree whose
# parts do not add back to 52.
CEO_TREE = {
    "B1": {
        "title": "Asset availability and unplanned downtime",
        "apqc": "11.0.3",
        "branches": ["asset_reliability", "maintenance_execution"],
        "mechanism": (
            "Detect the fault before it stops the mill, and rank what to fix by "
            "what fails behind it rather than by who asked loudest."
        ),
        "anchored": True,
    },
    "B2": {
        "title": "Ore realisation — grade and dilution against plan",
        "apqc": "2.0.1",
        "branches": ["geology"],
        "mechanism": (
            "Reconcile what the block model promised against what the mill "
            "received, so dilution is caught in the pit rather than in the "
            "month-end variance."
        ),
        "anchored": False,
    },
    "B3": {
        "title": "Processing recovery and throughput",
        "apqc": "11.0.3",
        "branches": ["processing"],
        "mechanism": (
            "Hold recovery against feed variability by moving the plant set "
            "points on evidence rather than on the last shift's habit."
        ),
        "anchored": False,
    },
    "B4": {
        "title": "Haulage productivity and cycle efficiency",
        "apqc": "11.0.1",
        "branches": ["mine_ops"],
        "mechanism": (
            "Find the queue, the detour and the idling truck while the shift is "
            "still running and the dispatch can still change."
        ),
        "anchored": False,
    },
    "B5": {
        "title": "Materials and procurement cost leakage",
        "apqc": "4.1.2 / 3.0.1",
        "branches": ["supply_chain", "procurement"],
        "mechanism": (
            "Know a part will not be on the shelf before the crew is standing at "
            "the store, and buy it on a contract someone checked."
        ),
        "anchored": False,
    },
    "B6": {
        "title": "Safety, fatigue and licence to operate",
        "apqc": "9.1.2",
        "branches": ["safety"],
        "mechanism": (
            "Connect the fatigue signal to the operator, the vehicle and the "
            "incident, so the intervention lands before the incident does."
        ),
        "anchored": False,
    },
}

# S12 is deliberately not a branch: it is the convergence layer where all six
# resolve into one narrative, and the CEO/GM surface.
CONVERGENCE_BRANCH = "site_wide"


def build_value_tree(catalog: dict) -> dict:
    """The six-branch CEO tree, reconciled against the catalog.

    docs/personas-and-value-tree.md carries an arithmetic slip here: its table
    gives Branch 6 a count of 10 while listing 9 entrypoints, which absorbs S12
    into a branch the same document's prose explicitly places above all six. The
    catalog settles it -- safety holds 9, site_wide holds S12 alone -- and the
    assertion below stops that slip from reaching a screen.
    """
    by_branch = catalog["by_value_branch"]
    tree, claimed = [], []
    for code, spec in CEO_TREE.items():
        agents = sorted(
            a for b in spec["branches"] for a in by_branch.get(b, {}).get("agents", [])
        )
        claimed += agents
        tree.append(dict(spec, code=code, agents=agents, count=len(agents),
                         personas=sorted({
                             a["persona"] for a in catalog["agents"]
                             if a["agent_id"] in set(agents) and a["persona"]
                         })))

    convergence = by_branch.get(CONVERGENCE_BRANCH, {}).get("agents", [])
    total = len(claimed) + len(convergence)
    expected = catalog["counts"]["entrypoints"]
    if sorted(claimed + convergence) != sorted(
        a["agent_id"] for a in catalog["agents"] if a["is_entrypoint"]
    ):
        raise SystemExit(
            f"the CEO tree covers {total} entrypoints, the catalog has {expected}. "
            "Every entrypoint must land in exactly one branch or in the "
            "convergence layer; re-derive CEO_TREE against the catalog."
        )

    return {
        "root": "All-in Sustaining Cost (AISC) per tonne",
        "root_source": "docs/personas-and-value-tree.md section 1",
        "branches": tree,
        "convergence": {
            "agents": convergence,
            "note": (
                "S12 is deliberately not a branch. It sits above the six as the "
                "layer where every branch's day resolves into one narrative, "
                "which is also the CEO and GM surface."
            ),
        },
    }


def build_facts() -> dict:
    """The site as the demo actually holds it, counted rather than remembered.

    Every entry carries the file it was counted from, so screen 1.2 can cite a
    source per figure. Anything the local files cannot settle is left out
    entirely rather than filled in from an earlier note -- the fleet size is the
    live example: data/profile only keeps a three-row vehicle sample, so this
    export cannot honestly state how many vehicles the site runs.
    """
    import pandas as pd

    def parquet(name):
        return pd.read_parquet(GENERATED / f"{name}.parquet")

    telemetry = parquet("telemetry_stream")
    work_orders = parquet("erp_work_orders")
    fatigue = parquet("fatigue_logs_node")
    inventory = parquet("inventory_levels")
    stats = json.loads((PROFILE / "stats.json").read_text())
    generated = f"{GENERATED.relative_to(REPO)}"

    def entry(label, value, unit, source):
        return {"label": label, "value": value, "unit": unit, "source": source}

    return {
        "generated_at": _now(),
        "mill_downtime_usd_per_hour": MILL_DOWNTIME_USD_PER_HOUR,
        "mill_downtime_source": "docs/personas-and-value-tree.md",
        "note": (
            "This is the only monetary figure this repository establishes. Every "
            "other magnitude renders as [CLIENT INPUT REQUIRED]."
        ),
        "site": [
            entry("Assets under management", len(stats["assets"]), "assets",
                  "data/profile/stats.json"),
            entry("Telemetry readings", len(telemetry), "readings",
                  f"{generated}/telemetry_stream.parquet"),
            entry("Distinct telemetry metrics", telemetry["metric_name"].nunique(),
                  "metrics", f"{generated}/telemetry_stream.parquet"),
            entry("Work orders", len(work_orders), "orders",
                  f"{generated}/erp_work_orders.parquet"),
            entry("Parts held in inventory", len(inventory), "SKUs",
                  f"{generated}/inventory_levels.parquet"),
            entry("Parts at or below reorder point",
                  int((inventory["stock_level"] <= inventory["reorder_point_limit"]).sum()),
                  "SKUs", f"{generated}/inventory_levels.parquet"),
            entry("Operators monitored for fatigue", fatigue["operator_id"].nunique(),
                  "operators", f"{generated}/fatigue_logs_node.parquet"),
            entry("Fatigue readings", len(fatigue), "readings",
                  f"{generated}/fatigue_logs_node.parquet"),
            entry("Maintenance log entries", len(parquet("maintenance_logs")), "entries",
                  f"{generated}/maintenance_logs.parquet"),
            entry("Geological block model cells", len(parquet("geological_block_models")),
                  "blocks", f"{generated}/geological_block_models.parquet"),
            entry("Drill assay intervals", len(parquet("drill_assay_logs")), "intervals",
                  f"{generated}/drill_assay_logs.parquet"),
            entry("Metallurgical recovery records", len(parquet("metallurgical_recovery")),
                  "records", f"{generated}/metallurgical_recovery.parquet"),
        ],
        "window": {
            "from": str(telemetry["timestamp"].min()),
            "to": str(telemetry["timestamp"].max()),
            "source": f"{generated}/telemetry_stream.parquet",
        },
        "not_locally_derivable": [
            {
                "figure": "Fleet vehicle count",
                "why": (
                    "data/profile/stats.json keeps a three-row sample of "
                    "fleet_vehicles, not the table. Only the 5 vehicles carrying "
                    "an operator assignment are known locally. BigQuery settles it."
                ),
            },
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    catalog = build_catalog()
    personas = build_personas(catalog)
    graph = build_graph_from_local()
    facts = build_facts()

    workspace = build_workspace()
    workspace["generated_at"] = _now()

    payloads = {"catalog": catalog, "personas": personas,
                "graph": graph, "facts": facts,
                "value_tree": build_value_tree(catalog),
                "workspace": workspace}
    for name, payload in payloads.items():
        path = args.out / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")
        print(f"wrote {path.relative_to(REPO)} ({path.stat().st_size:,} bytes)")

    # The same payloads as one script tag. fetch() is blocked under file://, and
    # someone will open these screens by double-clicking them; a demo that shows
    # an empty page because of an origin rule is a demo that fails in the room.
    bundle = args.out / "bundle.js"
    bundle.write_text(
        "/* Generated by scripts/build_app_data.py. Do not edit. */\n"
        "window.MINING_DATA = " + json.dumps(payloads, sort_keys=False) + ";\n"
    )
    print(f"wrote {bundle.relative_to(REPO)} ({bundle.stat().st_size:,} bytes)")

    # tokens.css has one home, docs/ux/. Copying rather than importing keeps a
    # forked apps/ tree self-contained without giving the design system a
    # second editable copy.
    tokens_src = REPO / "docs" / "ux" / "tokens.css"
    tokens_dst = args.out.parent / "tokens.css"
    tokens_dst.write_text(
        "/* Copied from docs/ux/tokens.css by scripts/build_app_data.py.\n"
        "   Edit the source, not this file. */\n" + tokens_src.read_text()
    )
    print(f"wrote {tokens_dst.relative_to(REPO)} "
          f"({tokens_dst.stat().st_size:,} bytes)")

    print(f"\nagent nodes {catalog['counts']['agent_nodes']}, "
          f"entrypoints {catalog['counts']['entrypoints']}, "
          f"swarms {catalog['counts']['swarms']}, "
          f"HITL {catalog['counts']['hitl_entrypoints']}")
    print(f"personas {len(personas['personas'])}")
    print(f"formulas {len(workspace['formulas']['registry'])}, "
          f"traversals {len(workspace['traversals'])}, "
          f"models {len(workspace['models'])}, "
          f"approval columns {len(workspace['approval']['fields'])}")
    for name, info in graph["graphs"].items():
        print(f"graph {name:<14} {info['nodes']:>4} nodes {info['edges']:>4} edges  "
              f"{info['node_types']}")


if __name__ == "__main__":
    main()
