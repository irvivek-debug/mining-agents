"""Ontology concept expansion plus unstructured-document metadata.

Pattern C capability enters this build here — as a tool, not as an agent.
"""
from __future__ import annotations

from agents.config import settings
from agents.tools.base import tool
from agents.tools.bq_query import run_query
from agents.tools.graph_traverse import TRAVERSALS

TABLES = ["mining_data.ontology_concepts", "mining_data.unstructured_docs_metadata"]


def _sql(template: str) -> str:
    """Substitute the configured dataset name into a SQL template."""
    ds = settings().dataset
    return template.replace("{ds}", ds)


# Column names confirmed against `bq show unstructured_docs_metadata`.
# The table has no explicit concept_name column, so we use a broad JSON match.
_DOCS_SQL = _sql("""
SELECT *
FROM `{ds}.unstructured_docs_metadata` AS t
WHERE CONTAINS_SUBSTR(TO_JSON_STRING(t), @concept)
LIMIT 25
""")


@tool(TABLES)
def ontology_lookup(concept: str, include_docs: bool = True):
    """Expand a concept via MiningOntologyGraph and find related documents."""
    spec = TRAVERSALS["ontology_related"]
    related, scanned = run_query(spec.sql, {"concept": concept}, list(spec.tables_read))

    documents: list[dict] = []
    if include_docs:
        docs, doc_scanned = run_query(
            _DOCS_SQL, {"concept": concept},
            ["mining_data.unstructured_docs_metadata"],
        )
        documents = docs
        scanned += doc_scanned

    return {"concept": concept, "related": related, "documents": documents}, scanned
