"""
ui/copilot/autonomous_execution_cognition_console.py

Autonomous Execution Cognition Console.

Purpose:
- unified runtime cognition fusion command center
- operational cognition visibility
- cascading failure cognition visibility
- continuity and survivability intelligence
- fused sovereign operational telemetry
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
        "STABLE",
        "EXECUTED",
        "CONFIRMED",
        "VIABLE",
    }:
        return "🟢"

    if value in {
        "MEDIUM",
        "WATCH",
        "PENDING",
        "DEGRADED",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "UNSTABLE",
        "AT_RISK",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "FAILED",
        "BLOCKED",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_autonomous_execution_cognition_console(
    storage: Any,
) -> None:

    st.markdown("# 🧠 Autonomous Execution Cognition")
    st.caption(
        "Unified sovereign operational cognition, execution-chain intelligence, and fused runtime reasoning visibility."
    )

    engine = getattr(
        storage,
        "autonomous_execution_cognition_engine",
        None,
    )

    predictive_engine = getattr(
        storage,
        "predictive_runtime_stability_engine",
        None,
    )

    learning_engine = getattr(
        storage,
        "runtime_fabric_learning_engine",
        None,
    )

    sovereignty_engine = getattr(
        storage,
        "sovereignty_decision_engine",
        None,
    )

    if engine is None:
        st.error(
            "Autonomous Execution Cognition Engine unavailable."
        )
        return

    # ========================================================
    # STATUS
    # ========================================================

    st.markdown("## 🌐 Autonomous Cognition Status")

    try:
        status = engine.cognition_status()
    except Exception as exc:
        status = {"error": str(exc)}

    latest = status.get("latest_assessment") or {}

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Assessments",
        status.get("assessment_count", 0),
    )

    c2.metric(
        "Signals",
        status.get("signal_count", 0),
    )

    c3.metric(
        "Recommendations",
        status.get("recommendation_count", 0),
    )

    c4.metric(
        "Continuity",
        latest.get("continuity_score", 0),
    )

    c5.metric(
        "Cognition State",
        f"{_icon(latest.get('cognition_state'))} {latest.get('cognition_state', 'UNKNOWN')}",
    )

    st.markdown("---")

    # ========================================================
    # OPERATIONS
    # ========================================================

    st.markdown("## ⚙️ Autonomous Cognition Operations")

    o1, o2, o3 = st.columns(3)

    with o1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="exec_cognition_tenant",
        )

    with o2:
        dry_run = st.checkbox(
            "Dry Run Enforcement",
            value=True,
            key="exec_cognition_dry_run",
        )

    with o3:
        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=False,
            key="exec_cognition_auto_refresh",
        )

    workload_action = st.text_input(
        "Workload Action",
        value="RUNTIME_EXECUTION",
        key="exec_cognition_workload_action",
    )

    workload_categories = st.multiselect(
        "Sensitivity Categories",
        [
            "CUI",
            "ITAR",
            "EXPORT_CONTROLLED",
            "CLASSIFIED",
            "FEDRAMP_HIGH",
            "MISSION_CRITICAL",
        ],
        default=["CUI"],
        key="exec_cognition_categories",
    )

    op_tabs = st.tabs(
        [
            "Assess Cognition",
            "Enforce Cognition",
        ]
    )

    with op_tabs[0]:

        if st.button(
            "Run Autonomous Cognition Assessment",
            use_container_width=True,
            key="exec_cognition_assess_btn",
        ):
            try:

                assessment = engine.assess(
                    tenant_id=tenant_id,
                    workload={
                        "action": workload_action,
                        "categories": workload_categories,
                        "source": "autonomous_execution_cognition_console",
                    },
                )

                st.success(
                    "Autonomous execution cognition assessment completed."
                )

                st.json(
                    assessment.to_dict()
                    if hasattr(assessment, "to_dict")
                    else assessment
                )

            except Exception as exc:
                st.error(
                    f"Autonomous cognition assessment failed: {exc}"
                )

    with op_tabs[1]:

        if st.button(
            "Run Autonomous Cognition Enforcement",
            use_container_width=True,
            key="exec_cognition_enforce_btn",
        ):
            try:

                result = engine.enforce(
                    tenant_id=tenant_id,
                    workload={
                        "action": workload_action,
                        "categories": workload_categories,
                        "source": "autonomous_execution_cognition_console",
                    },
                    dry_run=dry_run,
                )

                st.success(
                    "Autonomous cognition enforcement completed."
                )

                st.json(result)

            except Exception as exc:
                st.error(
                    f"Autonomous cognition enforcement failed: {exc}"
                )

    st.markdown("---")

    # ========================================================
    # LATEST ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Autonomous Cognition Assessment")

    if latest:

        assess_tabs = st.tabs(
            [
                "Assessment",
                "Signal Fusion",
                "Recommendations",
                "Telemetry",
            ]
        )

        with assess_tabs[0]:

            top1, top2, top3, top4 = st.columns(4)

            top1.metric(
                "Risk",
                latest.get("risk_level", "UNKNOWN"),
            )

            top2.metric(
                "Cognition Score",
                latest.get("cognition_score", 0),
            )

            top3.metric(
                "Survivability",
                latest.get("survivability_score", 0),
            )

            top4.metric(
                "Confidence",
                latest.get("confidence", 0),
            )

            st.info(
                latest.get(
                    "summary",
                    "No cognition summary available.",
                )
            )

            st.json(latest)

        with assess_tabs[1]:

            rows = []

            for signal in latest.get("signals", []):

                rows.append(
                    {
                        "Signal": signal.get("signal_type"),
                        "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                        "Source": signal.get("source"),
                        "Confidence": signal.get("confidence"),
                        "Weight": signal.get("weight"),
                        "Target": signal.get("target"),
                        "Message": signal.get("message"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=450,
                )
            else:
                st.info(
                    "No cognition fusion signals available."
                )

        with assess_tabs[2]:

            rows = []

            for rec in latest.get("recommendations", []):

                rows.append(
                    {
                        "Action": rec.get("action"),
                        "Priority": f"{_icon(rec.get('priority'))} {rec.get('priority')}",
                        "Target": rec.get("target"),
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
                st.info(
                    "No cognition recommendations available."
                )

        with assess_tabs[3]:
            st.json(
                latest.get("telemetry", {})
            )

    else:
        st.info(
            "No autonomous cognition assessments available."
        )

    st.markdown("---")

    # ========================================================
    # CASCADING FAILURE COGNITION
    # ========================================================

    st.markdown("## 🔗 Cascading Failure Cognition")

    try:

        cascades = (
            latest.get("cascade_model", {})
            .get("cascades", [])
        )

        rows = []

        for item in cascades:

            rows.append(
                {
                    "Cascade": item.get("cascade"),
                    "Likelihood": f"{_icon(item.get('likelihood'))} {item.get('likelihood')}",
                    "Description": item.get("description"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=320,
            )
        else:
            st.info(
                "No cascading failure cognition available."
            )

    except Exception as exc:
        st.error(
            f"Cascade cognition failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # EXECUTION CHAIN COGNITION
    # ========================================================

    st.markdown("## 🧬 Execution Chain Cognition")

    try:

        chain = latest.get("execution_chain_model", {}) or {}

        top1, top2, top3, top4 = st.columns(4)

        top1.metric(
            "Chain State",
            chain.get("chain_state", "UNKNOWN"),
        )

        top2.metric(
            "Blocked Paths",
            chain.get("blocked_paths", 0),
        )

        top3.metric(
            "Failed Relays",
            chain.get("failed_relays", 0),
        )

        top4.metric(
            "High Sensitivity",
            chain.get("high_sensitivity", False),
        )

        st.json(chain)

    except Exception as exc:
        st.error(
            f"Execution chain cognition failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # OPERATIONAL MEMORY
    # ========================================================

    st.markdown("## 🧠 Operational Cognition Memory")

    try:

        rows = []

        for item in engine.list_assessments(limit=100):

            rows.append(
                {
                    "Time": _fmt_ts(item.get("created_at_ms")),
                    "State": f"{_icon(item.get('cognition_state'))} {item.get('cognition_state')}",
                    "Risk": item.get("risk_level"),
                    "Score": item.get("cognition_score"),
                    "Survivability": item.get("survivability_score"),
                    "Continuity": item.get("continuity_score"),
                    "Signals": len(item.get("signals", [])),
                    "Recommendations": len(item.get("recommendations", [])),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=420,
            )
        else:
            st.info(
                "No cognition memory available."
            )

    except Exception as exc:
        st.error(
            f"Operational cognition memory failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # LIVE SIGNAL STREAM
    # ========================================================

    st.markdown("## 📡 Live Cognition Signal Stream")

    try:

        rows = []

        for signal in engine.list_signals(limit=250):

            rows.append(
                {
                    "Time": _fmt_ts(signal.get("created_at_ms")),
                    "Signal": signal.get("signal_type"),
                    "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                    "Source": signal.get("source"),
                    "Target": signal.get("target"),
                    "Confidence": signal.get("confidence"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=420,
            )
        else:
            st.info(
                "No cognition signals available."
            )

    except Exception as exc:
        st.error(
            f"Live cognition stream failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # RECOMMENDATION STREAM
    # ========================================================

    st.markdown("## 🎯 Autonomous Recommendation Stream")

    try:

        rows = []

        for rec in engine.list_recommendations(limit=250):

            rows.append(
                {
                    "Time": _fmt_ts(rec.get("created_at_ms")),
                    "Action": rec.get("action"),
                    "Priority": f"{_icon(rec.get('priority'))} {rec.get('priority')}",
                    "Approval": rec.get("requires_approval"),
                    "Target": rec.get("target"),
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
            st.info(
                "No autonomous cognition recommendations available."
            )

    except Exception as exc:
        st.error(
            f"Recommendation telemetry failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # CONNECTED ENGINE TELEMETRY
    # ========================================================

    st.markdown("## 🔬 Connected Runtime Cognition Telemetry")

    telemetry_tabs = st.tabs(
        [
            "Predictive Runtime",
            "Learning Engine",
            "Sovereignty Engine",
            "Autonomous Cognition",
        ]
    )

    with telemetry_tabs[0]:

        try:
            if predictive_engine is not None:
                st.json(
                    predictive_engine.predictive_status()
                )
            else:
                st.info(
                    "Predictive runtime engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Predictive telemetry failed: {exc}"
            )

    with telemetry_tabs[1]:

        try:
            if learning_engine is not None:
                st.json(
                    learning_engine.learning_status()
                )
            else:
                st.info(
                    "Learning engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Learning telemetry failed: {exc}"
            )

    with telemetry_tabs[2]:

        try:
            if sovereignty_engine is not None:
                st.json(
                    sovereignty_engine.decision_engine_status()
                )
            else:
                st.info(
                    "Sovereignty engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Sovereignty telemetry failed: {exc}"
            )

    with telemetry_tabs[3]:
        st.json(status)

    if auto_refresh:
        time.sleep(5)
        st.rerun()