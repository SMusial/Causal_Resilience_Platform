# V1 Module 3 — Randomization: when association equals causation

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.1–2.2)

## Learning objective

Explain why randomization supports unconditional exchangeability in the V1
world, and why the difference in means estimates the ATE despite the richer
V1 confounder set.

## The V1 causal question

> Among eligible synthetic telecom incidents at detection, what is the average
> effect of assigning **COORDINATED_RESPONSE** rather than **MONITOR_REASSESS**
> on `customer_impact_minutes_24h` during the following 24 hours?

## Why randomization works

Under randomized assignment, treatment is allocated independently of severity,
topology criticality, team backlog, operational readiness, and all other
baseline characteristics:

```
Y(a) ⊥ A   (unconditional exchangeability)
```

When unconditional exchangeability holds, the observed group means identify
the potential-outcome means:

```
E[Y | A=1] = E[Y(1)]
E[Y | A=0] = E[Y(0)]
ATE = E[Y | A=1] − E[Y | A=0]
```

The crude difference in means is a valid causal estimator — not because the
groups are identical, but because treatment assignment is unrelated to the
potential outcomes.

## What changes from V0

| Dimension | V0 | V1 |
|---|---|---|
| Treatment label | `EARLY_COORDINATED_RESPONSE` | `COORDINATED_RESPONSE` |
| Confounders present | severity | severity, topology_criticality, team_backlog, operational_readiness |
| Confounders adjusted for under randomization | none needed | none needed |
| Exchangeability | unconditional | unconditional (unchanged) |
| Estimator | difference in means | difference in means (unchanged) |

The richer V1 confounder set does not change the logic. Under randomization,
none of the four confounders need to be measured or adjusted for — they are
balanced across treatment groups by design.

## Identification assumptions

1. Consistency: observed outcome equals potential outcome under assigned treatment.
2. Exchangeability: Y(a) ⊥ A (unconditional under randomization).
3. Positivity: 0 < P(A=1) < 1 for all episodes in the target population.
4. No interference: one episode's treatment does not affect another's outcome (V1 simplification).
5. Complete follow-up: 24-hour outcome is observed for all eligible episodes (V1 simplification).

## Finite-sample variability

The estimate will not equal the oracle ATE exactly in any finite sample.
The error shrinks as sample size grows.

> **The 95% bootstrap CI reflects sampling variability only.**
> It does not quantify uncertainty from unmeasured confounding.
> A narrow CI under strong unmeasured confounding is false precision.

## Limitation

Randomization is a design property — it cannot be assumed from observational
data. V1 M3 uses the V0 DGP for illustration; the V1 DGP with four confounders
is introduced in later modules.

## Reflection

- Why does balance on all four V1 confounders not need to be perfect for
  randomization to support a causal interpretation?
- What would happen to the estimate if the randomization probability were
  80/20 instead of 50/50?
- If you observed that treated and control groups differ on `team_backlog`
  in a randomized trial, would that invalidate the causal interpretation?
