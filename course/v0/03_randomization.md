# Lesson 3 — Randomization: when association can identify causation

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 2 (§2.1–2.2)

## Learning objective

Explain why randomization supports exchangeability and why a difference in
observed means estimates the ATE under randomized assignment.

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

## Finite-sample variability

The estimate will not equal the oracle ATE exactly in any finite sample.
The error shrinks as sample size grows. The bootstrap CI captures this
sampling variability.

## Reflection

- Why does balance on severity not need to be perfect for randomization to
  support a causal interpretation?
- What happens to the estimate as you increase the sample size?
- Would the estimate still be valid if the randomization were 70/30 instead
  of 50/50?
