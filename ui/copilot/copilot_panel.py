from __future__ import annotations

import json
import streamlit as st

from typing import Any, Dict, Optional


PRIORITY_COLORS = {
    "CRITICAL": "#D32F2F",
    "HIGH": "#FF9800",
    "MEDIUM": "#FFC107",
    "LOW": "#4CAF50",
}

ACTION_COLORS = {
    "ESCALATION": "#D32F2F",
    "LEGAL": "#8E24AA",
    "EXPORT_CONTROL": "#5E35B1",
    "PLAYBOOK": "#00897B",
    "ROUTING": "#1E88E5",
    "GRAPH": "#6D4C41",
    "EVIDENCE": "#546E7A",
    "APPROVAL": "#3949AB",
    "ENDPOINT": "#C62828",
    "CONTAINMENT": "#EF6C00",
    "SLA": "#AD1457",
}


# ----------------------------------------------------------------------
# Main Panel
# ----------------------------------------------------------------------

def render_copilot_panel(
    *,
    copilot_service: Any,
    case_id: Any,
    tenant_id: Optional[str] = None,
    expanded: bool = True,
):
    """
    Live AI investigation copilot UI.

    Capabilities:
    - explain escalation
    - summarize case
    - recommend next actions
    - explain graph risk
    - explain campaigns
    - summarize SLA pressure
    - analyst workload suggestions
    - recommend reassignment
    """

    if not case_id:
        st.warning("No case selected.")
        return

    try:

        analysis = copilot_service.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

    except Exception as exc:

        st.error(f"Copilot analysis failed: {exc}")
        return

    context = analysis.get("context") or {}
    reasoning = analysis.get("reasoning") or {}
    next_actions = analysis.get("next_actions") or {}
    summaries = analysis.get("summaries") or {}

    with st.container(border=True):

        render_copilot_header(
            context=context,
            next_actions=next_actions,
        )

        st.divider()

        (
            tab_summary,
            tab_actions,
            tab_reasoning,
            tab_graph,
            tab_campaigns,
            tab_sla,
            tab_handoff,
        ) = st.tabs([
            "Summary",
            "Next Actions",
            "Reasoning",
            "Graph Intelligence",
            "Campaigns",
            "SLA / Operations",
            "Shift Handoff",
        ])

        # --------------------------------------------------------------
        # SUMMARY
        # --------------------------------------------------------------

        with tab_summary:

            render_summary_tab(
                summaries=summaries,
                context=context,
            )

        # --------------------------------------------------------------
        # ACTIONS
        # --------------------------------------------------------------

        with tab_actions:

            render_actions_tab(
                copilot_service=copilot_service,
                case_id=case_id,
                tenant_id=tenant_id,
                next_actions=next_actions,
            )

        # --------------------------------------------------------------
        # REASONING
        # --------------------------------------------------------------

        with tab_reasoning:

            render_reasoning_tab(
                reasoning=reasoning,
            )

        # --------------------------------------------------------------
        # GRAPH
        # --------------------------------------------------------------

        with tab_graph:

            render_graph_tab(
                context=context,
                reasoning=reasoning,
            )

        # --------------------------------------------------------------
        # CAMPAIGNS
        # --------------------------------------------------------------

        with tab_campaigns:

            render_campaign_tab(
                context=context,
                reasoning=reasoning,
            )

        # --------------------------------------------------------------
        # SLA
        # --------------------------------------------------------------

        with tab_sla:

            render_sla_tab(
                context=context,
                reasoning=reasoning,
            )

        # --------------------------------------------------------------
        # HANDOFF
        # --------------------------------------------------------------

        with tab_handoff:

            render_handoff_tab(
                summaries=summaries,
            )


# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------

