"""
causal_resilience.foundations.dgp
===================================
V0 Slice 2 — Structural data-generating process.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 1 — potential outcomes, individual and average causal effects
  Chapter 2 — randomization, standardization
  Chapter 3 — identifiability conditions, positivity, consistency

Causal question:
  Among eligible synthetic telecom incidents at detection, what is the
  average effect of EARLY_COORDINATED_RESPONSE versus MONITOR_REASSESS
  on customer_impact_minutes_24h over 24 hours?

Estimand: ATE = E[Y(1) - Y(0)] on the mean-difference scale.

Structural relationships (baseline DAG):
  severity ──> treatment
  severity ──> outcome
  treatment ──> outcome

Generation order (mandatory):
  1. severity drawn from Uniform(0, 1)
  2. potential outcomes Y(0) and Y(1) generated from severity
  3. treatment assigned according to the selected mode
  4. observed outcome selected by consistency: Y = Y(A)

The oracle (GroundTruth) is computed from the generated potential outcomes.
It is never used as an estimator input in normal mode.

Implementation type: educational — transparent numpy operations, no library
  estimator called here.
Ground-truth validation: tests/foundations/test_dgp.py
Textbook/software difference: none — the structural equations follow the
  recommended form in the spec (section 8.3) exactly.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

import numpy as np

from causal_resilience.foundations.schemas import (
    AssignmentMode,
    DisturbanceType,
    FoundationsDataset,
    GroundTruth,
    IncidentEpisode,
    Provenance,
    ScenarioConfig,
    TreatmentLabel,
)

# Disturbance types available in V0 — abstract labels only, no causal role
_DISTURBANCE_TYPES = list(DisturbanceType)


# ---------------------------------------------------------------------------
# Protocol contract (matches spec section 16.2)
# ---------------------------------------------------------------------------

@runtime_checkable
class FoundationsScenario(Protocol):
    def generate(self, config: ScenarioConfig) -> FoundationsDataset: ...
    def truth(self, dataset: FoundationsDataset) -> GroundTruth: ...


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _config_hash(config: ScenarioConfig) -> str:
    """Stable hash of the scenario configuration for provenance."""
    payload = config.model_dump(mode="json")
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def _make_provenance(config: ScenarioConfig, oracle_used: bool = False) -> Provenance:
    return Provenance(
        seed=config.seed,
        scenario_id=config.scenario_id,
        generator_version=config.generator_version,
        schema_version=config.schema_version,
        created_at=datetime.now(timezone.utc),
        oracle_used=oracle_used,
        config_hash=_config_hash(config),
    )


def _assign_randomized(rng: np.random.Generator, n: int) -> np.ndarray:
    """P(A=1 | severity) = 0.5 — pure randomization."""
    return rng.binomial(1, 0.5, size=n).astype(float)


def _assign_confounded(
    rng: np.random.Generator,
    severity: np.ndarray,
    strength: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    P(A=1 | severity) = logistic(intercept + strength * (severity - 0.5))

    The intercept is chosen so that the marginal treatment probability is
    approximately 0.5, keeping both groups reasonably sized for teaching.
    Higher severity → higher probability of EARLY_COORDINATED_RESPONSE.
    Returns (treatment array, true propensity array).
    """
    log_odds = strength * (severity - 0.5)
    propensity = 1.0 / (1.0 + np.exp(-log_odds))
    treatment = rng.binomial(1, propensity).astype(float)
    return treatment, propensity


