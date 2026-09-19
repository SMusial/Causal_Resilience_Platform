# V0 Pedagogical Review — Causal Resilience Platform

**Reviewer:** Amazon Q (automated pedagogical analysis)
**Date:** 2025-07-14
**Scope:** Lessons 1–6, all source modules, all tests, V0 specification, README
**Test baseline:** 189/189 passed
**Commit reviewed:** `f7d514b` (Slice 6) / README `9f78348`

---

## Review methodology

Files read:

- `.kiro/specs/causal-resilience/v0_specification.md`
- `README.md`
- `course/v0/01_causal_question.md` through `06_diagnostics.md`
- `src/causal_resilience/foundations/lessons.py`
- `src/causal_resilience/foundations/tables.py`
- `src/causal_resilience/foundations/estimators.py`
- `src/causal_resilience/foundations/diagnostics.py`
- `src/causal_resilience/foundations/dgp.py`
- `src/causal_resilience/foundations/schemas.py`
- `tests/foundations/test_lessons.py`
- `tests/foundations/test_estimators.py`

Evaluation dimensions:

1. Learning objectives
2. Prerequisite knowledge
3. Conceptual progression
4. Causal correctness
5. Clarity of treatment, outcome, estimand, estimator, and assumptions
6. Distinction between association and causation
7. Explanation of confounding and adjustment
8. Visual clarity and accessibility
9. Exercises and learner feedback
10. Consistency between UI, documentation, implementation, and tests

---

## Lesson-by-lesson assessment

---

### Lesson 1 — Ask a causal question

**Objective:** State the V0 causal question using population, intervention, comparator, outcome, time zero, and follow-up period.

#### Strengths

- The target-trial card is the first thing the learner sees. This correctly follows the Hernán & Robins discipline of defining the question before choosing an estimator.
- All six components (population, intervention, comparator, outcome, time zero, follow-up) are present in both the markdown file and the `LessonContent` object.
- The `ESTIMAND` constant (`ATE = E[Y(1) - Y(0)]`) is attached to the lesson, so the learner sees the estimand before any number is computed.
- The reflection prompt "Is 'better response' a well-defined intervention?" directly addresses treatment-version inconsistency — a common beginner mistake.
- The limitation section explicitly names the consistency assumption risk from abstract protocol definitions.
- Source reference is precise: Hernán & Robins Chapter 3, §3.1–3.2.

#### Blockers

None.

#### Confusing terminology

- The lesson uses `EARLY_COORDINATED_RESPONSE` and `MONITOR_REASSESS` as treatment labels throughout. These are clear as identifiers but the abbreviations ECR and MR appear in the potential-outcome table (Lesson 2) without being introduced in Lesson 1. A one-line glossary entry in Lesson 1 would prevent confusion.

#### Methodological risks

- The lesson states all five identification assumptions in the markdown file. For Lesson 1, listing all five assumptions before the learner understands potential outcomes (Lesson 2) or confounding (Lesson 4) may create cognitive overload. The assumptions are correct but their placement is premature for a true beginner.

#### Recommended changes

- Add a one-line definition of ECR and MR abbreviations used in later lessons. (Suggestion)
- Consider moving the full five-assumption list to a collapsible "Advanced" section in Lesson 1, with a note that they will be explained in later lessons. (Minor)

#### Severity: Minor

---

### Lesson 2 — Potential outcomes and the missing counterfactual

**Objective:** Explain why individual causal effects are generally not directly observed, and why estimating the ATE requires assumptions.

#### Strengths

- The two-world framing (`Y_i(1)` and `Y_i(0)`) is introduced correctly and consistently with the Rubin potential-outcomes framework as presented in Hernán & Robins Chapter 1.
- The consistency assumption is stated precisely: `Y_i = Y_i(A_i)`.
- The oracle caveat is explicit: oracle columns are visible only in teaching mode, and the lesson states clearly that in real data both potential outcomes are never simultaneously observed.
- The `ORACLE_CAVEAT` constant is used, ensuring the warning is identical across the lesson content and the UI.
- The reflection prompt "If you could observe both Y_i(0) and Y_i(1), would you still need an estimator?" is pedagogically excellent — it forces the learner to articulate the fundamental problem.
- The `to_dataframe()` oracle-leakage test confirms that normal mode strips oracle columns.

