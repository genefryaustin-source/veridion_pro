"""
ui/copilot/live_soc_stream.py

Real-time Autonomous SOC telemetry stream.

Provides:
- live agent telemetry
- live graph execution updates
- live rollback propagation
- live containment feeds
- live escalation streams
- websocket hub visibility
- autonomous SOC operational stream

Designed for:
- Streamlit live rendering
- websocket_hub integration
- event_subscribers integration
- future FastAPI/WebSocket expansion
"""

from __future__ import annotations

import time
import json
from collections import Counter
from typing import Any, Dict, List, Optional

import streamlit as st

try:
    from core.events.websocket_hub import (
        get_websocket_hub,
        get_websocket_hub_stats,
        get_websocket_hub_clients,
    )
except Exception:

    def get_websocket_hub():
        return None

    def get_websocket_hub_stats():
        return {}

    def get_websocket_hub_clients():
        return []


try:
    from core.events.event_subscribers import (
        initialize_event_subscribers,
        get_recent_events,
    )
except Exception:

    def initialize_event_subscribers():
        return False

    def get_recent_events(limit: int = 100, event_type: Optional[str] = None):
        return []


SEVERITY_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f97316",
    "MEDIUM": "#eab308",
    "LOW": "#22c55e",
    "INFO": "#3b82f6",
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


ESCALATION_EVENTS = {
    "SLA_ESCALATION_TRIGGERED",
    "EXECUTIVE_ESCALATION_TRIGGERED",
    "LEGAL_ROUTING_TRIGGERED",
    "EXPORT_CONTROL_ESCALATION_TRIGGERED",
    "PAGER_ORCHESTRATION_TRIGGERED",
}


AGENT_EVENTS = {
    "AGENT_EXECUTION_STARTED",
    "AGENT_EXECUTION_COMPLETED",
    "AGENT_EXECUTION_FAILED",
    "AGENT_EXECUTION_BLOCKED",
}


OPTIMIZER_EVENTS = {
    "OPTIMIZER_WORKFLOW_TUNED",
    "OPTIMIZER_ROLLBACK_REDUCTION_RECOMMENDED",
    "OPTIMIZER_CONFIDENCE_LEARNED",
    "OPTIMIZER_PATH_OPTIMIZED",
    "OPTIMIZER_ESCALATION_TUNED",
    "OPTIMIZER_VERIFICATION_TUNED",
}


def _event_type(event: Dict[str, Any]) -> str:
    return str(event.get("event_type") or "UNKNOWN_EVENT")


def _payload(event: Dict[str, Any]) -> Dict[str, Any]:
    payload = event.get("payload") or {}
    return payload if isinstance(payload, dict) else {"value": str(payload)}


def _severity(event: Dict[str, Any]) -> str:
    return str(event.get("severity") or "LOW").upper()


def _source(event: Dict[str, Any]) -> str:
    return str(event.get("source") or "unknown")


def _fmt_ts(ts_ms: Any) -> str:
    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ts_ms) / 1000),
        )
    except Exception:
        return "unknown-time"


def _event_matches(
    event: Dict[str, Any],
    category_filters: List[str],
    severity_filters: List[str],
    source_filter: str,
    search_term: str,
) -> bool:

    event_type = _event_type(event)
    severity = _severity(event)
    source = _source(event)

    if severity_filters and severity not in severity_filters:
        return False

    if source_filter and source_filter != "All":
        if source != source_filter:
            return False

    if category_filters:
        matched = False

        for category in category_filters:

            if category == "Graphs" and event_type in GRAPH_EVENTS:
                matched = True

            elif category == "Containment" and event_type in CONTAINMENT_EVENTS:
                matched = True

            elif category == "Rollback" and event_type in ROLLBACK_EVENTS:
                matched = True

            elif category == "Escalation" and event_type in ESCALATION_EVENTS:
                matched = True

            elif category == "Agents" and event_type in AGENT_EVENTS:
                matched = True

            elif category == "Optimizer" and event_type in OPTIMIZER_EVENTS:
                matched = True

        if not matched:
            return False

    if search_term:
        blob = json.dumps(event, default=str).lower()
        if search_term.lower() not in blob:
            return False

    return True


def _render_stream_event(event: Dict[str, Any]) -> None:

    event_type = _event_type(event)
    severity = _severity(event)
    source = _source(event)
    timestamp = _fmt_ts(event.get("timestamp_ms"))

    color = SEVERITY_COLORS.get(severity, "#64748b")

    payload = _payload(event)

    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color};
            background: rgba(148,163,184,0.08);
            border-radius: 10px;
            padding: 0.85rem;
            margin-bottom: 0.75rem;
        ">
            <div style="
                display:flex;
                justify-content:space-between;
                gap:1rem;
            ">
                <div style="font-weight:800;">
                    {event_type}
                </div>

                <div style="
                    color:{color};
                    font-weight:800;
                ">
                    {severity}
                </div>
            </div>

            <div style="
                margin-top:0.25rem;
                opacity:0.8;
                font-size:0.82rem;
            ">
                {timestamp} · {source}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Telemetry Payload", expanded=False):
        st.json(payload)


