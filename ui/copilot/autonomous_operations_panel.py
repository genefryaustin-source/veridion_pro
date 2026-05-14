from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Any, Dict, List

from core.ai.orchestration.adaptive_policy_optimizer import (
    AdaptivePolicyOptimizer,
)


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    try:
        return pd.DataFrame(rows or [])
    except Exception:
        return pd.DataFrame()


def _metric(label: str, value: Any, delta: Any = None):
    try:
        st.metric(label, value, delta=delta)
    except Exception:
        st.write(f"**{label}:** {value}")


def _risk_color(level: str) -> str:
    level = str(level or "").upper()

    if level in {"CRITICAL", "HIGH"}:
        return "#ff4b4b"

    if level in {"MEDIUM", "WARNING"}:
        return "#ffb347"

    return "#22c55e"


def _render_banner(title: str, subtitle: str):
    st.markdown(
        f"""
        <div style="
            padding:16px;
            border-radius:12px;
            background:#0f172a;
            border:1px solid #1e293b;
            margin-bottom:16px;
        ">
            <h2 style="margin:0;color:white;">{title}</h2>
            <div style="margin-top:6px;color:#94a3b8;">
                {subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_autonomous_operations_panel(storage=None):
    st.markdown("## 🤖 Autonomous Operations")

    if storage is None:
        st.warning("Storage unavailable.")
        return

    governance = getattr(storage, "governance", None)

    if governance is None:
        st.warning("Governance repository unavailable.")
        return

    tenant_id = st.session_state.get("active_tenant_id", "default_tenant")

    optimizer = AdaptivePolicyOptimizer(
        ledger=storage.ledger,
        governance=governance,
    )

    try:
        optimization = optimizer.optimize_tenant_policy(
            tenant_id=tenant_id,
            lookback_limit=1000,
        )
    except Exception as e:
        st.error(f"Optimizer error: {e}")
        return

    readiness = optimization.get("autonomy_readiness", {})
    drift = optimization.get("governance_drift", {})
    reliability = optimization.get("execution_reliability", {})
    approval_latency = optimization.get("approval_latency", {})
    rollback_patterns = optimization.get("rollback_patterns", {})
    recommendations = optimization.get("recommended_policy_changes", [])

    mode = optimization.get("recommended_autonomy_mode", "MANUAL")
    readiness_score = readiness.get("readiness_score", 0)
    drift_level = drift.get("level", "LOW")
    friction_score = optimization.get("operational_friction_score", 0)

    _render_banner(
        "Autonomous Operations Control Plane",
        (
            f"Tenant: {tenant_id} | "
            f"Recommended Mode: {mode} | "
            f"Readiness Score: {readiness_score}"
        ),
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _metric(
            "Autonomy Readiness",
            readiness_score,
        )

    with c2:
        _metric(
            "Governance Drift",
            drift_level,
        )

    with c3:
        _metric(
            "Operational Friction",
            friction_score,
        )

    with c4:
        _metric(
            "Pending Approvals",
            approval_latency.get("pending_count", 0),
        )

    st.markdown("---")

    left, right = st.columns([1.4, 1])

    # ==========================================================
    # LEFT SIDE
    # ==========================================================

    with left:
        st.markdown("### 🚀 Live Execution State")

        try:
            recent_decisions = governance.get_recent_decisions(
                tenant_id=tenant_id,
                limit=25,
            )
        except Exception:
            recent_decisions = []

        df = _safe_df(recent_decisions)

        if not df.empty:
            show_cols = [
                c for c in [
                    "created_at_ms",
                    "final_action",
                    "severity",
                    "status",
                    "confidence",
                    "requires_approval",
                    "rollback_available",
                ]
                if c in df.columns
            ]

            st.dataframe(
                df[show_cols],
                use_container_width=True,
                height=320,
            )
        else:
            st.info("No recent execution decisions.")

        st.markdown("### 🛡️ Approval Bottlenecks")

        bottlenecks = approval_latency.get("bottlenecks", [])

        if bottlenecks:
            for item in bottlenecks:
                st.warning(
                    f"""
                    **{item.get('type')}**

                    {item.get('recommendation')}
                    """
                )
        else:
            st.success("No major approval bottlenecks detected.")

        st.markdown("### 🔄 Rollback Activity")

        rollback_alerts = rollback_patterns.get("alerts", [])

        if rollback_alerts:
            for alert in rollback_alerts:
                st.error(
                    f"""
                    **{alert.get('type')}**

                    Action: `{alert.get('action')}`

                    Failure Rate: `{alert.get('failure_rate')}`

                    {alert.get('recommendation')}
                    """
                )
        else:
            st.success("Rollback activity stable.")

    # ==========================================================
    # RIGHT SIDE
    # ==========================================================

    with right:
        st.markdown("### 🧠 Autonomy Readiness")

        posture = readiness.get("readiness_posture", "UNKNOWN")

        st.markdown(
            f"""
            <div style="
                padding:14px;
                border-radius:12px;
                border:1px solid #334155;
                background:#111827;
            ">
                <div style="font-size:20px;font-weight:700;color:white;">
                    {mode}
                </div>

                <div style="
                    margin-top:10px;
                    color:{_risk_color(drift_level)};
                    font-weight:600;
                ">
                    Governance Drift: {drift_level}
                </div>

                <div style="margin-top:10px;color:#cbd5e1;">
                    {posture}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 📉 Governance Drift")

        findings = drift.get("findings", [])

        if findings:
            for finding in findings:
                st.warning(
                    f"""
                    **{finding.get('type')}**

                    {finding.get('recommendation')}
                    """
                )
        else:
            st.success("Governance drift low.")

        st.markdown("### ⚡ Execution Reliability")

        rel_df = _safe_df([
            {
                "Action": action,
                "Success Rate": stats.get("success_rate"),
                "Failure Rate": stats.get("failure_rate"),
                "Rollback Rate": stats.get("rollback_rate"),
            }
            for action, stats in reliability.get("by_action", {}).items()
        ])

        if not rel_df.empty:
            st.dataframe(
                rel_df,
                use_container_width=True,
                height=220,
            )
        else:
            st.info("No execution reliability telemetry.")

    st.markdown("---")

    st.markdown("## 🧭 Adaptive Policy Recommendations")

    if recommendations:
        for rec in recommendations[:20]:
            rec_type = rec.get("type", "UNKNOWN")
            recommendation = rec.get("recommendation", "")

            st.markdown(
                f"""
                <div style="
                    padding:14px;
                    border-radius:10px;
                    background:#111827;
                    border:1px solid #1e293b;
                    margin-bottom:12px;
                ">
                    <div style="
                        font-weight:700;
                        color:#60a5fa;
                        margin-bottom:8px;
                    ">
                        {rec_type}
                    </div>

                    <div style="color:#e2e8f0;">
                        {recommendation}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No adaptive policy recommendations.")