"""
causal_resilience.foundations.estimators
==========================================
V0 Slice 2 — Difference-in-means estimator.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 1 — association versus causation, crude comparison
  Chapter 2 — randomized experiment, difference in means as causal estimator
    under randomization

Causal question: ATE = E[Y(1) - Y(0)]

Estimator A — difference in means:
  mean(Y | A=1) - mean(Y | A=0)

  Causal interpretation:
  - Valid under randomization (exchangeability holds by design).
  - Associational only under confounded assignment unless exchangeability
    is justified by adjustment. This estimator does NOT adjust.

Uncertainty: nonparametric bootstrap with a fixed seed for reproducibility.
  The bootstrap interval reflects sampling variability only. It does not
  quantify unmeasured-confounding uncertainty.

Implementation type: educational — transparent numpy operations.
Ground-truth validation: tests/foundations/test_estimators.py
Textbook/software difference: bootstrap CI rather than large-sample normal
  approximation, to avoid distributional assumptions in small samples.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

import numpy as np

from causal_resilience.foundations.schemas import (
    Diagnostic,
    DiagnosticLevel,
    Estimand,
    EstimateResult,
    FoundationsDataset,
    GroundTruth,
    OracleComparison,
    Provenance,
    ScenarioConfig,
)


# ---------------------------------------------------------------------------
# Estimator config
# ---------------------------------------------------------------------------

class EstimatorConfig:
    """Configuration for a single estimator run."""

    def __init__(
        self,
        bootstrap_iterations: int = 2000,
        bootstrap_seed: int = 0,
        confidence_level: float = 0.95,
    ) -> None:
        self.bootstrap_iterations = bootstrap_iterations
        self.bootstrap_seed = bootstrap_seed
        self.confidence_level = confidence_level


# ---------------------------------------------------------------------------
# Protocol contract (matches spec section 16.2)
# ---------------------------------------------------------------------------

@runtime_checkable
class CausalEstimator(Protocol):
    name: str

    def estimate(
        self,
        dataset: FoundationsDataset,
        estimand: Estimand,
        config: EstimatorConfig,
    ) -> EstimateResult: ...


# ---------------------------------------------------------------------------
# Bootstrap helper
# ---------------------------------------------------------------------------

def _bootstrap_dim(
    y1: np.ndarray,
    y0: np.ndarray,
    n_iter: int,
    seed: int,
    alpha: float,
) -> tuple[float, float]:
    """
    Nonparametric bootstrap confidence interval for the difference in means.
    Resamples treated and control groups independently.
    """
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_iter)
    n1, n0 = len(y1), len(y0)
    for i in range(n_iter):
        s1 = rng.choice(y1, size=n1, replace=True)
        s0 = rng.choice(y0, size=n0, replace=True)
        diffs[i] = s1.mean() - s0.mean()
    lo = float(np.percentile(diffs, 100 * alpha / 2))
    hi = float(np.percentile(diffs, 100 * (1 - alpha / 2)))
    return lo, hi


# ---------------------------------------------------------------------------
# Difference-in-means estimator
# ---------------------------------------------------------------------------

class DifferenceInMeans:
    """
    Crude difference in observed outcome means by treatment group.

    mean(Y | A=1) - mean(Y | A=0)

    This estimator does not adjust for any covariate. Under randomization
    it is a valid estimator of the ATE. Under confounded assignment it
    estimates an associational contrast that may differ from the ATE.
    """

    name: str = "difference_in_means"

    def estimate(
        self,
        dataset: FoundationsDataset,
        estimand: Estimand,
        config: EstimatorConfig,
        ground_truth: GroundTruth | None = None,
    ) -> EstimateResult:
        df = dataset.to_dataframe()

        y1 = df.loc[df["treatment"] == 1, "outcome"].to_numpy()
        y0 = df.loc[df["treatment"] == 0, "outcome"].to_numpy()

        diagnostics: list[Diagnostic] = []
        warnings: list[str] = []

        if len(y1) == 0 or len(y0) == 0:
            warnings.append(
                "One treatment group is empty. Difference in means cannot be computed."
            )
            estimate = float("nan")
            ci = None
            se = None
        else:
            estimate = float(y1.mean() - y0.mean())
            ci = _bootstrap_dim(
                y1, y0,
                n_iter=config.bootstrap_iterations,
                seed=config.bootstrap_seed,
                alpha=1.0 - config.confidence_level,
            )
            se = float(
                np.sqrt(y1.var(ddof=1) / len(y1) + y0.var(ddof=1) / len(y0))
            )

        # Small-sample warning
        min_group = min(len(y1), len(y0))
        if min_group < 30:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.WARNING,
                code="SMALL_SAMPLE",
                message=f"Smallest treatment group has {min_group} episodes. "
                        "Bootstrap intervals may be unstable.",
            ))

        oracle_comparison = None
        if ground_truth is not None:
            abs_err = abs(estimate - ground_truth.finite_sample_ate)
            rel_err = (
                abs_err / abs(ground_truth.finite_sample_ate) * 100
                if ground_truth.finite_sample_ate != 0 else None
            )
            oracle_comparison = OracleComparison(
                oracle_ate=ground_truth.finite_sample_ate,
                estimate=estimate,
                absolute_error=abs_err,
                relative_error_pct=rel_err,
            )

        provenance = Provenance(
            seed=dataset.provenance.seed,
            scenario_id=dataset.provenance.scenario_id,
            generator_version=dataset.provenance.generator_version,
            schema_version=dataset.provenance.schema_version,
            created_at=datetime.now(timezone.utc),
            oracle_used=ground_truth is not None,
            config_hash=dataset.provenance.config_hash,
        )

        return EstimateResult(
            estimand_name=estimand.name,
            estimator_name=self.name,
            estimate=estimate,
            confidence_interval=ci,
            standard_error=se,
            sample_size=len(df),
            treatment_counts={"treated": int(len(y1)), "control": int(len(y0))},
            assumptions=estimand.assumptions,
            diagnostics=diagnostics,
            warnings=warnings,
            oracle_comparison=oracle_comparison,
            provenance=provenance,
        )


# ---------------------------------------------------------------------------
# Module-level convenience instance
# ---------------------------------------------------------------------------

difference_in_means = DifferenceInMeans()
