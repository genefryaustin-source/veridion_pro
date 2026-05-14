"""
ui/copilot/live_execution_stream.py

Realtime SOC Execution Stream for Veridion Pro / CUI GovCloud App.

Purpose:
- Live autonomous operations feed
- Governance approval stream
- Rollback telemetry
- Execution visibility
- SLA escalation visibility
- Analyst collaboration awareness
- Realtime orchestration timeline

Designed for:
- Command Center
- SOC War Room
- Governance Operations
- Distributed Operations Map
"""

from __future__ import annotations

import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

import pandas as pd
import streamlit as st

from core.events.websocket_hub import (
    get_websocket_hub,
)


# =============================================================================
# Constants
# =============================================================================

MAX_EVENTS = 500

SEVERITY_COLORS = {
    "INFO": "#2563eb",
    "LOW": "#0891b2",
    "MEDIUM": "#f59e0b",
    "HIGH": "#dc2626",
    "CRITICAL": "#7f1d1d",
}

EVENT_ICONS = {
    "APPROVAL_GRANTED": "✅",
    "APPROVAL_REJECTED": "❌",
    "GOVERNANCE_ACTION_APPROVED": "⚖️",
    "GOVERNANCE_ACTION_REJECTED": "🚫",
    "GOVERNANCE_OVERRIDE_APPROVED": "🔥",
    "EXECUTION_STARTED": "🚀",
    "EXECUTION_COMPLETED": "✅",
    "EXECUTION_FAILED": "❌",
    "ROLLBACK_TRIGGERED": "↩️",
    "ROLLBACK_STARTED": "↩️",
    "ROLLBACK_COMPLETED": "✅",
    "ROLLBACK_FAILED": "❌",
    "SLA_BREACH": "⏰",
    "CASE_ESCALATED": "🚨",
    "AI_ACTION_BLOCKED": "🛑",
    "POLICY_VIOLATION": "⚠️",
}


# =============================================================================
# Helpers
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def _fmt_ts(ms: Any) -> str:
    try:
        value = int(ms or 0)

        if value <= 0:
            return ""

        return pd.to_datetime(
            value,
            unit="ms",
        ).strftime("%Y-%m-%d %H:%M:%S")

    except Exception:
        return ""


def _severity_badge(severity: Any) -> str:

    sev = _safe_str(
        severity,
        "INFO",
    ).upper()

    color = SEVERITY_COLORS.get(
        sev,
        "#64748b",
    )

    return f"""
    <span style="
        background:{color};
        color:white;
        padding:4px 10px;
        border-radius:999px;
        font-size:11px;
        font-weight:800;
    ">
        {sev}
    </span>
    """


def _event_icon(event_type: str) -> str:
    return EVENT_ICONS.get(
        _safe_str(event_type).upper(),
        "📡",
    )


def _event_row(event: Dict[str, Any]) -> Dict[str, Any]:

    payload = event.get("payload") or {}

    return {
        "Time": _fmt_ts(
            event.get("created_at_ms")
        ),
        "Severity": _safe_str(
            event.get("severity"),
            "INFO",
        ).upper(),
        "Event": _safe_str(
            event.get("event_type")
        ),
        "Source": _safe_str(
            event.get("source")
        ),
        "Tenant": _safe_str(
            event.get("tenant_id")
        ),
        "Case": (
            payload.get("case_id")
            or ""
        ),
        "Approval": (
            payload.get("approval_id")
            or ""
        ),
        "Execution": (
            payload.get("execution_id")
            or ""
        ),
        "Message": (
            payload.get("message")
            or payload.get("reason")
            or ""
        ),
    }


# =============================================================================
# Session Event Buffer
# =============================================================================

def _get_buffer() -> Deque[Dict[str, Any]]:

    if "live_execution_stream_events" not in st.session_state:

        st.session_state[
            "live_execution_stream_events"
        ] = deque(
            maxlen=MAX_EVENTS
        )

    return st.session_state[
        "live_execution_stream_events"
    ]


# =============================================================================
# Event Subscription
# =============================================================================

def _subscribe_once() -> None:

    if st.session_state.get(
        "live_execution_stream_subscribed"
    ):
        return

    hub = get_websocket_hub()

    buffer = _get_buffer()

    def _callback(event: Any) -> None:

        try:

            if hasattr(event, "to_dict"):
                data = event.to_dict()

            elif isinstance(event, dict):
                data = event

            else:
                data = {
                    "event_type": str(event)
                }

            buffer.appendleft(data)

        except Exception:
            pass

    hub.subscribe_callback(
        "*",
        _callback,
    )

    st.session_state[
        "live_execution_stream_subscribed"
    ] = True


# =============================================================================
# Metrics
# =============================================================================

def _render_metrics(
    events: List[Dict[str, Any]],
) -> None:

    total = len(events)

    critical = sum(
        1
        for e in events
        if _safe_str(
            e.get("severity")
        ).upper() == "CRITICAL"
    )

    failed = sum(
        1
        for e in events
        if "FAILED" in _safe_str(
            e.get("event_type")
        ).upper()
    )

    approvals = sum(
        1
        for e in events
        if "APPROVAL" in _safe_str(
            e.get("event_type")
        ).upper()
    )

    executions = sum(
        1
        for e in events
        if "EXECUTION" in _safe_str(
            e.get("event_type")
        ).upper()
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Events",
        total,
    )

    c2.metric(
        "Critical",
        critical,
    )

    c3.metric(
        "Failures",
        failed,
    )

    c4.metric(
        "Approvals",
        approvals,
    )

    c5.metric(
        "Executions",
        executions,
    )


