# Causal Foundations — V0 Specification

## 1. Document status

**Project:** Causal Resilience Platform

**Module:** Causal Foundations (V0)

**Status:** Implementation baseline

**Audience:** Beginners and practitioners who understand basic data analysis but do not yet have a reliable mental model of causal inference.

**Primary source:** Hernán and Robins, *Causal Inference: What If*, Chapters 1–3, with selected conceptual support from Chapter 6.

**Relationship to V1:** V0 is a small, standalone foundations module that will later become the first course section of the V1 Telecom Causal Resilience reference implementation.

## 2. Purpose

V0 teaches the minimum conceptual and practical workflow required to interpret a causal estimate responsibly:

```text
causal question
→ intervention and comparator
→ outcome and population
→ potential outcomes
→ estimand
→ identification assumptions
→ estimator
→ diagnostics
→ uncertainty and limitations
```

The module uses one simple telecom-flavored incident-response scenario so that the learner can focus on causal reasoning rather than operational complexity.

V0 is intentionally not a miniature version of the whole platform. It is a learning gate before the dynamic telecom incident-response system is implemented.

## 3. Design principles

1. **Teach one causal question deeply.** Do not introduce multiple operational decisions before the learner understands one binary contrast.
2. **Define the intervention before choosing an estimator.** A library call is never a substitute for a causal question or an identification argument.
3. **Separate truth, data, and assumptions.** The simulator knows the truth; the learner must estimate from the observed data.
4. **Use visual explanations before mathematical detail.** Every important result has a chart, an interpretation, and an assumptions panel.
5. **Show warnings instead of false precision.** Positivity problems, unsupported adjustments, and unknown confounding must be visible.
6. **Preserve the V1 mental model without importing V1 complexity.** V0 has a compatible conceptual architecture but does not implement V1’s dynamic policy engine.
7. **Make the learning loop repeatable.** A learner can change one assumption, rerun the analysis, and see what changed.

## 4. V0 learning outcomes

After completing V0, a learner should be able to:

1. Distinguish prediction, association, and causation.
2. State a causal question using a population, intervention, comparator, outcome, time zero, and follow-up period.
3. Explain potential outcomes and why both potential outcomes are not observed for the same episode.
4. Define an average treatment effect and interpret its sign and units.
5. Distinguish an estimand, an estimator, and an estimate.
6. Explain why randomization supports exchangeability.
7. Recognize confounding as a common cause of treatment and outcome.
8. Read a simple DAG containing a confounder.
9. Explain why a crude observational comparison may be biased.
10. Use stratification or standardization to adjust for a measured baseline confounder.
11. Explain the intuition behind inverse-probability weighting.
12. Interpret propensity overlap and effective sample size.
13. State the practical meaning of exchangeability, positivity, consistency, and no interference in this scenario.
14. Recognize that adjustment cannot repair unmeasured confounding or an ill-defined intervention.
15. Explain why a result from synthetic data is an educational demonstration, not evidence about real telecom operations.

## 5. Canonical V0 scenario

### 5.1 Scenario statement

A telecom service incident is detected at time zero. An operations team can either initiate an early, predefined coordinated response or monitor the incident and reassess later.

The V0 question is:

> Among eligible synthetic telecom incidents at detection, what is the average effect of assigning an early coordinated response rather than monitor-and-reassess on customer-impact minutes during the following 24 hours?

### 5.2 Binary intervention contrast

The treatment variable is binary and must have exactly two well-defined versions:

| Value | Name | Definition |
|---|---|---|
| `1` | `EARLY_COORDINATED_RESPONSE` | Within the first 15 minutes after detection, execute the predefined coordination protocol: a NOC/SOC triage handoff, initial containment or service-stabilization action, and a documented reassessment checkpoint. |
| `0` | `MONITOR_REASSESS` | Do not execute the coordinated protocol during the first 60 minutes; monitor the incident, record observations, and reassess at the scheduled checkpoint. |

V0 does not estimate separate effects for NOC, SOC, L1, L2, L3, or Field Operations. Those roles remain part of the V1 operational world.

