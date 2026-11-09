"""
ci_session1.py — Session 1 Period 1 Simulation
9-tab narrative: BI/ML Trap → Causal Inference
Spec: 03_session1_period1_simulation_spec-v6.md
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from scipy.optimize import brentq
from scipy.stats import gaussian_kde

st.set_page_config(page_title="CI Session 1 — Period 1", page_icon="🔬", layout="wide")

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
_CYAN   = "#64FFDA"
_ORANGE = "#E05C2A"
_AMBER  = "#F1C40F"
_GREY   = "#aaaaaa"
_T1     = "#0072b2"   # Tier-1 blue
_T2     = "#d55e00"   # Tier-2 vermillion
_TCO    = "#009e73"   # TCO green

# ---------------------------------------------------------------------------
# SCM
# ---------------------------------------------------------------------------
def generate_data(num_sites: int, mu_z: float, sigma_z: float,
                  x1_share: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Z — terrain difficulty (custom normal clipped to [1,10])
    Z = np.clip(rng.normal(mu_z, sigma_z, num_sites), 1.0, 10.0)

    # X — dispatcher selection bias (sigmoid on Z, then override to hit x1_share target)
    p_tier1 = 1.0 / (1.0 + np.exp(-1.2 * (Z - 5.5)))
    X_obs = rng.binomial(1, p_tier1).astype(float)
    # blend toward x1_share target so knob has visible effect
    n_target = int(round(x1_share * num_sites))
    idx_sorted = np.argsort(p_tier1)[::-1]
    X = np.zeros(num_sites)
    X[idx_sorted[:n_target]] = 1.0

    # Y1 — direct contract cost
    noise1 = rng.normal(0, 1500, num_sites)
    Y1 = np.where(X == 1,
                  60_000 + 8_333 * (Z - 1) + noise1,
                  45_000 + 7_222 * (Z - 1) + noise1)

    # M5 — construction duration (hidden)
    M5 = np.maximum(5.0 + 3.0 * Z - 5.0 * X + rng.normal(0, 1.5, num_sites), 7.0)

    # Y2 — SLA penalty
    Y2 = np.where(M5 <= 14, 0.0,
         np.where(M5 <= 21, (M5 - 14) * 2_000,
                  14_000 + (M5 - 21) * 5_000))

    # Y3 — rework cost
    noise3 = rng.normal(0, 1000, num_sites)
    Y3 = np.maximum(
        np.where(X == 1,
                 3_000 + 800  * (Z - 1) + noise3,
                 8_000 + 1_500 * (Z - 1) + noise3),
        0.0)

    Y_TCO = Y1 + Y2 + Y3

    return pd.DataFrame({
        "Z": Z, "X": X, "tier": np.where(X == 1, "Tier-1", "Tier-2"),
        "Y1": Y1, "Y2": Y2, "Y3": Y3, "Y_TCO": Y_TCO, "M5": M5,
        "p_tier1": p_tier1,
    })


def analytical_cate(z: float) -> float:
    """E[Y_TCO | X=1] - E[Y_TCO | X=0] at terrain z (no noise)."""
    y1_t1 = 60_000 + 8_333 * (z - 1)
    y1_t2 = 45_000 + 7_222 * (z - 1)
    m5_t1 = max(5.0 + 3.0 * z - 5.0, 7.0)
    m5_t2 = max(5.0 + 3.0 * z,        7.0)
    def sla(m): return 0 if m <= 14 else (m-14)*2000 if m <= 21 else 14000+(m-21)*5000
    y2_t1 = sla(m5_t1); y2_t2 = sla(m5_t2)
    y3_t1 = 3_000 + 800  * (z - 1)
    y3_t2 = 8_000 + 1_500 * (z - 1)
    return (y1_t1 + y2_t1 + y3_t1) - (y1_t2 + y2_t2 + y3_t2)

Z_STAR = brentq(analytical_cate, 1.0, 9.9)

# ---------------------------------------------------------------------------
# Hi-Fi knob
# ---------------------------------------------------------------------------
def render_knob(label: str, min_val: float, max_val: float,
                default_val: float, step: float,
                color_hex: str = _CYAN, key: str = "knob") -> float:
    html = f"""
    <div style="display:flex;flex-direction:column;align-items:center;
                font-family:'Inter',sans-serif;background:#0e1117;padding:12px;
                border-radius:12px;border:1px solid #1f242d;">
      <span style="color:#e8eaed;font-size:13px;font-weight:600;
                   margin-bottom:8px;letter-spacing:0.5px;">{label}</span>
      <div id="kc-{key}" style="position:relative;width:84px;height:84px;
           background:radial-gradient(circle,#2b303c 0%,#12151b 100%);
           border-radius:50%;box-shadow:0 4px 12px rgba(0,0,0,0.6),
           inset 0 1px 2px rgba(255,255,255,0.25);cursor:pointer;
           display:flex;align-items:center;justify-content:center;">
        <div id="cap-{key}" style="width:64px;height:64px;background:#1a1e26;
             border-radius:50%;border:1px solid #363c4a;position:relative;
             transition:transform 0.05s ease-out;">
          <div style="position:absolute;top:6px;left:50%;
               transform:translateX(-50%);width:4px;height:12px;
               background:{color_hex};border-radius:2px;
               box-shadow:0 0 10px {color_hex};"></div>
        </div>
      </div>
      <span id="val-{key}" style="color:{color_hex};font-size:17px;
            font-weight:700;margin-top:10px;font-family:monospace;">{default_val}</span>
    </div>
    <script>(function(){{
      let mn={min_val},mx={max_val},cv={default_val},st={step};
      const cap=document.getElementById('cap-{key}');
      const vd=document.getElementById('val-{key}');
      const kc=document.getElementById('kc-{key}');
      let drag=false,sy=0;
      function upd(v){{
        let pct=(v-mn)/(mx-mn);
        cap.style.transform=`rotate(${{-135+pct*270}}deg)`;
        vd.innerText=Number.isInteger(st)?v:v.toFixed(1);
      }}
      upd(cv);
      kc.addEventListener('mousedown',e=>{{drag=true;sy=e.clientY;}});
      window.addEventListener('mousemove',e=>{{
        if(!drag)return;
        let dy=sy-e.clientY,chg=(dy/120)*(mx-mn);
        let nv=Math.min(mx,Math.max(mn,cv+chg));
        nv=Math.round(nv/st)*st;
        if(nv!==cv){{cv=nv;upd(cv);if(window.Streamlit)window.Streamlit.setComponentValue(cv);}}
      }});
      window.addEventListener('mouseup',()=>{{drag=false;}});
    }})();</script>
    """
    result = components.html(html, height=150, key=key)
    return result if result is not None else default_val

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.title("Simulation controls")
num_sites   = st.sidebar.slider("Sites", 300, 5000, 500, 100)
country     = st.sidebar.selectbox("Country preset", ["Netherlands", "Norway"])
random_seed = st.sidebar.number_input("Seed", 0, 999, 42, 1)

mu_z_default    = 2.8 if country == "Netherlands" else 7.8
sigma_z_default = 1.2

mu_z_knob    = st.sidebar.slider("μZ (terrain mean)",   1.0, 10.0, mu_z_default,    0.1)
sigma_z_knob = st.sidebar.slider("σZ (terrain spread)", 0.5,  3.0, sigma_z_default, 0.1)
x1_share_knob = st.sidebar.slider("Tier-1 share",       0.0,  1.0, 0.5,             0.05)

df = generate_data(num_sites, mu_z_knob, sigma_z_knob, x1_share_knob, int(random_seed))

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "0 · Intro",
    "1 · BI / ML Trap",
    "2 · Confounders",
    "3 · Selection Bias",
    "4 · Full DAG",
    "5 · TCO Crossover",
    "6 · Naive vs Causal",
    "7 · Period 1 TOP 3",
    "8 · Lessons",
])

# ===========================================================================
# Tab 0 — Intro
# ===========================================================================
with tabs[0]:
    st.title("Session 1 · Period 1: From BI to Causal Inference")
    st.markdown(
        "> *Data shows what happened. It never shows why. "
        "And it never tells you what will happen if you intervene.*"
    )
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("Problem framing", expanded=True):
            st.markdown(
                "A telecom operator deploys **macro sites** across Western Europe "
                "at **€45k–€170k per site**. Two contractor tiers are available:\n\n"
                "- **Tier-1** — premium, faster, higher base contract cost\n"
                "- **Tier-2** — standard, slower, lower base contract cost\n\n"
                "The BI dashboard shows Tier-1 sites cost more on average. "
                "The CFO wants to eliminate Tier-1. Is that the right call?"
            )
    with c2:
        with st.expander("€45k–€170k cost context", expanded=True):
            st.markdown(
                "| Cost driver | Range |\n"
                "|---|---|\n"
                "| Direct contract (Y₁) | €45k–€135k |\n"
                "| SLA penalty (Y₂) | €0–€35k |\n"
                "| Rework cost (Y₃) | €3k–€20k |\n"
                "| **Total TCO** | **€45k–€170k** |\n\n"
                f"Crossover point Z* ≈ **{Z_STAR:.1f}** "
                "(terrain difficulty where Tier-1 becomes cheaper overall)"
            )

# ===========================================================================
# Tab 1 — BI / ML Trap
# ===========================================================================
with tabs[1]:
    st.header("1 · The BI / ML Trap")
    st.markdown(
        "**Scenario 1:** Only the Tier-1 share knob is visible. "
        "Terrain difficulty Z is hidden — just like in a real BI dashboard."
    )

    k_col, chart_col = st.columns([1, 3])
    with k_col:
        x1_s1 = render_knob("Tier-1 Share", 0.0, 1.0, x1_share_knob, 0.05,
                             color_hex=_CYAN, key="knob_x1_s1")
        x1_s1 = x1_s1 if x1_s1 is not None else x1_share_knob

    df_s1 = generate_data(num_sites, mu_z_knob, sigma_z_knob, float(x1_s1), int(random_seed))

    with chart_col:
        avg_cost = df_s1.groupby("tier")["Y1"].mean().reset_index()
        fig = px.bar(avg_cost, x="tier", y="Y1",
                     color="tier",
                     color_discrete_map={"Tier-1": _T1, "Tier-2": _T2},
                     labels={"Y1": "Avg Direct Contract Cost (€)", "tier": ""},
                     title="Naive BI view: average direct cost by tier (Z hidden)")
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    naive_t1 = df_s1[df_s1["X"] == 1]["Y1"].mean()
    naive_t2 = df_s1[df_s1["X"] == 0]["Y1"].mean()
    st.info(
        f"Tier-1 avg cost: **€{naive_t1:,.0f}** | "
        f"Tier-2 avg cost: **€{naive_t2:,.0f}** | "
        f"Naive gap: **€{naive_t1 - naive_t2:+,.0f}**\n\n"
        "❓ *Who cuts Tier-1?* — This number is real. The conclusion is wrong."
    )

    st.caption("Z (terrain difficulty) is hidden here — exactly as it is in most BI tools.")

    st.dataframe(
        df_s1[["tier", "Y1", "Y_TCO"]].rename(columns={
            "tier": "Tier", "Y1": "Direct Cost (€)", "Y_TCO": "Total TCO (€)"
        }).head(20).style.format({"Direct Cost (€)": "{:,.0f}", "Total TCO (€)": "{:,.0f}"}),
        use_container_width=True,
    )

# ===========================================================================
# Tab 2 — Confounders
# ===========================================================================
with tabs[2]:
    st.header("2 · Confounders — Terrain Difficulty Z")
    st.markdown(
        "Z is the hidden driver. Netherlands (μZ≈2.8) is mostly flat. "
        "Norway (μZ≈7.8) is mostly mountainous. "
        "The same contractor policy produces very different cost profiles."
    )

    fig_kde = go.Figure()
    for label, mu, sigma, color in [
        ("Netherlands (μZ=2.8)", 2.8, 1.2, _CYAN),
        ("Norway (μZ=7.8)",      7.8, 1.2, _ORANGE),
        (f"Current (μZ={mu_z_knob:.1f})", mu_z_knob, sigma_z_knob, _AMBER),
    ]:
        z_range = np.linspace(1, 10, 300)
        rng_tmp = np.random.default_rng(42)
        z_sample = np.clip(rng_tmp.normal(mu, sigma, 5000), 1, 10)
        kde = gaussian_kde(z_sample)
        fig_kde.add_trace(go.Scatter(x=z_range, y=kde(z_range),
                                     mode="lines", name=label,
                                     line=dict(color=color, width=2.5)))
    fig_kde.add_vline(x=Z_STAR, line_dash="dash", line_color=_TCO,
                      annotation_text=f"Z*≈{Z_STAR:.1f}", annotation_position="top right")
    fig_kde.update_layout(
        title="Terrain difficulty distribution by geography",
        xaxis_title="Z — Terrain Difficulty (1=flat, 10=extreme mountain)",
        yaxis_title="Density", height=380,
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_kde, use_container_width=True)
    st.caption(
        f"Dashed line = crossover Z*≈{Z_STAR:.1f}. "
        "Sites to the right of Z* are cheaper with Tier-1 on total TCO."
    )

# ===========================================================================
# Tab 3 — Selection Bias (Z → X), NOW WITH Y_TCO
# ===========================================================================
with tabs[3]:
    st.header("3 · Selection Bias — Z → X")
    st.markdown(
        "**Scenario 2:** Three knobs active. "
        "Dispatchers sent Tier-1 to the hardest sites — "
        "that's the backdoor path Z → X. "
        "Y (Total TCO) is shown here so you can see *why it matters*: "
        "Z drives both who gets Tier-1 **and** what the TCO ends up being."
    )

    k1, k2, k3 = st.columns(3)
    with k1:
        x1_s2 = render_knob("Tier-1 Share", 0.0, 1.0, x1_share_knob, 0.05,
                             color_hex=_CYAN, key="knob_x1_s2")
        x1_s2 = x1_s2 if x1_s2 is not None else x1_share_knob
    with k2:
        mu_s2 = render_knob("μZ Terrain Mean", 1.0, 10.0, mu_z_knob, 0.1,
                            color_hex=_ORANGE, key="knob_mu_s2")
        mu_s2 = mu_s2 if mu_s2 is not None else mu_z_knob
    with k3:
        sig_s2 = render_knob("σZ Terrain Spread", 0.5, 3.0, sigma_z_knob, 0.1,
                             color_hex=_AMBER, key="knob_sig_s2")
        sig_s2 = sig_s2 if sig_s2 is not None else sigma_z_knob

    df_s2 = generate_data(num_sites, float(mu_s2), float(sig_s2),
                          float(x1_s2), int(random_seed))

    col_left, col_right = st.columns(2)

    with col_left:
        # Tier-1 share by Z bin
        df_s2["Z_bin"] = pd.cut(df_s2["Z"], bins=np.arange(1, 11, 1))
        share_by_z = df_s2.groupby("Z_bin", observed=True)["X"].mean().reset_index()
        share_by_z["Z_mid"] = share_by_z["Z_bin"].apply(lambda b: b.mid)
        fig_share = go.Figure()
        fig_share.add_trace(go.Bar(
            x=share_by_z["Z_mid"].astype(float),
            y=share_by_z["X"],
            marker_color=_T1, name="Tier-1 share",
        ))
        # sigmoid overlay
        z_line = np.linspace(1, 10, 200)
        p_line = 1 / (1 + np.exp(-1.2 * (z_line - 5.5)))
        fig_share.add_trace(go.Scatter(
            x=z_line, y=p_line, mode="lines",
            line=dict(color=_ORANGE, width=2.5, dash="dot"),
            name="Sigmoid P(Tier-1|Z)",
        ))
        fig_share.update_layout(
            title="Z → X: Tier-1 share rises with terrain difficulty",
            xaxis_title="Z — Terrain Difficulty",
            yaxis_title="Tier-1 Share", height=340,
            legend=dict(orientation="h", y=-0.3),
        )
        st.plotly_chart(fig_share, use_container_width=True)

    with col_right:
        # Y_TCO by Z bin and tier — this is the key addition
        df_s2["Z_bin_str"] = df_s2["Z_bin"].astype(str)
        tco_by_z = df_s2.groupby(["Z_bin", "tier"], observed=True)["Y_TCO"].mean().reset_index()
        tco_by_z["Z_mid"] = tco_by_z["Z_bin"].apply(lambda b: b.mid)
        fig_tco = go.Figure()
        for tier, color in [("Tier-1", _T1), ("Tier-2", _T2)]:
            sub = tco_by_z[tco_by_z["tier"] == tier]
            fig_tco.add_trace(go.Scatter(
                x=sub["Z_mid"].astype(float), y=sub["Y_TCO"],
                mode="lines+markers", name=tier,
                line=dict(color=color, width=2.5),
            ))
        fig_tco.add_vline(x=Z_STAR, line_dash="dash", line_color=_TCO,
                          annotation_text=f"Z*≈{Z_STAR:.1f}", annotation_position="top left")
        fig_tco.update_layout(
            title="Y (Total TCO) by terrain Z and tier — the outcome Z also drives",
            xaxis_title="Z — Terrain Difficulty",
            yaxis_title="Avg Total TCO (€)", height=340,
            legend=dict(orientation="h", y=-0.3),
        )
        st.plotly_chart(fig_tco, use_container_width=True)

    st.info(
        "**Why show Y here?** Z drives X (left chart) *and* Z drives Y (right chart). "
        "That's the definition of a confounder. Without seeing both, "
        "the backdoor path Z → X → Y is invisible."
    )

# ===========================================================================
# Tab 4 — Full DAG (with Y_TCO scatter)
# ===========================================================================
with tabs[4]:
    st.header("4 · Full DAG — Z drives X and Y")

    dag_col, scatter_col = st.columns([1, 2])

    with dag_col:
        st.markdown("**Structural DAG**")
        nodes = {"Z\n(terrain)": (1.0, 1.8), "X\n(tier)": (0.0, 1.0), "Y\n(TCO)": (2.0, 1.0)}
        _PINK = "#cc79a7"
        _BLUE = "#0072b2"
        edges = [
            ("Z\n(terrain)", "X\n(tier)",  _PINK, 2.5, "Z→X (backdoor)"),
            ("Z\n(terrain)", "Y\n(TCO)",   _PINK, 2.5, "Z→Y (direct)"),
            ("X\n(tier)",    "Y\n(TCO)",   _BLUE, 2.5, "X→Y (causal)"),
        ]
        fig_dag = go.Figure()
        for src, dst, color, width, _ in edges:
            x0, y0 = nodes[src]; x1, y1 = nodes[dst]
            fig_dag.add_annotation(
                x=x1, y=y1, ax=x0, ay=y0,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.5,
                arrowwidth=width, arrowcolor=color,
            )
        nc = {"Z\n(terrain)": _PINK, "X\n(tier)": _BLUE, "Y\n(TCO)": _TCO}
        for name, (x, y) in nodes.items():
            fig_dag.add_trace(go.Scatter(
                x=[x], y=[y], mode="markers+text",
                text=[name], textposition="top center",
                marker=dict(size=32, color=nc[name], line=dict(color="white", width=2)),
                textfont=dict(size=12, color="#000000"), showlegend=False,
            ))
        for color, label in [(_PINK, "Confounder path (backdoor)"), (_BLUE, "Causal path")]:
            fig_dag.add_trace(go.Scatter(x=[None], y=[None], mode="lines",
                                         line=dict(color=color, width=3), name=label))
        fig_dag.update_layout(
            title="Full DAG: Z→X, Z→Y, X→Y",
            xaxis=dict(visible=False, range=[-0.5, 2.5]),
            yaxis=dict(visible=False, range=[0.6, 2.2]),
            height=360, margin=dict(t=50, b=10),
            legend=dict(orientation="h", y=-0.05),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_dag, use_container_width=True)
        st.caption(
            "Pink = confounder paths (Z→X and Z→Y). "
            "Blue = causal path (X→Y). "
            "Naive comparison conflates all three."
        )

    with scatter_col:
        st.markdown("**Z vs Y (Total TCO) coloured by tier**")
        fig_sc = px.scatter(
            df, x="Z", y="Y_TCO", color="tier",
            color_discrete_map={"Tier-1": _T1, "Tier-2": _T2},
            opacity=0.5, labels={"Z": "Z — Terrain Difficulty", "Y_TCO": "Total TCO (€)"},
            title="Z → Y: terrain difficulty drives TCO regardless of tier",
        )
        fig_sc.add_vline(x=Z_STAR, line_dash="dash", line_color=_TCO,
                         annotation_text=f"Z*≈{Z_STAR:.1f}", annotation_position="top left")
        fig_sc.update_layout(height=360, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_sc, use_container_width=True)
        st.caption(
            "Both tiers show rising TCO with Z — that's Z→Y. "
            "Tier-1 sites cluster at high Z — that's Z→X. "
            "Naive comparison picks up both effects at once."
        )

# ===========================================================================
# Tab 5 — TCO Crossover
# ===========================================================================
with tabs[5]:
    st.header("5 · TCO Crossover Point Z*")
    st.markdown(
        f"Below Z*≈**{Z_STAR:.1f}** Tier-2 is cheaper overall. "
        f"Above Z*≈**{Z_STAR:.1f}** Tier-1 saves money despite higher contract cost."
    )

    z_range = np.linspace(1.0, 10.0, 300)
    tco_t1 = [60_000 + 8_333*(z-1) + max(5+3*z-5,7-5)*0
              + (lambda m: 0 if m<=14 else (m-14)*2000 if m<=21 else 14000+(m-21)*5000)(max(5+3*z-5,7))
              + 3_000 + 800*(z-1) for z in z_range]
    tco_t2 = [45_000 + 7_222*(z-1)
              + (lambda m: 0 if m<=14 else (m-14)*2000 if m<=21 else 14000+(m-21)*5000)(max(5+3*z,7))
              + 8_000 + 1_500*(z-1) for z in z_range]

    fig_cross = go.Figure()
    fig_cross.add_trace(go.Scatter(x=z_range, y=tco_t1, mode="lines",
                                   name="E[TCO | Tier-1]", line=dict(color=_T1, width=2.5)))
    fig_cross.add_trace(go.Scatter(x=z_range, y=tco_t2, mode="lines",
                                   name="E[TCO | Tier-2]", line=dict(color=_T2, width=2.5)))
    fig_cross.add_vline(x=Z_STAR, line_dash="dash", line_color=_TCO,
                        annotation_text=f"Z*≈{Z_STAR:.1f} — crossover",
                        annotation_position="top left")
    fig_cross.update_layout(
        title="Expected Total TCO by terrain difficulty — crossover at Z*",
        xaxis_title="Z — Terrain Difficulty",
        yaxis_title="Expected Total TCO (€)",
        height=400, legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_cross, use_container_width=True)

    saving = analytical_cate(9.0)
    st.success(
        f"At Z=9 (extreme terrain), Tier-1 saves ≈ **€{abs(saving):,.0f}** per site vs Tier-2. "
        f"Eliminating Tier-1 would cost the operator money on difficult sites."
    )

# ===========================================================================
# Tab 6 — Naive vs Causal
# ===========================================================================
with tabs[6]:
    st.header("6 · Naive OLS vs Causal Estimate")
    st.markdown(
        "OLS ignores Z and returns a flat (wrong) estimate. "
        "A Z-adjusted estimate recovers the true CATE curve."
    )

    try:
        from sklearn.linear_model import LinearRegression
        from econml.dml import CausalForestDML
        from sklearn.ensemble import GradientBoostingRegressor

        X_feat = df[["Z"]].values
        T = df["X"].values
        Y = df["Y_TCO"].values

        ols = LinearRegression().fit(
            np.column_stack([T, X_feat]), Y
        )
        ols_effect = ols.coef_[0]

        cf = CausalForestDML(
            model_y=GradientBoostingRegressor(n_estimators=100, random_state=42),
            model_t=GradientBoostingRegressor(n_estimators=100, random_state=42),
            n_estimators=200, random_state=42,
        )
        cf.fit(Y, T, X=X_feat)
        z_test = np.linspace(1, 10, 100).reshape(-1, 1)
        cate_pred = cf.effect(z_test)

        fig_cate = go.Figure()
        fig_cate.add_trace(go.Scatter(
            x=z_test.flatten(), y=cate_pred,
            mode="lines", name="CausalForestDML CATE",
            line=dict(color=_TCO, width=2.5),
        ))
        fig_cate.add_hline(y=ols_effect, line_dash="dash", line_color=_T2,
                           annotation_text=f"OLS flat: €{ols_effect:,.0f}",
                           annotation_position="bottom right")
        fig_cate.add_hline(y=0, line_dash="dot", line_color=_GREY)
        fig_cate.add_vline(x=Z_STAR, line_dash="dash", line_color=_TCO,
                           annotation_text=f"Z*≈{Z_STAR:.1f}", annotation_position="top left")
        fig_cate.update_layout(
            title="CATE(Z): CausalForestDML vs flat OLS",
            xaxis_title="Z — Terrain Difficulty",
            yaxis_title="Estimated effect of Tier-1 on TCO (€)",
            height=400, legend=dict(orientation="h", y=-0.2),
        )
        st.plotly_chart(fig_cate, use_container_width=True)
        st.caption("Negative = Tier-1 saves money. OLS misses the heterogeneity entirely.")

    except ImportError:
        st.warning("Install `econml` and `scikit-learn` to enable this tab: `pip install econml scikit-learn`")
        z_line = np.linspace(1, 10, 200)
        cate_true = [analytical_cate(z) for z in z_line]
        fig_true = go.Figure()
        fig_true.add_trace(go.Scatter(x=z_line, y=cate_true, mode="lines",
                                      name="True CATE (analytical)",
                                      line=dict(color=_TCO, width=2.5)))
        fig_true.add_hline(y=0, line_dash="dot", line_color=_GREY)
        fig_true.add_vline(x=Z_STAR, line_dash="dash", line_color=_TCO,
                           annotation_text=f"Z*≈{Z_STAR:.1f}", annotation_position="top left")
        fig_true.update_layout(
            title="True analytical CATE(Z) — install econml for ML estimate",
            xaxis_title="Z", yaxis_title="CATE (€)", height=380,
        )
        st.plotly_chart(fig_true, use_container_width=True)

# ===========================================================================
# Tab 7 — Period 1 TOP 3
# ===========================================================================
with tabs[7]:
    st.header("7 · Period 1 — TOP 3 Takeaways")
    for title, body in [
        ("1 · Correlation is not causation",
         "The BI dashboard showed Tier-1 costs more. "
         "That's true on average — but only because dispatchers sent Tier-1 to the hardest sites. "
         "The data was generated by a process, not by randomness."),
        (f"2 · The crossover point Z*≈{Z_STAR:.1f} is the decision boundary",
         "Below Z* use Tier-2. Above Z* use Tier-1. "
         "A flat policy (always Tier-2) leaves money on the table on difficult sites."),
        ("3 · Causal inference recovers what BI cannot",
         "EconML's CausalForestDML estimates the heterogeneous treatment effect CATE(Z). "
         "OLS returns a single flat number that is wrong for every individual site."),
    ]:
        with st.expander(title, expanded=True):
            st.write(body)

    st.markdown("---")
    st.info("❓ **Executive question:** If you had to set a single policy today — "
            "Tier-1 always, Tier-2 always, or Z-conditional — which would you choose and why?")

# ===========================================================================
# Tab 8 — Lessons
# ===========================================================================
with tabs[8]:
    st.header("8 · Lessons & Session 2 Preview")
    lessons = [
        ("Ask how the data was generated",
         "Before any number, ask: who made what decision, based on what? "
         "The dispatcher's sigmoid rule is invisible in the BI output."),
        ("Name the confounder",
         "Z (terrain difficulty) is a common cause of X (tier assignment) and Y (TCO). "
         "That's the textbook definition of a confounder."),
        ("Draw the DAG before fitting a model",
         "The DAG makes the backdoor path explicit: Z→X→Y and Z→Y. "
         "Without the DAG you don't know what to adjust for."),
        ("Adjustment recovers the causal effect",
         "Conditioning on Z removes the backdoor path. "
         "Standardization, IPW, and CausalForestDML all do this — in different ways."),
        ("Heterogeneous effects matter",
         f"The effect of Tier-1 is not constant. It crosses zero at Z*≈{Z_STAR:.1f}. "
         "A single ATE hides this and leads to the wrong policy."),
        ("Session 2 preview — dynamic decisions",
         "Period 1 used a static, one-shot assignment. "
         "Session 2 introduces sequential decisions, time-varying confounding, "
         "and marginal structural models."),
    ]
    for title, body in lessons:
        with st.expander(title):
            st.write(body)