def render_copilot_header(
    *,
    context: Dict[str, Any],
    next_actions: Dict[str, Any],
):
    severity = str(
        context.get("severity") or "UNKNOWN"
    ).upper()

    color = PRIORITY_COLORS.get(
        severity,
        "#777777",
    )

    top_action = next_actions.get("top_action") or {}

    st.markdown(
        f"""
        <div style="
            background:#111;
            border:1px solid #333;
            border-radius:10px;
            padding:16px;
        ">
            <div style="
                font-size:22px;
                font-weight:bold;
                margin-bottom:10px;
            ">
                🤖 AI Investigation Copilot
            </div>

            <div style="
                display:inline-block;
                background:{color};
                color:white;
                padding:6px 12px;
                border-radius:8px;
                font-weight:bold;
                margin-bottom:10px;
            ">
                {severity}
            </div>

            <div style="margin-top:10px;">
                <b>Case:</b> {context.get("title")}
            </div>

            <div>
                <b>Status:</b> {context.get("status")}
            </div>

            <div>
                <b>Priority Score:</b>
                {context.get("operational_priority_score")}
            </div>

            <div style="margin-top:12px;">
                <b>Top Recommended Action:</b>
                {top_action.get("label", "None")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Summary Tab
# ----------------------------------------------------------------------

def render_summary_tab(
    *,
    summaries: Dict[str, Any],
    context: Dict[str, Any],
):
    executive = summaries.get(
        "executive_summary"
    ) or {}

    analyst = summaries.get(
        "analyst_summary"
    ) or {}

    st.subheader("Executive Summary")

    st.info(
        executive.get(
            "summary",
            "No executive summary available.",
        )
    )

    key_points = executive.get(
        "key_points"
    ) or []

    if key_points:

        st.markdown("### Key Points")

        for item in key_points:
            st.write(f"- {item}")

    st.divider()

    st.subheader("Analyst Summary")

    st.write(
        analyst.get(
            "summary",
            "No analyst summary available.",
        )
    )

    drivers = analyst.get(
        "risk_drivers"
    ) or []

    if drivers:

        st.markdown("### Risk Drivers")

        for driver in drivers:
            st.write(f"- {driver}")

    st.divider()

    cols = st.columns(4)

    with cols[0]:

        st.metric(
            "Evidence",
            context.get(
                "evidence_count",
                0,
            ),
        )

    with cols[1]:

        st.metric(
            "Entities",
            len(
                context.get("entities") or []
            ),
        )

    with cols[2]:

        st.metric(
            "Linked Cases",
            len(
                context.get("linked_cases")
                or []
            ),
        )

    with cols[3]:

        st.metric(
            "Blast Radius",
            context.get(
                "blast_radius_score",
                0,
            ),
        )


# ----------------------------------------------------------------------
# Actions Tab
# ----------------------------------------------------------------------

def render_actions_tab(
    *,
    copilot_service: Any,
    case_id: Any,
    tenant_id: Optional[str],
    next_actions: Dict[str, Any],
):
    actions = next_actions.get(
        "recommended_actions",
        [],
    )

    if not actions:
        st.info("No recommended actions.")
        return

    st.markdown("## ⚡ Operational Actions")

    dry_run = st.toggle(
        "Dry Run Mode",
        value=True,
        key=f"copilot_dry_run_{case_id}",
        help=(
            "When enabled, AI actions are simulated "
            "without operational execution."
        ),
    )

    for idx, action in enumerate(actions):

        category = action.get("category")

        color = ACTION_COLORS.get(
            category,
            "#777777",
        )

        with st.container(border=True):

            st.markdown(
                f"""
                <div style="
                    display:inline-block;
                    background:{color};
                    color:white;
                    padding:4px 10px;
                    border-radius:8px;
                    font-size:12px;
                    font-weight:bold;
                    margin-bottom:10px;
                ">
                    {category}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"### {action.get('label')}"
            )

            st.write(
                action.get("reason")
                or "No reasoning provided."
            )

            cols = st.columns(4)

            with cols[0]:

                st.metric(
                    "Priority",
                    action.get("priority"),
                )

            with cols[1]:

                st.metric(
                    "Confidence",
                    action.get("confidence"),
                )

            with cols[2]:

                st.metric(
                    "Approval",
                    "YES"
                    if action.get(
                        "requires_approval"
                    )
                    else "NO",
                )

            with cols[3]:

                st.metric(
                    "Action",
                    action.get("action"),
                )

            render_action_buttons(
                copilot_service=copilot_service,
                case_id=case_id,
                tenant_id=tenant_id,
                action=action,
                idx=idx,
                dry_run=dry_run,
            )

    # --------------------------------------------------------------
    # PLAYBOOKS
    # --------------------------------------------------------------

    st.divider()

    st.markdown(
        "## 📘 Playbook Execution"
    )

    playbook = st.selectbox(
        "Playbook",
        options=[
            "EXPORT_CONTROL_INVESTIGATION",
            "INSIDER_THREAT_INVESTIGATION",
            "EVIDENCE_PRESERVATION",
            "CRITICAL_ESCALATION",
            "CONTAINMENT_REVIEW",
        ],
        key=f"playbook_select_{case_id}",
    )

    if st.button(
        "Execute Playbook",
        key=f"exec_playbook_{case_id}",
        use_container_width=True,
    ):

        try:

            result = (
                copilot_service.execute_playbook(
                    case_id=case_id,
                    playbook=playbook,
                    tenant_id=tenant_id,
                    actor="copilot_panel",
                    dry_run=dry_run,
                )
            )

            st.success(
                f"Playbook executed: {playbook}"
            )

            st.json(result)

        except Exception as exc:

            st.error(
                f"Playbook execution failed: {exc}"
            )

    # --------------------------------------------------------------
    # AUTONOMOUS RESPONSE
    # --------------------------------------------------------------

    st.divider()

    st.markdown(
        "## 🤖 Autonomous Response"
    )

    if st.button(
        "Run Autonomous Response",
        key=f"auto_response_{case_id}",
        use_container_width=True,
    ):

        try:

            if (
                copilot_service
                .autonomous_response_engine
                is None
            ):

                st.warning(
                    "AutonomousResponseEngine unavailable."
                )

            else:

                result = (
                    copilot_service
                    .autonomous_response_engine
                    .respond_to_case(
                        case_id=case_id,
                        tenant_id=tenant_id,
                        actor="copilot_panel",
                        dry_run=dry_run,
                    )
                )

                st.success(
                    "Autonomous response completed."
                )

                st.json(result)

        except Exception as exc:

            st.error(
                f"Autonomous response failed: {exc}"
            )


