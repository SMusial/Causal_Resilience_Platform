"""
causal_resilience.foundations.estimators
==========================================
V0 Slice 2/5 — Difference-in-means, Standardization, and IPW estimators.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 1 — association versus causation, crude comparison
  Chapter 2 — randomized experiment, standardization, IPW
  Chapter 3 — identifiability conditions, positivity

Causal question: ATE = E[Y(1) - Y(0)]

Estimator A — difference in means (Slice 2):
  mean(Y | A=1) - mean(Y | A=0)
  Causal under randomization; biased under confounding without adjustment.

Estimator B — standardization / outcome regression (Slice 5):
  Fit E[Y | A, severity] with OLS. Predict Y(1) and Y(0) for every episode.
  ATE = mean(Y_hat(1) - Y_hat(0)).
  Requires correct outcome-model specification.

Estimator C — inverse-probability weighting (Slice 5):
  Fit P(A=1 | severity) with logistic regression.
  Weight each episode by 1/P(A=a_i | severity_i).
  ATE = weighted_mean(Y | A=1) - weighted_mean(Y | A=0).
  Requires correct propensity-model specification and positivity.

Uncertainty: nonparametric bootstrap with a fixed seed for reproducibility.
  The bootstrap interval reflects sampling variability only. It does not
  quantify unmeasured-confounding uncertainty.

Implementation type: educational — transparent numpy/sklearn operations.
Ground-truth validation: tests/foundations/test_estimators.py
Textbook/software difference: bootstrap CI rather than large-sample normal
  approximation, to avoid distributional assumptions in small samples.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Protocol, runtime_checkable

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression

from causal_resilience.foundations.diagnostics import (
    compute_balance,
    compute_overlap,
    compute_weight_diagnostic,
)
from causal_resilience.foundations.schemas import (
    Diagnostic,
    DiagnosticLevel,
    Estimand,
    EstimateResult,
    FoundationsDataset,
    GroundTruth,
    OracleComparison,
    Provenance,
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
# Shared helpers
# ---------------------------------------------------------------------------

def _make_oracle_comparison(
    estimate: float, ground_truth: GroundTruth | None
) -> OracleComparison | None:
    if ground_truth is None:
        return None
    abs_err = abs(estimate - ground_truth.finite_sample_ate)
    rel_err = (
        abs_err / abs(ground_truth.finite_sample_ate) * 100
        if ground_truth.finite_sample_ate != 0 else None
    )
    return OracleComparison(
        oracle_ate=ground_truth.finite_sample_ate,
        estimate=estimate,
        absolute_error=abs_err,
        relative_error_pct=rel_err,
    )


def _make_provenance(
    dataset: FoundationsDataset, ground_truth: GroundTruth | None
) -> Provenance:
    return Provenance(
        seed=dataset.provenance.seed,
        scenario_id=dataset.provenance.scenario_id,
        generator_version=dataset.provenance.generator_version,
        schema_version=dataset.provenance.schema_version,
        created_at=datetime.now(timezone.utc),
        oracle_used=ground_truth is not None,
        config_hash=dataset.provenance.config_hash,
    )


# ---------------------------------------------------------------------------
# Bootstrap helpers
# ---------------------------------------------------------------------------

def _bootstrap_dim(
    y1: np.ndarray,
    y0: np.ndarray,
    n_iter: int,
    seed: int,
    alpha: float,
) -> tuple[float, float]:
    """
    Nonparametric bootstrap CI for the difference in means.
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


def _bootstrap_rows(
    fn: Callable[[pd.DataFrame], float],
    df: pd.DataFrame,
    n_iter: int,
    seed: int,
    alpha: float,
) -> tuple[float, float]:
    """
    Nonparametric bootstrap CI for any row-level estimator.
    Resamples rows with replacement.
    """
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_iter)
    n = len(df)
    for i in range(n_iter):
        idx = rng.integers(0, n, size=n)
        diffs[i] = fn(df.iloc[idx].reset_index(drop=True))
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

        min_group = min(len(y1), len(y0))
        if min_group < 30:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.WARNING,
                code="SMALL_SAMPLE",
                message=f"Smallest treatment group has {min_group} episodes. "
                        "Bootstrap intervals may be unstable.",
            ))

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
            oracle_comparison=_make_oracle_comparison(estimate, ground_truth),
            provenance=_make_provenance(dataset, ground_truth),
        )


# ---------------------------------------------------------------------------
# Standardization (outcome regression / g-formula)
# ---------------------------------------------------------------------------

