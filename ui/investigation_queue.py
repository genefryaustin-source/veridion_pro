from __future__ import annotations

import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional

from core.services.cases.assignment_service import AssignmentService
from core.services.cases.sla_service import SLAService
from core.services.graph.graph_risk_service import GraphRiskService
from core.services.cases.case_state_machine import CaseStateMachine

from ui.realtime.live_sync import get_live_sync, LiveSync
from ui.realtime.notification_center import (
    render_notification_banner,
    render_notification_sidebar_widget,
    render_notification_center,
)
from ui.realtime.live_activity_stream import render_live_activity_stream
from ui.realtime.live_queue_refresh import (
    LiveQueueRefresh,
    apply_live_queue_refresh,
)
from ui.realtime.live_graph_updates import render_live_graph_updates


STATUS_COLORS = {
    "NEW": "#2196F3",
    "TRIAGE": "#03A9F4",
    "INVESTIGATING": "#4CAF50",
    "ESCALATED": "#FF9800",
    "CONTAINED": "#9C27B0",
    "RESOLVED": "#607D8B",
    "CLOSED": "#777777",
}

SEVERITY_COLORS = {
    "CRITICAL": "#D32F2F",
    "HIGH": "#FF5722",
    "MEDIUM": "#FFC107",
    "LOW": "#4CAF50",
    "INFO": "#777777",
}


def _get_current_user() -> Dict[str, Any]:
    user = st.session_state.get("user") or st.session_state.get("current_user") or {}

    if isinstance(user, str):
        return {
            "username": user,
            "email": user,
            "tenant_id": st.session_state.get("tenant_id"),
        }

    if not isinstance(user, dict):
        return {
            "username": "unknown",
            "email": "unknown",
            "tenant_id": st.session_state.get("tenant_id"),
        }

    return user


def _get_user_id(user: Dict[str, Any]) -> str:
    return (
        user.get("username")
        or user.get("email")
        or user.get("user_id")
        or "unknown"
    )


def render_badge(text: str, color: str):
    st.markdown(
        f"""
        <span style="
            background:{color};
            color:white;
            padding:4px 8px;
            border-radius:6px;
            font-size:12px;
            font-weight:bold;
        ">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_case_card(
    storage,
    case: Dict[str, Any],
    graph_risk_service,
    sla_service,
):
    case_id = case.get("case_id") or case.get("id")
    case_version = LiveQueueRefresh.get_case_version(case_id)

    title = case.get("title") or f"Case {case_id}"
    owner = case.get("owner") or case.get("assigned_to") or "UNASSIGNED"
    status = (case.get("status") or "NEW").upper()

    try:
        graph_risk = graph_risk_service.analyze_case_graph(case_id)
    except Exception as exc:
        graph_risk = {
            "case_risk": {
                "severity": "LOW",
                "score": 0,
                "reasons": [f"Graph risk unavailable: {exc}"],
                "cross_case_pivots": 0,
                "relationship_count": 0,
            }
        }

    case_risk = graph_risk.get("case_risk", {}) or {}
    severity = (case_risk.get("severity") or case.get("severity") or "LOW").upper()

    try:
        sla = sla_service.calculate_case_sla(
            case=case,
            graph_risk=graph_risk,
        )
    except TypeError:
        sla = sla_service.calculate_case_sla(case, graph_risk)
    except Exception as exc:
        sla = {
            "breached": False,
            "remaining_minutes": "N/A",
            "overdue_minutes": 0,
            "error": str(exc),
        }

    breached = bool(sla.get("breached"))

    with st.container():

        st.markdown(
            """
            <div style="
                border:1px solid #333;
                border-radius:10px;
                padding:14px;
                margin-bottom:12px;
                background:#111;
            ">
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"### {title}")
            st.caption(f"Case ID: {case_id} • Live Version: {case_version}")

        with col2:
            if st.button(
                "Open",
                key=f"open_case_{case_id}_{case_version}",
                use_container_width=True,
            ):
                st.session_state["selected_case_id"] = case_id
                st.rerun()

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            render_badge(
                status,
                STATUS_COLORS.get(status, "#777777"),
            )

        with c2:
            render_badge(
                severity,
                SEVERITY_COLORS.get(severity, "#777777"),
            )

        with c3:
            st.metric(
                "Risk Score",
                case_risk.get("score", 0),
            )

        with c4:
            if breached:
                st.error(
                    f"SLA BREACHED ({sla.get('overdue_minutes', 0)} min)"
                )
            else:
                st.success(
                    f"{sla.get('remaining_minutes', 'N/A')} min remaining"
                )

        st.divider()

        st.write(f"**Owner:** {owner}")

        st.write(
            f"**Cross-Case Pivots:** {case_risk.get('cross_case_pivots', 0)}"
        )

        st.write(
            f"**Relationships:** {case_risk.get('relationship_count', 0)}"
        )

        reasons = case_risk.get("reasons", []) or []

        if reasons:
            st.markdown("#### Risk Drivers")
            for reason in reasons:
                st.write(f"- {reason}")

        st.markdown("</div>", unsafe_allow_html=True)