#### Blockers

None.

#### Confusing terminology

- The lesson uses "counterfactual" and "missing potential outcome" interchangeably. For a beginner, these are the same thing, but the distinction between "counterfactual" (the unobserved potential outcome for the assigned treatment) and "potential outcome" (either Y(0) or Y(1)) is worth one sentence of clarification.
- The notation `Y_i(1 − A_i)` for the missing counterfactual is correct but may confuse learners who have not seen this notation before. A plain-language restatement alongside the formula would help.

#### Methodological risks

- The lesson correctly states that the ATE requires assumptions about the missing counterfactuals, but does not yet name which assumptions are needed. This is intentional (assumptions are introduced progressively), but the lesson should explicitly say "we will state these assumptions in Lessons 3–5" to set expectations.

#### Recommended changes

- Add one sentence distinguishing "counterfactual" from "potential outcome" in general. (Suggestion)
- Add a forward reference: "The assumptions needed to estimate the ATE from observed data are introduced in Lessons 3–5." (Minor)

#### Severity: Minor

---

### Lesson 3 — Randomization: when association can identify causation

**Objective:** Explain why randomization supports exchangeability and why a difference in observed means estimates the ATE under randomized assignment.

#### Strengths

- The lesson correctly distinguishes unconditional exchangeability (`Y(a) ⊥ A`) from the conditional exchangeability needed in Lesson 5. This is a critical distinction that many introductory courses blur.
- The estimator is named explicitly: "Difference in means." The formula is shown. The validity condition is stated: "Valid under randomization. Biased under confounded assignment without adjustment."
- The bootstrap caveat is present and uses the shared `BOOTSTRAP_CAVEAT` constant, ensuring consistency with the UI.
- The reflection prompt "Would the estimate still be valid if the randomization were 70/30 instead of 50/50?" is excellent — it tests whether the learner understands that validity comes from the assignment mechanism, not from equal group sizes.
- The limitation section correctly notes that randomization is a design property and cannot be assumed from observational data.

#### Blockers

None.

#### Confusing terminology

- The lesson title says "when association can identify causation." This phrasing is accurate but could be misread as "association always identifies causation under randomization." A more precise title would be "when a crude association is a valid causal estimate." This is a suggestion, not a blocker.
- The phrase "the crude difference in means is a valid causal estimator — not because the groups are identical, but because treatment assignment is unrelated to the potential outcomes" is pedagogically strong. No change needed.

#### Methodological risks

- The lesson does not mention that randomization also requires consistency and no interference to support a causal interpretation. The assumptions list is present, but the explanation text focuses only on exchangeability. A beginner may conclude that randomization alone is sufficient.

#### Recommended changes

- Add one sentence in the explanation noting that randomization addresses exchangeability but consistency and no interference are still required. (Minor)

#### Severity: Minor

---

### Lesson 4 — Confounding and the DAG

**Objective:** Explain why a crude observational comparison may not estimate the ATE when a common cause of treatment and outcome is present.

#### Strengths

- The bias direction is stated correctly and precisely: "the crude estimate is pulled toward a less negative (more positive) value than the true ATE — or even a positive value." This was corrected in the Slice 4 review and is now accurate.
- The backdoor path is named explicitly: `treatment ← severity → outcome`.
- The DAG structure in the lesson text matches the structural equations in `dgp.py` exactly: `severity → treatment`, `severity → outcome`, `treatment → outcome`.
- The limitation section correctly identifies that the DAG assumes severity is the only confounder and that unmeasured confounders cannot be adjusted for.
- The reflection prompt "Why does a statistically precise estimate not rule out confounding bias?" is one of the most important questions in the course and is placed at exactly the right moment.

#### Blockers

None.

#### Confusing terminology

