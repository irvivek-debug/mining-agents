"""The shipped P6 pack, checked for structure and against the live data."""
from pathlib import Path

import pytest

from mining_agents.method.pack import load_pack
from mining_agents.tools.bq_query import assert_no_interpolation, run_query

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "method" / "p6-metallurgist.yaml"
BOTH = ["mining_data.metallurgical_recovery", "mining_data.crusher_states"]


def test_the_shipped_pack_loads():
    pack = load_pack(PACK)
    assert pack.metric == "unit cost per tonne of contained metal"
    assert {d.id for d in pack.drivers} == {
        "liberation", "feed_variability", "bypass",
        "reagent_regime", "grind_size_p80",
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
    # Dropping them would let the answer imply the tree was fully explored.
    statuses = {d.id: d.status for d in load_pack(PACK).drivers}
    assert statuses["reagent_regime"] == "not_instrumented"
    assert statuses["grind_size_p80"] == "not_instrumented"
    assert statuses["bypass"] == "unevidenced"


@pytest.mark.integration
def test_the_liberation_diagnostic_reproduces_the_design_finding():
    driver = next(d for d in load_pack(PACK).drivers if d.id == "liberation")
    rows, _ = run_query(
        (ROOT / "method" / driver.sql).read_text(), driver.params, BOTH
    )
    bands = {r["band"]: r for r in rows}
    assert set(bands) == {"tight", "mid", "wide"}
    # Recovery falls monotonically as the gap opens.
    assert bands["tight"]["recovery_pct"] > bands["mid"]["recovery_pct"]
    assert bands["mid"]["recovery_pct"] > bands["wide"]["recovery_pct"]
    # Throughput does not improve when the gap opens — this is what kills the
    # "but you will lose tonnes" objection, so it is a gate.
    assert bands["wide"]["throughput_tph"] <= bands["tight"]["throughput_tph"]
    # Torque stays under the documented 4500 Nm critical alarm in every band.
    assert max(b["torque_max_nm"] for b in bands.values()) < 4500


@pytest.mark.integration
def test_the_setting_effect_survives_the_feed_grade_control():
    driver = next(d for d in load_pack(PACK).drivers if d.id == "feed_variability")
    rows, _ = run_query(
        (ROOT / "method" / driver.sql).read_text(), driver.params, BOTH
    )
    assert len(rows) == 3
    for row in rows:
        assert row["recovery_tight"] > row["recovery_wide"], (
            f"tercile {row['feed_tercile']} does not hold; the finding would "
            "be a feed-grade artefact"
        )
