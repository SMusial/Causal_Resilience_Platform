# Causal Resilience Intervention Allocator

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Tests](https://img.shields.io/badge/Tests-189%20passed-0A9EDC)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)

An educational causal-inference laboratory and decision-intelligence demonstration built around a synthetic telecom incident-response world.

> All data, incidents, organizations, and results in this repository are entirely synthetic and illustrative. Nothing here constitutes evidence about real telecom operations, real organizations, or real interventions.

## What this project teaches

The project studies one practical question:

> For a service-affecting incident, what would the outcome have been if the organization had applied intervention A instead of a feasible alternative B at the defined decision time?

It teaches the difference between:

- predicting an outcome
- estimating the effect of an intervention
- simulating counterfactual trajectories
- evaluating a policy
- allocating scarce operational capacity

## The causal question

Among eligible synthetic telecom incidents at detection, what is the average effect of assigning an **early coordinated response** rather than **monitor-and-reassess** on customer-impact minutes during the following 24 hours?

```
ATE = E[Y(1) - Y(0)]

Y(1) = customer_impact_minutes_24h under EARLY_COORDINATED_RESPONSE
Y(0) = customer_impact_minutes_24h under MONITOR_REASSESS
```

A negative ATE means early coordinated response reduces average customer impact.

## Implementation status

This repository is under active development. The implementation follows a gated slice plan. Each slice is reviewed before the next begins.

| Slice | Scope | Status |
|---|---|---|
| 1 | Schemas, provenance, dependencies, tests | ✅ Complete — commit `0bbe918` |
| 2 | Structural DGP, randomized contrast, oracle | ✅ Complete — commit `75cb440` |
| 3 | First Streamlit page, Lessons 1–2, target-trial card | ✅ Complete — commit `acd6b4a` |
| 4 | Confounding, DAG, Lessons 3–4 | ✅ Complete — commit `f9cc08b` |
| 5 | Adjustment, IPW, diagnostics, Lessons 5–6 | ✅ Complete — commit `7735014` |
| 6 | Accessibility, documentation, release gate | ✅ Complete — commit `f7d514b` |

## Repository structure

```text
Causal_Resilience_Platform/
├── app.py                          # Streamlit application — 6 lessons + sandbox
├── pyproject.toml                  # Package config and pinned dependencies
├── requirements.txt                # Direct pip install
├── src/
│   └── causal_resilience/
│       └── foundations/
│           ├── schemas.py          # V0 data contracts (Slice 1)
│           ├── dgp.py              # Structural data-generating process (Slice 2+)
│           ├── estimators.py       # DiM, Standardization, IPW (Slice 2/5)
│           ├── diagnostics.py      # Overlap, balance, weight diagnostics (Slice 5)
│           ├── lessons.py          # Course lesson content, Lessons 1–6 (Slice 3/5)
│           └── tables.py           # Potential-outcome table rendering (Slice 3)
├── course/
│   └── v0/
│       ├── 01_causal_question.md
│       ├── 02_potential_outcomes.md
│       ├── 03_randomization.md
│       ├── 04_confounding.md
│       ├── 05_adjustment.md
│       └── 06_diagnostics.md
├── tests/
│   └── foundations/
│       ├── test_schemas.py         # Schema validation tests (Slice 1)
│       ├── test_dgp.py             # DGP and ground-truth tests (Slice 2)
│       ├── test_estimators.py      # DiM, Standardization, IPW tests (Slice 2/5)
│       ├── test_diagnostics.py     # Overlap, weight, balance tests (Slice 5)
│       └── test_lessons.py         # Lesson content and table tests (Slice 3/5)
├── docs/
│   ├── guides/
│   │   ├── causal-inference-ch1-churn-use-case.pdf  # Chapter 1 applied guide
│   │   └── causal-inference-ch2-churn-use-case.pdf  # Chapter 2 applied guide
│   └── sources/
│       └── whatif.pdf              # Hernán & Robins, Causal Inference: What If
└── .kiro/
    └── specs/causal-resilience/    # Reconciled V0 and V1 specifications
```

## Installation

Requires Python 3.11 or newer.

```bash
git clone https://github.com/SMusial/Causal_Resilience_Platform.git
cd Causal_Resilience_Platform

python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS / Linux
# source .venv/bin/activate

pip install -e ".[dev]"
```

## Run the application

```bash
streamlit run app.py
```

## Run the tests

```bash
pytest -v
```

Current result: **189 passed** across `test_schemas.py`, `test_dgp.py`, `test_estimators.py`, `test_diagnostics.py`, and `test_lessons.py`.

## Data model (Slice 1)

The V0 data model separates configuration, episodes, and results into distinct layers.

### Configuration

`ScenarioConfig` holds everything needed to reproduce a run: random seed, number of episodes, assignment mode (randomized, confounded, or limited-overlap), confounding strength, treatment effect magnitude, outcome noise, overlap mode, and a teaching-mode flag.

### Episode

`IncidentEpisode` is the unit of analysis — one synthetic incident. It contains:

- `severity`: continuous baseline confounder in [0, 1], measured before treatment
- `disturbance_type`: abstract incident category (equipment failure, software regression, misconfiguration, overload, weather disruption, cyber disruption, physical disruption)
- `treatment`: binary assignment — 1 for `EARLY_COORDINATED_RESPONSE`, 0 for `MONITOR_REASSESS`
- `outcome`: `customer_impact_minutes_24h`, continuous and non-negative

Oracle fields (`potential_outcome_0`, `potential_outcome_1`, `propensity_true`) are `None` in normal mode and visible only when `teaching_mode=True`. A consistency rule is enforced at construction: the observed outcome must equal the potential outcome under the assigned treatment whenever oracle fields are present.

`FoundationsDataset` wraps a list of episodes with provenance metadata. Its `to_dataframe()` method strips oracle columns in normal mode.

### Results

`GroundTruth` holds the finite-sample ATE and marginal potential-outcome means computed by the structural oracle. It is available only in teaching and test mode.

`Estimand` declares what the analysis is trying to learn: the ATE on the mean-difference scale, with outcome name, units, follow-up period, direction of benefit, and five pre-populated identification assumptions.

`EstimateResult` is the common return object for every estimator. It carries the estimate, confidence interval, standard error, sample sizes, assumptions, structured diagnostics, string warnings, an optional oracle comparison, and provenance. The `has_warnings` property aggregates both string warnings and diagnostic-level warnings.

`Provenance` attaches seed, scenario identifier, generator version, schema version, creation timestamp, and an `oracle_used` flag to every dataset and estimate.

## Data model (Slice 2)

### Structural data-generating process

`TelecomFoundationsDGP` generates synthetic incident episodes using structural equations:

```text
baseline_impact = 100 + 240 × severity + noise
Y(0) = max(0, baseline_impact)
Y(1) = max(0, baseline_impact + treatment_effect + noise_delta)
```

Default `treatment_effect = −40.0` minutes. Three assignment modes are supported:

- `RANDOMIZED` — 50/50 coin flip, no confounding
- `CONFOUNDED` — logistic propensity driven by severity
- `LIMITED_OVERLAP` — extreme-severity episodes receive near-deterministic assignment

Oracle fields are populated only when `teaching_mode=True`. `truth()` returns a `GroundTruth` object with the finite-sample ATE computed directly from potential outcomes.

## Estimators (Slices 2 and 5)

All estimators share the `CausalEstimator` protocol, return a fully populated `EstimateResult`, and use a nonparametric bootstrap for uncertainty. The bootstrap interval reflects sampling variability only — it does not quantify unmeasured-confounding uncertainty.

### Difference in means

```text
ATE_hat = mean(Y | A=1) − mean(Y | A=0)
```

Valid under randomization. Biased under confounded assignment without adjustment.

### Standardization (g-formula)

```text
1. Fit E[Y | A, severity] with OLS.
2. Predict Y_hat(1) and Y_hat(0) for every episode.
3. ATE_hat = mean(Y_hat(1) − Y_hat(0))
```

Requires correct outcome-model specification. Under the correctly specified linear DGP, recovers the oracle ATE within 5 minutes at n=3000.

### Inverse-probability weighting

```text
1. Fit P(A=1 | severity) with logistic regression.
2. Weight each episode by 1 / P(A=a_i | severity_i).
3. ATE_hat = weighted_mean(Y | A=1) − weighted_mean(Y | A=0)
```

Requires correct propensity-model specification and positivity. Under the correctly specified DGP, recovers the oracle ATE within 5 minutes at n=3000.

## Diagnostics (Slice 5)

`diagnostics.py` provides three checks that must be examined before interpreting any adjusted estimate.

### Overlap

`compute_overlap` assesses whether propensity scores for treated and control episodes span a common range. Episodes with propensity within 0.05 of 0 or 1 are flagged as near-boundary. Non-overlapping ranges trigger a positivity warning.

### Weight distribution and effective sample size

`compute_weight_diagnostic` summarises the IPW weight distribution and computes the Kish effective sample size:

```text
ESS = (sum w)² / sum(w²)
```

Weights above the configurable threshold (default 10) are flagged as extreme. A low ESS relative to the nominal sample size indicates the estimate is driven by a small number of episodes.

### Covariate balance

`compute_balance` computes the standardized mean difference (SMD) for severity before and after IPW weighting:

```text
SMD = |mean_treated − mean_control| / pooled_sd
```

SMD < 0.1 is the conventional threshold for adequate balance. Under correctly specified IPW, the weighted SMD should be substantially smaller than the unweighted SMD.

## Identification assumptions

Every causal result in this project is conditional on the following assumptions being stated and examined:

1. **Consistency** — the observed outcome equals the potential outcome under the assigned treatment.
2. **Exchangeability** — conditional on measured severity, potential outcomes are independent of treatment assignment.
3. **Positivity** — every severity level in the target population has a positive probability of receiving either intervention.
4. **No interference** — one episode's treatment does not affect another episode's outcome (V0 simplification; relaxed in V1).
5. **Complete follow-up** — the 24-hour outcome is observed for all eligible episodes (V0 simplification).

These assumptions cannot be verified from observed data alone. The simulator's structural data-generating process makes them true by construction in the teaching scenarios, which is why the oracle comparison is a useful learning tool but not evidence about real operations.

## V0 course outline

V0 is a six-lesson guided sequence. Each lesson has a learning objective, a short explanation, one interactive visual, one estimate or diagnostic, an interpretation, and a source reference.

| Lesson | Topic |
|---|---|
| 1 | Ask a causal question — population, intervention, comparator, outcome, time zero |
| 2 | Potential outcomes and the missing counterfactual |
| 3 | Randomization: when association can identify causation |
| 4 | Confounding and the DAG |
| 5 | Adjustment: standardization and IPW |
| 6 | Diagnostics, uncertainty, and responsible interpretation |

## Methodological foundation

The primary source is Hernán MA, Robins JM, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook) (free PDF: [`docs/sources/whatif.pdf`](docs/sources/whatif.pdf)). V0 draws on Chapters 1–3 and selected material from Chapter 6.

