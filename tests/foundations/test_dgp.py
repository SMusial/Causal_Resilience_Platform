"""
tests/foundations/test_dgp.py
================================
V0 Slice 2 — Structural DGP tests.

Covers spec section 17.1:
- same configuration and seed produce identical data
- potential outcomes exist in teaching mode
- observed outcome equals the potential outcome under assigned treatment
- severity is in [0, 1] and generated before treatment
- treatment assignment follows the selected mode
- oracle ATE equals the mean of generated potential-outcome differences
- normal mode does not expose oracle fields
- outcome units and ranges are valid
"""

import numpy as np
import pytest

from causal_resilience.foundations.dgp import TelecomFoundationsDGP
from causal_resilience.foundations.schemas import AssignmentMode, ScenarioConfig


@pytest.fixture
def dgp():
    return TelecomFoundationsDGP()


def make_config(**kwargs) -> ScenarioConfig:
    defaults = dict(seed=42, n_episodes=200, scenario_id="test")
    defaults.update(kwargs)
    return ScenarioConfig(**defaults)


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------

class TestReproducibility:
    def test_same_seed_same_data(self, dgp):
        cfg = make_config(seed=7)
        ds1 = dgp.generate(cfg)
        ds2 = dgp.generate(cfg)
        df1 = ds1.to_dataframe()
        df2 = ds2.to_dataframe()
        assert list(df1["outcome"]) == list(df2["outcome"])
        assert list(df1["treatment"]) == list(df2["treatment"])
        assert list(df1["severity"]) == list(df2["severity"])

    def test_different_seeds_different_data(self, dgp):
        ds1 = dgp.generate(make_config(seed=1))
        ds2 = dgp.generate(make_config(seed=2))
        outcomes1 = [ep.outcome for ep in ds1.episodes]
        outcomes2 = [ep.outcome for ep in ds2.episodes]
        assert outcomes1 != outcomes2

    def test_provenance_seed_matches_config(self, dgp):
        cfg = make_config(seed=99)
        ds = dgp.generate(cfg)
        assert ds.provenance.seed == 99

    def test_provenance_config_hash_stable(self, dgp):
        cfg = make_config(seed=42)
        ds1 = dgp.generate(cfg)
        ds2 = dgp.generate(cfg)
        assert ds1.provenance.config_hash == ds2.provenance.config_hash


# ---------------------------------------------------------------------------
# Episode structure
# ---------------------------------------------------------------------------

class TestEpisodeStructure:
    def test_episode_count_matches_config(self, dgp):
        cfg = make_config(n_episodes=150)
        ds = dgp.generate(cfg)
        assert len(ds.episodes) == 150

    def test_episode_ids_unique(self, dgp):
        ds = dgp.generate(make_config(n_episodes=100))
        ids = [ep.episode_id for ep in ds.episodes]
        assert len(set(ids)) == 100

    def test_severity_in_unit_interval(self, dgp):
        ds = dgp.generate(make_config(n_episodes=500))
        for ep in ds.episodes:
            assert 0.0 <= ep.severity <= 1.0

    def test_outcome_non_negative(self, dgp):
        ds = dgp.generate(make_config(n_episodes=500))
        for ep in ds.episodes:
            assert ep.outcome >= 0.0

    def test_treatment_binary(self, dgp):
        ds = dgp.generate(make_config(n_episodes=200))
        for ep in ds.episodes:
            assert ep.treatment in (0, 1)


# ---------------------------------------------------------------------------
# Oracle fields
# ---------------------------------------------------------------------------

class TestOracleFields:
    def test_oracle_hidden_in_normal_mode(self, dgp):
        ds = dgp.generate(make_config(teaching_mode=False))
        for ep in ds.episodes:
            assert ep.potential_outcome_0 is None
            assert ep.potential_outcome_1 is None
            assert ep.propensity_true is None

    def test_oracle_exposed_in_teaching_mode(self, dgp):
        ds = dgp.generate(make_config(teaching_mode=True))
        for ep in ds.episodes:
            assert ep.potential_outcome_0 is not None
            assert ep.potential_outcome_1 is not None
            assert ep.propensity_true is not None

    def test_to_dataframe_hides_oracle_in_normal_mode(self, dgp):
        ds = dgp.generate(make_config(teaching_mode=False))
        df = ds.to_dataframe()
        assert "potential_outcome_0" not in df.columns
        assert "potential_outcome_1" not in df.columns
        assert "propensity_true" not in df.columns

    def test_to_dataframe_exposes_oracle_in_teaching_mode(self, dgp):
        ds = dgp.generate(make_config(teaching_mode=True))
        df = ds.to_dataframe()
        assert "potential_outcome_0" in df.columns
        assert "potential_outcome_1" in df.columns
        assert "propensity_true" in df.columns


# ---------------------------------------------------------------------------
# Consistency rule: Y = Y(A)
# ---------------------------------------------------------------------------

class TestConsistency:
    def test_observed_outcome_equals_po_under_assigned_treatment(self, dgp):
        ds = dgp.generate(make_config(n_episodes=300, teaching_mode=True))
        for ep in ds.episodes:
            if ep.treatment == 1:
                assert abs(ep.outcome - ep.potential_outcome_1) < 1e-9
            else:
                assert abs(ep.outcome - ep.potential_outcome_0) < 1e-9


# ---------------------------------------------------------------------------
# Ground-truth oracle
# ---------------------------------------------------------------------------

