# Requirements — Causal Resilience Intervention Allocator (V1)

## 1. Purpose

An educational causal-inference laboratory and decision-intelligence demonstration built around a telecom incident-response scenario. The system teaches the difference between predicting an outcome, estimating the effect of an intervention, simulating counterfactual trajectories, evaluating a policy, and allocating scarce operational capacity.

## 2. Functional requirements

### 2.1 User experiences

- REQ-UX-01: Provide a **Course mode** — a guided sequence of 13 lessons using the same incident-response case.
- REQ-UX-02: Provide an **Experimental sandbox** — a free-form interface for changing data-generating assumptions, treatment assignment, overlap, capacity, and policy rules.
- REQ-UX-03: Users must be able to move backward and forward through lessons without losing scenario configuration.

### 2.2 Causal curriculum (13 lessons)

- REQ-CUR-01: Lesson 1 — What is a causal effect? Compare potential outcomes under two response pathways.
- REQ-CUR-02: Lesson 2 — Randomized incident-response experiment. Activate randomized assignment and compare empirical difference in means with known ground truth.
- REQ-CUR-03: Lesson 3 — Observational incident response. Turn on severity-driven assignment and observe naive comparison bias.
- REQ-CUR-04: Lesson 4 — Exchangeability, positivity, and consistency. Change the DGP so each assumption is satisfied or violated.
- REQ-CUR-05: Lesson 5 — DAGs and confounding. Inspect the incident DAG, choose an adjustment set, observe consequences.
- REQ-CUR-06: Lesson 6 — Selection and measurement bias. Change which incidents enter the dataset and how severity is measured.
- REQ-CUR-07: Lesson 7 — Effect modification and interaction. Examine how effect changes by disturbance type, severity, topology criticality, and security risk.
- REQ-CUR-08: Lesson 8 — Outcome regression and standardization. Fit an outcome model, standardize predictions over the target covariate distribution.
- REQ-CUR-09: Lesson 9 — Propensity scores and IPW. Inspect treatment probabilities, overlap, weight distributions, effective sample size.
- REQ-CUR-10: Lesson 10 — Doubly robust estimation. Compare outcome and treatment nuisance models, cross-fitting where supported.
- REQ-CUR-11: Lesson 11 — Causal heterogeneity. Examine conditional effects and counterfactual risks.
- REQ-CUR-12: Lesson 12 — Policy value and constrained allocation. Compare naive risk ranking with causal benefit ranking under constraints.
- REQ-CUR-13: Lesson 13 — Audit and limitations. Produce an analysis card with target trial, estimand, assumptions, diagnostics, uncertainty, limitations, and provenance.

### 2.3 Data generation

- REQ-DGP-01: Structural simulator — not a random table generator. Must recover latent factors, potential outcomes, treatment-assignment mechanism, and transition parameters in test mode.
- REQ-DGP-02: Support disturbance types: equipment failure, software regression, misconfiguration, overload, weather-related disruption, cyberattack, and vandalism.
- REQ-DGP-03: Include all six operational roles: L1/Front Office, NOC, SOC, L2/Back Office, L3/Product Development, Field Operations.
- REQ-DGP-04: Support bias and failure scenarios: randomized assignment, confounding by severity, confounding by indication, unmeasured operational readiness, limited overlap, treatment-version mismatch, selection, measurement error, outcome missingness, informative censoring, changing workload, post-treatment state variables, concurrent episodes.
- REQ-DGP-05: Reproducibility — same seed + scenario + generator version + schema version must produce identical results.

### 2.4 Causal estimators

- REQ-EST-01: Randomized difference in means.
- REQ-EST-02: Crude observational difference in means.
- REQ-EST-03: Stratified adjustment.
- REQ-EST-04: Outcome regression.
- REQ-EST-05: Standardization / parametric g-formula for supported baseline contrasts.
- REQ-EST-06: Propensity-score diagnostics.
- REQ-EST-07: Inverse-probability weighting (stabilized where appropriate).
- REQ-EST-08: Doubly robust estimation for supported static contrasts.
- REQ-EST-09: Transparent subgroup effect estimation.
- REQ-EST-10: Policy value calculation on simulated or held-out episodes.
- REQ-EST-11: Every estimator must expose its estimand and assumptions. Return a common `EstimateResult` object.
- REQ-EST-12: Report uncertainty (bootstrap or large-sample approximation). Distinguish sampling, model, overlap, and assumption uncertainty.

### 2.5 Intervention protocols

- REQ-INT-01: `MONITOR_REASSESS` — monitor and reassess.
- REQ-INT-02: `NOC_REMOTE` — NOC reroute, failover, rollback, or remote repair.
- REQ-INT-03: `SOC_CONTAIN` — security triage, enrichment, isolation, containment.
- REQ-INT-04: `L2_INVESTIGATE` — Back Office specialist investigation.
- REQ-INT-05: `L3_PRODUCT` — Product Development and Lifecycle escalation.
- REQ-INT-06: `FIELD_REPAIR` — safe on-site inspection, repair, replacement.
- REQ-INT-07: `COORDINATED_RESPONSE` — pre-defined SOC/NOC or NOC/L2 bundle.
- REQ-INT-08: Eligibility rules must be enforced. Not all routes are available for all cases.
- REQ-INT-09: Primary V1 contrast: early coordinated response vs. standard triage and delayed reassessment.

### 2.6 Outcomes

