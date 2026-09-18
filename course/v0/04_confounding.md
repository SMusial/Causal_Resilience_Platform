# Lesson 4 — Confounding and the DAG

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 6 (§6.1–6.3)

## Learning objective

Explain why a crude observational comparison may not estimate the ATE when a
common cause of treatment and outcome is present.

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

## Estimator (naive, biased under confounding)

**Crude difference in means:**

```
ATE_hat = mean(Y | A=1) - mean(Y | A=0)
```

Under confounded assignment this is an associational comparison, not a
causal estimate.

## The V0 confounder

Severity is a common cause of both treatment assignment and the outcome:

```
severity ──> treatment
severity ──> outcome
treatment ──> outcome
```

Higher-severity incidents are more likely to receive EARLY_COORDINATED_RESPONSE
and also tend to have higher `customer_impact_minutes_24h` regardless of
treatment.

## The backdoor path and bias direction

The path `treatment ← severity → outcome` is a backdoor path. It opens a
non-causal association between treatment and outcome.

Because high-severity episodes cluster in the treated group and would have
had worse outcomes regardless of treatment, the crude estimate is pulled
toward a **less negative (more positive)** value than the true ATE — or even
a positive value. The raw comparison makes the intervention look less
beneficial than it truly is.

## The DAG

A directed acyclic graph (DAG) makes the confounding structure explicit:

- Orange arrows: confounder paths (backdoor)
- Blue arrow: causal path

The DAG guides the choice of adjustment strategy. To estimate the ATE, we
must block the backdoor path by adjusting for severity.

## Identification assumptions

1. Consistency: observed outcome equals potential outcome under assigned treatment.
2. Exchangeability: Y(a) ⊥ A | severity (conditional on measured severity).
3. Positivity: 0 < P(A=1 | severity=l) < 1 for all l.
4. No interference: one episode's treatment does not affect another's outcome.
5. Complete follow-up: 24-hour outcome is observed for all eligible episodes.

## Limitation

The DAG assumes severity is the only confounder. In real data, unmeasured
confounders may exist. Adjustment for measured severity cannot remove bias
from variables that were not recorded.

> All data are entirely synthetic and illustrative. Results do not represent
> real telecom operations, real organizations, or real interventions.

## Reflection

- If you did not know the DGP, how would you decide whether severity is a
  confounder?
- Why does a statistically precise estimate not rule out confounding bias?
- What would happen to the bias if confounding strength were increased?