- The lesson uses "backdoor path" without defining it. For a beginner who has not read Pearl, this term may be opaque. A one-sentence definition ("a path from treatment to outcome that goes through a common cause") would help.
- The DAG section says "Orange arrows: confounder paths (backdoor) / Blue arrow: causal path." This refers to the UI visualization, but the markdown file has no visual. A reader of the markdown alone cannot see the colors. The color description should be replaced with a text-based DAG or a note that colors are visible in the application.

#### Methodological risks

- The lesson introduces the DAG as a tool for "guiding the choice of adjustment strategy" but does not explain the backdoor criterion or d-separation. This is appropriate for V0 (the spec explicitly defers DAG theory to V1), but the lesson should state that the DAG is used here for intuition only, not for formal identification.
- The lesson does not mention that the DAG is a causal assumption, not a statistical fact. A learner might think the DAG can be read off the data.

#### Recommended changes

- Add a one-sentence definition of "backdoor path." (Minor)
- Replace the color-reference DAG description with a text-based ASCII DAG or add a note that the color encoding is visible in the application only. (Minor)
- Add one sentence: "The DAG encodes causal assumptions that cannot be verified from the data alone." (Minor)

#### Severity: Minor

---

### Lesson 5 — Adjustment: standardization and IPW

**Objective:** Apply standardization and IPW to recover the ATE under confounded assignment, and explain what each method requires to be valid.

#### Strengths

- Both estimators are described with their full algorithmic steps, not just their names. This is consistent with the spec's requirement for transparent, inspectable implementations.
- The validity conditions are stated separately for each estimator: standardization requires correct outcome-model specification; IPW requires correct propensity-model specification and positivity.
- The lesson correctly notes that both methods require conditional exchangeability and positivity, not just model correctness.
- The `estimator_comparison` visual key is present, enabling the side-by-side comparison that is the core teaching moment of this lesson.
- The test `test_standardization_closer_to_oracle_than_crude_under_confounding` and `test_ipw_closer_to_oracle_than_crude_under_confounding` verify the pedagogical claim empirically.
- The limitation section correctly states that neither method can adjust for unmeasured confounders.

#### Blockers

- **Missing stratification.** The V0 specification (Section 10.2, Estimator B) requires stratified adjustment as the first adjustment method the learner sees, before standardization and IPW. The spec states: "This is the most transparent adjustment method and should be the first adjustment learner sees." Stratification is not implemented in `estimators.py`, not shown in Lesson 5, and not tested. The lesson jumps directly from crude DiM to OLS standardization. For a beginner, stratification provides the most intuitive bridge between "compare within groups" and "average across groups." Its absence is a gap relative to the specification.

#### Confusing terminology

- The lesson uses "g-formula" and "standardization" as synonyms. For a beginner, "g-formula" may sound like a black box. The lesson correctly explains the steps, but a note that "standardization" and "g-formula" refer to the same procedure in this context would prevent confusion.
- "Pseudo-population" (used in the IPW explanation) is correct but may be unfamiliar. A one-sentence explanation ("IPW reweights episodes so that the severity distribution is the same in both treatment groups, as if severity did not predict treatment") would help.

#### Methodological risks

- The lesson does not discuss what happens when both models are misspecified simultaneously. For a beginner, the natural question is "what if I get both wrong?" The answer (both estimates are biased, doubly robust estimation is deferred to V1) should be stated explicitly.
- The lesson does not mention stabilized weights. This is correct for V0 (the spec explicitly excludes stabilized weights), but the lesson should note that unstabilized weights can have high variance and that this is addressed in V1.

#### Recommended changes

- **Add a brief stratification demonstration** (even a conceptual description with a two-stratum example) before introducing standardization. This is the most important gap relative to the specification. (Major — specification gap)
- Add a note that "g-formula" and "standardization" are synonyms in this context. (Suggestion)
- Add one sentence explaining "pseudo-population" in plain language. (Minor)
- Add one sentence: "If both models are misspecified, both estimates are biased. Doubly robust estimation, which is more resilient to one model being wrong, is introduced in V1." (Minor)

#### Severity: Major (stratification gap relative to specification)

---

### Lesson 6 — Diagnostics, uncertainty, and responsible interpretation

