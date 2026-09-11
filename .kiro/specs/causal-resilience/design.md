# Design — Causal Resilience Intervention Allocator (V1)

## 1. Architecture overview

```
causal-resilience-intervention-allocator/
├── app.py                          # Streamlit UI — course mode + sandbox
├── src/causal_resilience/
│   ├── config.py                   # ScenarioConfig, CapacityConfig, PolicyConfig
│   ├── schemas.py                  # Pydantic schemas: Episode, State, Action, Outcome, EstimateResult
│   ├── provenance.py               # Provenance, reproducibility metadata
│   ├── domain/
│   │   ├── adapter.py              # DomainAdapter Protocol contract
│   │   └── telecom_resilience.py   # Telecom adapter implementation
│   ├── simulation/
│   │   ├── structural_model.py     # Structural DGP, counterfactual oracle
│   │   ├── generator.py            # Episode generation entry point
│   │   ├── transitions.py          # State transition functions
│   │   └── policies.py             # Policy execution and simulation loop
│   ├── causal/
│   │   ├── dag.py                  # DAG definition, backdoor paths, adjustment sets
│   │   ├── estimands.py            # Estimand, TargetTrial, PopulationDefinition
│   │   ├── identification.py       # Identification checks, assumption warnings
│   │   ├── diagnostics.py          # Overlap, balance, weight diagnostics
│   │   ├── baselines.py            # Randomized DiM, crude observational DiM, stratified
│   │   ├── standardization.py      # Outcome regression + g-formula standardization
│   │   ├── ipw.py                  # Propensity model, IPW, stabilized weights
│   │   ├── doubly_robust.py        # DR estimator, cross-fitting
│   │   └── heterogeneity.py        # Subgroup effects, CATE via EconML
│   ├── policy/
│   │   ├── value.py                # Policy value V(π), holdout evaluation
│   │   ├── allocator.py            # Constrained intervention allocator
│   │   └── constraints.py          # Capacity, safety, security, budget constraints
│   ├── explanations.py             # Analysis cards, reason codes, audit export
│   └── visualization.py            # Plotly helpers for all required charts
├── course/                         # Lesson markdown files (01–13)
├── tests/                          # pytest test suite
└── docs/                           # Data dictionary, assumptions, limitations
```

## 2. Core design principles

1. **One case, many lessons** — all lessons reuse the same telecom incident-response world.
2. **Dynamic simulation ≠ dynamic causal estimation** — V1 estimands are defined at a baseline decision point. Longitudinal estimands are deferred.
3. **Ground truth is a teaching instrument** — the oracle is hidden from normal estimates; accessible only in teaching/test mode.
4. **A warning is better than a false number** — if a contrast is not supported, show an identification warning, not a precise estimate.
5. **Separate four layers** — state prediction, causal estimation, simulation, and allocation must be distinct.

## 3. Domain model

### 3.1 Primary unit: `incident_episode`

```python
Episode(
    episode_id: str,
    baseline_covariates: dict,
    disturbance: Disturbance,
    initial_state: CaseState,
    treatment: Action,
    state_history: list[CaseState],
    action_history: list[Action],
    outcomes: OutcomeSet,
    censoring: CensoringIndicator,
    provenance: Provenance,
    ground_truth: GroundTruth | None,   # hidden in normal mode
)
```

### 3.2 State vector

```python
CaseState(
    service_impact: float,
    severity: float,
    affected_customers: int,
    asset_health: float,
    fault_probability: float,
    security_risk: float,
    topology_criticality: float,
    redundancy: float,
    queue_backlog: int,
    sla_time_remaining: float,
    team_load: dict[str, float],
    weather_and_access: float,
    prior_actions: list[str],
    escalation_history: list[str],
    observability_quality: float,
    operational_readiness: float,
)
```

### 3.3 State transition

```
S_t, U_t, A_t, E_t → S_(t+1), Y, C
```

