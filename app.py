"""
app.py — V0 Slice 3 Streamlit application.

Two-page course experience: Lesson 1 (causal question) and Lesson 2
(potential outcomes). Sandbox generates data and shows a randomized
difference-in-means estimate with oracle comparison in teaching mode.

Oracle fields are hidden in normal mode and labeled explicitly in teaching mode.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Any

from causal_resilience.foundations.schemas import (
    AssignmentMode,
    Estimand,
    ScenarioConfig,
)
from causal_resilience.foundations.dgp import TelecomFoundationsDGP
from causal_resilience.foundations.estimators import DifferenceInMeans, EstimatorConfig
from causal_resilience.foundations.lessons import LESSON_1, LESSON_2

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Causal Resilience — V0 Foundations",
    page_icon="🔬",
    layout="wide",
)

_DGP = TelecomFoundationsDGP()
_ESTIMAND = Estimand()
_ESTIMATOR = DifferenceInMeans()

# ---------------------------------------------------------------------------
# Sidebar — scenario controls
# ---------------------------------------------------------------------------

st.sidebar.title("Scenario controls")

seed = st.sidebar.number_input("Random seed", min_value=0, max_value=99_999, value=42, step=1)
n_episodes = st.sidebar.slider("Episodes", min_value=50, max_value=5_000, value=500, step=50)
teaching_mode = st.sidebar.toggle("Teaching mode (show oracle)", value=False)

if teaching_mode:
    st.sidebar.info("⚠️ **Teaching mode ON** — oracle / simulator truth is visible. "
                    "These values are not available in real data.")

config = ScenarioConfig(
    seed=int(seed),
    n_episodes=int(n_episodes),
    assignment_mode=AssignmentMode.RANDOMIZED,
    teaching_mode=teaching_mode,
    scenario_id="v0-slice3",
)

dataset = _DGP.generate(config)
df = dataset.to_dataframe()

ground_truth = _DGP.truth(dataset) if teaching_mode else None

est_config = EstimatorConfig(bootstrap_iterations=1000, bootstrap_seed=0)
result = _ESTIMATOR.estimate(dataset, _ESTIMAND, est_config, ground_truth=ground_truth)

# ---------------------------------------------------------------------------
# Potential-outcome table helpers (Lesson 2)
# ---------------------------------------------------------------------------

# Cell styles — no color-only encoding; text labels carry the meaning.
_STYLE_OBSERVED = (
    "background-color:#dbeafe; color:#1e3a5f; font-weight:bold; "
    "border:2px solid #2563eb; padding:4px 8px;"
)
_STYLE_COUNTERFACTUAL = (
    "background-color:#f0f0f0; color:#1a1a1a; "
    "border:1px dashed #6b7280; padding:4px 8px;"
)
_STYLE_PLAIN = "padding:4px 8px; color:#1a1a1a; background-color:#ffffff;"
_STYLE_TH = (
    "background-color:#1e3a5f; color:#ffffff; font-weight:bold; "
    "padding:6px 8px; text-align:left;"
)


def _build_po_table_rows(sample: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Pure function: convert a sample DataFrame into a list of row dicts
    with 'observed' and 'counterfactual' flags for each potential-outcome cell.

    Each row dict has keys:
      episode, severity, treatment,
      y0_value, y0_observed (bool),
      y1_value, y1_observed (bool),
      outcome
    """
    rows = []
    for _, r in sample.iterrows():
        treated = r["treatment_label"] == "EARLY_COORDINATED_RESPONSE"
        rows.append({
            "episode": r["episode_id"],
            "severity": f"{r['severity']:.2f}",
            "treatment": "ECR" if treated else "MR",
            "y0_value": f"{r['potential_outcome_0']:.1f}",
            "y0_observed": not treated,
            "y1_value": f"{r['potential_outcome_1']:.1f}",
            "y1_observed": treated,
            "outcome": f"{r['outcome']:.1f}",
        })
    return rows


