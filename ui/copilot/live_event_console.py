"""
ui/copilot/live_event_console.py

Real-time operational telemetry console.

Provides:
- Live SOC event feed
- Governance telemetry
- Agent coordination visibility
- Containment replay
- Execution replay
- Operational event filtering
- Severity filtering
- Multi-agent observability

This is the foundation for:
AUTONOMOUS CYBER OPERATIONS VISIBILITY
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import streamlit as st


from core.events.event_subscribers import (
    initialize_event_subscribers,
    get_recent_events,
    get_event_statistics,
)


# ============================================================
# UI HELPERS
# ============================================================

SEVERITY_COLORS = {
    "CRITICAL": "#ff4b4b",
    "HIGH": "#ff9800",
    "MEDIUM": "#ffd54f",
    "LOW": "#4caf50",
}


EVENT_ICONS = {
    "EXECUTION_STARTED": "▶️",
    "EXECUTION_COMPLETED": "✅",
    "EXECUTION_FAILED": "❌",
    "ROLLBACK_TRIGGERED": "↩️",
    "AUTONOMY_POLICY_BLOCK": "🛡️",
    "CASE_ESCALATED": "🚨",
    "CONTAINMENT_EXECUTED": "🔒",
    "VERIFICATION_FAILED": "⚠️",
    "LOCKDOWN_ACTIVATED": "🚨",
    "ALERT_CREATED": "📣",
    "EVIDENCE_CREATED": "📁",
    "AGENT_ACTION": "🤖",
    "SYSTEM_ERROR": "💥",
}


def _format_ts(ts_ms: int) -> str:

    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(ts_ms / 1000),
        )
    except Exception:
        return str(ts_ms)


def render_event_card(event: Dict[str, Any]) -> None:

    severity = str(event.get("severity", "LOW")).upper()
    event_type = str(event.get("event_type", "UNKNOWN"))
    source = str(event.get("source", "unknown"))
    payload = event.get("payload", {})
    ts_ms = int(event.get("timestamp_ms", 0))

    color = SEVERITY_COLORS.get(severity, "#999999")
    icon = EVENT_ICONS.get(event_type, "📌")

    st.markdown(
        f"""
        <div style="
            border-left: 6px solid {color};
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            background-color: rgba(255,255,255,0.03);
        ">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div>
                <span style="font-size:20px;">{icon}</span>
                <span style="
                    font-weight:700;
                    margin-left:8px;
                ">
                    {event_type}
                </span>
            </div>

            <div style="
                color:{color};
                font-weight:700;
            ">
                {severity}
            </div>

        </div>

        <div style="
            margin-top:8px;
            font-size:13px;
            opacity:0.8;
        ">
            {_format_ts(ts_ms)} · {source}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Payload", expanded=False):
        st.json(payload)


# ============================================================
# MAIN CONSOLE
# ============================================================

def render_live_event_console() -> None:

    initialize_event_subscribers()

    st.markdown("# Live Event Console")

    st.caption(
        "Real-time operational telemetry, governance events, and autonomous execution visibility."
    )

    stats = get_event_statistics()

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Total Events", stats["total_events"])

    with c2:
        st.metric("Critical", stats["critical_events"])

    with c3:
        st.metric("High", stats["high_events"])

    with c4:
        st.metric("Medium", stats["medium_events"])

    with c5:
        st.metric("Low", stats["low_events"])

    st.divider()

    # ============================================================
    # FILTERS
    # ============================================================

    c1, c2 = st.columns(2)

    with c1:
        severity_filter = st.multiselect(
            "Severity Filter",
            ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        )

    with c2:
        event_type_filter = st.text_input(
            "Event Type Contains",
            "",
        )

    limit = st.slider(
        "Max Events",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
    )

    st.divider()

    # ============================================================
    # EVENT FEED
    # ============================================================

    events = get_recent_events(limit=limit)

    filtered = []

    for event in events:

        severity = str(event.get("severity", "LOW")).upper()
        event_type = str(event.get("event_type", ""))

        if severity not in severity_filter:
            continue

        if event_type_filter:
            if event_type_filter.lower() not in event_type.lower():
                continue

        filtered.append(event)

    st.markdown(f"### Live Feed ({len(filtered)} events)")

    if not filtered:
        st.info("No matching events.")
        return

    for event in filtered:
        render_event_card(event)