- `S_t` observed state, `U_t` latent factors, `A_t` action, `E_t` exogenous disturbance
- `Y` outcome set, `C` censoring indicator

### 3.4 Default time scales

| Horizon | Default |
|---|---|
| Decision/observation step | 15 minutes |
| Incident-response horizon | 24 hours |
| Recurrence follow-up | 30 days |
| Portfolio simulation | 30 days |

## 4. Module contracts

### 4.1 `DomainAdapter` Protocol

```python
class DomainAdapter(Protocol):
    domain_name: str
    schema_version: str

    def generate_dataset(self, config: ScenarioConfig) -> CaseDataset: ...
    def define_target_trials(self) -> list[TargetTrial]: ...
    def list_actions(self, state: CaseState) -> list[Action]: ...
    def feasible_actions(self, state: CaseState, resources: ResourceState) -> list[Action]: ...
    def transition(self, state: CaseState, action: Action, rng: RandomGenerator) -> CaseState: ...
    def calculate_outcomes(self, episode: Episode) -> OutcomeSet: ...
    def constraints(self, horizon: Horizon) -> ConstraintSet: ...
    def explain(self, recommendation: Recommendation) -> Explanation: ...
```

### 4.2 `EstimateResult`

```python
EstimateResult(
    estimand: Estimand,
    population: PopulationDefinition,
    estimate: float,
    confidence_interval: tuple[float, float],
    standard_error: float | None,
    method: str,
    assumptions: list[str],
    diagnostics: list[Diagnostic],
    warnings: list[str],
    sample_size: int,
    effective_sample_size: float | None,
    ground_truth_comparison: GroundTruthComparison | None,
    provenance: Provenance,
)
```

### 4.3 `TargetTrial`

```python
TargetTrial(
    trial_id: str,
    eligibility: EligibilityRule,
    time_zero: TimeZeroRule,
    strategies: list[TreatmentStrategy],
    outcomes: list[OutcomeDefinition],
    follow_up: FollowUpDefinition,
    censoring: CensoringDefinition,
    estimand: Estimand,
    assumptions: list[Assumption],
)
```

### 4.4 `ScenarioConfig`

```python
ScenarioConfig(
    seed: int,
    n_episodes: int,
    disturbance_mix: dict,
    confounding_strength: float,
    overlap_mode: str,
    measurement_error: float,
    missingness_mode: str,
    censoring_mode: str,
    capacity_config: CapacityConfig,
    policy_config: PolicyConfig,
    schema_version: str,
)
```

## 5. Causal graph (baseline DAG)

```
Disturbance severity ──┬──> Treatment assignment ──> Outcome
                       ├──> Outcome
                       └──> Escalation need

Topology criticality ──┬──> Treatment assignment
                       └──> Outcome

Team backlog ──────────┬──> Treatment assignment
                       └──> Outcome

Operational readiness ─┬──> Treatment assignment   (latent in bias scenario)
                       └──> Outcome

Treatment ─────────────> Containment ─────────────> Outcome
```

## 6. Simulator separation

The simulator keeps these components strictly separate:

| Component | Responsibility |
|---|---|
| Transition model | State evolution given action and disturbance |
| Treatment-assignment mechanism | How treatments are assigned (randomized / confounded) |
| Observation and measurement model | What is observed vs. latent |
| Missingness and censoring mechanism | Which outcomes are observed |
| Resource and queue model | Capacity, backlog, availability |
| Policy execution | Which action a policy selects |
| Ground-truth oracle | Counterfactual outcomes — never called by estimators |

## 7. Policy layer

### 7.1 Objective

```
maximize  expected avoided_customer_impact_minutes
        - cost_penalty
        - safety_risk_penalty
        - residual_security_risk_penalty
        - recurrence_penalty
```

### 7.2 Policies compared

| Policy | Description |
|---|---|
| Current-practice | Observed assignment distribution |
| Severity-only | Assign most intensive intervention to highest severity |
| Predictive-risk | Assign based on predicted outcome risk |
| Causal-effect | Assign based on estimated incremental benefit |
| Value-per-resource | Maximize benefit per unit of constrained resource |
| Oracle | Ground-truth optimal — teaching mode only |

