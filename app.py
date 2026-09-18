"""
app.py — V0 Slice 6 Streamlit application.

Six-lesson course + sandbox. All lessons display:
  - causal question, treatment, comparator, outcome, follow-up, estimand
  - identification assumptions
  - synthetic-data disclaimer
  - bootstrap-uncertainty caveat where estimates are shown
  - provenance panel

Accessibility (Slice 6):
  - High-contrast colors throughout (WCAG AA minimum).
  - Observed vs. counterfactual distinguished by color + symbol + text label.
  - Chart legends use both color and shape/dash encoding.
  - No essential information conveyed by color alone.
  - Oracle values hidden in normal mode; labeled explicitly in teaching mode.

All data are entirely synthetic and illustrative.
Results do not represent real telecom operations, real organizations,
or real interventions.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from causal_resilience.foundations.schemas import (
    AssignmentMode,
    Estimand,
    ScenarioConfig,
)
from causal_resilience.foundations.dgp import TelecomFoundationsDGP
from causal_resilience.foundations.estimators import (
    DifferenceInMeans, EstimatorConfig, Standardization, IPW,
)
from causal_resilience.foundations.lessons import (
    LESSON_1, LESSON_2, LESSON_3, LESSON_4, LESSON_5, LESSON_6,
    SYNTHETIC_DATA_DISCLAIMER, BOOTSTRAP_CAVEAT, ORACLE_CAVEAT,
)
from causal_resilience.foundations.diagnostics import (
    compute_overlap, compute_weight_diagnostic, compute_balance,
)
from causal_resilience.foundations.tables import build_po_table_rows, render_po_table

# ---------------------------------------------------------------------------
# Accessible color palette
# All colors checked for WCAG AA contrast against white and dark backgrounds.
# Shape/dash encoding duplicates color so charts are readable without color.
# ---------------------------------------------------------------------------
_C_ECR   = "#0072b2"   # blue  — EARLY_COORDINATED_RESPONSE
_C_MR    = "#d55e00"   # vermillion — MONITOR_REASSESS
_C_CRUDE = "#d55e00"   # vermillion — crude DiM (biased)
_C_STD   = "#009e73"   # green  — standardization
_C_IPW   = "#0072b2"   # blue   — IPW
_C_ORACLE = "#e69f00"  # amber  — oracle (teaching mode)
_C_CONF  = "#cc79a7"   # pink   — confounder path in DAG
_C_CAUSAL = "#0072b2"  # blue   — causal path in DAG
_C_ZERO  = "#555555"   # grey   — no-effect reference line

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Causal Resilience — V0 Foundations",
    page_icon="\U0001f52c",
    layout="wide",
)

_DGP = TelecomFoundationsDGP()
_ESTIMAND = Estimand()
_ESTIMATOR = DifferenceInMeans()

# ---------------------------------------------------------------------------
# Sidebar — scenario controls
# ---------------------------------------------------------------------------

st.sidebar.title("Scenario controls")

seed = st.sidebar.number_input(
    "Random seed", min_value=0, max_value=99_999, value=42, step=1
)
n_episodes = st.sidebar.slider(
    "Episodes", min_value=50, max_value=5_000, value=500, step=50
)
teaching_mode = st.sidebar.toggle("Teaching mode (show oracle)", value=False)

assignment_mode_label = st.sidebar.selectbox(
    "Assignment mode",
    ["Randomized", "Confounded"],
    index=0,
)
assignment_mode = (
    AssignmentMode.RANDOMIZED if assignment_mode_label == "Randomized"
    else AssignmentMode.CONFOUNDED
)

confounding_strength = 3.0
if assignment_mode == AssignmentMode.CONFOUNDED:
    confounding_strength = st.sidebar.slider(
        "Confounding strength", min_value=1.0, max_value=8.0, value=3.0, step=0.5
    )

if teaching_mode:
    st.sidebar.warning(
        "\u26a0\ufe0f **Teaching mode ON** \u2014 oracle / simulator truth is visible. "
        "These values are not available in real data."
    )

st.sidebar.caption(
    f"Seed: {int(seed)} | n: {int(n_episodes)} | "
    f"Mode: {assignment_mode_label} | Oracle: {'ON' if teaching_mode else 'OFF'}"
)

config = ScenarioConfig(
    seed=int(seed),
    n_episodes=int(n_episodes),
    assignment_mode=assignment_mode,
    confounding_strength=confounding_strength,
    teaching_mode=teaching_mode,
    scenario_id="v0-slice6",
)

dataset = _DGP.generate(config)
df = dataset.to_dataframe()

ground_truth = _DGP.truth(dataset) if teaching_mode else None

est_config = EstimatorConfig(bootstrap_iterations=1000, bootstrap_seed=0)
result = _ESTIMATOR.estimate(dataset, _ESTIMAND, est_config, ground_truth=ground_truth)

# ---------------------------------------------------------------------------
# Shared UI helpers
# ---------------------------------------------------------------------------

def _disclaimer() -> None:
    """Render the synthetic-data disclaimer on every lesson page."""
    st.caption(f"\U0001f6ab {SYNTHETIC_DATA_DISCLAIMER}")


def _lesson_header(lesson) -> None:
    """Render the standard lesson header: causal question card + disclaimer."""
    with st.expander("Causal question, estimand, and assumptions", expanded=False):
        st.markdown(f"**Causal question:** {lesson.causal_question}")
        st.markdown(f"**Intervention:** {lesson.treatment}")
        st.markdown(f"**Comparator:** {lesson.comparator}")
        st.markdown(f"**Outcome:** {lesson.outcome}")
        st.markdown(f"**Follow-up:** {lesson.follow_up}")
        st.markdown(f"**Estimand:** `{lesson.estimand}`")
        st.markdown("**Identification assumptions:**")
        for a in lesson.assumptions:
            st.write(f"  \u2022 {a}")
    _disclaimer()


def _provenance_expander(prov, teaching_mode: bool, n: int, mode: str) -> None:
    """Render a provenance expander on every lesson page."""
    with st.expander("Provenance"):
        st.json({
            "seed": prov.seed,
            "scenario_id": prov.scenario_id,
            "n_episodes": n,
            "assignment_mode": mode,
            "generator_version": prov.generator_version,
            "schema_version": prov.schema_version,
            "oracle_used": prov.oracle_used,
            "config_hash": prov.config_hash,
            "teaching_mode": teaching_mode,
            "created_at": str(prov.created_at),
        })


def _bootstrap_note() -> None:
    st.caption(f"\U0001f4ca {BOOTSTRAP_CAVEAT}")


def _show_estimate_chart(res, gt, teaching_mode: bool) -> None:
    """Estimate + 95% CI chart with optional oracle marker."""
    ci = res.confidence_interval or (res.estimate, res.estimate)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[res.estimate], y=["Difference in means"],
        mode="markers", name="Estimate (diamond)",
        marker=dict(symbol="diamond", size=14, color=_C_CRUDE),
        error_x=dict(
            type="data", symmetric=False,
            array=[ci[1] - res.estimate],
            arrayminus=[res.estimate - ci[0]],
            color=_C_CRUDE,
        ),
    ))
    if teaching_mode and res.oracle_comparison is not None:
        fig.add_trace(go.Scatter(
            x=[res.oracle_comparison.oracle_ate], y=["Difference in means"],
            mode="markers", name="Oracle ATE \u2605 (teaching mode only)",
            marker=dict(symbol="star", size=16, color=_C_ORACLE),
        ))
    fig.add_vline(x=0, line_dash="dash", line_color=_C_ZERO,
                  annotation_text="No effect", annotation_position="top right")
    fig.update_layout(
        title="ATE estimate with 95% bootstrap CI (negative = beneficial)",
        xaxis_title="customer_impact_minutes_24h (mean difference)",
        yaxis=dict(visible=False), height=220,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", y=-0.35),
    )
    st.plotly_chart(fig, use_container_width=True)
    _bootstrap_note()


def _render_dag() -> go.Figure:
    """V0 baseline DAG with accessible color + shape encoding."""
    nodes = {"severity": (1.0, 1.8), "treatment": (0.0, 1.0), "outcome": (2.0, 1.0)}
    edges = [
        ("severity", "treatment", _C_CONF,  "Confounder path (backdoor)"),
        ("severity", "outcome",   _C_CONF,  "Confounder path (backdoor)"),
        ("treatment", "outcome",  _C_CAUSAL, "Causal path"),
    ]
    fig = go.Figure()
    for src, dst, color, _label in edges:
        x0, y0 = nodes[src]
        x1, y1 = nodes[dst]
        fig.add_annotation(
            x=x1, y=y1, ax=x0, ay=y0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.5,
            arrowwidth=2.5, arrowcolor=color,
        )
    node_colors = {
        "severity": _C_CONF, "treatment": _C_CAUSAL, "outcome": _C_CAUSAL,
    }
    for name, (x, y) in nodes.items():
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            text=[name], textposition="top center",
            marker=dict(
                size=28, color=node_colors[name],
                line=dict(color="white", width=2),
            ),
            textfont=dict(color="#000000", size=13),
            showlegend=False,
        ))
    for color, label, dash in [
        (_C_CONF,   "Confounder path (backdoor) \u2014 pink/dashed", "dash"),
        (_C_CAUSAL, "Causal path \u2014 blue/solid", "solid"),
    ]:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=color, width=3, dash=dash),
            name=label,
        ))
    fig.update_layout(
        title="V0 baseline DAG: severity is a common cause of treatment and outcome",
        xaxis=dict(visible=False, range=[-0.5, 2.5]),
        yaxis=dict(visible=False, range=[0.6, 2.1]),
        height=300, margin=dict(t=50, b=20),
        legend=dict(orientation="h", y=-0.05),
        plot_bgcolor="white",
    )
    return fig


def _estimator_comparison_chart(
    r_crude, r_std, r_ipw, gt, teaching_mode: bool
) -> go.Figure:
    """Three-estimator forest plot with accessible color + shape encoding."""
    rows = [
        ("Crude DiM \u25c6 (biased under confounding)", r_crude, _C_CRUDE, "diamond"),
        ("Standardization \u25a0",                       r_std,   _C_STD,   "square"),
        ("IPW \u25b2",                                   r_ipw,   _C_IPW,   "triangle-up"),
    ]
    fig = go.Figure()
    for name, r, color, symbol in rows:
        ci = r.confidence_interval or (r.estimate, r.estimate)
        fig.add_trace(go.Scatter(
            x=[r.estimate], y=[name], mode="markers", name=name,
            marker=dict(symbol=symbol, size=14, color=color),
            error_x=dict(
                type="data", symmetric=False,
                array=[ci[1] - r.estimate],
                arrayminus=[r.estimate - ci[0]],
                color=color,
            ),
        ))
    if teaching_mode and gt is not None:
        fig.add_vline(
            x=gt.finite_sample_ate, line_dash="dot", line_color=_C_ORACLE,
            annotation_text="\u2605 Oracle ATE (teaching mode)",
            annotation_position="top right",
        )
    fig.add_vline(x=0, line_dash="dash", line_color=_C_ZERO,
                  annotation_text="No effect", annotation_position="bottom right")
    fig.update_layout(
        title="ATE estimates with 95% bootstrap CI",
        xaxis_title="customer_impact_minutes_24h (mean difference)",
        yaxis=dict(autorange="reversed"),
        height=300, margin=dict(t=50, b=40),
        legend=dict(orientation="h", y=-0.35),
    )
    return fig


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

page = st.sidebar.radio(
    "Course",
    [
        "Lesson 1 \u2014 Causal question",
        "Lesson 2 \u2014 Potential outcomes",
        "Lesson 3 \u2014 Randomization",
        "Lesson 4 \u2014 Confounding and the DAG",
        "Lesson 5 \u2014 Adjustment",
        "Lesson 6 \u2014 Diagnostics",
        "Sandbox",
    ],
    index=0,
)

# ===========================================================================
# LESSON 1
# ===========================================================================

if page == "Lesson 1 \u2014 Causal question":
    st.title(f"Lesson 1: {LESSON_1.title}")
    st.caption(f"Source: {LESSON_1.source_reference}")
    _lesson_header(LESSON_1)

    st.subheader("Learning objective")
    st.write(LESSON_1.objective)

    st.subheader("Explanation")
    st.write(LESSON_1.explanation)

    st.subheader("Target-trial card")
    trial_rows = [
        ("Eligibility", "Eligible synthetic incidents at detection with observed baseline severity"),
        ("Time zero", "First reliable detection timestamp"),
        ("Intervention", "EARLY_COORDINATED_RESPONSE"),
        ("Comparator", "MONITOR_REASSESS"),
        ("Assignment", assignment_mode_label),
        ("Follow-up", "24 hours from detection"),
        ("Outcome", "customer_impact_minutes_24h"),
        ("Censoring", "None \u2014 complete outcome observation assumed"),
        ("Causal contrast", "Population average treatment effect (ATE)"),
        ("Target estimand", "E[Y(1) \u2212 Y(0)]"),
    ]
    st.table(pd.DataFrame(trial_rows, columns=["Component", "V0 definition"]))

    st.subheader("Treatment timeline")
    fig_tl = go.Figure()
    fig_tl.add_shape(type="line", x0=0, x1=24, y0=0.5, y1=0.5,
                     line=dict(color="#333333", width=2))
    events = [
        (0,    "Detection\n(time zero)",                          "#333333"),
        (0.25, "EARLY_COORDINATED_RESPONSE\nassigned within 15 min", _C_ECR),
        (1.0,  "MONITOR_REASSESS\nreassess at 60 min",            _C_MR),
        (24,   "Outcome measured\n(24 h)",                        _C_ORACLE),
    ]
    for x, label, color in events:
        fig_tl.add_shape(type="line", x0=x, x1=x, y0=0.3, y1=0.7,
                         line=dict(color=color, width=2, dash="dot"))
        fig_tl.add_annotation(x=x, y=0.78, text=label, showarrow=False,
                               font=dict(size=11, color=color), align="center")
    fig_tl.update_layout(
        title="Incident timeline: detection \u2192 intervention \u2192 24-hour outcome",
        xaxis=dict(title="Hours after detection", range=[-1, 25]),
        yaxis=dict(visible=False, range=[0, 1.2]),
        height=220, margin=dict(t=50, b=40),
    )
    st.plotly_chart(fig_tl, use_container_width=True)

    st.subheader("Limitation")
    st.warning(LESSON_1.limitation)
    st.subheader("Reflection")
    st.info(LESSON_1.reflection)
    _provenance_expander(result.provenance, teaching_mode, int(n_episodes), assignment_mode_label)


# ===========================================================================
# LESSON 2
# ===========================================================================

elif page == "Lesson 2 \u2014 Potential outcomes":
    st.title(f"Lesson 2: {LESSON_2.title}")
    st.caption(f"Source: {LESSON_2.source_reference}")
    _lesson_header(LESSON_2)

    st.subheader("Learning objective")
    st.write(LESSON_2.objective)
    st.subheader("Explanation")
    st.write(LESSON_2.explanation)

    st.subheader("Two-world potential-outcome table")
    if teaching_mode:
        st.success(
            "\u26a0\ufe0f **Teaching mode** \u2014 oracle columns are visible below. "
            "In real data, only the observed outcome column exists. "
            + ORACLE_CAVEAT
        )
        sample = df.head(12)[
            ["episode_id", "severity", "treatment_label",
             "potential_outcome_0", "potential_outcome_1", "outcome"]
        ].copy()
        st.markdown(render_po_table(sample), unsafe_allow_html=True)
        st.caption(
            "\u2605 Observed outcome (dark blue, bold). "
            "[missing] = counterfactual \u2014 not available in real data."
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

    st.subheader("Observed vs. missing counterfactual")
    plot_df = df.head(40).copy()
    fig_po = go.Figure()
    fig_po.add_trace(go.Scatter(
        x=plot_df.index, y=plot_df["outcome"],
        mode="markers", name="Observed outcome \u25cf",
        marker=dict(symbol="circle", size=8, color=_C_ECR),
    ))
    if teaching_mode:
        missing = plot_df.apply(
            lambda r: r["potential_outcome_0"] if r["treatment"] == 1
                      else r["potential_outcome_1"], axis=1,
        )
        fig_po.add_trace(go.Scatter(
            x=plot_df.index, y=missing,
            mode="markers", name="Missing counterfactual \u2715 (oracle only)",
            marker=dict(symbol="x", size=9, color=_C_MR),
        ))
    fig_po.update_layout(
        title="First 40 episodes: observed (\u25cf) vs. missing counterfactual (\u2715, oracle only)",
        xaxis_title="Episode index",
        yaxis_title="customer_impact_minutes_24h",
        legend=dict(orientation="h", y=-0.25), height=350,
    )
    st.plotly_chart(fig_po, use_container_width=True)

    if teaching_mode and ground_truth is not None:
        st.subheader("Oracle ATE (teaching mode only)")
        st.warning(
            f"\u2605 **Oracle / simulator truth** \u2014 finite-sample ATE = "
            f"**{ground_truth.finite_sample_ate:.1f} minutes** "
            f"(mean Y(1) = {ground_truth.mean_y1:.1f}, "
            f"mean Y(0) = {ground_truth.mean_y0:.1f}). "
            + ORACLE_CAVEAT
        )

    st.subheader("Limitation")
    st.warning(LESSON_2.limitation)
    st.subheader("Reflection")
    st.info(LESSON_2.reflection)
    _provenance_expander(result.provenance, teaching_mode, int(n_episodes), assignment_mode_label)


# ===========================================================================
# LESSON 3
# ===========================================================================

elif page == "Lesson 3 \u2014 Randomization":
    st.title(f"Lesson 3: {LESSON_3.title}")
    st.caption(f"Source: {LESSON_3.source_reference}")
    if assignment_mode != AssignmentMode.RANDOMIZED:
        st.warning("Set **Assignment mode** to Randomized in the sidebar for this lesson.")
    _lesson_header(LESSON_3)

    st.subheader("Learning objective")
    st.write(LESSON_3.objective)
    st.subheader("Explanation")
    st.write(LESSON_3.explanation)

    st.subheader("Severity balance by treatment group")
    fig_bal = go.Figure()
    for label, color, dash in [
        ("EARLY_COORDINATED_RESPONSE", _C_ECR, "solid"),
        ("MONITOR_REASSESS",           _C_MR,  "dash"),
    ]:
        grp = df[df["treatment_label"].astype(str) == label]["severity"]
        fig_bal.add_trace(go.Histogram(
            x=grp, name=label, opacity=0.7, nbinsx=20,
            marker_color=color,
        ))
    fig_bal.update_layout(
        barmode="overlay",
        title="Severity distribution by treatment group",
        xaxis_title="Severity", yaxis_title="Count",
        legend=dict(orientation="h", y=-0.25), height=320,
    )
    st.plotly_chart(fig_bal, use_container_width=True)
    st.caption("Under randomization the two distributions should overlap closely.")

    st.subheader("Estimate vs. oracle ATE")
    _show_estimate_chart(result, ground_truth, teaching_mode)

    st.subheader("Limitation")
    st.warning(LESSON_3.limitation)
    st.subheader("Reflection")
    st.info(LESSON_3.reflection)
    _provenance_expander(result.provenance, teaching_mode, int(n_episodes), assignment_mode_label)


# ===========================================================================
# LESSON 4
# ===========================================================================

elif page == "Lesson 4 \u2014 Confounding and the DAG":
    st.title(f"Lesson 4: {LESSON_4.title}")
    st.caption(f"Source: {LESSON_4.source_reference}")
    if assignment_mode != AssignmentMode.CONFOUNDED:
        st.warning("Set **Assignment mode** to Confounded in the sidebar for this lesson.")
    _lesson_header(LESSON_4)

    st.subheader("Learning objective")
    st.write(LESSON_4.objective)
    st.subheader("Explanation")
    st.write(LESSON_4.explanation)

    st.subheader("Causal DAG")
    st.plotly_chart(_render_dag(), use_container_width=True)
    st.caption(
        "Pink/dashed arrows: confounder paths (backdoor). "
        "Blue/solid arrow: causal path. "
        "The backdoor path treatment \u2190 severity \u2192 outcome opens a non-causal association."
    )

    st.subheader("Severity balance by treatment group")
    fig_bal4 = go.Figure()
    for label, color in [
        ("EARLY_COORDINATED_RESPONSE", _C_ECR),
        ("MONITOR_REASSESS",           _C_MR),
    ]:
        grp = df[df["treatment_label"].astype(str) == label]["severity"]
        fig_bal4.add_trace(go.Histogram(
            x=grp, name=label, opacity=0.7, nbinsx=20,
            marker_color=color,
        ))
    fig_bal4.update_layout(
        barmode="overlay",
        title="Severity distribution by treatment group (confounded)",
        xaxis_title="Severity", yaxis_title="Count",
        legend=dict(orientation="h", y=-0.25), height=320,
    )
    st.plotly_chart(fig_bal4, use_container_width=True)
    st.caption("Under confounding, higher-severity episodes cluster in the treated group.")

    st.subheader("Crude estimate vs. oracle ATE")
    _show_estimate_chart(result, ground_truth, teaching_mode)
    if teaching_mode and result.oracle_comparison is not None:
        bias = result.estimate - result.oracle_comparison.oracle_ate
        st.info(
            f"Confounding bias \u2248 **{bias:+.1f} minutes** "
            f"(crude {result.estimate:.1f} \u2212 oracle {result.oracle_comparison.oracle_ate:.1f}). "
            "Adjustment for severity is introduced in Lesson 5."
        )

    st.subheader("Limitation")
    st.warning(LESSON_4.limitation)
    st.subheader("Reflection")
    st.info(LESSON_4.reflection)
    _provenance_expander(result.provenance, teaching_mode, int(n_episodes), assignment_mode_label)


# ===========================================================================
# LESSON 5
# ===========================================================================

elif page == "Lesson 5 \u2014 Adjustment":
    st.title(f"Lesson 5: {LESSON_5.title}")
    st.caption(f"Source: {LESSON_5.source_reference}")
    if assignment_mode != AssignmentMode.CONFOUNDED:
        st.warning("Set **Assignment mode** to Confounded in the sidebar for this lesson.")
    _lesson_header(LESSON_5)

    st.subheader("Learning objective")
    st.write(LESSON_5.objective)
    st.subheader("Explanation")
    st.write(LESSON_5.explanation)

    est_cfg_l5 = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=0)
    r_crude = DifferenceInMeans().estimate(dataset, _ESTIMAND, est_cfg_l5, ground_truth=ground_truth)
    r_std   = Standardization().estimate(dataset, _ESTIMAND, est_cfg_l5, ground_truth=ground_truth)
    r_ipw   = IPW().estimate(dataset, _ESTIMAND, est_cfg_l5, ground_truth=ground_truth)

    st.subheader("Estimator comparison")
    st.plotly_chart(
        _estimator_comparison_chart(r_crude, r_std, r_ipw, ground_truth, teaching_mode),
        use_container_width=True,
    )
    st.caption(
        "Crude DiM \u25c6 (vermillion) is biased under confounding. "
        "Standardization \u25a0 (green) and IPW \u25b2 (blue) adjust for severity. "
        "Shape encoding duplicates color."
    )
    _bootstrap_note()

    if teaching_mode and ground_truth is not None:
        st.info(
            f"\u2605 Oracle ATE = **{ground_truth.finite_sample_ate:.1f} min** "
            f"| Crude DiM = {r_crude.estimate:.1f} "
            f"| Standardization = {r_std.estimate:.1f} "
            f"| IPW = {r_ipw.estimate:.1f}. "
            + ORACLE_CAVEAT
        )

    st.subheader("Propensity overlap")
    ps, w = IPW().get_propensity_and_weights(dataset)
    trt_arr = df["treatment"].to_numpy()
    fig_ps = go.Figure()
    for label, mask, color in [
        ("EARLY_COORDINATED_RESPONSE", trt_arr == 1, _C_ECR),
        ("MONITOR_REASSESS",           trt_arr == 0, _C_MR),
    ]:
        fig_ps.add_trace(go.Histogram(
            x=ps[mask], name=label, opacity=0.7, nbinsx=30,
            marker_color=color,
        ))
    fig_ps.update_layout(
        barmode="overlay",
        title="Estimated propensity score P(A=1 | severity) by treatment group",
        xaxis_title="P(A=1 | severity)", yaxis_title="Count",
        legend=dict(orientation="h", y=-0.25), height=300,
    )
    st.plotly_chart(fig_ps, use_container_width=True)

    st.subheader("IPW weight distribution")
    wd = compute_weight_diagnostic(w)
    fig_w = go.Figure(go.Histogram(x=w, nbinsx=40, marker_color=_C_IPW, opacity=0.8))
    fig_w.add_vline(x=10, line_dash="dash", line_color=_C_MR,
                    annotation_text="Extreme threshold (10)", annotation_position="top right")
    fig_w.update_layout(
        title=f"IPW weight distribution  |  ESS = {wd.effective_sample_size:.0f} / {len(w)}",
        xaxis_title="Weight", yaxis_title="Count", height=280,
    )
    st.plotly_chart(fig_w, use_container_width=True)
    if wd.warning_message:
        st.warning(f"\u26a0\ufe0f {wd.warning_message}")
    else:
        st.success(f"No extreme weights. ESS = {wd.effective_sample_size:.0f} of {len(w)} episodes.")

    st.subheader("Limitation")
    st.warning(LESSON_5.limitation)
    st.subheader("Reflection")
    st.info(LESSON_5.reflection)
    _provenance_expander(r_ipw.provenance, teaching_mode, int(n_episodes), assignment_mode_label)


# ===========================================================================
# LESSON 6
# ===========================================================================

elif page == "Lesson 6 \u2014 Diagnostics":
    st.title(f"Lesson 6: {LESSON_6.title}")
    st.caption(f"Source: {LESSON_6.source_reference}")
    _lesson_header(LESSON_6)

    st.subheader("Learning objective")
    st.write(LESSON_6.objective)
    st.subheader("Explanation")
    st.write(LESSON_6.explanation)

    est_cfg_l6 = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=0)
    r_crude = DifferenceInMeans().estimate(dataset, _ESTIMAND, est_cfg_l6, ground_truth=ground_truth)
    r_std   = Standardization().estimate(dataset, _ESTIMAND, est_cfg_l6, ground_truth=ground_truth)
    r_ipw   = IPW().estimate(dataset, _ESTIMAND, est_cfg_l6, ground_truth=ground_truth)
    ps, w   = IPW().get_propensity_and_weights(dataset)
    trt_arr = df["treatment"].to_numpy()
    sev_arr = df["severity"].to_numpy()

    st.subheader("Diagnostic 1 \u2014 Propensity overlap")
    overlap = compute_overlap(ps, trt_arr)
    col1, col2, col3 = st.columns(3)
    col1.metric("Treated ps range",
                f"{overlap.min_propensity_treated:.2f} \u2013 {overlap.max_propensity_treated:.2f}")
    col2.metric("Control ps range",
                f"{overlap.min_propensity_control:.2f} \u2013 {overlap.max_propensity_control:.2f}")
    col3.metric("Overlap adequate", "Yes \u2705" if overlap.overlap_adequate else "No \u26a0\ufe0f")
    if overlap.warning_message:
        st.warning(f"\u26a0\ufe0f {overlap.warning_message}")
    else:
        st.success("Propensity ranges overlap. Positivity assumption is supported.")

    st.subheader("Diagnostic 2 \u2014 Weight distribution and ESS")
    wd = compute_weight_diagnostic(w)
    col4, col5, col6 = st.columns(3)
    col4.metric("Max weight", f"{wd.max_weight:.1f}")
    col5.metric("% extreme (>10)", f"{wd.pct_extreme * 100:.1f}%")
    col6.metric("ESS", f"{wd.effective_sample_size:.0f} / {len(w)}")
    if wd.warning_message:
        st.warning(f"\u26a0\ufe0f {wd.warning_message}")
    else:
        st.success("No extreme weights detected.")

    st.subheader("Diagnostic 3 \u2014 Covariate balance (SMD)")
    balance = compute_balance(sev_arr, trt_arr, weights=w)
    col7, col8 = st.columns(2)
    col7.metric(
        "SMD unweighted", f"{balance.smd_unweighted:.3f}",
        delta="adequate \u2705" if balance.balance_adequate_unweighted else "imbalanced \u26a0\ufe0f",
        delta_color="normal" if balance.balance_adequate_unweighted else "inverse",
    )
    if balance.smd_weighted is not None:
        col8.metric(
            "SMD after IPW", f"{balance.smd_weighted:.3f}",
            delta="adequate \u2705" if balance.balance_adequate_weighted else "imbalanced \u26a0\ufe0f",
            delta_color="normal" if balance.balance_adequate_weighted else "inverse",
        )
    st.caption("SMD < 0.1 indicates adequate balance. SMD is computed for severity.")

    st.subheader("Estimator comparison with uncertainty")
    st.plotly_chart(
        _estimator_comparison_chart(r_crude, r_std, r_ipw, ground_truth, teaching_mode),
        use_container_width=True,
    )
    _bootstrap_note()

    st.subheader("Assumption checklist")
    # Exchangeability is supported when confounded (severity is measured and
    # adjustment is applied). Under randomization it holds unconditionally.
    exchangeability_ok = True  # holds by DGP construction in both modes
    checks = [
        ("Consistency", True,
         "Observed outcome equals potential outcome under assigned treatment (enforced by DGP)."),
        ("Exchangeability", exchangeability_ok,
         "Conditional on severity. Supported by DGP design; "
         "cannot be verified from observed data alone."),
        ("Positivity", overlap.overlap_adequate,
         f"Propensity ranges overlap: {overlap.overlap_adequate}."),
        ("No interference", True,
         "Episodes are independent in V0 (simplification)."),
        ("Complete follow-up", True,
         "24-hour outcome is observed for all episodes in V0."),
    ]
    for name, satisfied, note in checks:
        icon = "\u2705" if satisfied else "\u26a0\ufe0f"
        st.write(f"{icon} **{name}** \u2014 {note}")

    st.subheader("Limitation")
    st.warning(LESSON_6.limitation)
    st.subheader("Reflection")
    st.info(LESSON_6.reflection)
    _provenance_expander(r_ipw.provenance, teaching_mode, int(n_episodes), assignment_mode_label)


# ===========================================================================
# SANDBOX
# ===========================================================================

else:
    st.title("Sandbox \u2014 full estimator comparison")
    st.write(
        "Use the sidebar to change seed, sample size, assignment mode, and "
        "teaching mode. All three estimators run on the current scenario."
    )
    _disclaimer()

    est_cfg_sb = EstimatorConfig(bootstrap_iterations=500, bootstrap_seed=0)
    r_crude = DifferenceInMeans().estimate(dataset, _ESTIMAND, est_cfg_sb, ground_truth=ground_truth)
    r_std   = Standardization().estimate(dataset, _ESTIMAND, est_cfg_sb, ground_truth=ground_truth)
    r_ipw   = IPW().estimate(dataset, _ESTIMAND, est_cfg_sb, ground_truth=ground_truth)

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
        ("Assignment mode", assignment_mode_label),
        ("Sample size", str(result.sample_size)),
        ("Treated / control",
         f"{result.treatment_counts.get('treated', '?')} / "
         f"{result.treatment_counts.get('control', '?')}"),
        ("Teaching mode", "ON (oracle visible)" if teaching_mode else "OFF"),
        ("Seed", str(int(seed))),
    ]
    st.table(pd.DataFrame(card_rows, columns=["Field", "Value"]))

    if teaching_mode and ground_truth is not None:
        st.warning(
            f"\u2605 **Oracle / simulator truth** \u2014 "
            f"oracle ATE = {ground_truth.finite_sample_ate:.2f} min. "
            + ORACLE_CAVEAT
        )

    st.subheader("Estimator comparison")
    st.plotly_chart(
        _estimator_comparison_chart(r_crude, r_std, r_ipw, ground_truth, teaching_mode),
        use_container_width=True,
    )
    _bootstrap_note()

    st.subheader("Outcome distributions by treatment group")
    plot_df_dist = df.copy()
    plot_df_dist["treatment_label"] = plot_df_dist["treatment_label"].astype(str)
    fig_dist = px.histogram(
        plot_df_dist, x="outcome", color="treatment_label",
        barmode="overlay", nbins=40,
        labels={"outcome": "customer_impact_minutes_24h", "treatment_label": "Treatment"},
        title="Outcome distribution: EARLY_COORDINATED_RESPONSE vs. MONITOR_REASSESS",
        color_discrete_map={
            "EARLY_COORDINATED_RESPONSE": _C_ECR,
            "MONITOR_REASSESS": _C_MR,
        },
    )
    fig_dist.update_layout(legend=dict(orientation="h", y=-0.2), height=350)
    st.plotly_chart(fig_dist, use_container_width=True)

    with st.expander("Identification assumptions"):
        for a in _ESTIMAND.assumptions:
            st.write(f"\u2022 {a}")

    with st.expander("Limitations"):
        st.write(
            "\u2022 All data are entirely synthetic. Results do not represent real "
            "telecom operations or real organizations.\n"
            f"\u2022 {BOOTSTRAP_CAVEAT}\n"
            "\u2022 V0 uses a single baseline confounder (severity). Richer confounding "
            "structures are deferred to V1.\n"
            "\u2022 Doubly robust estimation, IV, mediation, and survival analysis "
            "are out of scope for V0."
        )

    _provenance_expander(r_ipw.provenance, teaching_mode, int(n_episodes), assignment_mode_label)
