from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import streamlit as st

from ui.case_workspace.command_center.queue_state import QueueState


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_upper(value: Any) -> str:
    return str(value or "").upper().strip()


def _severity_color(severity: str) -> str:

    severity = _safe_upper(severity)

    colors = {
        "CRITICAL": "#ff4b4b",
        "HIGH": "#ff8c42",
        "MEDIUM": "#ffd166",
        "LOW": "#4caf50",
        "UNKNOWN": "#999999",
    }

    return colors.get(severity, "#999999")


def _status_color(status: str) -> str:

    status = _safe_upper(status)

    colors = {
        "NEW": "#2196f3",
        "TRIAGE": "#03a9f4",
        "INVESTIGATING": "#9c27b0",
        "ESCALATED": "#ff4b4b",
        "CONTAINED": "#ff9800",
        "RESOLVED": "#4caf50",
        "CLOSED": "#607d8b",
    }

    return colors.get(status, "#999999")


def _render_badge(label: str, color: str):

    st.markdown(
        f"""
        <div style="
            display:inline-block;
            padding:4px 10px;
            margin-right:6px;
            border-radius:12px;
            background:{color};
            color:white;
            font-size:12px;
            font-weight:600;
        ">
            {label}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_minutes(minutes: Optional[float]) -> str:

    if minutes is None:
        return "N/A"

    if minutes < 0:
        return f"{abs(int(minutes))}m overdue"

    if minutes < 60:
        return f"{int(minutes)}m"

    hours = minutes / 60

    return f"{hours:.1f}h"


# ---------------------------------------------------------------------
# Main Case Card
# ---------------------------------------------------------------------

def render_case_card(
    case: Dict[str, Any],
    *,
    ledger: Any,
    assignment_service: Any = None,
    escalation_service: Any = None,
    state_machine: Any = None,
    approval_service: Any = None,
    analysts: Optional[List[str]] = None,
    current_user: str = "system",
):
    """
    Operational SOC case card.

    This component is designed to become:
    - websocket compatible
    - real-time refreshable
    - operationally actionable
    - SLA aware
    - escalation aware
    - graph intelligence aware
    """

    analysts = analysts or []

    case_id = case.get("case_id") or case.get("id")
    title = case.get("title") or "Untitled Investigation"

    severity = (
        case.get("severity")
        or case.get("priority")
        or "UNKNOWN"
    )

    status = case.get("status") or "NEW"

    tenant = (
        case.get("tenant_name")
        or case.get("tenant_id")
        or "UNKNOWN"
    )

    escalation_level = int(case.get("escalation_level") or 0)

    graph_risk = int(case.get("graph_risk_score") or 0)

    cross_case_links = int(case.get("cross_case_links") or 0)

    ai_summary = case.get("ai_summary") or ""

    entities = case.get("entities") or []

    assigned_to = (
        case.get("assigned_to")
        or case.get("owner")
    )

    sla_due_at_ms = (
        case.get("sla_due_at_ms")
        or case.get("sla_deadline_ms")
    )

    minutes_remaining = None

    if sla_due_at_ms:
        minutes_remaining = (
            int(sla_due_at_ms) - _now_ms()
        ) / 60000

    is_breached = (
        minutes_remaining is not None
        and minutes_remaining < 0
    )

    is_near_breach = (
        minutes_remaining is not None
        and 0 <= minutes_remaining <= 15
    )

    # -----------------------------------------------------------------
    # Card Container
    # -----------------------------------------------------------------

    with st.container(border=True):

        # -------------------------------------------------------------
        # Header
        # -------------------------------------------------------------

        top_col1, top_col2 = st.columns([0.08, 0.92])

        with top_col1:

            selected = st.checkbox(
                "",
                key=f"select_case_{case_id}",
                value=case_id in QueueState.get_selected_cases(),
            )

            if selected:
                QueueState.add_selected_case(case_id)
            else:
                QueueState.remove_selected_case(case_id)

        with top_col2:

            st.markdown(
                f"""
                ### {title}

                <div style='font-size:13px;color:#999;'>
                    {case_id}
                </div>
                """,
                unsafe_allow_html=True,
            )

            _render_badge(
                severity,
                _severity_color(severity),
            )

            _render_badge(
                status,
                _status_color(status),
            )

            if is_breached:
                _render_badge(
                    "SLA BREACHED",
                    "#ff0000",
                )

            elif is_near_breach:
                _render_badge(
                    "NEAR BREACH",
                    "#ff9800",
                )

            if escalation_level > 0:
                _render_badge(
                    f"ESC L{escalation_level}",
                    "#9c27b0",
                )

            _render_badge(
                f"TENANT: {tenant}",
                "#455a64",
            )

        st.divider()

        # -------------------------------------------------------------
        # Operational Metrics
        # -------------------------------------------------------------

        metric_cols = st.columns(5)

        with metric_cols[0]:
            st.metric(
                "Graph Risk",
                graph_risk,
            )

        with metric_cols[1]:
            st.metric(
                "Cross Links",
                cross_case_links,
            )

        with metric_cols[2]:
            st.metric(
                "Escalation",
                escalation_level,
            )

        with metric_cols[3]:
            st.metric(
                "Assigned",
                assigned_to or "UNASSIGNED",
            )

        with metric_cols[4]:
            st.metric(
                "SLA",
                _format_minutes(minutes_remaining),
            )

        # -------------------------------------------------------------
        # Assignment Controls
        # -------------------------------------------------------------

        st.subheader("Assignment")

        assign_cols = st.columns([0.7, 0.3])

        with assign_cols[0]:

            selected_analyst = st.selectbox(
                "Assign Analyst",
                options=[""] + analysts,
                index=0,
                key=f"assign_dropdown_{case_id}",
            )

        with assign_cols[1]:

            if st.button(
                "Assign",
                key=f"assign_btn_{case_id}",
                use_container_width=True,
            ):

                try:

                    if assignment_service:

                        assignment_service.assign_case(
                            case_id=case_id,
                            analyst_id=selected_analyst,
                            assigned_by=current_user,
                            reason="SOC Command Center assignment",
                        )

                    if hasattr(ledger, "add_case_event"):

                        ledger.add_case_event(
                            case_id=case_id,
                            event_type="CASE_ASSIGNED",
                            actor=current_user,
                            details={
                                "assigned_to": selected_analyst,
                                "source": "case_card",
                            },
                        )

                    st.success(
                        f"Assigned to {selected_analyst}"
                    )

                except Exception as exc:
                    st.error(str(exc))

        # -------------------------------------------------------------
        # State Transitions
        # -------------------------------------------------------------

        st.subheader("Workflow")

        workflow_cols = st.columns(6)

        transitions = [
            "TRIAGE",
            "INVESTIGATING",
            "ESCALATED",
            "CONTAINED",
            "RESOLVED",
            "CLOSED",
        ]

        for idx, next_state in enumerate(transitions):

            with workflow_cols[idx]:

                if st.button(
                    next_state,
                    key=f"transition_{case_id}_{next_state}",
                    use_container_width=True,
                ):

                    try:

                        if state_machine:

                            state_machine.transition(
                                case_id=case_id,
                                to_state=next_state,
                                actor=current_user,
                                reason="Command Center transition",
                            )

                        if hasattr(ledger, "add_case_event"):

                            ledger.add_case_event(
                                case_id=case_id,
                                event_type="CASE_STATUS_CHANGED",
                                actor=current_user,
                                details={
                                    "to_state": next_state,
                                    "source": "case_card",
                                },
                            )

                        st.success(
                            f"Transitioned to {next_state}"
                        )

                    except Exception as exc:
                        st.error(str(exc))

        # -------------------------------------------------------------
        # Escalation Controls
        # -------------------------------------------------------------

        st.subheader("Escalation")

        esc_cols = st.columns([0.7, 0.3])

        with esc_cols[0]:

            st.markdown(
                f"""
                **Escalation Level:** {escalation_level}
                """
            )

        with esc_cols[1]:

            if st.button(
                "Escalate",
                key=f"escalate_{case_id}",
                use_container_width=True,
            ):

                try:

                    if escalation_service:

                        escalation_service.auto_escalate_case(
                            case_id=case_id,
                            actor=current_user,
                            reason="Manual escalation from SOC Command Center",
                        )

                    if hasattr(ledger, "add_case_event"):

                        ledger.add_case_event(
                            case_id=case_id,
                            event_type="CASE_ESCALATED",
                            actor=current_user,
                            details={
                                "source": "case_card",
                            },
                        )

                    st.success("Case escalated")

                except Exception as exc:
                    st.error(str(exc))

        # -------------------------------------------------------------
        # AI / Graph Intelligence
        # -------------------------------------------------------------

        with st.expander(
            "AI / Graph Intelligence",
            expanded=False,
        ):

            intel_cols = st.columns(3)

            with intel_cols[0]:
                st.metric(
                    "Graph Risk",
                    graph_risk,
                )

            with intel_cols[1]:
                st.metric(
                    "Cross-Case Links",
                    cross_case_links,
                )

            with intel_cols[2]:
                st.metric(
                    "Entities",
                    len(entities),
                )

            if entities:

                st.markdown("#### Entities")

                entity_html = ""

                for entity in entities[:10]:

                    entity_html += f"""
                    <span style="
                        display:inline-block;
                        background:#1e1e1e;
                        color:#fff;
                        padding:5px 10px;
                        margin:4px;
                        border-radius:10px;
                        font-size:12px;
                    ">
                        {entity}
                    </span>
                    """

                st.markdown(
                    entity_html,
                    unsafe_allow_html=True,
                )

            if ai_summary:

                st.markdown("#### AI Summary")

                st.info(ai_summary)

        # -------------------------------------------------------------
        # Activity Timeline
        # -------------------------------------------------------------

        with st.expander(
            "Recent Investigation Activity",
            expanded=False,
        ):

            events = []

            for method_name in [
                "get_case_events",
                "list_case_events",
                "fetch_case_events",
            ]:

                method = getattr(ledger, method_name, None)

                if callable(method):

                    try:
                        events = method(case_id)
                        break

                    except Exception:
                        pass

            if not events:

                st.caption("No recent activity")

            else:

                for event in events[:10]:

                    ts = (
                        event.get("timestamp")
                        or event.get("created_at")
                        or event.get("created_at_ms")
                    )

                    label = (
                        event.get("event_type")
                        or event.get("action")
                        or "EVENT"
                    )

                    actor = (
                        event.get("actor")
                        or event.get("performed_by")
                        or "system"
                    )

                    st.markdown(
                        f"""
                        **{label}**
                        • {actor}
                        • {ts}
                        """
                    )

        # -------------------------------------------------------------
        # Future Approval Actions
        # -------------------------------------------------------------

        with st.expander(
            "Approvals",
            expanded=False,
        ):

            approval_cols = st.columns(4)

            actions = [
                "Request Closure Approval",
                "Request Legal Review",
                "Approve",
                "Reject",
            ]

            for idx, action in enumerate(actions):

                with approval_cols[idx]:

                    st.button(
                        action,
                        key=f"approval_{case_id}_{idx}",
                        use_container_width=True,
                        disabled=True,
                    )

        # -------------------------------------------------------------
        # Footer
        # -------------------------------------------------------------

        st.caption(
            f"Live-ready operational card • Case {case_id}"
        )