# Causal Resilience Intervention Allocator

## V1 Public Release Specification

**Document status:** Implementation-ready V1 specification  
**Release target:** First public GitHub release  
**Primary language:** English  
**Implementation language:** Python  
**Reference domain:** Telecom incident response  
**Primary purpose:** Learn causal inference through one realistic, dynamic operational decision problem  
**Cross-domain strategy:** A complete telecom adapter in V1 plus a formal domain-adapter contract for future industries

## 1. Executive summary

`Causal Resilience Intervention Allocator` is an educational causal-inference laboratory and decision-intelligence demonstration.

The project studies a practical question:

> For a service-affecting incident, what would the outcome have been if the organization had applied intervention A instead of a feasible alternative B at the defined decision time?

The reference scenario is a telecom incident that may involve network degradation, software or configuration failure, cyberattack, vandalism, environmental disruption, or a combination of these events. The response may involve the Front Office (L1), NOC, Security Operations Center (SOC), Back Office (L2), Product Development and Lifecycle (L3), and Field Operations.

The system will not merely predict which incidents are risky. It will teach the difference between:

* predicting an outcome;
* estimating the effect of an intervention;
* simulating counterfactual trajectories;
* evaluating a policy;
* allocating scarce operational capacity.

V1 will contain a realistic dynamic simulator, but its primary causal estimators will focus on a clearly defined decision point and static or baseline treatment contrasts. This separation is deliberate. A dynamic operational environment is valuable for intuition and policy simulation, but valid estimation of time-varying treatment effects requires additional methods that will be implemented in later releases.

The project will provide two user experiences:

* **Course mode:** a guided sequence of lessons based on the same incident-response case.
* **Experimental sandbox:** a free-form interface for changing data-generating assumptions, treatment assignment, overlap, capacity, and policy rules.

The project will be Python-first. It will use mature Python libraries where they improve reliability or learning value, while retaining transparent educational implementations for the core methods. Rust and R are explicitly outside the required V1 architecture.

## 2. Goals and non-goals

### 2.1 Goals

V1 must:

* teach the core causal-inference discipline described in *Causal Inference: What If*;
* make the causal question, estimand, population, treatment, comparator, outcome, time zero, follow-up, and assumptions explicit;
* use a single coherent telecom use case rather than a collection of unrelated examples;
* represent realistic incident dynamics, escalation, delayed recovery, shared capacity, and repeat incidents;
* include cyberattacks and vandalism as disturbance events that change the state and influence operational decisions;
* include L1, NOC, SOC, L2, L3, and Field Operations in the domain model;
* show confounding by indication, where the most severe cases receive more intensive interventions;
* show positivity problems, measurement error, selection, missingness, and treatment-version inconsistency;
* provide a structural data-generating process with known causal ground truth;
* implement and compare foundational causal estimators;
* explain assumptions and diagnostics visually and in plain language;
* demonstrate policy evaluation and constrained intervention allocation;
* prove architectural cross-domain readiness through a formal `DomainAdapter` contract;
* be reproducible, testable, safe to run, and credible as a public portfolio project.

### 2.2 Non-goals

V1 is not:

* a production network-management system;
* an automated cyber-defense or security-response tool;
* an operational change-execution platform;
* a replacement for a NOC, SOC, service desk, or field-dispatch process;
* a claim about the effectiveness of real telecom interventions;
* a complete implementation of every method in *What If*;
* a general-purpose causal-inference framework for arbitrary data;
* a second fully implemented industry adapter;
* a real-world safety, security, compliance, or reliability certification.

No real customer, employee, network, security, or incident data is required for V1. The public repository must clearly label all results as synthetic and illustrative.

## 3. Methodological foundation

### 3.1 Primary source

The educational spine is Miguel A. Hernán and James M. Robins, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook).

The project adopts the book’s central discipline:

1. State the causal question before looking for an estimator.
2. Define the intervention and the counterfactual outcome.
3. Separate identification assumptions from statistical estimation.
4. Use data and subject-matter knowledge together.
5. Make exchangeability, positivity, and consistency explicit.
6. Treat target-trial design as a practical way to specify an observational analysis.
7. Avoid interpreting a predictive model as a causal analysis merely because it produces a useful score.

V1 covers the foundations needed for these principles. It will use selected topics from Parts I and II of the book, including causal effects, randomized experiments, observational studies, effect modification, causal diagrams, confounding, selection bias, measurement bias, random variability, outcome regression, standardization, propensity scores, inverse-probability weighting, doubly robust estimation, and target-trial thinking.

### 3.2 Supplementary references

One book should be the primary syllabus for V1, but it should not be the only source consulted over the life of the project. *What If* itself explains that no single book can be a complete and permanently current survey of a large and rapidly developing field.

The following references are supplementary rather than competing syllabi:

