from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

from ui.case_workspace.command_center.queue_state import QueueState

from ui.case_workspace.command_center.case_card import render_case_card

from ui.case_workspace.command_center.activity_feed import (
    render_activity_feed,
    render_live_status_bar,
)

from ui.case_workspace.command_center.routing_panel import render_routing_panel

from ui.case_workspace.command_center.filters import (
    render_command_center_filters,
    apply_command_center_filters,
)

from ui.case_workspace.command_center.sorting import apply_command_center_sorting

from core.services.cases.bulk_case_service import BulkCaseService

from core.services.cases.sla_dashboard_service import SLADashboardService

from core.services.cases.command_center_service import CommandCenterService

from core.ai.copilot.copilot_service import CopilotService

from ui.copilot.copilot_panel import render_copilot_panel


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _safe_user_id(current_user: Any) -> str:
    if isinstance(current_user, dict):
        return (
            current_user.get("username")
            or current_user.get("email")
            or current_user.get("user_id")
            or "system"
        )

    if isinstance(current_user, str):
        return current_user

    return "system"


def _safe_tenant_id(current_user: Any) -> Optional[str]:
    if isinstance(current_user, dict):
        return current_user.get("tenant_id")

    return None


def _service_from_sources(
    service_name: str,
    *,
    explicit: Any = None,
    ledger: Any = None,
    source: Any = None,
) -> Any:
    """
    Safely resolves optional services from:
    1. explicit parameter
    2. source object, if supplied
    3. ledger object, if attached there
    """

    if explicit is not None:
        return explicit

    if source is not None and hasattr(source, service_name):
        return getattr(source, service_name)

    if ledger is not None and hasattr(ledger, service_name):
        return getattr(ledger, service_name)

    return None


# ---------------------------------------------------------------------
# Main Render
# ---------------------------------------------------------------------

