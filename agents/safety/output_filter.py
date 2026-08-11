"""Biometric output masking. Enforced by code, not by prompt instruction.

Agents may say "OP-014 is HIGH fatigue risk". Agents may not emit a raw
heart rate, sleep deficit, or microsleep count.
"""
from __future__ import annotations

import re

REDACTION = "[REDACTED:BIOMETRIC]"

# Exactly three sensitive columns — if you add a fourth here you MUST also add
# a matching prose pattern below, or the test_prose_coverage_matches_biometric_fields
# test will fail loudly.
BIOMETRIC_FIELDS = (
    "heart_rate_bpm",
    "sleep_deficit_hours",
    "microsleep_events_detected",
)

_NUM = r"[-+]?\d+(?:\.\d+)?"

# Between a column name and its numeric value, JSON, Python repr, and prose all
# insert different punctuation.  The connector group accepts: optional
# whitespace, then an optional run of punctuation characters (quotes, brackets,
# braces, commas) and/or keyword connectors (of/=/:/is/was/to), then optional
# whitespace again.  This matches all of:
#   heart_rate_bpm 118          (bare)
#   heart_rate_bpm: 118         (colon connector)
#   "heart_rate_bpm": 118       (JSON)
#   'heart_rate_bpm': 118       (Python repr)
#   heart_rate_bpm = 118        (assignment)
#   heart_rate_bpm is 118       (natural language)
#   {"heart_rate_bpm": 118, …}  (JSON object)
_CONN = r"""[\s"'{\[,]*(?:of|=|:|is|was|to)?[\s"'\]},]*"""

_PATTERNS = (
    # column-name forms — connector allows JSON/repr punctuation between name and value
    *(re.compile(rf"(?i)\b{field}\b{_CONN}{_NUM}")
      for field in BIOMETRIC_FIELDS),
    # prose: heart rate / heart_rate — connector includes "elevated to", "increased to",
    # etc. where an adjective/verb precedes the "to".
    re.compile(rf"(?i)\bheart[ _]rate\b\s*(?:\w+\s+)?{_CONN}{_NUM}\s*(?:bpm)?"),
    # bpm abbreviation (e.g. "118 bpm", "pulse: 118 bpm")
    re.compile(rf"(?i){_NUM}\s*bpm\b"),
    # HR: 118 / pulse: 118 — short abbreviations commonly used in reports
    re.compile(rf"(?i)\b(?:HR|pulse)\s*[:\-=]\s*{_NUM}"),
    # beats per minute
    re.compile(rf"(?i){_NUM}\s*beats?\s+per\s+minute\b"),
    # sleep deficit / sleep debt
    re.compile(rf"(?i)\bsleep[ _](?:deficit|debt)\b{_CONN}{_NUM}"),
    # microsleep count / microsleep events
    re.compile(rf"(?i)\bmicrosleep(?:[ _](?:events?|count))?\b{_CONN}{_NUM}"),
)


class RawBiometricLeak(Exception):
    """A raw biometric value reached an agent output or log."""


def scrub(text: str) -> str:
    """Redact raw biometric values, preserving the operator pseudonym."""
    out = text
    for pattern in _PATTERNS:
        out = pattern.sub(REDACTION, out)
    return out


def assert_clean(text: str) -> None:
    """Raise if any raw biometric value is present. Used by the S05/S10 critics."""
    if scrub(text) != text:
        raise RawBiometricLeak(
            "raw biometric value present in output; use the v_fatigue_scored band"
        )
