# Lesson 3 — Randomization: when association can identify causation

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.1–2.2)

## Learning objective

Explain why randomization supports exchangeability and why a difference in
observed means estimates the ATE under randomized assignment.

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

## Estimator

**Difference in means:**

```
ATE_hat = mean(Y | A=1) - mean(Y | A=0)
```

Valid under randomization. Biased under confounded assignment without adjustment.

## Why randomization works

Under randomized assignment, treatment is allocated independently of severity
and all other baseline characteristics:

```
Y(a) ⊥ A   (unconditional exchangeability)
```

This means the observed group means identify the potential-outcome means:

```
E[Y | A=1] = E[Y(1)]
E[Y | A=0] = E[Y(0)]
ATE = E[Y | A=1] − E[Y | A=0]
```

The crude difference in means is a valid causal estimator — not because the
groups are identical, but because treatment assignment is unrelated to the
potential outcomes.

## Identification assumptions

1. Consistency: observed outcome equals potential outcome under assigned treatment.
2. Exchangeability: Y(a) ⊥ A (unconditional under randomization).
3. Positivity: 0 < P(A=1) < 1.
4. No interference: one episode's treatment does not affect another's outcome.
5. Complete follow-up: 24-hour outcome is observed for all eligible episodes.

## Finite-sample variability and uncertainty

The estimate will not equal the oracle ATE exactly in any finite sample.
The error shrinks as sample size grows.

> **The 95% bootstrap CI reflects sampling variability only.**
> It does not quantify uncertainty from unmeasured confounding.
> A narrow CI under strong unmeasured confounding is false precision.

## Limitation

Randomization is a design property — it cannot be assumed from observational
data. The bootstrap CI captures sampling variability but not the uncertainty
introduced by unmeasured confounders in non-randomized settings.

> All data are entirely synthetic and illustrative. Results do not represent
> real telecom operations, real organizations, or real interventions.

## Reflection

- Why does balance on severity not need to be perfect for randomization to
  support a causal interpretation?
- What happens to the estimate as you increase the sample size?
- Would the estimate still be valid if the randomization were 70/30 instead
  of 50/50?
