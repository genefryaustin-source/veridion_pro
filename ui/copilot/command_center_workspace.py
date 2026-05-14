import streamlit as st

from ui.copilot.autonomous_control_panel import (
    render_autonomous_control_panel,
)

from ui.copilot.execution_timeline import (
    render_execution_timeline,
)

from ui.copilot.governance_queue import (
    render_governance_queue,
)

from ui.copilot.forensic_replay_panel import (
    render_forensic_replay_panel,
)

from ui.copilot.operational_memory_panel import (
    render_operational_memory_panel,
)

from ui.copilot.policy_insight_panel import (
    render_policy_insight_panel,
)

from ui.copilot.autonomous_operations_panel import (
    render_autonomous_operations_panel,
)

from ui.copilot.governance_heatmap import (
    render_governance_heatmap,
)

from ui.copilot.live_execution_stream import (
    render_live_execution_stream,
)

from ui.copilot.multi_agent_console import (
    render_multi_agent_console,
)

from ui.copilot.autonomous_soc_dashboard import (
    render_autonomous_soc_dashboard,
)

try:
    from core.events.event_subscribers import (
        initialize_event_subscribers,
    )
except Exception:
    initialize_event_subscribers = None

from ui.copilot.distributed_operations_map import (
    render_distributed_operations_map,
)
from ui.copilot.autonomous_execution_grid import render_autonomous_execution_grid
from ui.copilot.connector_operations_console import render_connector_operations_console
from ui.copilot.governance_war_room import render_governance_war_room
from ui.copilot.safety_guardrails_console import (
    render_safety_guardrails_console,
)
from ui.copilot.agent_operations_console import (
    render_agent_operations_console,
)
from ui.copilot.distributed_agent_fabric_console import (
    render_distributed_agent_fabric_console,
)
from ui.copilot.mission_planner_console import (
    render_mission_planner_console,
)
# ============================================================
# COMMAND CENTER WORKSPACE
# ============================================================

def render_command_center_workspace(storage):

    # ========================================================
    # INITIALIZE EVENT FABRIC
    # ========================================================

    try:
        if initialize_event_subscribers:
            initialize_event_subscribers()
    except Exception as e:
        st.warning(f"Event subscriber initialization warning: {e}")

    # ========================================================
    # HEADER
    # ========================================================

    st.title("🧠 Autonomous SOC Command Center")

    st.caption(
        "Governance, forensic replay, operational memory, policy intelligence, "
        "multi-agent orchestration, autonomous containment operations, "
        "and executive SOC telemetry."
    )

    st.markdown("---")

    # ========================================================
    # MAIN TABS
    # ========================================================

    (
        tab_control,
        tab_execution,
        tab_governance,
        tab_memory,
        tab_policy,
        tab_forensics,
        tab_multi_agent,
        tab_autonomous,
        tab_ops_map,
        tab_execution_grid,
        tab_connectors,
        tab_war_room,
        tab_safety,
        tab_agents,
        tab_fabric,
        tab_mission_planner,
    ) = st.tabs([
        "Control",
        "Live Execution",
        "Governance Queue",
        "Operational Memory",
        "Policy Insights",
        "Forensic Replay",
        "Multi-Agent SOC",
        "Autonomous Dashboard",
        "Ops Map",
        "Execution Grid",
        "Connectors",
        "War Room",
        "Safety",
        "Agents",
        "Fabric",
        "Mission Planner",
    ])

    # ========================================================
    # CONTROL TAB
    # ========================================================

    with tab_control:

        try:
            render_autonomous_control_panel(storage)

        except Exception as e:
            st.error(f"Autonomous Control Panel error: {e}")

    # ========================================================
    # EXECUTION TAB
    # ========================================================

    with tab_execution:

        try:
            render_execution_timeline(storage)

        except Exception as e:
            st.error(f"Execution Timeline error: {e}")

        st.markdown("---")

        try:
            render_live_execution_stream(storage)

        except Exception as e:
            st.error(f"Live Execution Stream error: {e}")

    # ========================================================
    # GOVERNANCE TAB
    # ========================================================

    with tab_governance:

        try:
            render_governance_queue(storage)

        except Exception as e:
            st.error(f"Governance Queue error: {e}")

        st.markdown("---")

        try:
            render_governance_heatmap(storage)

        except Exception as e:
            st.error(f"Governance Heatmap error: {e}")

    # ========================================================
    # MEMORY TAB
    # ========================================================

    with tab_memory:

        try:
            render_operational_memory_panel(storage)

        except Exception as e:
            st.error(f"Operational Memory Panel error: {e}")

    # ========================================================
    # POLICY TAB
    # ========================================================

    with tab_policy:

        try:
            render_policy_insight_panel(storage)

        except Exception as e:
            st.error(f"Policy Insight Panel error: {e}")

    # ========================================================
    # FORENSICS TAB
    # ========================================================

    with tab_forensics:

        try:
            render_forensic_replay_panel(storage)

        except Exception as e:
            st.error(f"Forensic Replay Panel error: {e}")

    # ========================================================
    # MULTI-AGENT SOC TAB
    # ========================================================

    with tab_multi_agent:

        try:
            render_multi_agent_console(storage)

        except Exception as e:
            st.error(f"Multi-Agent Console error: {e}")

    # ========================================================
    # AUTONOMOUS DASHBOARD TAB
    # ========================================================

    with tab_autonomous:

        try:
            render_autonomous_soc_dashboard(storage)

        except Exception as e:
            st.error(f"Autonomous SOC Dashboard error: {e}")


    # ========================================================
    # OPS MAP TAB
    # ========================================================


    with tab_ops_map:
        try:
            render_distributed_operations_map(storage)
        except Exception as e:
            st.error(f"Distributed Operations Map error: {e}")

    # ========================================================
    # GLOBAL AUTONOMOUS OPERATIONS PANEL
    # ========================================================

    st.markdown("---")

    try:
        render_autonomous_operations_panel(storage)

    except Exception as e:
        st.error(f"Autonomous Operations Panel error: {e}")

    with tab_execution_grid:
        render_autonomous_execution_grid(storage)

    with tab_connectors:
        render_connector_operations_console()

    with tab_war_room:
        render_governance_war_room(storage)

    with tab_safety:
        render_safety_guardrails_console(
            storage,
            event_bus=getattr(
                storage,
                "event_bus",
                None,
            ),
        )

    with (tab_agents):

        render_agent_operations_console(
            storage
        )

    with tab_fabric:

        render_distributed_agent_fabric_console(
            storage
        )

    with tab_mission_planner:

        render_mission_planner_console(
            storage
        )