class Standardization:
    """
    Outcome regression and standardization (g-formula).

    Fits E[Y | A, severity] with OLS, then predicts each episode's outcome
    under A=1 and A=0 and averages over the target population.

    ATE = mean(Y_hat(1) - Y_hat(0))

    Requires: correct outcome-model specification (linear in severity and A).
    Source: Hernán & Robins, What If, Chapter 2 (standardization, §2.3).
    """

    name: str = "standardization"

    def estimate(
        self,
        dataset: FoundationsDataset,
        estimand: Estimand,
        config: EstimatorConfig,
        ground_truth: GroundTruth | None = None,
    ) -> EstimateResult:
        df = dataset.to_dataframe()
        warnings: list[str] = []

        def _point(d: pd.DataFrame) -> float:
            sev = d["severity"].to_numpy()
            trt = d["treatment"].to_numpy()
            out = d["outcome"].to_numpy()
            X = np.column_stack([trt, sev])
            m = LinearRegression().fit(X, out)
            X1 = np.column_stack([np.ones(len(d)), sev])
            X0 = np.column_stack([np.zeros(len(d)), sev])
            return float((m.predict(X1) - m.predict(X0)).mean())

        estimate = _point(df)
        ci = _bootstrap_rows(
            _point, df,
            n_iter=config.bootstrap_iterations,
            seed=config.bootstrap_seed,
            alpha=1.0 - config.confidence_level,
        )
        se = float((ci[1] - ci[0]) / (2 * 1.96))

        warnings.append(
            "Standardization assumes the outcome model is correctly specified. "
            "Model misspecification can bias the ATE estimate."
        )

        return EstimateResult(
            estimand_name=estimand.name,
            estimator_name=self.name,
            estimate=estimate,
            confidence_interval=ci,
            standard_error=se,
            sample_size=len(df),
            treatment_counts={
                "treated": int((df["treatment"] == 1).sum()),
                "control": int((df["treatment"] == 0).sum()),
            },
            assumptions=estimand.assumptions,
            diagnostics=[],
            warnings=warnings,
            oracle_comparison=_make_oracle_comparison(estimate, ground_truth),
            provenance=_make_provenance(dataset, ground_truth),
        )


# ---------------------------------------------------------------------------
# Inverse-probability weighting
# ---------------------------------------------------------------------------

class IPW:
    """
    Inverse-probability weighting estimator.

    Fits P(A=1 | severity) with logistic regression, assigns each episode
    weight 1/P(A=a_i | severity_i), and computes the weighted outcome contrast.

    ATE = weighted_mean(Y | A=1) - weighted_mean(Y | A=0)

    Requires: correct propensity-model specification and positivity.
    Source: Hernán & Robins, What If, Chapter 2 (IPW, §2.4).
    """

    name: str = "ipw"

    def estimate(
        self,
        dataset: FoundationsDataset,
        estimand: Estimand,
        config: EstimatorConfig,
        ground_truth: GroundTruth | None = None,
        extreme_weight_threshold: float = 10.0,
    ) -> EstimateResult:
        df = dataset.to_dataframe()
        diagnostics: list[Diagnostic] = []
        warnings: list[str] = []

        severity = df["severity"].to_numpy().reshape(-1, 1)
        treatment = df["treatment"].to_numpy()
        outcome = df["outcome"].to_numpy()

        propensity, weights = self._fit(severity, treatment)

        overlap = compute_overlap(propensity, treatment)
        if overlap.warning_message:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.WARNING,
                code="OVERLAP_WARNING",
                message=overlap.warning_message,
            ))

        wd = compute_weight_diagnostic(weights, extreme_threshold=extreme_weight_threshold)
        if wd.warning_message:
            diagnostics.append(Diagnostic(
                level=DiagnosticLevel.WARNING,
                code="EXTREME_WEIGHTS",
                message=wd.warning_message,
            ))

        w_t = weights[treatment == 1]
        w_c = weights[treatment == 0]
        y_t = outcome[treatment == 1]
        y_c = outcome[treatment == 0]

        if w_t.sum() == 0 or w_c.sum() == 0:
            warnings.append("One treatment group has zero total weight.")
            estimate = float("nan")
            ci = None
            se = None
        else:
            estimate = float(
                np.average(y_t, weights=w_t) - np.average(y_c, weights=w_c)
            )

            def _point(d: pd.DataFrame) -> float:
                sev = d["severity"].to_numpy().reshape(-1, 1)
                trt = d["treatment"].to_numpy()
                out = d["outcome"].to_numpy()
                ps, w = self._fit(sev, trt)
                wt = w[trt == 1]; wc = w[trt == 0]
                yt = out[trt == 1]; yc = out[trt == 0]
                if wt.sum() == 0 or wc.sum() == 0:
                    return float("nan")
                return float(np.average(yt, weights=wt) - np.average(yc, weights=wc))

            ci = _bootstrap_rows(
                _point, df,
                n_iter=config.bootstrap_iterations,
                seed=config.bootstrap_seed,
                alpha=1.0 - config.confidence_level,
            )
            se = float((ci[1] - ci[0]) / (2 * 1.96))

        warnings.append(
            "IPW assumes the propensity model is correctly specified. "
            "Model misspecification can bias the ATE estimate."
        )

        return EstimateResult(
            estimand_name=estimand.name,
            estimator_name=self.name,
            estimate=estimate,
            confidence_interval=ci,
            standard_error=se,
            sample_size=len(df),
            treatment_counts={
                "treated": int((treatment == 1).sum()),
                "control": int((treatment == 0).sum()),
            },
            assumptions=estimand.assumptions,
            diagnostics=diagnostics,
            warnings=warnings,
            oracle_comparison=_make_oracle_comparison(estimate, ground_truth),
            provenance=_make_provenance(dataset, ground_truth),
        )

    def get_propensity_and_weights(
        self, dataset: FoundationsDataset
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return (propensity, ipw_weights) for diagnostic visualizations."""
        df = dataset.to_dataframe()
        severity = df["severity"].to_numpy().reshape(-1, 1)
        treatment = df["treatment"].to_numpy()
        return self._fit(severity, treatment)

    @staticmethod
    def _fit(
        severity: np.ndarray, treatment: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        ps = LogisticRegression(max_iter=1000).fit(severity, treatment).predict_proba(severity)[:, 1]
        w = np.where(treatment == 1, 1.0 / ps, 1.0 / (1.0 - ps))
        return ps, w


# ---------------------------------------------------------------------------
# Module-level convenience instances
# ---------------------------------------------------------------------------

difference_in_means = DifferenceInMeans()
standardization = Standardization()
ipw = IPW()
