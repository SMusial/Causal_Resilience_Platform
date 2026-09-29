# V1 Module 1 — Ask a causal question

**Source:** Hernán & Robins, *Causal Inference: What If*, Chapter 3 (§3.1–3.2)

## Learning objective

State the V1 causal question using population, intervention, comparator,
outcome, time zero, follow-up, and the minimum sufficient adjustment set
under the V1 baseline DAG.

## The V1 causal question

> Among eligible synthetic telecom incidents at detection, what is the average
> effect of assigning **COORDINATED_RESPONSE** rather than **MONITOR_REASSESS**
> on `customer_impact_minutes_24h` during the following 24 hours?

## Target-trial card

| Component | V1 definition |
|---|---|
| Eligibility | Eligible synthetic incidents at detection with observed baseline covariates and both strategies feasible |
| Time zero | First reliable detection timestamp |
| Intervention | `COORDINATED_RESPONSE` — fixed coordination bundle within 15 min |
| Comparator | `MONITOR_REASSESS` — monitor and reassess at scheduled checkpoint |
| Assignment | Randomized or observational, depending on selected DGP scenario |
| Follow-up | 24 hours from detection |
| Primary outcome | `customer_impact_minutes_24h` (minutes, lower is better) |
| Secondary outcome | `sla_breach_24h` (binary, risk-difference scale) |
| Censoring | None in V1 base scenario |
| Primary estimand | `E[Y(1) − Y(0)]` on the mean-difference scale |
| Secondary estimand | `E[Y(1) − Y(0)]` on the risk-difference scale for `sla_breach_24h` |

## What changes from V0

| Dimension | V0 | V1 |
|---|---|---|
| Adjustment set | severity only | severity, topology criticality, team backlog, operational readiness |
| Secondary outcome | none | `sla_breach_24h` |
| Protocols available | 2 (binary contrast) | 7 (simulation layer); binary contrast for causal estimation |
| Roles | none | L1, NOC, SOC, L2, L3, Field Operations |
| Disturbances | 7 abstract types | same + cyberattack and vandalism as disturbance types only |

## The seven protocols

| Protocol | Role | Use in V1 |
|---|---|---|
| `MONITOR_REASSESS` | — | Primary comparator |
| `NOC_REMOTE` | NOC | Simulation and policy demonstration |
| `SOC_CONTAIN` | SOC | Simulation and policy demonstration |
| `L2_INVESTIGATE` | L2 | Simulation and policy demonstration |
| `L3_PRODUCT` | L3 | Simulation and policy demonstration |
| `FIELD_REPAIR` | Field Operations | Simulation and policy demonstration |
| `COORDINATED_RESPONSE` | All roles | Primary treatment — fixed bundle |

V1 does not claim a fully identified seven-action observational causal effect.
The binary contrast is the only primary causal estimand.

## Minimum sufficient adjustment set

Under the V1 baseline DAG, the following variables are common causes of
treatment assignment and outcome:

- `severity` — drives both treatment urgency and outcome magnitude
- `topology_criticality` — affects treatment priority and impact scope
- `team_backlog` — affects treatment assignment probability and response speed
- `operational_readiness` — affects both assignment and execution quality

## Reflection

- Why is `COORDINATED_RESPONSE` defined as a fixed bundle rather than a free
  choice of role?
- What would happen to the estimand if we tried to estimate separate effects
  for each of the seven protocols from observational data?
- Why are cyberattack and vandalism disturbance types rather than treatments?
