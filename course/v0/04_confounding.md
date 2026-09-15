# Lesson 4 — Confounding and the DAG

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 6 (§6.1–6.3)

## Learning objective

Explain why a crude observational comparison may not estimate the ATE when a
common cause of treatment and outcome is present.

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

## The backdoor path

The path `treatment ← severity → outcome` is a backdoor path. It opens a
non-causal association between treatment and outcome. The crude difference in
means conflates the treatment effect with the severity effect.

## The DAG

A directed acyclic graph (DAG) makes the confounding structure explicit:

- Orange arrows: confounder paths (backdoor)
- Blue arrow: causal path

The DAG guides the choice of adjustment strategy. To estimate the ATE, we
must block the backdoor path by adjusting for severity.

## Reflection

- If you did not know the DGP, how would you decide whether severity is a
  confounder?
- Why does a statistically precise estimate not rule out confounding bias?
- What would happen to the bias if confounding strength were increased?