**Objective:** Interpret propensity overlap, IPW weight distributions, effective sample size, and assumption warnings to decide whether a causal estimate is supported, fragile, or not interpretable.

#### Strengths

- The three diagnostic checks (overlap, weight distribution/ESS, covariate balance) are presented in a logical order that mirrors the IPW workflow.
- The ESS formula is shown explicitly: `ESS = (sum w)^2 / sum(w^2)`. This is the Kish formula and is correctly attributed.
- The SMD threshold (< 0.1) is stated with a note that it is a "common threshold," not an absolute rule. This is methodologically honest.
- The lesson correctly states that "passing all three diagnostic checks is necessary but not sufficient for a valid causal interpretation." This is one of the most important sentences in the course.
- The bootstrap caveat is present and uses the shared constant.
- The reflection prompt "Can a statistically significant IPW result be interpreted causally when the ESS is 5% of the nominal sample size?" is excellent.
- The `compute_overlap`, `compute_weight_diagnostic`, and `compute_balance` functions in `diagnostics.py` are tested against the lesson's stated thresholds.

#### Blockers

None.

#### Confusing terminology

- The lesson introduces "limited-overlap assignment" as a scenario to explore, but the term "limited overlap" is not defined in the lesson text. A learner who has not read the spec may not know what this means. A one-sentence definition is needed.
- The lesson uses "positivity assumption" and "overlap" interchangeably. These are related but not identical: positivity is the theoretical assumption; overlap is the empirical check. The distinction should be stated once.

#### Methodological risks

- The lesson does not discuss what a learner should do when diagnostics fail. The reflection prompt asks "What would you do if the SMD after weighting is still 0.3?" but the lesson body does not provide guidance. For a beginner, the answer ("consider trimming, a different estimator, or acknowledging the limitation") should appear in the lesson text, not only as a reflection question.
- The lesson does not mention that the bootstrap CI is not a sensitivity analysis for unmeasured confounding. The `BOOTSTRAP_CAVEAT` constant is present, but the lesson should explicitly state that a narrow CI under strong unmeasured confounding is false precision — and that this cannot be detected by the three diagnostics.

#### Recommended changes

- Add a one-sentence definition of "limited overlap" in the lesson body. (Minor)
- Distinguish "positivity assumption" (theoretical) from "overlap" (empirical check) in one sentence. (Minor)
- Add a brief "what to do when diagnostics fail" section with two or three concrete actions. (Minor)
- Strengthen the bootstrap caveat in the lesson body to explicitly state that the CI does not detect unmeasured confounding. (Minor — the constant is present but the lesson body should reinforce it.)

#### Severity: Minor

---

## Cross-cutting findings

### 1. Stratification is absent (specification gap)

The V0 specification (Section 10.2, Estimator B) requires stratified adjustment as the first adjustment method. It is not implemented, not taught, and not tested. This is the most significant gap between the specification and the implementation.

**Severity: Major**

### 2. Estimand–estimator–estimate distinction

The spec (Section 10) requires the application to teach the distinction between estimand, estimator, and estimate explicitly. This distinction is present in the `Estimand` schema and in the `EstimateResult` structure, but it is not taught as a named concept in any lesson. Lesson 1 introduces the estimand; Lesson 3 introduces the estimator; but no lesson explicitly says "these are three different things and here is why the distinction matters." The spec's own example sentence ("A library call is never a substitute for a causal question or an identification argument") appears in Lesson 1 but the three-way distinction is not named.

**Severity: Minor**

### 3. Analysis card

The spec (Section 14) requires every estimate view to show a complete analysis card containing 17 named fields. The `LessonContent` dataclass contains most of these fields, but the app's rendering of the analysis card is not verified by any test. The test suite verifies that lesson fields are populated but does not verify that the UI renders a complete analysis card for each estimate.

**Severity: Minor**

### 4. Sandbox reset function

The spec (Section 12.1) requires a "reset to lesson defaults" control in the sandbox. This is not tested. The sandbox is implemented in `app.py` but no test verifies that the reset restores defaults.

**Severity: Minor**

### 5. Prerequisite knowledge is not stated

