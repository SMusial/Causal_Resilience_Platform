"""
tests/foundations/test_estimators.py
=======================================
V0 Slice 2 — Estimator tests.

Covers spec section 17.2:
- randomized DiM approaches oracle ATE as sample size increases
- crude observational DiM is visibly biased under confounding
- estimator outputs expose the correct estimand and assumptions
- bootstrap results are reproducible when the bootstrap seed is fixed
- EstimateResult structure is correct
"""

import numpy as np
import pytest

from causal_resilience.foundations.dgp import TelecomFoundationsDGP
from causal_resilience.foundations.estimators import DifferenceInMeans, EstimatorConfig
from causal_resilience.foundations.schemas import AssignmentMode, Estimand, ScenarioConfig


@pytest.fixture
def dgp():
    return TelecomFoundationsDGP()


@pytest.fixture
def estimand():
    return Estimand()


@pytest.fixture
def est_config():
    return EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=0)


def make_config(**kwargs) -> ScenarioConfig:
    defaults = dict(seed=42, scenario_id="test-est")
    defaults.update(kwargs)
    return ScenarioConfig(**defaults)


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------

class TestEstimateResultStructure:
    def test_returns_estimate_result(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(n_episodes=200))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        assert result.estimand_name == "ATE"
        assert result.estimator_name == "difference_in_means"
        assert isinstance(result.estimate, float)
        assert result.sample_size == 200

    def test_treatment_counts_sum_to_sample_size(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(n_episodes=300))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        assert result.treatment_counts["treated"] + result.treatment_counts["control"] == 300

    def test_confidence_interval_ordered(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(n_episodes=300))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        lo, hi = result.confidence_interval
        assert lo < hi

    def test_standard_error_positive(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(n_episodes=300))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        assert result.standard_error > 0

    def test_assumptions_list_non_empty(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(n_episodes=200))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        assert len(result.assumptions) > 0

    def test_provenance_attached(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(seed=7, n_episodes=200))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        assert result.provenance.seed == 7


# ---------------------------------------------------------------------------
# Randomized scenario: DiM approaches oracle ATE
# ---------------------------------------------------------------------------

class TestRandomizedDiM:
    def test_dim_close_to_oracle_large_sample(self, dgp, estimand, est_config):
        """
        With n=5000 and randomized assignment, the crude DiM should be
        within 5 minutes of the oracle ATE (treatment_effect=-40).
        Monte Carlo tolerance: 5 minutes at n=5000, noise_sd=20.
        """
        cfg = make_config(
            n_episodes=5000, seed=0,
            assignment_mode=AssignmentMode.RANDOMIZED,
            treatment_effect=-40.0, outcome_noise_sd=20.0,
            teaching_mode=True,
        )
        ds = dgp.generate(cfg)
        gt = dgp.truth(ds)
        result = DifferenceInMeans().estimate(ds, estimand, est_config, ground_truth=gt)
        assert abs(result.estimate - gt.finite_sample_ate) < 5.0

    def test_dim_converges_as_n_increases(self, dgp, estimand, est_config):
        """
        Absolute error should decrease as sample size grows.
        Compare n=200 vs n=2000 over multiple seeds.
        """
        errors_small, errors_large = [], []
        for seed in range(10):
            for n, store in [(200, errors_small), (2000, errors_large)]:
                cfg = make_config(
                    n_episodes=n, seed=seed,
                    assignment_mode=AssignmentMode.RANDOMIZED,
                    treatment_effect=-40.0, teaching_mode=True,
                )
                ds = dgp.generate(cfg)
                gt = dgp.truth(ds)
                result = DifferenceInMeans().estimate(ds, estimand, est_config)
                store.append(abs(result.estimate - gt.finite_sample_ate))
        assert np.mean(errors_large) < np.mean(errors_small)

    def test_oracle_comparison_populated_when_gt_provided(self, dgp, estimand, est_config):
        cfg = make_config(n_episodes=500, teaching_mode=True)
        ds = dgp.generate(cfg)
        gt = dgp.truth(ds)
        result = DifferenceInMeans().estimate(ds, estimand, est_config, ground_truth=gt)
        assert result.oracle_comparison is not None
        assert result.oracle_comparison.oracle_ate == pytest.approx(gt.finite_sample_ate)

    def test_oracle_comparison_none_when_gt_not_provided(self, dgp, estimand, est_config):
        ds = dgp.generate(make_config(n_episodes=200))
        result = DifferenceInMeans().estimate(ds, estimand, est_config)
        assert result.oracle_comparison is None


