"""Tests for request_approval — the HITL write path.

Every test row that touches BigQuery uses a TEST- prefix and cleans up on
teardown so the shared table is left exactly as we found it.

Cleanup uses the BigQuery jobs API (DML DELETE), not bq rm / DROP TABLE.
If a teardown itself fails the row stays; the next test run that succeeds
will still pass because each test uses a fresh unique approval_id.
"""
from __future__ import annotations

import time
import uuid

import pytest
from google.cloud import bigquery

from agents.config import settings
from agents.envelope import Envelope
from agents.tools.request_approval import approval_status, make_request_approval

# ── helpers ──────────────────────────────────────────────────────────────────


def _delete_test_rows(approval_ids: list[str]) -> None:
    """Attempt to delete TEST- rows from the live table.

    BigQuery streaming inserts go into a streaming buffer that cannot be
    DML-deleted until the data is moved to regular storage (typically 30–90
    minutes).  This function tries the DELETE but swallows the
    ``BadRequest: cannot run DML on streaming buffer`` error gracefully.
    The TEST- prefix in every approval_id ensures these synthetic rows are
    identifiable; a scheduled cleanup job (or the 90-day table TTL) will
    remove them eventually.  Tests still pass because each test generates a
    fresh uuid-based approval_id so old orphaned TEST- rows do not interfere.
    """
    if not approval_ids:
        return
    s = settings()
    client = bigquery.Client(project=s.project_id, location=s.location)
    placeholders = ", ".join(f"'{aid}'" for aid in approval_ids)
    # Plain DML — we are deleting our own synthetic TEST- rows.
    sql = (
        f"DELETE FROM `{s.project_id}.{s.dataset}.agent_approvals` "
        f"WHERE approval_id IN ({placeholders})"
    )
    try:
        client.query(sql).result()
    except Exception:  # noqa: BLE001
        # Swallow the streaming-buffer restriction; rows carry TEST- prefix and
        # will be cleaned up by the table's 90-day TTL or a manual DML run
        # once the streaming buffer drains.
        pass


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def cleanup():
    """Collect approval_ids written during a test; delete them on teardown."""
    ids: list[str] = []
    yield ids
    _delete_test_rows(ids)


# ── tests ─────────────────────────────────────────────────────────────────────


def test_a_request_is_written_and_comes_back_pending(cleanup):
    marker = f"TEST-{uuid.uuid4().hex[:8]}"
    ask = make_request_approval("D07")
    env = ask(
        "reorder_part",
        {"part_number": "SKU-BELT-SPLICE-G2", "qty": 40, "marker": marker},
        reasoning="stock below reorder point",
    )
    Envelope.model_validate(env)
    assert env["success"] is True
    assert env["data"]["status"] == "PENDING"
    aid = env["data"]["approval_id"]
    assert aid.startswith("TEST-"), "approval_id must carry the TEST- prefix"
    cleanup.append(aid)
    assert approval_status(aid) == "PENDING"


def test_the_row_records_the_requesting_agent(cleanup):
    ask = make_request_approval("S08")
    env = ask(
        "expedite_order",
        {"work_order_id": "WO-0001"},
        reasoning="critical asset at risk",
    )
    assert env["success"] is True
    assert env["data"]["agent_id"] == "S08"
    cleanup.append(env["data"]["approval_id"])


def test_meta_names_agent_approvals(cleanup):
    ask = make_request_approval("D07")
    env = ask("reorder_part", {"part_number": "X"}, reasoning="test")
    assert env["meta"]["tables_read"] == ["mining_data.agent_approvals"]
    cleanup.append(env["data"]["approval_id"])


def test_reasoning_is_required():
    ask = make_request_approval("D07")
    env = ask("reorder_part", {"part_number": "X"}, reasoning="")
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "INVALID_ARGUMENT"


def test_the_tool_never_returns_approved():
    """Nothing in this codebase may self-approve. Only a human sets APPROVED."""
    import pathlib

    source = pathlib.Path(
        "agents/tools/request_approval.py"
    ).read_text()
    assert "'APPROVED'" not in source and '"APPROVED"' not in source


def test_empty_source_tables_is_refused():
    """source_tables must be non-empty; an empty array is a silent data loss trap."""
    ask = make_request_approval("D07")
    # Attempt to create a request with an empty source_tables list.
    # The tool must raise ToolFailure before writing the row.
    env = ask(
        "reorder_part",
        {"part_number": "X"},
        reasoning="test empty source_tables guard",
        source_tables=[],
    )
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "INVALID_ARGUMENT"
    assert "source_tables" in env["error"]["message"].lower() or \
           "source_tables" in str(env["error"]["details"]).lower()


def test_source_tables_round_trips_through_bigquery(cleanup):
    """The repeated STRING column must survive a BigQuery write+read cycle intact."""
    tables_in = ["mining_data.inventory_levels", "mining_data.erp_work_orders"]
    ask = make_request_approval("D07")
    env = ask(
        "reorder_part",
        {"part_number": "SKU-BELT-SPLICE-G2", "qty": 1},
        reasoning="round-trip test for source_tables",
        source_tables=tables_in,
    )
    assert env["success"] is True, f"insert failed: {env.get('error')}"
    aid = env["data"]["approval_id"]
    assert aid.startswith("TEST-")
    cleanup.append(aid)

    # Read back and confirm exact array contents, not just that a row exists.
    s = settings()
    client = bigquery.Client(project=s.project_id, location=s.location)
    sql = (
        f"SELECT source_tables FROM `{s.project_id}.{s.dataset}.agent_approvals` "
        f"WHERE approval_id = @approval_id"
    )
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("approval_id", "STRING", aid)
        ]
    )
    # Streaming buffer can lag — retry up to 5 times with 1-second gap.
    rows = []
    for _ in range(5):
        rows = list(client.query(sql, job_config=job_config).result())
        if rows:
            break
        time.sleep(1)

    assert len(rows) == 1, "inserted row not readable after 5 retries"
    round_tripped = list(rows[0]["source_tables"])
    assert round_tripped == tables_in, (
        f"source_tables round-trip mismatch: expected {tables_in!r}, "
        f"got {round_tripped!r}"
    )