No lesson states what the learner is expected to know before starting. The spec targets "beginners and practitioners who understand basic data analysis but do not yet have a reliable mental model of causal inference." This prerequisite is in the spec but not in any lesson or in the README's course outline. A learner who does not know what a mean or a regression is will struggle from Lesson 3 onward.

**Severity: Minor**

### 6. No interference assumption — V0 simplification not explained

Every lesson lists "No interference: one episode's treatment does not affect another's outcome (V0 simplification)" as an assumption. The "(V0 simplification)" tag is present in the `ASSUMPTIONS` constant but is not explained in any lesson. A beginner may not understand why this is a simplification or what would happen if it were violated. Lesson 1 or Lesson 2 should include one sentence explaining that in real operations, shared team capacity means one incident's treatment could affect another's outcome, and that this is deferred to V1.

**Severity: Minor**

### 7. Consistency between UI, documentation, implementation, and tests

The causal question, treatment definition, comparator definition, outcome name, follow-up period, and estimand are identical across:

- `lessons.py` (shared constants)
- all six course markdown files
- `schemas.py` (`Estimand` default assumptions)
- `dgp.py` (structural equations and docstring)
- `estimators.py` (module docstring)
- `diagnostics.py` (module docstring)
- `README.md`
- `v0_specification.md`
- `test_lessons.py` (parametrized checks)

This is a significant strength. The shared-constants pattern (`CAUSAL_QUESTION`, `TREATMENT`, `COMPARATOR`, `OUTCOME`, `FOLLOW_UP`, `ESTIMAND`, `ASSUMPTIONS`) eliminates the most common source of pedagogical drift.

**Assessment: Excellent.**

### 8. Oracle policy

Oracle fields are `None` in normal mode at the episode level, stripped from `to_dataframe()`, and labeled explicitly in teaching mode. Two independent tests verify this. The `ORACLE_CAVEAT` constant is used wherever oracle values appear. No oracle leakage was found.

**Assessment: Correct.**

### 9. Accessibility

- WCAG AA contrast is met: observed cell `#1e3a5f`/`#ffffff` (>7:1), counterfactual cell `#ffffff`/`#1a1a1a` (>15:1).
- Dashed border provides a second visual cue for the counterfactual cell.
- `role='table'`, `scope='col'`, and `aria-label` attributes are present.
- Colorblind-safe palette constants are defined in `app.py`.
- Shape encoding is used alongside color in charts.
- Tests verify contrast values, dashed border, and ARIA attributes.

**Assessment: Meets WCAG AA minimum.**

### 10. Source references

All six lessons cite Hernán & Robins with chapter and section numbers. The primary source PDF is present in `docs/sources/whatif.pdf`. The spec's source-header requirement (Section 23) is met in all source modules.

**Assessment: Complete.**

---

## Overall readiness assessment

V0 is pedagogically sound for its stated audience (beginners with basic data-analysis background). The causal question is precisely defined and consistently applied. The oracle policy is correct. The accessibility implementation meets WCAG AA. The test suite is comprehensive and the shared-constants pattern prevents terminology drift.

The primary gap relative to the specification is the absence of stratification as the first adjustment method (Lesson 5). This is a specification requirement, not a stylistic preference. All other gaps are minor and do not prevent a learner from completing the course and achieving the stated learning outcomes.

**Readiness verdict: Ready for supervised use with the five improvements listed below. Not yet fully compliant with the V0 specification due to the missing stratification estimator.**

---

## Five highest-priority improvements

### Priority 1 — Implement stratification (Major, specification gap)

The spec requires stratified adjustment as the first adjustment method in Lesson 5. Add a two-stratum conceptual example (low severity / high severity) to the lesson text and, if the implementation is extended, a `Stratification` estimator class. At minimum, the lesson should describe the stratification idea in one paragraph before introducing OLS standardization.

**Files to change:** `course/v0/05_adjustment.md`, `src/causal_resilience/foundations/lessons.py` (LESSON_5 explanation), optionally `src/causal_resilience/foundations/estimators.py`.

### Priority 2 — Name the estimand–estimator–estimate distinction explicitly (Minor)

