import pytest
from agents.safety.output_filter import (
    BIOMETRIC_FIELDS,
    RawBiometricLeak,
    assert_clean,
    scrub,
)


# ---------------------------------------------------------------------------
# Existing baseline tests
# ---------------------------------------------------------------------------

def test_a_banded_statement_is_left_alone():
    text = "OP-014 is HIGH fatigue risk and should be stood down."
    assert scrub(text) == text
    assert_clean(text)


def test_a_raw_heart_rate_is_redacted():
    out = scrub("OP-014 shows heart_rate_bpm of 118 during shift 3.")
    assert "118" not in out
    assert "[REDACTED:BIOMETRIC]" in out


def test_prose_phrasing_is_caught_too():
    out = scrub("Her heart rate was 118 bpm at 04:00.")
    assert "118" not in out
    assert "[REDACTED:BIOMETRIC]" in out  # pinned: must replace, not just strip


def test_sleep_deficit_and_microsleep_counts_are_redacted():
    out = scrub("sleep_deficit_hours = 3.4 and microsleep_events_detected = 5")
    assert "3.4" not in out
    assert "5" not in out
    assert out.count("[REDACTED:BIOMETRIC]") == 2  # pinned: exactly two redactions


def test_the_operator_pseudonym_is_retained():
    """Banding OP-014 would make S10's stand-down action unactionable."""
    out = scrub("OP-014 heart_rate_bpm 118")
    assert "OP-014" in out


def test_assert_clean_raises_on_a_leak():
    with pytest.raises(RawBiometricLeak):
        assert_clean("heart_rate_bpm 118")


# ---------------------------------------------------------------------------
# C-1 / C-2: JSON and Python repr shapes must be caught
# ---------------------------------------------------------------------------

def test_json_dict_payload_is_fully_redacted():
    """C-1/C-2: bq_query returns rows as Python dicts; their JSON repr must be caught."""
    payload = (
        '{"heart_rate_bpm": 118, "sleep_deficit_hours": 3.4, '
        '"microsleep_events_detected": 5}'
    )
    out = scrub(payload)
    assert "118" not in out
    assert "3.4" not in out
    assert "5" not in out
    assert out.count("[REDACTED:BIOMETRIC]") == 3

def test_python_repr_payload_is_fully_redacted():
    """C-1/C-2: Python repr uses single-quotes — must also be caught."""
    payload = "{'heart_rate_bpm': 118, 'sleep_deficit_hours': 3.4, 'microsleep_events_detected': 5}"
    out = scrub(payload)
    assert "118" not in out
    assert "3.4" not in out
    assert "5" not in out
    assert out.count("[REDACTED:BIOMETRIC]") == 3


def test_pretty_printed_json_payload_is_fully_redacted():
    """C-1/C-2: multi-line pretty-printed JSON (as logged by some BigQuery clients)."""
    payload = (
        "{\n"
        '  "heart_rate_bpm": 118,\n'
        '  "sleep_deficit_hours": 3.4,\n'
        '  "microsleep_events_detected": 5\n'
        "}"
    )
    out = scrub(payload)
    assert "118" not in out
    assert "3.4" not in out
    assert "5" not in out
    assert out.count("[REDACTED:BIOMETRIC]") == 3


# ---------------------------------------------------------------------------
# I-1: alternate prose phrasings must be caught
# ---------------------------------------------------------------------------

def test_beats_per_minute_phrasing_is_caught():
    """I-1: '118 beats per minute' — only bpm abbreviation was previously covered."""
    out = scrub("Operator recorded 118 beats per minute during exertion.")
    assert "118" not in out
    assert "[REDACTED:BIOMETRIC]" in out


def test_heart_rate_elevated_to_connector_is_caught():
    """I-1: connector 'to' was missing from the alternation."""
    out = scrub("heart rate elevated to 118")
    assert "118" not in out
    assert "[REDACTED:BIOMETRIC]" in out


def test_sleep_debt_synonym_is_caught():
    """I-1: 'sleep debt' used interchangeably with 'sleep deficit' in reports."""
    out = scrub("sleep debt: 3.4 hours logged for this shift.")
    assert "3.4" not in out
    assert "[REDACTED:BIOMETRIC]" in out


def test_microsleep_count_phrasing_is_caught():
    """I-1: 'microsleep count' phrasing not previously covered."""
    out = scrub("microsleep count: 5 detected in the last two hours.")
    assert "5" not in out
    assert "[REDACTED:BIOMETRIC]" in out


def test_pulse_abbreviation_is_caught():
    """I-1: 'pulse: 118' commonly used in incident reports."""
    out = scrub("Medic recorded pulse: 118 on arrival.")
    assert "118" not in out
    assert "[REDACTED:BIOMETRIC]" in out


def test_hr_abbreviation_is_caught():
    """I-1: 'HR: 118' used in wearable-device exports."""
    out = scrub("HR: 118 at 03:45 UTC")
    assert "118" not in out
    assert "[REDACTED:BIOMETRIC]" in out


# ---------------------------------------------------------------------------
# I-1 negative / anti-false-positive tests
# ---------------------------------------------------------------------------

def test_inventory_percentage_is_not_redacted():
    """I-1 guard: capacity percentage must survive untouched."""
    text = "inventory at 85% capacity"
    assert scrub(text) == text


def test_distance_in_km_is_not_redacted():
    """I-1 guard: a bare number with a unit unrelated to biometrics must survive."""
    text = "truck ran 118 km on the eastern haul road"
    assert scrub(text) == text


def test_shift_time_is_not_redacted():
    """I-1 guard: shift start times (colon-separated) must survive untouched."""
    text = "shift 3 started at 06:00"
    assert scrub(text) == text


# ---------------------------------------------------------------------------
# M-3: prose coverage must stay in sync with BIOMETRIC_FIELDS
# ---------------------------------------------------------------------------

def test_prose_coverage_matches_biometric_fields():
    """M-3: if BIOMETRIC_FIELDS gains a member, this test fails loudly.

    Each field in BIOMETRIC_FIELDS must be detectable in a bare column-name
    form (field_name: <number>).  The column-name patterns are generated from
    BIOMETRIC_FIELDS, so this test actually validates the generator loop rather
    than hand-written prose, but it will also catch a case where someone removes
    a field from BIOMETRIC_FIELDS without a corresponding change elsewhere.
    """
    for field in BIOMETRIC_FIELDS:
        payload = f"{field}: 99"
        out = scrub(payload)
        assert "99" not in out, (
            f"Field '{field}' in BIOMETRIC_FIELDS has no working pattern — "
            f"add a column-name pattern for it in _PATTERNS"
        )
        assert "[REDACTED:BIOMETRIC]" in out, (
            f"Field '{field}' in BIOMETRIC_FIELDS produced no redaction token"
        )
