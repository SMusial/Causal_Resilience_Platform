# Causal Resilience Intervention Allocator

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Tests](https://img.shields.io/badge/Tests-235%20passed-0A9EDC)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE)

A causal-inference laboratory and decision-intelligence demonstration built around a synthetic telecom incident-response world.

> All data, incidents, organizations, and results in this repository are entirely synthetic and illustrative. Nothing here constitutes evidence about real telecom operations, real organizations, or real interventions.

## What this project demonstrates

The project addresses one practical question:

> For a service-affecting incident, what would the outcome have been if the organization had applied intervention A instead of a feasible alternative B at the defined decision time?

It demonstrates the difference between:

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

## Navigation

A single sidebar radio selects the active lesson. V0 and V1 lessons are listed together — no tabs.

| Entry | Version | Topic |
|---|---|---|
| V0 L1 | V0 | Ask a causal question |
| V0 L2 | V0 | Potential outcomes |
| V0 L3 | V0 | Randomization |
| V0 L4 | V0 | Confounding and the DAG |
| V0 L5 | V0 | Adjustment |
| V0 L6 | V0 | Diagnostics |
| V0 Sandbox | V0 | Full estimator comparison |
| V1 M1 | V1 | Ask a causal question (extended) |
| V1 M2 | V1 | Potential outcomes (extended) |

## V0 analytical modules

The V0 pipeline walks through six modules. Each has an interactive visual, a live estimate or diagnostic, and an interpretation grounded in the target trial.

| Module | Topic | What you see |
|---|---|---|
| 1 | Ask a causal question | Define population, intervention, comparator, outcome, and time zero using a structured target-trial card |
| 2 | Potential outcomes | Explore the fundamental problem of causal inference — the missing counterfactual — with an oracle comparison |
| 3 | Randomization | See when and why association equals causation; contrast randomized vs confounded assignment |
| 4 | Confounding and the DAG | Visualize how severity drives both treatment and outcome; understand what adjustment is needed and why |
| 5 | Adjustment | Apply standardization (g-formula) and inverse-probability weighting; compare adjusted estimates to the oracle ATE |
| 6 | Diagnostics | Inspect overlap, weight distribution, effective sample size, and covariate balance before trusting any estimate |

## How it was built — V0 slice plan

V0 was delivered in six gated slices. Each slice was reviewed and tested before the next began.

| Slice | What was built | Status |
|---|---|---|
| 1 | Data contracts, provenance tracking, reproducible episode schema, full test harness | ✅ Complete |
| 2 | Structural data-generating process with oracle ground truth; randomized, confounded, and limited-overlap assignment modes; difference-in-means estimator | ✅ Complete |
| 3 | First Streamlit page; causal question framing; potential outcomes with oracle reveal; target-trial card | ✅ Complete |
| 4 | Confounding module; DAG visualization; side-by-side randomized vs confounded comparison | ✅ Complete |
| 5 | Standardization and IPW estimators; overlap, weight, and balance diagnostics; oracle recovery validation | ✅ Complete |
| 6 | Accessibility audit, WCAG AA compliance, full documentation, release gate | ✅ Complete |

## Identification assumptions

Every causal result in this project is conditional on the following assumptions being stated and examined:

1. **Consistency** — the observed outcome equals the potential outcome under the assigned treatment.
2. **Exchangeability** — conditional on measured severity, potential outcomes are independent of treatment assignment.
3. **Positivity** — every severity level in the target population has a positive probability of receiving either intervention.
4. **No interference** — one episode's treatment does not affect another episode's outcome (V0 simplification; relaxed in V1).
5. **Complete follow-up** — the 24-hour outcome is observed for all eligible episodes (V0 simplification).

These assumptions cannot be verified from observed data alone. The simulator's structural data-generating process makes them true by construction, which is why the oracle comparison is a useful validation tool but not evidence about real operations.

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
| 5 | Interaction | [causal-inference-ch5-churn-use-case.pdf](docs/guides/causal-inference-ch5-churn-use-case.pdf) |
| 6 | Graphical representation of causal effects | [causal-inference-ch6-churn-use-case.pdf](docs/guides/causal-inference-ch6-churn-use-case.pdf) |
| 7 | Effect modification | [causal-inference-ch7-churn-use-case.pdf](docs/guides/causal-inference-ch7-churn-use-case.pdf) |
| 8 | Outcome regression and the g-formula | [causal-inference-ch8-churn-use-case.pdf](docs/guides/causal-inference-ch8-churn-use-case.pdf) |
| 9 | Propensity scores and IPW | [causal-inference-ch9-churn-use-case.pdf](docs/guides/causal-inference-ch9-churn-use-case.pdf) |
| 9 | Propensity scores and IPW | [causal-inference-ch9-churn-use-case.pdf](docs/guides/causal-inference-ch9-churn-use-case.pdf) |

## Repository structure

```text
Causal_Resilience_Platform/
├── app.py                          # Streamlit application — V0 L1–L6, Sandbox, V1 M1–M2
├── pyproject.toml                  # Package config and pinned dependencies
├── requirements.txt                # Direct pip install
├── src/
│   └── causal_resilience/
│       ├── foundations/
│       │   ├── schemas.py          # V0 data contracts (Slice 1)
│       │   ├── dgp.py              # Structural data-generating process (Slice 2+)
│       │   ├── estimators.py       # DiM, Standardization, IPW (Slice 2/5)
│       │   ├── diagnostics.py      # Overlap, balance, weight diagnostics (Slice 5)
│       │   ├── lessons.py          # V0 lesson content, modules 1–6 (Slice 3/5)
│       │   └── tables.py           # Potential-outcome table rendering (Slice 3)
│       └── v1/
│           ├── schemas.py          # V1 data contracts — TargetTrial, BaselineCovariates, Protocol
│           └── lessons.py          # V1 lesson content — M1, M2
├── course/
│   ├── v0/                         # V0 analytical module reference documents
│   └── v1/                         # V1 analytical module reference documents
├── tests/
│   ├── foundations/
│   │   ├── test_schemas.py         # Schema validation tests (Slice 1)
│   │   ├── test_dgp.py             # DGP and ground-truth tests (Slice 2)
│   │   ├── test_estimators.py      # DiM, Standardization, IPW tests (Slice 2/5)
│   │   ├── test_diagnostics.py     # Overlap, weight, balance tests (Slice 5)
│   │   └── test_lessons.py         # V0 analytical module and table tests (Slice 3/5)
│   └── v1/
│       ├── test_schemas.py         # V1 schema validation tests
│       └── test_lessons.py         # V1 lesson content tests — M1, M2
├── docs/
│   ├── guides/                     # Applied chapter guides (telecom churn use case)
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

235 tests pass across schemas, DGP, estimators, diagnostics, V0 analytical modules, and V1 lessons.

## What is out of scope for V0

- NOC, SOC, L1, L2, L3, and Field Operations as separate treatment options
- Dynamic state transitions or sequential treatment decisions
- Policy learning or constrained allocation
- Doubly robust estimation or cross-fitting
- Instrumental variables, survival analysis, mediation, or longitudinal methods
- Interference estimation
- DoWhy or EconML (introduced in V1)
- R or Rust implementation
- Real telecom data or operational-system integration

## V1 — planned platform extension

V0 is the foundation. V1 extends it into a full causal-inference and decision-intelligence platform without replacing or redefining any V0 concept.

### What V1 adds

| Area | V0 | V1 |
|---|---|---|
| Incident model | Single binary contrast, static covariates | Dynamic state transitions, 15-min decision steps, 24h follow-up |
| Roles and protocols | Two protocols (treatment vs comparator) | Six operational roles, seven response protocols, eligibility enforcement |
| Confounding | Severity-driven logistic propensity | Latent readiness, topology criticality, team backlog, measurement error, missingness |
| Estimators | DiM, standardization, IPW | + Doubly robust, stratified adjustment, subgroup/CATE, policy value |
| Policy layer | None | Constrained allocation across six roles; capacity, safety, budget, SLA hard gates |
| Diagnostics | Overlap, balance, ESS | + Assumption-warning panel, trade-off frontier, counterfactual distributions |
| Tooling | SciPy, scikit-learn | + DoWhy, EconML, statsmodels |
| Analytical modules | 6 | 13 guided modules + experimental sandbox |

### V1 analytical modules

| Module | Topic | Status |
|---|---|---|
| 1 | Ask a causal question — target trial, estimand, population, time zero | ✅ Complete |
| 2 | Potential outcomes and the fundamental problem of causal inference | ✅ Complete |
| 3 | Randomization — when association equals causation | 🔜 Planned |
| 4 | Observational assignment — confounding, bias, and the naive estimator | 🔜 Planned |
| 5 | The DAG — backdoor paths, valid adjustment sets, and collider bias | 🔜 Planned |
| 6 | Selection bias and measurement error as controlled failure scenarios | 🔜 Planned |
| 7 | Effect modification — subgroup effects by disturbance type, severity, and criticality | 🔜 Planned |
| 8 | Outcome regression and the g-formula | 🔜 Planned |
| 9 | Propensity scores, IPW, and overlap diagnostics | 🔜 Planned |
| 10 | Doubly robust estimation | 🔜 Planned |
| 11 | Subgroup effects and CATE — demonstrations with support warnings | 🔜 Planned |
| 12 | Policy evaluation — causal targeting vs risk targeting vs current practice | 🔜 Planned |
| 13 | Audit and limitations — target trial, assumptions, diagnostics, uncertainty, provenance | 🔜 Planned |

### How V1 sits alongside V0 in the repository

V1 does not overwrite V0. Both versions coexist under the same repository root. V0 foundations remain importable and tested independently.

```text
Causal_Resilience_Platform/
├── app.py                          # Entry point — routes to V0 or V1 UI
├── src/
│   └── causal_resilience/
│       ├── foundations/            # V0 — schemas, DGP, estimators, diagnostics, modules
│       └── v1/                     # V1 — new layers added on top of foundations
│           ├── domain/             # DomainAdapter contract + telecom implementation
│           ├── simulation/         # Dynamic state transitions, structural model, policies
│           ├── causal/             # Extended estimators: DR, CATE, policy value
│           ├── policy/             # Constrained allocator, capacity, hard gates
│           ├── explanations.py     # Audit cards, assumption warnings, provenance
│           └── visualization.py    # Extended Plotly views: timeline, DAG, frontier
├── course/
│   ├── v0/                         # V0 analytical module reference documents
│   └── v1/                         # V1 analytical module reference documents
├── tests/
│   ├── foundations/                # V0 test suite (211 tests, unchanged)
│   └── v1/                         # V1 test suite (24 tests, added alongside, never replacing)
├── docs/
│   ├── guides/                     # Applied chapter guides (telecom churn use case)
│   └── sources/
│       └── whatif.pdf              # Hernán & Robins, Causal Inference: What If
└── .kiro/
    └── specs/causal-resilience/    # V0 and V1 specifications
```

V1 must reuse V0's definitions of treatment, outcome, estimand, assumptions, estimate result, and provenance without silently redefining them. The `DomainAdapter` contract allows future industry adapters to plug in without modifying the causal estimator APIs.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