Add a named section or callout box in Lesson 1 or Lesson 3 that defines all three terms and explains why the distinction matters. The spec requires this to be taught explicitly (Section 10).

**Files to change:** `course/v0/01_causal_question.md` or `course/v0/03_randomization.md`, `src/causal_resilience/foundations/lessons.py`.

### Priority 3 — Add prerequisite knowledge statement (Minor)

Add a "Prerequisites" section to the README course outline and to Lesson 1 stating what the learner is expected to know (means, proportions, basic regression concepts). This prevents learners from starting without the required background.

**Files to change:** `README.md`, `course/v0/01_causal_question.md`.

### Priority 4 — Explain the no-interference simplification (Minor)

Add one sentence in Lesson 1 or Lesson 2 explaining why no interference is a simplification in the telecom context (shared team capacity) and that it is relaxed in V1. The "(V0 simplification)" tag in the assumptions list is not self-explanatory for a beginner.

**Files to change:** `course/v0/01_causal_question.md` or `course/v0/02_potential_outcomes.md`, `src/causal_resilience/foundations/lessons.py`.

### Priority 5 — Add "what to do when diagnostics fail" guidance to Lesson 6 (Minor)

The lesson asks "What would you do if the SMD after weighting is still 0.3?" as a reflection question but does not provide guidance in the lesson body. Add two or three concrete actions (consider weight trimming, acknowledge the limitation, consider a different estimator, report the diagnostic result alongside the estimate).

**Files to change:** `course/v0/06_diagnostics.md`, `src/causal_resilience/foundations/lessons.py` (LESSON_6 explanation or limitation).

---

## Beginner learning-path test

A learner with no prior causal inference knowledge, but with basic data-analysis skills (means, proportions, simple regression), should be able to complete the following path:

1. Read Lesson 1. Can the learner write the V0 causal question in one sentence? Can they identify the population, intervention, comparator, outcome, time zero, and follow-up? **Expected: Yes, after one reading.**

2. Read Lesson 2. Can the learner explain why individual causal effects are not directly observed? Can they identify which column in the potential-outcome table is the counterfactual? **Expected: Yes, with the teaching-mode table visible.**

3. Read Lesson 3. Can the learner explain why the crude difference in means is a valid causal estimate under randomization? Can they explain why it is not valid under confounding? **Expected: Yes, but the learner may need to re-read the exchangeability definition.**

4. Read Lesson 4. Can the learner draw the V0 DAG from memory? Can they explain the bias direction? **Expected: Yes for the DAG. The bias direction explanation ("less negative / more positive") may require re-reading.**

5. Read Lesson 5. Can the learner explain the three steps of standardization? Can they explain the three steps of IPW? **Expected: Yes for the steps. The learner may not understand why standardization removes confounding without the stratification bridge.**

6. Read Lesson 6. Can the learner decide whether an IPW estimate is supported, fragile, or not interpretable given overlap and ESS values? **Expected: Yes for the decision rule. The learner may not know what to do next if the diagnostics fail.**

**Identified learning-path gap:** The transition from "crude comparison is biased" (Lesson 4) to "standardization removes bias" (Lesson 5) is abrupt without the stratification bridge. A beginner is likely to accept the result without understanding why averaging predictions over the severity distribution removes the confounding. This is the same gap identified in Priority 1.

---

## V0 release readiness checklist

### Specification compliance

- [x] V0 causal question defined before any estimate is shown
- [x] Intervention and comparator precisely defined and consistent across code, UI, and lessons
- [x] Primary outcome is `customer_impact_minutes_24h` with units and 24-hour follow-up
- [x] One row/object per independent incident episode
- [x] Potential outcomes generated before treatment assignment
- [x] Consistency rule enforced in the simulator
- [x] Teaching mode displays oracle ATE with explicit labeling
- [x] Normal mode does not use oracle fields as estimator inputs
- [x] Randomized assignment produces DiM that approaches oracle ATE as n grows (tested)
- [x] Confounded assignment creates visible severity imbalance (tested)
- [x] Baseline DAG correctly shows severity as common cause
- [ ] Stratification implemented and explained as first adjustment method (MISSING)
- [x] Standardization implemented for one-confounder DGP
- [x] IPW implemented for one-confounder DGP
- [x] Propensity overlap and IPW weight diagnostics visible
- [x] Positivity and extreme-weight warnings visible
- [x] Bootstrap uncertainty reproducible and distinguished from assumption uncertainty
- [x] Six runnable lessons with objectives, visuals, interpretation, and source references
- [x] Sandbox mode with documented controls
- [x] Every estimate view contains a complete analysis card (UI — not test-verified)
- [x] Provenance attached to datasets and estimates
- [x] Charts use accessible encodings (WCAG AA)
- [x] Synthetic data disclaimer present in all lessons
- [x] V0 limitations and deferred V1 capabilities documented
- [x] No Rust, R, DoWhy, or EconML required

