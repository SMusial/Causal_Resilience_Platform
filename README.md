# Causal Resilience Intervention Allocator

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Tests](https://img.shields.io/badge/Tests-189%20passed-0A9EDC)](https://pytest.org/)
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

## Analytical modules

The application walks through six modules that form a complete causal-inference pipeline. Each module has an interactive visual, a live estimate or diagnostic, and an interpretation grounded in the target trial.

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

## Repository structure

```text
Causal_Resilience_Platform/
├── app.py                          # Streamlit application — 6 analytical modules + sandbox
├── pyproject.toml                  # Package config and pinned dependencies
├── requirements.txt                # Direct pip install
├── src/
│   └── causal_resilience/
│       └── foundations/
│           ├── schemas.py          # V0 data contracts (Slice 1)
│           ├── dgp.py              # Structural data-generating process (Slice 2+)
│           ├── estimators.py       # DiM, Standardization, IPW (Slice 2/5)
│           ├── diagnostics.py      # Overlap, balance, weight diagnostics (Slice 5)
│           ├── lessons.py          # Analytical module content, modules 1–6 (Slice 3/5)
│           └── tables.py           # Potential-outcome table rendering (Slice 3)
├── course/
│   └── v0/                         # Analytical module reference documents
├── tests/
│   └── foundations/
│       ├── test_schemas.py         # Schema validation tests (Slice 1)
│       ├── test_dgp.py             # DGP and ground-truth tests (Slice 2)
│       ├── test_estimators.py      # DiM, Standardization, IPW tests (Slice 2/5)
│       ├── test_diagnostics.py     # Overlap, weight, balance tests (Slice 5)
│       └── test_lessons.py         # Analytical module and table tests (Slice 3/5)
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

189 tests pass across schemas, DGP, estimators, diagnostics, and analytical modules.

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

## Relationship to V1

V0 is the conceptual and software foundation for the full V1 Telecom Causal Resilience platform. V1 will extend V0 with dynamic incident episodes, six operational roles, seven response protocols, shared resource constraints, richer confounding, doubly robust estimation, policy evaluation, and a formal domain-adapter contract.

V1 must reuse V0's definitions of treatment, outcome, estimand, assumptions, estimate result, and provenance without silently redefining them.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
