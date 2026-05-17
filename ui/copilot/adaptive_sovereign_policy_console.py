"""
ui/copilot/adaptive_sovereign_policy_console.py

Adaptive Sovereign Policy Console.

Purpose:
- sovereign policy cognition command center
- adaptive governance intelligence visibility
- sovereign posture management
- policy pressure visualization
- governance drift analysis
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def _fmt_ts(ms: Any) -> str:
    if not ms:
        return "-"
    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ms) / 1000),
        )
    except Exception:
        return str(ms)


def _icon(value: str) -> str:
    value = str(value or "").upper()

    if value in {
        "LOW",
        "RELAXED",
        "BALANCED",
        "COMPLETED",
        "HEALTHY",
        "AUTHORIZED",
    }:
        return "🟢"

    if value in {
        "MEDIUM",
        "IMPROVABLE",
        "PENDING",
        "RUNNING",
        "PRESSURE",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "HARDENED",
        "BLOCKED",
        "FAILED",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "LOCKDOWN",
        "QUARANTINED",
        "FROZEN",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_adaptive_sovereign_policy_console(
    storage: Any,
) -> None:
    st.markdown("# 🛡️ Adaptive Sovereign Policy")
    st.caption(
        "Adaptive sovereign governance cognition, policy posture intelligence, and runtime policy pressure analysis."
    )

    engine = getattr(
        storage,
        "adaptive_sovereign_policy_engine",
        None,
    )

    governor = getattr(
        storage,
        "autonomy_governor_v2",
        None,
    )

    relay = getattr(
        storage,
        "cross_runtime_execution_relay",
        None,
    )

    mesh_optimizer = getattr(
        storage,
        "sovereign_mesh_optimizer",
        None,
    )

    if engine is None:
        st.error(
            "Adaptive Sovereign Policy Engine is unavailable."
        )
        return

    # ========================================================
    # STATUS
    # ========================================================

    st.markdown("## 🌐 Sovereign Policy Status")

    try:
        status = engine.policy_engine_status()
    except Exception as exc:
        status = {"error": str(exc)}

    latest = status.get("latest_assessment") or {}

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Policy Posture",
        f"{_icon(status.get('tenant_posture'))} {status.get('tenant_posture')}",
    )

    c2.metric(
        "Risk Level",
        f"{_icon(latest.get('risk_level'))} {latest.get('risk_level', 'UNKNOWN')}",
    )

    c3.metric(
        "Risk Score",
        latest.get("risk_score", 0),
    )

    c4.metric(
        "Pressure",
        latest.get("policy_pressure_score", 0),
    )

    c5.metric(
        "Signals",
        status.get("signal_count", 0),
    )

    c6.metric(
        "Recommendations",
        status.get("recommendation_count", 0),
    )

    st.markdown("---")

    # ========================================================
    # POLICY POSTURE CONTROL
    # ========================================================

    st.markdown("## ⚙️ Sovereign Policy Posture")

    p1, p2, p3 = st.columns(3)

    with p1:
        posture = st.selectbox(
            "Policy Posture",
            [
                "RELAXED",
                "BALANCED",
                "HARDENED",
                "LOCKDOWN",
            ],
            index=1,
            key="adaptive_policy_posture",
        )

    with p2:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="adaptive_policy_tenant",
        )

    with p3:
        reason = st.text_input(
            "Reason",
            value="manual_policy_adjustment",
            key="adaptive_policy_reason",
        )

    if st.button(
        "Apply Policy Posture",
        use_container_width=True,
        key="apply_policy_posture_btn",
    ):
        try:
            result = engine.set_policy_posture(
                tenant_id=tenant_id,
                posture=posture,
                reason=reason,
            )

            st.success("Policy posture updated.")
            st.json(result)

        except Exception as exc:
            st.error(f"Policy posture update failed: {exc}")

    st.markdown("---")

    # ========================================================
    # POLICY ASSESSMENT
    # ========================================================

    st.markdown("## 🧠 Sovereign Policy Assessment")

    a1, a2 = st.columns(2)

    with a1:
        assess_tenant = st.text_input(
            "Assessment Tenant",
            value="default",
            key="policy_assess_tenant",
        )

    with a2:
        workload_action = st.text_input(
            "Workload Action",
            value="ASSESS_RUNTIME_POLICY",
            key="policy_assess_action",
        )

    sensitivity = st.multiselect(
        "Sensitivity Categories",
        [
            "CUI",
            "ITAR",
            "EXPORT_CONTROLLED",
            "CLASSIFIED",
            "FINANCIAL",
            "PII",
        ],
        default=["CUI"],
        key="policy_assess_categories",
    )

    workload = {
        "action": workload_action,
        "categories": sensitivity,
        "source": "adaptive_sovereign_policy_console",
    }

    dry_run = st.checkbox(
        "Dry Run",
        value=True,
        key="policy_assess_dry_run",
    )

    assess_tabs = st.tabs(
        [
            "Assessment",
            "Enforcement Simulation",
        ]
    )

    with assess_tabs[0]:
        if st.button(
            "Run Policy Assessment",
            use_container_width=True,
            key="run_policy_assessment_btn",
        ):
            try:
                assessment = engine.assess(
                    tenant_id=assess_tenant,
                    workload=workload,
                )

                st.json(
                    assessment.to_dict()
                    if hasattr(assessment, "to_dict")
                    else assessment
                )

            except Exception as exc:
                st.error(f"Policy assessment failed: {exc}")

    with assess_tabs[1]:
        if st.button(
            "Execute Policy Simulation",
            use_container_width=True,
            key="execute_policy_simulation_btn",
        ):
            try:
                result = engine.enforce(
                    tenant_id=assess_tenant,
                    workload=workload,
                    dry_run=dry_run,
                )

                st.json(result)

            except Exception as exc:
                st.error(f"Policy enforcement simulation failed: {exc}")

    st.markdown("---")

    # ========================================================
    # LATEST ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Sovereign Assessment")

    if latest:
        latest_tabs = st.tabs(
            [
                "Assessment",
                "Signals",
                "Recommendations",
                "Telemetry",
            ]
        )

        with latest_tabs[0]:
            st.json(latest)

        with latest_tabs[1]:
            signals = latest.get("signals", [])

            rows = []

            for signal in signals:
                rows.append(
                    {
                        "Type": signal.get("signal_type"),
                        "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                        "Source": signal.get("source"),
                        "Message": signal.get("message"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No policy signals available.")

        with latest_tabs[2]:
            recs = latest.get("recommendations", [])

            rows = []

            for rec in recs:
                rows.append(
                    {
                        "Action": rec.get("action"),
                        "Priority": f"{_icon(rec.get('priority'))} {rec.get('priority')}",
                        "Approval": rec.get("requires_approval"),
                        "Reason": rec.get("reason"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No policy recommendations available.")

        with latest_tabs[3]:
            st.json(
                latest.get("telemetry", {})
            )

    else:
        st.info("No assessments available.")

    st.markdown("---")

    # ========================================================
    # SIGNAL STREAM
    # ========================================================

    st.markdown("## 📡 Sovereign Policy Signal Stream")

    try:
        signals = engine.list_signals(limit=250)

        rows = []

        for signal in signals:
            rows.append(
                {
                    "Time": _fmt_ts(signal.get("created_at_ms")),
                    "Signal": signal.get("signal_type"),
                    "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                    "Tenant": signal.get("tenant_id"),
                    "Source": signal.get("source"),
                    "Message": signal.get("message"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=420,
            )
        else:
            st.info("No sovereign policy signals available.")

    except Exception as exc:
        st.error(f"Signal stream failed: {exc}")

    st.markdown("---")

    # ========================================================
    # POLICY RECOMMENDATIONS
    # ========================================================

    st.markdown("## 🧾 Policy Recommendations")

    try:
        recommendations = engine.list_recommendations(
            limit=250,
        )

        rows = []

        for rec in recommendations:
            rows.append(
                {
                    "Time": _fmt_ts(rec.get("created_at_ms")),
                    "Action": rec.get("action"),
                    "Priority": f"{_icon(rec.get('priority'))} {rec.get('priority')}",
                    "Tenant": rec.get("tenant_id"),
                    "Approval": rec.get("requires_approval"),
                    "Reason": rec.get("reason"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=420,
            )
        else:
            st.info("No policy recommendations available.")

    except Exception as exc:
        st.error(f"Policy recommendations failed: {exc}")

    st.markdown("---")

    # ========================================================
    # GOVERNANCE PRESSURE
    # ========================================================

    st.markdown("## 🌐 Governance Pressure Intelligence")

    pressure_tabs = st.tabs(
        [
            "Governor",
            "Relay",
            "Mesh Optimizer",
            "Engine Status",
        ]
    )

    with pressure_tabs[0]:
        try:
            if governor is not None:
                st.json(
                    governor.governor_status()
                )
            else:
                st.info("Governor unavailable.")
        except Exception as exc:
            st.error(f"Governor pressure failed: {exc}")

    with pressure_tabs[1]:
        try:
            if relay is not None:
                st.json(
                    relay.relay_status()
                )
            else:
                st.info("Execution relay unavailable.")
        except Exception as exc:
            st.error(f"Relay pressure failed: {exc}")

    with pressure_tabs[2]:
        try:
            if mesh_optimizer is not None:
                st.json(
                    mesh_optimizer.optimizer_status()
                )
            else:
                st.info("Mesh optimizer unavailable.")
        except Exception as exc:
            st.error(f"Mesh optimizer pressure failed: {exc}")

    with pressure_tabs[3]:
        st.json(status)

    st.markdown("---")

    # ========================================================
    # GOVERNANCE DRIFT
    # ========================================================

    st.markdown("## 🧭 Governance Drift Analysis")

    try:
        assessments = engine.list_assessments(
            limit=100,
        )

        rows = []

        for item in assessments:
            rows.append(
                {
                    "Time": _fmt_ts(item.get("created_at_ms")),
                    "Posture": f"{_icon(item.get('posture'))} {item.get('posture')}",
                    "Recommended": f"{_icon(item.get('recommended_posture'))} {item.get('recommended_posture')}",
                    "Risk": f"{_icon(item.get('risk_level'))} {item.get('risk_level')}",
                    "Risk Score": item.get("risk_score"),
                    "Pressure": item.get("policy_pressure_score"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=360,
            )
        else:
            st.info("No governance drift history available.")

    except Exception as exc:
        st.error(f"Governance drift analysis failed: {exc}")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="adaptive_policy_console_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()