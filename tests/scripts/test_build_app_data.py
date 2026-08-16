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