# ----------------------------------------------------------------------
# Action Buttons
# ----------------------------------------------------------------------

def render_action_buttons(
    *,
    copilot_service: Any,
    case_id: Any,
    tenant_id: Optional[str],
    action: Dict[str, Any],
    idx: int,
    dry_run: bool,
):
    cols = st.columns(3)

    # --------------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------------

    with cols[0]:

        if st.button(
            "Execute",
            key=f"copilot_execute_{case_id}_{idx}",
            use_container_width=True,
        ):

            try:

                result = (
                    copilot_service
                    .execute_recommendation(
                        case_id=case_id,
                        recommendation=action,
                        tenant_id=tenant_id,
                        actor="copilot_panel",
                        dry_run=dry_run,
                    )
                )

                st.success(
                    f"Executed: {action.get('label')}"
                )

                st.json(result)

            except Exception as exc:

                st.error(
                    f"Execution failed: {exc}"
                )

    # --------------------------------------------------------------
    # CONTAINMENT
    # --------------------------------------------------------------

    with cols[1]:

        if st.button(
            "Containment",
            key=f"copilot_containment_{case_id}_{idx}",
            use_container_width=True,
        ):

            try:

                result = (
                    copilot_service
                    .execute_containment(
                        case_id=case_id,
                        action=action,
                        tenant_id=tenant_id,
                        actor="copilot_panel",
                        dry_run=dry_run,
                    )
                )

                st.warning(
                    f"Containment workflow started: "
                    f"{action.get('label')}"
                )

                st.json(result)

            except Exception as exc:

                st.error(
                    f"Containment failed: {exc}"
                )

    # --------------------------------------------------------------
    # DISMISS
    # --------------------------------------------------------------

    with cols[2]:

        if st.button(
            "Dismiss",
            key=f"copilot_dismiss_{case_id}_{idx}",
            use_container_width=True,
        ):

            st.info(
                f"Dismissed: "
                f"{action.get('label')}"
            )