The treatment definition is deliberately abstract and defensive. It does not contain attack procedures, vulnerabilities, credentials, or operational security instructions.

### 5.3 Outcome

The primary outcome is:

`customer_impact_minutes_24h`

Definition: the total number of customer-impact minutes accumulated by the incident during the 24 hours after detection.

* Type: continuous, non-negative.
* Lower values are better.
* Time zero: incident detection.
* Follow-up: 24 hours.
* In V0, the outcome is fully observed and there is no censoring.

Secondary descriptive quantities may be shown, such as a binary indicator for exceeding an illustrative SLA threshold, but no secondary quantity is a required causal estimand in V0.

### 5.4 Population

The target population is the set of synthetic, eligible incident episodes generated under the selected scenario configuration.

Eligibility is intentionally simple:

* one incident episode per unit;
* incident is observed at detection;
* baseline severity is available before treatment;
* both intervention strategies are conceptually feasible;
* 24-hour outcome is observed.

### 5.5 Unit of analysis

The unit is one incident episode. Episodes are independent in V0.

The V0 no-interference assumption means that the outcome for one episode does not depend on the treatment assigned to another episode. Shared team capacity and incident-to-incident spillovers are deferred to V1.

## 6. Target-trial specification

V0 must show the following target-trial card before presenting any causal estimate.

| Component | V0 definition |
|---|---|
| Eligibility | Eligible synthetic incidents at detection with observed baseline severity |
| Time zero | First reliable detection timestamp |
| Intervention | `EARLY_COORDINATED_RESPONSE` |
| Comparator | `MONITOR_REASSESS` |
| Assignment | Randomized or observational, depending on the selected DGP scenario |
| Follow-up | From detection through 24 hours |
| Outcome | `customer_impact_minutes_24h` |
| Censoring | None in V0; complete outcome observation is assumed |
| Causal contrast | Population average treatment effect on the mean difference scale |
| Target estimand | `E[Y(1) - Y(0)]` |

The interface must distinguish the target trial from the data-generating scenario. A randomized scenario is a teaching design; an observational scenario is a teaching approximation that requires assumptions.

## 7. Causal notation and interpretation

For incident episode `i`:

* `A_i = 1` means the episode received `EARLY_COORDINATED_RESPONSE`.
* `A_i = 0` means the episode received `MONITOR_REASSESS`.
* `Y_i(1)` is the customer-impact outcome that would occur under early coordinated response.
* `Y_i(0)` is the customer-impact outcome that would occur under monitor-and-reassess.
* `Y_i = Y_i(A_i)` is the observed outcome.

The individual causal effect is:

```text
Y_i(1) - Y_i(0)
```

The primary V0 estimand is the average treatment effect:

```text
ATE = E[Y(1)] - E[Y(0)] = E[Y(1) - Y(0)]
```

Because lower customer-impact minutes are better, a negative ATE indicates that early coordinated response reduces average customer impact.

V0 must explicitly teach that the individual causal effect is generally not identifiable because only one potential outcome is observed for each episode. The simulator’s hidden oracle is available only for validation and teaching mode.

## 8. Data-generating process

### 8.1 Baseline variables

The minimal V0 DGP contains:

| Variable | Role | Definition |
|---|---|---|
| `episode_id` | Identifier | Stable synthetic episode identifier |
| `severity` | Baseline confounder | Continuous incident severity measured in `[0, 1]` before treatment |
| `disturbance_type` | Descriptive context | One of a small set of abstract incident categories; not required for adjustment in V0 |
| `treatment` | Exposure | Binary intervention assignment `A` |
| `outcome` | Observed outcome | `customer_impact_minutes_24h` |
| `propensity_true` | Teaching-only field | True probability of treatment assignment; hidden in normal mode |
| `potential_outcome_0` | Oracle-only field | `Y(0)`; hidden in normal mode |
| `potential_outcome_1` | Oracle-only field | `Y(1)`; hidden in normal mode |
| `provenance` | Audit metadata | Seed, scenario, generator version, and schema version |

