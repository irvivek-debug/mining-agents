import pytest
from agents.envelope import Envelope, ok, fail
from agents.tools.base import tool, ToolFailure


def test_ok_produces_a_valid_envelope():
    env = ok({"n": 1}, tables_read=["mining_data.assets_node"], rows_scanned=5)
    Envelope.model_validate(env)
    assert env["success"] is True
    assert env["error"] is None
    assert env["meta"]["tables_read"] == ["mining_data.assets_node"]
    assert env["meta"]["rows_scanned"] == 5
    assert env["meta"]["timestamp"].endswith("Z")


def test_fail_uses_rfc7807_shape():
    env = fail("INVALID_ARGUMENT", "bad input", {"field": "asset_id"},
               tables_read=["mining_data.assets_node"])
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["data"] == {}
    assert set(env["error"]) == {"code", "message", "details"}
    assert env["error"]["code"] == "INVALID_ARGUMENT"
    assert env["error"]["details"]["field"] == "asset_id"


def test_decorator_wraps_a_successful_call():
    @tool(["mining_data.telemetry_stream"])
    def probe(x: int):
        return {"doubled": x * 2}, 7

    env = probe(3)
    Envelope.model_validate(env)
    assert env["data"] == {"doubled": 6}
    assert env["meta"]["rows_scanned"] == 7
    assert env["meta"]["tables_read"] == ["mining_data.telemetry_stream"]


def test_decorator_converts_toolfailure_to_rfc7807():
    @tool(["mining_data.telemetry_stream"])
    def probe():
        raise ToolFailure("NOT_FOUND", "no such asset", asset_id="PUMP-999")

    env = probe()
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "NOT_FOUND"
    assert env["error"]["details"] == {"asset_id": "PUMP-999"}


def test_failure_envelope_still_carries_tables_read():
    """meta.tables_read is mandatory on EVERY tool result, including failures."""
    @tool(["mining_data.erp_work_orders"])
    def explode():
        raise RuntimeError("boom")

    env = explode()
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "INTERNAL"
    assert env["meta"]["tables_read"] == ["mining_data.erp_work_orders"]


def test_tool_requires_a_nonempty_tables_read_declaration():
    with pytest.raises(ValueError):
        @tool([])
        def nothing():
            return {}, 0
