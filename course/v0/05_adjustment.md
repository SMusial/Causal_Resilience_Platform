# Lesson 5 — Adjustment: standardization and IPW

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.3–2.4)

## Learning objective

Apply outcome regression (standardization) and inverse-probability weighting
to recover the ATE under confounded assignment, and explain what each method
requires to be valid.

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

## Estimators

### Crude difference in means (biased under confounding)

```
ATE_hat = mean(Y | A=1) - mean(Y | A=0)
```

### Standardization (g-formula)

1. Fit an outcome model: `E[Y | A, severity]` using OLS.
2. For every episode, predict `Y_hat(1)` (set A=1) and `Y_hat(0)` (set A=0).
3. `ATE = mean(Y_hat(1) - Y_hat(0))`.

This averages predictions over the observed severity distribution, removing
the confounding by severity.

**Requires:** correct outcome-model specification.

### Inverse-probability weighting (IPW)

1. Fit a propensity model: `P(A=1 | severity)` using logistic regression.
2. Weight each episode by `1 / P(A=a_i | severity_i)`.
3. `ATE = weighted_mean(Y | A=1) - weighted_mean(Y | A=0)`.

IPW creates a pseudo-population where severity is balanced across treatment
groups, removing the backdoor path.

**Requires:** correct propensity-model specification and positivity.

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

Both estimators assume the adjustment model is correctly specified.
Standardization is biased if the outcome model is misspecified.
IPW is biased if the propensity model is misspecified.
Neither method can adjust for unmeasured confounders.

> All data are entirely synthetic and illustrative. Results do not represent
> real telecom operations, real organizations, or real interventions.

## Reflection

- If the outcome model is misspecified, will standardization still recover the ATE?
- What happens to IPW estimates when some propensity scores are very close to 0 or 1?