`severity` is the only required adjustment covariate in V0. This restriction is intentional: the learner should understand one confounding path before working with a high-dimensional feature set.

### 8.2 Structural relationships

The baseline DAG is:

```text
severity ───────> treatment
    │                │
    └──────────────> outcome

 treatment ───────> outcome
```

Interpretation:

* more severe incidents are more likely to receive early coordinated response;
* more severe incidents tend to have more customer impact regardless of treatment;
* early coordinated response changes the outcome.

### 8.3 Potential-outcome generation

The generator must create potential outcomes before assigning the observed treatment. A recommended transparent implementation is:

```text
severity ~ Uniform(0, 1)

baseline_impact = 100 + 240 × severity + outcome_noise_0
potential_outcome_0 = max(0, baseline_impact)
potential_outcome_1 = max(0, baseline_impact - treatment_effect + outcome_noise_delta)
observed_outcome = potential_outcome_treatment
```

The exact coefficients are configurable, but the following properties are mandatory:

* severity increases expected customer impact under both interventions;
* early coordinated response has a configurable average effect;
* potential outcomes are generated before observed treatment assignment;
* the observed outcome is selected by the assigned treatment;
* the oracle can calculate the finite-sample ATE from the generated potential outcomes.

The generator must document whether the treatment effect is constant or heterogeneous. V0 defaults to a constant treatment effect to avoid introducing effect modification too early. A simple optional heterogeneity demonstration may be added only after the core lessons pass their acceptance gate.

### 8.4 Treatment assignment modes

V0 supports three assignment modes:

#### Randomized assignment

```text
P(A = 1 | severity) = 0.5
```

Randomization is the primary introductory scenario. The crude difference in observed means estimates the ATE up to sampling variability.

#### Confounded observational assignment

```text
P(A = 1 | severity) = logistic(intercept + strength × (severity - 0.5))
```

Higher-severity incidents are more likely to receive early coordinated response. In this scenario, the crude difference is generally not a causal estimate because severity is associated with both treatment and outcome.

#### Limited-overlap assignment

Treatment probabilities are pushed toward 0 or 1 for parts of the severity range. The dataset must retain the true propensity for teaching diagnostics, but normal analysis may use only the observed or estimated propensity.

The interface must label limited overlap as a support problem, not as proof of a treatment effect.

### 8.5 Disturbance types

V0 may include the following abstract labels:

* equipment failure;
* software regression;
* misconfiguration;
* overload;
* weather-related disruption;
* cyber disruption;
* physical disruption.

These labels provide telecom context but do not introduce separate treatment policies, attack mechanics, or causal estimands. Cyber and physical disruption are event types only.

## 9. Identification assumptions

V0 teaches assumptions in plain language first and notation second.

### 9.1 Consistency

The intervention versions are sufficiently well-defined, and the observed outcome for an episode receiving treatment `a` equals that episode’s potential outcome under `a`:

```text
A = a  ⇒  Y = Y(a)
```

In practical V0 terms, all episodes coded as `EARLY_COORDINATED_RESPONSE` are treated as receiving the same protocol for purposes of the causal question.

### 9.2 Exchangeability

In the randomized scenario, treatment assignment is independent of the potential outcomes by design.

In the observational scenario, V0 assumes conditional exchangeability given measured severity:

```text
Y(a) ⟂ A | severity
```

The UI must state that this assumption cannot be proven from the observed data alone. It is supported only by the DGP design in the teaching simulator.

### 9.3 Positivity

For every severity level represented in the target population, there must be a positive probability of receiving either intervention:

```text
0 < P(A = a | severity = l) < 1
```

V0 must show empirical overlap and warn when the observed data do not support both treatments across the target severity range.

### 9.4 No interference

One incident’s treatment does not change another incident’s potential outcome. This is a V0 simplification and is explicitly removed in the V1 resource-constrained simulator.

### 9.5 Complete follow-up

The 24-hour outcome is observed for every eligible episode. Missing outcomes, censoring, and informative observation processes are out of scope for V0.

## 10. Estimands, estimators, and estimates

The application must teach the distinction explicitly:

