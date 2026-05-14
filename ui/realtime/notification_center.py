from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import streamlit as st

from ui.realtime.live_sync import LiveSync


def _now_ms() -> int:
    return int(time.time() * 1000)


# ----------------------------------------------------------------------
# Severity Styling
# ----------------------------------------------------------------------

SEVERITY_ICONS = {
    "CRITICAL": "🚨",
    "HIGH": "⚠️",
    "MEDIUM": "🟡",
    "LOW": "🔵",
    "INFO": "ℹ️",
}

SEVERITY_COLORS = {
    "CRITICAL": "#ff4b4b",
    "HIGH": "#ff9800",
    "MEDIUM": "#fbc02d",
    "LOW": "#64b5f6",
    "INFO": "#90a4ae",
}


# ----------------------------------------------------------------------
# Notification Formatting
# ----------------------------------------------------------------------

def summarize_notification(
    event: Dict[str, Any],
) -> str:

    event_type = str(
        event.get("event_type") or "UNKNOWN"
    ).upper()

    payload = event.get("payload") or {}

    case_id = event.get("case_id")

    mapping = {

        "CASE_CREATED":
            f"Case created: {case_id}",

        "CASE_ASSIGNED":
            (
                f"Case {case_id} assigned to "
                f"{payload.get('analyst', 'analyst')}"
            ),

        "CASE_ESCALATED":
            (
                f"Case {case_id} escalated"
            ),

        "SLA_BREACHED":
            (
                f"SLA breached for case {case_id}"
            ),

        "APPROVAL_REQUESTED":
            (
                f"Approval requested for case {case_id}"
            ),

        "GRAPH_UPDATED":
            (
                f"Graph updated for case {case_id}"
            ),

        "CAMPAIGN_DETECTED":
            (
                f"Campaign detected for case {case_id}"
            ),

        "PLAYBOOK_EXECUTED":
            (
                f"Playbook executed for case {case_id}"
            ),

        "QUEUE_REFRESH_REQUIRED":
            (
                "Operational queue refresh required"
            ),
    }

    return mapping.get(
        event_type,
        event_type.replace("_", " ").title(),
    )


def format_timestamp(
    timestamp_ms: Optional[int],
) -> str:

    if not timestamp_ms:
        return "Unknown"

    age_seconds = int(
        (_now_ms() - int(timestamp_ms))
        / 1000
    )

    if age_seconds < 60:
        return f"{age_seconds}s ago"

    if age_seconds < 3600:
        return f"{int(age_seconds / 60)}m ago"

    if age_seconds < 86400:
        return f"{int(age_seconds / 3600)}h ago"

    return f"{int(age_seconds / 86400)}d ago"


# ----------------------------------------------------------------------
# Main Notification Center
# ----------------------------------------------------------------------

def render_notification_center(
    *,
    max_notifications: int = 25,
    show_controls: bool = True,
    title: str = "Operational Notifications",
) -> None:
    """
    Live operational notification center.

    Displays:
    - escalations
    - approvals
    - SLA breaches
    - campaign alerts
    - graph updates
    - analyst routing events
    """

    notifications = LiveSync.get_notifications(
        limit=max_notifications,
    )

    with st.container(border=True):

        col1, col2 = st.columns([8, 2])

        with col1:
            st.markdown(
                f"### 🔔 {title}"
            )

        with col2:

            if show_controls:

                if st.button(
                    "Clear",
                    key="clear_notifications_btn",
                    use_container_width=True,
                ):
                    LiveSync.clear_notifications()
                    st.rerun()

        if not notifications:

            st.info(
                "No operational notifications."
            )

            return

        critical = [
            n for n in notifications
            if str(
                n.get("severity") or ""
            ).upper() == "CRITICAL"
        ]

        high = [
            n for n in notifications
            if str(
                n.get("severity") or ""
            ).upper() == "HIGH"
        ]

        metric_cols = st.columns(4)

        with metric_cols[0]:
            st.metric(
                "Notifications",
                len(notifications),
            )

        with metric_cols[1]:
            st.metric(
                "Critical",
                len(critical),
            )

        with metric_cols[2]:
            st.metric(
                "High",
                len(high),
            )

        with metric_cols[3]:
            st.metric(
                "Live Channels",
                len(
                    LiveSync.get(
                        "channels",
                        []
                    )
                ),
            )

        st.divider()

        for idx, notification in enumerate(
            notifications
        ):

            render_notification_card(
                notification,
                idx=idx,
            )


# ----------------------------------------------------------------------
# Notification Card
# ----------------------------------------------------------------------

