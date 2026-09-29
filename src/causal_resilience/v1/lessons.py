"""
causal_resilience.v1.lessons
==============================
V1 Module 1 — Course lesson content.

Source: Hernán & Robins, *Causal Inference: What If*, Chapter 3 (§3.1-3.2)
Implementation type: educational content layer — no estimator logic.
"""

from __future__ import annotations

from dataclasses import dataclass

from causal_resilience.foundations.lessons import LessonContent


LESSON_V1_01 = LessonContent(
    lesson_id="V1-L1",
    title="Ask a causal question",
    objective=(
        "State the V1 causal question using population, intervention, "
        "comparator, outcome, time zero, follow-up, and the minimum "
        "sufficient adjustment set under the V1 baseline DAG."
    ),
    explanation=(
        "V1 extends the V0 causal question to a richer operational world: "
        "six roles, seven protocols, and multiple baseline confounders.\n\n"
        "The causal question remains the same in structure:\n"
        "  Among eligible synthetic telecom incidents at detection, what is "
        "the average effect of COORDINATED_RESPONSE versus MONITOR_REASSESS "
        "on customer_impact_minutes_24h over 24 hours?\n\n"
        "What changes in V1:\n"
        "  - The adjustment set now includes severity, topology criticality, "
        "team backlog, and operational readiness.\n"
        "  - The secondary estimand targets sla_breach_24h on the "
        "risk-difference scale.\n"
        "  - Seven protocols are available to the simulation layer, but the "
        "primary causal contrast remains binary.\n"
        "  - Cyberattack and vandalism are disturbance types, never treatments.\n\n"
        "The target-trial framework still requires that the intervention and "
        "comparator be defined precisely before any estimator is chosen.\n\n"
        "Source: Hernán & Robins, What If, Chapter 3 (§3.1-3.2)."
    ),
    visual_keys=["v1_target_trial_card", "v1_protocol_table", "v1_estimand_card"],
    estimate_or_diagnostic=(
        "Read the V1 target-trial card. Identify the primary and secondary "
        "estimands. Note the expanded adjustment set and explain why each "
        "variable belongs there."
    ),
    interpretation=(
        "The V1 target trial is more complex than V0 but follows the same "
        "discipline: question first, estimand second, estimator third. "
        "The additional confounders reflect a richer operational world — "
        "they do not change the fundamental identification logic."
    ),
    reflection=(
        "Why is COORDINATED_RESPONSE defined as a fixed bundle rather than "
        "a free choice of role? "
        "What would happen to the estimand if we tried to estimate separate "
        "effects for each of the seven protocols from observational data?"
    ),
    source_reference="Hernán & Robins, What If, Chapter 3 (§3.1-3.2)",
)


V1_LESSONS: dict[str, LessonContent] = {
    LESSON_V1_01.lesson_id: LESSON_V1_01,
}