def _render_po_table(sample: pd.DataFrame) -> str:
    """Render the potential-outcome table as an accessible HTML string."""
    rows = _build_po_table_rows(sample)
    headers = [
        "Episode", "Severity", "Assigned treatment",
        "Y(0) oracle", "Y(1) oracle", "Observed outcome",
    ]
    th_cells = "".join(f"<th style='{_STYLE_TH}'>{h}</th>" for h in headers)
    html_rows = []
    for row in rows:
        def _cell(value: str, observed: bool, label: str) -> str:
            if observed:
                return (
                    f"<td style='{_STYLE_OBSERVED}'>"
                    f"&#9733; {value}<br><small>observed</small></td>"
                )
            return (
                f"<td style='{_STYLE_COUNTERFACTUAL}'>"
                f"{value}<br><small>[missing]</small></td>"
            )

        html_rows.append(
            "<tr>"
            f"<td style='{_STYLE_PLAIN}'>{row['episode']}</td>"
            f"<td style='{_STYLE_PLAIN}'>{row['severity']}</td>"
            f"<td style='{_STYLE_PLAIN}'>{row['treatment']}</td>"
            + _cell(row["y0_value"], row["y0_observed"], "Y(0)")
            + _cell(row["y1_value"], row["y1_observed"], "Y(1)")
            + f"<td style='{_STYLE_OBSERVED}'>{row['outcome']}<br><small>observed</small></td>"
            "</tr>"
        )

    return (
        "<table style='border-collapse:collapse; width:100%; font-size:0.9rem;'>"
        f"<thead><tr>{th_cells}</tr></thead>"
        f"<tbody>{''.join(html_rows)}</tbody>"
        "</table>"
    )


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

page = st.sidebar.radio(
    "Course",
    ["Lesson 1 — Causal question", "Lesson 2 — Potential outcomes", "Sandbox"],
    index=0,
)

# ===========================================================================
# LESSON 1
# ===========================================================================

if page == "Lesson 1 — Causal question":
    st.title(f"Lesson 1: {LESSON_1.title}")
    st.caption(f"Source: {LESSON_1.source_reference}")

    st.subheader("Learning objective")
    st.write(LESSON_1.objective)

    st.subheader("Explanation")
    st.write(LESSON_1.explanation)

    # --- Target-trial card ---
    st.subheader("Target-trial card")
    trial_rows = [
        ("Eligibility", "Eligible synthetic incidents at detection with observed baseline severity"),
        ("Time zero", "First reliable detection timestamp"),
        ("Intervention", "EARLY_COORDINATED_RESPONSE"),
        ("Comparator", "MONITOR_REASSESS"),
        ("Assignment", "Randomized (this scenario)"),
        ("Follow-up", "24 hours from detection"),
        ("Outcome", "customer_impact_minutes_24h"),
        ("Censoring", "None — complete outcome observation assumed"),
        ("Causal contrast", "Population average treatment effect (ATE)"),
        ("Target estimand", "E[Y(1) − Y(0)]"),
    ]
    st.table(pd.DataFrame(trial_rows, columns=["Component", "V0 definition"]))

    # --- Treatment timeline ---
    st.subheader("Treatment timeline")
    fig_tl = go.Figure()
    fig_tl.add_shape(type="line", x0=0, x1=24, y0=0.5, y1=0.5,
                     line=dict(color="#555", width=2))
    events = [
        (0, "Detection\n(time zero)", "#1f77b4"),
        (0.25, "EARLY_COORDINATED_RESPONSE\nassigned within 15 min", "#2ca02c"),
        (1.0, "MONITOR_REASSESS\nreassess at 60 min", "#d62728"),
        (24, "Outcome measured\n(24 h)", "#ff7f0e"),
    ]
    for x, label, color in events:
        fig_tl.add_shape(type="line", x0=x, x1=x, y0=0.3, y1=0.7,
                         line=dict(color=color, width=2, dash="dot"))
        fig_tl.add_annotation(x=x, y=0.75, text=label, showarrow=False,
                               font=dict(size=11, color=color), align="center")
    fig_tl.update_layout(
        title="Incident timeline: detection → intervention → 24-hour outcome",
        xaxis=dict(title="Hours after detection", range=[-1, 25]),
        yaxis=dict(visible=False, range=[0, 1.2]),
        height=220,
        margin=dict(t=50, b=40),
    )
    st.plotly_chart(fig_tl, use_container_width=True)

    st.subheader("Reflection")
    st.info(LESSON_1.reflection)


# ===========================================================================
# LESSON 2
# ===========================================================================

