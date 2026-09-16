# Lesson 5 — Adjustment: standardization and IPW

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.3–2.4)

## Learning objective

Apply outcome regression (standardization) and inverse-probability weighting
to recover the ATE under confounded assignment, and explain what each method
requires to be valid.

## The problem

Under confounded assignment, the crude difference in means is biased because
severity is a common cause of treatment and outcome. To estimate the ATE we
must block the backdoor path `treatment ← severity → outcome`.

## Standardization (g-formula)

1. Fit an outcome model: `E[Y | A, severity]` using OLS.
2. For every episode, predict `Y_hat(1)` (set A=1) and `Y_hat(0)` (set A=0).
3. `ATE = mean(Y_hat(1) - Y_hat(0))`.

This averages predictions over the observed severity distribution, removing
the confounding by severity.

**Requires:** correct outcome-model specification.

## Inverse-probability weighting (IPW)

1. Fit a propensity model: `P(A=1 | severity)` using logistic regression.
2. Weight each episode by `1 / P(A=a_i | severity_i)`.
3. `ATE = weighted_mean(Y | A=1) - weighted_mean(Y | A=0)`.

IPW creates a pseudo-population where severity is balanced across treatment
groups, removing the backdoor path.

**Requires:** correct propensity-model specification and positivity.

## Shared identification requirements

- Conditional exchangeability: `Y(a) ⊥ A | severity`
- Positivity: `0 < P(A=1 | severity=l) < 1` for all `l` in the target population
- Consistency: observed outcome equals potential outcome under assigned treatment

## Reflection

- If the outcome model is misspecified, will standardization still recover the ATE?
- What happens to IPW estimates when some propensity scores are very close to 0 or 1?
