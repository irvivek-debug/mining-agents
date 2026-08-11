"""Environment-driven settings and tier-to-model resolution."""
from __future__ import annotations

import os
import pathlib
import re
from dataclasses import dataclass

_VALID_TIERS = ("reasoning", "balanced")
_ROW = re.compile(r"^\|\s*`(?P<tier>[a-z-]+)`\s*\|\s*`(?P<model>[^`]+)`\s*\|")


@dataclass(frozen=True)
class Settings:
    project_id: str
    dataset: str
    location: str
    bq_binary: str
    model_policy_path: pathlib.Path


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def settings() -> Settings:
    return Settings(
        project_id=os.environ.get("GOOGLE_CLOUD_PROJECT", "genial-union-475913-i7"),
        dataset=os.environ.get("MINING_DATASET", "mining_data"),
        location=os.environ.get("MINING_LOCATION", "US"),
        bq_binary=os.environ.get(
            "BQ_BINARY", str(pathlib.Path.home() / ".local" / "bin" / "bq")
        ),
        model_policy_path=_repo_root() / "references" / "model-policy.md",
    )


def model_for_tier(tier: str) -> str:
    """Resolve a model tier to a concrete model ID via references/model-policy.md."""
    if tier not in _VALID_TIERS:
        raise ValueError(
            f"unknown model tier {tier!r}; valid tiers are {_VALID_TIERS}"
        )
    text = settings().model_policy_path.read_text()
    for line in text.splitlines():
        match = _ROW.match(line.strip())
        if match and match.group("tier") == tier:
            return match.group("model")
    raise ValueError(f"tier {tier!r} not found in model-policy.md")
