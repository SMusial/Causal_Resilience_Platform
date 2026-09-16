# Lesson 6 — Diagnostics, uncertainty, and responsible interpretation

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.4) and Chapter 3 (§3.1)

## Learning objective

Interpret propensity overlap, IPW weight distributions, effective sample size,
and assumption warnings to decide whether a causal estimate is supported,
fragile, or not interpretable.

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

## Uncertainty

The bootstrap CI reflects sampling variability only. It does not capture
unmeasured-confounding uncertainty. A narrow CI under strong unmeasured
confounding is false precision.

## Reflection

- Can a statistically significant IPW result be interpreted causally when
  the ESS is 5% of the nominal sample size?
- What would you do if the SMD after weighting is still 0.3?