def _render_hub_stats() -> None:

    stats = get_websocket_hub_stats()

    st.markdown("### Streaming Fabric")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Clients",
            stats.get("total_clients", 0),
        )

    with c2:
        st.metric(
            "WebSockets",
            stats.get("websocket_clients", 0),
        )

    with c3:
        st.metric(
            "Broadcasts",
            stats.get("total_events_broadcast", 0),
        )

    with c4:
        st.metric(
            "Failures",
            stats.get("failed_broadcasts", 0),
        )

    with c5:
        st.metric(
            "Queue",
            stats.get("queue_size", 0),
        )


def _render_stream_metrics(events: List[Dict[str, Any]]) -> None:

    total = len(events)

    severity_counts = Counter(
        [_severity(e) for e in events]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Events", total)

    with c2:
        st.metric(
            "Critical",
            severity_counts.get("CRITICAL", 0),
        )

    with c3:
        st.metric(
            "High",
            severity_counts.get("HIGH", 0),
        )

    with c4:
        st.metric(
            "Medium",
            severity_counts.get("MEDIUM", 0),
        )

    with c5:
        st.metric(
            "Low",
            severity_counts.get("LOW", 0),
        )


def _render_client_visibility() -> None:

    clients = get_websocket_hub_clients()

    st.markdown("### Connected Streaming Clients")

    if not clients:
        st.info("No websocket/callback clients connected.")
        return

    rows = []

    for client in clients:

        rows.append({
            "Client ID": client.get("client_id"),
            "Type": client.get("client_type"),
            "Connected": _fmt_ts(client.get("connected_at_ms")),
            "Events": client.get("event_count"),
            "Last Event": _fmt_ts(client.get("last_event_ms"))
            if client.get("last_event_ms")
            else "—",
            "Last Error": client.get("last_error") or "—",
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )


def render_live_soc_stream(storage: Optional[Any] = None) -> None:
    """
    Main UI entrypoint.

    Usage:
        from ui.copilot.live_soc_stream import (
            render_live_soc_stream,
        )

        render_live_soc_stream(storage)
    """

    try:
        initialize_event_subscribers()
    except Exception:
        pass

    st.markdown("# Live Autonomous SOC Stream")

    st.caption(
        "Real-time operational telemetry across agents, "
        "execution graphs, rollback propagation, "
        "containment flows, escalation routing, "
        "and autonomous orchestration."
    )

    hub = get_websocket_hub()

    try:
        stats = hub.get_stats() if hub else {}
    except Exception:
        stats = {}

    _render_hub_stats()

    st.markdown("---")

    events = get_recent_events(limit=1000)

    _render_stream_metrics(events)

    st.markdown("---")

    # ========================================================
    # FILTERS
    # ========================================================

    st.markdown("### Stream Filters")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        category_filters = st.multiselect(
            "Categories",
            [
                "Graphs",
                "Containment",
                "Rollback",
                "Escalation",
                "Agents",
                "Optimizer",
            ],
            default=[
                "Graphs",
                "Containment",
                "Rollback",
                "Escalation",
            ],
            key="live_soc_categories",
        )

    with c2:

        severity_filters = st.multiselect(
            "Severity",
            [
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
            default=[
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
            ],
            key="live_soc_severity",
        )

    with c3:

        sources = sorted(set([
            _source(e)
            for e in events
        ]))

        source_filter = st.selectbox(
            "Source",
            ["All"] + sources,
            key="live_soc_source",
        )

    with c4:

        search_term = st.text_input(
            "Search",
            "",
            key="live_soc_search",
        )

    # ========================================================
    # FILTERED STREAM
    # ========================================================

    filtered_events = [
        e for e in events
        if _event_matches(
            e,
            category_filters,
            severity_filters,
            source_filter,
            search_term,
        )
    ]

    st.caption(
        f"Showing {len(filtered_events)} of {len(events)} telemetry events."
    )

    if not filtered_events:
        st.info("No telemetry matches current filters.")
    else:

        for event in filtered_events[:150]:
            _render_stream_event(event)

    st.markdown("---")

    _render_client_visibility()

    st.markdown("---")

    # ========================================================
    # STREAM CONTROL
    # ========================================================

    st.markdown("### Stream Controls")

    c1, c2, c3 = st.columns(3)

    with c1:

        auto_refresh = st.checkbox(
            "Enable Auto Refresh",
            value=True,
            key="live_soc_auto_refresh",
        )

    with c2:

        refresh_seconds = st.slider(
            "Refresh Interval (seconds)",
            min_value=1,
            max_value=30,
            value=5,
            key="live_soc_refresh_interval",
        )

    with c3:

        st.metric(
            "Hub Started",
            "YES" if stats.get("started") else "NO",
        )

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.rerun()