def _filter_cases(
    cases: List[Dict[str, Any]],
    queue_type: str,
    sla_service,
    graph_risk_service,
) -> List[Dict[str, Any]]:
    results = []

    for case in cases:
        case_id = case.get("case_id") or case.get("id")
        status = (case.get("status") or "NEW").upper()

        try:
            graph_risk = graph_risk_service.analyze_case_graph(case_id)
        except Exception:
            graph_risk = {"case_risk": {"severity": "LOW"}}

        severity = (
            graph_risk.get("case_risk", {}).get("severity", "LOW")
        ).upper()

        try:
            sla = sla_service.calculate_case_sla(case, graph_risk)
        except Exception:
            sla = {"breached": False}

        owner = case.get("owner") or case.get("assigned_to")

        if queue_type == "UNASSIGNED" and not owner:
            results.append(case)

        elif queue_type == "ASSIGNED" and owner:
            results.append(case)

        elif queue_type == "ESCALATED" and (
            status == "ESCALATED" or severity == "CRITICAL"
        ):
            results.append(case)

        elif queue_type == "BREACHED" and sla.get("breached"):
            results.append(case)

        elif queue_type == "AWAITING_APPROVAL" and status == "RESOLVED":
            results.append(case)

        elif queue_type == "CLOSED" and status == "CLOSED":
            results.append(case)

    return results


def _load_all_cases(ledger) -> List[Dict[str, Any]]:
    with ledger._connect() as con:
        rows = con.execute(
            """
            SELECT *
            FROM cases
            ORDER BY created_at_ms DESC
            """
        ).fetchall()

        return [dict(r) for r in rows]


def render_queue_tabs(
    storage,
    all_cases: List[Dict[str, Any]],
    sla_service,
    graph_risk_service,
):
    queue_tabs = st.tabs([
        "📥 Unassigned",
        "👤 Assigned",
        "🚨 Escalated",
        "⏱️ Breached",
        "📝 Awaiting Approval",
        "✅ Closed",
    ])

    queue_map = {
        0: "UNASSIGNED",
        1: "ASSIGNED",
        2: "ESCALATED",
        3: "BREACHED",
        4: "AWAITING_APPROVAL",
        5: "CLOSED",
    }

    for idx, queue_type in queue_map.items():

        with queue_tabs[idx]:

            filtered = _filter_cases(
                all_cases,
                queue_type,
                sla_service,
                graph_risk_service,
            )

            st.metric(f"{queue_type} Cases", len(filtered))
            st.divider()

            if not filtered:
                st.info(f"No {queue_type.lower()} cases.")
                continue

            for case in filtered:
                render_case_card(
                    storage=storage,
                    case=case,
                    graph_risk_service=graph_risk_service,
                    sla_service=sla_service,
                )


