import pytest
from agents.envelope import Envelope
from agents.tools.bq_query import (
    assert_no_interpolation, make_bq_query, run_query, SqlInterpolationError,
)


@pytest.mark.parametrize("sql", [
    "SELECT * FROM t WHERE id = 'PUMP-104A'",
    'SELECT * FROM t WHERE id = "PUMP-104A"',
    "SELECT * FROM t WHERE n = 5",
])
def test_literal_values_in_predicates_are_rejected(sql):
    with pytest.raises(SqlInterpolationError):
        assert_no_interpolation(sql)


def test_parameterised_sql_is_accepted():
    assert_no_interpolation("SELECT * FROM t WHERE id = @asset_id LIMIT @n")


def test_run_query_returns_rows_and_a_count():
    rows, scanned = run_query(
        "SELECT asset_id FROM `mining_data.assets` "
        "WHERE asset_id = @asset_id",
        {"asset_id": "PUMP-104A"},
        ["mining_data.assets"],
    )
    assert len(rows) == 1
    assert rows[0]["asset_id"] == "PUMP-104A"
    assert scanned == 1


def test_enveloped_tool_reports_the_declared_tables():
    q = make_bq_query(["mining_data.assets"])
    env = q("SELECT COUNT(*) AS n_assets FROM `mining_data.assets`", {})
    Envelope.model_validate(env)
    assert env["success"] is True
    assert env["meta"]["tables_read"] == ["mining_data.assets"]
    assert env["data"]["rows"][0]["n_assets"] > 0


def test_interpolated_sql_fails_inside_the_envelope_not_as_a_crash():
    q = make_bq_query(["mining_data.assets"])
    asset = "PUMP-104A"
    env = q(f"SELECT * FROM `mining_data.assets` WHERE asset_id = '{asset}'", {})
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "SQL_INTERPOLATION"
    assert env["meta"]["tables_read"] == ["mining_data.assets"]