* **Estimand:** the population quantity the analysis is trying to learn.
* **Estimator:** the rule or algorithm used to calculate an estimate from data.
* **Estimate:** the numerical result produced for the current sample.

### 10.1 Required V0 estimands

1. Population ATE on the mean-difference scale.
2. Finite-sample oracle ATE for teaching-mode comparison only.
3. Standardized mean under `A = 1`.
4. Standardized mean under `A = 0`.

The primary result is:

```text
ATE = standardized_mean(A=1) - standardized_mean(A=0)
```

### 10.2 Required estimators

#### A. Difference in means

```text
mean(Y | A = 1) - mean(Y | A = 0)
```

Interpretation:

* causal in the randomized scenario under the stated trial conditions, subject to sampling variability;
* an associational comparison in the confounded observational scenario unless exchangeability is justified without adjustment;
* not a causal estimate merely because the number is statistically precise.

#### B. Stratified adjustment

Partition severity into a small number of pre-treatment strata, calculate the within-stratum treatment contrast, and average the contrasts using the target population’s severity distribution.

This is the most transparent adjustment method and should be the first adjustment learner sees.

#### C. Outcome regression and standardization

Fit an outcome model using treatment and baseline severity, predict each episode’s outcome under both treatment values, and average predictions over the target population.

V0 should use a simple, interpretable model such as linear regression or a generalized linear model. The application must display the model form and warn that model misspecification can bias results.

#### D. Inverse-probability weighting

Fit a treatment-assignment model for `P(A = 1 | severity)`, assign each episode the inverse probability of the treatment actually received, and compare weighted outcome means.

The UI must show:

* estimated propensity scores;
* overlap by treatment group;
* weight distribution;
* effective sample size;
* whether extreme weights are present.

V0 does not require stabilized weights, cross-fitting, doubly robust estimation, or machine-learning propensity models. Those belong to V1 or later.

### 10.3 Uncertainty

V0 must report uncertainty for sample-based estimates, preferably using a reproducible nonparametric bootstrap. The interface should display:

* point estimate;
* 95% bootstrap interval;
* sample size by treatment group;
* a plain-language note that the interval reflects sampling variability, not unmeasured-confounding uncertainty.

The oracle comparison must not be presented as a confidence interval.

## 11. Course mode

Course mode is a guided sequence of six short lessons. Each lesson contains:

1. a learning objective;
2. a short explanation;
3. one interactive visual;
4. one estimate or diagnostic;
5. a “what changed?” interpretation;
6. a knowledge check or reflection prompt;
7. a link to the relevant source chapter.

### Lesson 1 — Ask a causal question

Teach population, intervention, comparator, outcome, time zero, follow-up, and unit of analysis.

Visuals:

* target-trial card;
* timeline from detection to 24-hour outcome;
* treatment-definition comparison.

Learner outcome: write the V0 causal question without using vague terms such as “the effect of resilience.”

### Lesson 2 — Potential outcomes and the missing counterfactual

Show a small set of synthetic episodes with hidden `Y(1)` and `Y(0)` values in teaching mode. Reveal that the observed dataset contains only one potential outcome per episode.

Visuals:

* two-world potential-outcome table;
* observed-versus-missing counterfactual markers;
* individual effect illustration.

Learner outcome: explain why individual causal effects are generally not directly observed.

### Lesson 3 — Randomization: when association can identify causation

Use randomized treatment assignment and compare:

* observed mean under treatment;
* observed mean under comparator;
* oracle mean under treatment;
* oracle mean under comparator;
* estimated ATE;
* oracle ATE.

Visuals:

* treatment-group outcome distributions;
* estimate versus oracle interval chart;
* randomization balance chart.

Learner outcome: explain why randomization supports exchangeability and why finite samples still vary.

### Lesson 4 — Confounding and the DAG

Switch to severity-driven observational assignment. Show that severity affects both treatment assignment and outcome.

Visuals:

* animated or highlighted DAG;
* severity distributions by treatment group;
* crude comparison versus oracle ATE.

