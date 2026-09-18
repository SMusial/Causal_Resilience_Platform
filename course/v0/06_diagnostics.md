# Lesson 6 — Diagnostics, uncertainty, and responsible interpretation

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.4) and Chapter 3 (§3.1)

## Learning objective

Interpret propensity overlap, IPW weight distributions, effective sample size,
and assumption warnings to decide whether a causal estimate is supported,
fragile, or not interpretable.

## Causal question

Among eligible synthetic telecom incidents at detection, what is the average
effect of assigning **EARLY_COORDINATED_RESPONSE** rather than
**MONITOR_REASSESS** on `customer_impact_minutes_24h` during the following
24 hours?

## Treatment and comparator

- **Intervention:** `EARLY_COORDINATED_RESPONSE`
- **Comparator:** `MONITOR_REASSESS`
- **Outcome:** `customer_impact_minutes_24h` (lower is better)
- **Follow-up:** 24 hours from detection

## Estimand

```
ATE = E[Y(1) - Y(0)]   on the mean-difference scale
```

## Estimators compared

| Estimator | Adjustment | Valid under |
|---|---|---|
| Crude DiM | None | Randomization only |
| Standardization | Outcome model (OLS) | Correct model + exchangeability + positivity |
| IPW | Propensity model (logistic) | Correct model + exchangeability + positivity |

## Diagnostic 1 — Overlap (positivity check)

Propensity scores for treated and control episodes must span a common range.
If one group has propensities near 0 or 1, the positivity assumption is
violated and IPW weights become extreme.

**Warning threshold:** propensity within 0.05 of 0 or 1.

## Diagnostic 2 — Weight distribution and effective sample size

Extreme IPW weights (e.g., > 10) inflate variance and signal positivity
problems. The Kish effective sample size (ESS) measures how much information
the weighted sample retains:

```
ESS = (sum w)^2 / sum(w^2)
```

A low ESS relative to the nominal sample size means the estimate is driven
by a small number of episodes.

## Diagnostic 3 — Covariate balance

The standardized mean difference (SMD) for severity should be small after
weighting. SMD < 0.1 is a common threshold for adequate balance.

```
SMD = |mean_treated - mean_control| / pooled_sd
```

Large post-weighting SMD indicates the propensity model did not adequately
balance the groups.

## Identification assumptions

1. Consistency: observed outcome equals potential outcome under assigned treatment.
2. Exchangeability: Y(a) ⊥ A | severity (conditional on measured severity).
3. Positivity: 0 < P(A=1 | severity=l) < 1 for all l.
4. No interference: one episode's treatment does not affect another's outcome.
5. Complete follow-up: 24-hour outcome is observed for all eligible episodes.

## Uncertainty

> **The 95% bootstrap CI reflects sampling variability only.**
> It does not quantify uncertainty from unmeasured confounding.
> A narrow CI under strong unmeasured confounding is false precision.

## Limitation

Diagnostics can detect some problems (poor overlap, extreme weights, residual
imbalance) but cannot detect unmeasured confounding. Passing all three
diagnostic checks is necessary but not sufficient for a valid causal
interpretation.

> All data are entirely synthetic and illustrative. Results do not represent
> real telecom operations, real organizations, or real interventions.

## Reflection

- Can a statistically significant IPW result be interpreted causally when
  the ESS is 5% of the nominal sample size?
- What would you do if the SMD after weighting is still 0.3?
