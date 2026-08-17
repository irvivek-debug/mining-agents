"""The three declared packs: AGT-13, AGT-14, AGT-19.

Every driver in all three packs is `not_instrumented` — the data these agents
need (a contracts table, a warranty table, a price deck / capital pipeline)
does not exist in this build yet. That is the point, not a gap in this test
file: an uninstrumented driver is declared, never dropped, and a pack that
quietly omitted its own gaps would be a report with a chat interface in front
of it. These tests hold the packs to the same honesty rules as the shipped
ones (see test_p3_pack.py, test_p6_pack.py) plus the extra rule specific to a
fully-declared pack: every question must name the table it needs, because
that is what turns the pack into the data generator's specification.
"""
import re
from pathlib import Path

import pytest

from mining_agents.method.pack import load_pack

ROOT = Path(__file__).resolve().parents[2]

PACKS = {
    "agt13": ROOT / "method" / "agt13-warranty.yaml",
    "agt14": ROOT / "method" / "agt14-contract-integrity.yaml",
    "agt19": ROOT / "method" / "agt19-strategic-planning.yaml",
}

# Tables each pack's questions must name, spelled out here so the test is
# checking against a known-good answer rather than "did the author write
# something in backticks" — a table name pulled from the wrong pack, or a
# typo'd one, fails this just as surely as a missing one.
EXPECTED_TABLES = {
    "agt13": {"warranty_entitlements", "warranty_claims", "maintenance_logs"},
    "agt14": {
        "contracts",
        "contract_transactions",
        "procurement_bids",
        "rebate_claims",
        "invoices",
    },
    "agt19": {
        "plan_assumptions",
        "plan_versions",
        "plan_scenarios",
        "site_plans",
        "group_plan",
        "capital_options",
        "option_outcomes",
        "plan_output_checklist",
    },
}

TABLE_TOKEN = re.compile(r"`([a-z][a-z0-9_]*)`")

VERDICT_WORDS = ("too few", "too many", "unevidenced", "no signal", "insufficient")


@pytest.mark.parametrize("name", PACKS)
def test_the_pack_loads_with_at_least_four_drivers(name):
    # A pack with fewer drivers than this could be an empty stub that still
    # satisfies every other assertion in this file; the floor makes that
    # impossible to ship silently.
    pack = load_pack(PACKS[name])
    assert len(pack.drivers) >= 4, (
        f"{name}: only {len(pack.drivers)} drivers; an empty or near-empty "
        "pack must not pass"
    )
    ids = [d.id for d in pack.drivers]
    assert len(set(ids)) == len(ids), f"{name}: duplicate driver ids {ids}"


@pytest.mark.parametrize("name", PACKS)
def test_every_driver_is_not_instrumented(name):
    # These agents' data does not exist yet. A driver that claimed
    # `instrumented` here would be lying about a diagnostic that isn't there.
    pack = load_pack(PACKS[name])
    statuses = {d.id: d.status for d in pack.drivers}
    assert statuses, f"{name}: no drivers found"
    for driver_id, status in statuses.items():
        assert status == "not_instrumented", (
            f"{name}/{driver_id}: status is {status!r}, expected "
            "not_instrumented — none of these agents' source tables exist yet"
        )


@pytest.mark.parametrize("name", PACKS)
def test_no_driver_carries_sql_or_compare(name):
    # load_pack already refuses sql/compare on a not_instrumented driver at
    # load time, so this is a second, independent check directly on the
    # parsed Driver objects — the property the honesty rule actually depends
    # on, not just the loader's internal enforcement of it.
    pack = load_pack(PACKS[name])
    for driver in pack.drivers:
        assert driver.sql is None, f"{name}/{driver.id}: carries sql {driver.sql!r}"
        assert driver.compare is None, (
            f"{name}/{driver.id}: carries compare {driver.compare!r}"
        )


