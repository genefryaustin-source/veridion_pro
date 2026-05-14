from __future__ import annotations

import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

import streamlit as st

from ui.realtime.live_sync import LiveSync, get_live_sync


def _now_ms() -> int:
    return int(time.time() * 1000)


SEVERITY_ICONS = {
    "CRITICAL": "🚨",
    "HIGH": "⚠️",
    "MEDIUM": "🟡",
    "LOW": "🔵",
    "INFO": "ℹ️",
    "ERROR": "❌",
}

EVENT_ICONS = {
    "CASE_CREATED": "🆕",
    "CASE_ASSIGNED": "👤",
    "CASE_ESCALATED": "🚨",
    "CASE_STATUS_CHANGED": "🔄",
    "CASE_CLOSED": "✅",
    "SLA_BREACHED": "⏰",
    "SLA_WARNING": "⚠️",
    "APPROVAL_REQUESTED": "📝",
    "APPROVAL_GRANTED": "✅",
    "APPROVAL_REJECTED": "❌",
    "GRAPH_UPDATED": "🕸️",
    "GRAPH_REFRESH_REQUIRED": "🕸️",
    "CAMPAIGN_DETECTED": "🎯",
    "PLAYBOOK_EXECUTED": "⚙️",
    "ENTITY_RESOLVED": "🧠",
    "QUEUE_REFRESH_REQUIRED": "🔁",
}


DEFAULT_EVENT_FILTERS = [
    "CASE_ESCALATED",
    "CASE_ASSIGNED",
    "SLA_BREACHED",
    "APPROVAL_REQUESTED",
    "GRAPH_UPDATED",
    "CAMPAIGN_DETECTED",
    "PLAYBOOK_EXECUTED",
    "ENTITY_RESOLVED",
]


def format_relative_time(timestamp_ms: Optional[int]) -> str:
    if not timestamp_ms:
        return "unknown"

    age = max(0, int((_now_ms() - int(timestamp_ms)) / 1000))

    if age < 60:
        return f"{age}s ago"

    if age < 3600:
        return f"{age // 60}m ago"

    if age < 86400:
        return f"{age // 3600}h ago"

    return f"{age // 86400}d ago"


def summarize_event(event: Dict[str, Any]) -> str:
    event_type = str(event.get("event_type") or "EVENT").upper()
    payload = event.get("payload") or {}
    case_id = event.get("case_id")
    actor = event.get("actor") or "system"

    if event_type == "CASE_ASSIGNED":
        return f"Case {case_id} assigned to {payload.get('analyst') or payload.get('assigned_to') or actor}"

    if event_type == "CASE_ESCALATED":
        return f"Case {case_id} escalated"

    if event_type == "SLA_BREACHED":
        return f"SLA breached for case {case_id}"

    if event_type == "APPROVAL_REQUESTED":
        return f"Approval requested for case {case_id}"

    if event_type == "GRAPH_UPDATED":
        return f"Graph updated for case {case_id}"

    if event_type == "CAMPAIGN_DETECTED":
        return f"Campaign detected: {payload.get('campaign_id') or case_id}"

    if event_type == "PLAYBOOK_EXECUTED":
        return f"Playbook executed: {payload.get('playbook_name') or 'Investigation playbook'}"

    if event_type == "ENTITY_RESOLVED":
        return f"Entity resolution updated"

    if event_type == "QUEUE_REFRESH_REQUIRED":
        return "Investigation queue refresh required"

    return event_type.replace("_", " ").title()


