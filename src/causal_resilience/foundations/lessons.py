"""
causal_resilience.foundations.lessons
=======================================
V0 Slice 3/5/6 — Course lesson content for all six lessons.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 1 — causal effects, potential outcomes, individual and average effects
  Chapter 2 — randomization, standardization, IPW
  Chapter 3 — target trial, estimand, time zero, follow-up
  Chapter 6 — DAGs, confounding, backdoor paths

Causal question: ATE = E[Y(1) - Y(0)]
Estimand: population average treatment effect on the mean-difference scale.
Assumptions: consistency, exchangeability, positivity, no interference,
  complete follow-up.
Implementation type: educational content layer — no estimator logic.
Ground-truth validation: tests/foundations/test_lessons.py
Textbook/software difference: none.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Shared constants — used across lessons and tests
# ---------------------------------------------------------------------------

CAUSAL_QUESTION = (
    "Among eligible synthetic telecom incidents at detection, what is the "
    "average effect of assigning EARLY_COORDINATED_RESPONSE rather than "
    "MONITOR_REASSESS on customer_impact_minutes_24h during the following "
    "24 hours?"
)

TREATMENT = "EARLY_COORDINATED_RESPONSE — predefined coordination protocol within 15 min of detection"
COMPARATOR = "MONITOR_REASSESS — monitor and reassess at the 60-minute checkpoint"
OUTCOME = "customer_impact_minutes_24h — total customer-impact minutes over 24 hours (lower is better)"
FOLLOW_UP = "24 hours from first reliable detection timestamp"
ESTIMAND = "ATE = E[Y(1) - Y(0)] on the mean-difference scale"

ASSUMPTIONS = [
    "Consistency: observed outcome equals potential outcome under assigned treatment.",
    "Exchangeability: Y(a) ⊥ A | severity (conditional on measured severity).",
    "Positivity: 0 < P(A=1 | severity=l) < 1 for all l in the target population.",
    "No interference: one episode's treatment does not affect another's outcome (V0 simplification).",
    "Complete follow-up: 24-hour outcome is observed for all eligible episodes (V0 simplification).",
]

SYNTHETIC_DATA_DISCLAIMER = (
    "All data are entirely synthetic and illustrative. "
    "Results do not represent real telecom operations, real organizations, "
    "or real interventions."
)

BOOTSTRAP_CAVEAT = (
    "The 95% bootstrap CI reflects sampling variability only. "
    "It does not quantify uncertainty from unmeasured confounding. "
    "A narrow CI under strong unmeasured confounding is false precision."
)

ORACLE_CAVEAT = (
    "The oracle ATE is available only because the data are synthetic. "
    "In real data, both potential outcomes are never simultaneously observed."
)


# ---------------------------------------------------------------------------
# Lesson content schema
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LessonContent:
    """Structured content for one course lesson."""
    lesson_id: str
    title: str
    objective: str
    causal_question: str            # the V0 causal question (consistent across lessons)
    treatment: str                  # intervention definition
    comparator: str                 # comparator definition
    outcome: str                    # outcome name, units, direction
    follow_up: str                  # follow-up period
    estimand: str                   # target estimand
    assumptions: list[str]          # identification assumptions
    explanation: str
    visual_keys: list[str]          # keys consumed by the Streamlit page
    estimator_or_diagnostic: str    # what the learner computes or observes
    interpretation: str
    limitation: str                 # key limitation for this lesson
    reflection: str
    source_reference: str


# ---------------------------------------------------------------------------
# Lesson 1 — Ask a causal question
# ---------------------------------------------------------------------------

LESSON_1 = LessonContent(
    lesson_id="L1",
    title="Ask a causal question",
    objective=(
        "State the V0 causal question using population, intervention, "
        "comparator, outcome, time zero, and follow-up period."
    ),
    causal_question=CAUSAL_QUESTION,
    treatment=TREATMENT,
    comparator=COMPARATOR,
    outcome=OUTCOME,
    follow_up=FOLLOW_UP,
    estimand=ESTIMAND,
    assumptions=ASSUMPTIONS,
    explanation=(
        "A causal question is not the same as a prediction question. "
        "Prediction asks: given what we observe, what will happen? "
        "Causation asks: if we intervene and change something, what would happen?\n\n"
        "Before choosing any estimator or running any analysis, we must define:\n"
        "  \u2022 Population \u2014 who are we studying?\n"
        "  \u2022 Intervention \u2014 what action are we evaluating?\n"
        "  \u2022 Comparator \u2014 what is the alternative?\n"
        "  \u2022 Outcome \u2014 what do we measure?\n"
        "  \u2022 Time zero \u2014 when does follow-up begin?\n"
        "  \u2022 Follow-up \u2014 how long do we observe?\n\n"
        "The V0 question is:\n"
        "  Among eligible synthetic telecom incidents at detection, what is the "
        "average effect of assigning EARLY_COORDINATED_RESPONSE rather than "
        "MONITOR_REASSESS on customer_impact_minutes_24h during the following "
        "24 hours?\n\n"
        "Source: Hern\u00e1n & Robins, What If, Chapter 3 \u2014 target trial."
    ),
    visual_keys=["target_trial_card", "treatment_timeline"],
    estimator_or_diagnostic=(
        "Read the target-trial card. Identify each component of the causal "
        "question. Notice that no number has been computed yet \u2014 the question "
        "must be defined before any estimator is chosen."
    ),
    interpretation=(
        "The target-trial card makes the causal question precise. "
        "Vague language such as 'the effect of resilience' or 'better response' "
        "cannot be estimated. A well-defined intervention and comparator can."
    ),
    limitation=(
        "The intervention definition is deliberately abstract. In real operations, "
        "treatment-version inconsistency \u2014 different teams executing the protocol "
        "differently \u2014 would violate the consistency assumption and bias any estimate."
    ),
    reflection=(
        "Can you restate the V0 causal question in one sentence without using "
        "the words 'impact', 'resilience', or 'performance'? "
        "What would change if the follow-up period were 48 hours instead of 24?"
    ),
    source_reference="Hern\u00e1n & Robins, What If, Chapter 3 (target trial, \u00a73.1\u20133.2)",
)


# ---------------------------------------------------------------------------
# Lesson 2 — Potential outcomes and the missing counterfactual
# ---------------------------------------------------------------------------

LESSON_2 = LessonContent(
    lesson_id="L2",
    title="Potential outcomes and the missing counterfactual",
    objective=(
        "Explain why individual causal effects are generally not directly "
        "observed, and why the average treatment effect requires assumptions."
    ),
    causal_question=CAUSAL_QUESTION,
    treatment=TREATMENT,
    comparator=COMPARATOR,
    outcome=OUTCOME,
    follow_up=FOLLOW_UP,
    estimand=ESTIMAND,
    assumptions=ASSUMPTIONS,
    explanation=(
        "For each incident episode i, there are two potential outcomes:\n"
        "  Y_i(1) \u2014 customer impact if the episode receives EARLY_COORDINATED_RESPONSE\n"
        "  Y_i(0) \u2014 customer impact if the episode receives MONITOR_REASSESS\n\n"
        "The individual causal effect is Y_i(1) \u2212 Y_i(0).\n\n"
        "The fundamental problem of causal inference: we can only observe one "
        "of the two potential outcomes for each episode. The other is the "
        "counterfactual \u2014 what would have happened under the alternative.\n\n"
        "In teaching mode, the simulator knows both potential outcomes. "
        "In normal analysis, only the observed outcome is available.\n\n"
        "The average treatment effect (ATE) is:\n"
        "  ATE = E[Y(1) \u2212 Y(0)] = E[Y(1)] \u2212 E[Y(0)]\n\n"
        "Estimating the ATE from observed data requires assumptions about "
        "the missing counterfactuals.\n\n"
        "Source: Hern\u00e1n & Robins, What If, Chapter 1 \u2014 individual and average "
        "causal effects, \u00a71.1\u20131.2."
    ),
    visual_keys=["potential_outcome_table", "missing_counterfactual_chart"],
    estimator_or_diagnostic=(
        "In teaching mode: inspect the two-world table showing Y(0) and Y(1) "
        "for a small sample. Observe that the observed outcome matches the "
        "assigned treatment. The other column is the missing counterfactual.\n"
        "In normal mode: the oracle columns are hidden. Only the observed "
        "outcome is available for estimation."
    ),
    interpretation=(
        "The oracle ATE is the mean of Y(1) \u2212 Y(0) computed directly from "
        "the simulator's hidden truth. In real data, this quantity is never "
        "available. The teaching simulator exposes it only to help you "
        "understand what estimators are trying to recover."
    ),
    limitation=(
        "The oracle is available only because the data are synthetic. "
        "In real data, both potential outcomes are never simultaneously observed "
        "for the same episode. Any estimator must rely on assumptions about "
        "the missing counterfactual."
    ),
    reflection=(
        "If you could observe both Y_i(0) and Y_i(1) for every episode, "
        "would you still need an estimator? "
        "Why does the consistency assumption matter for connecting potential "
        "outcomes to observed data?"
    ),
    source_reference="Hern\u00e1n & Robins, What If, Chapter 1 (\u00a71.1\u20131.2)",
)


# ---------------------------------------------------------------------------
# Lesson 3 — Randomization: when association can identify causation
# ---------------------------------------------------------------------------

LESSON_3 = LessonContent(
    lesson_id="L3",
    title="Randomization: when association can identify causation",
    objective=(
        "Explain why randomization supports exchangeability and why a "
        "difference in observed means estimates the ATE under randomization."
    ),
    causal_question=CAUSAL_QUESTION,
    treatment=TREATMENT,
    comparator=COMPARATOR,
    outcome=OUTCOME,
    follow_up=FOLLOW_UP,
    estimand=ESTIMAND,
    assumptions=ASSUMPTIONS,
    explanation=(
        "Under randomized assignment, treatment is allocated independently of "
        "severity and all other baseline characteristics. This means:\n"
        "  Y(a) \u22a5 A  (unconditional exchangeability)\n\n"
        "When exchangeability holds, the observed group means identify the "
        "potential-outcome means:\n"
        "  E[Y | A=1] = E[Y(1)]\n"
        "  E[Y | A=0] = E[Y(0)]\n\n"
        "So the crude difference in means estimates the ATE:\n"
        "  E[Y | A=1] \u2212 E[Y | A=0] = E[Y(1)] \u2212 E[Y(0)] = ATE\n\n"
        "Finite samples still vary \u2014 the estimate will not equal the oracle "
        "ATE exactly, but the error shrinks as sample size grows.\n\n"
        "Source: Hern\u00e1n & Robins, What If, Chapter 2 (\u00a72.1\u20132.2)."
    ),
    visual_keys=["outcome_distributions", "estimate_vs_oracle", "severity_balance"],
    estimator_or_diagnostic=(
        "Compare the difference-in-means estimate with the oracle ATE. "
        "Check the severity balance chart \u2014 under randomization the severity "
        "distributions of treated and control groups should overlap closely."
    ),
    interpretation=(
        "Under randomization the estimate tracks the oracle ATE. "
        "The severity distributions are balanced by design, not by adjustment. "
        "Remaining error is sampling variability, not confounding bias."
    ),
    limitation=(
        "The bootstrap CI reflects sampling variability only. "
        "It does not quantify uncertainty from unmeasured confounding. "
        "Randomization is a design property \u2014 it cannot be assumed from "
        "observational data."
    ),
    reflection=(
        "Why does balance on severity not need to be perfect for randomization "
        "to support a causal interpretation? "
        "What happens to the estimate as you increase the sample size?"
    ),
    source_reference="Hern\u00e1n & Robins, What If, Chapter 2 (\u00a72.1\u20132.2)",
)


# ---------------------------------------------------------------------------
# Lesson 4 — Confounding and the DAG
# ---------------------------------------------------------------------------

LESSON_4 = LessonContent(
    lesson_id="L4",
    title="Confounding and the DAG",
    objective=(
        "Explain why a crude observational comparison may not estimate the ATE "
        "when a common cause of treatment and outcome is present."
    ),
    causal_question=CAUSAL_QUESTION,
    treatment=TREATMENT,
    comparator=COMPARATOR,
    outcome=OUTCOME,
    follow_up=FOLLOW_UP,
    estimand=ESTIMAND,
    assumptions=ASSUMPTIONS,
    explanation=(
        "A confounder is a variable that is a common cause of both treatment "
        "assignment and the outcome. In the V0 scenario, severity plays this role:\n\n"
        "  severity \u2500\u2500> treatment\n"
        "  severity \u2500\u2500> outcome\n"
        "  treatment \u2500\u2500> outcome\n\n"
        "Higher-severity incidents are more likely to receive "
        "EARLY_COORDINATED_RESPONSE and also tend to have higher "
        "customer_impact_minutes_24h regardless of treatment.\n\n"
        "This creates a backdoor path: treatment \u2190 severity \u2192 outcome.\n"
        "The crude difference in means conflates the treatment effect with "
        "the severity effect, producing a biased estimate of the ATE.\n\n"
        "A directed acyclic graph (DAG) makes the confounding structure "
        "explicit and guides the choice of adjustment strategy.\n\n"
        "Source: Hern\u00e1n & Robins, What If, Chapter 6 (\u00a76.1\u20136.3)."
    ),
    visual_keys=["dag", "severity_balance", "crude_vs_oracle"],
    estimator_or_diagnostic=(
        "Switch to confounded assignment. Observe that the severity "
        "distributions diverge between treatment groups. Compare the crude "
        "difference-in-means with the oracle ATE \u2014 the gap is confounding bias."
    ),
    interpretation=(
        "Under confounded assignment, higher-severity incidents cluster in the "
        "treated group. The crude estimate is pulled toward a less negative "
        "(more positive) value than the true ATE \u2014 or even a positive value \u2014 "
        "because treated episodes would have had worse outcomes even without "
        "treatment. The raw comparison makes the intervention look less "
        "beneficial than it truly is. Adjustment for severity is required \u2014 "
        "introduced in Lesson 5."
    ),
    limitation=(
        "The DAG assumes severity is the only confounder. In real data, "
        "unmeasured confounders may exist. Adjustment for measured severity "
        "cannot remove bias from variables that were not recorded."
    ),
    reflection=(
        "If you did not know the DGP, how would you decide whether severity "
        "is a confounder? "
        "Why does a statistically precise estimate not rule out confounding bias?"
    ),
    source_reference="Hern\u00e1n & Robins, What If, Chapter 6 (\u00a76.1\u20136.3)",
)


# ---------------------------------------------------------------------------
# Lesson 5 — Adjustment: standardization and IPW
# ---------------------------------------------------------------------------

LESSON_5 = LessonContent(
    lesson_id="L5",
    title="Adjustment: standardization and IPW",
    objective=(
        "Apply outcome regression (standardization) and inverse-probability "
        "weighting to recover the ATE under confounded assignment, and explain "
        "what each method requires to be valid."
    ),
    causal_question=CAUSAL_QUESTION,
    treatment=TREATMENT,
    comparator=COMPARATOR,
    outcome=OUTCOME,
    follow_up=FOLLOW_UP,
    estimand=ESTIMAND,
    assumptions=ASSUMPTIONS,
    explanation=(
        "When exchangeability does not hold unconditionally, we must adjust "
        "for the confounder. V0 teaches two transparent methods.\n\n"
        "Standardization (g-formula):\n"
        "  1. Fit an outcome model: E[Y | A, severity] using OLS.\n"
        "  2. For every episode, predict Y_hat(1) and Y_hat(0).\n"
        "  3. ATE = mean(Y_hat(1) - Y_hat(0)).\n"
        "This averages predictions over the observed severity distribution, "
        "removing the confounding by severity.\n\n"
        "Inverse-probability weighting (IPW):\n"
        "  1. Fit a propensity model: P(A=1 | severity) using logistic regression.\n"
        "  2. Weight each episode by 1/P(A=a_i | severity_i).\n"
        "  3. ATE = weighted_mean(Y | A=1) - weighted_mean(Y | A=0).\n"
        "IPW creates a pseudo-population where severity is balanced across "
        "treatment groups, removing the backdoor path.\n\n"
        "Both methods require:\n"
        "  - Conditional exchangeability: Y(a) \u22a5 A | severity.\n"
        "  - Positivity: 0 < P(A=1 | severity=l) < 1 for all l.\n"
        "  - Correct model specification (each method for its own model).\n\n"
        "Source: Hern\u00e1n & Robins, What If, Chapter 2 (\u00a72.3\u20132.4)."
    ),
    visual_keys=[
        "estimator_comparison",
        "propensity_overlap",
        "weight_distribution",
        "severity_balance_after",
    ],
    estimator_or_diagnostic=(
        "Switch to confounded assignment. Compare the crude DiM, "
        "standardization, and IPW estimates side by side. "
        "In teaching mode, compare all three with the oracle ATE. "
        "Observe that the adjusted estimates are closer to the oracle "
        "than the crude DiM."
    ),
    interpretation=(
        "Under correctly specified models and adequate overlap, both "
        "standardization and IPW recover the oracle ATE within sampling "
        "variability. The crude DiM remains biased. The two adjusted "
        "estimators can differ when models are misspecified or overlap is "
        "limited \u2014 neither is automatically correct in real data."
    ),
    limitation=(
        "Both estimators assume the adjustment model is correctly specified. "
        "Standardization is biased if the outcome model is misspecified. "
        "IPW is biased if the propensity model is misspecified. "
        "Neither method can adjust for unmeasured confounders."
    ),
    reflection=(
        "If the outcome model is misspecified (e.g., the true relationship "
        "is non-linear), will standardization still recover the ATE? "
        "What happens to IPW estimates when some propensity scores are "
        "very close to 0 or 1?"
    ),
    source_reference="Hern\u00e1n & Robins, What If, Chapter 2 (\u00a72.3\u20132.4)",
)


# ---------------------------------------------------------------------------
# Lesson 6 — Diagnostics, uncertainty, and responsible interpretation
# ---------------------------------------------------------------------------

LESSON_6 = LessonContent(
    lesson_id="L6",
    title="Diagnostics, uncertainty, and responsible interpretation",
    objective=(
        "Interpret propensity overlap, IPW weight distributions, effective "
        "sample size, and assumption warnings to decide whether a causal "
        "estimate is supported, fragile, or not interpretable."
    ),
    causal_question=CAUSAL_QUESTION,
    treatment=TREATMENT,
    comparator=COMPARATOR,
    outcome=OUTCOME,
    follow_up=FOLLOW_UP,
    estimand=ESTIMAND,
    assumptions=ASSUMPTIONS,
    explanation=(
        "A numerically precise estimate is not automatically a causal estimate. "
        "Three diagnostic checks are required before interpreting any adjusted "
        "result:\n\n"
        "1. Overlap (positivity check):\n"
        "   Propensity scores for treated and control episodes must span a "
        "common range. If one group has propensities near 0 or 1, the "
        "positivity assumption is violated and IPW weights become extreme.\n\n"
        "2. Weight distribution:\n"
        "   Extreme IPW weights (e.g., > 10) inflate variance and signal "
        "positivity problems. The effective sample size (ESS) measures how "
        "much information the weighted sample retains:\n"
        "   ESS = (sum w)^2 / sum(w^2)\n"
        "   A low ESS relative to the nominal sample size means the estimate "
        "is driven by a small number of episodes.\n\n"
        "3. Covariate balance:\n"
        "   The standardized mean difference (SMD) for severity should be "
        "small after weighting (SMD < 0.1 is a common threshold). "
        "Large post-weighting SMD indicates the propensity model did not "
        "adequately balance the groups.\n\n"
        "Uncertainty from the bootstrap CI reflects sampling variability only. "
        "It does not capture unmeasured-confounding uncertainty. A narrow CI "
        "under strong unmeasured confounding is false precision.\n\n"
        "Source: Hern\u00e1n & Robins, What If, Chapter 3 (\u00a73.1) and Chapter 2 (\u00a72.4)."
    ),
    visual_keys=[
        "propensity_overlap",
        "weight_distribution",
        "effective_sample_size",
        "estimator_comparison",
        "assumption_checklist",
    ],
    estimator_or_diagnostic=(
        "Switch to limited-overlap assignment. Observe that propensity scores "
        "cluster near 0 and 1, IPW weights become extreme, and the ESS drops. "
        "Compare the overlap warning with the adequate-overlap scenario. "
        "Check whether the SMD after weighting is below 0.1."
    ),
    interpretation=(
        "When overlap is adequate and models are correctly specified, the "
        "adjusted estimates are supported. When overlap is limited, extreme "
        "weights signal that the positivity assumption is violated and the "
        "IPW estimate should not be interpreted causally without further "
        "investigation. The assumption checklist makes these conditions "
        "explicit rather than hiding them."
    ),
    limitation=(
        "Diagnostics can detect some problems (poor overlap, extreme weights, "
        "residual imbalance) but cannot detect unmeasured confounding. "
        "Passing all three diagnostic checks is necessary but not sufficient "
        "for a valid causal interpretation."
    ),
    reflection=(
        "Can a statistically significant result from an IPW estimator be "
        "interpreted causally when the ESS is 5% of the nominal sample size? "
        "What would you do if the SMD after weighting is still 0.3?"
    ),
    source_reference="Hern\u00e1n & Robins, What If, Chapter 2 (\u00a72.4) and Chapter 3 (\u00a73.1)",
)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

LESSONS: dict[str, LessonContent] = {
    LESSON_1.lesson_id: LESSON_1,
    LESSON_2.lesson_id: LESSON_2,
    LESSON_3.lesson_id: LESSON_3,
    LESSON_4.lesson_id: LESSON_4,
    LESSON_5.lesson_id: LESSON_5,
    LESSON_6.lesson_id: LESSON_6,
}

ALL_LESSON_IDS = ["L1", "L2", "L3", "L4", "L5", "L6"]
