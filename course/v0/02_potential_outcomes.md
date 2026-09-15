# Lesson 2 — Potential outcomes and the missing counterfactual

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 1 (§1.1–1.2)

## Learning objective

Explain why individual causal effects are generally not directly observed,
and why estimating the average treatment effect requires assumptions.

## Potential outcomes

For each incident episode *i*, define two potential outcomes:

- **Y_i(1)** — `customer_impact_minutes_24h` if episode *i* receives
  `EARLY_COORDINATED_RESPONSE`
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

## The average treatment effect

Because individual effects are not identifiable from a single observation,
we target the **population average treatment effect (ATE)**:

```
ATE = E[Y(1) − Y(0)] = E[Y(1)] − E[Y(0)]
```

A negative ATE means early coordinated response reduces average
customer-impact minutes — a beneficial effect.

## The oracle (teaching mode only)

The V0 simulator generates both potential outcomes before assigning
treatment. In **teaching mode**, the oracle columns `Y(0)` and `Y(1)` are
visible. In **normal mode**, they are hidden — as they would be in real data.

The oracle ATE is the mean of `Y(1) − Y(0)` computed directly from the
simulator's hidden truth. It is a learning reference, not an estimator.

## Reflection

- If you could observe both `Y_i(0)` and `Y_i(1)` for every episode, would
  you still need an estimator?
- Why does the consistency assumption (`Y = Y(A)`) matter for connecting
  potential outcomes to observed data?
- What would it mean for the consistency assumption to be violated in this
  scenario?
