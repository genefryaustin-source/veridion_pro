"""
ui/copilot/runtime_fabric_learning_console.py

Runtime Fabric Learning Console.

Purpose:
- sovereign runtime learning command center
- operational learning visibility
- topology trust modeling
- runtime degradation learning intelligence
- sovereign operational memory visualization
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
        "SUCCESS",
        "HEALTHY",
    }:
        return "🟢"

    if value in {
        "MEDIUM",
        "DEGRADING",
        "PARTIAL",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "UNSTABLE",
        "FAILED",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "RECURRING",
        "BLOCKED",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_runtime_fabric_learning_console(
    storage: Any,
) -> None:

    st.markdown("# 🧠 Runtime Fabric Learning")
    st.caption(
        "Adaptive sovereign operational learning cognition, runtime memory intelligence, and topology trust evolution."
    )

    engine = getattr(
        storage,
        "runtime_fabric_learning_engine",
        None,
    )

    sovereignty_engine = getattr(
        storage,
        "sovereignty_decision_engine",
        None,
    )

    policy_engine = getattr(
        storage,
        "adaptive_sovereign_policy_engine",
        None,
    )

    relay = getattr(
        storage,
        "cross_runtime_execution_relay",
        None,
    )

    if engine is None:
        st.error(
            "Runtime Fabric Learning Engine unavailable."
        )
        return

    # ========================================================
    # STATUS
    # ========================================================

    st.markdown("## 🌐 Runtime Learning Status")

    try:
        status = engine.learning_status()
    except Exception as exc:
        status = {"error": str(exc)}

    latest = status.get("latest_assessment") or {}

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Events",
        status.get("event_count", 0),
    )

    c2.metric(
        "Patterns",
        status.get("pattern_count", 0),
    )

    c3.metric(
        "Assessments",
        status.get("assessment_count", 0),
    )

    c4.metric(
        "Targets",
        status.get("target_count", 0),
    )

    c5.metric(
        "Learning State",
        f"{_icon(latest.get('learning_state'))} {latest.get('learning_state', 'UNKNOWN')}",
    )

    st.markdown("---")

    # ========================================================
    # LEARNING CONTROL
    # ========================================================

    st.markdown("## ⚙️ Runtime Learning Operations")

    l1, l2, l3 = st.columns(3)

    with l1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="runtime_learning_tenant",
        )

    with l2:
        auto_ingest = st.checkbox(
            "Auto Ingest",
            value=False,
            key="runtime_learning_auto_ingest",
        )

    with l3:
        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=False,
            key="runtime_learning_auto_refresh",
        )

    ops_tabs = st.tabs(
        [
            "Ingest Runtime State",
            "Run Learning Assessment",
        ]
    )

    with ops_tabs[0]:

        if st.button(
            "Ingest Current Runtime State",
            use_container_width=True,
            key="runtime_learning_ingest_btn",
        ):
            try:
                result = engine.ingest_current_state(
                    tenant_id=tenant_id,
                )

                st.success(
                    "Runtime learning ingestion completed."
                )

                st.json(result)

            except Exception as exc:
                st.error(
                    f"Runtime learning ingestion failed: {exc}"
                )

    with ops_tabs[1]:

        if st.button(
            "Run Runtime Learning Assessment",
            use_container_width=True,
            key="runtime_learning_assess_btn",
        ):
            try:
                assessment = engine.assess(
                    tenant_id=tenant_id,
                )

                st.success(
                    "Runtime learning assessment completed."
                )

                st.json(
                    assessment.to_dict()
                    if hasattr(assessment, "to_dict")
                    else assessment
                )

            except Exception as exc:
                st.error(
                    f"Runtime learning assessment failed: {exc}"
                )

    st.markdown("---")

    # ========================================================
    # LATEST ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Runtime Learning Assessment")

    if latest:

        latest_tabs = st.tabs(
            [
                "Assessment",
                "Patterns",
                "Learned Signals",
                "Telemetry",
            ]
        )

        with latest_tabs[0]:
            st.json(latest)

        with latest_tabs[1]:

            rows = []

            for pattern in latest.get("patterns", []):

                rows.append(
                    {
                        "Pattern": pattern.get("pattern_type"),
                        "Severity": f"{_icon(pattern.get('severity'))} {pattern.get('severity')}",
                        "Confidence": pattern.get("confidence"),
                        "Events": pattern.get("event_count"),
                        "Target": pattern.get("target"),
                        "Message": pattern.get("message"),
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
                    "No runtime learning patterns available."
                )

        with latest_tabs[2]:

            rows = []

            for signal in latest.get("learned_signals", []):

                rows.append(
                    {
                        "Signal": signal.get("signal_type"),
                        "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                        "Confidence": signal.get("confidence"),
                        "Target": signal.get("target"),
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
                st.info(
                    "No learned runtime signals available."
                )

        with latest_tabs[3]:
            st.json(
                latest.get("telemetry", {})
            )

    else:
        st.info(
            "No runtime learning assessments available."
        )

    st.markdown("---")

    # ========================================================
    # OPERATIONAL MEMORY
    # ========================================================

    st.markdown("## 🧠 Operational Learning Memory")

    try:

        events = engine.list_events(limit=250)

        rows = []

        for event in events:

            rows.append(
                {
                    "Time": _fmt_ts(event.get("created_at_ms")),
                    "Event": event.get("event_type"),
                    "Outcome": f"{_icon(event.get('outcome'))} {event.get('outcome')}",
                    "Source": event.get("source"),
                    "Target": event.get("target"),
                    "Score": event.get("score"),
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
                "No runtime learning events available."
            )

    except Exception as exc:
        st.error(
            f"Operational learning memory failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # PATTERN INTELLIGENCE
    # ========================================================

    st.markdown("## 🔗 Runtime Pattern Intelligence")

    try:

        patterns = engine.list_patterns(limit=250)

        rows = []

        for pattern in patterns:

            rows.append(
                {
                    "Time": _fmt_ts(pattern.get("created_at_ms")),
                    "Pattern": pattern.get("pattern_type"),
                    "Severity": f"{_icon(pattern.get('severity'))} {pattern.get('severity')}",
                    "Confidence": pattern.get("confidence"),
                    "Target": pattern.get("target"),
                    "Events": pattern.get("event_count"),
                    "Message": pattern.get("message"),
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
                "No runtime learning patterns available."
            )

    except Exception as exc:
        st.error(
            f"Runtime pattern intelligence failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # TOPOLOGY TRUST MODELING
    # ========================================================

    st.markdown("## 🌐 Runtime Trust Intelligence")

    try:

        scores = engine.target_scores()

        rows = []

        for item in scores:

            trust = float(item.get("trust_score", 0.0) or 0.0)

            if trust >= 80:
                severity = "LOW"
            elif trust >= 60:
                severity = "MEDIUM"
            elif trust >= 35:
                severity = "HIGH"
            else:
                severity = "CRITICAL"

            rows.append(
                {
                    "Target": item.get("target"),
                    "Trust": f"{_icon(severity)} {trust}",
                    "Events": item.get("events"),
                    "Success": item.get("success"),
                    "Failed": item.get("failed"),
                    "Blocked": item.get("blocked"),
                    "Average Score": item.get("avg_score"),
                    "Updated": _fmt_ts(item.get("updated_at_ms")),
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
                "No topology trust models available."
            )

    except Exception as exc:
        st.error(
            f"Runtime trust intelligence failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # PREDICTIVE LEARNING SIGNALS
    # ========================================================

    st.markdown("## 🚨 Predictive Runtime Signals")

    try:

        assessments = engine.list_assessments(limit=100)

        rows = []

        for assessment in assessments:

            rows.append(
                {
                    "Time": _fmt_ts(assessment.get("created_at_ms")),
                    "State": f"{_icon(assessment.get('learning_state'))} {assessment.get('learning_state')}",
                    "Confidence": assessment.get("confidence"),
                    "Stability": assessment.get("stability_score"),
                    "Patterns": len(assessment.get("patterns", [])),
                    "Signals": len(assessment.get("learned_signals", [])),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=360,
            )
        else:
            st.info(
                "No predictive runtime learning signals available."
            )

    except Exception as exc:
        st.error(
            f"Predictive runtime learning failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # CONNECTED ENGINE TELEMETRY
    # ========================================================

    st.markdown("## 🔬 Runtime Cognition Telemetry")

    telemetry_tabs = st.tabs(
        [
            "Sovereignty Decisions",
            "Policy Engine",
            "Execution Relay",
            "Learning Status",
        ]
    )

    with telemetry_tabs[0]:

        try:
            if sovereignty_engine is not None:
                st.json(
                    sovereignty_engine.decision_engine_status()
                )
            else:
                st.info(
                    "Sovereignty decision engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Sovereignty telemetry failed: {exc}"
            )

    with telemetry_tabs[1]:

        try:
            if policy_engine is not None:
                st.json(
                    policy_engine.policy_engine_status()
                )
            else:
                st.info(
                    "Policy engine unavailable."
                )
        except Exception as exc:
            st.error(
                f"Policy telemetry failed: {exc}"
            )

    with telemetry_tabs[2]:

        try:
            if relay is not None:
                st.json(
                    relay.relay_status()
                )
            else:
                st.info(
                    "Execution relay unavailable."
                )
        except Exception as exc:
            st.error(
                f"Execution relay telemetry failed: {exc}"
            )

    with telemetry_tabs[3]:
        st.json(status)

    if auto_ingest:
        try:
            engine.ingest_current_state(
                tenant_id=tenant_id,
            )
        except Exception:
            pass

    if auto_refresh:
        time.sleep(5)
        st.rerun()