Learner outcome: explain why a higher outcome in the treated group does not necessarily mean the treatment caused harm.

### Lesson 5 — Adjustment: stratification, standardization, and IPW

Introduce one adjustment idea at a time:

1. compare treated and untreated within severity strata;
2. standardize stratum-specific predictions to the target population;
3. use inverse-probability weights to create a pseudo-population with balanced severity.

Visuals:

* before/after severity balance;
* standardized prediction chart;
* propensity overlap plot;
* IPW weight distribution.

Learner outcome: understand that different estimators target the same ATE under the same identification assumptions, but can behave differently under model error and poor overlap.

### Lesson 6 — Diagnostics, uncertainty, and responsible interpretation

Show good overlap, limited overlap, stronger confounding, and smaller sample size.

Visuals:

* estimator comparison with uncertainty;
* overlap warning;
* effective sample size;
* assumption checklist;
* final analysis card.

Learner outcome: state whether the result is supported, fragile, or not interpretable as a causal effect under the selected scenario.

## 12. Experimental sandbox

The sandbox is separate from Course mode and permits controlled experimentation.

### 12.1 Required controls

* random seed;
* sample size;
* assignment mode: randomized or confounded;
* confounding strength;
* treatment effect magnitude;
* outcome noise;
* overlap mode: adequate or limited;
* estimator selection;
* teaching-mode oracle visibility.

The sandbox must avoid exposing more than one conceptual change at a time through default presets. A “reset to lesson defaults” control is required.

### 12.2 Required sandbox outputs

* current scenario summary;
* target-trial card;
* DAG;
* estimate and uncertainty;
* oracle comparison in teaching mode;
* overlap and weight diagnostics;
* assumption warnings;
* reproducibility metadata.

## 13. Visual design requirements

The application must use Plotly for interactive charts.

Required V0 visuals:

1. target-trial timeline;
2. two-world potential-outcome illustration;
3. treatment/outcome distribution chart;
4. DAG with highlighted backdoor path;
5. baseline severity balance chart;
6. crude versus adjusted versus oracle estimate chart;
7. propensity overlap chart;
8. IPW weight distribution;
9. effective sample-size indicator;
10. assumption-warning panel;
11. analysis card.

Accessibility requirements:

* color must never be the only encoding;
* treatment groups must also use labels, symbols, or line styles;
* charts must have descriptive titles and axis units;
* warnings must include text and an icon or symbol;
* the palette must be suitable for common color-vision deficiencies;
* every chart must remain understandable in a static screenshot.

## 14. Analysis card

Every estimate view must show an analysis card containing:

* causal question;
* target population;
* time zero;
* intervention;
* comparator;
* outcome and units;
* follow-up period;
* estimand;
* estimator;
* adjustment variables;
* identification assumptions;
* diagnostics;
* point estimate and uncertainty;
* oracle comparison, when teaching mode is enabled;
* plain-language interpretation;
* limitations;
* provenance.

Example interpretation:

> Under the randomized synthetic scenario, early coordinated response reduced average customer-impact minutes over 24 hours by approximately 38 minutes in this sample. This estimate is illustrative, depends on the simulated protocol and outcome definition, and does not establish an effect in real telecom operations.

## 15. Provenance and reproducibility

Every generated dataset and estimate must carry:

* seed;
* scenario identifier;
* generator version;
* schema version;
* configuration values;
* estimator name and version;
* bootstrap seed, when applicable;
* code revision when available;
* creation timestamp;
* whether oracle fields were used.

The same seed, configuration, generator version, and schema version must reproduce the same generated data and deterministic results.

Normal user mode must not expose `potential_outcome_0`, `potential_outcome_1`, or `propensity_true` as ordinary analysis inputs. Teaching mode may show them with explicit “oracle / simulator truth” labeling.

## 16. Recommended Python architecture

V0 should live inside the future V1 package rather than becoming a separate repository:

