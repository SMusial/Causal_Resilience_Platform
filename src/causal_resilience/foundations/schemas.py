"""
causal_resilience.foundations.schemas
======================================
V0 Slice 1 — Pydantic data contracts.

Source: Hernán & Robins, *Causal Inference: What If*, Chapters 1–3.
Causal question: Among eligible synthetic telecom incidents at detection,
  what is the average effect of EARLY_COORDINATED_RESPONSE versus
  MONITOR_REASSESS on customer_impact_minutes_24h?
Estimand: ATE = E[Y(1) - Y(0)] on the mean-difference scale.
Assumptions declared: consistency, exchangeability, positivity,
  no interference, complete follow-up.
Implementation type: educational schema layer only (no estimator logic here).
Ground-truth validation: see tests/foundations/test_schemas.py.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AssignmentMode(str, Enum):
    """Treatment assignment mechanism for the DGP."""
    RANDOMIZED = "randomized"
    CONFOUNDED = "confounded"
    LIMITED_OVERLAP = "limited_overlap"


class DisturbanceType(str, Enum):
    """Abstract incident categories. Not required for V0 adjustment."""
    EQUIPMENT_FAILURE = "equipment_failure"
    SOFTWARE_REGRESSION = "software_regression"
    MISCONFIGURATION = "misconfiguration"
    OVERLOAD = "overload"
    WEATHER_DISRUPTION = "weather_disruption"
    CYBER_DISRUPTION = "cyber_disruption"
    PHYSICAL_DISRUPTION = "physical_disruption"


class TreatmentLabel(str, Enum):
    """Binary intervention contrast — V0 canonical names."""
    EARLY_COORDINATED_RESPONSE = "EARLY_COORDINATED_RESPONSE"
    MONITOR_REASSESS = "MONITOR_REASSESS"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

class Provenance(BaseModel):
    """
    Reproducibility metadata attached to every dataset and estimate.
    Same seed + scenario_id + generator_version + schema_version must
    reproduce identical data and deterministic results.
    """
    seed: int = Field(..., description="Random seed used for generation.")
    scenario_id: str = Field(..., description="Unique scenario identifier.")
    generator_version: str = Field("v0.0.1", description="DGP code version.")
    schema_version: str = Field("v0.0.1", description="Schema version.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    oracle_used: bool = Field(
        False,
        description="True only when oracle fields were used in this result.",
    )
    config_hash: str | None = Field(
        None,
        description="Hash of the ScenarioConfig for change detection.",
    )


# ---------------------------------------------------------------------------
# Scenario configuration
# ---------------------------------------------------------------------------

class ScenarioConfig(BaseModel):
    """
    All parameters needed to reproduce a V0 run.
    Changing any field changes the data-generating process.
    """
    seed: int = Field(42, ge=0)
    n_episodes: int = Field(500, ge=10, le=50_000)
    assignment_mode: AssignmentMode = AssignmentMode.RANDOMIZED
    confounding_strength: float = Field(
        3.0,
        ge=0.0,
        le=10.0,
        description=(
            "Logistic-regression coefficient for severity in the confounded "
            "assignment model. 0 = no confounding."
        ),
    )
    treatment_effect: float = Field(
        -40.0,
        description=(
            "Average reduction in customer_impact_minutes_24h under "
            "EARLY_COORDINATED_RESPONSE. Negative = beneficial."
        ),
    )
    outcome_noise_sd: float = Field(
        20.0,
        ge=0.0,
        description="Standard deviation of outcome noise.",
    )
    overlap_mode: Literal["adequate", "limited"] = "adequate"
    teaching_mode: bool = Field(
        False,
        description=(
            "When True, oracle fields (potential outcomes, true propensity) "
            "are included in the dataset. Must be labeled explicitly in UI."
        ),
    )
    scenario_id: str = Field("v0-default")
    generator_version: str = Field("v0.0.1")
    schema_version: str = Field("v0.0.1")


# ---------------------------------------------------------------------------
# Episode record
# ---------------------------------------------------------------------------

class IncidentEpisode(BaseModel):
    """One synthetic incident episode — the unit of analysis."""
    episode_id: str
    severity: float = Field(..., ge=0.0, le=1.0)
    disturbance_type: DisturbanceType
    treatment: int = Field(..., description="1 = EARLY_COORDINATED_RESPONSE, 0 = MONITOR_REASSESS")
    treatment_label: TreatmentLabel
    outcome: float = Field(..., ge=0.0, description="customer_impact_minutes_24h")

    # Oracle-only fields — None in normal mode
    potential_outcome_0: float | None = Field(None, description="Y(0) — oracle only.")
    potential_outcome_1: float | None = Field(None, description="Y(1) — oracle only.")
    propensity_true: float | None = Field(None, description="True P(A=1|severity) — oracle only.")

    @field_validator("treatment")
    @classmethod
    def treatment_is_binary(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("treatment must be 0 or 1")
        return v

    @model_validator(mode="after")
    def outcome_matches_treatment(self) -> "IncidentEpisode":
        """Consistency check: observed outcome must equal the potential outcome
        under the assigned treatment when oracle fields are present."""
        if self.treatment == 1 and self.potential_outcome_1 is not None:
            if abs(self.outcome - self.potential_outcome_1) > 1e-9:
                raise ValueError(
                    "Consistency violation: outcome != potential_outcome_1 for treated episode."
                )
        if self.treatment == 0 and self.potential_outcome_0 is not None:
            if abs(self.outcome - self.potential_outcome_0) > 1e-9:
                raise ValueError(
                    "Consistency violation: outcome != potential_outcome_0 for control episode."
                )
        return self


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class FoundationsDataset(BaseModel):
    """
    Container for a generated V0 episode collection.
    episodes: list of IncidentEpisode objects.
    provenance: reproducibility metadata.
    teaching_mode: mirrors ScenarioConfig.teaching_mode.
    """
    episodes: list[IncidentEpisode]
    provenance: Provenance
    teaching_mode: bool = False

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("episodes")
    @classmethod
    def at_least_one_episode(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError("FoundationsDataset must contain at least one episode.")
        return v

    def to_dataframe(self) -> pd.DataFrame:
        """Return episodes as a pandas DataFrame.
        Oracle columns are included only when teaching_mode is True."""
        rows = [ep.model_dump() for ep in self.episodes]
        df = pd.DataFrame(rows)
        if not self.teaching_mode:
            df = df.drop(
                columns=["potential_outcome_0", "potential_outcome_1", "propensity_true"],
                errors="ignore",
            )
        return df


# ---------------------------------------------------------------------------
# Ground truth
# ---------------------------------------------------------------------------

class GroundTruth(BaseModel):
    """
    Oracle quantities computed from the structural DGP.
    Available only in teaching/test mode. Must never be used as an
    estimator input in normal mode.
    """
    finite_sample_ate: float = Field(
        ...,
        description="Mean of (Y(1) - Y(0)) over all generated episodes.",
    )
    mean_y1: float = Field(..., description="Mean potential outcome under treatment.")
    mean_y0: float = Field(..., description="Mean potential outcome under control.")
    n_episodes: int
    provenance: Provenance


# ---------------------------------------------------------------------------
# Estimand
# ---------------------------------------------------------------------------

class Estimand(BaseModel):
    """
    Precisely defined causal quantity of interest.
    Separates what we want to know from how we estimate it.
    """
    name: str = Field("ATE", description="Short name, e.g. 'ATE'.")
    description: str = Field(
        "Average Treatment Effect: E[Y(1) - Y(0)]",
    )
    treatment_label_1: TreatmentLabel = TreatmentLabel.EARLY_COORDINATED_RESPONSE
    treatment_label_0: TreatmentLabel = TreatmentLabel.MONITOR_REASSESS
    outcome_name: str = "customer_impact_minutes_24h"
    outcome_units: str = "minutes"
    follow_up_hours: int = 24
    scale: Literal["mean_difference", "risk_difference", "risk_ratio"] = "mean_difference"
    direction_of_benefit: Literal["lower", "higher"] = "lower"
    population: str = "Eligible synthetic incident episodes at detection"
    time_zero: str = "First reliable detection timestamp"
    assumptions: list[str] = Field(
        default=[
            "Consistency: observed outcome equals potential outcome under assigned treatment.",
            "Exchangeability: Y(a) ⊥ A | severity (conditional on measured severity).",
            "Positivity: 0 < P(A=1 | severity=l) < 1 for all l in target population.",
            "No interference: one episode's treatment does not affect another's outcome.",
            "Complete follow-up: 24-hour outcome is observed for all eligible episodes.",
        ]
    )


# ---------------------------------------------------------------------------
# Diagnostic
# ---------------------------------------------------------------------------

class DiagnosticLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Diagnostic(BaseModel):
    """A single diagnostic message attached to an estimate or dataset."""
    level: DiagnosticLevel
    code: str = Field(..., description="Short machine-readable code, e.g. 'OVERLAP_WARNING'.")
    message: str
    detail: str | None = None


# ---------------------------------------------------------------------------
# Estimate result
# ---------------------------------------------------------------------------

class OracleComparison(BaseModel):
    """Teaching-mode comparison between an estimate and the known ground truth."""
    oracle_ate: float
    estimate: float
    absolute_error: float
    relative_error_pct: float | None = None
    label: str = "Oracle / simulator truth — visible in teaching mode only."


class EstimateResult(BaseModel):
    """
    Common result object returned by every V0 estimator.
    Separates estimand (what), estimator (how), and estimate (result).
    """
    estimand_name: str
    estimator_name: str
    estimate: float
    confidence_interval: tuple[float, float] | None = None
    standard_error: float | None = None
    sample_size: int
    treatment_counts: dict[str, int] = Field(
        ...,
        description="{'treated': n, 'control': n}",
    )
    assumptions: list[str] = Field(default_factory=list)
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    oracle_comparison: OracleComparison | None = Field(
        None,
        description="Populated only in teaching mode.",
    )
    provenance: Provenance

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings) or any(
            d.level in (DiagnosticLevel.WARNING, DiagnosticLevel.ERROR)
            for d in self.diagnostics
        )
