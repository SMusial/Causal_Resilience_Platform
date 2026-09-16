"""
causal_resilience.foundations.lessons
=======================================
V0 Slice 3 — Course lesson content for Lessons 1 and 2.

Source: Hernán & Robins, *Causal Inference: What If*
  Chapter 1 — causal effects, potential outcomes, individual and average effects
  Chapter 3 — target trial, estimand, time zero, follow-up

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


@dataclass(frozen=True)
class LessonContent:
    """Structured content for one course lesson."""
    lesson_id: str
    title: str
    objective: str
    explanation: str
    visual_keys: list[str]          # keys consumed by the Streamlit page
    estimate_or_diagnostic: str     # what the learner computes or observes
    interpretation: str
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
    explanation=(
        "A causal question is not the same as a prediction question. "
        "Prediction asks: given what we observe, what will happen? "
        "Causation asks: if we intervene and change something, what would happen?\n\n"
        "Before choosing any estimator or running any analysis, we must define:\n"
        "  • Population — who are we studying?\n"
        "  • Intervention — what action are we evaluating?\n"
        "  • Comparator — what is the alternative?\n"
        "  • Outcome — what do we measure?\n"
        "  • Time zero — when does follow-up begin?\n"
        "  • Follow-up — how long do we observe?\n\n"
        "The V0 question is:\n"
        "  Among eligible synthetic telecom incidents at detection, what is the "
        "average effect of assigning EARLY_COORDINATED_RESPONSE rather than "
        "MONITOR_REASSESS on customer_impact_minutes_24h during the following "
        "24 hours?\n\n"
        "Source: Hernán & Robins, What If, Chapter 3 — target trial."
    ),
    visual_keys=["target_trial_card", "treatment_timeline"],
    estimate_or_diagnostic=(
        "Read the target-trial card. Identify each component of the causal "
        "question. Notice that no number has been computed yet — the question "
        "must be defined before any estimator is chosen."
    ),
    interpretation=(
        "The target-trial card makes the causal question precise. "
        "Vague language such as 'the effect of resilience' or 'better response' "
        "cannot be estimated. A well-defined intervention and comparator can."
    ),
    reflection=(
        "Can you restate the V0 causal question in one sentence without using "
        "the words 'impact', 'resilience', or 'performance'? "
        "What would change if the follow-up period were 48 hours instead of 24?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 3 (target trial, §3.1–3.2)",
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
    explanation=(
        "For each incident episode i, there are two potential outcomes:\n"
        "  Y_i(1) — customer impact if the episode receives EARLY_COORDINATED_RESPONSE\n"
        "  Y_i(0) — customer impact if the episode receives MONITOR_REASSESS\n\n"
        "The individual causal effect is Y_i(1) − Y_i(0).\n\n"
        "The fundamental problem of causal inference: we can only observe one "
        "of the two potential outcomes for each episode. The other is the "
        "counterfactual — what would have happened under the alternative.\n\n"
        "In teaching mode, the simulator knows both potential outcomes. "
        "In normal analysis, only the observed outcome is available.\n\n"
        "The average treatment effect (ATE) is:\n"
        "  ATE = E[Y(1) − Y(0)] = E[Y(1)] − E[Y(0)]\n\n"
        "Estimating the ATE from observed data requires assumptions about "
        "the missing counterfactuals.\n\n"
        "Source: Hernán & Robins, What If, Chapter 1 — individual and average "
        "causal effects, §1.1–1.2."
    ),
    visual_keys=["potential_outcome_table", "missing_counterfactual_chart"],
    estimate_or_diagnostic=(
        "In teaching mode: inspect the two-world table showing Y(0) and Y(1) "
        "for a small sample. Observe that the observed outcome matches the "
        "assigned treatment. The other column is the missing counterfactual.\n"
        "In normal mode: the oracle columns are hidden. Only the observed "
        "outcome is available for estimation."
    ),
    interpretation=(
        "The oracle ATE is the mean of Y(1) − Y(0) computed directly from "
        "the simulator's hidden truth. In real data, this quantity is never "
        "available. The teaching simulator exposes it only to help you "
        "understand what estimators are trying to recover."
    ),
    reflection=(
        "If you could observe both Y_i(0) and Y_i(1) for every episode, "
        "would you still need an estimator? "
        "Why does the consistency assumption matter for connecting potential "
        "outcomes to observed data?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 1 (§1.1–1.2)",
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
    explanation=(
        "Under randomized assignment, treatment is allocated independently of "
        "severity and all other baseline characteristics. This means:\n"
        "  Y(a) ⊥ A  (unconditional exchangeability)\n\n"
        "When exchangeability holds, the observed group means identify the "
        "potential-outcome means:\n"
        "  E[Y | A=1] = E[Y(1)]\n"
        "  E[Y | A=0] = E[Y(0)]\n\n"
        "So the crude difference in means estimates the ATE:\n"
        "  E[Y | A=1] − E[Y | A=0] = E[Y(1)] − E[Y(0)] = ATE\n\n"
        "Finite samples still vary — the estimate will not equal the oracle "
        "ATE exactly, but the error shrinks as sample size grows.\n\n"
        "Source: Hernán & Robins, What If, Chapter 2 (§2.1–2.2)."
    ),
    visual_keys=["outcome_distributions", "estimate_vs_oracle", "severity_balance"],
    estimate_or_diagnostic=(
        "Compare the difference-in-means estimate with the oracle ATE. "
        "Check the severity balance chart — under randomization the severity "
        "distributions of treated and control groups should overlap closely."
    ),
    interpretation=(
        "Under randomization the estimate tracks the oracle ATE. "
        "The severity distributions are balanced by design, not by adjustment. "
        "Remaining error is sampling variability, not confounding bias."
    ),
    reflection=(
        "Why does balance on severity not need to be perfect for randomization "
        "to support a causal interpretation? "
        "What happens to the estimate as you increase the sample size?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 2 (§2.1–2.2)",
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
    explanation=(
        "A confounder is a variable that is a common cause of both treatment "
        "assignment and the outcome. In the V0 scenario, severity plays this role:\n\n"
        "  severity ──> treatment\n"
        "  severity ──> outcome\n"
        "  treatment ──> outcome\n\n"
        "Higher-severity incidents are more likely to receive "
        "EARLY_COORDINATED_RESPONSE and also tend to have higher "
        "customer_impact_minutes_24h regardless of treatment.\n\n"
        "This creates a backdoor path: treatment ← severity → outcome.\n"
        "The crude difference in means conflates the treatment effect with "
        "the severity effect, producing a biased estimate of the ATE.\n\n"
        "A directed acyclic graph (DAG) makes the confounding structure "
        "explicit and guides the choice of adjustment strategy.\n\n"
        "Source: Hernán & Robins, What If, Chapter 6 (§6.1–6.3)."
    ),
    visual_keys=["dag", "severity_balance", "crude_vs_oracle"],
    estimate_or_diagnostic=(
        "Switch to confounded assignment. Observe that the severity "
        "distributions diverge between treatment groups. Compare the crude "
        "difference-in-means with the oracle ATE — the gap is confounding bias."
    ),
    interpretation=(
        "Under confounded assignment, higher-severity incidents cluster in the "
        "treated group. The crude estimate is pulled toward a less negative "
        "(more positive) value than the true ATE — or even a positive value — "
        "because treated episodes would have had worse outcomes even without "
        "treatment. The raw comparison makes the intervention look less "
        "beneficial than it truly is. Adjustment for severity is required — "
        "introduced in Lesson 5."
    ),
    reflection=(
        "If you did not know the DGP, how would you decide whether severity "
        "is a confounder? "
        "Why does a statistically precise estimate not rule out confounding bias?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 6 (§6.1–6.3)",
)


# ---------------------------------------------------------------------------
# Lesson 5 — Adjustment: stratification, standardization, and IPW
# ---------------------------------------------------------------------------

LESSON_5 = LessonContent(
    lesson_id="L5",
    title="Adjustment: standardization and IPW",
    objective=(
        "Apply outcome regression (standardization) and inverse-probability "
        "weighting to recover the ATE under confounded assignment, and explain "
        "what each method requires to be valid."
    ),
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
        "  - Conditional exchangeability: Y(a) ⊥ A | severity.\n"
        "  - Positivity: 0 < P(A=1 | severity=l) < 1 for all l.\n"
        "  - Correct model specification (each method for its own model).\n\n"
        "Source: Hernán & Robins, What If, Chapter 2 (§2.3–2.4)."
    ),
    visual_keys=[
        "estimator_comparison",
        "propensity_overlap",
        "weight_distribution",
        "severity_balance_after",
    ],
    estimate_or_diagnostic=(
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
        "limited — neither is automatically correct in real data."
    ),
    reflection=(
        "If the outcome model is misspecified (e.g., the true relationship "
        "is non-linear), will standardization still recover the ATE? "
        "What happens to IPW estimates when some propensity scores are "
        "very close to 0 or 1?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 2 (§2.3–2.4)",
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
        "Source: Hernán & Robins, What If, Chapter 3 (§3.1) and Chapter 2 (§2.4)."
    ),
    visual_keys=[
        "propensity_overlap",
        "weight_distribution",
        "effective_sample_size",
        "estimator_comparison",
        "assumption_checklist",
    ],
    estimate_or_diagnostic=(
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
    reflection=(
        "Can a statistically significant result from an IPW estimator be "
        "interpreted causally when the ESS is 5% of the nominal sample size? "
        "What would you do if the SMD after weighting is still 0.3?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 2 (§2.4) and Chapter 3 (§3.1)",
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
