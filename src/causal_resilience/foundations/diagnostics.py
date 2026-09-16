"""
causal_resilience.foundations.diagnostics
==========================================
V0 Slice 5 — Overlap, weight, and balance diagnostics.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 2 — positivity, standardization, inverse-probability weighting
  Chapter 3 — identifiability conditions, positivity

Causal question: ATE = E[Y(1) - Y(0)]
Estimand: population average treatment effect on the mean-difference scale.
Assumptions checked here: positivity (overlap), no extreme weights.
Implementation type: educational — transparent numpy/pandas operations.
Ground-truth validation: tests/foundations/test_diagnostics.py
Textbook/software difference: none.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class OverlapDiagnostic:
    """Propensity-score overlap summary."""
    min_propensity_treated: float
    max_propensity_treated: float
    min_propensity_control: float
    max_propensity_control: float
    # Fraction of treated episodes with propensity outside (trim_lo, trim_hi)
    pct_near_boundary_treated: float
    pct_near_boundary_control: float
    overlap_adequate: bool          # True when both groups span a common range
    warning_message: str | None


@dataclass
class WeightDiagnostic:
    """IPW weight distribution summary."""
    min_weight: float
    max_weight: float
    mean_weight: float
    pct_extreme: float              # fraction with weight > extreme_threshold
    effective_sample_size: float    # Kish ESS = (sum w)^2 / sum(w^2)
    extreme_threshold: float
    has_extreme_weights: bool
    warning_message: str | None


@dataclass
class BalanceDiagnostic:
    """Standardized mean difference for severity before/after weighting."""
    smd_unweighted: float           # |mean_treated - mean_control| / pooled_sd
    smd_weighted: float | None      # SMD after IPW weighting; None if no weights
    balance_adequate_unweighted: bool   # SMD < 0.1 threshold
    balance_adequate_weighted: bool | None


# ---------------------------------------------------------------------------
# Overlap diagnostic
# ---------------------------------------------------------------------------

def compute_overlap(
    propensity: np.ndarray,
    treatment: np.ndarray,
    boundary: float = 0.05,
) -> OverlapDiagnostic:
    """
    Assess propensity-score overlap between treatment groups.

    boundary: propensity values within `boundary` of 0 or 1 are flagged
    as near-boundary (practical positivity violation).
    """
    p_treated = propensity[treatment == 1]
    p_control = propensity[treatment == 0]

    if len(p_treated) == 0 or len(p_control) == 0:
        return OverlapDiagnostic(
            min_propensity_treated=float("nan"),
            max_propensity_treated=float("nan"),
            min_propensity_control=float("nan"),
            max_propensity_control=float("nan"),
            pct_near_boundary_treated=float("nan"),
            pct_near_boundary_control=float("nan"),
            overlap_adequate=False,
            warning_message="One treatment group is empty — overlap cannot be assessed.",
        )

    def _pct_near(p: np.ndarray) -> float:
        return float(np.mean((p < boundary) | (p > 1 - boundary)))

    min_t, max_t = float(p_treated.min()), float(p_treated.max())
    min_c, max_c = float(p_control.min()), float(p_control.max())

    # Common support: the intersection of the two ranges
    common_lo = max(min_t, min_c)
    common_hi = min(max_t, max_c)
    overlap_adequate = common_lo < common_hi

    pct_nb_t = _pct_near(p_treated)
    pct_nb_c = _pct_near(p_control)

    warning = None
    if not overlap_adequate:
        warning = (
            "Propensity ranges do not overlap. IPW estimates are not supported "
            "for this scenario. Positivity assumption is violated."
        )
    elif pct_nb_t > 0.05 or pct_nb_c > 0.05:
        warning = (
            f"{pct_nb_t * 100:.1f}% of treated and "
            f"{pct_nb_c * 100:.1f}% of control episodes have propensity "
            f"within {boundary} of 0 or 1. Practical positivity may be weak."
        )

    return OverlapDiagnostic(
        min_propensity_treated=min_t,
        max_propensity_treated=max_t,
        min_propensity_control=min_c,
        max_propensity_control=max_c,
        pct_near_boundary_treated=pct_nb_t,
        pct_near_boundary_control=pct_nb_c,
        overlap_adequate=overlap_adequate,
        warning_message=warning,
    )


# ---------------------------------------------------------------------------
# Weight diagnostic
# ---------------------------------------------------------------------------

def compute_weight_diagnostic(
    weights: np.ndarray,
    extreme_threshold: float = 10.0,
) -> WeightDiagnostic:
    """
    Summarise IPW weight distribution and compute Kish effective sample size.

    ESS = (sum w)^2 / sum(w^2)

    extreme_threshold: weights above this value are flagged as extreme.
    """
    w = np.asarray(weights, dtype=float)
    if len(w) == 0:
        return WeightDiagnostic(
            min_weight=float("nan"), max_weight=float("nan"),
            mean_weight=float("nan"), pct_extreme=float("nan"),
            effective_sample_size=float("nan"),
            extreme_threshold=extreme_threshold,
            has_extreme_weights=False,
            warning_message="No weights provided.",
        )

    ess = float(w.sum() ** 2 / (w ** 2).sum())
    pct_extreme = float(np.mean(w > extreme_threshold))
    has_extreme = pct_extreme > 0.0

    warning = None
    if has_extreme:
        warning = (
            f"{pct_extreme * 100:.1f}% of IPW weights exceed {extreme_threshold:.0f}. "
            "Extreme weights inflate variance and may indicate positivity violations. "
            "Consider weight trimming or a different estimator."
        )

    return WeightDiagnostic(
        min_weight=float(w.min()),
        max_weight=float(w.max()),
        mean_weight=float(w.mean()),
        pct_extreme=pct_extreme,
        effective_sample_size=ess,
        extreme_threshold=extreme_threshold,
        has_extreme_weights=has_extreme,
        warning_message=warning,
    )


# ---------------------------------------------------------------------------
# Balance diagnostic
# ---------------------------------------------------------------------------

def compute_balance(
    severity: np.ndarray,
    treatment: np.ndarray,
    weights: np.ndarray | None = None,
) -> BalanceDiagnostic:
    """
    Standardized mean difference (SMD) for severity before and after weighting.

    SMD = |mean_treated - mean_control| / pooled_sd

    SMD < 0.1 is the conventional threshold for adequate balance.
    """
    sev_t = severity[treatment == 1]
    sev_c = severity[treatment == 0]

    if len(sev_t) == 0 or len(sev_c) == 0:
        return BalanceDiagnostic(
            smd_unweighted=float("nan"),
            smd_weighted=None,
            balance_adequate_unweighted=False,
            balance_adequate_weighted=None,
        )

    pooled_sd = float(np.sqrt(
        (sev_t.var(ddof=1) + sev_c.var(ddof=1)) / 2
    ))
    if pooled_sd == 0:
        pooled_sd = 1.0  # avoid division by zero in degenerate cases

    smd_u = float(abs(sev_t.mean() - sev_c.mean()) / pooled_sd)

    smd_w = None
    balance_w = None
    if weights is not None:
        w_t = weights[treatment == 1]
        w_c = weights[treatment == 0]
        if w_t.sum() > 0 and w_c.sum() > 0:
            mean_t_w = float(np.average(sev_t, weights=w_t))
            mean_c_w = float(np.average(sev_c, weights=w_c))
            smd_w = float(abs(mean_t_w - mean_c_w) / pooled_sd)
            balance_w = smd_w < 0.1

    return BalanceDiagnostic(
        smd_unweighted=smd_u,
        smd_weighted=smd_w,
        balance_adequate_unweighted=smd_u < 0.1,
        balance_adequate_weighted=balance_w,
    )
