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

## Components

| Component | V0 definition |
|---|---|
| Population | Eligible synthetic incidents at detection with observed baseline severity |
| Time zero | First reliable detection timestamp |
| Intervention | `EARLY_COORDINATED_RESPONSE` — predefined coordination protocol within 15 min |
| Comparator | `MONITOR_REASSESS` — monitor and reassess at 60-min checkpoint |
| Outcome | `customer_impact_minutes_24h` — total customer-impact minutes over 24 h |
| Follow-up | 24 hours from detection |
| Causal contrast | Population average treatment effect (ATE) on the mean-difference scale |
| Estimand | `E[Y(1) − Y(0)]` |

## Why the question must come first

A library call is never a substitute for a causal question. Choosing an
estimator before defining the estimand produces a number without a meaning.

The target-trial framework (Hernán & Robins, Chapter 3) requires that the
intervention and comparator be defined precisely enough that two analysts
would agree on whether a given episode received the intervention.

## Reflection

- Can you restate the V0 causal question in one sentence without using the
  words "impact", "resilience", or "performance"?
- What would change if the follow-up period were 48 hours instead of 24?
- Is "better response" a well-defined intervention? Why or why not?
