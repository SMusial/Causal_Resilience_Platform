# Requirements — Causal Resilience Intervention Allocator (V1, Reconciled)

## 1. Purpose

Build an educational causal-inference platform around a synthetic telecom incident-response world. It must teach prediction versus causation, potential outcomes, estimands and estimators, identification assumptions, basic adjustment methods, policy evaluation, and constrained operational simulation.

## 2. Scope rules

* V1 causal estimation is static and anchored at `time_zero`.
* The primary contrast is binary: `COORDINATED_RESPONSE` versus `MONITOR_REASSESS`.
* Seven protocols are available to the simulation and policy layers; V1 does not claim a fully identified seven-action observational causal effect.
* `customer_impact_minutes_24h` is the primary causal outcome.
* `sla_breach_24h` is the secondary causal outcome.
* Time-to-containment and time-to-restoration are descriptive/simulation metrics only.
* Cyberattack and vandalism are synthetic disturbances, never treatments.
* V1 is Python-only; no R, Rust, real system integration, autonomous response, or second industry adapter.

## 3. User experience

* REQ-UX-01: Provide Course mode with 13 guided lessons.
* REQ-UX-02: Provide Experimental Sandbox mode.
* REQ-UX-03: Preserve scenario configuration while navigating lessons.
* REQ-UX-04: Every result view must show an analysis card and assumption warnings where relevant.

## 4. Course curriculum

* REQ-CUR-01: Explain causal effects through potential outcomes and counterfactual incident trajectories.
* REQ-CUR-02: Demonstrate randomized assignment and empirical difference in means.
* REQ-CUR-03: Demonstrate severity-driven observational assignment and naive bias.
* REQ-CUR-04: Teach exchangeability, positivity, and consistency through controlled DGP switches.
* REQ-CUR-05: Show a DAG, backdoor paths, valid adjustment, and collider bias.
* REQ-CUR-06: Demonstrate selection and measurement error as controlled failure scenarios.
* REQ-CUR-07: Demonstrate effect modification by disturbance, severity, criticality, and security risk without claiming mediation.
* REQ-CUR-08: Implement outcome regression and standardization/g-formula.
* REQ-CUR-09: Implement propensity diagnostics and IPW.
* REQ-CUR-10: Implement doubly robust estimation for supported static contrasts.
* REQ-CUR-11: Demonstrate transparent subgroup effects/CATE with warnings about support and model dependence.
* REQ-CUR-12: Compare causal-effect targeting with risk targeting using policy simulation and explicit labeling.
* REQ-CUR-13: Produce an audit/limitations lesson with target trial, estimand, assumptions, diagnostics, uncertainty, and provenance.

## 5. Structural simulator

* REQ-DGP-01: Generate episodes from explicit structural mechanisms, not an arbitrary random table.
* REQ-DGP-02: Support equipment failure, software regression, misconfiguration, overload, weather disruption, cyberattack, and vandalism.
* REQ-DGP-03: Include L1/Front Office, NOC, SOC, L2/Back Office, L3/Product Development and Lifecycle, and Field Operations.
* REQ-DGP-04: Support randomized assignment and controlled confounding by severity, confounding by indication, latent readiness, and limited overlap.
* REQ-DGP-05: Support measurement error, selection, missingness, treatment-version mismatch, post-treatment variables, changing workload, and concurrent episodes as warnings/demonstrations. V1 does not implement longitudinal causal estimators for these scenarios.
* REQ-DGP-06: Same seed, scenario, generator version, and schema version must reproduce identical results.
* REQ-DGP-07: Ground truth must be inaccessible to ordinary estimators and visible only in explicit teaching/test mode.

## 6. Causal estimators and diagnostics

* REQ-EST-01: Randomized difference in means.
* REQ-EST-02: Crude observational difference in means.
* REQ-EST-03: Stratified adjustment.
* REQ-EST-04: Outcome regression.
* REQ-EST-05: Standardization/parametric g-formula for supported baseline contrasts.
* REQ-EST-06: Propensity model diagnostics.
* REQ-EST-07: IPW, with stabilized weights when justified.
* REQ-EST-08: Doubly robust estimation for supported static contrasts.
* REQ-EST-09: Subgroup effect/CATE demonstration with diagnostics.
* REQ-EST-10: Policy value calculation for explicitly defined simulated or held-out policies.
* REQ-EST-11: Every estimator exposes its estimand, assumptions, diagnostics, and provenance through a common result object.
* REQ-EST-12: Report uncertainty and distinguish sampling uncertainty from model, overlap, and assumption limitations.

## 7. Operational protocols

* REQ-INT-01: Implement `MONITOR_REASSESS`.
* REQ-INT-02: Implement `NOC_REMOTE`.
* REQ-INT-03: Implement `SOC_CONTAIN`.
* REQ-INT-04: Implement `L2_INVESTIGATE`.
* REQ-INT-05: Implement `L3_PRODUCT`.
* REQ-INT-06: Implement `FIELD_REPAIR`.
* REQ-INT-07: Implement `COORDINATED_RESPONSE` as a fixed, documented bundle.
* REQ-INT-08: Enforce eligibility and hard safety/security rules.
* REQ-INT-09: Use the binary primary contrast for causal estimation; use all protocols for simulation/policy demonstration.

