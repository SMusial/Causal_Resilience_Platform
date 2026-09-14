# V1 Specification Reconciliation Decisions

## Purpose

This document is the authoritative reconciliation record for the V1 specification of the Causal Resilience Intervention Allocator. It resolves conflicts between the original requirements, design, and task plan before implementation begins.

## Decisions

### 1. V1 causal scope

V1 teaches and estimates static, point-treatment causal effects at a clearly defined baseline decision point (`time zero`). The simulator may generate dynamic incident trajectories, but dynamic trajectories are not evidence that V1 estimates longitudinal causal effects.

V1 does not implement time-varying treatment estimands, treatment-confounder feedback methods, marginal structural models, g-estimation, causal survival analysis, mediation, or instrumental variables.

### 2. Primary causal contrast

The primary V1 contrast is binary and consistently named:

* Treatment: `COORDINATED_RESPONSE`
* Comparison: `MONITOR_REASSESS`

`COORDINATED_RESPONSE` is one pre-defined protocol with an explicit operational definition. It is not an arbitrary bundle assembled differently for each episode.

### 3. Multi-action protocols

The seven operational protocols remain in the domain model because they make the telecom scenario realistic:

* `MONITOR_REASSESS`
* `NOC_REMOTE`
* `SOC_CONTAIN`
* `L2_INVESTIGATE`
* `L3_PRODUCT`
* `FIELD_REPAIR`
* `COORDINATED_RESPONSE`

In V1 they are used for eligibility, dynamic simulation, policy demonstration, and constrained allocation. The observational causal estimators are only required to estimate the primary binary contrast. V1 must not present a seven-action policy comparison as an identified causal estimate unless a separate multi-valued treatment estimand and identification strategy are explicitly defined.

### 4. Outcome scope

The primary causal outcome is:

* `customer_impact_minutes_24h`: continuous, lower is better, measured over a fixed 24-hour follow-up.

The main secondary outcome is:

* `sla_breach_24h`: binary, defined over the same follow-up.

`time_to_containment` and `time_to_service_restoration` may be displayed as descriptive timeline metrics and simulated policy outcomes. Causal survival estimands, censoring-weighted survival estimators, and survival-specific inference are deferred.

### 5. Disturbances

Cyberattack and vandalism are exogenous disturbance types in the synthetic data-generating process. They are not causal treatments. They affect incident state, eligibility, resource needs, and potential outcomes. All security content remains abstract and operational; the project contains no exploit instructions or real vulnerabilities.

### 6. Dynamic simulation boundary

The dynamic simulator includes state transitions, delays, queues, escalation, resource capacity, and recurrence. A dynamic policy rollout answers a simulation question such as “what trajectory does this policy generate under the specified structural model?” It must not be labelled as an observational causal estimate of a dynamic regime in V1.

### 7. Cross-domain boundary

V1 proves cross-domain readiness through a formal `DomainAdapter` contract and a complete telecom adapter. A second industry adapter is post-V1. The contract must require domain semantics, a domain DAG, a structural DGP with known ground truth, transitions, constraints, and contract tests.

### 8. Visualization baseline

Plotly is the required visualization baseline. Graphviz is optional and must not be a required installation dependency for V1. Every visual must use labels, annotations, symbols, or patterns in addition to color.

### 9. Validation

The structural simulator's known ground truth is the primary correctness oracle. Library output is not treated as proof of causal validity. Tests must evaluate bias, uncertainty, overlap, reproducibility, and behavior under deliberately violated assumptions.

### 10. Release acceptance

The previous task plan referenced a non-existent section 26. This reconciliation replaces that reference with `docs/v1_release_acceptance.md`, which contains exactly 26 explicit release criteria.

## Canonical terminology

* `incident_episode`: one synthetic incident observed from eligibility through follow-up.
* `time_zero`: the first decision point at which the primary treatment could be assigned.
* `baseline_covariate`: information available immediately before treatment assignment.
* `disturbance`: an exogenous event type such as equipment failure, cyberattack, or vandalism.
* `treatment`: the primary binary protocol assigned at time zero.
* `outcome`: a pre-specified post-treatment result.
* `estimand`: the precisely defined causal quantity of interest.
* `estimator`: the procedure used to estimate the estimand from data.
* `estimate`: the numerical result returned by the estimator.
* `policy simulation`: a structural-model rollout, not automatically a causal estimate.

## Implementation gate

No V1 implementation should start until the corrected requirements, design, task plan, and release acceptance criteria are stored in the repository. V0 implementation is the next active workstream.
