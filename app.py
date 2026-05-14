# app.py

import streamlit as st
from core.db.bootstrap import bootstrap_database
from core.storage.factory import build_storage
from core.events.event_subscribers import (
    register_event_subscribers,
)
from core.connectors.connector_bootstrap import (
    bootstrap_connectors,
)
from core.runtime.distributed_execution_queue import (
    get_distributed_execution_queue,
)


if "db_bootstrapped" not in st.session_state:

    bootstrap_database("data/ledger.db")

    st.session_state.db_bootstrapped = True
# ----------------------------------
# 🔥 MUST BE FIRST STREAMLIT CALL
# ----------------------------------
st.set_page_config(
    page_title="CUI Mail Monitor",
    page_icon="🛡️",
    layout="wide",
)
# ==================================
# VERIDION PRO THEME
# ==================================
from ui.theme import apply_veridion_pro_theme, veridion_header, render_compliance_metrics

# Apply theme once
apply_veridion_pro_theme()

# Then in your pages, you can use:
# veridion_header("Compliance Overview")
# render_compliance_metrics()
# ----------------------------------
# 🔥 NOW SAFE TO IMPORT EVERYTHING
# ----------------------------------

# UI pages

from ui.evidence_viewer import render_evidence_viewer
from ui.metrics_page import render_metrics_page
from ui.supervisor_dashboard import render_supervisor_dashboard
from ui.trust_center_page import render_trust_center_page
from ui.admin_alerts_page import render_alert_settings_page
from ui.investigation_page import render_investigation_page
from ui.alert_center_page import render_alert_center_page
from ui.scan_page import render_scan_page
from ui.admin_page import render_admin_page
from ui.case_workspace.workspace import (render_case_workspace)
from ui.help_page import render_help_page
from ui.relationship_graph_page import (render_relationship_graph,)
from ui.timeline_page import (render_timeline_page)
from ui.case_workspace.case_queue import (render_case_queue)

# Core services
from core.storage.factory import build_storage

from server.scan.worker import start_scan_workers, stop_scan_workers
from core.runtime.execution_graph_engine import (
    get_execution_graph_engine,
)

# ----------------------------------
# 🔥 GLOBAL STORAGE (ALWAYS AVAILABLE)
# ----------------------------------

if "storage" not in st.session_state:

    st.session_state["storage"] = build_storage()

    # ----------------------------------
    # 🔥 INIT DB PRAGMAS ONCE
    # ----------------------------------

    try:

        with (
            st.session_state["storage"]
            .ledger
            ._connect()
            as con
        ):

            st.session_state[
                "storage"
            ].ledger._set_pragmas_once(con)

        print("✅ SQLite WAL initialized")

    except Exception as e:

        print("⚠️ WAL init failed:", e)

storage = st.session_state["storage"]
execution_queue = get_distributed_execution_queue()

storage.execution_queue = execution_queue
# ----------------------------------
# 🔥 EVENT BUS
# ----------------------------------

event_bus = getattr(
    storage,
    "event_bus",
    None,
)

# ----------------------------------
# 🔥 EVENT SUBSCRIBERS
# ----------------------------------

if (
    "event_subscribers_registered"
    not in st.session_state
):

    try:

        register_event_subscribers(
            storage=storage,
            event_bus=event_bus,
        )

        st.session_state[
            "event_subscribers_registered"
        ] = True

        print(
            "✅ Event subscribers registered"
        )

    except Exception as e:

        print(
            "⚠️ Event subscriber registration failed:",
            e,
        )

# ----------------------------------
# 🔥 CONNECTOR BOOTSTRAP
# ----------------------------------

if (
    "connectors_bootstrapped"
    not in st.session_state
):

    try:

        connector_registry = (
            bootstrap_connectors(
                storage,
                event_bus=event_bus,
                tenant_id="default",

                # ----------------------------------
                # KEEP TRUE UNTIL PROD
                # ----------------------------------
                simulation_mode=True,

                enable_graph=True,
                enable_okta=True,
                enable_crowdstrike=True,
                enable_sentinelone=True,
                enable_google_workspace=True,
            )
        )

        storage.connector_registry = (
            connector_registry
        )

        st.session_state[
            "connectors_bootstrapped"
        ] = True

        print(
            "✅ Connectors bootstrapped"
        )

    except Exception as e:

        print(
            "⚠️ Connector bootstrap failed:",
            e,
        )

# ---------------------------------------------------------
# AGENT COORDINATOR
# ---------------------------------------------------------

from core.agents.agent_coordinator import (
    get_agent_coordinator,
)

if "agent_coordinator_initialized" not in st.session_state:

    try:

        storage.agent_coordinator = (
            get_agent_coordinator(
                storage,
                event_bus=event_bus,
            )
        )

        st.session_state[
            "agent_coordinator_initialized"
        ] = True

        print(
            "✅ Agent coordinator initialized"
        )

    except Exception as e:

        print(
            "⚠️ Agent coordinator initialization failed:",
            e,
        )

# ---------------------------------------------------------
# DISTRIBUTED AGENT FABRIC
# ---------------------------------------------------------

from core.runtime.distributed_agent_fabric import (
    get_distributed_agent_fabric,
)

if "distributed_agent_fabric_initialized" not in st.session_state:

    try:

        storage.distributed_agent_fabric = (
            get_distributed_agent_fabric(
                storage,
                event_bus=event_bus,
                agent_coordinator=getattr(
                    storage,
                    "agent_coordinator",
                    None,
                ),
            )
        )

        st.session_state[
            "distributed_agent_fabric_initialized"
        ] = True

        print(
            "✅ Distributed agent fabric initialized"
        )

    except Exception as e:

        print(
            "⚠️ Distributed agent fabric initialization failed:",
            e,
        )

