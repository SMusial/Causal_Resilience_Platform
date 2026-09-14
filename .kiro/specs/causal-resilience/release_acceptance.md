# V1 Release Acceptance Criteria

All 26 criteria must pass before the V1 public release is tagged.

1. The project installs from a clean Python 3.11+ environment using pinned dependencies.
2. `pytest` runs successfully in the clean environment.
3. `streamlit run app.py` starts without an application error.
4. Course mode exposes all 13 lessons in the documented order.
5. Experimental Sandbox mode can change seed, sample size, confounding, overlap, and at least one policy/resource setting.
6. The primary binary contrast is consistently named `COORDINATED_RESPONSE` versus `MONITOR_REASSESS`.
7. The primary causal outcome is consistently defined as `customer_impact_minutes_24h` with a 24-hour follow-up.
8. Every causal result displays its causal question, estimand, population, time zero, treatment, outcome, and estimator.
9. The randomized difference-in-means estimator recovers the simulator's known ATE within the documented Monte Carlo tolerance.
10. The confounded observational scenario produces a visibly and numerically different crude estimate from the known effect.
11. The project displays a baseline DAG distinguishing baseline causes, treatment, post-treatment variables, and outcome.
12. Exchangeability, positivity, consistency, and temporal-ordering checks produce visible diagnostics or warnings.
13. Outcome regression and standardization/g-formula run for the supported static binary contrast.
14. IPW runs with propensity diagnostics, weight diagnostics, and effective sample size.
15. Doubly robust estimation runs for the supported static binary contrast and documents its nuisance-model limitations.
16. At least one subgroup-effect/CATE view includes support and model-dependence warnings.
17. Seven operational protocols are represented in the simulator and policy layer with explicit eligibility rules.
18. The policy layer clearly labels causal estimates, policy values, and structural simulation results as different quantities.
19. The allocator never violates hard capacity, budget, safety, or security constraints in automated tests.
20. Infeasible allocation requests are reported explicitly rather than silently relaxed.
21. Cyberattack and vandalism scenarios contain only abstract synthetic operational details and no exploit guidance.
22. The ground-truth oracle is unavailable to ordinary estimators and normal user mode.
23. Re-running the same seed, scenario, generator version, and schema version reproduces the same data and results.
24. Required visualizations are present, labelled, and interpretable without relying on color alone.
25. Documentation identifies what is implemented, conceptually demonstrated, and deferred; it does not claim unsupported source access or methodological coverage.
26. README, data dictionary, assumptions, limitations, causal questions, visualization guide, provenance, and source notes are complete and consistent with the reconciled design and requirements.

## Explicitly deferred from V1

Instrumental variables, causal survival analysis, mediation, time-varying treatment, treatment-confounder feedback, marginal structural models, g-estimation, a second industry adapter, R validation, Rust implementation, real system integration, and autonomous incident response.
