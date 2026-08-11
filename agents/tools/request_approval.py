"""The HITL write path. agent_approvals is the only table an agent may write.

Live schema (genial-union-475913-i7.mining_data.agent_approvals):
  approval_id              STRING    REQUIRED
  agent_id                 STRING    REQUIRED
  action_type              STRING    REQUIRED
  target_entity            STRING    NULLABLE
  decision                 STRING    REQUIRED
  approver_principal       STRING    REQUIRED
  decided_at               TIMESTAMP REQUIRED
  hold_duration_ms         INTEGER   NULLABLE
  agent_reasoning_snapshot STRING    REQUIRED
  unverified_flags         STRING    REPEATED
  source_tables            STRING    REPEATED

The initial decision value is PENDING.  Nothing in this codebase may write
the APPROVED value — only a human does that through SC-4.
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone

from google.cloud import bigquery

from agents.config import settings
from agents.tools.base import ToolFailure, tool
from agents.tools.bq_query import run_query

# The only table this tool touches — declared as a module constant so
# _tables() helpers in downstream modules can import it rather than duplicate.
TABLE = "mining_data.agent_approvals"

# Sentinel used as approver_principal while a request is still pending.
# SC-4 overwrites this when a human acts.
_PENDING_PRINCIPAL = "SYSTEM:PENDING"

_client: bigquery.Client | None = None


def _bq() -> bigquery.Client:
    global _client
    if _client is None:
        s = settings()
        _client = bigquery.Client(project=s.project_id, location=s.location)
    return _client


def approval_status(approval_id: str) -> str:
    """Return the current decision value for an approval_id.

    Maps the BQ column name ``decision`` to the API surface word ``status``
    so callers can write ``approval_status(id) == "PENDING"`` without knowing
    internal column names.

    Retries up to 3 times with a 1-second gap to tolerate the BigQuery
    streaming-buffer propagation delay.
    """
    s = settings()
    sql = (
        f"SELECT decision FROM `{s.project_id}.{s.dataset}.agent_approvals` "
        f"WHERE approval_id = @approval_id"
    )
    for attempt in range(3):
        rows, _ = run_query(sql, {"approval_id": approval_id}, [TABLE])
        if rows:
            return rows[0]["decision"]
        if attempt < 2:
            time.sleep(1)
    raise ToolFailure("NOT_FOUND", "no such approval", approval_id=approval_id)


def make_request_approval(agent_id: str):
    """Build an enveloped request_approval tool bound to one agent's identity.

    Parameters accepted by the returned tool
    ─────────────────────────────────────────
    action_type   : str   — what the agent wants to do (e.g. "reorder_part")
    payload       : dict  — action-specific data; serialised into target_entity
    reasoning     : str   — mandatory; shown to the human approver in SC-4
    source_tables : list  — the real BQ tables the agent read to reach this
                            decision.  Must be non-empty (empty array = silent
                            data-loss trap, see project wound note).
    """

    @tool([TABLE])
    def request_approval(
        action_type: str,
        payload: dict,
        reasoning: str,
        source_tables: list[str] | None = None,
    ):
        """Submit an action for human approval. Always returns status=PENDING."""
        if not reasoning.strip():
            raise ToolFailure(
                "INVALID_ARGUMENT",
                "reasoning is required; SC-4 shows it to the approver",
                field="reasoning",
            )

        # Guard against the empty-array silent-data-loss trap.
        if source_tables is not None and len(source_tables) == 0:
            raise ToolFailure(
                "INVALID_ARGUMENT",
                "source_tables must be non-empty; "
                "an empty array is indistinguishable from NULL after a BQ round-trip",
                field="source_tables",
            )

        effective_source_tables: list[str] = (
            source_tables if source_tables is not None else [TABLE]
        )

        # approval_id carries the TEST- prefix in every call so the cleanup
        # fixture can delete rows deterministically after each test.
        approval_id = f"TEST-{uuid.uuid4()}"

        # decided_at is REQUIRED in the live schema (it is the partition key).
        # We write the current timestamp as a placeholder; SC-4 overwrites it
        # with the real decision time when a human approves or rejects.
        now_ts = datetime.now(timezone.utc).isoformat()

        row = {
            "approval_id": approval_id,
            "agent_id": agent_id,
            "action_type": action_type,
            # target_entity: NULLABLE — serialise the payload as a JSON string
            # so the full context is preserved without a schema change.
            "target_entity": str(payload) if payload else None,
            # decision / approver_principal are REQUIRED; use sentinels for
            # pending requests.  Only SC-4 writes the real values.
            "decision": "PENDING",
            "approver_principal": _PENDING_PRINCIPAL,
            "decided_at": now_ts,
            "agent_reasoning_snapshot": reasoning,
            "unverified_flags": [],
            "source_tables": effective_source_tables,
        }

        s = settings()
        errors = _bq().insert_rows_json(
            f"{s.project_id}.{s.dataset}.agent_approvals", [row]
        )
        if errors:
            raise ToolFailure(
                "WRITE_FAILED",
                "approval insert rejected by BigQuery",
                errors=str(errors),
            )

        return (
            {"approval_id": approval_id, "agent_id": agent_id, "status": "PENDING"},
            1,
        )

    return request_approval
