"""Parameterised BigQuery reads. String-interpolated SQL never executes."""
from __future__ import annotations

import re

from google.cloud import bigquery

from agents.config import settings
from agents.tools.base import ToolFailure, tool

# A quoted literal or a bare number appearing on the right of a comparison or
# inside an IN list. Table names in backticks and @parameters are unaffected.
_LITERAL_PREDICATE = re.compile(
    r"""(?ix)
    (?: =\s*|<\s*|>\s*|<=\s*|>=\s*|!=\s*|<>\s*|\bLIKE\s+|\bIN\s*\(\s* )
    (?: '[^']*' | "[^"]*" | \d+(?:\.\d+)? )
    """
)

_client: bigquery.Client | None = None


class SqlInterpolationError(ToolFailure):
    def __init__(self, message: str, **details):
        super().__init__("SQL_INTERPOLATION", message, **details)


def assert_no_interpolation(sql: str) -> None:
    """Reject SQL that compares against a literal instead of an @parameter."""
    match = _LITERAL_PREDICATE.search(sql)
    if match:
        raise SqlInterpolationError(
            "literal value in a predicate; use an @parameter instead",
            fragment=match.group(0).strip(),
        )


def _bq_client() -> bigquery.Client:
    global _client
    if _client is None:
        s = settings()
        _client = bigquery.Client(project=s.project_id, location=s.location)
    return _client


def _to_param(name: str, value):
    if isinstance(value, (list, tuple)):
        element = value[0] if value else ""
        return bigquery.ArrayQueryParameter(name, _bq_type(element), list(value))
    return bigquery.ScalarQueryParameter(name, _bq_type(value), value)


def _bq_type(value) -> str:
    if isinstance(value, bool):
        return "BOOL"
    if isinstance(value, int):
        return "INT64"
    if isinstance(value, float):
        return "FLOAT64"
    return "STRING"


def run_query(sql: str, params: dict, tables_read: list[str]) -> tuple[list[dict], int]:
    """Execute parameterised SQL. Returns (rows, row_count). No envelope."""
    assert_no_interpolation(sql)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[_to_param(k, v) for k, v in params.items()],
        use_query_cache=False,
    )
    try:
        rows = [dict(r) for r in _bq_client().query(sql, job_config=job_config).result()]
    except Exception as exc:  # noqa: BLE001 - boundary with BigQuery
        raise ToolFailure(
            "QUERY_FAILED", str(exc), tables_read=list(tables_read)
        ) from exc
    return rows, len(rows)


def make_bq_query(tables_read: list[str]):
    """Build an enveloped bq_query tool bound to the tables an agent may read."""

    @tool(tables_read)
    def bq_query(sql: str, params: dict | None = None):
        """Run a parameterised read against mining_data. Use @parameters only."""
        rows, scanned = run_query(sql, params or {}, tables_read)
        return {"rows": rows}, scanned

    return bq_query
