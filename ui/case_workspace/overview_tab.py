

import streamlit as st

from ui.case_workspace.components.assignment_panel import (
    render_assignment_panel
)

from ui.case_workspace.components.risk_badge import (
    render_risk_badge
)

from ui.case_workspace.components.sla_panel import (
    render_sla_panel
)

from ui.case_workspace.components.escalation_panel import (
    render_escalation_panel
)


def render_overview_tab(
    storage,
    case,
    alerts,
    evidence,
):

    ledger = storage.ledger

    case_id = case.get("id")

    st.subheader("📌 Case Overview")

    # -----------------------------------
    # CASE METADATA
    # -----------------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Case ID", case_id)

    with col2:
        st.metric("Status", case.get("status", "OPEN"))

    with col3:
        st.metric("Alerts", len(alerts))

    with col4:
        st.metric("Evidence", len(evidence))

    st.divider()

    # -----------------------------------
    # STATUS MANAGEMENT
    # -----------------------------------
    st.subheader("🔄 Status Management")

    status_options = [
        "OPEN",
        "INVESTIGATING",
        "ESCALATED",
        "RESOLVED",
        "CLOSED",
    ]

    current_status = case.get("status", "OPEN")

    try:
        current_index = status_options.index(current_status)
    except ValueError:
        current_index = 0

    new_status = st.selectbox(
        "Case Status",
        status_options,
        index=current_index,
        key=f"overview_status_{case_id}",
    )

    if st.button(
        "Update Status",
        key=f"overview_update_status_{case_id}",
    ):

        ledger.update_case_status(case_id, new_status)

        if hasattr(ledger, "add_case_event"):
            ledger.add_case_event(
                case_id,
                "STATUS_CHANGE",
                f"Case status updated to {new_status}"
            )

        st.success("Case status updated")
        st.rerun()

    st.divider()

    # -----------------------------------
    # ASSIGNMENT PANEL
    # -----------------------------------
    render_assignment_panel(
        storage=storage,
        case=case,
    )

    st.divider()

    # -----------------------------------
    # SLA PANEL
    # -----------------------------------
    render_sla_panel(
        storage=storage,
        case=case,
    )

    st.divider()

    # -----------------------------------
    # ESCALATION PANEL
    # -----------------------------------
    render_escalation_panel(
        storage=storage,
        case=case,
    )