# ----------------------------------------------------------------------
# Reasoning Tab
# ----------------------------------------------------------------------

def render_reasoning_tab(
    *,
    reasoning: Dict[str, Any],
):
    st.subheader(
        "Operational Reasoning"
    )

    st.json(reasoning)


# ----------------------------------------------------------------------
# Graph Tab
# ----------------------------------------------------------------------

def render_graph_tab(
    *,
    context: Dict[str, Any],
    reasoning: Dict[str, Any],
):
    graph = context.get(
        "graph_risk"
    ) or {}

    st.subheader(
        "Graph Intelligence"
    )

    cols = st.columns(4)

    with cols[0]:

        st.metric(
            "Graph Risk",
            graph.get(
                "graph_risk_score",
                0,
            ),
        )

    with cols[1]:

        st.metric(
            "Cross-Case Links",
            graph.get(
                "cross_case_links",
                0,
            ),
        )

    with cols[2]:

        st.metric(
            "Relationship Count",
            graph.get(
                "relationship_count",
                0,
            ),
        )

    with cols[3]:

        st.metric(
            "Campaign Links",
            graph.get(
                "campaign_links",
                0,
            ),
        )

    linked_cases = context.get(
        "linked_cases"
    ) or []

    if linked_cases:

        st.markdown(
            "### Linked Cases"
        )

        for case in linked_cases:
            st.write(f"- {case}")


# ----------------------------------------------------------------------
# Campaign Tab
# ----------------------------------------------------------------------

def render_campaign_tab(
    *,
    context: Dict[str, Any],
    reasoning: Dict[str, Any],
):
    campaigns = context.get(
        "campaigns"
    ) or []

    st.subheader(
        "Campaign Analysis"
    )

    if not campaigns:

        st.info(
            "No campaign linkage detected."
        )

        return

    for campaign in campaigns:

        st.markdown(
            f"### {campaign.get('campaign_id')}"
        )

        st.write(
            campaign.get("summary")
        )

        indicators = campaign.get(
            "indicators"
        ) or []

        if indicators:

            for item in indicators:
                st.write(f"- {item}")


# ----------------------------------------------------------------------
# SLA Tab
# ----------------------------------------------------------------------

def render_sla_tab(
    *,
    context: Dict[str, Any],
    reasoning: Dict[str, Any],
):
    sla = context.get("sla") or {}

    operational = (
        reasoning.get(
            "operational_priority_reasoning"
        )
        or {}
    )

    cols = st.columns(4)

    with cols[0]:

        st.metric(
            "Breached",
            "YES"
            if sla.get("breached")
            else "NO",
        )

    with cols[1]:

        st.metric(
            "Remaining",
            sla.get(
                "remaining_minutes",
                "N/A",
            ),
        )

    with cols[2]:

        st.metric(
            "Overdue",
            sla.get(
                "overdue_minutes",
                0,
            ),
        )

    with cols[3]:

        st.metric(
            "Priority",
            operational.get(
                "priority_level",
                "UNKNOWN",
            ),
        )

    reasons = operational.get(
        "reasons"
    ) or []

    if reasons:

        st.markdown(
            "### Operational Pressure"
        )

        for reason in reasons:
            st.write(f"- {reason}")


# ----------------------------------------------------------------------
# Handoff Tab
# ----------------------------------------------------------------------

def render_handoff_tab(
    *,
    summaries: Dict[str, Any],
):
    handoff = (
        summaries.get(
            "shift_handoff_summary"
        )
        or {}
    )

    st.subheader(
        "Shift Handoff Summary"
    )

    st.info(
        handoff.get(
            "summary",
            "No handoff summary available.",
        )
    )

    notes = handoff.get(
        "handoff_notes",
        [],
    )

    if notes:

        st.markdown(
            "### Handoff Notes"
        )

        for note in notes:
            st.write(f"- {note}")

    events = handoff.get(
        "recent_events",
        [],
    )

    if events:

        st.markdown(
            "### Recent Events"
        )

        for event in events:

            st.write(
                f"- {event.get('event_type')} "
                f"({event.get('timestamp_ms')})"
            )