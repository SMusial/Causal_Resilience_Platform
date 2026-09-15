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
# Registry
# ---------------------------------------------------------------------------

LESSONS: dict[str, LessonContent] = {
    LESSON_1.lesson_id: LESSON_1,
    LESSON_2.lesson_id: LESSON_2,
}
