from __future__ import annotations

import time
from typing import Any, Dict, List

import streamlit as st

from ui.case_workspace.command_center.queue_state import (
    QueueState,
    ALL_PRIORITIES,
    ALL_STATUSES,
    SORT_OPTIONS,
)


def render_command_center_filters() -> None:
    """
    Filter controls for SOC Command Center.
    """

    QueueState.initialize()

    st.subheader("Operational Filters")

    row1 = st.columns(4)

    with row1[0]:
        query = st.text_input(
            "Search",
            value=QueueState.get_search_query(),
            key="cmd_filter_search_query",
        )
        QueueState.set_search_query(query)

    with row1[1]:
        statuses = st.multiselect(
            "Statuses",
            options=ALL_STATUSES,
            default=QueueState.get_status_filters(),
            key="cmd_filter_statuses",
        )
        QueueState.set_status_filters(statuses)

    with row1[2]:
        priorities = st.multiselect(
            "Priorities",
            options=ALL_PRIORITIES,
            default=QueueState.get_priority_filters(),
            key="cmd_filter_priorities",
        )
        QueueState.set_priority_filters(priorities)

    with row1[3]:
        sort_by = st.selectbox(
            "Sort By",
            options=SORT_OPTIONS,
            index=SORT_OPTIONS.index(QueueState.get_sort_by())
            if QueueState.get_sort_by() in SORT_OPTIONS
            else 0,
            key="cmd_filter_sort_by",
        )
        QueueState.set_sort_by(sort_by)

    row2 = st.columns(5)

    with row2[0]:
        escalation_only = st.toggle(
            "Escalated Only",
            value=QueueState.get("escalation_only", False),
            key="cmd_filter_escalated_only",
        )
        QueueState.set("escalation_only", escalation_only)

    with row2[1]:
        breached_only = st.toggle(
            "Breached Only",
            value=QueueState.show_breached_only(),
            key="cmd_filter_breached_only",
        )
        QueueState.set_show_breached_only(breached_only)

    with row2[2]:
        unassigned_only = st.toggle(
            "Unassigned Only",
            value=QueueState.get("unassigned_only", False),
            key="cmd_filter_unassigned_only",
        )
        QueueState.set("unassigned_only", unassigned_only)

    with row2[3]:
        compact = st.toggle(
            "Compact Mode",
            value=QueueState.compact_mode(),
            key="cmd_filter_compact_mode",
        )
        QueueState.set_compact_mode(compact)

    with row2[4]:
        if st.button("Reset Filters", use_container_width=True):
            QueueState.reset_filters()
            QueueState.set("unassigned_only", False)
            st.rerun()


def apply_command_center_filters(
    cases: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Apply QueueState filters to cases.
    """

    query = QueueState.get_search_query().lower().strip()
    statuses = QueueState.get_status_filters()
    priorities = QueueState.get_priority_filters()

    escalation_only = QueueState.get("escalation_only", False)
    breached_only = QueueState.show_breached_only()
    unassigned_only = QueueState.get("unassigned_only", False)

    now_ms = int(time.time() * 1000)

    filtered = []

    for case in cases:
        title = str(case.get("title") or "").lower()
        case_id = str(case.get("case_id") or case.get("id") or "").lower()

        status = str(case.get("status") or "").upper()

        priority = str(
            case.get("severity")
            or case.get("priority")
            or ""
        ).upper()

        assigned_to = case.get("assigned_to") or case.get("owner")

        escalation_level = int(case.get("escalation_level") or 0)

        sla_due_at = (
            case.get("sla_due_at_ms")
            or case.get("sla_deadline_ms")
        )

        is_breached = False

        if case.get("sla_breached") is True:
            is_breached = True
        elif sla_due_at:
            try:
                is_breached = int(sla_due_at) < now_ms
            except Exception:
                is_breached = False

        if query and query not in title and query not in case_id:
            continue

        if statuses and status not in statuses:
            continue

        if priorities and priority not in priorities:
            continue

        if escalation_only and escalation_level <= 0:
            continue

        if breached_only and not is_breached:
            continue

        if unassigned_only and assigned_to:
            continue

        filtered.append(case)

    return filtered