```text
src/causal_resilience/
├── foundations/
│   ├── __init__.py
│   ├── schemas.py
│   ├── dgp.py
│   ├── estimators.py
│   ├── diagnostics.py
│   ├── provenance.py
│   └── lessons.py
├── visualization.py
└── app_support.py

course/
└── v0/
    ├── 01_causal_question.md
    ├── 02_potential_outcomes.md
    ├── 03_randomization.md
    ├── 04_confounding.md
    ├── 05_adjustment.md
    └── 06_diagnostics.md

tests/
├── foundations/
│   ├── test_dgp.py
│   ├── test_estimators.py
│   ├── test_diagnostics.py
│   └── test_reproducibility.py
└── test_app_smoke.py
```

### 16.1 Dependencies

Required V0 dependencies:

* Python 3.11 or newer;
* `numpy`;
* `pandas`;
* `scipy`;
* `statsmodels`;
* `scikit-learn`;
* `plotly`;
* `streamlit`;
* `pydantic`;
* `pytest`.

DoWhy and EconML are not required for V0. V0 should make the causal logic transparent with small, inspectable implementations. DoWhy and EconML can be introduced in V1 after the learner understands the estimand and assumptions.

Rust and R are excluded from V0.

### 16.2 Core contracts

```python
class FoundationsScenario(Protocol):
    def generate(self, config: ScenarioConfig) -> FoundationsDataset: ...
    def truth(self, dataset: FoundationsDataset) -> GroundTruth: ...

class CausalEstimator(Protocol):
    name: str
    def estimate(
        self,
        dataset: FoundationsDataset,
        estimand: Estimand,
        config: EstimatorConfig,
    ) -> EstimateResult: ...
```

`EstimateResult` must include:

```python
EstimateResult(
    estimand_name: str,
    estimator_name: str,
    estimate: float,
    confidence_interval: tuple[float, float] | None,
    standard_error: float | None,
    sample_size: int,
    treatment_counts: dict[str, int],
    assumptions: list[str],
    diagnostics: list[Diagnostic],
    warnings: list[str],
    oracle_comparison: OracleComparison | None,
    provenance: Provenance,
)
```

## 17. Testing strategy

### 17.1 Data-generating process tests

* same configuration and seed produce identical data;
* potential outcomes exist in teaching mode;
* observed outcome equals the potential outcome corresponding to observed treatment;
* severity is measured before treatment;
* treatment assignment follows the selected mode;
* oracle ATE equals the mean of generated potential-outcome differences;
* normal mode does not expose oracle fields as analysis variables;
* outcome units and ranges are valid.

### 17.2 Estimator tests

* randomized difference in means approaches the oracle ATE as sample size increases;
* crude observational difference is visibly biased under configured confounding;
* stratification reduces bias under the correctly specified one-confounder DGP;
* standardization recovers the oracle ATE within a documented Monte Carlo tolerance under the correctly specified model;
* IPW recovers the oracle ATE within a documented Monte Carlo tolerance under adequate overlap and a correctly specified propensity model;
* estimator outputs expose the correct estimand and assumptions;
* bootstrap results are reproducible when the bootstrap seed is fixed.

### 17.3 Diagnostic tests

* overlap warning fires when propensity support is inadequate;
* extreme-weight warning fires when IPW weights exceed the configured threshold;
* effective sample size decreases as weights become more concentrated;
* balance diagnostics identify the severity imbalance before adjustment;
* balance diagnostics improve after correctly specified adjustment in the confounded scenario;
* the application does not claim that an adjusted estimate is valid when exchangeability is deliberately violated by an unmeasured factor scenario, if that optional scenario is enabled.

### 17.4 UI tests

* the app starts with `streamlit run app.py`;
* Course mode opens on Lesson 1;
* navigation preserves seed and scenario configuration;
* Sandbox reset restores defaults;
* oracle values are labeled and hidden in normal mode;
* every result view contains an analysis card;
* warnings are rendered as text and not only as color;
* all required charts render with a small dataset.

## 18. V0 acceptance criteria

V0 is complete only when all criteria below are satisfied:

