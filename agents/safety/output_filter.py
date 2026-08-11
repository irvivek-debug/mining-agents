"""Biometric output masking. Enforced by code, not by prompt instruction.

Agents may say "OP-014 is HIGH fatigue risk". Agents may not emit a raw
heart rate, sleep deficit, or microsleep count.
"""
from __future__ import annotations

import re

REDACTION = "[REDACTED:BIOMETRIC]"

BIOMETRIC_FIELDS = (
    "heart_rate_bpm",
    "sleep_deficit_hours",
    "microsleep_events_detected",
)

_NUM = r"[-+]?\d+(?:\.\d+)?"

_PATTERNS = (
    # column-name forms: heart_rate_bpm of 118 / heart_rate_bpm = 118 / ... : 118
    *(re.compile(rf"(?i)\b{field}\b\s*(?:of|=|:|is|was)?\s*{_NUM}")
      for field in BIOMETRIC_FIELDS),
    # prose forms
    re.compile(rf"(?i)\bheart[ _]rate\b\s*(?:of|=|:|is|was)?\s*{_NUM}\s*(?:bpm)?"),
    re.compile(rf"(?i){_NUM}\s*bpm\b"),
    re.compile(rf"(?i)\bsleep[ _]deficit\b\s*(?:of|=|:|is|was)?\s*{_NUM}"),
    re.compile(rf"(?i)\bmicrosleep(?:[ _]events?)?\b\s*(?:of|=|:|is|was)?\s*{_NUM}"),
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
