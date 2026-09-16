"""
tests/foundations/test_diagnostics.py
========================================
V0 Slice 5 — Diagnostic tests.

Covers spec section 17.3:
- overlap warning fires when propensity support is inadequate
- extreme-weight warning fires when IPW weights exceed the threshold
- effective sample size decreases as weights become more concentrated
- balance diagnostics identify severity imbalance before adjustment
- balance diagnostics improve after correctly specified adjustment
"""

import numpy as np
import pytest

from causal_resilience.foundations.diagnostics import (
    BalanceDiagnostic,
    OverlapDiagnostic,
    WeightDiagnostic,
    compute_balance,
    compute_overlap,
    compute_weight_diagnostic,
)


# ---------------------------------------------------------------------------
# Overlap diagnostics
# ---------------------------------------------------------------------------

class TestOverlapDiagnostic:
    def test_adequate_overlap_no_warning(self):
        rng = np.random.default_rng(0)
        n = 500
        propensity = rng.uniform(0.2, 0.8, size=n)
        treatment = rng.binomial(1, propensity)
        result = compute_overlap(propensity, treatment)
        assert result.overlap_adequate is True
        assert result.warning_message is None

    def test_non_overlapping_ranges_fires_warning(self):
        # treated group has propensity > 0.6, control < 0.4 — no common support
        propensity = np.concatenate([
            np.full(100, 0.8),   # treated
            np.full(100, 0.2),   # control
        ])
        treatment = np.concatenate([np.ones(100), np.zeros(100)])
        result = compute_overlap(propensity, treatment)
        assert result.overlap_adequate is False
        assert result.warning_message is not None

    def test_near_boundary_fires_warning(self):
        rng = np.random.default_rng(1)
        n = 200
        # Push many propensities near 0 or 1
        propensity = np.concatenate([
            rng.uniform(0.01, 0.04, size=n // 2),
            rng.uniform(0.96, 0.99, size=n // 2),
        ])
        treatment = rng.binomial(1, np.clip(propensity, 0.01, 0.99))
        result = compute_overlap(propensity, treatment)
        assert result.warning_message is not None

    def test_empty_group_returns_warning(self):
        propensity = np.array([0.5, 0.6, 0.7])
        treatment = np.array([1, 1, 1])   # no control group
        result = compute_overlap(propensity, treatment)
        assert result.overlap_adequate is False
        assert result.warning_message is not None

    def test_min_max_propensity_recorded(self):
        propensity = np.array([0.3, 0.5, 0.7, 0.4, 0.6])
        treatment = np.array([1, 1, 1, 0, 0])
        result = compute_overlap(propensity, treatment)
        assert result.min_propensity_treated == pytest.approx(0.3)
        assert result.max_propensity_treated == pytest.approx(0.7)
        assert result.min_propensity_control == pytest.approx(0.4)
        assert result.max_propensity_control == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Weight diagnostics
# ---------------------------------------------------------------------------

class TestWeightDiagnostic:
    def test_no_extreme_weights_no_warning(self):
        weights = np.array([1.0, 1.5, 2.0, 1.2, 0.8])
        result = compute_weight_diagnostic(weights, extreme_threshold=10.0)
        assert result.has_extreme_weights is False
        assert result.warning_message is None

    def test_extreme_weights_fire_warning(self):
        weights = np.array([1.0, 2.0, 15.0, 20.0, 1.5])
        result = compute_weight_diagnostic(weights, extreme_threshold=10.0)
        assert result.has_extreme_weights is True
        assert result.warning_message is not None

    def test_ess_equals_n_for_uniform_weights(self):
        n = 100
        weights = np.ones(n)
        result = compute_weight_diagnostic(weights)
        assert result.effective_sample_size == pytest.approx(n, rel=1e-6)

    def test_ess_decreases_with_concentrated_weights(self):
        # One episode gets all the weight
        weights_uniform = np.ones(100)
        weights_concentrated = np.zeros(100)
        weights_concentrated[0] = 100.0
        ess_uniform = compute_weight_diagnostic(weights_uniform).effective_sample_size
        ess_concentrated = compute_weight_diagnostic(weights_concentrated).effective_sample_size
        assert ess_concentrated < ess_uniform

    def test_pct_extreme_correct(self):
        weights = np.array([1.0, 5.0, 11.0, 12.0, 2.0])
        result = compute_weight_diagnostic(weights, extreme_threshold=10.0)
        assert result.pct_extreme == pytest.approx(0.4)

    def test_empty_weights_returns_nan(self):
        result = compute_weight_diagnostic(np.array([]))
        assert np.isnan(result.effective_sample_size)


# ---------------------------------------------------------------------------
# Balance diagnostics
# ---------------------------------------------------------------------------

class TestBalanceDiagnostic:
    def test_imbalanced_severity_detected(self):
        # Treated group has higher severity
        sev_t = np.full(100, 0.8)
        sev_c = np.full(100, 0.2)
        severity = np.concatenate([sev_t, sev_c])
        treatment = np.concatenate([np.ones(100), np.zeros(100)])
        result = compute_balance(severity, treatment)
        assert result.smd_unweighted > 0.1
        assert result.balance_adequate_unweighted is False

    def test_balanced_severity_passes(self):
        rng = np.random.default_rng(0)
        severity = rng.uniform(0, 1, size=200)
        treatment = rng.binomial(1, 0.5, size=200)
        result = compute_balance(severity, treatment)
        # Under randomization SMD should be small on average
        assert result.smd_unweighted < 0.5   # loose bound; randomization is not perfect

    def test_weighted_smd_smaller_than_unweighted_under_confounding(self):
        """
        Under confounding, IPW weights should reduce the SMD.
        Use a simple constructed case where weights perfectly balance severity.
        """
        rng = np.random.default_rng(42)
        n = 500
        severity = rng.uniform(0, 1, size=n)
        # Confounded: high severity -> treated
        propensity = 1 / (1 + np.exp(-4 * (severity - 0.5)))
        treatment = rng.binomial(1, propensity)
        # IPW weights
        weights = np.where(treatment == 1, 1.0 / propensity, 1.0 / (1.0 - propensity))
        result = compute_balance(severity, treatment, weights=weights)
        assert result.smd_weighted is not None
        assert result.smd_weighted < result.smd_unweighted

    def test_no_weights_returns_none_for_weighted_smd(self):
        severity = np.array([0.3, 0.5, 0.7, 0.4, 0.6])
        treatment = np.array([1, 1, 0, 0, 1])
        result = compute_balance(severity, treatment, weights=None)
        assert result.smd_weighted is None
        assert result.balance_adequate_weighted is None

    def test_empty_group_returns_nan(self):
        severity = np.array([0.5, 0.6])
        treatment = np.array([1, 1])
        result = compute_balance(severity, treatment)
        assert np.isnan(result.smd_unweighted)
