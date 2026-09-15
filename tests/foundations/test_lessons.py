"""
tests/foundations/test_lessons.py
===================================
V0 Slice 3/4 — Lesson content and potential-outcome table tests.
"""

import pandas as pd
import pytest

from causal_resilience.foundations.lessons import (
    LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSONS,
)
from causal_resilience.foundations.tables import build_po_table_rows, render_po_table


def _make_sample(treated: bool) -> pd.DataFrame:
    return pd.DataFrame([{
        "episode_id": "v0-000001",
        "severity": 0.6,
        "treatment_label": "EARLY_COORDINATED_RESPONSE" if treated else "MONITOR_REASSESS",
        "potential_outcome_0": 200.0,
        "potential_outcome_1": 160.0,
        "outcome": 160.0 if treated else 200.0,
    }])


# ---------------------------------------------------------------------------
# Lesson content
# ---------------------------------------------------------------------------

def test_lesson_1_fields():
    assert LESSON_1.lesson_id == "L1"
    assert LESSON_1.title and LESSON_1.objective and LESSON_1.explanation
    assert "target_trial_card" in LESSON_1.visual_keys
    assert LESSON_1.source_reference


def test_lesson_2_fields():
    assert LESSON_2.lesson_id == "L2"
    assert LESSON_2.title and LESSON_2.objective and LESSON_2.explanation
    assert "potential_outcome_table" in LESSON_2.visual_keys
    assert LESSON_2.source_reference


def test_lesson_3_fields():
    assert LESSON_3.lesson_id == "L3"
    assert LESSON_3.title and LESSON_3.objective and LESSON_3.explanation
    assert "severity_balance" in LESSON_3.visual_keys
    assert LESSON_3.source_reference


def test_lesson_4_fields():
    assert LESSON_4.lesson_id == "L4"
    assert LESSON_4.title and LESSON_4.objective and LESSON_4.explanation
    assert "dag" in LESSON_4.visual_keys
    assert "crude_vs_oracle" in LESSON_4.visual_keys
    assert LESSON_4.source_reference


def test_registry_complete():
    for lid, lesson in [("L1", LESSON_1), ("L2", LESSON_2),
                        ("L3", LESSON_3), ("L4", LESSON_4)]:
        assert lid in LESSONS
        assert LESSONS[lid] is lesson


def test_lessons_are_frozen():
    with pytest.raises((AttributeError, TypeError)):
        LESSON_1.title = "mutated"  # type: ignore[misc]


def test_lesson_explanations_mention_source():
    for lesson in (LESSON_1, LESSON_2, LESSON_3, LESSON_4):
        assert "Hernán" in lesson.explanation or "What If" in lesson.explanation


def test_lesson_2_contains_ate_formula():
    assert "E[Y(1)" in LESSON_2.explanation or "ATE" in LESSON_2.explanation


def test_lesson_3_mentions_exchangeability():
    assert "exchangeability" in LESSON_3.explanation.lower()


def test_lesson_4_mentions_backdoor():
    assert "backdoor" in LESSON_4.explanation.lower()


def test_lesson_4_mentions_dag():
    assert "dag" in LESSON_4.explanation.lower() or "directed" in LESSON_4.explanation.lower()


# ---------------------------------------------------------------------------
# Potential-outcome table helpers
# ---------------------------------------------------------------------------

def test_treated_row_flags():
    rows = build_po_table_rows(_make_sample(treated=True))
    assert rows[0]["y1_observed"] is True
    assert rows[0]["y0_observed"] is False


def test_control_row_flags():
    rows = build_po_table_rows(_make_sample(treated=False))
    assert rows[0]["y0_observed"] is True
    assert rows[0]["y1_observed"] is False


def test_observed_outcome_matches_treatment():
    for treated in (True, False):
        rows = build_po_table_rows(_make_sample(treated=treated))
        r = rows[0]
        assert r["outcome"] == (r["y1_value"] if treated else r["y0_value"])


def test_render_contains_observed_label():
    assert "observed" in render_po_table(_make_sample(treated=True))


def test_render_contains_missing_label():
    assert "[missing]" in render_po_table(_make_sample(treated=True))


def test_render_no_grey_text():
    html = render_po_table(_make_sample(treated=True))
    assert "#aaa" not in html
