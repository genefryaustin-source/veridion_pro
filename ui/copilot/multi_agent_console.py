"""
ui/copilot/multi_agent_console.py

Multi-Agent SOC Console.

Shows:
- active autonomous SOC activity
- agent health
- graph execution telemetry
- containment chains
- verification failures
- rollback chains
- escalation routing
- recent multi-agent events

Safe:
- Works with the in-memory event_subscribers buffer
- Does not require DB schema changes
- Does not require active graph executions to render
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


AGENT_NAMES = [
    "containment_agent",
    "verification_agent",
    "governance_agent",
    "escalation_agent",
    "optimizer_agent",
    "evidence_agent",
]

GRAPH_EVENT_TYPES = {
    "EXECUTION_GRAPH_STARTED",
    "EXECUTION_GRAPH_COMPLETED",
    "EXECUTION_GRAPH_FAILED",
    "EXECUTION_GRAPH_NODE_STARTED",
    "EXECUTION_GRAPH_NODE_COMPLETED",
    "EXECUTION_GRAPH_ROLLBACK_STARTED",
    "EXECUTION_GRAPH_NODE_ROLLED_BACK",
    "EXECUTION_GRAPH_ROLLBACK_FAILED",
    "EXECUTION_GRAPH_OPTIMIZER_FEEDBACK",
}

AGENT_EVENT_TYPES = {
    "AGENT_EXECUTION_STARTED",
    "AGENT_EXECUTION_COMPLETED",
    "AGENT_EXECUTION_FAILED",
    "AGENT_EXECUTION_BLOCKED",
    "AGENT_ACTION",
}

CONTAINMENT_EVENT_TYPES = {
    "MAILBOX_ISOLATED",
    "ENDPOINT_QUARANTINED",
    "TOKENS_REVOKED",
    "SESSIONS_TERMINATED",
    "CONTAINMENT_ROLLBACK_EXECUTED",
    "CONTAINMENT_VERIFIED",
    "CONTAINMENT_VERIFICATION_FAILED",
}

ESCALATION_EVENT_TYPES = {
    "SLA_ESCALATION_TRIGGERED",
    "EXECUTIVE_ESCALATION_TRIGGERED",
    "LEGAL_ROUTING_TRIGGERED",
    "EXPORT_CONTROL_ESCALATION_TRIGGERED",
    "PAGER_ORCHESTRATION_TRIGGERED",
}

ROLLBACK_EVENT_TYPES = {
    "ROLLBACK_TRIGGERED",
    "COORDINATOR_STEP_ROLLED_BACK",
    "COORDINATOR_ROLLBACK_FAILED",
    "EXECUTION_GRAPH_ROLLBACK_STARTED",
    "EXECUTION_GRAPH_NODE_ROLLED_BACK",
    "EXECUTION_GRAPH_ROLLBACK_FAILED",
    "CONTAINMENT_ROLLBACK_EXECUTED",
}

SEVERITY_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f97316",
    "MEDIUM": "#eab308",
    "LOW": "#22c55e",
    "INFO": "#3b82f6",
}


def _fmt_ts(ts_ms: Any) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ts_ms) / 1000))
    except Exception:
        return "unknown-time"


def _payload(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = event.get("payload") or {}
    return payload if isinstance(payload, dict) else {"value": str(payload)}


def _event_type(event: Dict[str, Any]) -> str:
    return str(event.get("event_type") or "UNKNOWN")


def _severity(event: Dict[str, Any]) -> str:
    return str(event.get("severity") or "LOW").upper()


def _source(event: Dict[str, Any]) -> str:
    return str(event.get("source") or "unknown")


def _agent_from_event(event: Dict[str, Any]) -> str:
    payload = _payload(event)
    return str(payload.get("agent_name") or event.get("source") or "unknown")


def _metric_card(label: str, value: Any, help_text: str = "") -> None:
    st.metric(label, value, help=help_text or None)


def _render_event_card(event: Dict[str, Any], expanded: bool = False) -> None:
    event_type = _event_type(event)
    severity = _severity(event)
    source = _source(event)
    ts = _fmt_ts(event.get("timestamp_ms"))
    color = SEVERITY_COLORS.get(severity, "#64748b")

    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {color};
            background: rgba(148,163,184,0.08);
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.65rem;
        ">
            <div style="display:flex; justify-content:space-between; gap:1rem;">
                <div style="font-weight:800;">{event_type}</div>
                <div style="font-weight:800; color:{color};">{severity}</div>
            </div>
            <div style="font-size:0.82rem; opacity:0.75; margin-top:0.25rem;">
                {ts} · {source}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Payload", expanded=expanded):
        st.json(_payload(event))


def _filter_events(
    events: List[Dict[str, Any]],
    event_types: Optional[set] = None,
    agent: Optional[str] = None,
    severity_filter: Optional[List[str]] = None,
    contains: str = "",
) -> List[Dict[str, Any]]:
    filtered = []

    for event in events:
        et = _event_type(event)
        sev = _severity(event)
        ag = _agent_from_event(event)

        if event_types and et not in event_types:
            continue

        if agent and agent != "All" and ag != agent:
            continue

        if severity_filter and sev not in severity_filter:
            continue

        if contains:
            blob = f"{et} {_source(event)} {_payload(event)}".lower()
            if contains.lower() not in blob:
                continue

        filtered.append(event)

    return filtered


def _summarize_agent_health(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    health: Dict[str, Dict[str, Any]] = {}

    for name in AGENT_NAMES:
        health[name] = {
            "status": "IDLE",
            "events": 0,
            "failures": 0,
            "blocked": 0,
            "last_seen_ms": None,
        }

    for event in events:
        agent = _agent_from_event(event)
        if agent not in health:
            health[agent] = {
                "status": "IDLE",
                "events": 0,
                "failures": 0,
                "blocked": 0,
                "last_seen_ms": None,
            }

        et = _event_type(event)

        health[agent]["events"] += 1
        health[agent]["last_seen_ms"] = event.get("timestamp_ms")

        if "FAILED" in et or _severity(event) == "CRITICAL":
            health[agent]["failures"] += 1
            health[agent]["status"] = "DEGRADED"
        elif "BLOCKED" in et:
            health[agent]["blocked"] += 1
            if health[agent]["status"] != "DEGRADED":
                health[agent]["status"] = "BLOCKING"
        elif "STARTED" in et:
            if health[agent]["status"] not in {"DEGRADED", "BLOCKING"}:
                health[agent]["status"] = "ACTIVE"
        elif health[agent]["status"] == "IDLE":
            health[agent]["status"] = "OBSERVED"

    return health


def _render_agent_health(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Agent Health")

    health = _summarize_agent_health(events)

    rows = []
    for agent, data in health.items():
        rows.append(
            {
                "Agent": agent,
                "Status": data["status"],
                "Events": data["events"],
                "Failures": data["failures"],
                "Blocked": data["blocked"],
                "Last Seen": _fmt_ts(data["last_seen_ms"]) if data["last_seen_ms"] else "—",
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_graph_activity(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Execution Graph Activity")

    graph_events = _filter_events(events, event_types=GRAPH_EVENT_TYPES)

    if not graph_events:
        st.info("No execution graph activity captured yet.")
        return

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        _metric_card(
            "Graphs Started",
            len([e for e in graph_events if _event_type(e) == "EXECUTION_GRAPH_STARTED"]),
        )
    with c2:
        _metric_card(
            "Graphs Completed",
            len([e for e in graph_events if _event_type(e) == "EXECUTION_GRAPH_COMPLETED"]),
        )
    with c3:
        _metric_card(
            "Graphs Failed",
            len([e for e in graph_events if _event_type(e) == "EXECUTION_GRAPH_FAILED"]),
        )
    with c4:
        _metric_card(
            "Nodes Rolled Back",
            len([e for e in graph_events if _event_type(e) == "EXECUTION_GRAPH_NODE_ROLLED_BACK"]),
        )

    st.divider()

    for event in graph_events[:30]:
        _render_event_card(event)


def _render_containment_chains(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Containment Chains")

    containment_events = _filter_events(events, event_types=CONTAINMENT_EVENT_TYPES)

    if not containment_events:
        st.info("No containment chain events captured yet.")
        return

    for event in containment_events[:50]:
        _render_event_card(event)


def _render_verification_failures(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Verification Failures")

    failure_events = [
        e for e in events
        if _event_type(e) in {"VERIFICATION_FAILED", "CONTAINMENT_VERIFICATION_FAILED"}
        or "VERIFICATION_FAILED" in _event_type(e)
    ]

    if not failure_events:
        st.success("No verification failures captured.")
        return

    for event in failure_events[:50]:
        _render_event_card(event, expanded=True)


def _render_rollback_chains(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Rollback Chains")

    rollback_events = _filter_events(events, event_types=ROLLBACK_EVENT_TYPES)

    if not rollback_events:
        st.info("No rollback chain activity captured yet.")
        return

    for event in rollback_events[:50]:
        _render_event_card(event)


def _render_escalation_routing(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Escalation Routing")

    escalation_events = _filter_events(events, event_types=ESCALATION_EVENT_TYPES)

    if not escalation_events:
        st.info("No escalation routing events captured yet.")
        return

    for event in escalation_events[:50]:
        _render_event_card(event)


def _render_live_activity(events: List[Dict[str, Any]]) -> None:
    st.markdown("### Live Autonomous SOC Activity")

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        severity_filter = st.multiselect(
            "Severity",
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            key="multi_agent_severity_filter",
        )

    with c2:
        agent_filter = st.selectbox(
            "Agent",
            ["All"] + sorted({_agent_from_event(e) for e in events}),
            key="multi_agent_agent_filter",
        )

    with c3:
        contains = st.text_input(
            "Search events",
            "",
            key="multi_agent_event_search",
        )

    filtered = _filter_events(
        events,
        severity_filter=severity_filter,
        agent=agent_filter,
        contains=contains,
    )

    st.caption(f"Showing {len(filtered)} of {len(events)} recent events.")

    if not filtered:
        st.info("No matching activity.")
        return

    for event in filtered[:100]:
        _render_event_card(event)


def _render_test_launcher(storage: Optional[Any] = None) -> None:
    st.markdown("### Test Multi-Agent Flow")

    with st.expander("Run simulated containment graph", expanded=False):
        mailbox = st.text_input("Mailbox", "test@example.com", key="test_graph_mailbox")
        endpoint = st.text_input("Endpoint", "WIN-DEVICE-001", key="test_graph_endpoint")
        user = st.text_input("User", "test.user", key="test_graph_user")
        severity = st.selectbox(
            "Severity",
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            index=2,
            key="test_graph_severity",
        )
        export_control = st.checkbox(
            "Export-control case",
            value=False,
            key="test_graph_export_control",
        )

        if st.button("Run Test Containment Graph", use_container_width=True, key="run_test_containment_graph"):
            try:
                from core.agents.execution_graph_engine import ExecutionGraphEngine

                engine = ExecutionGraphEngine(storage=storage)

                context = {
                    "mailbox": mailbox,
                    "endpoint": endpoint,
                    "user": user,
                    "severity": severity,
                    "export_control": export_control,
                    "category": "EXPORT_CONTROL" if export_control else "CUI",
                    "source": "multi_agent_console_test",
                }

                result = engine.execute_containment_graph(context)

                if result.success:
                    st.success("Test containment graph completed.")
                else:
                    st.warning(f"Test containment graph finished with status: {result.status}")

                st.json(result.__dict__)

            except Exception as exc:
                st.error(f"Unable to run test graph: {exc}")


def render_multi_agent_console(storage: Optional[Any] = None) -> None:
    """
    Main UI entrypoint.

    Usage:
        from ui.copilot.multi_agent_console import render_multi_agent_console
        render_multi_agent_console(storage)
    """

    initialized = initialize_event_subscribers()

    st.markdown("# Multi-Agent SOC Console")
    st.caption(
        "Autonomous agent activity, execution graphs, containment chains, rollback visibility, and escalation routing."
    )

    if initialized:
        st.success("Live event subscriber fabric is active.")
    else:
        st.warning("Event subscriber fabric is not active yet. Console will render available in-memory telemetry only.")

    events = get_recent_events(limit=1000)
    stats = get_event_statistics()

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Total Events", stats.get("total_events", 0))
    with c2:
        st.metric("Critical", stats.get("critical_events", 0))
    with c3:
        st.metric("High", stats.get("high_events", 0))
    with c4:
        st.metric("Medium", stats.get("medium_events", 0))
    with c5:
        st.metric("Low", stats.get("low_events", 0))

    st.divider()

    tabs = st.tabs(
        [
            "Live Activity",
            "Agent Health",
            "Execution Graphs",
            "Containment",
            "Verification",
            "Rollback",
            "Escalation",
            "Test Runner",
        ]
    )

    with tabs[0]:
        _render_live_activity(events)

    with tabs[1]:
        _render_agent_health(events)

    with tabs[2]:
        _render_graph_activity(events)

    with tabs[3]:
        _render_containment_chains(events)

    with tabs[4]:
        _render_verification_failures(events)

    with tabs[5]:
        _render_rollback_chains(events)

    with tabs[6]:
        _render_escalation_routing(events)

    with tabs[7]:
        _render_test_launcher(storage)