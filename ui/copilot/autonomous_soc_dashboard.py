"""
ui/copilot/autonomous_soc_dashboard.py

Executive Autonomous SOC Dashboard.

Shows:
- active autonomous operations
- graph execution map
- rollback pressure
- governance drift
- optimizer confidence
- live agent topology
- containment posture
- legal/export escalation visibility
- multi-agent orchestration status
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import streamlit as st

try:
    from core.events.event_subscribers import (
        initialize_event_subscribers,
        get_recent_events,
        get_event_statistics,
    )
except Exception:
    def initialize_event_subscribers() -> bool:
        return False

    def get_recent_events(limit: int = 100, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return []

    def get_event_statistics() -> Dict[str, Any]:
        return {
            "total_events": 0,
            "critical_events": 0,
            "high_events": 0,
            "medium_events": 0,
            "low_events": 0,
        }


GRAPH_EVENTS = {
    "EXECUTION_GRAPH_STARTED",
    "EXECUTION_GRAPH_COMPLETED",
    "EXECUTION_GRAPH_FAILED",
    "EXECUTION_GRAPH_NODE_STARTED",
    "EXECUTION_GRAPH_NODE_COMPLETED",
    "EXECUTION_GRAPH_ROLLBACK_STARTED",
    "EXECUTION_GRAPH_NODE_ROLLED_BACK",
}

CONTAINMENT_EVENTS = {
    "MAILBOX_ISOLATED",
    "ENDPOINT_QUARANTINED",
    "TOKENS_REVOKED",
    "SESSIONS_TERMINATED",
    "CONTAINMENT_VERIFIED",
    "CONTAINMENT_VERIFICATION_FAILED",
}

ROLLBACK_EVENTS = {
    "ROLLBACK_TRIGGERED",
    "COORDINATOR_STEP_ROLLED_BACK",
    "EXECUTION_GRAPH_ROLLBACK_STARTED",
    "EXECUTION_GRAPH_NODE_ROLLED_BACK",
    "CONTAINMENT_ROLLBACK_EXECUTED",
}

OPTIMIZER_EVENTS = {
    "OPTIMIZER_WORKFLOW_TUNED",
    "OPTIMIZER_ROLLBACK_REDUCTION_RECOMMENDED",
    "OPTIMIZER_CONFIDENCE_LEARNED",
    "OPTIMIZER_PATH_OPTIMIZED",
    "OPTIMIZER_ESCALATION_TUNED",
    "OPTIMIZER_VERIFICATION_TUNED",
}

ESCALATION_EVENTS = {
    "SLA_ESCALATION_TRIGGERED",
    "EXECUTIVE_ESCALATION_TRIGGERED",
    "LEGAL_ROUTING_TRIGGERED",
    "EXPORT_CONTROL_ESCALATION_TRIGGERED",
    "PAGER_ORCHESTRATION_TRIGGERED",
}

AGENTS = [
    "containment_agent",
    "verification_agent",
    "governance_agent",
    "escalation_agent",
    "optimizer_agent",
    "evidence_agent",
]


def _event_type(event: Dict[str, Any]) -> str:
    return str(event.get("event_type") or "UNKNOWN")


def _payload(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = event.get("payload") or {}
    return payload if isinstance(payload, dict) else {"value": str(payload)}


def _severity(event: Dict[str, Any]) -> str:
    return str(event.get("severity") or "LOW").upper()


def _source(event: Dict[str, Any]) -> str:
    return str(event.get("source") or "unknown")


def _fmt_ts(ts_ms: Any) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ts_ms) / 1000))
    except Exception:
        return "—"


def _count(events: List[Dict[str, Any]], event_types: set) -> int:
    return len([e for e in events if _event_type(e) in event_types])


def _rollback_pressure(events: List[Dict[str, Any]]) -> float:
    graph_started = len([e for e in events if _event_type(e) == "EXECUTION_GRAPH_STARTED"])
    rollback_count = _count(events, ROLLBACK_EVENTS)
    if graph_started <= 0:
        return 0.0
    return round((rollback_count / graph_started) * 100.0, 2)


def _optimizer_confidence(events: List[Dict[str, Any]]) -> float:
    optimizer_events = [e for e in events if _event_type(e) in OPTIMIZER_EVENTS]
    if not optimizer_events:
        return 0.0

    confidences = []
    for event in optimizer_events:
        payload = _payload(event)
        for key in ("confidence", "learned_confidence"):
            if key in payload:
                try:
                    confidences.append(float(payload[key]) * 100 if float(payload[key]) <= 1 else float(payload[key]))
                except Exception:
                    pass

    if not confidences:
        return 75.0

    return round(sum(confidences) / len(confidences), 2)


def _governance_drift(events: List[Dict[str, Any]]) -> float:
    blocked = len([e for e in events if "BLOCKED" in _event_type(e)])
    failed = len([e for e in events if "FAILED" in _event_type(e)])
    total = max(len(events), 1)
    return round(((blocked + failed) / total) * 100.0, 2)


def _render_kpis(events: List[Dict[str, Any]], stats: Dict[str, Any]) -> None:
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.metric("Active Events", stats.get("total_events", 0))
    with c2:
        st.metric("Graphs", _count(events, GRAPH_EVENTS))
    with c3:
        st.metric("Containments", _count(events, CONTAINMENT_EVENTS))
    with c4:
        st.metric("Rollback Pressure", f"{_rollback_pressure(events)}%")
    with c5:
        st.metric("Governance Drift", f"{_governance_drift(events)}%")
    with c6:
        st.metric("Optimizer Confidence", f"{_optimizer_confidence(events)}%")


def _render_agent_topology(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Live Agent Topology")

    rows = []

    for agent in AGENTS:
        agent_events = [
            e for e in events
            if _source(e) == agent or _payload(e).get("agent_name") == agent
        ]

        failures = len([e for e in agent_events if "FAILED" in _event_type(e) or _severity(e) == "CRITICAL"])
        blocked = len([e for e in agent_events if "BLOCKED" in _event_type(e)])

        if failures:
            status = "DEGRADED"
        elif blocked:
            status = "BLOCKING"
        elif agent_events:
            status = "ACTIVE"
        else:
            status = "IDLE"

        last_seen = max([int(e.get("timestamp_ms") or 0) for e in agent_events], default=0)

        rows.append(
            {
                "Agent": agent,
                "Status": status,
                "Events": len(agent_events),
                "Failures": failures,
                "Blocked": blocked,
                "Last Seen": _fmt_ts(last_seen) if last_seen else "—",
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_graph_map(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Graph Execution Map")

    graph_events = [e for e in events if _event_type(e) in GRAPH_EVENTS]

    if not graph_events:
        st.info("No graph execution telemetry captured yet.")
        return

    rows = []

    for e in graph_events[:100]:
        payload = _payload(e)
        rows.append(
            {
                "Time": _fmt_ts(e.get("timestamp_ms")),
                "Event": _event_type(e),
                "Graph ID": payload.get("graph_id", "—"),
                "Node ID": payload.get("node_id", "—"),
                "Agent": payload.get("agent_name", "—"),
                "Action": payload.get("action", "—"),
                "Success": payload.get("success", "—"),
                "Severity": _severity(e),
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_containment_posture(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Containment Posture")

    containment_events = [e for e in events if _event_type(e) in CONTAINMENT_EVENTS]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Mailbox Isolation", len([e for e in containment_events if _event_type(e) == "MAILBOX_ISOLATED"]))
    with c2:
        st.metric("Endpoint Quarantine", len([e for e in containment_events if _event_type(e) == "ENDPOINT_QUARANTINED"]))
    with c3:
        st.metric("Token Revocation", len([e for e in containment_events if _event_type(e) == "TOKENS_REVOKED"]))
    with c4:
        st.metric("Verification Failed", len([e for e in containment_events if "FAILED" in _event_type(e)]))

    if containment_events:
        for event in containment_events[:15]:
            with st.expander(f"{_event_type(event)} · {_fmt_ts(event.get('timestamp_ms'))}", expanded=False):
                st.json(_payload(event))
    else:
        st.info("No containment telemetry captured yet.")


def _render_escalation_visibility(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Legal / Export Escalation Visibility")

    escalation_events = [e for e in events if _event_type(e) in ESCALATION_EVENTS]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("SLA Escalations", len([e for e in escalation_events if _event_type(e) == "SLA_ESCALATION_TRIGGERED"]))
    with c2:
        st.metric("Executive", len([e for e in escalation_events if _event_type(e) == "EXECUTIVE_ESCALATION_TRIGGERED"]))
    with c3:
        st.metric("Legal", len([e for e in escalation_events if _event_type(e) == "LEGAL_ROUTING_TRIGGERED"]))
    with c4:
        st.metric("Export Control", len([e for e in escalation_events if _event_type(e) == "EXPORT_CONTROL_ESCALATION_TRIGGERED"]))

    if escalation_events:
        for event in escalation_events[:15]:
            with st.expander(f"{_event_type(event)} · {_fmt_ts(event.get('timestamp_ms'))}", expanded=False):
                st.json(_payload(event))
    else:
        st.info("No legal/export escalation telemetry captured yet.")


def _render_optimizer_panel(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Optimizer Intelligence")

    optimizer_events = [e for e in events if _event_type(e) in OPTIMIZER_EVENTS]

    if not optimizer_events:
        st.info("No optimizer intelligence captured yet.")
        return

    for event in optimizer_events[:20]:
        with st.expander(f"{_event_type(event)} · {_fmt_ts(event.get('timestamp_ms'))}", expanded=False):
            st.json(_payload(event))


def _render_recent_operations(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Recent Autonomous Operations")

    if not events:
        st.info("No autonomous operations captured yet.")
        return

    rows = []

    for event in events[:75]:
        rows.append(
            {
                "Time": _fmt_ts(event.get("timestamp_ms")),
                "Event": _event_type(event),
                "Severity": _severity(event),
                "Source": _source(event),
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_test_controls(storage: Optional[Any] = None) -> None:
    st.markdown("### Executive Test Controls")

    with st.expander("Run autonomous containment simulation", expanded=False):
        mailbox = st.text_input("Mailbox", "test@example.com", key="soc_dash_mailbox")
        endpoint = st.text_input("Endpoint", "WIN-DEVICE-001", key="soc_dash_endpoint")
        user = st.text_input("User", "test.user", key="soc_dash_user")
        severity = st.selectbox("Severity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"], index=2, key="soc_dash_sev")
        export_control = st.checkbox("Export Control", value=False, key="soc_dash_export")

        if st.button("Run Simulation", use_container_width=True, key="soc_dash_run_sim"):
            try:
                from core.agents.execution_graph_engine import ExecutionGraphEngine

                engine = ExecutionGraphEngine(storage=storage)
                result = engine.execute_containment_graph(
                    {
                        "mailbox": mailbox,
                        "endpoint": endpoint,
                        "user": user,
                        "severity": severity,
                        "export_control": export_control,
                        "category": "EXPORT_CONTROL" if export_control else "CUI",
                        "source": "autonomous_soc_dashboard",
                    }
                )

                if result.success:
                    st.success("Autonomous simulation completed.")
                else:
                    st.warning(f"Simulation completed with status: {result.status}")

                st.json(result.__dict__)

            except Exception as exc:
                st.error(f"Simulation failed: {exc}")


def render_autonomous_soc_dashboard(storage: Optional[Any] = None) -> None:
    """
    Main UI entrypoint.

    Usage:
        from ui.copilot.autonomous_soc_dashboard import render_autonomous_soc_dashboard
        render_autonomous_soc_dashboard(storage)
    """

    initialized = initialize_event_subscribers()
    events = get_recent_events(limit=1500)
    stats = get_event_statistics()

    st.markdown("# Autonomous SOC Command Dashboard")
    st.caption(
        "Executive visibility across autonomous operations, containment posture, rollback pressure, governance drift, optimization, and escalation routing."
    )

    if initialized:
        st.success("Autonomous telemetry fabric active.")
    else:
        st.warning("Telemetry fabric not fully active yet. Showing available in-memory events.")

    _render_kpis(events, stats)

    st.divider()

    tabs = st.tabs(
        [
            "Operations",
            "Agent Topology",
            "Execution Graphs",
            "Containment",
            "Legal / Export",
            "Optimizer",
            "Test Controls",
        ]
    )

    with tabs[0]:
        _render_recent_operations(events)

    with tabs[1]:
        _render_agent_topology(events)

    with tabs[2]:
        _render_graph_map(events)

    with tabs[3]:
        _render_containment_posture(events)

    with tabs[4]:
        _render_escalation_visibility(events)

    with tabs[5]:
        _render_optimizer_panel(events)

    with tabs[6]:
        _render_test_controls(storage)