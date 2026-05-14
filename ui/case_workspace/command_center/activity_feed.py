from __future__ import annotations

import time
from collections import Counter
from typing import Any, Dict, List, Optional

import streamlit as st

from ui.case_workspace.command_center.queue_state import QueueState


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _event_color(event_type: str) -> str:

    event_type = str(event_type or "").upper()

    mapping = {
        "CASE_ESCALATED": "#ff4b4b",
        "CASE_ASSIGNED": "#2196f3",
        "CASE_STATUS_CHANGED": "#9c27b0",
        "SLA_BREACH": "#ff0000",
        "SLA_WARNING": "#ff9800",
        "AI_ENRICHMENT_COMPLETED": "#00bcd4",
        "GRAPH_UPDATED": "#8bc34a",
        "APPROVAL_REQUESTED": "#ffc107",
        "APPROVAL_GRANTED": "#4caf50",
        "APPROVAL_REJECTED": "#f44336",
        "EVIDENCE_INGESTED": "#607d8b",
        "ENTITY_DETECTED": "#795548",
    }

    return mapping.get(event_type, "#999999")


def _event_icon(event_type: str) -> str:

    event_type = str(event_type or "").upper()

    mapping = {
        "CASE_ESCALATED": "🚨",
        "CASE_ASSIGNED": "👤",
        "CASE_STATUS_CHANGED": "🔄",
        "SLA_BREACH": "⏰",
        "SLA_WARNING": "⚠️",
        "AI_ENRICHMENT_COMPLETED": "🤖",
        "GRAPH_UPDATED": "🕸️",
        "APPROVAL_REQUESTED": "📝",
        "APPROVAL_GRANTED": "✅",
        "APPROVAL_REJECTED": "❌",
        "EVIDENCE_INGESTED": "📎",
        "ENTITY_DETECTED": "🧠",
    }

    return mapping.get(event_type, "•")


def _format_relative_time(timestamp_ms: Optional[int]) -> str:

    if not timestamp_ms:
        return "unknown"

    delta_sec = int((_now_ms() - timestamp_ms) / 1000)

    if delta_sec < 60:
        return f"{delta_sec}s ago"

    if delta_sec < 3600:
        return f"{delta_sec // 60}m ago"

    if delta_sec < 86400:
        return f"{delta_sec // 3600}h ago"

    return f"{delta_sec // 86400}d ago"


# ---------------------------------------------------------------------
# Activity Feed
# ---------------------------------------------------------------------

def render_activity_feed(
    *,
    ledger: Any,
    limit: int = 50,
    tenant_id: Optional[str] = None,
    auto_refresh: bool = True,
    compact: bool = False,
):
    """
    Operational SOC activity stream.

    Designed for future:
    - websocket updates
    - streaming events
    - live analyst collaboration
    - real-time SOC telemetry
    """

    QueueState.initialize()

    # -----------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------

    header_cols = st.columns([0.7, 0.15, 0.15])

    with header_cols[0]:

        st.subheader("Recent Investigation Activity")

    with header_cols[1]:

        auto_refresh = st.toggle(
            "Auto Refresh",
            value=auto_refresh,
            key="activity_feed_auto_refresh",
        )

    with header_cols[2]:

        if st.button(
            "Refresh",
            use_container_width=True,
            key="activity_feed_refresh",
        ):
            QueueState.mark_refreshed()
            st.rerun()

    # -----------------------------------------------------------------
    # Load Events
    # -----------------------------------------------------------------

    events = _load_activity_events(
        ledger=ledger,
        tenant_id=tenant_id,
        limit=limit,
    )

    # -----------------------------------------------------------------
    # Metrics Summary
    # -----------------------------------------------------------------

    render_activity_summary(events)

    st.divider()

    # -----------------------------------------------------------------
    # Feed Rendering
    # -----------------------------------------------------------------

    if not events:

        st.info("No recent investigation activity.")

        return

    for event in events:

        render_activity_event(
            event=event,
            compact=compact,
        )


# ---------------------------------------------------------------------
# Event Renderer
# ---------------------------------------------------------------------

