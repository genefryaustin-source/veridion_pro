"""
ui/copilot/runtime_federation_console.py

Distributed Runtime Federation Console.

Purpose:
- federated runtime governance UI
- distributed runtime topology visibility
- runtime placement visibility
- failover awareness
- sovereignty / trust boundary visibility
- GovCloud runtime awareness
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


def _fmt_ts(ms: Any) -> str:
    if not ms:
        return "-"

    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ms) / 1000),
        )
    except Exception:
        return str(ms)


def _status_icon(status: str) -> str:
    status = str(status or "").upper()

    mapping = {
        "ONLINE": "🟢",
        "DEGRADED": "🟡",
        "OFFLINE": "🔴",
        "QUARANTINED": "🟠",
        "MAINTENANCE": "🔵",
    }

    return mapping.get(status, "⚪")


def _domain_icon(domain: str) -> str:
    domain = str(domain or "").upper()

    mapping = {
        "LOCAL": "💻",
        "STANDALONE": "🖥️",
        "DISTRIBUTED": "🌐",
        "GOVCLOUD": "🏛️",
        "AIRGAPPED": "🔒",
        "CUSTOMER_ISOLATED": "🏢",
    }

    return mapping.get(domain, "⚪")


def _risk_icon(level: str) -> str:
    level = str(level or "").upper()

    mapping = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴",
    }

    return mapping.get(level, "⚪")


def render_runtime_federation_console(
    storage: Any,
) -> None:

    st.markdown(
        "# 🌐 Runtime Federation Console"
    )

    st.caption(
        "Distributed runtime topology governance and operational federation."
    )

    federation = getattr(
        storage,
        "runtime_federation_manager",
        None,
    )

    if federation is None:

        st.warning(
            "Runtime federation manager unavailable."
        )

        st.info(
            "Federation may be disabled in runtime_bootstrap(enable_federation=False)."
        )

        return

    # ========================================================
    # FEDERATION HEALTH
    # ========================================================

    st.markdown(
        "## 🌍 Federation Health"
    )

    try:

        health = federation.federation_health()

        c1, c2, c3, c4, c5, c6 = st.columns(6)

        c1.metric(
            "Runtimes",
            health.get(
                "total_runtimes",
                0,
            ),
        )

        c2.metric(
            "Online",
            health.get(
                "online",
                0,
            ),
        )

        c3.metric(
            "Degraded",
            health.get(
                "degraded",
                0,
            ),
        )

        c4.metric(
            "Offline",
            health.get(
                "offline",
                0,
            ),
        )

        c5.metric(
            "Quarantined",
            health.get(
                "quarantined",
                0,
            ),
        )

        risk = health.get(
            "risk",
            "UNKNOWN",
        )

        c6.metric(
            "Risk",
            f"{_risk_icon(risk)} {risk}",
        )

        st.progress(
            min(
                max(
                    float(
                        health.get(
                            "avg_health",
                            0.0,
                        )
                    ) / 100.0,
                    0.0,
                ),
                1.0,
            )
        )

        st.caption(
            f"Average Federation Health: {health.get('avg_health', 0.0)}"
        )

    except Exception as e:

        st.error(
            f"Federation health failed: {e}"
        )

    st.markdown("---")

    # ========================================================
    # RUNTIME TOPOLOGY
    # ========================================================

    st.markdown(
        "## 🕸️ Runtime Topology"
    )

    try:

        runtimes = federation.list_runtimes()

        if runtimes:

            rows = []

            for rt in runtimes:

                rows.append({

                    "Runtime":
                        rt.get(
                            "runtime_id",
                            "-"
                        ),

                    "Name":
                        rt.get(
                            "name",
                            "-"
                        ),

                    "Domain":
                        (
                            f"{_domain_icon(rt.get('domain_type'))} "
                            f"{rt.get('domain_type')}"
                        ),

                    "Region":
                        rt.get(
                            "region",
                            "-"
                        ),

                    "Status":
                        (
                            f"{_status_icon(rt.get('status'))} "
                            f"{rt.get('status')}"
                        ),

                    "Trust":
                        rt.get(
                            "trust_level",
                            "-"
                        ),

                    "Health":
                        round(
                            float(
                                rt.get(
                                    "health_score",
                                    0.0,
                                )
                            ),
                            2,
                        ),

                    "Risk":
                        (
                            f"{_risk_icon(rt.get('risk_level'))} "
                            f"{rt.get('risk_level')}"
                        ),

                    "Capacity":
                        (
                            f"{rt.get('active_units', 0)}"
                            f"/"
                            f"{rt.get('capacity_units', 0)}"
                        ),

                    "Capabilities":
                        ", ".join(
                            rt.get(
                                "capabilities",
                                [],
                            )[:5]
                        ),

                    "Tenants":
                        ", ".join(
                            rt.get(
                                "tenant_affinity",
                                [],
                            )[:5]
                        ),

                    "Heartbeat":
                        _fmt_ts(
                            rt.get(
                                "last_heartbeat_ms"
                            )
                        ),
                })

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                height=420,
            )

        else:

            st.info(
                "No federated runtimes registered."
            )

    except Exception as e:

        st.error(
            f"Runtime topology load failed: {e}"
        )

    st.markdown("---")

    # ========================================================
    # TOPOLOGY GRAPH DATA
    # ========================================================

    st.markdown(
        "## 🔗 Federation Topology Graph"
    )

    try:

        topology = federation.federation_topology()

        st.json({
            "nodes": len(
                topology.get(
                    "nodes",
                    [],
                )
            ),
            "edges": len(
                topology.get(
                    "edges",
                    [],
                )
            ),
            "health": topology.get(
                "health",
                {},
            ),
        })

        with st.expander(
            "View Full Topology JSON"
        ):

            st.json(topology)

    except Exception as e:

        st.error(
            f"Topology graph failed: {e}"
        )

    st.markdown("---")

    # ========================================================
    # FEDERATED PLACEMENT TEST
    # ========================================================

    st.markdown(
        "## 🚦 Placement Decision Simulator"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="fed_sim_tenant",
        )

    with col2:

        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="fed_sim_capability",
        )

    with col3:

        require_govcloud = st.checkbox(
            "Require GovCloud",
            value=False,
            key="fed_sim_govcloud",
        )

    require_high_trust = st.checkbox(
        "Require High Trust",
        value=False,
        key="fed_sim_high_trust",
    )

    if st.button(
        "Simulate Placement",
        use_container_width=True,
        key="simulate_federation_placement",
    ):

        try:

            decision = federation.choose_runtime(
                tenant_id=tenant_id,
                capability=capability,
                require_govcloud=require_govcloud,
                require_high_trust=require_high_trust,
            )

            st.success(
                "Placement simulation completed."
            )

            st.json(
                decision.to_dict()
                if hasattr(
                    decision,
                    "to_dict",
                )
                else decision
            )

        except Exception as e:

            st.error(
                f"Placement simulation failed: {e}"
            )

    st.markdown("---")

    # ========================================================
    # PLACEMENT DECISIONS
    # ========================================================

    st.markdown(
        "## 🧭 Placement Decisions"
    )

    try:

        decisions = federation.list_decisions(
            limit=100,
        )

        if decisions:

            rows = []

            for d in decisions:

                rows.append({

                    "Decision":
                        d.get(
                            "decision_id",
                            "-"
                        ),

                    "Tenant":
                        d.get(
                            "tenant_id",
                            "-"
                        ),

                    "Capability":
                        d.get(
                            "capability",
                            "-"
                        ),

                    "Status":
                        d.get(
                            "status",
                            "-"
                        ),

                    "Selected Runtime":
                        d.get(
                            "selected_runtime_id",
                            "-"
                        ),

                    "Allowed":
                        d.get(
                            "allowed",
                            False,
                        ),

                    "Candidates":
                        len(
                            d.get(
                                "candidate_runtime_ids",
                                [],
                            )
                        ),

                    "Blocked":
                        len(
                            d.get(
                                "blocked_runtime_ids",
                                [],
                            )
                        ),

                    "Reason":
                        d.get(
                            "reason",
                            "-"
                        ),

                    "Created":
                        _fmt_ts(
                            d.get(
                                "created_at_ms"
                            )
                        ),
                })

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                height=420,
            )

        else:

            st.info(
                "No placement decisions available."
            )

    except Exception as e:

        st.error(
            f"Placement decisions failed: {e}"
        )

    st.markdown("---")

    # ========================================================
    # FAILOVER OPERATIONS
    # ========================================================

    st.markdown(
        "## 🔄 Runtime Failover Planning"
    )

    runtimes = federation.list_runtimes()

    runtime_ids = [
        r.get("runtime_id")
        for r in runtimes
    ]

    if runtime_ids:

        selected_runtime = st.selectbox(
            "Failed Runtime",
            runtime_ids,
            key="failover_runtime_select",
        )

        failover_tenant = st.text_input(
            "Tenant",
            value="default",
            key="failover_tenant",
        )

        failover_capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="failover_capability",
        )

        if st.button(
            "Generate Failover Plan",
            use_container_width=True,
            key="generate_failover_plan",
        ):

            try:

                plan = federation.failover_plan(
                    failed_runtime_id=selected_runtime,
                    tenant_id=failover_tenant,
                    capability=failover_capability,
                )

                st.success(
                    "Failover plan generated."
                )

                st.json(plan)

            except Exception as e:

                st.error(
                    f"Failover planning failed: {e}"
                )

    st.markdown("---")

    # ========================================================
    # RUNTIME CONTROL OPERATIONS
    # ========================================================

    st.markdown(
        "## 🎛️ Runtime Control Operations"
    )

    ctl1, ctl2 = st.columns(2)

    with ctl1:

        quarantine_runtime = st.selectbox(
            "Quarantine Runtime",
            runtime_ids,
            key="quarantine_runtime",
        )

        quarantine_reason = st.text_input(
            "Quarantine Reason",
            value="manual_operator_quarantine",
            key="quarantine_reason",
        )

        if st.button(
            "Quarantine Runtime",
            use_container_width=True,
            key="quarantine_runtime_btn",
        ):

            try:

                federation.quarantine_runtime(
                    quarantine_runtime,
                    reason=quarantine_reason,
                )

                st.warning(
                    "Runtime quarantined."
                )

            except Exception as e:

                st.error(
                    f"Quarantine failed: {e}"
                )

    with ctl2:

        restore_runtime = st.selectbox(
            "Restore Runtime",
            runtime_ids,
            key="restore_runtime",
        )

        if st.button(
            "Restore Runtime",
            use_container_width=True,
            key="restore_runtime_btn",
        ):

            try:

                federation.restore_runtime(
                    restore_runtime
                )

                st.success(
                    "Runtime restored."
                )

            except Exception as e:

                st.error(
                    f"Runtime restore failed: {e}"
                )

    st.markdown("---")

    # ========================================================
    # AUTO REFRESH
    # ========================================================

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="runtime_federation_auto_refresh",
    )

    if auto_refresh:

        time.sleep(5)

        st.rerun()