def _assign_limited_overlap(
    rng: np.random.Generator,
    severity: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Push treatment probabilities toward 0 or 1 at the extremes of severity.
    Low severity (< 0.2): P(A=1) ≈ 0.05
    High severity (> 0.8): P(A=1) ≈ 0.95
    Middle range: P(A=1) ≈ 0.5

    This creates a positivity problem at the tails — the teaching point.
    """
    propensity = np.where(
        severity < 0.2, 0.05,
        np.where(severity > 0.8, 0.95, 0.5),
    )
    treatment = rng.binomial(1, propensity).astype(float)
    return treatment, propensity


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

class TelecomFoundationsDGP:
    """
    Structural data-generating process for V0.

    Generation order enforces the causal structure:
      severity → potential outcomes → treatment → observed outcome

    The oracle (potential outcomes and true propensity) is always generated
    internally. It is exposed in the dataset only when teaching_mode=True.
    """

    def generate(self, config: ScenarioConfig) -> FoundationsDataset:
        rng = np.random.default_rng(config.seed)
        n = config.n_episodes

        # ------------------------------------------------------------------
        # Step 1: baseline severity — drawn before treatment
        # ------------------------------------------------------------------
        severity = rng.uniform(0.0, 1.0, size=n)

        # ------------------------------------------------------------------
        # Step 2: disturbance types — descriptive context only
        # ------------------------------------------------------------------
        disturbance_indices = rng.integers(0, len(_DISTURBANCE_TYPES), size=n)

        # ------------------------------------------------------------------
        # Step 3: potential outcomes — generated before treatment assignment
        #
        # baseline_impact = 100 + 240 * severity + noise_0
        # Y(0) = max(0, baseline_impact)
        # Y(1) = max(0, baseline_impact + treatment_effect + noise_delta)
        #
        # treatment_effect is negative (beneficial) by default.
        # noise_0 and noise_delta are independent draws.
        # ------------------------------------------------------------------
        noise_0 = rng.normal(0.0, config.outcome_noise_sd, size=n)
        noise_delta = rng.normal(0.0, config.outcome_noise_sd, size=n)

        baseline_impact = 100.0 + 240.0 * severity + noise_0
        po0 = np.maximum(0.0, baseline_impact)
        po1 = np.maximum(0.0, baseline_impact + config.treatment_effect + noise_delta)

        # ------------------------------------------------------------------
        # Step 4: treatment assignment
        # ------------------------------------------------------------------
        if config.assignment_mode == AssignmentMode.RANDOMIZED:
            treatment = _assign_randomized(rng, n)
            propensity_true = np.full(n, 0.5)

        elif config.assignment_mode == AssignmentMode.CONFOUNDED:
            treatment, propensity_true = _assign_confounded(
                rng, severity, config.confounding_strength
            )

        else:  # LIMITED_OVERLAP
            treatment, propensity_true = _assign_limited_overlap(rng, severity)

        # ------------------------------------------------------------------
        # Step 5: observed outcome — consistency rule Y = Y(A)
        # ------------------------------------------------------------------
        observed_outcome = np.where(treatment == 1, po1, po0)

        # ------------------------------------------------------------------
        # Step 6: assemble episodes
        # ------------------------------------------------------------------
        provenance = _make_provenance(config, oracle_used=False)
        episodes = []

        for i in range(n):
            t = int(treatment[i])
            label = (
                TreatmentLabel.EARLY_COORDINATED_RESPONSE if t == 1
                else TreatmentLabel.MONITOR_REASSESS
            )
            episodes.append(
                IncidentEpisode(
                    episode_id=f"{config.scenario_id}-{i:06d}",
                    severity=float(severity[i]),
                    disturbance_type=_DISTURBANCE_TYPES[int(disturbance_indices[i])],
                    treatment=t,
                    treatment_label=label,
                    outcome=float(observed_outcome[i]),
                    potential_outcome_0=float(po0[i]) if config.teaching_mode else None,
                    potential_outcome_1=float(po1[i]) if config.teaching_mode else None,
                    propensity_true=float(propensity_true[i]) if config.teaching_mode else None,
                )
            )

        return FoundationsDataset(
            episodes=episodes,
            provenance=provenance,
            teaching_mode=config.teaching_mode,
        )

    def truth(self, dataset: FoundationsDataset) -> GroundTruth:
        """
        Compute the finite-sample oracle ATE from generated potential outcomes.
        Requires teaching_mode=True (oracle fields must be present).
        Raises ValueError if oracle fields are missing.
        """
        po0_vals, po1_vals = [], []
        for ep in dataset.episodes:
            if ep.potential_outcome_0 is None or ep.potential_outcome_1 is None:
                raise ValueError(
                    "truth() requires teaching_mode=True so that oracle fields "
                    "are present. Do not call truth() in normal mode."
                )
            po0_vals.append(ep.potential_outcome_0)
            po1_vals.append(ep.potential_outcome_1)

        po0_arr = np.array(po0_vals)
        po1_arr = np.array(po1_vals)
        ate = float(np.mean(po1_arr - po0_arr))

        provenance = Provenance(
            seed=dataset.provenance.seed,
            scenario_id=dataset.provenance.scenario_id,
            generator_version=dataset.provenance.generator_version,
            schema_version=dataset.provenance.schema_version,
            created_at=datetime.now(timezone.utc),
            oracle_used=True,
            config_hash=dataset.provenance.config_hash,
        )

        return GroundTruth(
            finite_sample_ate=ate,
            mean_y1=float(np.mean(po1_arr)),
            mean_y0=float(np.mean(po0_arr)),
            n_episodes=len(dataset.episodes),
            provenance=provenance,
        )


# ---------------------------------------------------------------------------
# Module-level convenience instance
# ---------------------------------------------------------------------------

dgp = TelecomFoundationsDGP()