class TestGroundTruth:
    def test_truth_requires_teaching_mode(self, dgp):
        ds = dgp.generate(make_config(teaching_mode=False))
        with pytest.raises(ValueError, match="teaching_mode"):
            dgp.truth(ds)

    def test_oracle_ate_equals_mean_individual_effects(self, dgp):
        ds = dgp.generate(make_config(n_episodes=500, teaching_mode=True))
        gt = dgp.truth(ds)
        individual_effects = [
            ep.potential_outcome_1 - ep.potential_outcome_0
            for ep in ds.episodes
        ]
        expected_ate = np.mean(individual_effects)
        assert abs(gt.finite_sample_ate - expected_ate) < 1e-9

    def test_oracle_mean_y1_minus_mean_y0_equals_ate(self, dgp):
        ds = dgp.generate(make_config(n_episodes=500, teaching_mode=True))
        gt = dgp.truth(ds)
        assert abs(gt.mean_y1 - gt.mean_y0 - gt.finite_sample_ate) < 1e-9

    def test_oracle_provenance_oracle_used_true(self, dgp):
        ds = dgp.generate(make_config(teaching_mode=True))
        gt = dgp.truth(ds)
        assert gt.provenance.oracle_used is True

    def test_oracle_n_episodes_matches_dataset(self, dgp):
        ds = dgp.generate(make_config(n_episodes=200, teaching_mode=True))
        gt = dgp.truth(ds)
        assert gt.n_episodes == 200


# ---------------------------------------------------------------------------
# Treatment assignment modes
# ---------------------------------------------------------------------------

class TestAssignmentModes:
    def test_randomized_propensity_is_half(self, dgp):
        ds = dgp.generate(make_config(
            n_episodes=1000, assignment_mode=AssignmentMode.RANDOMIZED,
            teaching_mode=True,
        ))
        propensities = [ep.propensity_true for ep in ds.episodes]
        assert all(abs(p - 0.5) < 1e-9 for p in propensities)

    def test_randomized_treatment_rate_near_half(self, dgp):
        ds = dgp.generate(make_config(
            n_episodes=2000, seed=0, assignment_mode=AssignmentMode.RANDOMIZED,
        ))
        rate = np.mean([ep.treatment for ep in ds.episodes])
        assert 0.42 < rate < 0.58

    def test_confounded_high_severity_more_treated(self, dgp):
        ds = dgp.generate(make_config(
            n_episodes=2000, seed=0,
            assignment_mode=AssignmentMode.CONFOUNDED,
            confounding_strength=4.0,
            teaching_mode=True,
        ))
        high = [ep for ep in ds.episodes if ep.severity > 0.7]
        low = [ep for ep in ds.episodes if ep.severity < 0.3]
        rate_high = np.mean([ep.treatment for ep in high])
        rate_low = np.mean([ep.treatment for ep in low])
        assert rate_high > rate_low

    def test_limited_overlap_extreme_propensities(self, dgp):
        ds = dgp.generate(make_config(
            n_episodes=1000, seed=0,
            assignment_mode=AssignmentMode.LIMITED_OVERLAP,
            teaching_mode=True,
        ))
        low_sev = [ep for ep in ds.episodes if ep.severity < 0.2]
        high_sev = [ep for ep in ds.episodes if ep.severity > 0.8]
        if low_sev:
            assert np.mean([ep.propensity_true for ep in low_sev]) < 0.15
        if high_sev:
            assert np.mean([ep.propensity_true for ep in high_sev]) > 0.85

    def test_confounded_propensity_varies_with_severity(self, dgp):
        ds = dgp.generate(make_config(
            n_episodes=500, assignment_mode=AssignmentMode.CONFOUNDED,
            confounding_strength=3.0, teaching_mode=True,
        ))
        propensities = np.array([ep.propensity_true for ep in ds.episodes])
        severities = np.array([ep.severity for ep in ds.episodes])
        correlation = np.corrcoef(severities, propensities)[0, 1]
        assert correlation > 0.5  # strong positive relationship


# ---------------------------------------------------------------------------
# Structural relationships
# ---------------------------------------------------------------------------

class TestStructuralRelationships:
    def test_severity_increases_expected_outcome_under_control(self, dgp):
        """Higher severity → higher Y(0) on average."""
        ds = dgp.generate(make_config(n_episodes=2000, teaching_mode=True))
        low = [ep.potential_outcome_0 for ep in ds.episodes if ep.severity < 0.3]
        high = [ep.potential_outcome_0 for ep in ds.episodes if ep.severity > 0.7]
        assert np.mean(high) > np.mean(low)

    def test_treatment_reduces_expected_outcome(self, dgp):
        """Y(1) < Y(0) on average when treatment_effect is negative."""
        ds = dgp.generate(make_config(
            n_episodes=2000, treatment_effect=-40.0, teaching_mode=True,
        ))
        gt = dgp.truth(ds)
        assert gt.finite_sample_ate < 0

    def test_treatment_effect_magnitude_approximately_correct(self, dgp):
        """Oracle ATE should be close to the configured treatment_effect."""
        cfg = make_config(
            n_episodes=5000, seed=0, treatment_effect=-40.0,
            outcome_noise_sd=5.0, teaching_mode=True,
        )
        ds = dgp.generate(cfg)
        gt = dgp.truth(ds)
        assert abs(gt.finite_sample_ate - (-40.0)) < 5.0
