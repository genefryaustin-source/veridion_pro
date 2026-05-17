"""
ui/copilot/sovereign_autonomy_governance_dashboard.py

Sovereign Autonomy Governance Dashboard

Upper-tier sovereign governance command surface.

This dashboard visualizes:

- global governance posture
- execution governance posture
- execution verification posture
- adaptive learning posture
- policy evolution posture
- survivability posture
- continuity posture
- resilience posture
- sovereignty posture

This becomes:

sovereign autonomy governance operational command UI
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


# ==========================================================
# HELPERS
# ==========================================================

def _safe_score(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        value = float(value)

    except Exception:
        value = default

    return max(
        0.0,
        min(100.0, value),
    )


def _status_color(score: float) -> str:

    if score >= 90:
        return "#00d084"

    if score >= 75:
        return "#ffb020"

    if score >= 50:
        return "#ff6b35"

    return "#ff3b30"


def _metric_card(
    title: str,
    value: float,
    subtitle: str,
) -> None:

    color = _status_color(value)

    st.markdown(
        f"""
        <div style="
            background:#111827;
            border:1px solid #1f2937;
            border-radius:14px;
            padding:18px;
            margin-bottom:10px;
        ">
            <div style="
                color:#9ca3af;
                font-size:0.85rem;
                margin-bottom:8px;
            ">
                {title}
            </div>

            <div style="
                color:{color};
                font-size:2rem;
                font-weight:700;
                margin-bottom:6px;
            ">
                {value:.1f}
            </div>

            <div style="
                color:#d1d5db;
                font-size:0.85rem;
            ">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _timeline_event(
    title: str,
    severity: str,
    summary: str,
    ts: str,
) -> None:

    severity_colors = {
        "INFO": "#3b82f6",
        "LOW": "#10b981",
        "MEDIUM": "#f59e0b",
        "HIGH": "#ef4444",
        "CRITICAL": "#dc2626",
    }

    color = severity_colors.get(
        severity.upper(),
        "#3b82f6",
    )

    st.markdown(
        f"""
        <div style="
            border-left:4px solid {color};
            background:#111827;
            padding:14px;
            border-radius:10px;
            margin-bottom:10px;
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">
                <div style="
                    font-weight:700;
                    color:white;
                ">
                    {title}
                </div>

                <div style="
                    color:{color};
                    font-size:0.8rem;
                    font-weight:700;
                ">
                    {severity}
                </div>
            </div>

            <div style="
                color:#d1d5db;
                margin-top:8px;
                font-size:0.9rem;
            ">
                {summary}
            </div>

            <div style="
                color:#6b7280;
                margin-top:8px;
                font-size:0.75rem;
            ">
                {ts}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# DEMO TELEMETRY
# ==========================================================

def _demo_runtime_metrics() -> Dict[str, float]:

    return {

        "governance_posture": random.uniform(
            78,
            99,
        ),

        "verification_posture": random.uniform(
            75,
            98,
        ),

        "adaptive_learning_posture": random.uniform(
            70,
            97,
        ),

        "policy_evolution_posture": random.uniform(
            72,
            96,
        ),

        "survivability_posture": random.uniform(
            65,
            99,
        ),

        "continuity_posture": random.uniform(
            68,
            98,
        ),

        "resilience_posture": random.uniform(
            74,
            98,
        ),

        "sovereignty_posture": random.uniform(
            70,
            99,
        ),

        "governance_drift": random.uniform(
            2,
            35,
        ),

        "sovereignty_pressure": random.uniform(
            3,
            45,
        ),

        "resilience_pressure": random.uniform(
            5,
            40,
        ),
    }


def _demo_policy_table() -> pd.DataFrame:

    rows = [

        {
            "proposal": (
                "Increase Resilience Governance"
            ),
            "priority": "CRITICAL",
            "approval_required": True,
            "stability_gain": 92.4,
        },

        {
            "proposal": (
                "Adapt Orchestration Policy"
            ),
            "priority": "HIGH",
            "approval_required": True,
            "stability_gain": 84.2,
        },

        {
            "proposal": (
                "Reduce Sovereignty Pressure"
            ),
            "priority": "HIGH",
            "approval_required": True,
            "stability_gain": 79.8,
        },

        {
            "proposal": (
                "Continuity Threshold Recalibration"
            ),
            "priority": "MEDIUM",
            "approval_required": False,
            "stability_gain": 71.5,
        },
    ]

    return pd.DataFrame(rows)


def _demo_verification_table() -> pd.DataFrame:

    rows = []

    for idx in range(12):

        rows.append(
            {
                "verification_id": (
                    f"VERIFY-{1000 + idx}"
                ),
                "state": random.choice(
                    [
                        "VERIFIED",
                        "MONITORING",
                        "PARTIAL_SUCCESS",
                        "STABILIZING",
                    ]
                ),
                "governance_score": round(
                    random.uniform(70, 99),
                    2,
                ),
                "survivability_score": round(
                    random.uniform(65, 99),
                    2,
                ),
                "recovery_score": round(
                    random.uniform(68, 99),
                    2,
                ),
            }
        )

    return pd.DataFrame(rows)


def _demo_timeline() -> List[Dict[str, str]]:

    return [

        {
            "title": (
                "Governance Policy Evolution"
            ),
            "severity": "HIGH",
            "summary": (
                "Adaptive policy recalibration "
                "triggered from survivability "
                "pressure observations."
            ),
        },

        {
            "title": (
                "Execution Verification Completed"
            ),
            "severity": "INFO",
            "summary": (
                "Distributed orchestration "
                "verification completed successfully."
            ),
        },

        {
            "title": (
                "Resilience Stabilization"
            ),
            "severity": "MEDIUM",
            "summary": (
                "Runtime resilience posture "
                "improving after escalation recovery."
            ),
        },

        {
            "title": (
                "Sovereignty Boundary Hardening"
            ),
            "severity": "CRITICAL",
            "summary": (
                "Sovereignty pressure exceeded "
                "threshold tolerance window."
            ),
        },
    ]


# ==========================================================
# MAIN RENDER
# ==========================================================

def render_sovereign_autonomy_governance_dashboard(
    runtime_fabric: Optional[Any] = None,
) -> None:

    st.markdown(
        """
        # 🌐 Sovereign Autonomy Governance Dashboard
        """
    )

    st.caption(
        """
        Upper-tier sovereign governance command surface for:
        orchestration governance, survivability governance,
        adaptive learning governance, and policy evolution cognition.
        """
    )

    metrics = _demo_runtime_metrics()

    # ======================================================
    # TOP STATUS BAR
    # ======================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        _metric_card(
            "Governance Posture",
            metrics[
                "governance_posture"
            ],
            "Global governance stability",
        )

    with col2:

        _metric_card(
            "Verification Posture",
            metrics[
                "verification_posture"
            ],
            "Execution verification health",
        )

    with col3:

        _metric_card(
            "Adaptive Learning",
            metrics[
                "adaptive_learning_posture"
            ],
            "Operational learning cognition",
        )

    with col4:

        _metric_card(
            "Policy Evolution",
            metrics[
                "policy_evolution_posture"
            ],
            "Governance policy evolution",
        )

    st.divider()

    # ======================================================
    # GOVERNANCE STATUS
    # ======================================================

    st.subheader(
        "🛡️ Sovereign Governance Status"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        _metric_card(
            "Survivability",
            metrics[
                "survivability_posture"
            ],
            "Runtime survivability posture",
        )

    with col2:

        _metric_card(
            "Continuity",
            metrics[
                "continuity_posture"
            ],
            "Operational continuity posture",
        )

    with col3:

        _metric_card(
            "Resilience",
            metrics[
                "resilience_posture"
            ],
            "Resilience stabilization posture",
        )

    with col4:

        _metric_card(
            "Sovereignty",
            metrics[
                "sovereignty_posture"
            ],
            "Sovereignty assurance posture",
        )

    st.divider()

    # ======================================================
    # PRESSURE INDICATORS
    # ======================================================

    st.subheader(
        "⚠️ Pressure Indicators"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Governance Drift",
            f"{metrics['governance_drift']:.1f}",
        )

        st.progress(
            metrics[
                "governance_drift"
            ] / 100.0
        )

    with col2:

        st.metric(
            "Sovereignty Pressure",
            f"{metrics['sovereignty_pressure']:.1f}",
        )

        st.progress(
            metrics[
                "sovereignty_pressure"
            ] / 100.0
        )

    with col3:

        st.metric(
            "Resilience Pressure",
            f"{metrics['resilience_pressure']:.1f}",
        )

        st.progress(
            metrics[
                "resilience_pressure"
            ] / 100.0
        )

    st.divider()

    # ======================================================
    # EXECUTION VERIFICATION STREAM
    # ======================================================

    st.subheader(
        "✅ Execution Verification Stream"
    )

    verification_df = (
        _demo_verification_table()
    )

    st.dataframe(
        verification_df,
        use_container_width=True,
        height=320,
    )

    st.divider()

    # ======================================================
    # POLICY EVOLUTION
    # ======================================================

    st.subheader(
        "⚙️ Policy Evolution Recommendations"
    )

    policy_df = _demo_policy_table()

    st.dataframe(
        policy_df,
        use_container_width=True,
        height=240,
    )

    st.divider()

    # ======================================================
    # GOVERNANCE TIMELINE
    # ======================================================

    st.subheader(
        "🧬 Replayable Governance Timeline"
    )

    timeline = _demo_timeline()

    for item in timeline:

        _timeline_event(
            title=item["title"],
            severity=item["severity"],
            summary=item["summary"],
            ts=time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

    st.divider()

    # ======================================================
    # RUNTIME FABRIC STATUS
    # ======================================================

    st.subheader(
        "🌐 Sovereign Runtime Fabric"
    )

    if runtime_fabric is not None:

        metadata = getattr(
            runtime_fabric,
            "metadata",
            {},
        ) or {}

        st.json(metadata)

    else:

        st.info(
            """
            Runtime fabric not connected.
            Dashboard operating in sovereign demo mode.
            """
        )