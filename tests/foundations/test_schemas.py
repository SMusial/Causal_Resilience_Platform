"""
tests/foundations/test_schemas.py
===================================
V0 Slice 1 — Schema validation tests.

Covers:
- ScenarioConfig field validation and defaults
- Provenance construction and oracle_used flag
- IncidentEpisode binary treatment constraint
- IncidentEpisode consistency rule (outcome == potential_outcome under assigned treatment)
- FoundationsDataset empty-episode guard and to_dataframe oracle hiding
- GroundTruth construction
- Estimand defaults and assumption list
- Diagnostic levels
- EstimateResult construction and has_warnings property
- OracleComparison construction
"""

import pytest
from datetime import datetime

from pydantic import ValidationError

from causal_resilience.foundations.schemas import (
    AssignmentMode,
    Diagnostic,
    DiagnosticLevel,
    Estimand,
    EstimateResult,
    FoundationsDataset,
    GroundTruth,
    IncidentEpisode,
    OracleComparison,
    Provenance,
    ScenarioConfig,
    TreatmentLabel,
    DisturbanceType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_provenance(**kwargs) -> Provenance:
    defaults = dict(seed=42, scenario_id="test", generator_version="v0.0.1", schema_version="v0.0.1")
    defaults.update(kwargs)
    return Provenance(**defaults)


def make_episode(
    treatment: int = 1,
    outcome: float = 60.0,
    po0: float | None = None,
    po1: float | None = None,
    propensity: float | None = None,
) -> IncidentEpisode:
    return IncidentEpisode(
        episode_id="ep-001",
        severity=0.5,
        disturbance_type=DisturbanceType.EQUIPMENT_FAILURE,
        treatment=treatment,
        treatment_label=(
            TreatmentLabel.EARLY_COORDINATED_RESPONSE if treatment == 1
            else TreatmentLabel.MONITOR_REASSESS
        ),
        outcome=outcome,
        potential_outcome_0=po0,
        potential_outcome_1=po1,
        propensity_true=propensity,
    )


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

class TestProvenance:
    def test_defaults(self):
        p = make_provenance()
        assert p.oracle_used is False
        assert p.generator_version == "v0.0.1"
        assert isinstance(p.created_at, datetime)

    def test_oracle_used_flag(self):
        p = make_provenance(oracle_used=True)
        assert p.oracle_used is True

    def test_config_hash_optional(self):
        p = make_provenance()
        assert p.config_hash is None


# ---------------------------------------------------------------------------
# ScenarioConfig
# ---------------------------------------------------------------------------

class TestScenarioConfig:
    def test_defaults(self):
        cfg = ScenarioConfig()
        assert cfg.seed == 42
        assert cfg.n_episodes == 500
        assert cfg.assignment_mode == AssignmentMode.RANDOMIZED
        assert cfg.teaching_mode is False

    def test_confounded_mode(self):
        cfg = ScenarioConfig(assignment_mode=AssignmentMode.CONFOUNDED, confounding_strength=4.0)
        assert cfg.assignment_mode == AssignmentMode.CONFOUNDED
        assert cfg.confounding_strength == 4.0

    def test_n_episodes_lower_bound(self):
        with pytest.raises(ValidationError):
            ScenarioConfig(n_episodes=5)

    def test_n_episodes_upper_bound(self):
        with pytest.raises(ValidationError):
            ScenarioConfig(n_episodes=100_001)

    def test_confounding_strength_bounds(self):
        with pytest.raises(ValidationError):
            ScenarioConfig(confounding_strength=-1.0)
        with pytest.raises(ValidationError):
            ScenarioConfig(confounding_strength=11.0)

    def test_overlap_mode_values(self):
        cfg_a = ScenarioConfig(overlap_mode="adequate")
        cfg_l = ScenarioConfig(overlap_mode="limited")
        assert cfg_a.overlap_mode == "adequate"
        assert cfg_l.overlap_mode == "limited"

    def test_invalid_overlap_mode(self):
        with pytest.raises(ValidationError):
            ScenarioConfig(overlap_mode="unknown")


# ---------------------------------------------------------------------------
# IncidentEpisode
# ---------------------------------------------------------------------------

class TestIncidentEpisode:
    def test_valid_treated_episode_no_oracle(self):
        ep = make_episode(treatment=1, outcome=60.0)
        assert ep.treatment == 1
        assert ep.treatment_label == TreatmentLabel.EARLY_COORDINATED_RESPONSE
        assert ep.potential_outcome_0 is None
        assert ep.potential_outcome_1 is None

    def test_valid_control_episode_no_oracle(self):
        ep = make_episode(treatment=0, outcome=100.0)
        assert ep.treatment == 0
        assert ep.treatment_label == TreatmentLabel.MONITOR_REASSESS

    def test_treatment_must_be_binary(self):
        with pytest.raises(ValidationError):
            make_episode(treatment=2)

    def test_severity_bounds(self):
        with pytest.raises(ValidationError):
            IncidentEpisode(
                episode_id="x", severity=1.5,
                disturbance_type=DisturbanceType.OVERLOAD,
                treatment=0, treatment_label=TreatmentLabel.MONITOR_REASSESS,
                outcome=50.0,
            )

    def test_outcome_non_negative(self):
        with pytest.raises(ValidationError):
            make_episode(treatment=1, outcome=-1.0)

    def test_consistency_treated_passes(self):
        ep = make_episode(treatment=1, outcome=60.0, po1=60.0, po0=100.0)
        assert ep.outcome == ep.potential_outcome_1

    def test_consistency_control_passes(self):
        ep = make_episode(treatment=0, outcome=100.0, po0=100.0, po1=60.0)
        assert ep.outcome == ep.potential_outcome_0

    def test_consistency_violation_treated(self):
        with pytest.raises(ValidationError, match="Consistency violation"):
            make_episode(treatment=1, outcome=60.0, po1=70.0)

    def test_consistency_violation_control(self):
        with pytest.raises(ValidationError, match="Consistency violation"):
            make_episode(treatment=0, outcome=100.0, po0=90.0)

    def test_oracle_fields_none_in_normal_mode(self):
        ep = make_episode(treatment=1, outcome=60.0)
        assert ep.propensity_true is None


# ---------------------------------------------------------------------------
# FoundationsDataset
# ---------------------------------------------------------------------------

class TestFoundationsDataset:
    def _make_dataset(self, n: int = 3, teaching: bool = False) -> FoundationsDataset:
        episodes = []
        for i in range(n):
            t = i % 2
            po0, po1 = (100.0, 60.0) if teaching else (None, None)
            outcome = po1 if t == 1 else po0
            if outcome is None:
                outcome = 60.0 if t == 1 else 100.0
            episodes.append(
                IncidentEpisode(
                    episode_id=f"ep-{i:03d}",
                    severity=0.5,
                    disturbance_type=DisturbanceType.EQUIPMENT_FAILURE,
                    treatment=t,
                    treatment_label=(
                        TreatmentLabel.EARLY_COORDINATED_RESPONSE if t == 1
                        else TreatmentLabel.MONITOR_REASSESS
                    ),
                    outcome=outcome,
                    potential_outcome_0=po0,
                    potential_outcome_1=po1,
                )
            )
        return FoundationsDataset(
            episodes=episodes,
            provenance=make_provenance(),
            teaching_mode=teaching,
        )

    def test_empty_episodes_rejected(self):
        with pytest.raises(ValidationError):
            FoundationsDataset(episodes=[], provenance=make_provenance())

    def test_to_dataframe_normal_mode_hides_oracle(self):
        ds = self._make_dataset(n=4, teaching=False)
        df = ds.to_dataframe()
        assert "potential_outcome_0" not in df.columns
        assert "potential_outcome_1" not in df.columns
        assert "propensity_true" not in df.columns

    def test_to_dataframe_teaching_mode_exposes_oracle(self):
        ds = self._make_dataset(n=4, teaching=True)
        df = ds.to_dataframe()
        assert "potential_outcome_0" in df.columns
        assert "potential_outcome_1" in df.columns

    def test_to_dataframe_row_count(self):
        ds = self._make_dataset(n=6)
        assert len(ds.to_dataframe()) == 6

    def test_required_columns_present(self):
        ds = self._make_dataset(n=2)
        df = ds.to_dataframe()
        for col in ("episode_id", "severity", "treatment", "outcome"):
            assert col in df.columns


# ---------------------------------------------------------------------------
# GroundTruth
# ---------------------------------------------------------------------------

class TestGroundTruth:
    def test_construction(self):
        gt = GroundTruth(
            finite_sample_ate=-40.0,
            mean_y1=60.0,
            mean_y0=100.0,
            n_episodes=500,
            provenance=make_provenance(oracle_used=True),
        )
        assert gt.finite_sample_ate == pytest.approx(-40.0)
        assert gt.mean_y1 < gt.mean_y0

    def test_oracle_used_flag_set(self):
        gt = GroundTruth(
            finite_sample_ate=-40.0, mean_y1=60.0, mean_y0=100.0,
            n_episodes=100, provenance=make_provenance(oracle_used=True),
        )
        assert gt.provenance.oracle_used is True


# ---------------------------------------------------------------------------
# Estimand
# ---------------------------------------------------------------------------

class TestEstimand:
    def test_defaults(self):
        e = Estimand()
        assert e.name == "ATE"
        assert e.outcome_name == "customer_impact_minutes_24h"
        assert e.follow_up_hours == 24
        assert e.direction_of_benefit == "lower"
        assert len(e.assumptions) == 5

    def test_custom_estimand(self):
        e = Estimand(name="ATT", description="Average Treatment effect on the Treated")
        assert e.name == "ATT"

    def test_assumption_list_non_empty(self):
        e = Estimand()
        assert all(isinstance(a, str) and len(a) > 0 for a in e.assumptions)


# ---------------------------------------------------------------------------
# Diagnostic
# ---------------------------------------------------------------------------

class TestDiagnostic:
    def test_warning_level(self):
        d = Diagnostic(level=DiagnosticLevel.WARNING, code="OVERLAP_WARNING", message="Low overlap.")
        assert d.level == DiagnosticLevel.WARNING

    def test_error_level(self):
        d = Diagnostic(level=DiagnosticLevel.ERROR, code="POSITIVITY_VIOLATION", message="No overlap.")
        assert d.level == DiagnosticLevel.ERROR

    def test_detail_optional(self):
        d = Diagnostic(level=DiagnosticLevel.INFO, code="INFO_01", message="OK")
        assert d.detail is None


# ---------------------------------------------------------------------------
# EstimateResult
# ---------------------------------------------------------------------------

class TestEstimateResult:
    def _make_result(self, warnings=None, diagnostics=None) -> EstimateResult:
        return EstimateResult(
            estimand_name="ATE",
            estimator_name="difference_in_means",
            estimate=-38.5,
            confidence_interval=(-45.0, -32.0),
            standard_error=3.2,
            sample_size=500,
            treatment_counts={"treated": 250, "control": 250},
            assumptions=["Consistency", "Exchangeability"],
            diagnostics=diagnostics or [],
            warnings=warnings or [],
            provenance=make_provenance(),
        )

    def test_basic_construction(self):
        r = self._make_result()
        assert r.estimate == pytest.approx(-38.5)
        assert r.sample_size == 500
        assert r.oracle_comparison is None

    def test_has_warnings_false_when_clean(self):
        r = self._make_result()
        assert r.has_warnings is False

    def test_has_warnings_true_with_warning_string(self):
        r = self._make_result(warnings=["Extreme weights detected."])
        assert r.has_warnings is True

    def test_has_warnings_true_with_diagnostic_warning(self):
        d = Diagnostic(level=DiagnosticLevel.WARNING, code="W01", message="Low ESS.")
        r = self._make_result(diagnostics=[d])
        assert r.has_warnings is True

    def test_oracle_comparison_attached(self):
        oc = OracleComparison(
            oracle_ate=-40.0, estimate=-38.5,
            absolute_error=1.5, relative_error_pct=3.75,
        )
        r = self._make_result()
        r2 = r.model_copy(update={"oracle_comparison": oc})
        assert r2.oracle_comparison.oracle_ate == pytest.approx(-40.0)

    def test_treatment_counts_keys(self):
        r = self._make_result()
        assert "treated" in r.treatment_counts
        assert "control" in r.treatment_counts
