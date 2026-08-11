import pytest
from agents.safety.output_filter import RawBiometricLeak, assert_clean, scrub


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
