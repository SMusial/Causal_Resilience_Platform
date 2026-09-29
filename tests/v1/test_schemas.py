"""
tests/v1/test_schemas.py
==========================
V1 Module 1 — Schema validation tests.
"""

import pytest
from pydantic import ValidationError

from causal_resilience.v1.schemas import (
    AssignmentMode,
    BaselineCovariates,
    DisturbanceType,
    OperationalRole,
    Protocol,
    TargetTrial,
    V1Estimand,
    V1ScenarioConfig,
    V1_TARGET_TRIAL,
)


# ---------------------------------------------------------------------------
# BaselineCovariates
# ---------------------------------------------------------------------------

def _valid_covariates(**overrides) -> dict:
    base = dict(
        disturbance_type=DisturbanceType.EQUIPMENT_FAILURE,
        severity=0.6,
        topology_criticality=0.7,
        topology_redundancy=0.4,
        affected_customers=500,
        sla_priority=0.8,
        asset_health=0.5,
        fault_probability=0.3,
        security_risk=0.1,
        team_backlog=0.4,
        operational_readiness=0.9,
        observability_quality=0.8,
    )
    base.update(overrides)
    return base


def test_baseline_covariates_valid():
    cov = BaselineCovariates(**_valid_covariates())
    assert cov.severity == 0.6
    assert cov.disturbance_type == DisturbanceType.EQUIPMENT_FAILURE


def test_baseline_covariates_severity_bounds():
    with pytest.raises(ValidationError):
        BaselineCovariates(**_valid_covariates(severity=1.5))
    with pytest.raises(ValidationError):
        BaselineCovariates(**_valid_covariates(severity=-0.1))


def test_baseline_covariates_no_post_treatment_fields():
    fields = set(BaselineCovariates.model_fields.keys())
    post_treatment = {"containment_action", "escalation_count", "state_history"}
    assert fields.isdisjoint(post_treatment)


def test_baseline_covariates_weather_default():
    cov = BaselineCovariates(**_valid_covariates())
    assert cov.weather_access_penalty == 0.0


# ---------------------------------------------------------------------------
# TargetTrial
# ---------------------------------------------------------------------------

def test_v1_target_trial_intervention():
    assert V1_TARGET_TRIAL.intervention == Protocol.COORDINATED_RESPONSE


def test_v1_target_trial_comparator():
    assert V1_TARGET_TRIAL.comparator == Protocol.MONITOR_REASSESS


def test_v1_target_trial_follow_up():
    assert V1_TARGET_TRIAL.follow_up_hours == 24


def test_v1_target_trial_primary_outcome():
    assert V1_TARGET_TRIAL.primary_outcome == "customer_impact_minutes_24h"


def test_v1_target_trial_secondary_outcome():
    assert V1_TARGET_TRIAL.secondary_outcome == "sla_breach_24h"


def test_v1_target_trial_direction_of_benefit():
    assert V1_TARGET_TRIAL.direction_of_benefit == "lower"


# ---------------------------------------------------------------------------
# V1Estimand
# ---------------------------------------------------------------------------

def test_v1_estimand_defaults():
    est = V1Estimand()
    assert est.name == "ATE"
    assert est.treatment_label_1 == Protocol.COORDINATED_RESPONSE
    assert est.treatment_label_0 == Protocol.MONITOR_REASSESS
    assert est.follow_up_hours == 24


def test_v1_estimand_adjustment_set_non_empty():
    est = V1Estimand()
    assert len(est.adjustment_set) >= 4


def test_v1_estimand_assumptions_non_empty():
    est = V1Estimand()
    assert len(est.assumptions) >= 5


def test_v1_estimand_mentions_positivity():
    est = V1Estimand()
    assert any("positivity" in a.lower() for a in est.assumptions)


def test_v1_estimand_mentions_exchangeability():
    est = V1Estimand()
    assert any("exchangeability" in a.lower() for a in est.assumptions)


# ---------------------------------------------------------------------------
# V1ScenarioConfig
# ---------------------------------------------------------------------------

def test_v1_scenario_config_defaults():
    cfg = V1ScenarioConfig()
    assert cfg.seed == 42
    assert cfg.assignment_mode == AssignmentMode.RANDOMIZED
    assert cfg.generator_version == "v1.0.0"


def test_v1_scenario_config_disturbance_mix_keys():
    cfg = V1ScenarioConfig()
    assert "cyberattack" in cfg.disturbance_mix
    assert "vandalism" in cfg.disturbance_mix


def test_v1_scenario_config_disturbance_mix_sums_to_one():
    cfg = V1ScenarioConfig()
    total = sum(cfg.disturbance_mix.values())
    assert abs(total - 1.0) < 1e-9


def test_v1_scenario_config_teaching_mode_default_false():
    cfg = V1ScenarioConfig()
    assert cfg.teaching_mode is False


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

def test_all_protocols_present():
    expected = {
        "MONITOR_REASSESS", "NOC_REMOTE", "SOC_CONTAIN",
        "L2_INVESTIGATE", "L3_PRODUCT", "FIELD_REPAIR", "COORDINATED_RESPONSE",
    }
    assert {p.value for p in Protocol} == expected


def test_all_roles_present():
    expected = {
        "L1_FRONT_OFFICE", "NOC", "SOC",
        "L2_BACK_OFFICE", "L3_PRODUCT", "FIELD_OPERATIONS",
    }
    assert {r.value for r in OperationalRole} == expected


def test_disturbance_includes_cyberattack_and_vandalism():
    values = {d.value for d in DisturbanceType}
    assert "cyberattack" in values
    assert "vandalism" in values