## 8. Visual language

| Color | Meaning |
|---|---|
| Blue | Baseline and observed state |
| Orange | Intervention or treatment assignment |
| Green | Improvement, containment, beneficial effect |
| Red | Deterioration, harm, warning, constraint violation |
| Purple | Latent, hidden, or counterfactual information |
| Gray | Unavailable, censored, or not identified |

Color is never the only carrier of meaning — every chart also uses labels, symbols, annotations, or patterns.

## 9. Lesson structure (each lesson)

1. Operational situation
2. Causal question
3. Target trial
4. Assumptions
5. Data and DAG
6. Method
7. Result (estimate + uncertainty + ground-truth comparison where allowed)
8. Interpretation
9. Experiment (what should the learner change?)

## 10. Telecom adapter specifics

### Organizational roles

| Role | Responsibility |
|---|---|
| L1 / Front Office | Intake, classification, communication, basic diagnostics, SLA control |
| NOC | Network diagnosis, rerouting, failover, rollback, remote remediation |
| SOC | Security triage, enrichment, containment, isolation, residual-risk assessment |
| L2 / Back Office | Deeper investigation, correlation, remediation planning |
| L3 | Product defect analysis, engineering decision, durable fix |
| Field Operations | Physical inspection, safe repair, replacement, facility restoration |

### Intervention protocols

| Code | Typical eligibility |
|---|---|
| `MONITOR_REASSESS` | Low immediate impact, sufficient observability |
| `NOC_REMOTE` | Network/software condition with safe remote action |
| `SOC_CONTAIN` | Cyber-risk or security-relevant disturbance |
| `L2_INVESTIGATE` | Complex technical issue or failed initial response |
| `L3_PRODUCT` | Product, version, defect, or lifecycle issue |
| `FIELD_REPAIR` | Physical fault and safe site access |
| `COORDINATED_RESPONSE` | Multi-domain incident with explicit coordination rules |

## 11. Source hierarchy and assumptions

| Source | Role in V1 |
|---|---|
| Hernán & Robins, *What If* | Primary methodological source — potential outcomes, estimands, target-trial thinking, IPW, standardization |
| Pearl, *Causality* | Supplementary — DAGs, structural causal models, do-calculus, graphical identification |
| Cunningham, *The Mixtape* | Supplementary — intuition, communication, selected econometric methods (Python re-implementations only) |
| VanderWeele, *Explanation in Causal Inference* | Deferred — mediation, interaction, effect decomposition (post-V1) |
| DoWhy, EconML, statsmodels, scikit-learn docs | Implementation references — APIs and patterns, not methodological authorities |
| Streamlit, Plotly docs | Engineering references |
| `rlvr-enterprise-allocator` | Educational architecture reference — one coherent operational use case pattern |

Key project assumptions:
- Python-first and Python-only for V1. R and Rust excluded.
- Every causal result requires: causal question → estimand → target-trial spec → identification assumptions → diagnostics → estimator.
- Simulator ground truth is the primary validation oracle, not package output.
- Distinguish clearly: method implemented vs. demonstrated conceptually vs. deferred.
- Per-module documentation must identify: source and section, estimand, assumptions, implementation type, validation test, and any textbook-vs-software differences.

## 12. Cross-domain architecture

The causal engine depends on domain-neutral contracts. The telecom adapter supplies telecom-specific semantics. A future adapter must:

1. Define one domain decision and one primary estimand
2. Define eligibility, time zero, treatment strategies, outcomes, follow-up, censoring
3. Create a domain DAG and declare assumptions
4. Map domain entities into the neutral contract
5. Create a structural simulator with known ground truth
6. Implement state transitions, delays, queues, and constraints
7. Run common estimators without modifying the causal engine
8. Pass contract and ground-truth tests