1. A clean Python environment can install the project from the documented dependency file.
2. `pytest` passes for the complete V0 test suite.
3. `streamlit run app.py` starts without an exception.
4. The application presents the V0 causal question before showing an estimate.
5. The intervention and comparator are described precisely and consistently in code, UI, and lessons.
6. The primary outcome is `customer_impact_minutes_24h` with units and a 24-hour follow-up period.
7. The dataset contains one row or object per independent incident episode.
8. The structural generator creates potential outcomes before observed treatment assignment.
9. The observed outcome follows the consistency rule in the simulator.
10. Teaching mode can display the oracle ATE with explicit labeling.
11. Normal mode does not use oracle fields to calculate an estimator.
12. Randomized assignment produces a difference-in-means estimate that approaches the oracle ATE as sample size grows.
13. Confounded assignment creates a visible severity imbalance and a difference between crude association and oracle ATE.
14. The baseline DAG correctly shows severity as a common cause of treatment and outcome.
15. At least one transparent adjustment method is implemented and explained.
16. Standardization is implemented for the one-confounder DGP.
17. IPW is implemented for the one-confounder DGP.
18. Propensity overlap and IPW weight diagnostics are visible.
19. Positivity and extreme-weight warnings are visible when the selected scenario violates practical support.
20. Bootstrap uncertainty is reproducible and clearly distinguished from assumption uncertainty.
21. Course mode contains six runnable lessons with objectives, visuals, interpretation, and source references.
22. Sandbox mode exposes only the documented controls and provides a reset function.
23. Every estimate view contains a complete analysis card.
24. Provenance is attached to datasets and estimates.
25. Charts use accessible encodings and remain interpretable without color alone.
26. Cyber and physical disruption labels, if enabled, remain abstract and contain no offensive or procedural content.
27. Documentation states that all data are synthetic and illustrative.
28. Documentation clearly lists V0 limitations and deferred V1 capabilities.
29. No code requires Rust, R, DoWhy, or EconML for V0 to run.
30. The V0 implementation can later be wrapped by the V1 domain-adapter architecture without changing the meaning of the V0 estimand.

## 19. Explicitly out of scope for V0

The following must not be implemented as V0 requirements:

* NOC, SOC, L1, L2, L3, and Field Operations as separate treatment options;
* seven-action intervention allocation;
* queueing, shared capacity, budget, or resource constraints;
* dynamic state transitions or sequential treatment decisions;
* policy learning or policy-value optimization;
* causal heterogeneity or CATE as a required lesson;
* doubly robust estimation or cross-fitting;
* instrumental variables;
* survival analysis or censoring adjustment;
* mediation analysis;
* time-varying treatments or longitudinal g-methods;
* interference estimation;
* real telecom data or operational-system integration;
* autonomous incident response;
* production claims or operational recommendations;
* R validation layer;
* Rust implementation;
* a second industry adapter.

## 20. Relationship to V1

V0 provides the conceptual and software foundation for V1:

| V0 | V1 extension |
|---|---|
| One binary intervention contrast | Multiple operational protocols and policy comparisons |
| One baseline confounder | Rich telecom baseline state and DAG |
| Independent episodes | Dynamic incident episodes with state transitions |
| Complete follow-up | Recurrence, censoring, and later survival work |
| No shared resources | Capacity, queue, safety, security, and budget constraints |
| Explicit estimators | DoWhy/EconML integrations after the concepts are understood |
| Teaching oracle | Structural DGP and counterfactual oracle for the telecom adapter |
| Foundations scenario contract | Full `DomainAdapter` contract |

V1 must reuse V0’s definitions of treatment, outcome, estimand, assumptions, estimate result, provenance, and analysis card. V1 may extend them, but must not silently redefine them.

## 21. Implementation plan for Kiro

Kiro must implement V0 in vertical slices. Do not implement the entire V0 specification in one task.

### Slice 1 — Project foundation and schemas

* create or verify the Python package structure;
* implement `ScenarioConfig`, `FoundationsDataset`, `GroundTruth`, `Estimand`, `Diagnostic`, `EstimateResult`, and `Provenance`;
* add dependency and test configuration;
* add schema tests;
* stop and report test results.

Exit gate: schemas validate, imports work, and no UI or estimator code is required yet.

