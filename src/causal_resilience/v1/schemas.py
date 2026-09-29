"""
causal_resilience.v1.schemas
==============================
V1 Module 1 — Extended data contracts.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 3 — target trial, estimand, time zero, follow-up, eligibility

Causal question:
  Among eligible synthetic telecom incidents at detection (time_zero), what is
  the average effect of COORDINATED_RESPONSE versus MONITOR_REASSESS on
  customer_impact_minutes_24h over 24 hours?

Primary estimand:  ATE = E[Y(1) - Y(0)], mean-difference scale.
Secondary estimand: Risk difference for sla_breach_24h.

Relationship to V0:
  V1 reuses V0's TreatmentLabel, Provenance, Estimand, EstimateResult, and
  Diagnostic without redefining them. V1 extends the covariate set, adds a
  richer TargetTrial object, and introduces the six-role / seven-protocol
  operational world.

Implementation type: schema layer only — no estimator logic here.
Ground-truth validation: tests/v1/test_schemas.py
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from causal_resilience.foundations.schemas import (
    Provenance,
    TreatmentLabel,
)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DisturbanceType(str, Enum):
    EQUIPMENT_FAILURE = "equipment_failure"
    SOFTWARE_REGRESSION = "software_regression"
    MISCONFIGURATION = "misconfiguration"
    OVERLOAD = "overload"
    WEATHER_DISRUPTION = "weather_disruption"
    CYBERATTACK = "cyberattack"
    VANDALISM = "vandalism"


class OperationalRole(str, Enum):
    L1_FRONT_OFFICE = "L1_FRONT_OFFICE"
    NOC = "NOC"
    SOC = "SOC"
    L2_BACK_OFFICE = "L2_BACK_OFFICE"
    L3_PRODUCT = "L3_PRODUCT"
    FIELD_OPERATIONS = "FIELD_OPERATIONS"


class Protocol(str, Enum):
    MONITOR_REASSESS = "MONITOR_REASSESS"
    NOC_REMOTE = "NOC_REMOTE"
    SOC_CONTAIN = "SOC_CONTAIN"
    L2_INVESTIGATE = "L2_INVESTIGATE"
    L3_PRODUCT = "L3_PRODUCT"
    FIELD_REPAIR = "FIELD_REPAIR"
    COORDINATED_RESPONSE = "COORDINATED_RESPONSE"


class AssignmentMode(str, Enum):
    RANDOMIZED = "randomized"
    CONFOUNDED = "confounded"
    LIMITED_OVERLAP = "limited_overlap"


# ---------------------------------------------------------------------------
# Baseline covariates
# ---------------------------------------------------------------------------

class BaselineCovariates(BaseModel):
    """
    All baseline variables measured at time_zero, before treatment assignment.
    No post-treatment state may appear here.

    Source: design.md §5.2
    """
    # Disturbance
    disturbance_type: DisturbanceType
    severity: float = Field(..., ge=0.0, le=1.0,
                            description="Incident severity at detection [0, 1].")

    # Network topology
    topology_criticality: float = Field(..., ge=0.0, le=1.0,
                                        description="Criticality of affected network segment.")
    topology_redundancy: float = Field(..., ge=0.0, le=1.0,
                                       description="Available redundancy at detection.")

    # Customer impact
    affected_customers: int = Field(..., ge=0,
                                    description="Estimated customers affected at detection.")
    sla_priority: float = Field(..., ge=0.0, le=1.0,
                                description="SLA priority weight of affected services.")

    # Asset health
    asset_health: float = Field(..., ge=0.0, le=1.0,
                                description="Asset health index at detection.")
    fault_probability: float = Field(..., ge=0.0, le=1.0,
                                     description="Prior fault probability for affected asset.")

    # Security
    security_risk: float = Field(..., ge=0.0, le=1.0,
                                 description="Security risk score at detection.")

    # Operational state
    team_backlog: float = Field(..., ge=0.0,
                                description="Normalised team queue backlog at detection.")
    operational_readiness: float = Field(..., ge=0.0, le=1.0,
                                         description="Team readiness score at detection.")
    observability_quality: float = Field(..., ge=0.0, le=1.0,
                                         description="Signal quality / observability at detection.")

    # Environment
    weather_access_penalty: float = Field(0.0, ge=0.0, le=1.0,
                                          description="Weather/access difficulty [0=none, 1=severe].")


# ---------------------------------------------------------------------------
# Target trial
# ---------------------------------------------------------------------------

class TargetTrial(BaseModel):
    """
    Structured target-trial specification.
    Must be defined before any estimator is chosen.

    Source: Hernán & Robins, What If, Chapter 3 (§3.1-3.2)
    """
    eligibility: str
    time_zero: str
    intervention: Protocol
    comparator: Protocol
    assignment: str
    follow_up_hours: int = 24
    primary_outcome: str = "customer_impact_minutes_24h"
    primary_outcome_units: str = "minutes"
    secondary_outcome: str = "sla_breach_24h"
    censoring: str = "None in V1 base scenario — complete outcome observation assumed."
    causal_contrast: str = "Population average treatment effect (ATE)"
    primary_estimand: str = "E[Y(1) - Y(0)] on the mean-difference scale"
    secondary_estimand: str = "E[Y(1) - Y(0)] on the risk-difference scale for sla_breach_24h"
    direction_of_benefit: Literal["lower", "higher"] = "lower"
    notes: str = ""


# ---------------------------------------------------------------------------
# V1 canonical target trial (module-level constant)
# ---------------------------------------------------------------------------

V1_TARGET_TRIAL = TargetTrial(
    eligibility=(
        "Eligible synthetic telecom incidents at detection with observed "
        "baseline covariates and both intervention strategies feasible."
    ),
    time_zero="First reliable detection timestamp.",
    intervention=Protocol.COORDINATED_RESPONSE,
    comparator=Protocol.MONITOR_REASSESS,
    assignment="Randomized or observational, depending on selected DGP scenario.",
    follow_up_hours=24,
    notes=(
        "COORDINATED_RESPONSE is a fixed, documented bundle: NOC/SOC triage "
        "handoff, initial containment or service-stabilisation action, and a "
        "documented reassessment checkpoint — all within 15 minutes of detection."
    ),
)


# ---------------------------------------------------------------------------
# V1 estimand
# ---------------------------------------------------------------------------

class V1Estimand(BaseModel):
    """
    Extended estimand for V1. Reuses V0 assumptions and adds V1-specific
    confounders and secondary outcome.
    """
    name: str = "ATE"
    description: str = "E[Y(1) - Y(0)] — average effect of COORDINATED_RESPONSE vs MONITOR_REASSESS"
    treatment_label_1: Protocol = Protocol.COORDINATED_RESPONSE
    treatment_label_0: Protocol = Protocol.MONITOR_REASSESS
    primary_outcome: str = "customer_impact_minutes_24h"
    primary_outcome_units: str = "minutes"
    secondary_outcome: str = "sla_breach_24h"
    follow_up_hours: int = 24
    population: str = "Eligible synthetic telecom incidents at detection"
    time_zero: str = "First reliable detection timestamp"
    adjustment_set: list[str] = Field(
        default=[
            "severity",
            "topology_criticality",
            "team_backlog",
            "operational_readiness",
        ],
        description="Minimum sufficient adjustment set under the V1 baseline DAG.",
    )
    assumptions: list[str] = Field(
        default=[
            "Consistency: observed outcome equals potential outcome under assigned treatment.",
            "Exchangeability: Y(a) ⊥ A | baseline covariates (conditional on adjustment set).",
            "Positivity: 0 < P(A=1 | covariates=l) < 1 for all l in target population.",
            "No interference: one episode's treatment does not affect another's outcome.",
            "Complete follow-up: 24-hour outcome is observed for all eligible episodes.",
            "No unmeasured confounding: all common causes of treatment and outcome are in the adjustment set.",
        ]
    )


# ---------------------------------------------------------------------------
# V1 scenario configuration
# ---------------------------------------------------------------------------

class V1ScenarioConfig(BaseModel):
    """
    Configuration for a V1 run. Extends V0 ScenarioConfig with V1-specific
    parameters. V0 foundations remain importable independently.
    """
    seed: int = Field(42, ge=0)
    n_episodes: int = Field(500, ge=10, le=50_000)
    assignment_mode: AssignmentMode = AssignmentMode.RANDOMIZED
    confounding_strength: float = Field(3.0, ge=0.0, le=10.0)
    treatment_effect: float = Field(
        -40.0,
        description="Average reduction in customer_impact_minutes_24h. Negative = beneficial.",
    )
    outcome_noise_sd: float = Field(20.0, ge=0.0)
    teaching_mode: bool = False
    scenario_id: str = "v1-default"
    generator_version: str = "v1.0.0"
    schema_version: str = "v1.0.0"
    # V1 extensions
    disturbance_mix: dict[str, float] = Field(
        default={
            "equipment_failure": 0.25,
            "software_regression": 0.20,
            "misconfiguration": 0.20,
            "overload": 0.15,
            "weather_disruption": 0.10,
            "cyberattack": 0.05,
            "vandalism": 0.05,
        },
        description="Probability weights for disturbance types. Must sum to 1.0.",
    )
    include_measurement_error: bool = False
    include_missingness: bool = False
