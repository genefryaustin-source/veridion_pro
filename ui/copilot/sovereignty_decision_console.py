"""
ui/copilot/sovereignty_decision_console.py

Sovereignty Decision Console.

Purpose:
- sovereign operational reasoning command center
- fused sovereign decision visibility
- operational impact analysis
- sovereign risk intelligence
- governance escalation cognition
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
        "BALANCED",
        "HEALTHY",
        "AUTHORIZED",
        "EXECUTED",
        "OBSERVE",
    }:
        return "🟢"

    if value in {
        "MEDIUM",
        "PENDING",
        "DRY_RUN",
        "RECOMMENDED",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "HARDENED",
        "FAILED",
        "RESTRICT_RELAYS",
        "RESTRICT_FEDERATED_ROUTING",
        "REDUCE_AUTONOMY",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "LOCKDOWN",
        "QUARANTINE_CLUSTER",
        "QUARANTINE_DOMAIN",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_sovereignty_decision_console(
    storage: Any,
) -> None:
    st.markdown("# 🧠 Sovereignty Decision Engine")
    st.caption(
        "Fused sovereign operational reasoning, topology cognition, governance escalation intelligence, and sovereign decision orchestration."
    )

    engine = getattr(
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

    mesh_optimizer = getattr(
        storage,
        "sovereign_mesh_optimizer",
        None,
    )

    autonomy_governor = getattr(
        storage,
        "autonomy_governor_v2",
        None,
    )

    if engine is None:
        st.error(
            "Sovereignty Decision Engine unavailable."
        )
        return

    # ========================================================
    # ENGINE STATUS
    # ========================================================

    st.markdown("## 🌐 Sovereign Reasoning Status")

    try:
        status = engine.decision_engine_status()
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
        "Decisions",
        status.get("decision_count", 0),
    )

    c4.metric(
        "Risk",
        f"{_icon(latest.get('risk_level'))} {latest.get('risk_level', 'UNKNOWN')}",
    )

    c5.metric(
        "Confidence",
        latest.get("confidence", 0),
    )

    st.markdown("---")

    # ========================================================
    # DECISION REASONING
    # ========================================================

    st.markdown("## 🧠 Sovereign Operational Reasoning")

    r1, r2, r3 = st.columns(3)

    with r1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="sov_decision_tenant",
        )

    with r2:
        action = st.text_input(
            "Workload Action",
            value="SOVEREIGN_RUNTIME_REASONING",
            key="sov_decision_action",
        )

    with r3:
        dry_run = st.checkbox(
            "Dry Run",
            value=True,
            key="sov_decision_dry_run",
        )

    categories = st.multiselect(
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
        key="sov_decision_categories",
    )

    workload = {
        "action": action,
        "categories": categories,
        "source": "sovereignty_decision_console",
    }

    reasoning_tabs = st.tabs(
        [
            "Assess",
            "Enforce",
        ]
    )

    with reasoning_tabs[0]:

        if st.button(
            "Run Sovereign Reasoning",
            use_container_width=True,
            key="run_sovereign_reasoning_btn",
        ):
            try:
                assessment = engine.assess(
                    tenant_id=tenant_id,
                    workload=workload,
                )

                st.success(
                    "Sovereign operational reasoning completed."
                )

                st.json(
                    assessment.to_dict()
                    if hasattr(assessment, "to_dict")
                    else assessment
                )

            except Exception as exc:
                st.error(
                    f"Sovereign reasoning failed: {exc}"
                )

    with reasoning_tabs[1]:

        if st.button(
            "Execute Sovereign Decisions",
            use_container_width=True,
            key="execute_sovereign_decisions_btn",
        ):
            try:
                result = engine.enforce(
                    tenant_id=tenant_id,
                    workload=workload,
                    dry_run=dry_run,
                )

                st.success(
                    "Sovereign decision execution completed."
                )

                st.json(result)

            except Exception as exc:
                st.error(
                    f"Sovereign decision execution failed: {exc}"
                )

    st.markdown("---")

    # ========================================================
    # LATEST ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Sovereign Assessment")

    if latest:

        assess_tabs = st.tabs(
            [
                "Assessment",
                "Signals",
                "Decisions",
                "Telemetry",
            ]
        )

        with assess_tabs[0]:
            st.json(latest)

        with assess_tabs[1]:

            rows = []

            for signal in latest.get("signals", []):

                rows.append(
                    {
                        "Type": signal.get("signal_type"),
                        "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                        "Source": signal.get("source"),
                        "Weight": signal.get("weight"),
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
                    "No sovereign reasoning signals available."
                )

        with assess_tabs[2]:

            rows = []

            for decision in latest.get("decisions", []):

                rows.append(
                    {
                        "Decision": f"{_icon(decision.get('decision_type'))} {decision.get('decision_type')}",
                        "Risk": f"{_icon(decision.get('risk_level'))} {decision.get('risk_level')}",
                        "Confidence": decision.get("confidence"),
                        "Blast Radius": decision.get("blast_radius"),
                        "Governance": decision.get("governance_impact"),
                        "Operational": decision.get("operational_impact"),
                        "Reason": decision.get("reason"),
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
                    "No sovereign decisions available."
                )

        with assess_tabs[3]:
            st.json(
                latest.get("telemetry", {})
            )

    else:
        st.info("No sovereign assessments available.")

    st.markdown("---")

    # ========================================================
    # DECISION STREAM
    # ========================================================

    st.markdown("## 📡 Sovereign Decision Stream")

    try:

        decisions = engine.list_decisions(limit=250)

        rows = []

        for decision in decisions:

            rows.append(
                {
                    "Time": _fmt_ts(decision.get("created_at_ms")),
                    "Decision": f"{_icon(decision.get('decision_type'))} {decision.get('decision_type')}",
                    "Risk": f"{_icon(decision.get('risk_level'))} {decision.get('risk_level')}",
                    "Confidence": decision.get("confidence"),
                    "Blast Radius": decision.get("blast_radius"),
                    "Status": decision.get("status"),
                    "Reason": decision.get("reason"),
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
                "No sovereign decisions available."
            )

    except Exception as exc:
        st.error(
            f"Sovereign decision stream failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # SIGNAL CORRELATION
    # ========================================================

    st.markdown("## 🔗 Signal Correlation Intelligence")

    try:

        signals = engine.list_signals(limit=250)

        rows = []

        for signal in signals:

            rows.append(
                {
                    "Time": _fmt_ts(signal.get("created_at_ms")),
                    "Signal": signal.get("signal_type"),
                    "Severity": f"{_icon(signal.get('severity'))} {signal.get('severity')}",
                    "Weight": signal.get("weight"),
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
            st.info(
                "No sovereign signals available."
            )

    except Exception as exc:
        st.error(
            f"Signal correlation analysis failed: {exc}"
        )

    st.markdown("---")

    # ========================================================
    # OPERATIONAL IMPACT
    # ========================================================

    st.markdown("## 🌐 Operational Impact Intelligence")

    impact_tabs = st.tabs(
        [
            "Policy Engine",
            "Execution Relay",
            "Mesh Optimizer",
            "Autonomy Governor",
            "Engine Status",
        ]
    )

    with impact_tabs[0]:

        try:
            if policy_engine is not None:
                st.json(
                    policy_engine.policy_engine_status()
                )
            else:
                st.info("Policy engine unavailable.")
        except Exception as exc:
            st.error(
                f"Policy engine telemetry failed: {exc}"
            )

    with impact_tabs[1]:

        try:
            if relay is not None:
                st.json(
                    relay.relay_status()
                )
            else:
                st.info("Execution relay unavailable.")
        except Exception as exc:
            st.error(
                f"Execution relay telemetry failed: {exc}"
            )

    with impact_tabs[2]:

        try:
            if mesh_optimizer is not None:
                st.json(
                    mesh_optimizer.optimizer_status()
                )
            else:
                st.info("Mesh optimizer unavailable.")
        except Exception as exc:
            st.error(
                f"Mesh optimizer telemetry failed: {exc}"
            )

    with impact_tabs[3]:

        try:
            if autonomy_governor is not None:
                st.json(
                    autonomy_governor.governor_status()
                )
            else:
                st.info("Autonomy governor unavailable.")
        except Exception as exc:
            st.error(
                f"Autonomy governor telemetry failed: {exc}"
            )

    with impact_tabs[4]:
        st.json(status)

    st.markdown("---")

    # ========================================================
    # GOVERNANCE ESCALATION INTELLIGENCE
    # ========================================================

    st.markdown("## 🚨 Governance Escalation Intelligence")

    try:

        assessments = engine.list_assessments(limit=100)

        rows = []

        for item in assessments:

            rows.append(
                {
                    "Time": _fmt_ts(item.get("created_at_ms")),
                    "Risk": f"{_icon(item.get('risk_level'))} {item.get('risk_level')}",
                    "Confidence": item.get("confidence"),
                    "Signals": len(item.get("signals", [])),
                    "Decisions": len(item.get("decisions", [])),
                    "Summary": item.get("summary"),
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
                "No governance escalation intelligence available."
            )

    except Exception as exc:
        st.error(
            f"Governance escalation intelligence failed: {exc}"
        )

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="sovereignty_decision_console_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()