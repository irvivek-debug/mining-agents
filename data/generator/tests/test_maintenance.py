"""Tests for data/generator/maintenance.py.

Verifies:
  - corr(repair_cost, actual_duration_hours) in [0.70, 0.90] on the 152-row join
  - every repair_cost reproducible from components to within $1
  - mean cost by priority ordered CRITICAL > HIGH > MEDIUM > LOW
  - total spend within 15% of $3,007,375
  - the 152 logged work orders remain exactly the COMPLETED ones
  - deterministic: two runs produce identical output
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest

from maintenance import generate_work_orders, generate_maintenance_logs, LABOUR_RATE, MOB_BASE, CREW_SIZE, compute_parts_cost

# ---------------------------------------------------------------------------
# Constants from the brief
# ---------------------------------------------------------------------------
SEED = 20260810
TARGET_TOTAL_SPEND = 3_007_375.0
TOTAL_SPEND_TOLERANCE = 0.15  # ±15%
CORR_LOW = 0.70
CORR_HIGH = 0.90
REPRODUCIBILITY_TOLERANCE = 1.0  # dollars


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def generated_data():
    """Generate both tables once and cache for all tests in this module."""
    wo = generate_work_orders(seed=SEED)
    ml = generate_maintenance_logs(seed=SEED)
    return wo, ml


@pytest.fixture(scope="module")
def joined(generated_data):
    """152-row join of work orders with maintenance logs."""
    wo, ml = generated_data
    j = wo.merge(ml, on="work_order_id", how="inner")
    return j


# ---------------------------------------------------------------------------
# Schema / structure tests
# ---------------------------------------------------------------------------

class TestSchemas:
    def test_work_orders_row_count(self, generated_data):
        wo, _ = generated_data
        assert len(wo) == 500, f"Expected 500 work orders, got {len(wo)}"

    def test_maintenance_logs_row_count(self, generated_data):
        _, ml = generated_data
        assert len(ml) == 152, f"Expected 152 maintenance logs, got {len(ml)}"

    def test_work_orders_columns(self, generated_data):
        wo, _ = generated_data
        expected = {"created_at", "repair_cost", "description", "work_order_id",
                    "priority", "status", "asset_id"}
        assert expected == set(wo.columns), f"Column mismatch: {set(wo.columns)}"

    def test_maintenance_logs_columns(self, generated_data):
        _, ml = generated_data
        expected = {"parts_replaced", "log_entry_id", "actual_duration_hours",
                    "asset_id", "technician_notes", "work_order_id"}
        assert expected == set(ml.columns), f"Column mismatch: {set(ml.columns)}"

    def test_repair_cost_positive(self, generated_data):
        wo, _ = generated_data
        assert (wo["repair_cost"] > 0).all(), "All repair costs must be positive"

    def test_actual_duration_in_range(self, generated_data):
        _, ml = generated_data
        assert ml["actual_duration_hours"].between(1.0, 19.0).all(), \
            f"Duration out of [1, 19] range: min={ml['actual_duration_hours'].min()}, max={ml['actual_duration_hours'].max()}"


# ---------------------------------------------------------------------------
# The "152 = COMPLETED" claim
# ---------------------------------------------------------------------------

class TestCompletedAlignment:
    def test_logged_work_orders_are_completed(self, generated_data):
        """All work orders with a maintenance log must have status=COMPLETED."""
        wo, ml = generated_data
        logged_wos = set(ml["work_order_id"])
        statuses = wo[wo["work_order_id"].isin(logged_wos)]["status"]
        assert (statuses == "COMPLETED").all(), \
            f"Non-COMPLETED work orders have logs: {statuses.value_counts().to_dict()}"

    def test_all_completed_have_logs(self, generated_data):
        """Every COMPLETED work order must have exactly one maintenance log."""
        wo, ml = generated_data
        completed_wos = set(wo[wo["status"] == "COMPLETED"]["work_order_id"])
        logged_wos = set(ml["work_order_id"])
        assert completed_wos == logged_wos, \
            f"COMPLETED/logged mismatch: {len(completed_wos)} COMPLETED, {len(logged_wos)} logged"

    def test_join_produces_152_rows(self, joined):
        assert len(joined) == 152, f"Expected 152-row join, got {len(joined)}"


# ---------------------------------------------------------------------------
# Cost / correlation tests
# ---------------------------------------------------------------------------

class TestCostModel:
    def test_correlation_in_band(self, joined):
        """corr(repair_cost, actual_duration_hours) must be in [0.70, 0.90]."""
        corr = joined["repair_cost"].corr(joined["actual_duration_hours"])
        assert CORR_LOW <= corr <= CORR_HIGH, \
            f"Correlation {corr:.4f} not in [{CORR_LOW}, {CORR_HIGH}]"

    def test_priority_ordering(self, generated_data):
        """mean cost: CRITICAL > HIGH > MEDIUM > LOW."""
        wo, _ = generated_data
        means = wo.groupby("priority")["repair_cost"].mean()
        assert means["CRITICAL"] > means["HIGH"], \
            f"CRITICAL mean {means['CRITICAL']:.2f} not > HIGH {means['HIGH']:.2f}"
        assert means["HIGH"] > means["MEDIUM"], \
            f"HIGH mean {means['HIGH']:.2f} not > MEDIUM {means['MEDIUM']:.2f}"
        assert means["MEDIUM"] > means["LOW"], \
            f"MEDIUM mean {means['MEDIUM']:.2f} not > LOW {means['LOW']:.2f}"

    def test_total_spend_within_15pct(self, generated_data):
        """Total spend within 15% of $3,007,375."""
        wo, _ = generated_data
        total = wo["repair_cost"].sum()
        ratio = abs(total - TARGET_TOTAL_SPEND) / TARGET_TOTAL_SPEND
        assert ratio <= TOTAL_SPEND_TOLERANCE, \
            f"Total spend {total:.2f} deviates {ratio*100:.1f}% from target {TARGET_TOTAL_SPEND:.2f}"

    def test_reproducibility_from_components(self, generated_data, joined):
        """Each repair_cost for COMPLETED WOs must be reproducible from components to within $1.

        For each row in the 152-row join, verify:
          repair_cost ≈ LABOUR_RATE * crew_size * actual_duration_hours + parts_cost + fixed_mobilisation
        within $1.
        """
        wo, ml = generated_data
        j = joined.copy()

        errors = []
        for _, row in j.iterrows():
            crew = CREW_SIZE[row["priority"]]
            mob = MOB_BASE * crew
            parts = compute_parts_cost(row["work_order_id"])
            expected = LABOUR_RATE * crew * row["actual_duration_hours"] + parts + mob
            diff = abs(row["repair_cost"] - expected)
            if diff > REPRODUCIBILITY_TOLERANCE:
                errors.append(
                    f"WO {row['work_order_id']}: expected {expected:.2f}, got {row['repair_cost']:.2f}, diff {diff:.2f}"
                )
        assert not errors, f"Reproducibility failures:\n" + "\n".join(errors[:5])


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_two_runs_identical_work_orders(self):
        """Two calls with the same seed must produce byte-identical work orders."""
        wo1 = generate_work_orders(seed=SEED)
        wo2 = generate_work_orders(seed=SEED)
        pd.testing.assert_frame_equal(wo1.reset_index(drop=True), wo2.reset_index(drop=True))

    def test_two_runs_identical_maintenance_logs(self):
        """Two calls with the same seed must produce byte-identical maintenance logs."""
        ml1 = generate_maintenance_logs(seed=SEED)
        ml2 = generate_maintenance_logs(seed=SEED)
        pd.testing.assert_frame_equal(ml1.reset_index(drop=True), ml2.reset_index(drop=True))
