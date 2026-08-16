"""The shipped P5 pack, checked for structure and against the live data."""
from pathlib import Path

import pytest

from mining_agents.method.pack import load_pack
from mining_agents.tools.bq_query import assert_no_interpolation, run_query

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "method" / "p5-geologist.yaml"
TABLES = [
    "mining_data.drill_assay_logs",
    "mining_data.geological_block_models",
    "mining_data.drill_holes",
    "mining_data.metallurgical_recovery",
]


def test_the_shipped_pack_loads():
    pack = load_pack(PACK)
    assert pack.metric == "contained-metal variance between the block model and realised grade"
    assert {d.id for d in pack.drivers} == {
        "model_bias", "bias_by_lithology", "bias_by_depth",
        "bias_by_elevation", "feed_grade_vs_model",
        "tonnage_reconciliation", "qaqc_bias",
    }


def test_every_named_sql_file_exists():
    for driver in load_pack(PACK).drivers:
        if driver.sql:
            assert (ROOT / "method" / driver.sql).is_file(), driver.sql


def test_every_diagnostic_uses_parameters_not_literals():
    for driver in load_pack(PACK).drivers:
        if driver.sql:
            assert_no_interpolation((ROOT / "method" / driver.sql).read_text())


def test_the_uninstrumented_drivers_are_declared_not_omitted():
    statuses = {d.id: d.status for d in load_pack(PACK).drivers}
    assert statuses["tonnage_reconciliation"] == "not_instrumented"
    assert statuses["qaqc_bias"] == "not_instrumented"


def test_no_driver_decides_in_advance_what_its_own_diagnostic_will_show():
    verdicts = ("too few", "too many", "unevidenced", "no signal", "insufficient")
    for driver in load_pack(PACK).drivers:
        assert driver.status in ("instrumented", "not_instrumented"), driver.id
        said = (driver.guard or "").lower()
        for verdict in verdicts:
            assert verdict not in said, (
                f"{driver.id}: the guard says {verdict!r}, which decides the "
                "diagnostic's result before it runs"
            )


def test_the_root_does_not_state_the_direction_of_the_variance():
    """The model under-calls in this data. The pack must not say so.

    Writing the direction into the root turns the pack into a precomputed
    report: the agent would carry the answer into the diagnostic instead of
    reading it out of the rows, and on a fork whose model over-calls the pack
    would ship a wrong answer in a YAML file.
    """
    root = load_pack(PACK).root.lower()
    for leak in ("under", "over", "optimistic", "pessimistic", "understate", "overstate"):
        assert leak not in root, root


@pytest.mark.integration
def test_the_model_bias_diagnostic_pairs_samples_to_blocks():
    driver = next(d for d in load_pack(PACK).drivers if d.id == "model_bias")
    rows, _ = run_query(
        (ROOT / "method" / driver.sql).read_text(), driver.params, TABLES
    )
    assert rows, "the desurvey join returned nothing"
    row = rows[0]
    # The pairing is the whole diagnostic: assert it found the pairs the design
    # was built on, not merely that a query ran.
    assert row["paired_samples"] >= 100, row
    assert row["modelled_grade"] > 0 and row["assayed_grade"] > 0