@pytest.mark.parametrize("name", PACKS)
def test_no_guard_holds_a_verdict_word(name):
    """A guard is the method's caveat, true before any row is read.

    None of these drivers carry a guard at all (there is no diagnostic to
    guard), so this test is really asserting the field stays empty — but it
    is written against the same verdict list as the shipped packs so that if
    a future author adds guard text to one of these drivers, it is held to
    the same rule immediately rather than silently exempted because this
    pack started with no guards.
    """
    pack = load_pack(PACKS[name])
    for driver in pack.drivers:
        said = (driver.guard or "").lower()
        for verdict in VERDICT_WORDS:
            assert verdict not in said, (
                f"{name}/{driver.id}: guard says {verdict!r}, which decides "
                "a diagnostic's result before it runs"
            )


@pytest.mark.parametrize("name", PACKS)
def test_no_guard_describes_the_data(name):
    """'in this dataset' is the marker of a guard describing data, not a
    measurement. See test_p3_pack.py::test_no_guard_describes_the_data for
    the full rationale; this pins the same rule on the three new packs.
    """
    pack = load_pack(PACKS[name])
    for driver in pack.drivers:
        said = (driver.guard or "").lower()
        assert "in this dataset" not in said, (
            f"{name}/{driver.id}: guard contains 'in this dataset', which "
            "describes the data rather than the measurement"
        )


@pytest.mark.parametrize("name", PACKS)
def test_every_question_names_a_table(name):
    """Each not_instrumented driver's question doubles as the generator's
    spec. A question with no table named in it is a wish, not a spec — this
    asserts the table name is actually there, not just that the sentence
    sounds concrete.
    """
    pack = load_pack(PACKS[name])
    seen_tables = set()
    for driver in pack.drivers:
        tables = set(TABLE_TOKEN.findall(driver.question))
        assert tables, (
            f"{name}/{driver.id}: question names no table (no `backtick`-quoted "
            f"identifier found): {driver.question!r}"
        )
        seen_tables |= tables
    # Every table this pack is supposed to specify actually appears somewhere
    # in its questions — not just that some backticked word appears once.
    missing = EXPECTED_TABLES[name] - seen_tables
    assert not missing, f"{name}: expected tables never named: {missing}"


def test_agt19_states_the_permanent_l1_ceiling():
    """PRD §8.1: AGT-19 is the one agent whose authority can never be
    promoted — the product declines to build an agent that can move capital.
    The Pack schema has no authority field, so this is stated in the file's
    own prose rather than structured data; the test reads the raw text
    because load_pack() strips comments along with everything else YAML
    doesn't parse into the schema.
    """
    text = PACKS["agt19"].read_text().lower()
    assert "permanently l1" in text or "permanent l1" in text, (
        "agt19-strategic-planning.yaml never states the permanent L1 ceiling"
    )
    assert "no promotion path" in text, (
        "agt19-strategic-planning.yaml never states that AGT-19 has no "
        "promotion path"
    )


@pytest.mark.parametrize("name", PACKS)
def test_no_pack_names_a_metal_or_a_dollar_amount(name):
    """Commodity-neutral and money-as-ranges are constraints inherited from
    the design doc. A named metal or a bare currency figure would break a
    fork that mines something else, or assert a precision this build cannot
    back.
    """
    text = PACKS[name].read_text().lower()
    for metal in ("copper", "gold", "iron ore", "nickel", "zinc", "lithium"):
        assert metal not in text, f"{name}: names a specific commodity {metal!r}"
    assert "$" not in text, f"{name}: contains a currency symbol"


@pytest.mark.parametrize("name", PACKS)
def test_no_pack_references_the_data_generator(name):
    """A customer forks this repo and inherits every word in it. A pack that
    told the reader 'this is synthetic/demo data' would be lying to every
    fork that has replaced that data with its own.
    """
    text = PACKS[name].read_text().lower()
    for phrase in ("synthetic data", "data generator", "demo dataset", "demo data"):
        assert phrase not in text, f"{name}: references {phrase!r}"
