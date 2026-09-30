"""
tests/v1/test_lessons.py
==========================
V1 lesson content tests — M1 and M2.
"""

from causal_resilience.v1.lessons import LESSON_V1_01, LESSON_V1_02, V1_LESSONS
from causal_resilience.foundations.lessons import LessonContent


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_v1_lessons_registry_contains_m1_and_m2():
    assert "V1-L1" in V1_LESSONS
    assert "V1-L2" in V1_LESSONS


def test_v1_lessons_are_lesson_content_instances():
    for lesson in V1_LESSONS.values():
        assert isinstance(lesson, LessonContent)


# ---------------------------------------------------------------------------
# LESSON_V1_01
# ---------------------------------------------------------------------------

def test_v1_m1_lesson_id():
    assert LESSON_V1_01.lesson_id == "V1-L1"


def test_v1_m1_title_non_empty():
    assert len(LESSON_V1_01.title) > 0


def test_v1_m1_assumptions_count():
    assert len(LESSON_V1_01.assumptions) >= 5


def test_v1_m1_estimand_mentions_ate():
    assert "ATE" in LESSON_V1_01.estimand


def test_v1_m1_treatment_mentions_coordinated():
    assert "COORDINATED_RESPONSE" in LESSON_V1_01.treatment


def test_v1_m1_estimator_or_diagnostic_non_empty():
    assert len(LESSON_V1_01.estimator_or_diagnostic) > 0


# ---------------------------------------------------------------------------
# LESSON_V1_02
# ---------------------------------------------------------------------------

def test_v1_m2_lesson_id():
    assert LESSON_V1_02.lesson_id == "V1-L2"


def test_v1_m2_title_mentions_potential_outcomes():
    assert "potential" in LESSON_V1_02.title.lower()


def test_v1_m2_objective_non_empty():
    assert len(LESSON_V1_02.objective) > 0


def test_v1_m2_assumptions_count():
    assert len(LESSON_V1_02.assumptions) >= 5


def test_v1_m2_assumptions_mention_exchangeability():
    assert any("exchangeability" in a.lower() for a in LESSON_V1_02.assumptions)


def test_v1_m2_assumptions_mention_positivity():
    assert any("positivity" in a.lower() for a in LESSON_V1_02.assumptions)


def test_v1_m2_assumptions_mention_four_confounders():
    combined = " ".join(LESSON_V1_02.assumptions)
    assert "topology_criticality" in combined
    assert "team_backlog" in combined
    assert "operational_readiness" in combined


def test_v1_m2_estimand_mentions_ate():
    assert "ATE" in LESSON_V1_02.estimand


def test_v1_m2_treatment_mentions_coordinated():
    assert "COORDINATED_RESPONSE" in LESSON_V1_02.treatment


def test_v1_m2_explanation_mentions_fundamental_problem():
    assert "fundamental" in LESSON_V1_02.explanation.lower()


def test_v1_m2_explanation_mentions_counterfactual():
    assert "counterfactual" in LESSON_V1_02.explanation.lower()


def test_v1_m2_explanation_mentions_v0_dgp():
    assert "V0 DGP" in LESSON_V1_02.explanation


def test_v1_m2_limitation_non_empty():
    assert len(LESSON_V1_02.limitation) > 0


def test_v1_m2_reflection_non_empty():
    assert len(LESSON_V1_02.reflection) > 0


def test_v1_m2_source_reference_mentions_chapter_1():
    assert "Chapter 1" in LESSON_V1_02.source_reference


def test_v1_m2_visual_keys_non_empty():
    assert len(LESSON_V1_02.visual_keys) > 0