elif page == "Lesson 2 — Potential outcomes":
    st.title(f"Lesson 2: {LESSON_2.title}")
    st.caption(f"Source: {LESSON_2.source_reference}")

    st.subheader("Learning objective")
    st.write(LESSON_2.objective)

    st.subheader("Explanation")
    st.write(LESSON_2.explanation)

    # --- Potential-outcome table (teaching mode only) ---
    st.subheader("Two-world potential-outcome table")

    if teaching_mode:
        st.success("**Teaching mode** — oracle columns are visible below. "
                   "In real data, only the observed outcome column exists.")
        sample = df.head(12)[
            ["episode_id", "severity", "treatment_label",
             "potential_outcome_0", "potential_outcome_1", "outcome"]
        ].copy()
        st.markdown(
            _render_po_table(sample),
            unsafe_allow_html=True,
        )
        st.caption(
            "★ Observed outcome (pale blue highlight, bold). "
            "[missing] = counterfactual — not available in real data."
        )
    else:
        st.warning(
            "Enable **Teaching mode** in the sidebar to reveal oracle columns "
            "(Y(0) and Y(1)). In normal mode only the observed outcome is shown."
        )
        sample = df.head(12)[["episode_id", "severity", "treatment_label", "outcome"]].copy()
        sample.columns = ["Episode", "Severity", "Assigned treatment", "Observed outcome"]
        st.dataframe(
            sample.style.format({"Severity": "{:.2f}", "Observed outcome": "{:.1f}"}),
            use_container_width=True,
        )

    # --- Missing counterfactual chart ---
    st.subheader("Observed vs. missing counterfactual")

    plot_df = df.head(40).copy()
    plot_df["observed_marker"] = plot_df["outcome"]
    if teaching_mode:
        plot_df["missing_marker"] = plot_df.apply(
            lambda r: r["potential_outcome_0"] if r["treatment"] == 1
                      else r["potential_outcome_1"],
            axis=1,
        )
    else:
        plot_df["missing_marker"] = None

    fig_po = go.Figure()
    fig_po.add_trace(go.Scatter(
        x=plot_df.index, y=plot_df["observed_marker"],
        mode="markers", name="Observed outcome",
        marker=dict(symbol="circle", size=8, color="#1f77b4"),
    ))
    if teaching_mode:
        fig_po.add_trace(go.Scatter(
            x=plot_df.index, y=plot_df["missing_marker"],
            mode="markers", name="Missing counterfactual (oracle)",
            marker=dict(symbol="x", size=8, color="#d62728", opacity=0.5),
        ))
    fig_po.update_layout(
        title="First 40 episodes: observed outcome (●) vs. missing counterfactual (✕, oracle only)",
        xaxis_title="Episode index",
        yaxis_title="customer_impact_minutes_24h",
        legend=dict(orientation="h", y=-0.2),
        height=350,
    )
    st.plotly_chart(fig_po, use_container_width=True)

    if teaching_mode and ground_truth is not None:
        st.subheader("Oracle ATE (teaching mode only)")
        st.warning(
            f"**Oracle / simulator truth** — finite-sample ATE = "
            f"**{ground_truth.finite_sample_ate:.1f} minutes** "
            f"(mean Y(1) = {ground_truth.mean_y1:.1f}, "
            f"mean Y(0) = {ground_truth.mean_y0:.1f}). "
            "This value is computed from the hidden potential outcomes. "
            "It is not available in real data."
        )

    st.subheader("Reflection")
    st.info(LESSON_2.reflection)


# ===========================================================================
# SANDBOX
# ===========================================================================

