# Causal Resilience Intervention Allocator

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC)](https://pytest.org/)
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
| 4 | Confounding, DAG, Lessons 3–4 | 🔲 Pending |
| 5 | Adjustment, IPW, diagnostics, Lessons 5–6 | 🔲 Pending |
| 6 | Accessibility, documentation, release gate | 🔲 Pending |

## Repository structure

```text
causal-resilience-intervention-allocator/
├── app.py                          # Streamlit application (Slice 3+)
├── pyproject.toml                  # Package config and pinned dependencies
├── requirements.txt                # Direct pip install
├── src/
│   └── causal_resilience/
│       └── foundations/
│           ├── schemas.py          # V0 data contracts (Slice 1)
│           ├── dgp.py              # Structural data-generating process (Slice 2+)
│           ├── estimators.py       # Causal estimators (Slice 2+)
│           ├── diagnostics.py      # Overlap, balance, weight diagnostics (Slice 5+)
│           ├── provenance.py       # Reproducibility utilities (Slice 2+)
│           └── lessons.py          # Course lesson content (Slice 3+)
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
│       ├── test_schemas.py         # 39 schema tests (Slice 1)
│       ├── test_dgp.py             # DGP and ground-truth tests (Slice 2+)
│       ├── test_estimators.py      # Estimator correctness tests (Slice 2+)
│       ├── test_diagnostics.py     # Diagnostic behavior tests (Slice 5+)
│       └── test_reproducibility.py # Seed and config reproducibility (Slice 2+)
├── docs/
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

> Run `streamlit run app.py` to start the application.

## Run the tests

```bash
pytest -v
```

Current result: **95 passed** across `test_schemas.py`, `test_dgp.py`, `test_estimators.py`, and `test_lessons.py`.

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

### Difference-in-means estimator

`DifferenceInMeans` computes the naive treated-minus-control mean difference with a bootstrap 95% confidence interval. It accepts an optional `GroundTruth` for oracle comparison and returns a fully populated `EstimateResult`.

Under randomization at n=1000, the estimator recovers the oracle ATE to within ~1 minute (oracle −39.2, estimate −40.0 in the reference run).

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
| 5 | Adjustment: stratification, standardization, and IPW |
| 6 | Diagnostics, uncertainty, and responsible interpretation |

## Methodological foundation

The primary source is Hernán MA, Robins JM, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook). V0 draws on Chapters 1–3 and selected material from Chapter 6.

The project follows the book's central discipline: define the causal question, population, intervention, comparator, outcome, time zero, follow-up, and identification assumptions before selecting an estimator or displaying a number.

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

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
