"""
ui/copilot/governance_war_room.py

Governance War Room.

Executive operational oversight console for:
- autonomy pressure
- rollback storms
- escalation spikes
- tenant risk
- connector outages
- governance drift
- sandbox blocks
- confidence collapse
- legal/export pressure
- autonomy freeze conditions
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


try:
    from core.governance.autonomy_governor import (
        get_autonomy_governor,
        MODE_MANUAL,
        MODE_ASSISTED,
        MODE_SUPERVISED_AUTONOMY,
        MODE_FULL_AUTONOMY,
        MODE_LOCKDOWN,
        DECISION_CONTINUE,
        DECISION_THROTTLE,
        DECISION_REQUIRE_APPROVAL,
        DECISION_FREEZE,
        DECISION_LOCKDOWN,
    )
except Exception:
    get_autonomy_governor = None

    MODE_MANUAL = "MANUAL"
    MODE_ASSISTED = "ASSISTED"
    MODE_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
    MODE_FULL_AUTONOMY = "FULL_AUTONOMY"
    MODE_LOCKDOWN = "LOCKDOWN"

    DECISION_CONTINUE = "CONTINUE"
    DECISION_THROTTLE = "THROTTLE"
    DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DECISION_FREEZE = "FREEZE"
    DECISION_LOCKDOWN = "LOCKDOWN"


try:
    from core.connectors.connector_health_monitor import (
        get_connector_health_monitor,
    )
except Exception:
    get_connector_health_monitor = None


try:
    from core.runtime.worker_orchestrator import (
        get_worker_orchestrator,
    )
except Exception:
    get_worker_orchestrator = None


try:
    from core.runtime.distributed_execution_queue import (
        DistributedExecutionQueue,
    )
except Exception:
    DistributedExecutionQueue = None


# ============================================================
# MAIN RENDER
# ============================================================

def render_governance_war_room(
    storage: Optional[Any] = None,
    autonomy_mode: str = MODE_ASSISTED,
) -> None:

    st.subheader("🛡️ Governance War Room")
    st.caption(
        "Executive governance oversight for autonomy pressure, rollback storms, "
        "connector outages, governance drift, and freeze/lockdown conditions."
    )

    governor = (
        get_autonomy_governor()
        if get_autonomy_governor
        else None
    )

    if governor is None:
        st.error("AutonomyGovernor unavailable.")
        return

    # ========================================================
    # LIVE EVALUATION
    # ========================================================

    decision = governor.evaluate(
        autonomy_mode=autonomy_mode,
        persist=True,
    )

    # ========================================================
    # EXECUTIVE STATUS BAR
    # ========================================================

    _render_decision_banner(decision)

    st.markdown("---")

    # ========================================================
    # TOPLINE PRESSURE
    # ========================================================

    st.markdown("### 🌐 Executive Pressure Indicators")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Rollback %",
        f"{decision.rollback_pressure:.1f}%",
    )

    c2.metric(
        "Gov Drift %",
        f"{decision.governance_drift:.1f}%",
    )

    c3.metric(
        "Confidence",
        f"{decision.optimizer_confidence:.1f}",
    )

    c4.metric(
        "Queue Pressure",
        decision.queue_pressure,
    )

    c5.metric(
        "Connector Outages",
        decision.connector_outages,
    )

    c6.metric(
        "Sandbox Blocks",
        decision.sandbox_blocks,
    )

    st.markdown("---")

    # ========================================================
    # EXECUTION STATE
    # ========================================================

    left, right = st.columns([2, 1])

    with left:
        _render_governance_heatmap(decision)

    with right:
        _render_governor_summary(decision)

    st.markdown("---")

    # ========================================================
    # WAR ROOM TABS
    # ========================================================

    tabs = st.tabs([
        "Governance Drift",
        "Rollback Storms",
        "Connector Pressure",
        "Tenant Risk",
        "Worker Health",
        "Decision Timeline",
        "Findings",
    ])

    with tabs[0]:
        _render_governance_drift(decision)

    with tabs[1]:
        _render_rollback_pressure(decision)

    with tabs[2]:
        _render_connector_pressure()

    with tabs[3]:
        _render_tenant_risk(governor)

    with tabs[4]:
        _render_worker_health()

    with tabs[5]:
        _render_decision_timeline(governor)

    with tabs[6]:
        _render_findings(decision)


# ============================================================
# EXECUTIVE BANNER
# ============================================================

def _render_decision_banner(decision) -> None:

    decision_type = decision.decision

    if decision_type == DECISION_LOCKDOWN:
        st.error(
            f"🚨 LOCKDOWN ACTIVE — {decision.reason}"
        )

    elif decision_type == DECISION_FREEZE:
        st.warning(
            f"⛔ EXECUTION FREEZE — {decision.reason}"
        )

    elif decision_type == DECISION_THROTTLE:
        st.warning(
            f"⚠️ AUTONOMY THROTTLED ({decision.throttle_factor:.2f}) — {decision.reason}"
        )

    elif decision_type == DECISION_REQUIRE_APPROVAL:
        st.info(
            f"📝 APPROVAL REQUIRED — {decision.reason}"
        )

    else:
        st.success(
            f"✅ AUTONOMY STABLE — {decision.reason}"
        )


# ============================================================
# HEATMAP
# ============================================================

def _render_governance_heatmap(decision) -> None:

    st.markdown("### 🔥 Governance Pressure Heatmap")

    rows = [
        {
            "Metric": "Rollback Pressure",
            "Value": decision.rollback_pressure,
            "Severity": _severity_from_percentage(decision.rollback_pressure),
        },
        {
            "Metric": "Governance Drift",
            "Value": decision.governance_drift,
            "Severity": _severity_from_percentage(decision.governance_drift),
        },
        {
            "Metric": "Connector Outages",
            "Value": decision.connector_outages,
            "Severity": _severity_from_count(decision.connector_outages),
        },
        {
            "Metric": "Sandbox Blocks",
            "Value": decision.sandbox_blocks,
            "Severity": _severity_from_count(decision.sandbox_blocks),
        },
        {
            "Metric": "Dead Letters",
            "Value": decision.dead_letters,
            "Severity": _severity_from_count(decision.dead_letters),
        },
        {
            "Metric": "Escalation Spike",
            "Value": decision.escalation_spike,
            "Severity": _severity_from_count(decision.escalation_spike),
        },
        {
            "Metric": "Legal / Export Pressure",
            "Value": decision.legal_export_pressure,
            "Severity": _severity_from_count(decision.legal_export_pressure),
        },
    ]

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


# ============================================================
# GOVERNOR SUMMARY
# ============================================================

def _render_governor_summary(decision) -> None:

    st.markdown("### 🧠 Governor State")

    st.metric(
        "Decision",
        decision.decision,
    )

    st.metric(
        "Current Mode",
        decision.autonomy_mode,
    )

    st.metric(
        "Recommended Mode",
        decision.recommended_mode,
    )

    st.metric(
        "Approval Required",
        "YES" if decision.require_approval else "NO",
    )

    st.metric(
        "Freeze",
        "YES" if decision.freeze_execution else "NO",
    )

    st.metric(
        "Lockdown",
        "YES" if decision.enter_lockdown else "NO",
    )


# ============================================================
# GOVERNANCE DRIFT
# ============================================================

def _render_governance_drift(decision) -> None:

    st.markdown("### 📉 Governance Drift Analysis")

    rows = [
        {
            "Drift Source": "Policy Blocks",
            "Pressure": decision.governance_drift,
        },
        {
            "Drift Source": "Sandbox Violations",
            "Pressure": decision.sandbox_blocks,
        },
        {
            "Drift Source": "Connector Instability",
            "Pressure": decision.connector_outages + decision.connector_degraded,
        },
        {
            "Drift Source": "Rollback Instability",
            "Pressure": decision.rollback_pressure,
        },
    ]

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=250,
    )


# ============================================================
# ROLLBACK STORMS
# ============================================================

def _render_rollback_pressure(decision) -> None:

    st.markdown("### 🔄 Rollback Storm Analysis")

    cols = st.columns(4)

    cols[0].metric(
        "Rollback %",
        f"{decision.rollback_pressure:.2f}%",
    )

    cols[1].metric(
        "Dead Letters",
        decision.dead_letters,
    )

    cols[2].metric(
        "Throttle Factor",
        f"{decision.throttle_factor:.2f}",
    )

    cols[3].metric(
        "Escalation Spike",
        decision.escalation_spike,
    )

    risk = _pressure_risk_label(
        decision.rollback_pressure,
    )

    st.markdown(f"**Rollback Storm Risk:** `{risk}`")


# ============================================================
# CONNECTOR PRESSURE
# ============================================================

def _render_connector_pressure() -> None:

    st.markdown("### 🔌 Connector Operations Pressure")

    monitor = (
        get_connector_health_monitor()
        if get_connector_health_monitor
        else None
    )

    if monitor is None:
        st.warning("ConnectorHealthMonitor unavailable.")
        return

    rows = []

    for state in monitor.list_states():
        rows.append({
            "Connector": state.connector_name,
            "Health": state.health,
            "Failures": state.failure_count,
            "Retries": state.retry_count,
            "Auth Failures": state.auth_failures,
            "Latency(ms)": round(state.avg_latency_ms, 2),
            "Outage": state.outage_detected,
        })

    if not rows:
        st.info("No connector telemetry yet.")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


# ============================================================
# TENANT RISK
# ============================================================

def _render_tenant_risk(governor) -> None:

    st.markdown("### 🏢 Tenant Risk Overview")

    tenants = [
        "default",
        "govcloud",
        "enterprise",
        "mssp",
    ]

    rows = []

    for tenant in tenants:

        try:
            d = governor.evaluate(
                autonomy_mode=MODE_SUPERVISED_AUTONOMY,
                tenant_id=tenant,
                persist=False,
            )

            rows.append({
                "Tenant": tenant,
                "Decision": d.decision,
                "Rollback %": d.rollback_pressure,
                "Gov Drift %": d.governance_drift,
                "Queue Pressure": d.queue_pressure,
                "Confidence": d.optimizer_confidence,
                "Risk": _decision_risk_label(d.decision),
            })

        except Exception:
            pass

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            height=280,
        )


# ============================================================
# WORKER HEALTH
# ============================================================

def _render_worker_health() -> None:

    st.markdown("### 🧑‍🏭 Worker Health")

    orchestrator = (
        get_worker_orchestrator()
        if get_worker_orchestrator
        else None
    )

    if orchestrator is None:
        st.warning("WorkerOrchestrator unavailable.")
        return

    workers = orchestrator.list_workers()

    rows = []

    for worker in workers:
        rows.append({
            "Worker": worker.worker_id,
            "Status": worker.status,
            "Active Jobs": worker.active_jobs,
            "Max Jobs": worker.max_concurrent_jobs,
            "Capabilities": ", ".join(worker.capabilities),
            "Tenant Affinity": ", ".join(worker.tenant_affinity),
            "Last Seen": worker.last_seen_ms,
            "Last Error": worker.last_error,
        })

    if not rows:
        st.info("No worker telemetry.")
        return

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


# ============================================================
# DECISION TIMELINE
# ============================================================

def _render_decision_timeline(governor) -> None:

    st.markdown("### 📜 Governor Decision Timeline")

    decisions = governor.list_decisions(limit=100)

    if not decisions:
        st.info("No governor decisions recorded.")
        return

    rows = []

    for d in decisions:
        rows.append({
            "Time": d.get("created_at_ms"),
            "Decision": d.get("decision"),
            "Mode": d.get("autonomy_mode"),
            "Recommended": d.get("recommended_mode"),
            "Rollback %": d.get("rollback_pressure"),
            "Gov Drift %": d.get("governance_drift"),
            "Queue Pressure": d.get("queue_pressure"),
            "Outages": d.get("connector_outages"),
            "Reason": d.get("reason"),
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=420,
    )


# ============================================================
# FINDINGS
# ============================================================

def _render_findings(decision) -> None:

    st.markdown("### 🚨 Active Governance Findings")

    findings = decision.findings or []

    if not findings:
        st.success("No active governance findings.")
        return

    rows = []

    for finding in findings:
        rows.append({
            "Finding": finding,
            "Severity": _finding_severity(finding),
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=320,
    )


# ============================================================
# HELPERS
# ============================================================

def _severity_from_percentage(value: float) -> str:

    if value >= 50:
        return "CRITICAL"

    if value >= 30:
        return "HIGH"

    if value >= 15:
        return "MEDIUM"

    return "LOW"


def _severity_from_count(value: int) -> str:

    if value >= 15:
        return "CRITICAL"

    if value >= 8:
        return "HIGH"

    if value >= 3:
        return "MEDIUM"

    return "LOW"


def _pressure_risk_label(value: float) -> str:

    if value >= 50:
        return "CRITICAL"

    if value >= 30:
        return "HIGH"

    if value >= 15:
        return "MEDIUM"

    return "LOW"


def _decision_risk_label(decision: str) -> str:

    if decision == DECISION_LOCKDOWN:
        return "CRITICAL"

    if decision == DECISION_FREEZE:
        return "HIGH"

    if decision == DECISION_THROTTLE:
        return "MEDIUM"

    return "LOW"


def _finding_severity(finding: str) -> str:

    upper = str(finding).upper()

    if any(k in upper for k in [
        "LOCKDOWN",
        "FREEZE",
        "CRITICAL",
    ]):
        return "CRITICAL"

    if any(k in upper for k in [
        "THROTTLE",
        "OUTAGE",
        "DEAD",
    ]):
        return "HIGH"

    return "MEDIUM"