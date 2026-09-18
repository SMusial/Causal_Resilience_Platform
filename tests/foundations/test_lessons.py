"""
tests/foundations/test_lessons.py
===================================
V0 Slice 3/4/5/6 — Lesson content, table, and release-gate tests.
"""

import pandas as pd
import pytest

from causal_resilience.foundations.lessons import (
    LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6,
    LESSONS, ALL_LESSON_IDS,
    CAUSAL_QUESTION, TREATMENT, COMPARATOR, OUTCOME, FOLLOW_UP,
    ESTIMAND, ASSUMPTIONS, SYNTHETIC_DATA_DISCLAIMER, BOOTSTRAP_CAVEAT,
    ORACLE_CAVEAT,
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
# Lesson content — basic field checks (Slices 3/4/5)
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


def test_lesson_5_fields():
    assert LESSON_5.lesson_id == "L5"
    assert LESSON_5.title and LESSON_5.objective and LESSON_5.explanation
    assert "estimator_comparison" in LESSON_5.visual_keys
    assert "propensity_overlap" in LESSON_5.visual_keys
    assert LESSON_5.source_reference


def test_lesson_6_fields():
    assert LESSON_6.lesson_id == "L6"
    assert LESSON_6.title and LESSON_6.objective and LESSON_6.explanation
    assert "propensity_overlap" in LESSON_6.visual_keys
    assert "effective_sample_size" in LESSON_6.visual_keys
    assert LESSON_6.source_reference


def test_registry_complete():
    for lid, lesson in [
        ("L1", LESSON_1), ("L2", LESSON_2), ("L3", LESSON_3),
        ("L4", LESSON_4), ("L5", LESSON_5), ("L6", LESSON_6),
    ]:
        assert lid in LESSONS
        assert LESSONS[lid] is lesson


def test_lessons_are_frozen():
    with pytest.raises((AttributeError, TypeError)):
        LESSON_1.title = "mutated"  # type: ignore[misc]


def test_lesson_explanations_mention_source():
    for lesson in (LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6):
        assert "Hern" in lesson.explanation or "What If" in lesson.explanation


def test_lesson_2_contains_ate_formula():
    assert "E[Y(1)" in LESSON_2.explanation or "ATE" in LESSON_2.explanation


def test_lesson_3_mentions_exchangeability():
    assert "exchangeability" in LESSON_3.explanation.lower()


def test_lesson_4_mentions_backdoor():
    assert "backdoor" in LESSON_4.explanation.lower()


def test_lesson_4_mentions_dag():
    assert "dag" in LESSON_4.explanation.lower() or "directed" in LESSON_4.explanation.lower()


def test_lesson_5_mentions_ipw():
    assert "ipw" in LESSON_5.explanation.lower() or "inverse" in LESSON_5.explanation.lower()


def test_lesson_5_mentions_standardization():
    assert "standardization" in LESSON_5.explanation.lower() or "g-formula" in LESSON_5.explanation.lower()


def test_lesson_6_mentions_ess():
    assert "ess" in LESSON_6.explanation.lower() or "effective sample" in LESSON_6.explanation.lower()


def test_lesson_6_mentions_positivity():
    assert "positivity" in LESSON_6.explanation.lower()


def test_registry_includes_lessons_5_and_6():
    assert "L5" in LESSONS and LESSONS["L5"] is LESSON_5
    assert "L6" in LESSONS and LESSONS["L6"] is LESSON_6


# ---------------------------------------------------------------------------
# Slice 6 — required metadata fields on every lesson
# ---------------------------------------------------------------------------

ALL_LESSONS = [LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6]


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_causal_question(lesson):
    assert lesson.causal_question
    assert "EARLY_COORDINATED_RESPONSE" in lesson.causal_question
    assert "MONITOR_REASSESS" in lesson.causal_question


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_treatment_and_comparator(lesson):
    assert lesson.treatment and "EARLY_COORDINATED_RESPONSE" in lesson.treatment
    assert lesson.comparator and "MONITOR_REASSESS" in lesson.comparator


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_outcome_and_follow_up(lesson):
    assert lesson.outcome and "customer_impact_minutes_24h" in lesson.outcome
    assert lesson.follow_up and "24" in lesson.follow_up


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_estimand(lesson):
    assert lesson.estimand
    assert "ATE" in lesson.estimand or "E[Y" in lesson.estimand


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_five_assumptions(lesson):
    assert len(lesson.assumptions) == 5
    texts = " ".join(lesson.assumptions).lower()
    assert "consistency" in texts
    assert "exchangeability" in texts
    assert "positivity" in texts
    assert "interference" in texts
    assert "follow" in texts


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_limitation(lesson):
    assert lesson.limitation and len(lesson.limitation) > 20


@pytest.mark.parametrize("lesson", ALL_LESSONS, ids=[l.lesson_id for l in ALL_LESSONS])
def test_lesson_has_estimator_or_diagnostic(lesson):
    assert lesson.estimator_or_diagnostic and len(lesson.estimator_or_diagnostic) > 20


# ---------------------------------------------------------------------------
# Slice 6 — shared constants correctness
# ---------------------------------------------------------------------------

def test_causal_question_constant_complete():
    assert "EARLY_COORDINATED_RESPONSE" in CAUSAL_QUESTION
    assert "MONITOR_REASSESS" in CAUSAL_QUESTION
    assert "customer_impact_minutes_24h" in CAUSAL_QUESTION
    assert "24 hours" in CAUSAL_QUESTION


def test_assumptions_constant_has_five_items():
    assert len(ASSUMPTIONS) == 5


def test_synthetic_disclaimer_present():
    assert "synthetic" in SYNTHETIC_DATA_DISCLAIMER.lower()
    assert "real" in SYNTHETIC_DATA_DISCLAIMER.lower()


def test_bootstrap_caveat_mentions_sampling():
    assert "sampling" in BOOTSTRAP_CAVEAT.lower()
    assert "unmeasured" in BOOTSTRAP_CAVEAT.lower()


def test_oracle_caveat_mentions_synthetic():
    assert "synthetic" in ORACLE_CAVEAT.lower()


def test_all_lesson_ids_constant():
    assert ALL_LESSON_IDS == ["L1", "L2", "L3", "L4", "L5", "L6"]
    for lid in ALL_LESSON_IDS:
        assert lid in LESSONS


# ---------------------------------------------------------------------------
# Slice 6 — accessibility: table color config
# ---------------------------------------------------------------------------

def test_observed_cell_uses_dark_background():
    """Observed cell must use a dark background for white text (high contrast)."""
    from causal_resilience.foundations.tables import _STYLE_OBSERVED
    assert "#1e3a5f" in _STYLE_OBSERVED   # dark blue background
    assert "#ffffff" in _STYLE_OBSERVED   # white text


def test_counterfactual_cell_uses_white_background():
    """Counterfactual cell must use white background with dark text (high contrast)."""
    from causal_resilience.foundations.tables import _STYLE_COUNTERFACTUAL
    assert "#ffffff" in _STYLE_COUNTERFACTUAL   # white background
    assert "#1a1a1a" in _STYLE_COUNTERFACTUAL   # near-black text


def test_counterfactual_cell_has_dashed_border():
    """Dashed border provides a second visual cue beyond color."""
    from causal_resilience.foundations.tables import _STYLE_COUNTERFACTUAL
    assert "dashed" in _STYLE_COUNTERFACTUAL


def test_render_table_has_role_attribute():
    html = render_po_table(_make_sample(treated=True))
    assert "role='table'" in html


def test_render_table_has_scope_on_headers():
    html = render_po_table(_make_sample(treated=True))
    assert "scope='col'" in html


def test_render_table_has_aria_labels():
    html = render_po_table(_make_sample(treated=True))
    assert "aria-label=" in html


def test_render_no_grey_text():
    html = render_po_table(_make_sample(treated=True))
    assert "#aaa" not in html
    assert "#f0f0f0" not in html   # old low-contrast background must be gone


# ---------------------------------------------------------------------------
# Slice 6 — oracle leakage: normal mode must not expose oracle columns
# ---------------------------------------------------------------------------

def test_no_oracle_leakage_in_normal_mode():
    from causal_resilience.foundations.dgp import TelecomFoundationsDGP
    from causal_resilience.foundations.schemas import ScenarioConfig
    dgp = TelecomFoundationsDGP()
    ds = dgp.generate(ScenarioConfig(seed=0, n_episodes=50, teaching_mode=False,
                                     scenario_id="leak-test"))
    df = ds.to_dataframe()
    assert "potential_outcome_0" not in df.columns
    assert "potential_outcome_1" not in df.columns
    assert "propensity_true" not in df.columns


def test_oracle_fields_none_in_normal_mode_episodes():
    from causal_resilience.foundations.dgp import TelecomFoundationsDGP
    from causal_resilience.foundations.schemas import ScenarioConfig
    dgp = TelecomFoundationsDGP()
    ds = dgp.generate(ScenarioConfig(seed=0, n_episodes=20, teaching_mode=False,
                                     scenario_id="leak-test2"))
    for ep in ds.episodes:
        assert ep.potential_outcome_0 is None
        assert ep.potential_outcome_1 is None
        assert ep.propensity_true is None


# ---------------------------------------------------------------------------
# Slice 6 — provenance completeness
# ---------------------------------------------------------------------------

def test_provenance_has_required_fields():
    from causal_resilience.foundations.dgp import TelecomFoundationsDGP
    from causal_resilience.foundations.schemas import ScenarioConfig
    dgp = TelecomFoundationsDGP()
    ds = dgp.generate(ScenarioConfig(seed=7, n_episodes=50, scenario_id="prov-test"))
    p = ds.provenance
    assert p.seed == 7
    assert p.scenario_id == "prov-test"
    assert p.generator_version
    assert p.schema_version
    assert p.created_at is not None
    assert p.config_hash is not None


def test_estimate_result_provenance_complete():
    from causal_resilience.foundations.dgp import TelecomFoundationsDGP
    from causal_resilience.foundations.estimators import DifferenceInMeans, EstimatorConfig
    from causal_resilience.foundations.schemas import Estimand, ScenarioConfig
    dgp = TelecomFoundationsDGP()
    ds = dgp.generate(ScenarioConfig(seed=3, n_episodes=100, scenario_id="est-prov"))
    result = DifferenceInMeans().estimate(ds, Estimand(), EstimatorConfig())
    p = result.provenance
    assert p.seed == 3
    assert p.scenario_id == "est-prov"
    assert p.generator_version
    assert p.schema_version
    assert p.created_at is not None


# ---------------------------------------------------------------------------
# Slice 6 — all six lessons reachable from registry
# ---------------------------------------------------------------------------

def test_all_six_lessons_reachable():
    for lid in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        lesson = LESSONS[lid]
        assert lesson.lesson_id == lid
        assert lesson.title
        assert lesson.objective
        assert lesson.explanation
        assert lesson.source_reference


# ---------------------------------------------------------------------------
# Potential-outcome table helpers (Slice 3)
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