# ---------------------------------------------------------------------------
# Confounded scenario: DiM is biased
# ---------------------------------------------------------------------------

class TestConfoundedDiM:
    def test_crude_dim_biased_under_confounding(self, dgp, estimand, est_config):
        """
        Under strong confounding, the crude DiM should differ from the
        oracle ATE by more than 10 minutes on average across seeds.
        Severe incidents are more likely treated AND have worse outcomes,
        so the crude comparison overstates the harm (or understates benefit).
        """
        biases = []
        for seed in range(15):
            cfg = make_config(
                n_episodes=1000, seed=seed,
                assignment_mode=AssignmentMode.CONFOUNDED,
                confounding_strength=4.0,
                treatment_effect=-40.0, teaching_mode=True,
            )
            ds = dgp.generate(cfg)
            gt = dgp.truth(ds)
            result = DifferenceInMeans().estimate(ds, estimand, est_config)
            biases.append(result.estimate - gt.finite_sample_ate)
        # Bias should be consistently positive (crude DiM underestimates benefit)
        assert np.mean(biases) > 10.0

    def test_confounded_estimate_differs_from_randomized(self, dgp, estimand, est_config):
        """Same seed, same treatment effect — confounded DiM != randomized DiM."""
        cfg_rand = make_config(
            n_episodes=1000, seed=42,
            assignment_mode=AssignmentMode.RANDOMIZED,
            treatment_effect=-40.0,
        )
        cfg_conf = make_config(
            n_episodes=1000, seed=42,
            assignment_mode=AssignmentMode.CONFOUNDED,
            confounding_strength=4.0, treatment_effect=-40.0,
        )
        ds_rand = dgp.generate(cfg_rand)
        ds_conf = dgp.generate(cfg_conf)
        r_rand = DifferenceInMeans().estimate(ds_rand, estimand, est_config)
        r_conf = DifferenceInMeans().estimate(ds_conf, estimand, est_config)
        assert abs(r_rand.estimate - r_conf.estimate) > 5.0


# ---------------------------------------------------------------------------
# Bootstrap reproducibility
# ---------------------------------------------------------------------------

class TestBootstrapReproducibility:
    def test_same_bootstrap_seed_same_ci(self, dgp, estimand):
        ds = dgp.generate(make_config(n_episodes=300))
        cfg1 = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=7)
        cfg2 = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=7)
        r1 = DifferenceInMeans().estimate(ds, estimand, cfg1)
        r2 = DifferenceInMeans().estimate(ds, estimand, cfg2)
        assert r1.confidence_interval == r2.confidence_interval

    def test_different_bootstrap_seed_different_ci(self, dgp, estimand):
        ds = dgp.generate(make_config(n_episodes=300))
        cfg1 = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=1)
        cfg2 = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=2)
        r1 = DifferenceInMeans().estimate(ds, estimand, cfg1)
        r2 = DifferenceInMeans().estimate(ds, estimand, cfg2)
        # CIs will differ slightly due to different bootstrap samples
        assert r1.confidence_interval != r2.confidence_interval

    def test_ci_contains_oracle_ate_frequently(self, dgp, estimand):
        """
        95% CI should contain the oracle ATE in roughly 90%+ of runs
        under randomization with adequate sample size.
        """
        covered = 0
        n_trials = 50
        for seed in range(n_trials):
            cfg = make_config(
                n_episodes=500, seed=seed,
                assignment_mode=AssignmentMode.RANDOMIZED,
                treatment_effect=-40.0, teaching_mode=True,
            )
            ds = dgp.generate(cfg)
            gt = dgp.truth(ds)
            est_cfg = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=seed)
            result = DifferenceInMeans().estimate(ds, estimand, est_cfg)
            lo, hi = result.confidence_interval
            if lo <= gt.finite_sample_ate <= hi:
                covered += 1
        coverage = covered / n_trials
        assert coverage >= 0.85