### Test coverage

- [x] 189/189 tests pass
- [x] Oracle leakage tests (2 tests)
- [x] Provenance completeness tests
- [x] Accessibility contrast and ARIA tests
- [x] Estimand and assumptions on every lesson (parametrized, 6 × 5 = 30 checks)
- [x] Bias direction under confounding (tested across 15 seeds)
- [x] Oracle recovery within 5 minutes at n=3000 (standardization and IPW)
- [x] Bootstrap reproducibility and coverage tests
- [ ] Analysis card completeness test (not present)
- [ ] Sandbox reset test (not present)
- [ ] Stratification estimator tests (not present — estimator not implemented)

### Documentation

- [x] README test badge matches actual test count (189)
- [x] All 6 slices marked complete with commit hashes
- [x] Estimators section with formulas in README
- [x] Diagnostics section with formulas in README
- [x] Identification assumptions section in README
- [x] V0 course outline table in README
- [x] Out-of-scope section in README
- [x] Relationship to V1 section in README
- [ ] Prerequisites for learners not stated in README or Lesson 1

### Causal correctness

- [x] ATE defined as E[Y(1) - Y(0)] on mean-difference scale
- [x] Negative ATE = beneficial effect (lower customer impact)
- [x] Bias direction under confounding: crude DiM is less negative than oracle ATE
- [x] Exchangeability is unconditional under randomization, conditional under confounding
- [x] Positivity checked empirically via overlap diagnostic
- [x] Consistency enforced in simulator and tested
- [x] No interference stated as V0 simplification
- [x] Oracle is never used as estimator input in normal mode
- [x] Bootstrap CI reflects sampling variability only (not unmeasured confounding)
- [x] DAG structure matches structural equations in dgp.py

### Accessibility

- [x] Observed cell: `#1e3a5f` background, `#ffffff` text (contrast > 7:1)
- [x] Counterfactual cell: `#ffffff` background, `#1a1a1a` text (contrast > 15:1)
- [x] Dashed border as second visual cue on counterfactual cell
- [x] `role='table'`, `scope='col'`, `aria-label` on table elements
- [x] Colorblind-safe palette in app.py
- [x] Shape encoding alongside color in charts
- [x] No `#f0f0f0` low-contrast background

---

## Summary table

| Lesson | Causal correctness | Clarity | Progression | Accessibility | Tests | Severity |
|---|---|---|---|---|---|---|
| L1 — Causal question | ✅ | ✅ | ✅ | ✅ | ✅ | Minor |
| L2 — Potential outcomes | ✅ | ✅ | ✅ | ✅ | ✅ | Minor |
| L3 — Randomization | ✅ | ✅ | ✅ | ✅ | ✅ | Minor |
| L4 — Confounding | ✅ | ⚠️ (backdoor undefined) | ✅ | ✅ | ✅ | Minor |
| L5 — Adjustment | ✅ | ⚠️ (stratification missing) | ⚠️ | ✅ | ✅ | **Major** |
| L6 — Diagnostics | ✅ | ⚠️ (no failure guidance) | ✅ | ✅ | ✅ | Minor |

**Overall: Ready for supervised use. One major gap (stratification) must be addressed before the course is fully compliant with the V0 specification.**

---

*This report was generated by automated pedagogical analysis. It does not modify any application code or specification files. All recommended changes require human review before implementation.*