- REQ-OUT-01: `time_to_containment`
- REQ-OUT-02: `time_to_service_restoration`
- REQ-OUT-03: `customer_impact_minutes`
- REQ-OUT-04: `sla_breach` (boolean)
- REQ-OUT-05: `total_operational_cost`
- REQ-OUT-06: `recurrence_30d` (boolean)
- REQ-OUT-07: Each lesson must select one primary outcome and state its scale, units, follow-up, and censoring rule.

### 2.7 Policy and allocation

- REQ-POL-01: Compare at least: current-practice, severity-only, predictive-risk, causal-effect, value-per-resource, and oracle policies.
- REQ-POL-02: Allocator must respect: NOC/SOC/L1/L2/L3/Field capacity, skill/permission/certification requirements, field access and safety conditions, security eligibility, budget, max concurrent changes, queue/backlog limits, SLA priorities, minimum critical-service coverage, fallback rules.
- REQ-POL-03: Allocator must never recommend an action that violates a hard safety or security constraint.
- REQ-POL-04: Evaluate policies on held-out simulated episodes. Report positivity warning if action is outside observed support.

### 2.8 Visualizations (required)

- REQ-VIZ-01: Incident timeline (disturbance, detection, triage, interventions, state changes, outcomes).
- REQ-VIZ-02: DAG with highlighted causal and non-causal paths.
- REQ-VIZ-03: Baseline covariate balance before and after adjustment.
- REQ-VIZ-04: Treatment propensity and overlap plots.
- REQ-VIZ-05: IPW weight distribution and effective sample size.
- REQ-VIZ-06: Naive vs. adjusted estimate vs. known ground truth.
- REQ-VIZ-07: Subgroup-effect forest or dot plot.
- REQ-VIZ-08: Counterfactual outcome distribution for selected interventions.
- REQ-VIZ-09: Policy-value comparison with uncertainty.
- REQ-VIZ-10: Capacity and constraint dashboard.
- REQ-VIZ-11: Policy trade-off frontier (impact, cost, risk).
- REQ-VIZ-12: Explicit warning panel for violated assumptions.
- REQ-VIZ-13: Analysis card on every result view (question, estimand, population, time zero, treatment, outcome, estimator, adjustment set, assumptions, diagnostics, estimate, interpretation, limitations, provenance).

### 2.9 Safety and ethics

- REQ-ETH-01: Use only synthetic data. No real credentials, vulnerabilities, attack procedures, or exploit details.
- REQ-ETH-02: Describe cyber events at an abstract operational level only.
- REQ-ETH-03: All results must be clearly labeled as synthetic and illustrative.
- REQ-ETH-04: Show uncertainty and limitations alongside every recommendation.

## 3. Non-functional requirements

- REQ-NFR-01: Python 3.11+, Streamlit, Plotly, pandas, numpy, scipy, statsmodels, scikit-learn, DoWhy, EconML, pydantic, pytest, graphviz. R and Rust are explicitly excluded from V1.
- REQ-NFR-02: Dependency versions pinned in lock file and tested in CI.
- REQ-NFR-03: Reproducible from a clean environment using documented commands.
- REQ-NFR-04: Full test suite runnable with `pytest`.
- REQ-NFR-05: Default time scales: 15-min decision step, 24-hour response horizon, 30-day recurrence follow-up, 30-day portfolio simulation.

## 5. Source and methodology policy

- REQ-SRC-01: Primary methodological source is Hernán & Robins, *Causal Inference: What If*. It is the backbone for potential outcomes, causal contrasts, exchangeability, positivity, consistency, standardization/g-computation, IPW, and target-trial thinking.
- REQ-SRC-02: Pearl (*Causality*) and Cunningham (*The Mixtape*) are supplementary sources for DAGs, structural causal models, and intuition. They supplement *What If*; they do not replace its estimand-first framing.
- REQ-SRC-03: VanderWeele (*Explanation in Causal Inference*) is a deferred specialist source reserved for mediation and interaction work in later releases. Not required for V1.
- REQ-SRC-04: DoWhy, EconML, statsmodels, and scikit-learn are implementation references, not methodological authorities. Using a library does not establish causal identification.
- REQ-SRC-05: Streamlit and Plotly documentation are engineering references only.
- REQ-SRC-06: `rlvr-enterprise-allocator` is an educational architecture reference for organizing a project around one coherent operational use case. Not a causal-inference source.
- REQ-SRC-07: Every causal result must be introduced through a causal question, estimand, target-trial specification, identification assumptions, and diagnostics before a library estimator is selected.
- REQ-SRC-08: The simulator's structural DGP and known ground truth are the primary validation oracle. Package output is not treated as proof of correctness.
- REQ-SRC-09: The project must clearly distinguish between a method being implemented, demonstrated conceptually, and deferred to a later release.
- REQ-SRC-10: Public documentation must not claim that all listed books were read in full when only a webpage, excerpt, or bibliographic record was available.
- REQ-SRC-11: For every chapter and module, the repository must identify: relevant source and section, causal question and estimand, identification assumptions, whether implementation is educational or library-based, simulator ground truth and validation test, and any material difference between textbook method and software implementation.

## 4. Explicitly out of scope for V1

- Instrumental variables, causal survival, mediation, time-varying treatment, marginal structural models, g-estimation.
- A second complete industry adapter.
- R or Rust implementation.
- Real-time integration with OSS/BSS, ITSM, SIEM, NMS, or field-service systems.
- Production deployment or autonomous incident response.
