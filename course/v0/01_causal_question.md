# Lesson 1 — Ask a causal question

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 3 (§3.1–3.2)

## Learning objective

State the V0 causal question using population, intervention, comparator,
outcome, time zero, and follow-up period.

## The V0 causal question

> Among eligible synthetic telecom incidents at detection, what is the average
> effect of assigning **EARLY_COORDINATED_RESPONSE** rather than
> **MONITOR_REASSESS** on `customer_impact_minutes_24h` during the following
> 24 hours?

## Treatment and comparator

| | Definition |
|---|---|
| **Intervention** | `EARLY_COORDINATED_RESPONSE` — predefined coordination protocol within 15 min of detection |
| **Comparator** | `MONITOR_REASSESS` — monitor and reassess at the 60-minute checkpoint |

## Outcome and follow-up

- **Outcome:** `customer_impact_minutes_24h` — total customer-impact minutes over 24 hours (lower is better)
- **Follow-up:** 24 hours from first reliable detection timestamp

## Estimand

```
ATE = E[Y(1) - Y(0)]   on the mean-difference scale
```

A negative ATE means early coordinated response reduces average customer-impact minutes.

## Target-trial components

| Component | V0 definition |
|---|---|
| Population | Eligible synthetic incidents at detection with observed baseline severity |
| Time zero | First reliable detection timestamp |
| Intervention | `EARLY_COORDINATED_RESPONSE` |
| Comparator | `MONITOR_REASSESS` |
| Outcome | `customer_impact_minutes_24h` |
| Follow-up | 24 hours from detection |
| Causal contrast | Population average treatment effect (ATE) |
| Estimand | `E[Y(1) − Y(0)]` |

## Identification assumptions

1. Consistency: observed outcome equals potential outcome under assigned treatment.
2. Exchangeability: Y(a) ⊥ A | severity.
3. Positivity: 0 < P(A=1 | severity=l) < 1 for all l.
4. No interference: one episode's treatment does not affect another's outcome.
5. Complete follow-up: 24-hour outcome is observed for all eligible episodes.

## Limitation

The intervention definition is deliberately abstract. In real operations,
treatment-version inconsistency — different teams executing the protocol
differently — would violate the consistency assumption and bias any estimate.

## Why the question must come first

A library call is never a substitute for a causal question. Choosing an
estimator before defining the estimand produces a number without a meaning.

> All data are entirely synthetic and illustrative. Results do not represent
> real telecom operations, real organizations, or real interventions.

## Reflection

- Can you restate the V0 causal question in one sentence without using the
  words "impact", "resilience", or "performance"?
- What would change if the follow-up period were 48 hours instead of 24?
- Is "better response" a well-defined intervention? Why or why not?
