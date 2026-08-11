"""The four canonical property-graph traversals, parameter-bound.

Edge LABELS, never table names. A graph over unmatched tables returns zero
rows with no error, so the tests pin real row counts on known-good keys.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from agents.tools.base import ToolFailure, tool
from agents.tools.bq_query import run_query


@dataclass(frozen=True)
class Traversal:
    graph: str
    sql: str
    params: tuple[str, ...]
    tables_read: list[str] = field(default_factory=list)


_BLAST_RADIUS = """
SELECT * FROM GRAPH_TABLE(
  mining_data.MiningAssetGraph
  MATCH (origin:assets WHERE origin.asset_id = @asset_id)
        -[:DEPENDS_ON]->{1,3} (impacted:assets)
  COLUMNS (origin.asset_id AS fail_origin,
           impacted.asset_id AS impacted_asset,
           impacted.criticality_rating AS impacted_criticality)
)
"""

_STOCKOUT_EXPOSURE = """
SELECT * FROM GRAPH_TABLE(
  mining_data.MiningSupplyChainGraph
  MATCH (p:SparePart WHERE p.part_number IN UNNEST(@below_rop_parts))
        <-[:REPLACED_PART]- (wo:WorkOrder) <-[:HAS_WORK_ORDER]- (a:Asset)
  COLUMNS (p.part_number AS part_number, wo.work_order_id AS work_order_id,
           wo.priority AS priority, wo.repair_cost AS repair_cost,
           a.asset_id AS asset_id, a.criticality_rating AS criticality_rating)
)
WHERE @asset_id IS NULL OR asset_id = @asset_id
ORDER BY part_number, work_order_id
"""

_FATIGUE_TO_INCIDENT = """
SELECT * FROM GRAPH_TABLE(
  mining_data.MiningOperationsSafetyGraph
  MATCH (f:FatigueLog) -[:LOGGED_FOR]->
        (o:Operator WHERE o.operator_id = @operator_id)
        -[:OPERATES]-> (v:Vehicle) -[:INVOLVED_IN]-> (i:Incident)
  COLUMNS (f.log_id AS log_id, o.operator_id AS operator_id,
           v.vehicle_id AS vehicle_id, i.incident_id AS incident_id,
           i.severity_level AS severity_level)
)
"""

_ONTOLOGY_RELATED = """
SELECT * FROM GRAPH_TABLE(
  mining_data.MiningOntologyGraph
  MATCH (s:ontology_concepts WHERE s.concept_name = @concept)
        -[r:RELATED_TO]-> (o:ontology_concepts)
  COLUMNS (s.concept_name AS subject, r.predicate AS predicate,
           o.concept_name AS object)
)
"""

TRAVERSALS: dict[str, Traversal] = {
    "blast_radius": Traversal(
        graph="MiningAssetGraph", sql=_BLAST_RADIUS, params=("asset_id",),
        tables_read=["mining_data.assets", "mining_data.asset_dependencies"],
    ),
    "stockout_exposure": Traversal(
        graph="MiningSupplyChainGraph", sql=_STOCKOUT_EXPOSURE,
        params=("below_rop_parts", "asset_id"),
        tables_read=["mining_data.inventory_levels", "mining_data.erp_work_orders",
                     "mining_data.work_order_parts_edge", "mining_data.assets"],
    ),
    "fatigue_to_incident": Traversal(
        graph="MiningOperationsSafetyGraph", sql=_FATIGUE_TO_INCIDENT,
        params=("operator_id",),
        tables_read=["mining_data.biometric_fatigue_logs", "mining_data.operators_node",
                     "mining_data.operator_vehicle_assignments",
                     "mining_data.incident_involvements",
                     "mining_data.safety_incidents"],
    ),
    "ontology_related": Traversal(
        graph="MiningOntologyGraph", sql=_ONTOLOGY_RELATED, params=("concept",),
        tables_read=["mining_data.ontology_concepts"],
    ),
}

_ALL_TABLES = sorted({t for trav in TRAVERSALS.values() for t in trav.tables_read})


def make_graph_traverse(allowed: list[str]):
    """Build an enveloped graph_traverse bound to the traversals an agent owns."""
    unknown = [name for name in allowed if name not in TRAVERSALS]
    if unknown:
        raise ValueError(f"unknown traversal(s): {unknown}")
    tables = sorted({t for name in allowed for t in TRAVERSALS[name].tables_read})

    @tool(tables or _ALL_TABLES)
    def graph_traverse(traversal: str, params: dict):
        """Run one of the canonical property-graph traversals."""
        if traversal not in allowed:
            raise ToolFailure(
                "TRAVERSAL_NOT_PERMITTED",
                f"this agent may run {sorted(allowed)}, not {traversal!r}",
                requested=traversal,
            )
        spec = TRAVERSALS[traversal]
        missing = [p for p in spec.params if p not in params]
        if missing:
            raise ToolFailure(
                "INVALID_ARGUMENT",
                f"traversal {traversal!r} requires {list(spec.params)}",
                missing=missing,
            )
        bound = {p: params[p] for p in spec.params}
        rows, scanned = run_query(spec.sql, bound, spec.tables_read)
        return {"graph": spec.graph, "rows": rows}, scanned

    return graph_traverse
