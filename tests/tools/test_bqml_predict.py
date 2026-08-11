"""Tests for bqml_predict — ML.PREDICT over the allowlisted BQML models.

The telemetry_alarm_risk_model was trained on six derived z-score features
(z_now, z_mean_24h, z_mean_72h, z_trend_48h, z_vol_72h, peer_z_24h) that are
not present verbatim in mining_data.telemetry_stream.  The input_sql in each
live test therefore computes those columns via CAST and literal constants so
that the subquery satisfies the model's expected schema.  The test does NOT
switch to a different model; it adjusts the input shape.
"""
import pytest
from agents.envelope import Envelope
from agents.tools.bqml_predict import list_models, make_bqml_predict

# The six feature columns required by telemetry_alarm_risk_model, projected
# from telemetry_stream via CAST/constant expressions.
_ALARM_RISK_SQL = """
SELECT
    CAST(metric_value AS FLOAT64) AS z_now,
    CAST(metric_value AS FLOAT64) AS z_mean_24h,
    CAST(metric_value AS FLOAT64) AS z_mean_72h,
    0.0                           AS z_trend_48h,
    0.0                           AS z_vol_72h,
    CAST(metric_value AS FLOAT64) AS peer_z_24h
FROM `mining_data.telemetry_stream`
LIMIT @n
"""


def test_the_dataset_exposes_eight_models():
    models = list_models()
    assert len(models) == 8, f"expected 8 BQML models, found {len(models)}: {models}"


def test_telemetry_alarm_risk_model_is_present():
    """Added in Phase 4; the design doc's list of 7 predates it."""
    assert "telemetry_alarm_risk_model" in list_models()


def test_allowlist_contains_all_eight_known_models():
    """Pin the exact allowlist so a missing or renamed model is caught immediately."""
    models = sorted(list_models())
    assert models == sorted([
        "asset_clustering_model",
        "downtime_regression_model",
        "inventory_impact_model",
        "inventory_impact_model_crusher",
        "inventory_impact_model_mill",
        "inventory_impact_model_pump",
        "safety_model",
        "telemetry_alarm_risk_model",
    ]), f"allowlist mismatch: {models}"


def test_predict_returns_rows_inside_the_envelope():
    model = "telemetry_alarm_risk_model"
    predict = make_bqml_predict([model])
    env = predict(model, _ALARM_RISK_SQL, {"n": 10})
    Envelope.model_validate(env)
    assert env["success"] is True
    assert len(env["data"]["rows"]) == 10
    assert any("predicted" in key for key in env["data"]["rows"][0])


def test_meta_names_both_the_model_and_the_input_tables():
    model = "telemetry_alarm_risk_model"
    predict = make_bqml_predict([model])
    env = predict(model, _ALARM_RISK_SQL, {"n": 5})
    assert f"mining_data.{model}" in env["meta"]["tables_read"]
    assert "mining_data.telemetry_stream" in env["meta"]["tables_read"]


def test_a_model_outside_the_allowlist_is_refused():
    predict = make_bqml_predict(["telemetry_alarm_risk_model"])
    env = predict("some_other_model", "SELECT 1", {})
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "MODEL_NOT_PERMITTED"
    assert env["meta"]["tables_read"]


def test_hostile_model_name_is_refused():
    """A model name with a backtick or SQL fragment must be rejected before SQL building."""
    predict = make_bqml_predict(["telemetry_alarm_risk_model"])
    hostile = "telemetry_alarm_risk_model`; DROP TABLE assets; --"
    env = predict(hostile, "SELECT 1", {})
    Envelope.model_validate(env)
    assert env["success"] is False
    assert env["error"]["code"] == "MODEL_NOT_PERMITTED"
    assert env["meta"]["tables_read"]


def test_interpolated_input_sql_is_refused():
    predict = make_bqml_predict(["telemetry_alarm_risk_model"])
    asset = "PUMP-104A"
    env = predict(
        "telemetry_alarm_risk_model",
        f"SELECT * FROM `mining_data.telemetry_stream` WHERE asset_id = '{asset}'",
        {},
    )
    assert env["success"] is False
    assert env["error"]["code"] == "SQL_INTERPOLATION"