def render_notification_card(
    notification: Dict[str, Any],
    *,
    idx: int = 0,
) -> None:

    severity = str(
        notification.get("severity")
        or "INFO"
    ).upper()

    color = SEVERITY_COLORS.get(
        severity,
        "#90a4ae",
    )

    icon = SEVERITY_ICONS.get(
        severity,
        "ℹ️",
    )

    summary = summarize_notification(
        notification
    )

    timestamp = format_timestamp(
        notification.get(
            "timestamp_ms"
        )
    )

    event_type = notification.get(
        "event_type"
    )

    payload = notification.get(
        "payload",
        {}
    )

    case_id = notification.get(
        "case_id"
    )

    with st.container(border=True):

        top_cols = st.columns(
            [1, 7, 2]
        )

        with top_cols[0]:
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

        with top_cols[1]:

            st.markdown(
                f"""
                <div style="
                    font-weight:700;
                    color:{color};
                    font-size:16px;
                ">
                    {summary}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(
                f"{event_type} • {timestamp}"
            )

        with top_cols[2]:

            st.markdown(
                f"""
                <div style="
                    text-align:right;
                    font-weight:700;
                    color:{color};
                ">
                    {severity}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if case_id is not None:

            st.caption(
                f"Case: {case_id}"
            )

        # --------------------------------------------------------------
        # Payload Details
        # --------------------------------------------------------------

        details = build_notification_details(
            notification
        )

        if details:

            with st.expander(
                "Details",
                expanded=False,
            ):
                st.json(details)

        # --------------------------------------------------------------
        # Quick Actions
        # --------------------------------------------------------------

        render_notification_actions(
            notification,
            idx=idx,
        )


# ----------------------------------------------------------------------
# Notification Actions
# ----------------------------------------------------------------------

def render_notification_actions(
    notification: Dict[str, Any],
    *,
    idx: int = 0,
) -> None:

    event_type = str(
        notification.get("event_type") or ""
    ).upper()

    case_id = notification.get(
        "case_id"
    )

    cols = st.columns(4)

    with cols[0]:

        if case_id is not None:

            if st.button(
                "Open Case",
                key=f"notif_open_case_{idx}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_case_id"
                ] = case_id

                st.success(
                    f"Selected case {case_id}"
                )

    with cols[1]:

        if event_type in {
            "CASE_ESCALATED",
            "SLA_BREACHED",
        }:

            if st.button(
                "Acknowledge",
                key=f"notif_ack_{idx}",
                use_container_width=True,
            ):

                st.success(
                    "Notification acknowledged"
                )

    with cols[2]:

        if event_type == "APPROVAL_REQUESTED":

            if st.button(
                "Review",
                key=f"notif_review_{idx}",
                use_container_width=True,
            ):

                st.info(
                    "Approval review requested"
                )

    with cols[3]:

        if st.button(
            "Dismiss",
            key=f"notif_dismiss_{idx}",
            use_container_width=True,
        ):

            notifications = LiveSync.get(
                "notifications",
                []
            )

            event_id = notification.get(
                "event_id"
            )

            filtered = [
                n for n in notifications
                if n.get("event_id")
                != event_id
            ]

            LiveSync.set(
                "notifications",
                filtered,
            )

            st.rerun()


# ----------------------------------------------------------------------
# Helper Builders
# ----------------------------------------------------------------------

def build_notification_details(
    notification: Dict[str, Any],
) -> Dict[str, Any]:

    payload = notification.get(
        "payload",
        {}
    )

    return {
        "event_type":
            notification.get(
                "event_type"
            ),

        "severity":
            notification.get(
                "severity"
            ),

        "case_id":
            notification.get(
                "case_id"
            ),

        "tenant_id":
            notification.get(
                "tenant_id"
            ),

        "actor":
            notification.get(
                "actor"
            ),

        "source":
            notification.get(
                "source"
            ),

        "payload":
            payload,

        "timestamp_ms":
            notification.get(
                "timestamp_ms"
            ),
    }


# ----------------------------------------------------------------------
# Compact Banner Renderer
# ----------------------------------------------------------------------

def render_notification_banner(
    *,
    limit: int = 5,
) -> None:
    """
    Compact top-of-page operational banner.
    """

    notifications = LiveSync.get_notifications(
        limit=limit,
    )

    if not notifications:
        return

    critical = [
        n for n in notifications
        if str(
            n.get("severity")
            or ""
        ).upper()
        in ["CRITICAL", "HIGH"]
    ]

    if not critical:
        return

    latest = critical[0]

    severity = str(
        latest.get("severity")
        or "INFO"
    ).upper()

    color = SEVERITY_COLORS.get(
        severity,
        "#90a4ae",
    )

    summary = summarize_notification(
        latest
    )

    st.markdown(
        f"""
        <div style="
            background:{color};
            color:white;
            padding:12px;
            border-radius:10px;
            font-weight:700;
            margin-bottom:12px;
        ">
            {summary}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Sidebar Widget
# ----------------------------------------------------------------------

def render_notification_sidebar_widget(
    *,
    limit: int = 10,
) -> None:

    notifications = LiveSync.get_notifications(
        limit=limit,
    )

    st.sidebar.markdown(
        "## 🔔 Notifications"
    )

    if not notifications:

        st.sidebar.caption(
            "No active alerts"
        )

        return

    for notification in notifications:

        severity = str(
            notification.get(
                "severity"
            )
            or "INFO"
        ).upper()

        icon = SEVERITY_ICONS.get(
            severity,
            "ℹ️",
        )

        summary = summarize_notification(
            notification
        )

        st.sidebar.markdown(
            f"{icon} {summary}"
        )