def render_analyst_workload(assignment_service):
    st.subheader("📊 Analyst Workload")

    try:
        workload = assignment_service.get_workload_summary()
    except Exception as exc:
        st.error(f"Unable to load analyst workload: {exc}")
        return

    if workload:
        df = pd.DataFrame(workload)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No analyst workload data available.")


def render_investigation_queue(storage):
    ledger = storage.ledger

    assignment_service = AssignmentService(ledger)
    sla_service = SLAService(ledger)
    graph_risk_service = GraphRiskService(ledger)
    state_machine = CaseStateMachine(ledger)

    user = _get_current_user()
    user_id = _get_user_id(user)
    tenant_id = user.get("tenant_id")

    # ------------------------------------------------------
    # LIVE REALTIME INITIALIZATION
    # ------------------------------------------------------

    live_sync = get_live_sync(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    if tenant_id:
        live_sync.subscribe_tenant(tenant_id)

    live_sync.subscribe_analyst(user_id)
    live_sync.subscribe_severity("HIGH")
    live_sync.subscribe_severity("CRITICAL")

    apply_live_queue_refresh(
        user_id=user_id,
        tenant_id=tenant_id,
        limit=100,
    )

    # ------------------------------------------------------
    # PAGE HEADER
    # ------------------------------------------------------

    st.title("🛡️ Investigation Command Center")

    render_notification_banner()
    LiveSync.render_live_banners()
    LiveQueueRefresh.render_compact_status()

    try:
        render_notification_sidebar_widget(limit=10)
    except Exception:
        pass

    st.divider()

    # ------------------------------------------------------
    # LOAD CASES
    # ------------------------------------------------------

    try:
        all_cases = _load_all_cases(ledger)
    except Exception as exc:
        st.error(f"Unable to load cases: {exc}")
        return

    # ------------------------------------------------------
    # MAIN COMMAND CENTER TABS
    # ------------------------------------------------------

    tab_queue, tab_activity, tab_graph, tab_notifications, tab_workload = st.tabs([
        "Investigation Queue",
        "Live Activity",
        "Graph Intelligence",
        "Notifications",
        "Analyst Workload",
    ])

    with tab_queue:
        LiveQueueRefresh.render_compact_status()

        render_queue_tabs(
            storage=storage,
            all_cases=all_cases,
            sla_service=sla_service,
            graph_risk_service=graph_risk_service,
        )

    with tab_activity:
        render_live_activity_stream(
            user_id=user_id,
            tenant_id=tenant_id,
            auto_poll=True,
            limit=100,
            show_filters=True,
            show_metrics=True,
            compact=False,
        )

    with tab_graph:
        render_live_graph_updates(
            user_id=user_id,
            tenant_id=tenant_id,
            auto_poll=True,
        )

    with tab_notifications:
        render_notification_center(
            max_notifications=100,
            show_controls=True,
        )

    with tab_workload:
        render_analyst_workload(
            assignment_service=assignment_service,
        )

    st.divider()

    # ------------------------------------------------------
    # LIVE REFRESH SNAPSHOT
    # ------------------------------------------------------

    refresh_snapshot = LiveQueueRefresh.snapshot_versions()

    st.caption(
        f"Live Versions • "
        f"Queue:{refresh_snapshot['queue_version']} "
        f"SLA:{refresh_snapshot['sla_version']} "
        f"Routing:{refresh_snapshot['routing_version']} "
        f"Activity:{refresh_snapshot['activity_version']} "
        f"Graph:{refresh_snapshot['graph_version']}"
    )

    # ------------------------------------------------------
    # FUTURE WEBSOCKET PARTIAL REFRESH HOOK
    # ------------------------------------------------------
    # Future:
    # partial case rerender
    # websocket-driven updates
    # graph streaming
    # collaborative analyst presence