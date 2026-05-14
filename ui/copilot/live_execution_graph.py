"""
ui/copilot/live_execution_graph.py

Realtime Live Execution Graph for Veridion Pro / CUI GovCloud.

Shows:
- execution chains
- approvals
- rollbacks
- verifications
- containment flows
- escalation paths
- autonomous orchestration telemetry
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st


GRAPH_EVENT_TYPES = {
    "CONNECTOR_EXECUTION_STARTED",
    "CONNECTOR_EXECUTION_COMPLETED",
    "CONNECTOR_EXECUTION_FAILED",
    "AI_ACTION_REQUIRES_APPROVAL",
    "GOVERNANCE_ACTION_APPROVED",
    "GOVERNANCE_ACTION_REJECTED",
    "APPROVAL_REQUEST_CREATED",
    "APPROVAL_GRANTED",
    "APPROVAL_REJECTED",
    "VERIFICATION_STARTED",
    "VERIFICATION_COMPLETED",
    "VERIFICATION_FAILED",
    "ROLLBACK_REQUIRED",
    "ROLLBACK_TRIGGERED",
    "ROLLBACK_STARTED",
    "ROLLBACK_COMPLETED",
    "ROLLBACK_FAILED",
    "ENDPOINT_ISOLATED",
    "ENDPOINT_RELEASED",
    "CASE_ESCALATED",
    "AUTONOMY_BLOCKED",
    "BLAST_RADIUS_ANALYZED",
    "SAFETY_CHECK_COMPLETED",
}


SEVERITY_COLORS = {
    "LOW": "#22c55e",
    "MEDIUM": "#f59e0b",
    "HIGH": "#f97316",
    "CRITICAL": "#dc2626",
    "INFO": "#3b82f6",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def _safe_json(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value

    if not value:
        return {}

    try:
        return json.loads(value)
    except Exception:
        return {}


def _fmt_ms(ms: Any) -> str:
    try:
        value = int(ms or 0)
        if value <= 0:
            return ""
        return pd.to_datetime(value, unit="ms").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_live_execution_graph(storage: Any) -> None:
    st.markdown(
        """
        ## 🧠 Live Execution Graph

        Realtime autonomous orchestration graph showing actions,
        approvals, verifications, rollbacks, containment chains,
        and escalation paths.
        """
    )

    ledger = getattr(storage, "ledger", None)

    events = _load_graph_events(ledger)

    metrics = _build_metrics(events)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Graph Events", metrics["events"])
    c2.metric("Executions", metrics["executions"])
    c3.metric("Approvals", metrics["approvals"])
    c4.metric("Rollbacks", metrics["rollbacks"])
    c5.metric("Failures", metrics["failures"])

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        severity_filter = st.selectbox(
            "Severity",
            ["ALL", "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
            key="live_execution_graph_severity",
        )

    with col2:
        event_filter = st.selectbox(
            "Event Type",
            ["ALL"] + sorted(GRAPH_EVENT_TYPES),
            key="live_execution_graph_event_type",
        )

    with col3:
        search = st.text_input(
            "Search execution, case, connector, target",
            key="live_execution_graph_search",
        ).strip()

    filtered_events = _filter_events(
        events,
        severity_filter=severity_filter,
        event_filter=event_filter,
        search=search,
    )

    tab_graph, tab_timeline, tab_table, tab_raw = st.tabs(
        [
            "Graph",
            "Timeline",
            "Structured Events",
            "Raw",
        ]
    )

    with tab_graph:
        _render_graph(filtered_events)

    with tab_timeline:
        _render_timeline(filtered_events)

    with tab_table:
        _render_table(filtered_events)

    with tab_raw:
        st.json(filtered_events[:100])


# ---------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------

def _load_graph_events(ledger: Any) -> List[Dict[str, Any]]:
    if ledger is None:
        return []

    try:
        rows = (
            ledger.get_recent_events(limit=1000)
            if hasattr(ledger, "get_recent_events")
            else []
        )
    except Exception:
        rows = []

    events: List[Dict[str, Any]] = []

    for row in rows:
        event_type = _safe_str(row.get("event_type")).upper()

        if event_type not in GRAPH_EVENT_TYPES:
            continue

        details = (
            row.get("details")
            or row.get("details_json")
            or row.get("payload")
            or row.get("payload_json")
            or {}
        )

        details_obj = _safe_json(details)

        event = {
            **row,
            "event_type": event_type,
            "details_obj": details_obj,
            "execution_id": (
                row.get("execution_id")
                or details_obj.get("execution_id")
                or details_obj.get("response_id")
                or details_obj.get("job_id")
            ),
            "approval_id": (
                row.get("approval_id")
                or details_obj.get("approval_id")
            ),
            "rollback_id": (
                row.get("rollback_id")
                or details_obj.get("rollback_id")
            ),
            "verification_id": (
                row.get("verification_id")
                or details_obj.get("verification_id")
            ),
            "case_id": (
                row.get("case_id")
                or details_obj.get("case_id")
            ),
            "connector_id": (
                row.get("connector_id")
                or details_obj.get("connector_id")
            ),
            "target_id": (
                row.get("target_id")
                or details_obj.get("target_id")
                or details_obj.get("host_id")
                or details_obj.get("user_id")
            ),
            "severity": (
                row.get("severity")
                or details_obj.get("severity")
                or details_obj.get("risk_level")
                or "INFO"
            ),
            "timestamp_ms": (
                row.get("timestamp_ms")
                or row.get("created_at_ms")
                or details_obj.get("timestamp_ms")
                or details_obj.get("created_at_ms")
            ),
        }

        events.append(event)

    events.sort(
        key=lambda x: int(x.get("timestamp_ms") or 0),
        reverse=True,
    )

    return events


def _filter_events(
    events: List[Dict[str, Any]],
    *,
    severity_filter: str,
    event_filter: str,
    search: str,
) -> List[Dict[str, Any]]:
    results = []

    for event in events:
        severity = _safe_str(event.get("severity"), "INFO").upper()
        event_type = _safe_str(event.get("event_type")).upper()

        if severity_filter != "ALL" and severity != severity_filter:
            continue

        if event_filter != "ALL" and event_type != event_filter:
            continue

        if search:
            blob = json.dumps(event, default=str).lower()
            if search.lower() not in blob:
                continue

        results.append(event)

    return results


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(events: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "events": len(events),
        "executions": sum(
            1 for e in events if "EXECUTION" in _safe_str(e.get("event_type"))
        ),
        "approvals": sum(
            1
            for e in events
            if "APPROVAL" in _safe_str(e.get("event_type"))
            or "GOVERNANCE" in _safe_str(e.get("event_type"))
        ),
        "rollbacks": sum(
            1 for e in events if "ROLLBACK" in _safe_str(e.get("event_type"))
        ),
        "failures": sum(
            1
            for e in events
            if "FAILED" in _safe_str(e.get("event_type"))
            or "BLOCKED" in _safe_str(e.get("event_type"))
        ),
    }


# ---------------------------------------------------------------------
# GRAPH RENDER
# ---------------------------------------------------------------------

def _render_graph(events: List[Dict[str, Any]]) -> None:
    st.markdown("### 🔗 Orchestration Chain Graph")

    if not events:
        st.info("No execution graph telemetry available.")
        return

    chains = _build_chains(events)

    if not chains:
        st.info("No linked execution chains available.")
        return

    for chain_id, chain_events in list(chains.items())[:25]:
        _render_chain(chain_id, chain_events)


def _build_chains(events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    chains: Dict[str, List[Dict[str, Any]]] = {}

    for event in events:
        chain_id = (
            event.get("execution_id")
            or event.get("rollback_id")
            or event.get("approval_id")
            or event.get("case_id")
            or "unlinked"
        )

        chain_id = _safe_str(chain_id, "unlinked")

        chains.setdefault(chain_id, []).append(event)

    for chain_id in chains:
        chains[chain_id].sort(
            key=lambda x: int(x.get("timestamp_ms") or 0),
        )

    return chains


def _render_chain(chain_id: str, events: List[Dict[str, Any]]) -> None:
    latest = events[-1] if events else {}

    severity = _safe_str(latest.get("severity"), "INFO").upper()
    color = SEVERITY_COLORS.get(severity, "#64748b")

    with st.expander(
        f"🔗 Chain {chain_id} · {len(events)} event(s) · {severity}",
        expanded=False,
    ):
        st.markdown(
            f"""
            <div style="
                border-left: 6px solid {color};
                background: #0f172a;
                padding: 14px;
                border-radius: 12px;
                margin-bottom: 12px;
                color: white;
            ">
                <b>Chain ID:</b> {chain_id}<br>
                <b>Latest Event:</b> {latest.get("event_type")}<br>
                <b>Case:</b> {latest.get("case_id") or "-"}<br>
                <b>Connector:</b> {latest.get("connector_id") or "-"}<br>
                <b>Target:</b> {latest.get("target_id") or "-"}
            </div>
            """,
            unsafe_allow_html=True,
        )

        _render_chain_visual(events)

        rows = [_event_to_row(e) for e in events]
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            height=240,
        )


def _render_chain_visual(events: List[Dict[str, Any]]) -> None:
    parts = []

    for event in events:
        event_type = _safe_str(event.get("event_type"))
        severity = _safe_str(event.get("severity"), "INFO").upper()
        color = SEVERITY_COLORS.get(severity, "#64748b")

        icon = _event_icon(event_type)

        parts.append(
            f"""
            <div style="
                display:inline-block;
                background:{color};
                color:white;
                padding:8px 12px;
                border-radius:999px;
                font-size:12px;
                font-weight:800;
                margin:4px;
            ">
                {icon} {event_type}
            </div>
            """
        )

    arrow = """
    <span style="color:#94a3b8;font-weight:900;margin:0 4px;">→</span>
    """

    st.markdown(
        arrow.join(parts),
        unsafe_allow_html=True,
    )


def _event_icon(event_type: str) -> str:
    event_type = _safe_str(event_type).upper()

    if "APPROVAL" in event_type or "GOVERNANCE" in event_type:
        return "⚖️"

    if "ROLLBACK" in event_type:
        return "↩️"

    if "VERIFICATION" in event_type:
        return "✅"

    if "FAILED" in event_type or "BLOCKED" in event_type:
        return "🛑"

    if "ENDPOINT" in event_type or "CONTAIN" in event_type:
        return "🛡️"

    if "BLAST" in event_type:
        return "🌐"

    if "SAFETY" in event_type:
        return "🚧"

    return "📡"


# ---------------------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------------------

def _render_timeline(events: List[Dict[str, Any]]) -> None:
    st.markdown("### 🕒 Execution Timeline")

    if not events:
        st.info("No timeline telemetry available.")
        return

    for idx, event in enumerate(events[:150]):
        severity = _safe_str(event.get("severity"), "INFO").upper()
        color = SEVERITY_COLORS.get(severity, "#64748b")
        event_type = _safe_str(event.get("event_type"))
        icon = _event_icon(event_type)

        st.markdown(
            f"""
            <div style="
                border-left: 6px solid {color};
                background:#111827;
                padding:12px 14px;
                border-radius:10px;
                margin-bottom:10px;
                color:white;
            ">
                <div style="font-size:16px;font-weight:900;">
                    {icon} {event_type}
                </div>
                <div style="color:#cbd5e1;font-size:13px;line-height:1.6;">
                    <b>Time:</b> {_fmt_ms(event.get("timestamp_ms"))}<br>
                    <b>Execution:</b> {event.get("execution_id") or "-"}<br>
                    <b>Approval:</b> {event.get("approval_id") or "-"}<br>
                    <b>Rollback:</b> {event.get("rollback_id") or "-"}<br>
                    <b>Verification:</b> {event.get("verification_id") or "-"}<br>
                    <b>Case:</b> {event.get("case_id") or "-"}<br>
                    <b>Connector:</b> {event.get("connector_id") or "-"}<br>
                    <b>Target:</b> {event.get("target_id") or "-"}<br>
                    <b>Severity:</b> {severity}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------
# TABLE
# ---------------------------------------------------------------------

def _render_table(events: List[Dict[str, Any]]) -> None:
    st.markdown("### 📊 Structured Graph Events")

    if not events:
        st.info("No graph events available.")
        return

    rows = [_event_to_row(e) for e in events]

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=520,
    )


def _event_to_row(event: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "time": _fmt_ms(event.get("timestamp_ms")),
        "event_type": event.get("event_type"),
        "severity": event.get("severity"),
        "execution_id": event.get("execution_id"),
        "approval_id": event.get("approval_id"),
        "rollback_id": event.get("rollback_id"),
        "verification_id": event.get("verification_id"),
        "case_id": event.get("case_id"),
        "connector_id": event.get("connector_id"),
        "target_id": event.get("target_id"),
    }


render_execution_graph = render_live_execution_graph