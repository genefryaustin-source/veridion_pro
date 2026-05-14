import streamlit as st

from ui.case_workspace.overview_tab import (
    render_overview_tab
)

from ui.case_workspace.intelligence_tab import (
    render_intelligence_tab
)

from ui.case_workspace.entities_tab import (
    render_entities_tab
)

from ui.case_workspace.relationships_tab import (
    render_relationships_tab
)

from ui.case_workspace.evidence_tab import (
    render_evidence_tab
)

from ui.case_workspace.timeline_tab import (
    render_timeline_tab
)

from ui.case_workspace.alerts_tab import (
    render_alerts_tab
)

from ui.case_workspace.notes_tab import (
    render_notes_tab
)

from ui.case_workspace.audit_tab import (
    render_audit_tab
)

from ui.case_workspace.components.case_header import (
    render_case_header
)

from core.services.cases.case_hydration_service import CaseHydrationService

from ui.case_workspace.graph_tab import (render_graph_tab)

def render_case_workspace(storage, case_id):
    if st.button(
            "← Back to Investigation Queue"
    ):
        st.session_state[
            "selected_case_id"
        ] = None

        st.rerun()
    ledger = storage.ledger

    # -----------------------------------
    # HYDRATE INVESTIGATION BUNDLE
    # -----------------------------------
    hydration_service = (
        CaseHydrationService(
            ledger
        )
    )

    bundle = hydration_service.hydrate_case(
        case_id
    )

    case = bundle.get(
        "case",
        {}
    )

    alerts = bundle.get(
        "alerts",
        []
    )

    evidence = bundle.get(
        "evidence",
        []
    )

    entities = bundle.get(
        "entities",
        []
    )

    relationships = bundle.get(
        "relationships",
        []
    )

    timeline = bundle.get(
        "timeline",
        []
    )

    metrics = bundle.get(
        "metrics",
        {}
    )
    graph = bundle.get(
        "graph",
        {}
    )

    # -----------------------------------
    # CASE HEADER
    # -----------------------------------
    render_case_header(
        storage=storage,
        case=case,
        alerts=alerts,
        evidence=evidence,
    )


    # -----------------------------------
    # WORKSPACE TABS
    # -----------------------------------
    tabs = st.tabs([
        "📌 Overview",
        "🧠 Intelligence",
        "🧬 Entities",
        "🕸️ Relationships",
        "📄 Evidence",
        "🕒 Timeline",
        "🚨 Alerts",
        "📝 Notes",
        "🕸️ Graph",
        "🧾 Audit",
    ])

    # -----------------------------------
    # OVERVIEW TAB
    # -----------------------------------
    with tabs[0]:

        render_overview_tab(
            storage=storage,
            case=case,
            alerts=alerts,
            evidence=evidence,
            metrics=metrics,
            entities=entities,
            relationships=relationships,
            timeline=timeline,
        )

    # -----------------------------------
    # INTELLIGENCE TAB
    # -----------------------------------
    with tabs[1]:

        render_intelligence_tab(
            storage=storage,
            case=case,
            alerts=alerts,
            evidence=evidence,
        )

    # -----------------------------------
    # ENTITIES TAB
    # -----------------------------------
    with tabs[2]:
        render_entities_tab(
            storage=storage,
            case=case,
            entities=entities,
        )

    # -----------------------------------
    # RELATIONSHIPS TAB
    # -----------------------------------
    with tabs[3]:
        render_relationships_tab(
            storage=storage,
            case=case,
            relationships=relationships,
        )

    # -----------------------------------
    # EVIDENCE TAB
    # -----------------------------------
    with tabs[4]:

        render_evidence_tab(
            storage=storage,
            case=case,
            evidence=evidence,
            alerts=alerts,
        )

    # -----------------------------------
    # TIMELINE TAB
    # -----------------------------------
    with tabs[5]:

        render_timeline_tab(
            storage=storage,
            case=case,
            timeline=timeline,
        )

    # -----------------------------------
    # ALERTS TAB
    # -----------------------------------
    with tabs[6]:

        render_alerts_tab(
            alerts=alerts,
        )

    # -----------------------------------
    # NOTES TAB
    # -----------------------------------
    with tabs[7]:

        render_notes_tab(
            storage=storage,
            case=case,
        )
        # -----------------------------------
        # GRAPH TAB
        # -----------------------------------
        with tabs[8]:
            render_graph_tab(
                storage=storage,
                case=case,
                graph=graph,
            )
    # -----------------------------------
    # AUDIT TAB
    # -----------------------------------
    with tabs[9]:

        render_audit_tab(
            storage=storage,
            case=case,
        )