def render_investigation_queue(
    *,
    ledger: Any,
    current_user: Any = "system",
    assignment_service: Any = None,
    escalation_service: Any = None,
    approval_service: Any = None,
    state_machine: Any = None,
    routing_service: Any = None,
    graph_service: Any = None,
    graph_risk_service: Any = None,
    activity_service: Any = None,
    case_intelligence_service: Any = None,
    campaign_service: Any = None,
    entity_resolution_service: Any = None,
    recommendation_engine: Any = None,
    playbook_service: Any = None,
    event_broadcaster: Any = None,
    service_source: Any = None,
):
    """
    SOC Command Center

    Operational investigation orchestration layer with:
    - modular filters
    - modular sorting
    - bulk actions
    - routing
    - activity feed
    - AI investigation copilot
    """

    QueueState.initialize()

    user_id = _safe_user_id(current_user)
    tenant_id = _safe_tenant_id(current_user)

    # -----------------------------------------------------------------
    # Optional Service Resolution
    # -----------------------------------------------------------------

    graph_risk_service = _service_from_sources(
        "graph_risk_service",
        explicit=graph_risk_service,
        ledger=ledger,
        source=service_source,
    )

    case_intelligence_service = _service_from_sources(
        "case_intelligence_service",
        explicit=case_intelligence_service,
        ledger=ledger,
        source=service_source,
    )

    campaign_service = _service_from_sources(
        "campaign_service",
        explicit=campaign_service,
        ledger=ledger,
        source=service_source,
    )

    entity_resolution_service = _service_from_sources(
        "entity_resolution_service",
        explicit=entity_resolution_service,
        ledger=ledger,
        source=service_source,
    )

    recommendation_engine = _service_from_sources(
        "recommendation_engine",
        explicit=recommendation_engine,
        ledger=ledger,
        source=service_source,
    )

    playbook_service = _service_from_sources(
        "playbook_service",
        explicit=playbook_service,
        ledger=ledger,
        source=service_source,
    )

    event_broadcaster = _service_from_sources(
        "event_broadcaster",
        explicit=event_broadcaster,
        ledger=ledger,
        source=service_source,
    )

    escalation_service = _service_from_sources(
        "escalation_service",
        explicit=escalation_service,
        ledger=ledger,
        source=service_source,
    )

    approval_service = _service_from_sources(
        "approval_service",
        explicit=approval_service,
        ledger=ledger,
        source=service_source,
    )

    # -----------------------------------------------------------------
    # Services
    # -----------------------------------------------------------------

    bulk_service = BulkCaseService(
        ledger=ledger,
        assignment_service=assignment_service,
        escalation_service=escalation_service,
        approval_service=approval_service,
        state_machine=state_machine,
    )

    sla_service = SLADashboardService(
        ledger=ledger,
    )

    command_center_service = CommandCenterService(
        ledger=ledger,
        assignment_service=assignment_service,
        escalation_service=escalation_service,
        approval_service=approval_service,
        routing_service=routing_service,
        graph_service=graph_service,
        activity_service=activity_service,
    )

    # -----------------------------------------------------------------
    # AI Copilot
    # -----------------------------------------------------------------

    copilot_service = CopilotService(
        ledger=ledger,
        sla_service=sla_service,
        graph_service=graph_service,
        graph_risk_service=graph_risk_service,
        case_intelligence_service=case_intelligence_service,
        campaign_service=campaign_service,
        entity_resolution_service=entity_resolution_service,
        recommendation_engine=recommendation_engine,
        playbook_service=playbook_service,
        approval_service=approval_service,
        assignment_service=assignment_service,
        escalation_service=escalation_service,
        event_broadcaster=event_broadcaster,
    )

    # -----------------------------------------------------------------
    # Header
    # -----------------------------------------------------------------

    st.title("SOC Command Center")

    render_live_status_bar()

    st.caption(
        "Operational investigation orchestration platform"
    )

    # -----------------------------------------------------------------
    # Dashboard
    # -----------------------------------------------------------------

    render_sla_dashboard(
        sla_service=sla_service,
    )

    st.divider()

    # -----------------------------------------------------------------
    # Filters
    # -----------------------------------------------------------------

    render_command_center_filters()

    st.divider()

    # -----------------------------------------------------------------
    # Snapshot
    # -----------------------------------------------------------------

    snapshot = command_center_service.get_command_center_snapshot(
        tenant_id=tenant_id,
    )

    cases = snapshot.get("cases", [])

    # -----------------------------------------------------------------
    # Apply Filters + Sorting
    # -----------------------------------------------------------------

    cases = apply_command_center_filters(cases)

    cases = apply_command_center_sorting(cases)

    # -----------------------------------------------------------------
    # Bulk Actions
    # -----------------------------------------------------------------

    render_bulk_actions(
        bulk_service=bulk_service,
        current_user=user_id,
    )

    st.divider()

    # -----------------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------------

    tabs = st.tabs([
        "Investigations",
        "Routing",
        "Activity",
        "AI Copilot",
    ])

    # -----------------------------------------------------------------
    # Investigations
    # -----------------------------------------------------------------

    with tabs[0]:

        queue_col, side_col = st.columns(
            [0.72, 0.28]
        )

        with queue_col:

            st.subheader(
                f"Investigations ({len(cases)})"
            )

            analysts = load_analysts(ledger)

            if not cases:

                st.info("No investigations found.")

            else:

                for case in cases:

                    case_id = (
                        case.get("case_id")
                        or case.get("id")
                    )

                    render_case_card(
                        case,
                        ledger=ledger,
                        assignment_service=assignment_service,
                        escalation_service=escalation_service,
                        approval_service=approval_service,
                        state_machine=state_machine,
                        analysts=analysts,
                        current_user=user_id,
                    )

                    # -------------------------------------------------
                    # Per-Case AI Copilot Preview
                    # -------------------------------------------------

                    with st.expander(
                        f"🤖 AI Copilot Guidance — Case {case_id}",
                        expanded=False,
                    ):
                        render_case_copilot_preview(
                            copilot_service=copilot_service,
                            case=case,
                            case_id=case_id,
                            tenant_id=tenant_id or case.get("tenant_id"),
                        )

        with side_col:

            render_activity_feed(
                ledger=ledger,
                limit=20,
                compact=True,
            )

            st.divider()

            render_selected_case_copilot(
                copilot_service=copilot_service,
                tenant_id=tenant_id,
            )

    # -----------------------------------------------------------------
    # Routing
    # -----------------------------------------------------------------

    with tabs[1]:

        render_routing_panel(
            ledger=ledger,
            assignment_service=assignment_service,
            routing_service=routing_service,
            current_user=user_id,
            tenant_id=tenant_id,
        )

    # -----------------------------------------------------------------
    # Activity
    # -----------------------------------------------------------------

    with tabs[2]:

        render_activity_feed(
            ledger=ledger,
            limit=100,
            compact=False,
        )

    # -----------------------------------------------------------------
    # AI Copilot
    # -----------------------------------------------------------------

    with tabs[3]:

        render_full_copilot_tab(
            copilot_service=copilot_service,
            cases=cases,
            tenant_id=tenant_id,
        )


# ---------------------------------------------------------------------
# Copilot UI Helpers
# ---------------------------------------------------------------------