def render_live_activity_stream(
    *,
    user_id: str = "unknown",
    tenant_id: Optional[str] = None,
    title: str = "Live Operational Activity",
    limit: int = 100,
    compact: bool = False,
    auto_poll: bool = True,
    show_filters: bool = True,
    show_metrics: bool = True,
    default_group_by: str = "None",
) -> None:
    """
    Live operational event stream.

    Consumes LiveSync.poll_events() now and remains websocket-ready later.
    """

    sync = get_live_sync(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    if auto_poll:
        sync.poll_events(limit=limit)

    events = LiveSync.get_notifications(limit=limit)

    with st.container(border=True):
        header_cols = st.columns([0.72, 0.14, 0.14])

        with header_cols[0]:
            st.markdown(f"### 📡 {title}")
            LiveSync.render_live_status()

        with header_cols[1]:
            if st.button("Poll", key="live_activity_poll_btn", use_container_width=True):
                sync.poll_events(limit=limit)
                st.rerun()

        with header_cols[2]:
            if st.button("Clear", key="live_activity_clear_btn", use_container_width=True):
                LiveSync.clear_notifications()
                st.rerun()

        if show_filters:
            filtered_events, group_by = render_activity_filters(
                events=events,
                default_group_by=default_group_by,
            )
        else:
            filtered_events = events
            group_by = default_group_by

        if show_metrics:
            render_activity_metrics(filtered_events)

        st.divider()

        if not filtered_events:
            st.info("No live operational activity.")
            return

        if group_by and group_by != "None":
            grouped = group_activity_events(
                events=filtered_events,
                group_by=group_by,
            )

            for group_name, group_events in grouped.items():
                with st.expander(
                    f"{group_name} ({len(group_events)})",
                    expanded=True,
                ):
                    for event in group_events:
                        render_activity_event(event, compact=compact)
        else:
            for event in filtered_events:
                render_activity_event(event, compact=compact)


def render_activity_filters(
    *,
    events: List[Dict[str, Any]],
    default_group_by: str = "None",
) -> tuple[List[Dict[str, Any]], str]:
    st.markdown("#### Filters")

    available_event_types = sorted(
        list(
            set(
                str(e.get("event_type") or "EVENT").upper()
                for e in events
            )
        )
    )

    if not available_event_types:
        available_event_types = DEFAULT_EVENT_FILTERS

    row1 = st.columns(4)

    with row1[0]:
        severity_filter = st.multiselect(
            "Severity",
            options=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "ERROR"],
            default=[],
            key="live_activity_severity_filter",
        )

    with row1[1]:
        event_type_filter = st.multiselect(
            "Event Types",
            options=available_event_types,
            default=[],
            key="live_activity_event_type_filter",
        )

    with row1[2]:
        case_filter = st.text_input(
            "Case ID",
            value="",
            key="live_activity_case_filter",
        )

    with row1[3]:
        group_by = st.selectbox(
            "Group By",
            options=[
                "None",
                "Case",
                "Tenant",
                "Campaign",
                "Analyst",
                "Severity",
                "Event Type",
            ],
            index=[
                "None",
                "Case",
                "Tenant",
                "Campaign",
                "Analyst",
                "Severity",
                "Event Type",
            ].index(default_group_by)
            if default_group_by in [
                "None",
                "Case",
                "Tenant",
                "Campaign",
                "Analyst",
                "Severity",
                "Event Type",
            ]
            else 0,
            key="live_activity_group_by",
        )

    row2 = st.columns(6)

    quick_filters = {
        "Critical Only": lambda e: str(e.get("severity") or "").upper() == "CRITICAL",
        "Escalations": lambda e: str(e.get("event_type") or "").upper() == "CASE_ESCALATED",
        "Approvals": lambda e: str(e.get("event_type") or "").upper().startswith("APPROVAL"),
        "Campaigns": lambda e: str(e.get("event_type") or "").upper() == "CAMPAIGN_DETECTED",
        "Graph": lambda e: "GRAPH" in str(e.get("event_type") or "").upper(),
        "Playbooks": lambda e: str(e.get("event_type") or "").upper() == "PLAYBOOK_EXECUTED",
    }

    active_quick = []

    for idx, label in enumerate(quick_filters.keys()):
        with row2[idx]:
            enabled = st.toggle(
                label,
                value=False,
                key=f"live_activity_quick_{label}",
            )

            if enabled:
                active_quick.append(label)

    filtered = []

    for event in events:
        event_type = str(event.get("event_type") or "").upper()
        severity = str(event.get("severity") or "").upper()
        case_id = str(event.get("case_id") or "")

        if severity_filter and severity not in severity_filter:
            continue

        if event_type_filter and event_type not in event_type_filter:
            continue

        if case_filter and case_filter.lower().strip() not in case_id.lower():
            continue

        if active_quick:
            if not any(quick_filters[label](event) for label in active_quick):
                continue

        filtered.append(event)

    return filtered, group_by


def render_activity_metrics(events: List[Dict[str, Any]]) -> None:
    counter = Counter(
        str(e.get("event_type") or "EVENT").upper()
        for e in events
    )

    severity_counter = Counter(
        str(e.get("severity") or "INFO").upper()
        for e in events
    )

    metrics = [
        ("Events", len(events)),
        ("Escalations", counter.get("CASE_ESCALATED", 0)),
        ("Breaches", counter.get("SLA_BREACHED", 0)),
        ("Campaigns", counter.get("CAMPAIGN_DETECTED", 0)),
        ("Playbooks", counter.get("PLAYBOOK_EXECUTED", 0)),
        ("Critical", severity_counter.get("CRITICAL", 0)),
    ]

    cols = st.columns(len(metrics))

    for idx, (label, value) in enumerate(metrics):
        with cols[idx]:
            st.metric(label, value)


