"""
tests/foundations/test_lessons.py
===================================
V0 Slice 3 — Lesson content smoke tests.

Verifies that lesson objects are well-formed and that the registry is complete.
Does not test Streamlit rendering.
"""

import pytest

from causal_resilience.foundations.lessons import LESSON_1, LESSON_2, LESSONS, LessonContent


def test_lesson_1_fields():
    assert LESSON_1.lesson_id == "L1"
    assert LESSON_1.title
    assert LESSON_1.objective
    assert LESSON_1.explanation
    assert len(LESSON_1.visual_keys) >= 1
    assert LESSON_1.reflection
    assert LESSON_1.source_reference


def test_lesson_2_fields():
    assert LESSON_2.lesson_id == "L2"
    assert LESSON_2.title
    assert LESSON_2.objective
    assert LESSON_2.explanation
    assert len(LESSON_2.visual_keys) >= 1
    assert LESSON_2.reflection
    assert LESSON_2.source_reference


def test_registry_contains_both_lessons():
    assert "L1" in LESSONS
    assert "L2" in LESSONS
    assert LESSONS["L1"] is LESSON_1
    assert LESSONS["L2"] is LESSON_2


def test_lessons_are_frozen():
    with pytest.raises((AttributeError, TypeError)):
        LESSON_1.title = "mutated"  # type: ignore[misc]


def test_lesson_1_references_target_trial():
    assert "target_trial_card" in LESSON_1.visual_keys


def test_lesson_2_references_potential_outcome_table():
    assert "potential_outcome_table" in LESSON_2.visual_keys


def test_lesson_explanations_mention_source():
    assert "Hernán" in LESSON_1.explanation or "What If" in LESSON_1.explanation
    assert "Hernán" in LESSON_2.explanation or "What If" in LESSON_2.explanation


def test_lesson_2_explanation_contains_ate_formula():
    assert "E[Y(1)" in LESSON_2.explanation or "ATE" in LESSON_2.explanation