# ---------------------------------------------------------
# MISSION PLANNER
# ---------------------------------------------------------

from core.ai.orchestration.mission_planner import (
    get_mission_planner,
)

if "mission_planner_initialized" not in st.session_state:

    try:

        storage.mission_planner = (
            get_mission_planner(
                storage,
                event_bus=event_bus,
            )
        )

        st.session_state[
            "mission_planner_initialized"
        ] = True

        print(
            "✅ Mission planner initialized"
        )

    except Exception as e:

        print(
            "⚠️ Mission planner initialization failed:",
            e,
        )

# ---------------------------------------------------------
# MISSION EXECUTION ENGINE
# ---------------------------------------------------------

from core.ai.orchestration.mission_execution_engine import (
    get_mission_execution_engine,
)

if "mission_execution_engine_initialized" not in st.session_state:

    try:

        storage.mission_execution_engine = (
            get_mission_execution_engine(
                storage,
                event_bus=event_bus,
            )
        )

        st.session_state[
            "mission_execution_engine_initialized"
        ] = True

        print(
            "✅ Mission execution engine initialized"
        )

    except Exception as e:

        print(
            "⚠️ Mission execution engine initialization failed:",
            e,
        )

# ============================================================
# EXECUTION GRAPH ENGINE
# ============================================================

execution_graph_engine = get_execution_graph_engine(
    db_path=getattr(
        storage,
        "db_path",
        "data/distributed_execution_queue.db",
    ),

    queue=execution_queue,

    storage=storage,

    event_bus=event_bus,
)

storage.execution_graph_engine = (
    execution_graph_engine
)
# ----------------------------------
# 🚀 START WORKERS (ONCE)
# ----------------------------------

if "workers_started" not in st.session_state:

    print("🚀 INITIALIZING WORKERS")

    # ----------------------------------
    # 🔥 RESET STOP FLAG
    # ----------------------------------

    storage.stop_workers = False

    # ----------------------------------
    # 🔥 START SCAN WORKERS
    # ----------------------------------

    start_scan_workers(storage)

    # ----------------------------------
    # 🔥 SESSION FLAGS
    # ----------------------------------

    st.session_state["workers_started"] = True
    st.session_state["workers_running"] = True

    print("✅ WORKERS STARTED")

else:

    print("ℹ️ Workers already running")
# ----------------------------------
# 🎯 USER ROLE & SIDEBAR
# ----------------------------------

if "user_role" not in st.session_state:
    st.session_state["user_role"] = "ANALYST"

# ----------------------------------
# SIDEBAR - VERIDION PRO (Dark Theme)
# ----------------------------------
with st.sidebar:
    from ui.theme import apply_veridion_pro_theme, veridion_sidebar_logo

    apply_veridion_pro_theme()

    # === VERIDION PRO LOGO (Darker blue VERIDION + bright PRO) ===
    veridion_sidebar_logo()

    st.divider()

    # Help Button
    if st.button("📘 Help / How To", use_container_width=True):
        st.session_state["page"] = "Help Center"
        st.rerun()

    st.divider()

    # Navigation
    st.markdown("**Navigation**")
    st.markdown("**Go to**")

    PAGES = [
        "Admin",
        "Scan",
        "Evidence Viewer",
        "Metrics",
        "Supervisor Dashboard",
        "Trust Center",
        "Alert Settings",
        "Alert Center",
        "Investigation Workspace",
        "Cases",
        "Relationship Graph",
        "Timeline Intelligence",
        "Help Center",
        "Command Center",
    ]

    if "page" not in st.session_state:
        st.session_state["page"] = "Scan"

    page = st.radio(
        label="Go to",
        options=PAGES,
        index=PAGES.index(st.session_state["page"]),
        key="page_radio",
        label_visibility="collapsed"
    )

    if page != st.session_state["page"]:
        st.session_state["page"] = page

    st.divider()

    # User Role + Controls
    st.selectbox("User Role", ["ANALYST", "SENIOR_ANALYST", "MANAGER", "ADMIN"], key="user_role")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛑 Stop", use_container_width=True):
            stop_scan_workers(storage)
            st.session_state["workers_running"] = False
    with col2:
        if st.button("🚀 Start", use_container_width=True):
            storage.stop_workers = False
            start_scan_workers(storage)
            st.session_state["workers_running"] = True

# ---------------------------
# ROUTER
# ---------------------------

if page == "Admin":
    render_admin_page(storage)

elif page == "Scan":
    render_scan_page(storage)

elif page == "Evidence Viewer":
    render_evidence_viewer(storage)

elif page == "Metrics":
    render_metrics_page(storage)

elif page == "Supervisor Dashboard":
    render_supervisor_dashboard(storage)

elif page == "Trust Center":
    render_trust_center_page(storage)

elif page == "Alert Settings":
    render_alert_settings_page(storage)

elif page == "Alert Center":
    render_alert_center_page(storage)

elif page == "Investigation Workspace":
    render_investigation_page(storage)

elif page == "Cases":
    selected_case_id = st.session_state.get("selected_case_id")
    if selected_case_id:
        render_case_workspace(storage, selected_case_id)
    else:
        render_case_queue(storage)

elif page == "Relationship Graph":
    render_relationship_graph(storage)

elif page == "Timeline Intelligence":
    render_timeline_page(storage)

elif page == "Help Center":
    render_help_page(storage)

elif page == "Command Center":
    from ui.copilot.command_center_workspace import render_command_center_workspace

    render_command_center_workspace(storage)