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
    assert reasoning.startswith("gemini-"), f"reasoning tier returned unexpected model ID: {reasoning!r}"
    assert balanced.startswith("gemini-"), f"balanced tier returned unexpected model ID: {balanced!r}"
    assert reasoning != balanced


def test_both_configured_models_are_callable_in_this_project():
    """A withdrawn or misspelled model ID must fail here, not at deploy time.

    model-policy.md is edited by hand and nothing else validates it, so a typo
    would survive every other test in this suite and surface as a 404 on the
    first live agent run. One token per model keeps this cheap.
    """
    import json
    import urllib.error
    import urllib.request

    import google.auth
    import google.auth.transport.requests

    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    creds.refresh(google.auth.transport.requests.Request())
    project = settings().project_id
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
        "generationConfig": {"maxOutputTokens": 1},
    }).encode()

    for tier in ("reasoning", "balanced"):
        model = model_for_tier(tier)
        url = (
            f"https://aiplatform.googleapis.com/v1/projects/{project}"
            f"/locations/global/publishers/google/models/{model}:generateContent"
        )
        request = urllib.request.Request(url, data=body, headers={
            "Authorization": f"Bearer {creds.token}",
            "Content-Type": "application/json",
        })
        try:
            urllib.request.urlopen(request)
        except urllib.error.HTTPError as exc:
            raise AssertionError(
                f"tier {tier!r} names {model!r}, which this project cannot call "
                f"(HTTP {exc.code}). Fix references/model-policy.md."
            ) from exc


def test_no_floating_model_alias_is_configured():
    """A `-latest` alias changes underneath a demo and breaks reproducibility."""
    for tier in ("reasoning", "balanced"):
        assert not model_for_tier(tier).endswith("-latest"), tier


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
    for path in (list(root.glob("agents/**/*.py")) + list(root.glob("tests/**/*.py"))
                 + list(root.glob("infra/**/*.py"))):
        if path == policy:
            continue
        if pattern.search(path.read_text()):
            offenders.append(str(path))
    assert offenders == [], f"raw model IDs found outside model-policy.md: {offenders}"
