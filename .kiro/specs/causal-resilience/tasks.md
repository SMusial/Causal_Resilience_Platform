# Tasks — Causal Resilience Intervention Allocator (V1)

Implementation follows five phases. Complete each phase before starting the next. Each task is independently runnable or testable.

---

## Phase 1 — Small runnable slice

- [ ] **TASK-01** Set up Python project: `pyproject.toml`, lock file (`uv` or `pip-tools`), `.gitignore`, `README.md` skeleton.
- [ ] **TASK-02** Create `src/causal_resilience/__init__.py` and package structure matching the design.
- [ ] **TASK-03** Implement `schemas.py`: `CaseState`, `Episode`, `Action`, `OutcomeSet`, `Provenance`, `ScenarioConfig` using pydantic.
- [ ] **TASK-04** Implement `provenance.py`: seed, scenario id, generator version, schema version, code revision, timestamp.
- [ ] **TASK-05** Implement `simulation/structural_model.py`: one telecom incident generator, one randomized binary contrast (`COORDINATED_RESPONSE` vs. `STANDARD_REASSESS`), one primary outcome (`customer_impact_minutes`), counterfactual oracle hidden behind a flag.
- [ ] **TASK-06** Implement `simulation/generator.py`: entry point that calls the structural model and returns a `CaseDataset`.
- [ ] **TASK-07** Write `tests/test_generator_ground_truth.py`: verify randomized DiM approaches known effect at large N.
- [ ] **TASK-08** Implement `causal/baselines.py`: randomized difference in means returning `EstimateResult`.
- [ ] **TASK-09** Implement `schemas.py` addition: `EstimateResult`, `Estimand`, `Diagnostic`, `GroundTruthComparison`.
- [ ] **TASK-10** Create minimal `app.py` Streamlit page: load dataset, show one estimate, one ground-truth comparison chart.
- [ ] **TASK-11** Implement `visualization.py`: one Plotly helper for naive vs. adjusted vs. ground truth bar chart.

**Phase 1 exit criterion:** `streamlit run app.py` shows a working page with a randomized estimate and ground-truth comparison.

---

## Phase 2 — Core causal curriculum

- [ ] **TASK-12** Implement `simulation/structural_model.py` extension: observational (severity-driven) treatment assignment with configurable confounding strength.
- [ ] **TASK-13** Implement `causal/dag.py`: DAG definition, backdoor path enumeration, adjustment-set validation, collider detection.
- [ ] **TASK-14** Implement `causal/estimands.py`: `TargetTrial`, `EligibilityRule`, `TimeZeroRule`, `TreatmentStrategy`, `OutcomeDefinition`, `FollowUpDefinition`, `CensoringDefinition`, `Assumption`.
- [ ] **TASK-15** Implement `causal/identification.py`: exchangeability, positivity, consistency, temporal-ordering checks; return warnings not errors.
- [ ] **TASK-16** Implement `causal/diagnostics.py`: covariate balance (SMD), overlap check, positivity warning.
- [ ] **TASK-17** Implement `causal/baselines.py` extension: crude observational DiM, stratified adjustment.
- [ ] **TASK-18** Implement `causal/standardization.py`: outcome regression (statsmodels GLM) + g-formula standardization over target covariate distribution.
- [ ] **TASK-19** Implement `causal/ipw.py`: propensity model (scikit-learn logistic), IPW, stabilized weights, effective sample size.
- [ ] **TASK-20** Write `tests/test_identification.py`: collider adjustment creates bias, valid adjustment set reduces bias, absent overlap triggers warning.
- [ ] **TASK-21** Write `tests/test_static_estimators.py`: standardization and IPW agree within tolerance on randomized scenario; repeated-seed benchmark.
- [ ] **TASK-22** Write `tests/test_diagnostics.py`: balance improves after IPW weighting; positivity warning fires when overlap is absent.
- [ ] **TASK-23** Add course-mode lessons 1–5 to `app.py` (tabs or pages), each with target-trial card, DAG view, and estimate panel.
- [ ] **TASK-24** Implement `visualization.py` additions: DAG chart (Plotly or graphviz), covariate balance chart, propensity overlap plot, IPW weight distribution.

**Phase 2 exit criterion:** Lessons 1–5 run end-to-end; naive vs. adjusted comparison is visibly different under confounding.

---

## Phase 3 — Dynamic telecom realism

- [ ] **TASK-25** Implement `simulation/transitions.py`: full state-transition model for all disturbance types (equipment failure, software regression, misconfiguration, overload, weather, cyberattack, vandalism).
- [ ] **TASK-26** Implement `domain/adapter.py`: `DomainAdapter` Protocol with all methods from the design.
- [ ] **TASK-27** Implement `domain/telecom_resilience.py`: telecom adapter — all six roles, all seven intervention protocols, eligibility rules, telecom-specific outcomes and constraints.
- [ ] **TASK-28** Implement `simulation/structural_model.py` extension: full bias and failure scenario support (measurement error, missingness, informative censoring, selection, treatment-version mismatch, post-treatment variables, concurrent episodes with interference warning).
- [ ] **TASK-29** Implement `simulation/policies.py`: policy execution loop over state transitions, queue and capacity model, shared resource tracking.
- [ ] **TASK-30** Implement `policy/constraints.py`: capacity, skill/permission/certification, field access and safety, security eligibility, budget, max concurrent changes, queue/backlog limits, SLA priorities, fallback rules.
- [ ] **TASK-31** Write `tests/test_adapter_contract.py`: domain-neutral contract tests — schema validity, deterministic generation, valid time ordering, valid action/outcome types, feasible-action behavior, constraint behavior, target-trial availability, explanation and provenance fields.
- [ ] **TASK-32** Add sandbox controls to `app.py`: seed, sample size, disturbance mix, confounding strength, overlap mode, measurement error, missingness, censoring, capacity, policy objective weights, estimator and adjustment set.
- [ ] **TASK-33** Implement `visualization.py` additions: incident timeline chart, capacity and constraint dashboard.
- [ ] **TASK-34** Add course-mode lessons 6–9 to `app.py`.