else:
    st.title("Sandbox — randomized estimate")
    st.write(
        "This sandbox generates data under randomized assignment and computes "
        "a difference-in-means estimate. Use the sidebar to change the seed, "
        "sample size, or enable teaching mode."
    )

    # --- Analysis card ---
    st.subheader("Analysis card")
    card_rows = [
        ("Causal question", "Average effect of EARLY_COORDINATED_RESPONSE vs. MONITOR_REASSESS "
                            "on customer_impact_minutes_24h over 24 hours"),
        ("Target population", _ESTIMAND.population),
        ("Time zero", _ESTIMAND.time_zero),
        ("Intervention", _ESTIMAND.treatment_label_1.value),
        ("Comparator", _ESTIMAND.treatment_label_0.value),
        ("Outcome", f"{_ESTIMAND.outcome_name} ({_ESTIMAND.outcome_units})"),
        ("Follow-up", f"{_ESTIMAND.follow_up_hours} hours"),
        ("Estimand", _ESTIMAND.description),
        ("Estimator", result.estimator_name),
        ("Adjustment variables", "None (randomized scenario)"),
        ("Sample size", str(result.sample_size)),
        ("Treated / control", f"{result.treatment_counts.get('treated', '?')} / "
                              f"{result.treatment_counts.get('control', '?')}"),
        ("Point estimate", f"{result.estimate:.2f} minutes"),
        ("95% bootstrap CI",
         f"[{result.confidence_interval[0]:.2f}, {result.confidence_interval[1]:.2f}]"
         if result.confidence_interval else "n/a"),
        ("Provenance — seed", str(result.provenance.seed)),
        ("Provenance — scenario", result.provenance.scenario_id),
        ("Provenance — generator", result.provenance.generator_version),
    ]
    st.table(pd.DataFrame(card_rows, columns=["Field", "Value"]))

    # --- Oracle comparison (teaching mode) ---
    if teaching_mode and result.oracle_comparison is not None:
        oc = result.oracle_comparison
        st.warning(
            f"**Oracle / simulator truth** — oracle ATE = {oc.oracle_ate:.2f} min | "
            f"estimate = {oc.estimate:.2f} min | "
            f"absolute error = {oc.absolute_error:.2f} min. "
            "Oracle values are not available in real data."
        )

    # --- Outcome distributions ---
    st.subheader("Outcome distributions by treatment group")
    plot_df_dist = df.copy()
    plot_df_dist["treatment_label"] = plot_df_dist["treatment_label"].astype(str)
    fig_dist = px.histogram(
        plot_df_dist, x="outcome", color="treatment_label",
        barmode="overlay", nbins=40,
        labels={"outcome": "customer_impact_minutes_24h",
                "treatment_label": "Treatment"},
        title="Outcome distribution: EARLY_COORDINATED_RESPONSE vs. MONITOR_REASSESS",
        color_discrete_map={
            "EARLY_COORDINATED_RESPONSE": "#2ca02c",
            "MONITOR_REASSESS": "#d62728",
        },
    )
    fig_dist.update_layout(legend=dict(orientation="h", y=-0.2), height=350)
    st.plotly_chart(fig_dist, use_container_width=True)

    # --- Estimate chart ---
    st.subheader("Estimate and uncertainty")
    ci = result.confidence_interval or (result.estimate, result.estimate)

    fig_est = go.Figure()
    fig_est.add_trace(go.Scatter(
        x=[result.estimate], y=["Difference in means"],
        mode="markers", name="Estimate",
        marker=dict(symbol="diamond", size=14, color="#1f77b4"),
        error_x=dict(
            type="data",
            symmetric=False,
            array=[ci[1] - result.estimate],
            arrayminus=[result.estimate - ci[0]],
            color="#1f77b4",
        ),
    ))
    if teaching_mode and result.oracle_comparison is not None:
        fig_est.add_trace(go.Scatter(
            x=[result.oracle_comparison.oracle_ate], y=["Difference in means"],
            mode="markers", name="Oracle ATE (teaching mode)",
            marker=dict(symbol="star", size=14, color="#ff7f0e"),
        ))
    fig_est.add_vline(x=0, line_dash="dash", line_color="#888",
                      annotation_text="No effect", annotation_position="top right")
    fig_est.update_layout(
        title="ATE estimate with 95% bootstrap CI (negative = beneficial)",
        xaxis_title="customer_impact_minutes_24h (mean difference)",
        yaxis=dict(visible=False),
        height=220,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", y=-0.3),
    )
    st.plotly_chart(fig_est, use_container_width=True)

    # --- Warnings ---
    if result.has_warnings:
        st.subheader("Warnings and diagnostics")
        for w in result.warnings:
            st.warning(f"⚠️ {w}")
        for d in result.diagnostics:
            if d.level.value in ("warning", "error"):
                st.warning(f"⚠️ [{d.code}] {d.message}")

    # --- Assumptions ---
    with st.expander("Identification assumptions"):
        for a in result.assumptions:
            st.write(f"• {a}")

    # --- Interpretation ---
    st.subheader("Plain-language interpretation")
    direction = "reduced" if result.estimate < 0 else "increased"
    st.write(
        f"Under the randomized synthetic scenario, early coordinated response "
        f"{direction} average customer-impact minutes over 24 hours by approximately "
        f"**{abs(result.estimate):.1f} minutes** in this sample "
        f"(95% CI: [{ci[0]:.1f}, {ci[1]:.1f}] min). "
        "This estimate is illustrative, depends on the simulated protocol and "
        "outcome definition, and does not establish an effect in real telecom operations."
    )

    # --- Limitations ---
    with st.expander("Limitations"):
        st.write(
            "• All data are entirely synthetic. Results do not represent real "
            "telecom operations or real organizations.\n"
            "• The bootstrap CI reflects sampling variability only. It does not "
            "quantify unmeasured-confounding uncertainty.\n"
            "• This scenario uses randomized assignment. Confounded observational "
            "scenarios are introduced in Lesson 4.\n"
            "• V0 uses a single baseline confounder (severity). Richer confounding "
            "structures are deferred to V1."
        )

    # --- Provenance ---
    with st.expander("Provenance"):
        st.json({
            "seed": result.provenance.seed,
            "scenario_id": result.provenance.scenario_id,
            "generator_version": result.provenance.generator_version,
            "schema_version": result.provenance.schema_version,
            "oracle_used": result.provenance.oracle_used,
            "config_hash": result.provenance.config_hash,
            "created_at": str(result.provenance.created_at),
        })