def render_activity_event(
    event: Dict[str, Any],
    compact: bool = False,
):
    """
    Render a single operational activity event.
    """

    event_type = (
        event.get("event_type")
        or event.get("action")
        or "EVENT"
    )

    actor = (
        event.get("actor")
        or event.get("performed_by")
        or "system"
    )

    case_id = (
        event.get("case_id")
        or "UNKNOWN"
    )

    timestamp_ms = (
        event.get("timestamp_ms")
        or event.get("created_at_ms")
        or event.get("ts_ms")
    )

    details = (
        event.get("details")
        or event.get("details_json")
        or {}
    )

    if isinstance(details, str):
        details = {
            "raw": details
        }

    icon = _event_icon(event_type)
    color = _event_color(event_type)

    with st.container(border=True):

        cols = st.columns([0.08, 0.72, 0.20])

        # -------------------------------------------------------------
        # Icon
        # -------------------------------------------------------------

        with cols[0]:

            st.markdown(
                f"""
                <div style="
                    font-size:28px;
                    text-align:center;
                    padding-top:6px;
                ">
                    {icon}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------------------
        # Main Event
        # -------------------------------------------------------------

        with cols[1]:

            st.markdown(
                f"""
                <div style="
                    color:{color};
                    font-weight:700;
                    font-size:15px;
                ">
                    {event_type}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                **Case:** {case_id}
                """
            )

            st.markdown(
                f"""
                **Actor:** {actor}
                """
            )

            if details:

                if not compact:

                    with st.expander(
                        "Event Details",
                        expanded=False,
                    ):

                        for k, v in details.items():

                            st.markdown(
                                f"""
                                **{k}:** {v}
                                """
                            )

        # -------------------------------------------------------------
        # Time
        # -------------------------------------------------------------

        with cols[2]:

            st.caption(
                _format_relative_time(timestamp_ms)
            )

            if timestamp_ms:

                st.caption(
                    str(timestamp_ms)
                )


# ---------------------------------------------------------------------
# Summary Metrics
# ---------------------------------------------------------------------

def render_activity_summary(
    events: List[Dict[str, Any]],
):
    """
    Operational activity metrics.
    """

    counter = Counter()

    for event in events:

        event_type = (
            event.get("event_type")
            or event.get("action")
            or "EVENT"
        )

        counter[event_type] += 1

    metrics = [
        ("Escalations", counter.get("CASE_ESCALATED", 0)),
        ("Assignments", counter.get("CASE_ASSIGNED", 0)),
        ("SLA Breaches", counter.get("SLA_BREACH", 0)),
        ("AI Events", counter.get("AI_ENRICHMENT_COMPLETED", 0)),
        ("Graph Updates", counter.get("GRAPH_UPDATED", 0)),
    ]

    cols = st.columns(len(metrics))

    for idx, (label, value) in enumerate(metrics):

        with cols[idx]:

            st.metric(
                label,
                value,
            )


# ---------------------------------------------------------------------
# Event Loaders
# ---------------------------------------------------------------------

def _load_activity_events(
    *,
    ledger: Any,
    tenant_id: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    """
    Unified event aggregation layer.

    Pulls from:
    - case_events
    - custody_events
    - pipeline_events
    - graph events
    - audit logs

    Future:
    - websocket event broker
    - Kafka streams
    - Redis pub/sub
    """

    events = []

    # -----------------------------------------------------------------
    # Case Events
    # -----------------------------------------------------------------

    for method_name in [
        "get_recent_case_events",
        "list_recent_case_events",
        "fetch_recent_case_events",
        "get_case_events",
    ]:

        method = getattr(ledger, method_name, None)

        if callable(method):

            try:

                if tenant_id:

                    result = method(
                        tenant_id=tenant_id,
                        limit=limit,
                    )

                else:

                    result = method(limit=limit)

                if result:
                    events.extend(result)

                break

            except TypeError:

                try:

                    result = method(limit)

                    if result:
                        events.extend(result)

                    break

                except Exception:
                    pass

            except Exception:
                pass

    # -----------------------------------------------------------------
    # Custody Events
    # -----------------------------------------------------------------

    for method_name in [
        "get_recent_custody_events",
        "list_recent_custody_events",
    ]:

        method = getattr(ledger, method_name, None)

        if callable(method):

            try:

                result = method(limit=limit)

                if result:

                    for r in result:

                        r.setdefault(
                            "event_type",
                            "EVIDENCE_INGESTED",
                        )

                    events.extend(result)

                break

            except Exception:
                pass

    # -----------------------------------------------------------------
    # Pipeline Events
    # -----------------------------------------------------------------

    for method_name in [
        "get_recent_pipeline_events",
        "list_recent_pipeline_events",
    ]:

        method = getattr(ledger, method_name, None)

        if callable(method):

            try:

                result = method(limit=limit)

                if result:
                    events.extend(result)

                break

            except Exception:
                pass

    # -----------------------------------------------------------------
    # Normalize Timestamps
    # -----------------------------------------------------------------

    for event in events:

        if "timestamp_ms" not in event:

            for field in [
                "created_at_ms",
                "ts_ms",
                "timestamp",
            ]:

                if event.get(field):

                    event["timestamp_ms"] = _safe_int(
                        event.get(field)
                    )

                    break

    # -----------------------------------------------------------------
    # Sort Descending
    # -----------------------------------------------------------------

    events.sort(
        key=lambda x: _safe_int(
            x.get("timestamp_ms"),
            0,
        ),
        reverse=True,
    )

    # -----------------------------------------------------------------
    # Trim
    # -----------------------------------------------------------------

    return events[:limit]


# ---------------------------------------------------------------------
# Live Feed Placeholder
# ---------------------------------------------------------------------

def render_live_status_bar():
    """
    Placeholder for future websocket status.

    Future:
    - websocket health
    - event stream lag
    - connected analysts
    - active investigations
    """

    connected = QueueState.get(
        "websocket_connected",
        False,
    )

    live_mode = QueueState.get(
        "live_mode",
        False,
    )

    if connected:

        st.success(
            "Live event stream connected"
        )

    elif live_mode:

        st.warning(
            "Live mode enabled — websocket not connected"
        )

    else:

        st.caption(
            "Polling mode active"
        )