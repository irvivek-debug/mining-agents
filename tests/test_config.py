import pytest
from agents.config import settings, model_for_tier


def test_settings_defaults_to_the_argolis_project():
    s = settings()
    assert s.project_id == "genial-union-475913-i7"
    assert s.dataset == "mining_data"
    assert s.location == "US"


def test_model_for_tier_resolves_both_tiers():
    reasoning = model_for_tier("reasoning")
    balanced = model_for_tier("balanced")
    assert reasoning and balanced
    assert reasoning != balanced


def test_model_for_tier_rejects_pattern_c_tier():
    with pytest.raises(ValueError):
        model_for_tier("high-volume-subagent")


def test_no_raw_model_id_outside_model_policy():
    """The design forbids raw model IDs anywhere but references/model-policy.md."""
    import pathlib, re
    root = pathlib.Path(__file__).resolve().parents[1]
    policy = root / "references" / "model-policy.md"
    pattern = re.compile(r"gemini-[0-9]")
    offenders = []
    for path in list(root.glob("agents/**/*.py")) + list(root.glob("tests/**/*.py")):
        if path == policy:
            continue
        if pattern.search(path.read_text()):
            offenders.append(str(path))
    assert offenders == [], f"raw model IDs found outside model-policy.md: {offenders}"