The project follows the book's central discipline: define the causal question, population, intervention, comparator, outcome, time zero, follow-up, and identification assumptions before selecting an estimator or displaying a number.

### Chapter guides

Applied chapter-by-chapter guides using a telecom churn use case are in [`docs/guides/`](docs/guides/):

| Chapter | Topic | Guide |
|---|---|---|
| 1 | A definition of causal effect | [causal-inference-ch1-churn-use-case.pdf](docs/guides/causal-inference-ch1-churn-use-case.pdf) |
| 2 | Randomized experiments | [causal-inference-ch2-churn-use-case.pdf](docs/guides/causal-inference-ch2-churn-use-case.pdf) |
| 3 | Observational studies | [causal-inference-ch3-churn-use-case.pdf](docs/guides/causal-inference-ch3-churn-use-case.pdf) |
| 4 | Effect modification | [causal-inference-ch4-churn-use-case.pdf](docs/guides/causal-inference-ch4-churn-use-case.pdf) |

## What is explicitly out of scope for V0

- NOC, SOC, L1, L2, L3, and Field Operations as separate treatment options
- Dynamic state transitions or sequential treatment decisions
- Policy learning or constrained allocation
- Doubly robust estimation or cross-fitting
- Instrumental variables, survival analysis, mediation, or longitudinal methods
- Interference estimation
- DoWhy or EconML (introduced in V1 after the concepts are understood)
- R or Rust implementation
- Real telecom data or operational-system integration

## Relationship to V1

V0 is the conceptual and software foundation for the full V1 Telecom Causal Resilience platform. V1 will extend V0 with dynamic incident episodes, six operational roles, seven response protocols, shared resource constraints, richer confounding, doubly robust estimation, policy evaluation, and a formal domain-adapter contract.

V1 must reuse V0's definitions of treatment, outcome, estimand, assumptions, estimate result, and provenance without silently redefining them.

## Pedagogical review

A full pedagogical review of V0 (Lessons 1–6) was completed after Slice 6. The review covers learning objectives, causal correctness, accessibility, consistency between UI/documentation/implementation/tests, and a V0 release readiness checklist.

Report: [`docs/reviews/v0_pedagogical_review.md`](docs/reviews/v0_pedagogical_review.md)

Verdict: **Ready for supervised use.** One major gap identified (stratification as first adjustment method, per spec §10.2) and four minor improvements recommended. All 189 tests pass. No oracle leakage. WCAG AA accessibility confirmed.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