## 8. Outcomes

* REQ-OUT-01: Generate `customer_impact_minutes_24h` as the primary causal outcome.
* REQ-OUT-02: Generate `sla_breach_24h` as the secondary causal outcome.
* REQ-OUT-03: Generate time-to-containment and time-to-restoration for descriptive timelines and simulation.
* REQ-OUT-04: Generate cost and 30-day recurrence for simulation/descriptive policy views.
* REQ-OUT-05: Every causal result states unit, scale, follow-up, and censoring rule.
* REQ-OUT-06: No V1 survival estimand or survival-specific inference is implied by time-to-event fields.

## 9. Policy and allocation

* REQ-POL-01: Compare current-practice, severity-only, predictive-risk, causal-effect, value-per-resource, and teaching-only oracle policies.
* REQ-POL-02: Enforce capacity, permissions, certification, field access/safety, security eligibility, budget, concurrent-change, backlog, SLA, critical-service, and fallback constraints.
* REQ-POL-03: Never recommend an action that violates a hard safety or security constraint.
* REQ-POL-04: Evaluate policies on held-out simulated episodes and label results as policy simulation/value.
* REQ-POL-05: Warn when a policy selects actions outside supported observed treatment support.
* REQ-POL-06: Report infeasible allocations explicitly rather than silently relaxing hard constraints.

## 10. Visualization

* REQ-VIZ-01: Incident timeline.
* REQ-VIZ-02: DAG with causal, non-causal, and post-treatment paths distinguished.
* REQ-VIZ-03: Covariate balance before/after adjustment.
* REQ-VIZ-04: Propensity and overlap plots.
* REQ-VIZ-05: Weight distribution and effective sample size.
* REQ-VIZ-06: Naive, adjusted, and ground-truth comparison where teaching mode permits.
* REQ-VIZ-07: Subgroup effect plot.
* REQ-VIZ-08: Simulated counterfactual outcome distributions.
* REQ-VIZ-09: Policy-value comparison with uncertainty or Monte Carlo error.
* REQ-VIZ-10: Capacity and constraint dashboard.
* REQ-VIZ-11: Impact/cost/risk trade-off frontier.
* REQ-VIZ-12: Explicit assumption-warning panel.
* REQ-VIZ-13: Analysis card on every result view.
* REQ-VIZ-14: Plotly is required; Graphviz is optional.
* REQ-VIZ-15: All visuals remain interpretable without relying on color alone.

## 11. Ethics and safety

* REQ-ETH-01: Use synthetic data only.
* REQ-ETH-02: Keep cyber and vandalism scenarios at an abstract operational level.
* REQ-ETH-03: Label all results synthetic and illustrative.
* REQ-ETH-04: Show uncertainty and limitations with recommendations.
* REQ-ETH-05: Do not implement autonomous actions or live-system integrations.

## 12. Non-functional requirements

* REQ-NFR-01: Python 3.11+ with pinned dependencies: Streamlit, Plotly, pandas or Polars, NumPy, SciPy, statsmodels, scikit-learn, DoWhy, EconML, Pydantic, pytest.
* REQ-NFR-02: R and Rust are excluded from V1.
* REQ-NFR-03: Clean-environment installation and documented run commands.
* REQ-NFR-04: Full pytest suite.
* REQ-NFR-05: Reproducible seeds, scenario identifiers, generator version, schema version, and provenance.
* REQ-NFR-06: Default step 15 minutes, primary follow-up 24 hours, recurrence 30 days, portfolio simulation 30 days.

## 13. Source and methodology policy

* REQ-SRC-01: *Causal Inference: What If* is the primary methodological source.
* REQ-SRC-02: Pearl and Cunningham are supplementary; they do not replace estimand-first reasoning.
* REQ-SRC-03: VanderWeele is deferred to post-V1 mediation/interaction work.
* REQ-SRC-04: DoWhy, EconML, statsmodels, and scikit-learn are implementation references, not proof of identification.
* REQ-SRC-05: Streamlit and Plotly are engineering references.
* REQ-SRC-06: `rlvr-enterprise-allocator` is an educational architecture reference only.
* REQ-SRC-07: Every causal result follows question → estimand → target trial → assumptions → diagnostics → estimator.
* REQ-SRC-08: Structural DGP ground truth is the primary validation oracle.
* REQ-SRC-09: Documentation distinguishes implemented, conceptually demonstrated, and deferred methods.
* REQ-SRC-10: Documentation does not claim full access to sources that were only partially available.
* REQ-SRC-11: Every module documents source section, estimand, assumptions, implementation type, validation, and textbook/software differences.

## 14. Out of scope

* Instrumental variables.
* Causal survival analysis.
* Mediation analysis.
* Time-varying treatment and treatment-confounder feedback.
* Marginal structural models and g-estimation.
* A second complete industry adapter.
* R or Rust implementation.
* Real OSS/BSS, ITSM, SIEM, NMS, or field-service integrations.
* Production deployment or autonomous incident response.

## 15. Release acceptance

The authoritative criteria are stored in `docs/v1_release_acceptance.md` and must contain 26 explicit checks.
