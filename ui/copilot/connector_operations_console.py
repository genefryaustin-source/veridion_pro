"""
ui/copilot/connector_operations_console.py

Connector Operations Console.

Operational infrastructure UI for:
- connector health
- auth visibility
- failover topology
- routing visibility
- degraded providers
- quarantine state
- execution pressure
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.connectors.connector_registry import (
    get_connector_registry,
)

from core.connectors.connector_health_monitor import (
    get_connector_health_monitor,
)


# ============================================================
# MAIN RENDER
# ============================================================

def render_connector_operations_console():

    st.subheader("🔌 Connector Operations Console")

    registry = get_connector_registry()
    monitor = get_connector_health_monitor()

    # ========================================================
    # SUMMARY
    # ========================================================

    stats = registry.stats()
    health_stats = monitor.stats()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Connectors", stats["total"])
    c2.metric("Enabled", stats["enabled"])
    c3.metric("Quarantined", stats["quarantined"])
    c4.metric("Outages", health_stats["outage"])

    st.markdown("---")

    # ========================================================
    # CONNECTOR TABLE
    # ========================================================

    rows = []

    registrations = registry.list_connectors()

    for reg in registrations:
        connector_name = (
                reg.get("connector_id")
                or reg.get("name")
                or "unknown"
        )

        health = monitor.get_state(
            connector_name
        )

        rows.append({

            "Connector": (
                    reg.get("connector_id")
                    or reg.get("name")
                    or "unknown"
            ),

            "Enabled": reg.get(
                "healthy",
                True,
            ),

            "Quarantined": reg.get(
                "quarantined",
                False,
            ),

            "Priority": reg.get(
                "priority",
                100,
            ),

            "Capabilities": ", ".join(
                reg.get(
                    "capabilities",
                    [],
                )
            ),

            "Health": getattr(
                health,
                "health",
                "UNKNOWN",
            ),

            "Failures": getattr(
                health,
                "failure_count",
                0,
            ),

            "Retries": getattr(
                health,
                "retry_count",
                0,
            ),

            "Auth Failures": getattr(
                health,
                "auth_failures",
                0,
            ),

            "Latency(ms)": round(
                getattr(
                    health,
                    "avg_latency_ms",
                    0.0,
                ),
                2,
            ),
        })

    df = pd.DataFrame(rows)

    if df.empty:
        st.info("No connectors registered.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        height=350,
    )

    st.markdown("---")

    # ========================================================
    # FAILOVER TOPOLOGY
    # ========================================================

    st.markdown("### 🔄 Failover Topology")

    capabilities = set()

    for reg in registrations:

        reg_capabilities = reg.get(
            "capabilities",
            [],
        )

        if isinstance(
                reg_capabilities,
                (list, set, tuple),
        ):
            capabilities.update(
                reg_capabilities
            )

    topology_rows = []

    for capability in sorted(capabilities):

        try:

            chain = registry.get_failover_chain(
                capability
            )

        except Exception:

            chain = []

        topology_rows.append({

            "Capability": capability,

            "Failover Chain": (
                " → ".join(chain)
                if chain
                else "No failover chain"
            ),
        })

    topology_df = pd.DataFrame(
        topology_rows
    )

    st.dataframe(
        topology_df,
        use_container_width=True,
        height=250,
    )

    st.markdown("---")

    # ========================================================
    # QUARANTINE OPERATIONS
    # ========================================================

    st.markdown("### 🚨 Quarantine Controls")

    selected_connector = st.selectbox(
        "Connector",
        [
            r.get("connector_id")
            or r.get("name")
            or "unknown"
            for r in registrations
        ],
        key="connector_console_select",
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Quarantine Connector",
            key="quarantine_connector_btn",
        ):

            registry.quarantine(
                selected_connector,
                reason="manual_operator_quarantine",
            )

            st.warning(
                f"{selected_connector} quarantined."
            )

    with col2:

        if st.button(
            "Clear Quarantine",
            key="clear_quarantine_btn",
        ):

            registry.clear_quarantine(selected_connector)

            st.success(
                f"{selected_connector} restored."
            )