# =============================================================================
# Timeline
# =============================================================================

def _render_timeline(
    events: List[Dict[str, Any]],
) -> None:

    st.markdown(
        "### 📡 Live Operations Timeline"
    )

    if not events:

        st.info(
            "No realtime events received yet."
        )
        return

    for idx, event in enumerate(events[:150]):

        payload = event.get("payload") or {}

        severity = _safe_str(
            event.get("severity"),
            "INFO",
        ).upper()

        color = SEVERITY_COLORS.get(
            severity,
            "#64748b",
        )

        event_type = _safe_str(
            event.get("event_type")
        )

        icon = _event_icon(
            event_type
        )

        timestamp = _fmt_ts(
            event.get("created_at_ms")
        )

        tenant = _safe_str(
            event.get("tenant_id")
        )

        source = _safe_str(
            event.get("source")
        )

        case_id = payload.get("case_id")
        execution_id = payload.get(
            "execution_id"
        )
        approval_id = payload.get(
            "approval_id"
        )

        reason = (
            payload.get("message")
            or payload.get("reason")
            or ""
        )

        st.markdown(
            f"""
            <div style="
                border-left:6px solid {color};
                background:#0f172a;
                padding:14px 16px;
                border-radius:12px;
                margin-bottom:10px;
                box-shadow:0 4px 14px rgba(0,0,0,.25);
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:8px;
                ">

                    <div style="
                        font-size:16px;
                        font-weight:800;
                        color:white;
                    ">
                        {icon} {event_type}
                    </div>

                    <div>
                        {_severity_badge(severity)}
                    </div>

                </div>

                <div style="
                    color:#cbd5e1;
                    font-size:13px;
                    line-height:1.6;
                ">

                    <b>Time:</b> {timestamp}<br>
                    <b>Tenant:</b> {tenant}<br>
                    <b>Source:</b> {source}<br>

                    <b>Case:</b> {case_id or "-"}<br>
                    <b>Execution:</b> {execution_id or "-"}<br>
                    <b>Approval:</b> {approval_id or "-"}<br>

                    <b>Message:</b> {reason or "-"}

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# Table
# =============================================================================

def _render_table(
    events: List[Dict[str, Any]],
) -> None:

    st.markdown(
        "### 📊 Structured Event Feed"
    )

    if not events:

        st.info(
            "No events available."
        )
        return

    rows = [
        _event_row(e)
        for e in events
    ]

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        height=420,
        hide_index=True,
        key="live_execution_stream_table",
    )


# =============================================================================
# Filters
# =============================================================================

def _apply_filters(
    events: List[Dict[str, Any]],
    severity_filter: str,
    search: str,
) -> List[Dict[str, Any]]:

    results = []

    for event in events:

        severity = _safe_str(
            event.get("severity"),
            "INFO",
        ).upper()

        if (
            severity_filter != "ALL"
            and severity != severity_filter
        ):
            continue

        if search:

            blob = str(event).lower()

            if search.lower() not in blob:
                continue

        results.append(event)

    return results


# =============================================================================
# Main Render
# =============================================================================

def render_live_execution_stream(
    storage: Any = None,
) -> None:

    _subscribe_once()

    st.markdown(
        """
        <div style="
            padding:20px;
            border-radius:18px;
            background:linear-gradient(
                135deg,
                #111827,
                #1e293b,
                #334155
            );
            color:white;
            margin-bottom:18px;
        ">

            <div style="
                font-size:13px;
                font-weight:800;
                letter-spacing:.12em;
                opacity:.8;
            ">
                VERIDION PRO
            </div>

            <div style="
                font-size:30px;
                font-weight:900;
                margin-top:6px;
            ">
                📡 Live Execution Stream
            </div>

            <div style="
                margin-top:10px;
                opacity:.9;
                font-size:15px;
            ">
                Realtime autonomous orchestration,
                approvals, rollback telemetry,
                governance actions, and SOC activity feed.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    buffer = _get_buffer()

    events = list(buffer)

    # -----------------------------------------------------------------
    # Filters
    # -----------------------------------------------------------------

    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:

        severity_filter = st.selectbox(
            "Severity",
            [
                "ALL",
                "INFO",
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
            ],
            key="live_execution_stream_severity",
        )

    with c2:

        search = st.text_input(
            "Search events",
            key="live_execution_stream_search",
        ).strip()

    with c3:

        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=True,
            key="live_execution_stream_refresh",
        )

    filtered = _apply_filters(
        events,
        severity_filter,
        search,
    )

    # -----------------------------------------------------------------
    # Metrics
    # -----------------------------------------------------------------

    _render_metrics(filtered)

    # -----------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------

    tab_timeline, tab_table, tab_raw = st.tabs(
        [
            "Timeline",
            "Structured Feed",
            "Raw Events",
        ]
    )

    with tab_timeline:
        _render_timeline(filtered)

    with tab_table:
        _render_table(filtered)

    with tab_raw:

        st.markdown(
            "### 🧠 Raw Realtime Event Payloads"
        )

        st.json(filtered[:50])

    # -----------------------------------------------------------------
    # Auto Refresh
    # -----------------------------------------------------------------

    if auto_refresh:

        time.sleep(1.5)

        st.rerun()


# =============================================================================
# Backwards-Compatible Alias
# =============================================================================

render_execution_stream = (
    render_live_execution_stream
)