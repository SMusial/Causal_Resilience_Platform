# Tasks — Causal Resilience Intervention Allocator (V1, Reconciled)

V1 implementation starts only after V0 has passed its pedagogical quality gate. Complete each phase before starting the next. Do not implement all tasks in one Kiro request.

## Phase 1 — Foundation and randomized slice

* [ ] TASK-01: Set up Python project, pinned dependencies, pytest, and README skeleton.
* [ ] TASK-02: Create package structure and configuration.
* [ ] TASK-03: Implement Pydantic schemas for baseline covariates, state, incident episode, binary treatment, outcomes, provenance, estimand, diagnostic, and estimate result.
* [ ] TASK-04: Implement deterministic provenance with seed, scenario id, generator version, schema version, and code revision.
* [ ] TASK-05: Implement one structural telecom incident generator with a randomized binary contrast and `customer_impact_minutes_24h`.
* [ ] TASK-06: Implement a hidden ground-truth oracle available only in teaching/test mode.
* [ ] TASK-07: Test that randomized difference in means approaches known ATE as sample size grows.
* [ ] TASK-08: Implement randomized difference in means and crude difference in means through the common result object.
* [ ] TASK-09: Build the first Streamlit page with one estimate, uncertainty, and ground-truth comparison.
* [ ] TASK-10: Add the first Plotly estimate comparison.

Exit: the app runs and displays a correct randomized estimate with clear estimand language.

## Phase 2 — Identification and foundational estimators

* [ ] TASK-11: Add severity-driven confounded treatment assignment.
* [ ] TASK-12: Implement the baseline DAG and distinguish baseline variables, treatment, mediators, and outcomes.
* [ ] TASK-13: Implement target-trial and estimand objects for the primary binary contrast.
* [ ] TASK-14: Implement exchangeability, positivity, consistency, and temporal-ordering checks as warnings/diagnostics.
* [ ] TASK-15: Implement covariate balance, overlap, and positivity diagnostics.
* [ ] TASK-16: Implement stratified adjustment.
* [ ] TASK-17: Implement outcome regression and standardization/g-formula.
* [ ] TASK-18: Implement propensity modelling and IPW with effective sample size.
* [ ] TASK-19: Add repeated-seed tests comparing estimators with known ground truth.
* [ ] TASK-20: Add collider, limited-overlap, and invalid-adjustment tests.
* [ ] TASK-21: Add course lessons for potential outcomes, randomization, confounding, assumptions, and DAGs.
* [ ] TASK-22: Add Plotly DAG, balance, overlap, and weight visualizations.

Exit: under confounding, the UI visibly distinguishes naive from adjusted estimates and warns when assumptions/overlap fail.

## Phase 3 — Telecom dynamic world and adapter contract

* [ ] TASK-23: Implement transition functions for all supported disturbance types.
* [ ] TASK-24: Implement the `DomainAdapter` protocol.
* [ ] TASK-25: Implement the telecom adapter with six roles and seven operational protocols.
* [ ] TASK-26: Implement explicit eligibility rules and hard safety/security constraints.
* [ ] TASK-27: Implement policy execution with state transitions, queues, capacity, and resource tracking.
* [ ] TASK-28: Add controlled measurement error, selection, missingness, treatment-version mismatch, post-treatment variables, and concurrent-episode warning scenarios. Do not add longitudinal causal estimators.
* [ ] TASK-29: Add adapter contract tests for deterministic generation, valid time ordering, feasible actions, target-trial availability, explanations, and provenance.
* [ ] TASK-30: Add sandbox controls for seed, sample size, disturbance mix, confounding, overlap, measurement error, missingness, capacity, and policy weights.
* [ ] TASK-31: Add incident timeline and capacity/constraint visualizations.
* [ ] TASK-32: Add course lessons for selection, measurement error, and effect modification.

Exit: full telecom episodes render, all roles appear, disturbance scenarios remain safe and abstract, and contract tests pass.

## Phase 4 — Heterogeneity, policy simulation, and explanations

* [ ] TASK-33: Implement doubly robust estimation for supported static contrasts; document cross-fitting limitations.
* [ ] TASK-34: Implement subgroup effects/CATE with support diagnostics and model-dependence warnings.
* [ ] TASK-35: Implement policy value for explicitly defined simulated/held-out policies.
* [ ] TASK-36: Implement constrained allocator over operational protocols; enforce hard constraints and report infeasibility.
* [ ] TASK-37: Add current-practice, severity-only, predictive-risk, causal-effect, value-per-resource, and teaching-only oracle policies.
* [ ] TASK-38: Implement analysis cards, reason codes, audit export, and provenance display.
* [ ] TASK-39: Add lessons for outcome regression, IPW, doubly robust estimation, heterogeneity, policy value, and audit/limitations.
* [ ] TASK-40: Add subgroup, simulated counterfactual, policy-value, trade-off, and assumption-warning visualizations.
* [ ] TASK-41: Test policy support warnings, Monte Carlo error, capacity, budget, safety, security, and oracle isolation.

Exit: all 13 lessons run and every policy result is clearly labelled as causal estimation, policy value, or structural simulation.

## Phase 5 — Hardening and public release

* [ ] TASK-42: Add schema validation tests.
* [ ] TASK-43: Add reproducibility tests.
* [ ] TASK-44: Add deliberate-bias tests for naive confounding, collider adjustment, measurement error, and selection/missingness demonstrations.
* [ ] TASK-45: Add temporal leakage tests; ensure future outcomes and post-treatment variables do not enter baseline adjustment silently.
* [ ] TASK-46: Complete data dictionary, causal questions, assumptions, limitations, and visualization guide.
* [ ] TASK-47: Complete README with educational purpose, synthetic-data limitation, installation, course, sandbox, tests, and reproducibility.
* [ ] TASK-48: Perform accessibility and color-blind review.
* [ ] TASK-49: Add clean-environment CI and Streamlit startup check.
* [ ] TASK-50: Create `docs/v1_release_acceptance.md` with exactly 26 explicit criteria.
* [ ] TASK-51: Add source header blocks to causal modules and document textbook/software differences.
* [ ] TASK-52: Perform final methodological review against the reconciled requirements and design.

Exit: all 26 acceptance criteria pass, tests pass in a clean environment, and the release documentation does not overclaim methods or source access.

## Deferred after V1

Instrumental variables, causal survival, mediation, time-varying treatment, treatment-confounder feedback, marginal structural models, g-estimation, a second industry adapter, R validation, and Rust implementation.

## Kiro execution rule

Execute one vertical slice at a time. For each slice, return the changed files, tests run, test output summary, screenshots or visual notes, assumptions introduced, and any unresolved methodological question. Do not begin the next slice until the previous exit criterion is reviewed.