* Judea Pearl, [*Causality*](https://bayes.cs.ucla.edu/BOOK-2K/), for structural causal models, DAGs, and do-calculus.
* Scott Cunningham, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/), for intuition and selected econometric methods.
* Tyler VanderWeele, [*Explanation in Causal Inference*](https://global.oup.com/academic/product/explanation-in-causal-inference-9780199325870), for interaction and mediation in later releases.
* The official documentation for [DoWhy](https://www.pywhy.org/dowhy/), [EconML](https://econml.azurewebsites.net/), [statsmodels](https://www.statsmodels.org/), and [scikit-learn](https://scikit-learn.org/).

The project must not turn reading every supplementary source into a prerequisite for using the repository. The intended learning loop is: read the relevant concept, implement or run the lesson, change the data-generating assumptions, and inspect what changes.

## 4. Reference use case

### 4.1 Business setting

A telecom operator detects a service-affecting incident. The incident may affect a mobile site, transport link, access network, core-network component, enterprise service, cloud-hosted network function, or supporting facility.

The organization must select a response under uncertainty and operational constraints. Possible actions differ in:

* time to start;
* probability of containment;
* expected time to restoration;
* cost;
* skill requirements;
* security and safety requirements;
* risk of causing a secondary incident;
* effect on other active incidents because resources are shared;
* ability to prevent recurrence.

The operational record is not a randomized experiment. Severe incidents are more likely to be escalated, to receive multiple teams, to occur during high-load periods, and to have poor outcomes even with excellent response. A naive comparison can therefore conclude that an intensive intervention is harmful when it was preferentially assigned to difficult cases.

This is the project’s central example of confounding by indication.

### 4.2 Organizational roles

The first release uses the following roles:

| Role | Meaning in V1 | Typical responsibility |
|---|---|---|
| L1 / Front Office | Initial customer-facing or service-desk response | Intake, classification, communication, basic diagnostics, SLA control |
| NOC | Network Operations Center | Network diagnosis, rerouting, failover, rollback, remote remediation |
| SOC | Security Operations Center | Security triage, enrichment, containment, isolation, residual-risk assessment |
| L2 / Back Office | Specialist technical support | Deeper investigation, correlation, remediation planning, coordination |
| L3 | Product Development and Lifecycle | Product defect analysis, engineering decision, durable product or lifecycle fix |
| Field Operations | On-site technical response | Physical inspection, safe repair, replacement, restoration of facilities or equipment |

The term SOC always means **Security Operations Center** in this project. A service-coordination function, if introduced in a future version, must use a different name.

### 4.3 Why this is a cross-domain use case in principle

The cross-domain abstraction is not the organizational labels. It is the decision pattern:

> A case or asset is degrading; several interventions are possible; the effect depends on the current state and available resources; the organization must choose an action under uncertainty and constraints.

The same abstraction can later describe:

* manufacturing equipment reliability;
* cloud and IT service incidents;
* utilities restoration;
* transportation and fleet reliability;
* facilities and data-center operations.

V1 will not implement those domains. It will demonstrate transferability by keeping the causal engine and adapter contract domain-neutral while giving telecom its own state model, interventions, DAGs, simulator, outcomes, and constraints.

## 5. V1 scope

### 5.1 Included

V1 includes:

* one telecom incident-response reference scenario;
* many synthetic incident episodes generated by one structural data-generating process;
* disturbance types including equipment failure, software regression, misconfiguration, overload, weather-related disruption, cyberattack, and vandalism;
* standardized L1 intake and triage;
* NOC, SOC, L2, L3, and Field Operations pathways;
* baseline intervention assignment at a documented decision point;
* dynamic state transitions and operational event history;
* delayed response and recovery;
* recurrence within a follow-up window;
* shared team capacity and queue pressure in simulation;
* a controlled randomized benchmark;
* observational scenarios with known confounding;
* deliberate positivity, measurement, selection, missingness, and treatment-version failure scenarios;
* causal graphs and backdoor-adjustment demonstrations;
* outcome regression and standardization/g-computation;
* propensity-score diagnostics and inverse-probability weighting;
* doubly robust estimation for supported static contrasts;
* transparent heterogeneous-effect analysis;
* static policy value and holdout evaluation;
* capacity- and safety-aware intervention allocation;
* course mode and experimental sandbox;
* colorful, accessible, explanatory visualizations;
* Python library integration where it improves quality;
* formal `DomainAdapter` and contract tests;
* reproducibility metadata, test suites, and limitations documentation.

### 5.2 Explicitly deferred

The following are planned, but not required for V1:

* instrumental-variable estimation;
* causal survival analysis and censoring-weighted survival estimands;
* causal mediation;
* time-varying treatment estimands;
* treatment-confounder feedback and full longitudinal g-methods;
* marginal structural models;
* g-estimation of structural nested models;
* full off-policy evaluation for adaptive treatment regimes;
* interference-aware causal estimands for network-level spillovers;
* a second complete industry adapter;
* R-based validation;
* Rust implementation;
* online learning or production deployment;
* real-time integration with OSS/BSS, ITSM, SIEM, NMS, or field-service systems.

V1 may display these topics in the roadmap, but must not present a placeholder calculation as a valid implementation.

## 6. Core design principles

### 6.1 One case, many lessons

All lessons should reuse the same recognizable incident-response world. The scenario may change its seed, disturbance, confounding strength, or assignment mechanism, but the user should always understand what operational decision is being studied.

### 6.2 Dynamic simulation does not automatically mean dynamic causal estimation

The simulator must be dynamic because real incidents evolve. The primary V1 estimands will nevertheless be defined at a baseline decision point. Later actions can be recorded as part of the trajectory and policy simulation, but V1 will not claim to estimate the causal effect of an adaptive sequence unless the required longitudinal assumptions and methods are implemented.

### 6.3 Ground truth is a teaching instrument, not a real-world claim

The generator will know counterfactual outcomes because it creates them structurally. This makes it possible to measure bias, variance, coverage, and policy regret. It does not make the synthetic assumptions true in an actual operator.

### 6.4 A warning is better than a false number

If the selected contrast is not supported by declared assumptions or available overlap, the application must show an identification warning. It must not hide the problem behind a precise estimate.

### 6.5 Separate four layers

The implementation must distinguish:

* **state prediction:** what may happen next;
* **causal estimation:** what would change under an intervention;
* **simulation:** how a policy plays out under a transition model;
* **allocation:** which feasible action should be selected given resources and constraints.

## 7. Unit of analysis and episode structure

### 7.1 Primary unit: `incident_episode`

The primary unit is an `incident_episode`: one service-affecting case observed from a defined `time_zero` through the end of follow-up or censoring.

An episode contains:

* baseline eligibility and covariates;
* disturbance information;
* the initial observed state;
* the treatment decision at the V1 decision point;
* subsequent state and action history;
* outcomes and censoring indicators;
* provenance and scenario metadata;
* hidden ground truth in test or teaching mode only.

Alarms, tickets, actions, technician visits, queue events, and communications are events within an episode, not automatically separate causal units.

### 7.2 Time zero and decision time

The default `time_zero` is the first reliable detection of a service-affecting incident, before the response pathway is selected. Ticket creation, later escalation, or the first field visit must not silently replace time zero.

The default V1 treatment decision occurs after a standardized L1 triage window. The lesson must state whether the estimand concerns:

* the action immediately after detection;
* the route selected after L1 triage; or
* a complete response bundle from detection onward.

These are different treatments and must not be mixed.

### 7.3 Interference boundary

The episode-level estimators use an isolated or controlled-population assumption for teaching. The simulator also contains shared capacity, topology, and concurrent incidents to demonstrate that operational policy value may involve interference.

The project must therefore label results as either:

* `episode_level_causal_estimate`; or
* `portfolio_policy_simulation`.

An episode-level ATE must not be described as a complete solution to network-level interference.

## 8. Domain model

### 8.1 Case and asset entities

The minimum domain model contains:

| Entity | Required fields or concepts |
|---|---|
| Incident case | `episode_id`, service, asset, region, time zero, severity, eligibility |
| Service | service class, customer segment, SLA class, criticality |
| Asset | asset type, age, version, health, redundancy, location |
| Topology | dependencies, affected neighbors, redundancy path, criticality |
| Disturbance | type, start time, intensity, detectability, propagation potential |
| State | severity, impact, health, backlog, SLA clock, readiness, observability |
| Action | protocol, version, actor, start time, duration, resources, eligibility |
| Resource | team, skill, capacity, queue, availability, safety/security status |
| Outcome | containment, restoration, impact, SLA, cost, recurrence, residual risk |
| Provenance | seed, scenario, schema version, code version, experiment id |

### 8.2 State vector

A state at time `t` is conceptually:

```text
S_t = {
    service_impact,
    severity,
    affected_customers,
    asset_health,
    fault_probability,
    security_risk,
    topology_criticality,
    redundancy,
    queue_backlog,
    sla_time_remaining,
    team_load,
    weather_and_access,
    prior_actions,
    escalation_history,
    observability_quality,
    operational_readiness
}
```

Some state variables are observed, some are measured with error, and some are partially or deliberately unobserved in bias scenarios. The application must distinguish an observed variable from the latent variable that generated it.

### 8.3 State transitions

The simulator follows the conceptual structure:

```text
S_t, U_t, A_t, E_t -> S_(t+1), Y, C
```

where:

* `S_t` is the observed state;
* `U_t` represents latent or unmeasured factors;
* `A_t` is the action;
* `E_t` is an exogenous disturbance or operational event;
* `S_(t+1)` is the next state;
* `Y` is the outcome set;
* `C` represents censoring or observation status.

Without effective action, the state may deteriorate through increasing customer impact, fault probability, SLA exposure, cost, or escalation pressure. An action may stabilize, improve, or temporarily worsen the state because of delay, side effects, or change risk.

### 8.4 Default time scales

The simulator defaults are:

* decision and observation step: 15 minutes;
* incident-response horizon: 24 hours;
* recurrence follow-up: 30 days;
* portfolio simulation horizon: 30 days.

All horizons are configuration values and must appear in every result card and export.

## 9. Disturbance events

Disturbances are causes or initiating events, not treatments.

### 9.1 Cyberattack

The generator may create abstract synthetic classes such as:

* credential compromise;
* denial-of-service-like disruption;
* malicious or unauthorized configuration change;
* malware-like service disruption;
* lateral-movement indicator.

The model may include:

* attack start time;
* detection delay;
* classification uncertainty;
* affected asset scope;
* propagation risk;
* security-control status;
* requirement for SOC participation;
* restrictions on technically feasible actions.

The project must not generate exploit instructions, operational attack guidance, credentials, or real detection signatures. Cyber events exist to teach causal decision-making under disturbance and response constraints.

### 9.2 Vandalism

The generator may create abstract synthetic classes such as:

* damaged cabinet or site;
* cut cable;
* physical intrusion;
* stolen component;
* damaged power or cooling equipment.

The model may include:

* location and access conditions;
* physical safety risk;
* availability of the site;
* travel time;
* facility or police dependency;
* Field Operations eligibility;
* expected repair duration.

### 9.3 Other disturbances

To avoid treating cyber and vandalism as special standalone projects, V1 also includes:

* equipment failure;
* software regression;
* configuration error;
* overload;
* weather-related disruption;
* dependency failure.

All are levels of `disturbance_type` within the same case model.

## 10. Intervention protocols

An intervention must be a versioned protocol, not a vague label such as “support the incident” or “increase engineering effort.”

### 10.1 Baseline L1 intake

L1 / Front Office performs standardized intake and triage in the reference scenario. The protocol defines:

* classification steps;
* basic diagnostics;
* customer communication;
* priority and SLA handling;
* escalation trigger recording;
* start and completion criteria.

For the primary V1 contrast, L1 is the common starting protocol and the treatment is the response route selected after triage. Other lessons may treat the intake protocol as the intervention.

### 10.2 V1 response routes

| Code | Protocol | Typical eligibility | Primary mechanism |
|---|---|---|---|
| `MONITOR_REASSESS` | Monitor for a fixed interval and reassess | Low immediate impact and sufficient observability | Information gathering with no active change |
| `NOC_REMOTE` | NOC reroute, failover, rollback, or remote repair according to a named runbook | Network or software condition with safe remote action | Fast stabilization or restoration |
| `SOC_CONTAIN` | Security triage, enrichment, isolation, and containment | Cyber-risk or security-relevant disturbance | Limit propagation and residual security risk |
| `L2_INVESTIGATE` | Back Office specialist investigation and remediation plan | Complex technical issue or failed initial response | Improve diagnosis and select remediation |
| `L3_PRODUCT` | Product Development and Lifecycle escalation | Product, version, defect, or lifecycle issue | Durable product-level resolution |
| `FIELD_REPAIR` | Safe on-site inspection, repair, replacement, or facility action | Physical fault and safe site access | Restore physical infrastructure |
| `COORDINATED_RESPONSE` | A pre-defined SOC/NOC or NOC/L2 bundle | Multi-domain incident with explicit coordination rules | Reduce delay caused by hand-offs and conflicting actions |

V1 must not treat all routes as available for all cases. Eligibility rules are part of the causal question and are also a source of positivity violations.

### 10.3 Treatment versions and consistency

Each protocol version defines:

* action steps;
* actor and team;
* required skills and permissions;
* maximum start delay;
* completion criteria;
* allowable fallback;
* expected cost;
* safety and security preconditions;
* possible direct side effects;
* version identifier.

If two teams execute “NOC remote remediation” differently, they must either be represented as distinct treatment versions or excluded from a contrast. A treatment label that combines materially different protocols violates the practical meaning of consistency.

### 10.4 Primary V1 contrast

The primary learning contrast is:

```text
Early coordinated response
versus
standard triage followed by delayed reassessment
```

The eligible population is restricted to incidents where both strategies are defined and feasible under the declared protocol. The primary contrast is intentionally narrower than the full operational action catalogue so that the first lessons have a stable estimand.

Secondary lessons use eligible multi-arm contrasts among `NOC_REMOTE`, `SOC_CONTAIN`, `L2_INVESTIGATE`, `L3_PRODUCT`, and `FIELD_REPAIR`.

## 11. Outcomes

### 11.1 Primary outcomes

V1 supports the following primary outcomes:

* `time_to_containment`: time from time zero to a documented reduction in further deterioration;
* `time_to_service_restoration`: time from time zero to a defined restored-service threshold;
* `customer_impact_minutes`: customer-weighted minutes of degradation or unavailability;
* `sla_breach`: whether the defined SLA threshold is breached;
* `total_operational_cost`: response, engineering, field, change, and downtime cost under the synthetic cost model;
* `recurrence_30d`: whether a related incident recurs within 30 days.

Each lesson must select one primary outcome and state its scale, units, follow-up, and censoring rule.

### 11.2 Secondary outcomes

Secondary outcomes include:

* number of escalations;
* number of transfers between support levels;
* affected services and assets;
* change-induced incident;
* residual security risk;
* personnel safety exposure;
* backlog after response;
* resource utilization;
* customer communication quality;
* total intervention count.

### 11.3 Outcome interpretation

The application must distinguish:

* a lower mean restoration time;
* a lower risk of SLA breach;
* a lower cumulative impact;
* a lower expected cost;
* a higher policy value under a particular objective.

These are different estimands. A single score must not hide which outcome was optimized.

## 12. Target-trial specification

Every main causal lesson begins with a target-trial card.

### 12.1 Target-trial template

The card must specify:

* **Eligibility:** which incident episodes enter the trial;
* **Time zero:** when assignment and follow-up begin;
* **Treatment strategies:** the exact protocol or strategy being compared;
* **Assignment:** randomized, observational, or simulated operational assignment;
* **Follow-up:** the time window for each outcome;
* **Outcome:** the primary and secondary outcomes;
* **Censoring:** how incomplete observation is handled;
* **Causal contrast:** risk difference, mean difference, risk ratio, policy value, or another named contrast;
* **Population:** the target population to which the result applies;
* **Analysis plan:** identification assumptions and estimator;
* **Transport boundary:** which synthetic scenario or domain the result does not cover.

### 12.2 Example target trial

**Question:** What is the effect of early coordinated response versus standard triage and delayed reassessment on customer-impact minutes over 24 hours?

* Eligibility: service-affecting incidents with sufficient baseline observability, a defined route decision after L1 triage, and feasibility of both strategies.
* Time zero: completion of the standardized L1 triage window.
* Treatment: `COORDINATED_RESPONSE` or `STANDARD_REASSESS` according to the named protocol version.
* Outcome: customer-impact minutes during the next 24 hours.
* Secondary outcomes: SLA breach, cost, restoration time, and 30-day recurrence.
* Censoring: episode not observed through the relevant horizon or observation terminated by an explicit censoring event.
* Estimand: average difference in potential customer-impact minutes in the eligible population.
* Assumptions: consistency, positivity, and conditional exchangeability given the declared pre-treatment covariates.

### 12.3 Time-zero validation

The implementation must flag covariates that are recorded after treatment begins. Post-treatment variables may be useful for prediction or explanation of the trajectory, but must not be silently included in a baseline adjustment set.

## 13. Causal graphs and assumptions

### 13.1 Baseline DAG

The reference DAG contains the following conceptual structure:

```text
Disturbance severity ─────┬──> Treatment assignment ───> Outcome
                          ├──> Outcome
                          └──> Escalation need

Topology criticality ─────┬──> Treatment assignment
                          └──> Outcome

Team backlog ─────────────┬──> Treatment assignment
                          └──> Outcome

Operational readiness ────┬──> Treatment assignment
(latent in one scenario)  └──> Outcome

Treatment ────────────────> Containment ────────────> Outcome
```

The graph is a teaching artifact and an analysis declaration. It is not inferred automatically from correlations.

### 13.2 Identification conditions

For each contrast, the application must discuss:

* **Exchangeability:** after conditioning on the declared baseline covariates, there are no unmeasured common causes of treatment and outcome, or the lesson explicitly states that this assumption is violated;
* **Positivity:** every strategy being compared has positive probability for the relevant covariate patterns in the target population;
* **Consistency:** the observed treatment corresponds to the well-defined intervention and the observed outcome equals the potential outcome under the treatment received;
* **Correct temporal ordering:** adjustment variables precede treatment;
* **No hidden transport claim:** the result applies to the declared synthetic population and scenario only.

### 13.3 Adjustment sets

The application must show:

* backdoor paths;
* candidate adjustment variables;
* variables that should not be adjusted for because they are post-treatment;
* colliders that would create bias if conditioned on;
* variables useful for prediction but not necessarily required for identification;
* warnings when the requested adjustment set is not sufficient under the active DAG.

## 14. Structural data-generating process

### 14.1 Requirements

The generator must be a structural simulator, not a random table generator. For each episode it should be possible in test mode to recover:

* latent baseline factors;
* observed baseline covariates;
* treatment-assignment mechanism;
* potential outcomes for supported interventions;
* conditional treatment effects;
* transition parameters;
* missingness and censoring mechanisms;
* policy value under the simulated population;
* the exact scenario configuration.

### 14.2 Counterfactual ground truth

The ground-truth engine will create potential outcomes by evaluating the transition model under alternative interventions while holding the relevant exogenous factors fixed according to the declared simulation design. The oracle is used to measure estimator bias and policy regret.

Ground truth must be:

* hidden from normal user-facing estimates;
* accessible in teaching mode with explicit labeling;
* available to automated tests;
* versioned with the generator;
* never presented as evidence about real telecom operations.

### 14.3 Bias and failure scenarios

The generator must support at least:

* randomized treatment assignment;
* confounding by severity;
* confounding by indication;
* unmeasured operational readiness;
* limited or absent overlap;
* treatment-version mismatch;
* selection into observed episodes;
* measurement error in severity, asset health, and security risk;
* outcome missingness;
* informative censoring;
* changing workload and capacity;
* post-treatment state variables;
* concurrent episodes and a warning about interference.

### 14.4 Reproducibility

A dataset or episode is identified by:

* random seed;
* scenario identifier;
* generator version;
* schema version;
* configuration hash;
* experiment identifier.

The same configuration must produce the same dataset and results within the supported environment.

## 15. V1 causal curriculum

The course is organized around the project’s operational question, not around a list of library APIs.

### Lesson 1: What is a causal effect?

The user compares potential outcomes under two response pathways and sees why individual causal effects are not directly observable.

### Lesson 2: Randomized incident-response experiment

The user activates randomized treatment assignment and compares the empirical difference in means with the known ground truth.

### Lesson 3: Observational incident response

The user turns on severity-driven treatment assignment and observes that the naive comparison is biased.

### Lesson 4: Exchangeability, positivity, and consistency

The user changes the data-generating process so that each assumption is satisfied or violated and sees the diagnostic response.

### Lesson 5: DAGs and confounding

The user inspects the incident DAG, chooses an adjustment set, and observes the consequences of adjusting for a confounder or collider.

### Lesson 6: Selection and measurement bias

The user changes which incidents enter the dataset and how severity is measured, then compares the observed and true effects.

### Lesson 7: Effect modification and interaction

The user examines how the effect of a response route changes by disturbance type, severity, topology criticality, and security risk. Joint-response interaction is shown as a controlled educational extension, not as a general claim about team synergy.

### Lesson 8: Outcome regression and standardization

The user fits an outcome model, standardizes predictions over the target covariate distribution, and separates identification from model fit.

### Lesson 9: Propensity scores and IPW

The user inspects treatment probabilities, overlap, weight distributions, effective sample size, and sensitivity to truncation.

### Lesson 10: Doubly robust estimation

The user compares outcome and treatment nuisance models, cross-fitting where supported, and the behavior of a doubly robust estimator when one nuisance model is misspecified.

### Lesson 11: Causal heterogeneity

The user examines conditional effects and counterfactual risks without treating a noisy individual-level estimate as a certainty.

### Lesson 12: Policy value and constrained allocation

The user compares naive risk ranking with causal benefit ranking under team, budget, safety, and security constraints.

### Lesson 13: Audit and limitations

The user produces an analysis card containing the target trial, estimand, assumptions, diagnostics, uncertainty, limitations, and provenance.

### 15.1 Deferred lessons

Later releases may add:

* instrumental variables;
* causal survival and censoring;
* mediation;
* time-varying treatment and treatment-confounder feedback;
* sequential g-formula, time-varying IPW, marginal structural models, and g-estimation.

These topics must not be simulated as if they were implemented merely because the dynamic simulator contains histories.

## 16. Estimation layer and Python stack

### 16.1 Library strategy

V1 uses a hybrid approach:

* transparent educational implementations for formulas and small examples;
* mature libraries for selected estimators, diagnostics, and cross-checks;
* tests against the structural ground truth;
* no assumption that one package is a universal causal engine.

### 16.2 Required or preferred libraries

| Concern | V1 choice | Purpose |
|---|---|---|
| Array and numerical work | `numpy`, `scipy` | Simulation, optimization, numerical utilities |
| Tabular data | `pandas` and `pyarrow` | Clear data manipulation and Parquet interchange |
| Typed contracts | `pydantic` or typed dataclasses | Schema validation and configuration |
| Transparent statistical models | `statsmodels` | Regression, generalized linear models, interpretable baselines |
| Nuisance models and cross-validation | `scikit-learn` | Propensity and outcome models, preprocessing, cross-fitting utilities |
| Causal identification and refutation | `DoWhy` | Graph-based causal model, identification workflow, refutation hooks |
| Heterogeneous effects and DML | `EconML` | CATE, DML, DR learners, causal forests where appropriate |
| Visualization | `plotly` | Interactive, colorful, browser-friendly charts |
| Application | `streamlit` | Course and sandbox interface |
| DAG display | `graphviz` or a lightweight Plotly renderer | Interactive causal diagrams |
| Testing | `pytest`, `hypothesis` | Unit, property, and contract tests |

Exact package versions must be pinned by the implementation’s lock file and tested in continuous integration. The specification intentionally does not prescribe a future version number.

### 16.3 V1 estimator catalogue

V1 implements or supports:

1. randomized difference in means;
2. crude observational difference in means;
3. stratified adjustment;
4. outcome regression;
5. standardization / parametric g-formula for supported baseline contrasts;
6. propensity-score diagnostics;
7. inverse-probability weighting, including stabilized weights where appropriate;
8. doubly robust estimation for supported static contrasts;
9. transparent subgroup effect estimation;
10. policy value calculation on simulated or held-out episodes.

Each estimator must expose its estimand and assumptions. A library call without an analysis declaration is not sufficient.

### 16.4 Common result object

All estimators return a common result structure:

```python
EstimateResult(
    estimand=Estimand(...),
    population=PopulationDefinition(...),
    estimate=float,
    confidence_interval=(float, float),
    standard_error=float | None,
    method=str,
    assumptions=list[str],
    diagnostics=list[Diagnostic],
    warnings=list[str],
    sample_size=int,
    effective_sample_size=float | None,
    ground_truth_comparison=GroundTruthComparison | None,
    provenance=Provenance(...),
)
```

The UI, tests, and exports must use this shared structure instead of method-specific ad hoc dictionaries.

### 16.5 Uncertainty

V1 must report uncertainty using a clearly documented method, such as bootstrap or an appropriate large-sample approximation. The application must distinguish:

* sampling uncertainty;
* model uncertainty;
* uncertainty caused by weak overlap;
* uncertainty about the causal assumptions themselves.

A narrow confidence interval does not prove exchangeability or consistency.

## 17. Policy evaluation and intervention allocation

### 17.1 Purpose

The policy layer turns causal estimates into an operational decision exercise. It must not assume that the intervention with the highest predicted risk has the highest incremental benefit.

### 17.2 Policies to compare

V1 compares at least:

* current-practice policy;
* severity-only policy;
* predictive-risk policy;
* causal-effect policy;
* value-per-resource policy;
* oracle policy using ground truth, visible only in teaching mode.

### 17.3 Objective

A default portfolio objective is:

```text
maximize expected avoided_customer_impact_minutes
       - cost_penalty
       - safety_risk_penalty
       - residual_security_risk_penalty
       - recurrence_penalty
```

The objective must be decomposable so the user can see why a policy wins or loses.

### 17.4 Constraints

The allocator must support:

* NOC, SOC, L1, L2, L3, and Field capacity;
* skill, permission, and certification requirements;
* field access and personnel-safety conditions;
* security eligibility;
* budget;
* maximum concurrent changes;
* queue and backlog limits;
* SLA priorities;
* minimum critical-service coverage;
* fallback rules when the preferred action is infeasible.

The allocator must never recommend an action that violates a hard safety or security constraint.

### 17.5 Policy value

For a static policy `π`, the application reports:

```text
V(π) = E[Y^π]
```

with the sign and direction made explicit for each outcome. For example, lower impact minutes is better, whereas higher avoided impact is better.

The policy must be evaluated on held-out simulated episodes. If an action is outside the observed support, the policy evaluation must report a positivity warning rather than silently extrapolate.

### 17.6 Dynamic simulation boundary

The simulator may execute a policy over a sequence of state transitions. V1 may compare such policies using the known simulator or a clearly labeled model-based evaluation. It must not describe that result as a longitudinal causal estimate from observational data unless the corresponding longitudinal estimator and assumptions are implemented.

## 18. User experience and visualization

### 18.1 Course mode

Each lesson follows the same visible structure:

1. **Operational situation:** what is happening to the telecom service?
2. **Causal question:** what would we like to know?
3. **Target trial:** who, when, which actions, which outcome, which horizon?
4. **Assumptions:** what must be true?
5. **Data and DAG:** what is observed and what can bias the comparison?
6. **Method:** how does the estimator work?
7. **Result:** estimate, uncertainty, and ground-truth comparison where allowed;
8. **Interpretation:** what can and cannot be concluded;
9. **Experiment:** which assumption or parameter should the learner change?

The user must be able to move backward and forward without losing the scenario configuration.

### 18.2 Experimental sandbox

The sandbox exposes controls for:

* random seed;
* sample size;
* disturbance mix;
* severity and security-risk distributions;
* confounding strength;
* unmeasured readiness;
* treatment assignment mechanism;
* positivity and eligibility rules;
* measurement error;
* missingness and censoring;
* capacity and backlog;
* policy objective weights;
* estimator and adjustment set.

The sandbox must show which controls change the data-generating process, which change the estimand, and which change only the decision policy.

### 18.3 Visual language

The visual design uses an accessible semantic palette:

* blue: baseline and observed state;
* orange: intervention or treatment assignment;
* green: improvement, containment, or beneficial effect;
* red: deterioration, harm, warning, or constraint violation;
* purple: latent, hidden, or counterfactual information;
* gray: unavailable, censored, or not identified.

Color must never be the only carrier of meaning. Every chart must also use labels, symbols, annotations, or patterns.

### 18.4 Required visualizations

V1 must include:

* incident timeline showing disturbance, detection, triage, interventions, state changes, and outcomes;
* DAG with highlighted causal and non-causal paths;
* baseline covariate balance before and after adjustment;
* treatment propensity and overlap plots;
* IPW weight distribution and effective sample size;
* naive versus adjusted estimate versus known ground truth;
* subgroup-effect forest or dot plot;
* counterfactual outcome distribution for selected interventions;
* policy-value comparison with uncertainty where applicable;
* capacity and constraint dashboard;
* policy trade-off frontier for impact, cost, and risk;
* explicit warning panel for violated assumptions.

### 18.5 Analysis card

Every result view must include a compact analysis card containing:

* causal question;
* estimand;
* target population;
* time zero and follow-up;
* treatment and comparator;
* outcome and direction of benefit;
* estimator;
* adjustment set;
* assumptions;
* diagnostics;
* estimate and uncertainty;
* plain-language interpretation;
* limitations and provenance.

## 19. Repository architecture

The proposed structure is:

```text
causal-resilience-intervention-allocator/
├── README.md
├── PROJECT_SPECIFICATION.md
├── CURRENT_STATE.md
├── pyproject.toml
├── uv.lock or equivalent lock file
├── app.py
├── src/
│   └── causal_resilience/
│       ├── __init__.py
│       ├── config.py
│       ├── schemas.py
│       ├── provenance.py
│       ├── domain/
│       │   ├── adapter.py
│       │   └── telecom_resilience.py
│       ├── simulation/
│       │   ├── structural_model.py
│       │   ├── generator.py
│       │   ├── transitions.py
│       │   └── policies.py
│       ├── causal/
│       │   ├── dag.py
│       │   ├── estimands.py
│       │   ├── identification.py
│       │   ├── diagnostics.py
│       │   ├── baselines.py
│       │   ├── standardization.py
│       │   ├── ipw.py
│       │   ├── doubly_robust.py
│       │   └── heterogeneity.py
│       ├── policy/
│       │   ├── value.py
│       │   ├── allocator.py
│       │   └── constraints.py
│       ├── explanations.py
│       └── visualization.py
├── course/
│   ├── 01_causal_effect.md
│   ├── 02_randomized_experiment.md
│   ├── 03_observational_confounding.md
│   ├── 04_identification_conditions.md
│   ├── 05_dags_and_bias.md
│   ├── 06_selection_and_measurement.md
│   ├── 07_heterogeneity_and_interaction.md
│   ├── 08_standardization.md
│   ├── 09_ipw.md
│   ├── 10_doubly_robust.md
│   ├── 11_policy_value.md
│   └── 12_audit_and_limitations.md
├── notebooks/
├── tests/
│   ├── test_schemas.py
│   ├── test_generator_ground_truth.py
│   ├── test_identification.py
│   ├── test_static_estimators.py
│   ├── test_diagnostics.py
│   ├── test_policy_value.py
│   ├── test_allocator.py
│   ├── test_adapter_contract.py
│   └── test_reproducibility.py
└── docs/
    ├── data_dictionary.md
    ├── causal_questions.md
    ├── assumptions.md
    ├── visualization_guide.md
    └── limitations.md
```

The code layout is a recommendation, not a requirement to create every file before the first working slice. The first implementation slice should be small and runnable.

## 20. Module contracts

### 20.1 `DomainAdapter`

The causal engine must depend on domain-neutral contracts rather than telecom names.

```python
class DomainAdapter(Protocol):
    domain_name: str
    schema_version: str

    def generate_dataset(self, config: ScenarioConfig) -> CaseDataset: ...
    def define_target_trials(self) -> list[TargetTrial]: ...
    def list_actions(self, state: CaseState) -> list[Action]: ...
    def feasible_actions(
        self,
        state: CaseState,
        resources: ResourceState,
    ) -> list[Action]: ...
    def transition(
        self,
        state: CaseState,
        action: Action,
        rng: RandomGenerator,
    ) -> CaseState: ...
    def calculate_outcomes(self, episode: Episode) -> OutcomeSet: ...
    def constraints(self, horizon: Horizon) -> ConstraintSet: ...
    def explain(self, recommendation: Recommendation) -> Explanation: ...
```

The contract must not require fields such as `NOC`, `site`, or `technician`. Telecom-specific vocabulary belongs inside the telecom adapter.

### 20.2 `TargetTrial`

```python
TargetTrial(
    trial_id=str,
    eligibility=EligibilityRule(...),
    time_zero=TimeZeroRule(...),
    strategies=list[TreatmentStrategy],
    outcomes=list[OutcomeDefinition],
    follow_up=FollowUpDefinition(...),
    censoring=CensoringDefinition(...),
    estimand=Estimand(...),
    assumptions=list[Assumption],
)
```

### 20.3 `ScenarioConfig`

The scenario configuration must hold all parameters needed to reproduce a run:

```python
ScenarioConfig(
    seed=int,
    n_episodes=int,
    disturbance_mix=dict,
    confounding_strength=float,
    overlap_mode=str,
    measurement_error=float,
    missingness_mode=str,
    censoring_mode=str,
    capacity_config=CapacityConfig(...),
    policy_config=PolicyConfig(...),
    schema_version=str,
)
```

### 20.4 Estimator interface

Every estimator must accept a target-trial definition, data, an explicit adjustment set, and an estimator configuration. It must return `EstimateResult` and diagnostics rather than only a scalar.

### 20.5 Simulator separation

The simulator must keep separate:

* transition model;
* treatment-assignment mechanism;
* observation and measurement model;
* missingness and censoring mechanism;
* resource and queue model;
* policy execution;
* ground-truth oracle.

An estimator must never call the hidden oracle to calculate its estimate.

## 21. Testing and quality requirements

### 21.1 Ground-truth recovery

For sufficiently large samples in a randomized or correctly specified scenario:

* crude randomized estimates should approach the known effect;
* standardization and IPW should agree within scenario-specific tolerance;
* the doubly robust estimator should remain consistent when one supported nuisance model is correctly specified;
* confidence-interval coverage should be assessed over repeated seeds;
* policy value should agree with the oracle simulation within documented Monte Carlo error.

Tolerances must be reported by scenario. There is no universal tolerance that is valid for every sample size or outcome scale.

### 21.2 Deliberate bias tests

The test suite must demonstrate that:

* naive observational comparisons are biased under confounding by indication;
* a valid adjustment set reduces bias when the relevant assumptions hold;
* adjusting for a collider can create or increase bias;
* absent overlap produces a warning and unstable or unsupported inference;
* treatment-version mismatch triggers a consistency warning;
* measurement error changes the result in a controlled direction or increases uncertainty;
* selection and censoring scenarios are visibly different from the complete-data scenario.

### 21.3 Dynamic and temporal tests

Tests must verify that:

* state histories are ordered and causal time is respected;
* future outcomes cannot leak into treatment assignment or baseline covariates;
* disturbance, detection, escalation, recovery, and capacity events are reproducible;
* every executed action was feasible at the time it was executed;
* outcome definitions use the declared horizon;
* post-treatment variables are not silently included in baseline adjustment.

### 21.4 Policy and allocator safety tests

The allocator must never:

* exceed hard capacity or budget constraints;
* dispatch Field Operations when safety or access conditions fail;
* assign SOC containment to an ineligible incident under the active policy;
* execute an unsafe or unauthorized action;
* use the oracle in normal recommendation mode;
* describe an unsupported counterfactual as identified;
* present a policy trained and evaluated on the same episodes as an unbiased out-of-sample result.

### 21.5 Adapter contract tests

The contract suite must be domain-neutral and must verify:

* schema validity;
* deterministic generation under a fixed seed;
* valid time ordering;
* valid action and outcome types;
* feasible-action behavior;
* constraint behavior;
* compatibility with the common estimator interface;
* availability of a target trial;
* explanation and provenance fields.

`telecom_resilience` must pass the contract without the tests depending on telecom-specific UI labels.

## 22. Reproducibility and provenance

Every exported estimate, chart, policy result, and teaching comparison must carry:

* seed;
* scenario id;
* generator version;
* schema version;
* code or Git revision;
* target-trial id;
* treatment protocol versions;
* estimator configuration;
* adjustment set;
* overlap and weight rules;
* missingness and censoring rules;
* policy and constraint configuration;
* creation timestamp;
* whether ground truth was used.

The README must provide commands for:

* installing the environment;
* launching the Streamlit application;
* running the full test suite;
* regenerating an example dataset;
* reproducing the main charts;
* running the estimator benchmark;
* running the policy-allocation demonstration.

## 23. Safety, ethics, and public communication

The repository must:

* use only synthetic operational and security data;
* avoid real credentials, vulnerabilities, attack procedures, or exploit details;
* describe cyber events at an abstract operational level;
* make clear that the project does not authorize real network changes;
* avoid claiming that synthetic estimates are evidence of real operator performance;
* explain that unmeasured confounding cannot be eliminated by software alone;
* avoid ranking real employees, teams, customers, or suppliers;
* show uncertainty and limitations alongside recommendations.

The output is an educational reference implementation, not an autonomous incident-response system.

## 24. Cross-domain architecture

### 24.1 What cross-domain means for V1

V1 is cross-domain by architecture, not by pretending to deliver multiple complete industry models. It contains:

* a complete telecom reference adapter;
* a domain-neutral causal and policy interface;
* a formal adapter contract;
* contract tests that do not depend on telecom vocabulary;
* documentation describing how a second domain would supply its own semantics and dynamics.

A future adapter is not a visual skin. It is a replaceable domain model with its own data-generating process, causal assumptions, actions, outcomes, and simulator.

### 24.2 Shared causal engine

The shared layer operates on abstractions such as:

* case;
* state;
* disturbance;
* action;
* resource;
* outcome;
* policy;
* target trial;
* estimand;
* assumption;
* diagnostic.

It provides:

* target-trial templates;
* estimand and result schemas;
* identification and assumption checks;
* estimator interfaces;
* overlap and weighting diagnostics;
* heterogeneous-effect interfaces;
* policy evaluation contracts;
* allocation constraints;
* explanation and provenance formats;
* shared course and visualization components where meaningful.

### 24.3 Telecom adapter

The telecom adapter supplies:

* incident, service, asset, and topology semantics;
* disturbance generation;
* L1, NOC, SOC, L2, L3, and Field actions;
* telecom-specific eligibility and constraints;
* service-impact, SLA, restoration, and recurrence outcomes;
* telecom-specific state transitions;
* telecom-specific reason codes and explanations.

### 24.4 Future industry mapping

| Generic concept | Telecom | Manufacturing | Cloud/IT | Utilities |
|---|---|---|---|---|
| Case | Service incident | Machine anomaly | Service incident | Grid or asset incident |
| Control function | NOC / SOC | Plant control room | SRE or operations center | Grid control center |
| Frontline | L1 Front Office | Operator or plant support | Service desk | Customer operations |
| Specialist | L2, L3, Field | Maintenance, reliability, OEM | Platform, security, product engineering | Field crew, asset engineering |
| Disturbance | Cyberattack, vandalism, failure | Wear, sabotage, process disruption | Cyberattack, overload, misconfiguration | Weather, damage, sabotage |
| Outcome | Restoration, impact, SLA, recurrence | Downtime, scrap, repair cost | Availability, incident duration | Restoration, affected customers, safety |

The similarity is at the level of decision structure. The mechanisms, interventions, confounders, outcomes, and constraints remain domain-specific.

### 24.5 Adding a future adapter

A future adapter must be added in this order:

1. define one domain decision and one primary estimand;
2. define eligibility, time zero, treatment strategies, outcomes, follow-up, and censoring;
3. create a domain DAG and declare assumptions;
4. map domain entities into the neutral contract;
5. create a structural simulator with known ground truth;
6. implement state transitions, delays, queues, and constraints;
7. run the common estimators without modifying the causal engine;
8. pass contract and ground-truth tests;
9. add domain-specific explanations and UI content;
10. document what transfers and what does not.

A domain must not be called supported merely because its labels appear in a dropdown.

## 25. Implementation roadmap

### Phase 1: Small runnable slice

* Python project setup and lock file;
* schemas and provenance;
* one telecom incident generator;
* one randomized binary contrast;
* one primary outcome;
* one plot and one ground-truth test;
* basic Streamlit page.

### Phase 2: Core causal curriculum

* observational assignment;
* DAG and adjustment declaration;
* confounding, positivity, and consistency diagnostics;
* outcome regression and standardization;
* propensity scores and IPW;
* repeated-seed benchmark;
* course-mode lessons.

### Phase 3: Dynamic telecom realism

* disturbance catalogue;
* L1, NOC, SOC, L2, L3, and Field protocols;
* state transitions and episode timeline;
* queues, capacity, access, safety, and security constraints;
* recurrence and policy simulation;
* sandbox controls.

### Phase 4: Doubly robust and policy layer

* supported doubly robust estimator;
* cross-fitting where appropriate;
* heterogeneous effects;
* holdout policy evaluation;
* constrained allocator;
* analysis cards and audit export.

### Phase 5: Public-release hardening

* contract tests;
* failure-mode tests;
* reproducibility commands;
* documentation and limitations;
* accessible visual review;
* clean-environment CI;
* public README and example walkthrough.

### Later releases

The next methodological releases may add IV, causal survival, mediation, and longitudinal g-methods in separate modules. Each addition must introduce its own target trial, assumptions, simulator scenario, estimator tests, and educational lesson.

## 26. Release acceptance criteria

V1 is ready for public release only when all of the following are true:

* the README explains the use case, educational purpose, and synthetic-data limitation;
* the telecom reference adapter passes the neutral contract suite;
* the simulator has a documented structural data-generating process and known ground truth;
* every main lesson declares a causal question and target trial;
* the application demonstrates at least one controlled randomized scenario and one confounded observational scenario;
* the application shows a visible difference between naive association and adjusted causal estimation;
* positivity, exchangeability, and consistency warnings are understandable to a learner;
* core estimators pass repeated-seed ground-truth tests within scenario-specific tolerances;
* uncertainty is reported with the estimate;
* at least one scenario shows confounding by indication;
* at least one scenario shows a positivity limitation;
* the dynamic timeline includes cyberattack and vandalism scenarios without offensive-security content;
* all six operational functions are represented in the telecom model: L1, NOC, SOC, L2, L3, and Field Operations;
* the policy allocator respects resource, safety, security, budget, and SLA constraints;
* policies are evaluated on held-out episodes or clearly labeled simulator runs;
* the course and sandbox use the same reproducible backend;
* required visualizations and analysis cards are present;
* no V1 screen implies that IV, mediation, causal survival, or longitudinal g-methods are already implemented;
* the repository runs from a clean environment using documented commands;
* the limitations section explicitly covers synthetic data, unmeasured confounding, positivity, consistency, interference, and transportability;
* the release makes no real-world effectiveness or production-readiness claim.

## 27. Key limitations

### Synthetic data

Recovering the generator’s known effect demonstrates implementation behavior under the generator’s assumptions. It does not validate those assumptions in a real telecom organization.

### Exchangeability

Operational logs cannot prove that all common causes of treatment and outcome were measured. Domain knowledge, design, sensitivity analysis, and triangulation remain necessary.

### Positivity

If every severe cyber incident receives SOC containment, the data do not identify the outcome under an alternative route for that subgroup without strong extrapolation. The application must show this limitation.

### Consistency

A broad label such as “field repair” or “L2 escalation” may hide materially different protocols. The estimand must be restricted or the treatment versions modeled explicitly.

### Dynamic treatment and feedback

Severity, workload, and readiness can change after an intervention and influence subsequent actions. V1’s dynamic simulator illustrates this phenomenon, but V1 does not claim to solve longitudinal causal estimation.

### Interference

Shared capacity, service dependencies, and network propagation mean that one incident’s response can affect another incident’s outcome. Portfolio simulation and episode-level causal estimation must remain visibly distinct.

### Policy evaluation

Policy value from a known simulator is useful for learning and testing. It is not equivalent to reliable off-policy evaluation from real observational operations.

### Transportability

The telecom adapter is not automatically valid for manufacturing, utilities, cloud/IT, or transport. A future adapter must provide its own causal story, data-generating process, and validation.

## 28. Final project definition

`Causal Resilience Intervention Allocator` is a public, Python-first educational laboratory that teaches causal inference through a dynamic telecom incident-response problem.

It moves from:

```text
service-affecting disturbance
→ observed and latent state
→ explicit treatment protocol
→ target trial and causal assumptions
→ identification and estimation
→ counterfactual interpretation
→ policy evaluation
→ constrained intervention allocation
→ transparent recommendation and audit
```

The project’s most important lesson is methodological discipline:

> Define the question, population, intervention, comparator, outcome, time zero, follow-up, and assumptions before selecting a model or displaying a number.

## 29. Sources

* Hernán MA, Robins JM, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook). Primary methodological source and V1 syllabus.
* Pearl J, [*Causality*](https://bayes.cs.ucla.edu/BOOK-2K/). Supplementary reference for causal diagrams and structural causal models.
* Cunningham S, [*Causal Inference: The Mixtape*](https://mixtape.scunning.com/). Supplementary reference for intuition and selected econometric methods.
* VanderWeele T, [*Explanation in Causal Inference*](https://global.oup.com/academic/product/explanation-in-causal-inference-9780199325870). Supplementary reference for interaction and later mediation work.
* [DoWhy documentation](https://www.pywhy.org/dowhy/). Causal model, identification, estimation, and refutation tooling.
* [EconML documentation](https://econml.azurewebsites.net/). Heterogeneous treatment effects and double/debiased machine-learning tooling.
* [statsmodels documentation](https://www.statsmodels.org/). Transparent statistical modeling.
* [scikit-learn documentation](https://scikit-learn.org/). Nuisance models, preprocessing, and validation.
* [Streamlit documentation](https://docs.streamlit.io/). Educational application layer.
* [Plotly Python documentation](https://plotly.com/python/). Interactive visualizations.
* [SMusial/rlvr-enterprise-allocator](https://github.com/SMusial/rlvr-enterprise-allocator). Reference pattern for learning a data-science domain through one coherent operational project.