### Slice 2 — Structural DGP and randomized contrast

* implement potential-outcome generation;
* implement randomized treatment assignment;
* implement observed-outcome consistency;
* implement oracle calculation;
* add reproducibility and ground-truth tests;
* add a minimal command-line or test-level demonstration.

Exit gate: randomized difference in means approaches the oracle with a large sample.

### Slice 3 — First course experience

* implement Lesson 1 and Lesson 2 content;
* implement the minimal Streamlit page;
* add target-trial card, potential-outcome visual, and randomized estimate chart;
* add normal-mode oracle hiding and teaching-mode labeling.

Exit gate: a beginner can run the app and understand the causal question and missing counterfactual.

### Slice 4 — Confounding and DAG

* implement severity-driven treatment assignment;
* implement the V0 DAG representation;
* implement crude observational difference;
* implement balance diagnostics;
* add Lessons 3 and 4;
* add the crude-versus-oracle visual.

Exit gate: confounding produces the intended teaching contrast and the app explains why the crude comparison is not automatically causal.

### Slice 5 — Adjustment and diagnostics

* implement stratification;
* implement outcome regression and standardization;
* implement propensity modeling and IPW;
* implement overlap, weight, and effective-sample-size diagnostics;
* add Lesson 5 and Lesson 6;
* add estimator-comparison and warning panels.

Exit gate: correctly specified adjustment recovers the oracle within documented simulation tolerance, and positivity warnings work.

### Slice 6 — Accessibility, documentation, and release gate

* complete all required visualizations;
* apply accessible encodings;
* complete source references, assumptions, data dictionary, and limitations;
* add UI smoke tests;
* run the full acceptance checklist;
* provide screenshots and test output for review.

Exit gate: V0 is approved for pedagogical review before any V1 implementation begins.

## 22. Kiro handoff instruction

Use the following instruction for the first Kiro task:

```text
Implement only V0 Slice 1 from:
.kiro/specs/causal-resilience/v0_specification.md

Do not implement the full V0. Do not implement V1. Do not add dynamic simulation, multi-action allocation, DoWhy, EconML, Rust, or R.

First inspect the existing repository and report any conflicts with the V0 specification. Then implement only the schemas, provenance model, dependency/test configuration, and schema tests required by Slice 1.

Run the relevant tests. Report:
1. files changed;
2. tests executed and results;
3. unresolved design conflicts;
4. any assumptions made.

Stop after Slice 1. Do not proceed to Slice 2 without a review checkpoint.
```

## 23. Sources and methodological policy

### Primary source

* Hernán, Miguel A., and James M. Robins. *Causal Inference: What If*. Use the repository copy of the PDF and cite the relevant chapter or section in each lesson. V0 relies primarily on:
  * Chapter 1: definition of causal effect, potential outcomes, average causal effects, consistency, and association versus causation;
  * Chapter 2: randomization, conditional exchangeability, standardization, and inverse-probability weighting;
  * Chapter 3: identifiability conditions, exchangeability, positivity, consistency, and target trials;
  * Chapter 6: causal diagrams, common causes, paths, and adjustment intuition.

### Supplementary sources

Pearl and Cunningham may be used later for alternative explanations of DAGs and causal intuition, but they are not required for V0 implementation. V0 must preserve the estimand-first and assumptions-first framing of *What If*.

### Library documentation

`statsmodels`, `scikit-learn`, `numpy`, `scipy`, `pandas`, `Plotly`, and `Streamlit` documentation are implementation references only. A library estimator does not establish causal identification.

### Source header requirement

Each causal module and each lesson must identify:

* relevant source chapter or section;
* causal question and estimand;
* assumptions;
* whether the implementation is educational, library-based, or both;
* the ground-truth validation test;
* any material difference between the textbook method and the software implementation.

## 24. Final V0 decision

V0 is a beginner-first causal inference foundations module with one clearly specified binary intervention and one continuous outcome. It is deliberately smaller than V1, but it is not disposable: it becomes the first course section, the first estimator testbed, and the conceptual contract that V1 must preserve.
