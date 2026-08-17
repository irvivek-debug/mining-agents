"""Tests for data/generator/capital.py (Task 2b — AGT-19 plan/capital data).

Verifies schema, that every `plan_version_id` foreign key resolves, and the
design invariants the module docstring states: the capital option pipeline
grows rather than being a fixed list, and the contained-metal price
assumption is sampled from the same dense series R12 measures autocorrelation
on (not an independent number that happens to share a name). The banded
staleness-distribution and autocorrelation statistics are R13/R12 in
``test_realism.py``.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import pytest

import capital as CAP


@pytest.fixture(scope="module")
def plan_versions():
    return CAP.build_plan_versions()


@pytest.fixture(scope="module")
def plan_assumptions(plan_versions):
    return CAP.build_plan_assumptions(plan_versions)


@pytest.fixture(scope="module")
def plan_scenarios(plan_versions):
    return CAP.build_plan_scenarios(plan_versions)


@pytest.fixture(scope="module")
def capital_options(plan_versions):
    return CAP.build_capital_options(plan_versions)


class TestSchema:
    def test_plan_versions_columns(self, plan_versions):
        assert list(plan_versions.columns) == [
            "plan_version_id", "published_date", "next_review_date",
        ]

    def test_plan_assumptions_columns(self, plan_assumptions):
        assert list(plan_assumptions.columns) == [
            "assumption_id", "plan_version_id", "metric_name", "assumed_value",
            "effective_date", "superseded_date",
        ]

    def test_plan_scenarios_columns(self, plan_scenarios):
        assert list(plan_scenarios.columns) == [
            "scenario_id", "plan_version_id", "assumption_delta",
            "reversal_trigger", "reversal_cost",
        ]

    def test_capital_options_columns(self, capital_options):
        assert list(capital_options.columns) == [
            "option_id", "plan_version_id", "description",
        ]

    def test_six_quarterly_plan_versions_in_order(self, plan_versions):
        assert len(plan_versions) == 6
        published = pd.to_datetime(plan_versions.published_date)
        assert list(published) == sorted(published)

    def test_published_before_next_review(self, plan_versions):
        pub = pd.to_datetime(plan_versions.published_date)
        rev = pd.to_datetime(plan_versions.next_review_date)
        assert (pub < rev).all()

    def test_seven_metrics_per_plan_version(self, plan_assumptions):
        assert set(plan_assumptions.groupby("plan_version_id").size()) == {
            len(CAP.ASSUMPTION_METRICS)
        }


class TestForeignKeys:
    def test_plan_assumptions_plan_version_id_resolves(self, plan_versions, plan_assumptions):
        missing = set(plan_assumptions.plan_version_id) - set(plan_versions.plan_version_id)
        assert not missing

    def test_plan_scenarios_plan_version_id_resolves(self, plan_versions, plan_scenarios):
        missing = set(plan_scenarios.plan_version_id) - set(plan_versions.plan_version_id)
        assert not missing

    def test_capital_options_plan_version_id_resolves(self, plan_versions, capital_options):
        missing = set(capital_options.plan_version_id) - set(plan_versions.plan_version_id)
        assert not missing


class TestInvariants:
    def test_superseded_date_when_present_is_between_effective_and_next_review(
        self, plan_versions, plan_assumptions
    ):
        pv = plan_versions.set_index("plan_version_id")
        rows = plan_assumptions.dropna(subset=["superseded_date"])
        assert len(rows) > 0, "no assumption ever went stale — nothing for R13 to measure"
        for row in rows.itertuples():
            next_review = pd.Timestamp(pv.loc[row.plan_version_id, "next_review_date"])
            eff = pd.Timestamp(row.effective_date)
            sup = pd.Timestamp(row.superseded_date)
            assert eff < sup <= next_review, (
                f"{row.assumption_id}: superseded_date {sup} outside "
                f"({eff}, {next_review}]"
            )

    def test_some_assumptions_never_go_stale_in_window(self, plan_assumptions):
        never_stale = plan_assumptions[plan_assumptions.superseded_date.isna()]
        assert len(never_stale) > 0

    def test_capital_option_pipeline_grows_rather_than_being_fixed(self, capital_options):
        counts = capital_options.groupby("plan_version_id").size()
        assert counts.iloc[0] < counts.iloc[-1], (
            "the capital pipeline is the same size at the first plan version "
            "as the last — it should grow as CAP-D/CAP-E are added"
        )

    def test_capital_options_description_cites_the_live_fleet_maintenance_count(
        self, capital_options
    ):
        n = CAP.fleet_maintenance_count()
        assert any(f"{n} of" in d for d in capital_options.description), (
            "no capital_options.description cites the live MAINTENANCE-status "
            "fleet count"
        )

    def test_price_series_is_dense_enough_for_a_lag1_measurement(self):
        series = CAP.build_price_series()
        assert len(series) >= 50, "price series too short for a meaningful autocorrelation test"

    def test_price_metric_assumed_value_is_sampled_from_the_dense_series(
        self, plan_versions, plan_assumptions
    ):
        series = CAP.build_price_series().set_index("date").price_usd_per_tonne
        price_rows = plan_assumptions[plan_assumptions.metric_name == CAP.PRICE_METRIC]
        for row in price_rows.itertuples():
            target = pd.Timestamp(row.effective_date, tz="UTC")
            nearest = series.iloc[int((series.index - target).__abs__().argmin())]
            assert row.assumed_value == pytest.approx(float(nearest))
