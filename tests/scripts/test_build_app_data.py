"""Tests that build_app_data correctly carries method pack metrics to the screens.

These tests read personas.json from the export, so they verify the full
pipeline: pack loaded, metric extracted, written into the export. They are
intentionally not re-testing the pack loader itself (test_persona_method.py
covers that). They test what screens see.

Note: build_app_data reads BigQuery for the graph export. These tests do not
invoke the build — they read the file it produced and check its content. If the
file is stale (BigQuery credentials have expired and the build cannot re-run),
re-run:

    PYTHONPATH=. python -m scripts.build_app_data

after restoring credentials.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_every_persona_with_a_pack_carries_its_metric_to_the_screens():
    from mining_agents.tools.method_lookup import PACKS
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    for code in PACKS:
        assert personas[code].get("method", {}).get("metric"), code


def test_a_persona_without_a_pack_carries_no_method_block():
    # A method block on a persona with no tree would put a problem-solving
    # question on a page that cannot answer it.
    from mining_agents.tools.method_lookup import PACKS
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    for code, persona in personas.items():
        if code not in PACKS:
            assert not persona.get("method"), code


def test_five_packs_means_five_personas_carry_a_metric():
    # Guards against the count silently shrinking. Five packs were authored;
    # five method blocks must appear. A future pack added without re-running the
    # build would leave this test failing, which is the correct outcome.
    from mining_agents.tools.method_lookup import PACKS
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    personas_with_method = [
        code for code, p in personas.items() if p.get("method", {}).get("metric")
    ]
    assert len(personas_with_method) == len(PACKS), (
        f"Expected {len(PACKS)} personas with a metric (one per pack), "
        f"got {len(personas_with_method)}: {sorted(personas_with_method)}"
    )


def test_each_metric_is_a_non_empty_string():
    # A metric of "" or None would cause the governing starter to silently fall
    # back to table questions, which is the problem the method pack exists to fix.
    from mining_agents.tools.method_lookup import PACKS
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    for code in PACKS:
        metric = personas[code].get("method", {}).get("metric")
        assert isinstance(metric, str) and metric.strip(), (
            f"{code}: metric is {metric!r}, not a non-empty string"
        )


def test_metrics_match_what_the_packs_declare():
    # The metric on the screen must match what the pack actually says, not a
    # stale copy. This verifies the full pipeline: pack -> build -> export.
    from mining_agents.tools.method_lookup import PACK_DIR, PACKS
    from mining_agents.method.pack import load_pack
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    for code, pack_name in PACKS.items():
        pack = load_pack(PACK_DIR / pack_name)
        screen_metric = personas[code]["method"]["metric"]
        assert screen_metric == pack.metric, (
            f"{code}: screen shows {screen_metric!r} but pack declares {pack.metric!r}"
        )


# --------------------------------------------------------------------------
# Task 3: agent cards, and coverage computed from the pack, never authored.
#
# A parallel workstream is instrumenting agt13/agt14/agt19's packs while these
# tests run, so the exact numbers below are read out of the shipped export
# and cross-checked against an independent read of the pack file in the same
# test -- never pinned as a literal -- so these tests keep passing as that
# work lands and would fail the moment the export stopped tracking the pack.
# --------------------------------------------------------------------------

def _card(personas, code, agent_id):
    cards = personas[code].get("cards") or []
    found = [c for c in cards if c["agent_id"] == agent_id]
    assert found, f"{agent_id} carries no card under persona {code}"
    return found[0]


def test_every_card_field_reaches_the_export():
    # The card's authored fields (everything except coverage) must reach the
    # export unchanged from AgentDef.card -- read independently here, not
    # copied from build_app_data.py, so a field the export silently dropped
    # would be caught.
    from mining_agents.catalog.definitions import ALL_AGENTS
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    checked = 0
    for agent in ALL_AGENTS:
        if agent.card is None:
            continue
        checked += 1
        card = _card(personas, agent.persona, agent.agent_id)
        assert card["decision"] == agent.card.decision
        assert card["leaks"] == list(agent.card.leaks)
        assert card["archetype"] == agent.card.archetype
        assert card["authority"] == agent.card.authority
        assert card["honest_limit"] == agent.card.honest_limit
        assert card["financial_lines"] == [
            {"line": fl.line, "evidence_class": fl.evidence_class}
            for fl in agent.card.financial_lines
        ]
    assert checked == 7, (
        f"expected the seven documented cards (S01, S02, S03, S05, S06, S07, "
        f"S09), found {checked}"
    )


def test_agt11_coverage_matches_the_pack_read_independently():
    # Not a tautology: this re-derives the count from p1-reliability.yaml
    # itself, in this test, rather than re-reading what build_app_data.py
    # already computed. A build that stopped computing coverage and started
    # copying a stale number would still pass a test that only compared the
    # export to itself; this one would not.
    from mining_agents.method.pack import load_pack
    personas = json.loads((ROOT / "apps/shared/data/personas.json").read_text())["personas"]
    card = _card(personas, "P1", "S01")
    assert card["pack"] == "p1-reliability.yaml"

    pack = load_pack(ROOT / "method" / "p1-reliability.yaml")
    instrumented = sum(1 for d in pack.drivers if d.status == "instrumented")
    assert card["coverage"] == {"instrumented": instrumented, "total": len(pack.drivers)}

    # Guards against a coverage function that always reports "all" or
    # "none": the real pack has both statuses, so a broken computation that
    # returned total==instrumented or instrumented==0 would fail here.
    assert 0 < instrumented < len(pack.drivers), (
        "p1-reliability.yaml no longer mixes instrumented and not_instrumented "
        "drivers, so this test can no longer tell a real computation from a "
        "constant one -- re-derive the assertion against the pack's new shape"
    )


def test_a_fully_uninstrumented_pack_reports_zero_not_absent():
    """A pack with zero instrumented drivers must export instrumented: 0 with
    total > 0 -- not an absent or null coverage field, which would read on a
    card as full coverage.

    Proved against a synthetic pack, not against agt13/agt14/agt19 (design §3
    shipped these three at zero). Those three are a live workstream running in
    parallel with this one, so a real pack at zero coverage today may not be
    at zero by the time this test next runs -- see the coverage numbers this
    build actually measured for them: no single one of the three is a stable
    "always zero" fixture to pin a test against. The behaviour under test
    (zero is reported, not omitted) has to hold regardless of which pack it is
    asked about, so it is proved on a pack this test controls end to end.
    """
    import scripts.build_app_data as build
    from mining_agents.catalog.definitions import AgentCard, FinancialLine
    from types import SimpleNamespace

    fixture = ROOT / "tests" / "scripts" / "fixtures"
    fixture.mkdir(exist_ok=True)
    pack_path = fixture / "_tmp_zero_pack.yaml"
    try:
        pack_path.write_text(
            "metric: test metric\n"
            "root: test root\n"
            "drivers:\n"
            "  - id: d1\n"
            "    question: q1\n"
            "    controllable: false\n"
            "    status: not_instrumented\n"
            "  - id: d2\n"
            "    question: q2\n"
            "    controllable: false\n"
            "    status: not_instrumented\n"
        )

        coverage = build._coverage(pack_path)
        assert coverage == {"instrumented": 0, "total": 2}
        assert coverage["total"] > 0

        # And through the real card-record pipeline, not just the coverage
        # helper in isolation -- PACK_DIR is pointed at the fixtures
        # directory for the duration of the call, so _card_record resolves
        # card.pack exactly the way it resolves a real pack, without writing
        # anything under method/ (owned by the parallel workstream).
        card = AgentCard(
            decision="test decision", leaks=["Latency"], archetype="Optimiser",
            authority="L1 — Recommend",
            financial_lines=[FinancialLine(line="test line", evidence_class="C")],
            honest_limit="test limit", pack="_tmp_zero_pack.yaml",
        )
        fake_agent = SimpleNamespace(agent_id="TEST-0", display_name="Test Agent", card=card)
        original_pack_dir = build.PACK_DIR
        build.PACK_DIR = fixture
        try:
            record = build._card_record(fake_agent)
        finally:
            build.PACK_DIR = original_pack_dir

        assert "coverage" in record, "coverage is absent, which reads as full coverage"
        assert record["coverage"]["instrumented"] == 0
        assert record["coverage"]["total"] > 0
    finally:
        pack_path.unlink(missing_ok=True)


def test_coverage_is_computed_from_the_pack_file_not_memorised():
    """Mutation-style proof that the coverage helper reads the file it is
    pointed at, rather than returning a number decided in advance."""
    import scripts.build_app_data as build

    fixture = ROOT / "tests" / "scripts" / "fixtures"
    fixture.mkdir(exist_ok=True)
    pack_path = fixture / "_tmp_coverage_pack.yaml"
    try:
        pack_path.write_text(
            "metric: test metric\n"
            "root: test root\n"
            "drivers:\n"
            "  - id: d1\n"
            "    question: q1\n"
            "    controllable: false\n"
            "    status: instrumented\n"
            "    sql: sql/d1.sql\n"
            "  - id: d2\n"
            "    question: q2\n"
            "    controllable: false\n"
            "    status: not_instrumented\n"
            "  - id: d3\n"
            "    question: q3\n"
            "    controllable: false\n"
            "    status: not_instrumented\n"
            "  - id: d4\n"
            "    question: q4\n"
            "    controllable: false\n"
            "    status: not_instrumented\n"
        )
        assert build._coverage(pack_path) == {"instrumented": 1, "total": 4}

        # Rewrite the same file with a second driver instrumented and no
        # other change. A hardcoded {"instrumented": 1, "total": 4} would
        # fail this half; only a function that re-reads the file passes both.
        pack_path.write_text(
            pack_path.read_text().replace(
                "    status: not_instrumented\n",
                "    status: instrumented\n"
                "    sql: sql/d2.sql\n",
                1,
            )
        )
        assert build._coverage(pack_path) == {"instrumented": 2, "total": 4}
    finally:
        pack_path.unlink(missing_ok=True)


def test_agt19_card_is_exported_with_computed_coverage():
    # AGT-19 has no persona (design §3), so its card is not under personas.json
    # -- it is exported on the catalog for the value screen instead.
    from mining_agents.method.pack import load_pack
    catalog = json.loads((ROOT / "apps/shared/data/catalog.json").read_text())
    card = catalog["group_agents"]["AGT-19"]
    assert card["pack"] == "agt19-strategic-planning.yaml"
    pack = load_pack(ROOT / "method" / "agt19-strategic-planning.yaml")
    instrumented = sum(1 for d in pack.drivers if d.status == "instrumented")
    assert card["coverage"] == {"instrumented": instrumented, "total": len(pack.drivers)}


def test_leak_counts_are_derived_never_authored():
    # Independently recount every leak off the catalog's own agent cards plus
    # AGT-19, and compare against the exported leak_counts -- not a
    # tautology, because this rebuilds the tally from AgentDef.card rather
    # than reading what build_app_data.py already produced.
    from mining_agents.catalog.definitions import ALL_AGENTS, LEAKS
    catalog = json.loads((ROOT / "apps/shared/data/catalog.json").read_text())

    expected = {leak: 0 for leak in LEAKS}
    for agent in ALL_AGENTS:
        if agent.card is None:
            continue
        for leak in agent.card.leaks:
            expected[leak] += 1
    for leak in catalog["group_agents"]["AGT-19"]["leaks"]:
        expected[leak] += 1

    assert catalog["leaks"] == list(LEAKS)
    assert catalog["leak_counts"] == expected
    # Every one of the five leaks is claimed by at least one card. A count of
    # zero would mean a leak from the taxonomy has no agent behind it at all.
    for leak in LEAKS:
        assert catalog["leak_counts"][leak] > 0, f"no card claims the {leak!r} leak"
