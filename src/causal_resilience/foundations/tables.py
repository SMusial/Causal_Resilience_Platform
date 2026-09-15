"""
causal_resilience.foundations.tables
======================================
V0 Slice 3/4 — Potential-outcome table rendering helpers.

Pure functions with no Streamlit dependency — fully testable.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

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


def build_po_table_rows(sample: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Convert a sample DataFrame into row dicts with observed/counterfactual flags.

    Each dict has keys: episode, severity, treatment,
    y0_value, y0_observed, y1_value, y1_observed, outcome.
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


def render_po_table(sample: pd.DataFrame) -> str:
    """Render the potential-outcome table as an accessible HTML string."""
    rows = build_po_table_rows(sample)
    headers = [
        "Episode", "Severity", "Assigned treatment",
        "Y(0) oracle", "Y(1) oracle", "Observed outcome",
    ]
    th_cells = "".join(f"<th style='{_STYLE_TH}'>{h}</th>" for h in headers)

    def _cell(value: str, observed: bool) -> str:
        if observed:
            return (
                f"<td style='{_STYLE_OBSERVED}'>"
                f"&#9733; {value}<br><small>observed</small></td>"
            )
        return (
            f"<td style='{_STYLE_COUNTERFACTUAL}'>"
            f"{value}<br><small>[missing]</small></td>"
        )

    html_rows = []
    for row in rows:
        html_rows.append(
            "<tr>"
            f"<td style='{_STYLE_PLAIN}'>{row['episode']}</td>"
            f"<td style='{_STYLE_PLAIN}'>{row['severity']}</td>"
            f"<td style='{_STYLE_PLAIN}'>{row['treatment']}</td>"
            + _cell(row["y0_value"], row["y0_observed"])
            + _cell(row["y1_value"], row["y1_observed"])
            + f"<td style='{_STYLE_OBSERVED}'>{row['outcome']}<br><small>observed</small></td>"
            "</tr>"
        )

    return (
        "<table style='border-collapse:collapse; width:100%; font-size:0.9rem;'>"
        f"<thead><tr>{th_cells}</tr></thead>"
        f"<tbody>{''.join(html_rows)}</tbody>"
        "</table>"
    )
