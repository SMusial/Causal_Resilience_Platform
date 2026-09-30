# V1 Module 2 — Potential outcomes and the missing counterfactual

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 1 (§1.1–1.2)

## Learning objective

Explain why individual causal effects are not directly observed in the V1
operational world, and why the richer V1 confounder set does not change the
fundamental problem of causal inference.

## The V1 causal question

> Among eligible synthetic telecom incidents at detection, what is the average
> effect of assigning **COORDINATED_RESPONSE** rather than **MONITOR_REASSESS**
> on `customer_impact_minutes_24h` during the following 24 hours?

## Potential outcomes

For each incident episode *i*, define two potential outcomes:

- **Y_i(1)** — `customer_impact_minutes_24h` if episode *i* receives
  `COORDINATED_RESPONSE`
- **Y_i(0)** — `customer_impact_minutes_24h` if episode *i* receives
  `MONITOR_REASSESS`

The **individual causal effect** is `Y_i(1) − Y_i(0)`.

## The fundamental problem

We can only observe **one** potential outcome per episode — the one
corresponding to the treatment actually assigned. The other is the
**counterfactual**: what would have happened under the alternative.

```
Observed:  Y_i = Y_i(A_i)   (consistency assumption)
Missing:   Y_i(1 − A_i)     (the counterfactual)
```

This is true regardless of how many confounders are in the adjustment set.
Adding severity, topology criticality, team backlog, and operational readiness
to the V1 world does not make the missing counterfactual observable — it only
changes what we must condition on to achieve exchangeability.

## The average treatment effect

Because individual effects are not identifiable from a single observation,
we target the **population average treatment effect (ATE)**:

```
ATE = E[Y(1) − Y(0)] = E[Y(1)] − E[Y(0)]
```

A negative ATE means COORDINATED_RESPONSE reduces average customer-impact
minutes — a beneficial effect.

## What changes from V0

| Dimension | V0 | V1 |
|---|---|---|
| Treatment label | `EARLY_COORDINATED_RESPONSE` | `COORDINATED_RESPONSE` |
| Adjustment set | severity only | severity, topology_criticality, team_backlog, operational_readiness |
| Confounders in PO table | severity | severity + 3 additional baseline covariates |
| Fundamental problem | unchanged | unchanged |
| Oracle availability | teaching mode only | teaching mode only |

The fundamental problem of causal inference is the same in V0 and V1.
A richer operational world does not make the counterfactual observable.

## The oracle (teaching mode only)

The V0 simulator generates both potential outcomes before assigning treatment.
V1 M2 uses the same V0 DGP oracle — the V1 DGP is introduced in later modules.
In **teaching mode**, the oracle columns `Y(0)` and `Y(1)` are visible.
In **normal mode**, they are hidden — as they would be in real data.

> **The oracle is available only because the data are synthetic.**
> In real data, both potential outcomes are never simultaneously observed
> for the same episode.

## Identification assumptions

1. Consistency: observed outcome equals potential outcome under assigned treatment.
2. Exchangeability: Y(a) ⊥ A | {severity, topology_criticality, team_backlog, operational_readiness}.
3. Positivity: every stratum of the adjustment set has positive probability of either protocol.
4. No interference: one episode's treatment does not affect another's outcome (V1 simplification).
5. Complete follow-up: 24-hour outcome is observed for all eligible episodes (V1 simplification).

## Limitation

Any estimator must rely on assumptions about the missing counterfactual.
These assumptions cannot be verified from observed data alone. The simulator
makes them true by construction — which is why the oracle comparison is a
useful learning tool but not evidence about real operations.

The V1 adjustment set is richer than V0 but still simplified. Unmeasured
confounders (team experience, vendor relationships, shift patterns) are not
captured.

## Reflection

- Does adding more confounders to the adjustment set make the missing
  counterfactual observable? Why or why not?
- If you could observe both `Y_i(0)` and `Y_i(1)` for every episode, would
  you still need an estimator?
- Why does the consistency assumption matter more when the treatment is a
  complex bundle like `COORDINATED_RESPONSE`?