**Phase 3 exit criterion:** Full episode timeline renders; cyberattack and vandalism scenarios run without offensive content; all six roles appear in the domain model.

---

## Phase 4 — Doubly robust and policy layer

- [ ] **TASK-35** Implement `causal/doubly_robust.py`: DR estimator, cross-fitting where appropriate, behavior under one misspecified nuisance model.
- [ ] **TASK-36** Implement `causal/heterogeneity.py`: subgroup effect estimation, CATE via EconML (DR learner or causal forest), counterfactual outcome distribution.
- [ ] **TASK-37** Implement `policy/value.py`: policy value V(π) on held-out episodes, positivity warning for out-of-support actions, oracle policy in teaching mode only.
- [ ] **TASK-38** Implement `policy/allocator.py`: constrained intervention allocator — maximize objective, respect all hard constraints, never violate safety or security constraints, report infeasibility explicitly.
- [ ] **TASK-39** Implement `explanations.py`: analysis card builder, reason codes, audit export with full provenance.
- [ ] **TASK-40** Write `tests/test_policy_value.py`: policy value agrees with oracle simulation within documented Monte Carlo error; positivity warning fires for out-of-support actions.
- [ ] **TASK-41** Write `tests/test_allocator.py`: allocator never exceeds capacity or budget; never dispatches Field Operations when safety fails; never assigns SOC to ineligible incident; never uses oracle in normal mode.
- [ ] **TASK-42** Add course-mode lessons 10–13 to `app.py`.
- [ ] **TASK-43** Implement `visualization.py` additions: subgroup-effect forest/dot plot, counterfactual outcome distribution, policy-value comparison, policy trade-off frontier, assumption warning panel.

**Phase 4 exit criterion:** All 13 lessons run; DR estimator, policy allocator, and analysis card are functional; allocator safety tests pass.

---

## Phase 5 — Public-release hardening

- [ ] **TASK-44** Write `tests/test_schemas.py`: schema validation, required fields, pydantic contract.
- [ ] **TASK-45** Write `tests/test_reproducibility.py`: same config produces identical dataset and results; provenance fields are complete.
- [ ] **TASK-46** Write deliberate bias tests in `tests/test_static_estimators.py`: naive comparison biased under confounding by indication; collider adjustment increases bias; measurement error changes result in controlled direction; selection and censoring scenarios differ from complete-data scenario.
- [ ] **TASK-47** Write temporal safety tests in `tests/test_generator_ground_truth.py`: state histories are ordered; future outcomes cannot leak into baseline covariates; every executed action was feasible at execution time; post-treatment variables are not silently included in baseline adjustment.
- [ ] **TASK-48** Complete `docs/data_dictionary.md`, `docs/assumptions.md`, `docs/limitations.md`, `docs/causal_questions.md`, `docs/visualization_guide.md`.
- [ ] **TASK-49** Complete `README.md`: use case, educational purpose, synthetic-data limitation, install commands, `streamlit run app.py`, `pytest`, dataset regeneration, chart reproduction, estimator benchmark, policy-allocation demo.
- [ ] **TASK-50** Accessibility review: every chart uses labels/symbols/annotations in addition to color; color-blind palette check.
- [ ] **TASK-51** Clean-environment CI: install from lock file, run full test suite, verify `streamlit run app.py` starts without error.
- [ ] **TASK-52** Final check against V1 release acceptance criteria (spec section 26): all 26 criteria must be met before tagging the release.

**Phase 5 exit criterion:** All tests pass in a clean environment; README is complete; all 26 release acceptance criteria are satisfied.

---

## Deferred (post-V1)

- Instrumental variables
- Causal survival analysis and censoring-weighted survival estimands
- Causal mediation (VanderWeele source reserved for this)
- Time-varying treatment and treatment-confounder feedback
- Marginal structural models, g-estimation
- Second industry adapter
- R-based validation

---

## Source documentation tasks (per module)

For each implemented module, add a source header block identifying:

- Relevant source and section (e.g., *What If* Chapter 2)
- Causal question and estimand being taught
- Identification assumptions required
- Whether implementation is educational, library-based, or both
- Simulator ground truth and validation test reference
- Any material difference between textbook method and software implementation

- [ ] **TASK-53** Add source header to `causal/baselines.py` (*What If* Ch. 1–2)
- [ ] **TASK-54** Add source header to `causal/standardization.py` (*What If* Ch. 13)
- [ ] **TASK-55** Add source header to `causal/ipw.py` (*What If* Ch. 12)
- [ ] **TASK-56** Add source header to `causal/doubly_robust.py` (*What If* Ch. 13 + EconML DR learner)
- [ ] **TASK-57** Add source header to `causal/heterogeneity.py` (*What If* Ch. 5 + EconML CATE)
- [ ] **TASK-58** Add source header to `causal/dag.py` (Pearl *Causality* Ch. 1–3, supplementary)
- [ ] **TASK-59** Add source header to `policy/value.py` (*What If* Ch. 4 + EconML policy)
- [ ] **TASK-60** Add source header to `policy/allocator.py` (domain constraints, no causal-inference source claim)
- [ ] **TASK-61** Update `docs/limitations.md` to explicitly state: which books were fully available vs. bibliographic references only; which methods are implemented vs. conceptually demonstrated vs. deferred.
