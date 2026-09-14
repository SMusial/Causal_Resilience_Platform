# Kiro Handoff — V1 Specification Reconciliation

## Current instruction

Do not implement V1 yet. The first project action is to archive these reconciled documents in the repository and stop for review:

* `v1_reconciliation_decisions.md`
* `design.md` replaced by the reconciled design
* `requirements.md` replaced by the reconciled requirements
* `tasks.md` replaced by the reconciled tasks

The documents are the baseline for later V1 implementation. V0 is the next active implementation target and will receive a separate specification.

## Non-negotiable decisions

* V1 causal estimation is static at `time_zero`.
* Primary contrast: `COORDINATED_RESPONSE` versus `MONITOR_REASSESS`.
* Primary causal outcome: `customer_impact_minutes_24h`.
* Time-to-containment and time-to-restoration are descriptive/simulation metrics only in V1.
* Seven operational protocols remain for simulation and constrained policy demonstration, not an automatically identified seven-action causal effect.
* Cyberattack and vandalism are abstract synthetic disturbances, never treatments.
* Plotly is required; Graphviz is optional.
* Python only; no R or Rust in V1.
* Do not start implementation from the old task list.

## Required response after archival

Return:

1. the repository paths used for the four documents;
2. confirmation that no code was changed;
3. confirmation that the old `STANDARD_REASSESS` / `MONITOR_REASSESS` inconsistency was removed;
4. confirmation that the missing release-acceptance document is planned;
5. any conflict discovered in the repository that prevents V0 work.