def group_activity_events(
    *,
    events: List[Dict[str, Any]],
    group_by: str,
) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for event in events:
        payload = event.get("payload") or {}

        if group_by == "Case":
            key = f"Case {event.get('case_id') or 'UNKNOWN'}"

        elif group_by == "Tenant":
            key = f"Tenant {event.get('tenant_id') or 'UNKNOWN'}"

        elif group_by == "Campaign":
            key = f"Campaign {payload.get('campaign_id') or 'UNKNOWN'}"

        elif group_by == "Analyst":
            key = f"Analyst {event.get('actor') or payload.get('analyst') or 'UNKNOWN'}"

        elif group_by == "Severity":
            key = f"Severity {event.get('severity') or 'INFO'}"

        elif group_by == "Event Type":
            key = str(event.get("event_type") or "EVENT")

        else:
            key = "Activity"

        grouped[key].append(event)

    return dict(grouped)


def render_activity_event(
    event: Dict[str, Any],
    *,
    compact: bool = False,
) -> None:
    event_type = str(event.get("event_type") or "EVENT").upper()
    severity = str(event.get("severity") or "INFO").upper()
    payload = event.get("payload") or {}

    icon = EVENT_ICONS.get(event_type) or SEVERITY_ICONS.get(severity) or "•"
    timestamp = format_relative_time(event.get("timestamp_ms"))
    summary = summarize_event(event)

    case_id = event.get("case_id")
    tenant_id = event.get("tenant_id")
    actor = event.get("actor")
    source = event.get("source")
    campaign_id = payload.get("campaign_id")

    with st.container(border=True):
        cols = st.columns([0.08, 0.67, 0.25])

        with cols[0]:
            st.markdown(
                f"""
                <div style="font-size:28px;text-align:center;padding-top:5px;">
                    {icon}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with cols[1]:
            st.markdown(f"**{summary}**")
            st.caption(f"{event_type} • {severity} • {timestamp}")

            context = []

            if case_id is not None:
                context.append(f"Case: `{case_id}`")

            if tenant_id:
                context.append(f"Tenant: `{tenant_id}`")

            if actor:
                context.append(f"Actor: `{actor}`")

            if campaign_id:
                context.append(f"Campaign: `{campaign_id}`")

            if context:
                st.markdown(" • ".join(context))

        with cols[2]:
            render_event_badge(severity)
            if source:
                st.caption(f"Source: {source}")

        if not compact:
            render_event_context(event)

            with st.expander("Raw Event", expanded=False):
                st.json(event)


def render_event_badge(severity: str) -> None:
    severity = str(severity or "INFO").upper()

    colors = {
        "CRITICAL": "#ff4b4b",
        "HIGH": "#ff9800",
        "MEDIUM": "#fbc02d",
        "LOW": "#64b5f6",
        "INFO": "#90a4ae",
        "ERROR": "#d32f2f",
    }

    color = colors.get(severity, "#90a4ae")

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            background:{color};
            color:white;
            padding:4px 10px;
            border-radius:12px;
            font-weight:700;
            font-size:12px;
        ">
            {severity}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_event_context(event: Dict[str, Any]) -> None:
    payload = event.get("payload") or {}
    event_type = str(event.get("event_type") or "").upper()

    if event_type == "CASE_ASSIGNED":
        analyst = payload.get("analyst") or payload.get("assigned_to")
        if analyst:
            st.info(f"Assigned analyst: {analyst}")

    elif event_type == "CASE_ESCALATED":
        reason = payload.get("reason")
        escalation_level = payload.get("escalation_level")
        st.warning(
            f"Escalation level: {escalation_level or 'N/A'}"
            + (f" • Reason: {reason}" if reason else "")
        )

    elif event_type == "CAMPAIGN_DETECTED":
        st.warning(
            f"Campaign detected: {payload.get('campaign_id') or 'UNKNOWN'}"
        )

    elif event_type == "APPROVAL_REQUESTED":
        st.info(
            f"Approval type: {payload.get('approval_type') or 'UNKNOWN'}"
        )

    elif event_type == "PLAYBOOK_EXECUTED":
        st.success(
            f"Playbook: {payload.get('playbook_name') or 'UNKNOWN'}"
        )

    linked_cases = payload.get("linked_cases") or []
    if linked_cases:
        with st.expander("Linked Cases", expanded=False):
            st.json(linked_cases)

    related_entities = payload.get("related_entities") or payload.get("entities") or []
    if related_entities:
        st.markdown("**Related Entities**")
        entity_html = ""

        for entity in related_entities[:20]:
            entity_html += f"""
            <span style="
                display:inline-block;
                background:#263238;
                color:white;
                padding:4px 9px;
                margin:3px;
                border-radius:10px;
                font-size:12px;
            ">
                {entity}
            </span>
            """

        st.markdown(entity_html, unsafe_allow_html=True)