def render_case_copilot_preview(
    *,
    copilot_service: CopilotService,
    case: Dict[str, Any],
    case_id: Any,
    tenant_id: Optional[str] = None,
):
    if not case_id:
        st.warning("Case ID unavailable.")
        return

    try:
        briefing = copilot_service.build_operational_briefing(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        st.info(
            briefing.get("headline")
            or "No AI briefing available."
        )

        cols = st.columns(4)

        with cols[0]:
            st.metric(
                "Severity",
                briefing.get("severity", "UNKNOWN"),
            )

        with cols[1]:
            st.metric(
                "Status",
                briefing.get("status", "UNKNOWN"),
            )

        with cols[2]:
            st.metric(
                "Priority",
                briefing.get("priority_score", 0),
            )

        with cols[3]:
            st.metric(
                "Blast Radius",
                briefing.get("blast_radius", 0),
            )

        top_action = briefing.get("top_action") or {}

        if top_action:
            st.success(
                f"Recommended: {top_action.get('label') or top_action.get('action')}"
            )

            reason = top_action.get("reason")

            if reason:
                st.caption(reason)

        critical_reasons = briefing.get("critical_reasons") or []

        if critical_reasons:
            st.markdown("#### Why This Matters")

            for reason in critical_reasons[:5]:
                st.write(f"- {reason}")

        if st.button(
            "Open Full Copilot",
            key=f"open_full_copilot_{case_id}",
            use_container_width=True,
        ):
            st.session_state["copilot_case_id"] = case_id
            st.success(f"Selected case {case_id} for full copilot review.")

    except Exception as exc:
        st.error(f"Copilot unavailable: {exc}")


def render_selected_case_copilot(
    *,
    copilot_service: CopilotService,
    tenant_id: Optional[str] = None,
):
    selected_case_id = (
        st.session_state.get("copilot_case_id")
        or st.session_state.get("selected_case_id")
    )

    st.subheader("🤖 AI Copilot")

    if not selected_case_id:
        st.caption("Open a case to view AI guidance.")
        return

    with st.expander(
        f"Selected Case: {selected_case_id}",
        expanded=True,
    ):
        try:
            briefing = copilot_service.build_operational_briefing(
                case_id=selected_case_id,
                tenant_id=tenant_id,
            )

            st.info(
                briefing.get("headline")
                or "No briefing available."
            )

            top_action = briefing.get("top_action") or {}

            if top_action:
                st.success(
                    top_action.get("label")
                    or top_action.get("action")
                    or "Recommended action available."
                )

            if st.button(
                "Open Full AI Copilot",
                key=f"side_full_copilot_{selected_case_id}",
                use_container_width=True,
            ):
                st.session_state["copilot_case_id"] = selected_case_id

        except Exception as exc:
            st.error(f"Copilot unavailable: {exc}")


def render_full_copilot_tab(
    *,
    copilot_service: CopilotService,
    cases: List[Dict[str, Any]],
    tenant_id: Optional[str] = None,
):
    st.subheader("🤖 AI Investigation Copilot")

    if not cases:
        st.info("No cases available for AI review.")
        return

    case_options = []

    for case in cases:
        case_id = case.get("case_id") or case.get("id")
        title = case.get("title") or f"Case {case_id}"

        if case_id is not None:
            case_options.append(
                {
                    "case_id": case_id,
                    "label": f"{case_id} — {title}",
                }
            )

    if not case_options:
        st.info("No selectable cases available.")
        return

    current = st.session_state.get("copilot_case_id")

    labels = [
        item["label"]
        for item in case_options
    ]

    selected_index = 0

    if current is not None:
        for idx, item in enumerate(case_options):
            if str(item["case_id"]) == str(current):
                selected_index = idx
                break

    selected_label = st.selectbox(
        "Select investigation",
        options=labels,
        index=selected_index,
        key="copilot_case_selector",
    )

    selected_case_id = case_options[
        labels.index(selected_label)
    ]["case_id"]

    st.session_state["copilot_case_id"] = selected_case_id

    render_copilot_panel(
        copilot_service=copilot_service,
        case_id=selected_case_id,
        tenant_id=tenant_id,
    )


# ---------------------------------------------------------------------
# SLA Dashboard
# ---------------------------------------------------------------------

def render_sla_dashboard(
    *,
    sla_service: SLADashboardService,
):

    try:
        summary = sla_service.get_dashboard_summary()
    except Exception as exc:
        st.error(f"SLA dashboard unavailable: {exc}")
        return

    try:
        pressure = sla_service.get_operational_pressure_score()
    except Exception:
        pressure = {
            "level": "UNKNOWN",
            "score": 0,
        }

    cols = st.columns(6)

    metrics = [
        ("Breached", summary.get("breached_count", 0)),
        ("Near Breach", summary.get("near_breach_count", 0)),
        ("Critical", summary.get("critical_count", 0)),
        ("Unassigned", summary.get("unassigned_count", 0)),
        ("Escalated", summary.get("escalated_count", 0)),
        ("Pressure", pressure.get("level", "UNKNOWN")),
    ]

    for idx, (label, value) in enumerate(metrics):

        with cols[idx]:

            st.metric(
                label,
                value,
            )


# ---------------------------------------------------------------------
# Bulk Actions
# ---------------------------------------------------------------------

def render_bulk_actions(
    *,
    bulk_service: BulkCaseService,
    current_user: str,
):

    selected_cases = QueueState.get_selected_cases()

    st.subheader(
        f"Bulk Actions ({len(selected_cases)} selected)"
    )

    if not selected_cases:

        st.caption(
            "Select investigations to enable bulk operations."
        )

        return

    cols = st.columns(5)

    # -------------------------------------------------------------
    # Escalate
    # -------------------------------------------------------------

    with cols[0]:

        if st.button(
            "Bulk Escalate",
            use_container_width=True,
            key="bulk_escalate_cases_btn",
        ):

            result = bulk_service.bulk_escalate_cases(
                case_ids=selected_cases,
                actor=current_user,
                reason="Bulk escalation from Command Center",
            )

            st.success(
                f"Escalated {result.get('succeeded', 0)} cases"
            )

    # -------------------------------------------------------------
    # Close
    # -------------------------------------------------------------

    with cols[1]:

        if st.button(
            "Bulk Close",
            use_container_width=True,
            key="bulk_close_cases_btn",
        ):

            result = bulk_service.bulk_close_cases(
                case_ids=selected_cases,
                actor=current_user,
                reason="Bulk closure from Command Center",
            )

            st.success(
                f"Processed {result.get('succeeded', 0)} closures"
            )

    # -------------------------------------------------------------
    # Transition
    # -------------------------------------------------------------

    with cols[2]:

        transition_target = st.selectbox(
            "Transition",
            options=[
                "TRIAGE",
                "INVESTIGATING",
                "ESCALATED",
                "CONTAINED",
                "RESOLVED",
                "CLOSED",
            ],
            key="bulk_transition_target",
        )

        if st.button(
            "Apply",
            use_container_width=True,
            key="bulk_apply_transition_btn",
        ):

            result = bulk_service.bulk_transition_cases(
                case_ids=selected_cases,
                to_state=transition_target,
                actor=current_user,
            )

            st.success(
                f"Transitioned {result.get('succeeded', 0)} cases"
            )

    # -------------------------------------------------------------
    # Approvals
    # -------------------------------------------------------------

    with cols[3]:

        if st.button(
            "Request Approval",
            use_container_width=True,
            key="bulk_request_approval_btn",
        ):

            result = bulk_service.bulk_request_approval(
                case_ids=selected_cases,
                approval_type="CLOSURE_APPROVAL",
                requested_by=current_user,
            )

            st.success(
                f"Approval requests created: {result.get('succeeded', 0)}"
            )

    # -------------------------------------------------------------
    # Clear
    # -------------------------------------------------------------

    with cols[4]:

        if st.button(
            "Clear Selection",
            use_container_width=True,
            key="bulk_clear_selection_btn",
        ):

            QueueState.clear_selected_cases()

            st.rerun()


# ---------------------------------------------------------------------
# Analysts
# ---------------------------------------------------------------------

def load_analysts(
    ledger: Any,
) -> List[str]:

    for method_name in [
        "get_analysts",
        "list_analysts",
        "get_users",
    ]:

        method = getattr(ledger, method_name, None)

        if callable(method):

            try:

                users = method()

                analysts = []

                for user in users:

                    if isinstance(user, dict):

                        role = str(
                            user.get("role", "")
                        ).lower()

                        if role in [
                            "analyst",
                            "investigator",
                            "soc_analyst",
                            "admin",
                            "tenant_admin",
                            "super_admin",
                        ]:

                            analyst = (
                                user.get("username")
                                or user.get("email")
                                or user.get("user_id")
                            )

                            if analyst:
                                analysts.append(analyst)

                    else:

                        analysts.append(str(user))

                return sorted(
                    list(set(analysts))
                )

            except Exception:
                pass

    return []