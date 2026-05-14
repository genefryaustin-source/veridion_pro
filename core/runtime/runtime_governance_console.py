"""
ui/copilot/runtime_governance_console.py

Runtime Governance Console.

Purpose:
- runtime governance visibility
- runtime health cognition
- dependency topology awareness
- policy violation operations
- quarantine management
- lifecycle/recovery operations
- operational control plane
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


def _health_icon(status: str) -> str:
    status = str(status or "").upper()

    mapping = {
        "READY": "🟢",
        "RUNNING": "🟢",
        "HEALTHY": "🟢",

        "DEGRADED": "🟡",

        "UNAVAILABLE": "🔴",
        "FAILED": "🔴",
        "CRITICAL": "🔴",

        "QUARANTINED": "🟣",

        "STOPPED": "⚫",

        "UNKNOWN": "⚪",
    }

    return mapping.get(status, "⚪")


def render_runtime_governance_console(
    storage: Any,
) -> None:

    st.markdown(
        "# 🛡️ Runtime Governance Console"
    )

    st.caption(
        "Operational governance and runtime cognition layer."
    )

    registry = getattr(
        storage,
        "runtime_service_registry",
        None,
    )

    lifecycle = getattr(
        storage,
        "runtime_lifecycle_manager",
        None,
    )

    policy = getattr(
        storage,
        "runtime_policy_manager",
        None,
    )

    health = getattr(
        storage,
        "runtime_health_manager",
        None,
    )

    dependency_graph = getattr(
        storage,
        "runtime_dependency_graph",
        None,
    )

    if registry is None:
        st.error(
            "Runtime service registry unavailable."
        )
        return

    # ========================================================
    # TOP-LEVEL STATUS
    # ========================================================

    st.markdown(
        "## 🌐 Runtime Status"
    )

    registry_stats = (
        registry.service_stats()
        if hasattr(
            registry,
            "service_stats",
        )
        else {}
    )

    runtime_health = (
        health.evaluate()
        if health is not None
        else None
    )

    runtime_health_dict = (
        runtime_health.to_dict()
        if runtime_health
        and hasattr(runtime_health, "to_dict")
        else {}
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Services",
        registry_stats.get(
            "total_services",
            0,
        ),
    )

    c2.metric(
        "Healthy",
        registry_stats.get(
            "ready",
            0,
        ),
    )

    c3.metric(
        "Degraded",
        registry_stats.get(
            "degraded",
            0,
        ),
    )

    c4.metric(
        "Quarantined",
        registry_stats.get(
            "quarantined",
            0,
        ),
    )

    c5.metric(
        "Runtime Risk",
        runtime_health_dict.get(
            "risk",
            "UNKNOWN",
        ),
    )

    st.markdown("---")

    # ========================================================
    # RUNTIME HEALTH
    # ========================================================

    st.markdown(
        "## ❤️ Runtime Health Cognition"
    )

    if runtime_health_dict:

        h1, h2, h3 = st.columns(3)

        h1.metric(
            "Health",
            runtime_health_dict.get(
                "health",
                "UNKNOWN",
            ),
        )

        h2.metric(
            "Score",
            round(
                runtime_health_dict.get(
                    "score",
                    0.0,
                ),
                2,
            ),
        )

        h3.metric(
            "Risk",
            runtime_health_dict.get(
                "risk",
                "UNKNOWN",
            ),
        )

        findings = runtime_health_dict.get(
            "findings",
            [],
        )

        if findings:

            st.markdown(
                "### ⚠️ Runtime Findings"
            )

            findings_df = pd.DataFrame(
                findings
            )

            st.dataframe(
                findings_df,
                use_container_width=True,
                height=220,
            )

        recommendations = (
            runtime_health_dict.get(
                "recommendations",
                [],
            )
        )

        if recommendations:

            st.markdown(
                "### 🧠 Recovery Recommendations"
            )

            rec_df = pd.DataFrame(
                recommendations
            )

            st.dataframe(
                rec_df,
                use_container_width=True,
                height=220,
            )

    st.markdown("---")

    # ========================================================
    # SERVICE REGISTRY
    # ========================================================

    st.markdown(
        "## 🛰️ Runtime Service Registry"
    )

    services = registry.list_services()

    rows = []

    for record in services:

        rows.append({

            "Service":
                (
                    f"{_health_icon(record.status)} "
                    f"{record.service_name}"
                ),

            "Status":
                record.status,

            "Health":
                round(
                    getattr(
                        record,
                        "health_score",
                        100.0,
                    ),
                    2,
                ),

            "Owner":
                getattr(
                    record,
                    "owner",
                    "system",
                ),

            "Tenant":
                getattr(
                    record,
                    "tenant_id",
                    "default",
                ),

            "Dependencies":
                ", ".join(
                    getattr(
                        record,
                        "dependencies",
                        [],
                    )
                ),

            "Errors":
                getattr(
                    record,
                    "error_count",
                    0,
                ),

            "Warnings":
                getattr(
                    record,
                    "warning_count",
                    0,
                ),

            "Updated":
                _fmt_ts(
                    getattr(
                        record,
                        "updated_at_ms",
                        None,
                    )
                ),
        })

    if rows:

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            height=420,
        )

    st.markdown("---")

    # ========================================================
    # POLICY GOVERNANCE
    # ========================================================

    st.markdown(
        "## ⚖️ Runtime Policy Governance"
    )

    if policy is not None:

        policy_status = (
            policy.policy_status()
        )

        p1, p2, p3, p4 = st.columns(4)

        p1.metric(
            "Policy Mode",
            policy_status.get(
                "policy_mode",
                "UNKNOWN",
            ),
        )

        p2.metric(
            "Violations",
            policy_status.get(
                "violation_count",
                0,
            ),
        )

        p3.metric(
            "Warnings",
            policy_status.get(
                "warning_count",
                0,
            ),
        )

        p4.metric(
            "Quarantined",
            len(
                policy_status.get(
                    "quarantined_services",
                    [],
                )
            ),
        )

        policy_events = (
            policy.list_events(
                limit=200,
            )
        )

        if policy_events:

            st.markdown(
                "### 🚨 Policy Events"
            )

            events_df = pd.DataFrame(
                policy_events
            )

            st.dataframe(
                events_df,
                use_container_width=True,
                height=320,
            )

    st.markdown("---")

    # ========================================================
    # DEPENDENCY TOPOLOGY
    # ========================================================

    st.markdown(
        "## 🕸️ Runtime Dependency Topology"
    )

    if dependency_graph is not None:

        validation = (
            dependency_graph.validate()
        )

        d1, d2, d3, d4 = st.columns(4)

        d1.metric(
            "Nodes",
            validation.get(
                "node_count",
                0,
            ),
        )

        d2.metric(
            "Edges",
            validation.get(
                "edge_count",
                0,
            ),
        )

        d3.metric(
            "Cycles",
            len(
                validation.get(
                    "cycles",
                    [],
                )
            ),
        )

        d4.metric(
            "Orphaned",
            len(
                validation.get(
                    "orphaned_services",
                    [],
                )
            ),
        )

        topology = (
            dependency_graph.visualization_payload()
        )

        edges = topology.get(
            "edges",
            [],
        )

        if edges:

            st.markdown(
                "### 🔗 Service Dependencies"
            )

            dep_rows = []

            for edge in edges:

                dep_rows.append({

                    "Dependency":
                        (
                            f"{edge['source']} "
                            f"→ "
                            f"{edge['target']}"
                        ),

                    "Type":
                        edge.get(
                            "type",
                            "UNKNOWN",
                        ),
                })

            st.dataframe(
                pd.DataFrame(dep_rows),
                use_container_width=True,
                height=320,
            )

        cycles = validation.get(
            "cycles",
            [],
        )

        if cycles:

            st.markdown(
                "### 🔥 Dependency Cycles"
            )

            cycle_rows = []

            for cycle in cycles:

                cycle_rows.append({
                    "Cycle":
                        " → ".join(cycle)
                })

            st.dataframe(
                pd.DataFrame(cycle_rows),
                use_container_width=True,
                height=180,
            )

    st.markdown("---")

    # ========================================================
    # QUARANTINE OPERATIONS
    # ========================================================

    st.markdown(
        "## 🚨 Quarantine Operations"
    )

    service_names = sorted([
        getattr(
            s,
            "service_name",
            "unknown",
        )
        for s in services
    ])

    if service_names:

        selected_service = st.selectbox(
            "Select Service",
            service_names,
            key="runtime_governance_service",
        )

        q1, q2, q3 = st.columns(3)

        with q1:

            if st.button(
                "Quarantine Service",
                key="runtime_quarantine_btn",
            ):

                if policy is not None:

                    result = (
                        policy.quarantine_service(
                            selected_service,
                            reason=(
                                "manual_runtime_governance"
                            ),
                        )
                    )

                    st.warning(
                        f"Service quarantined: "
                        f"{selected_service}"
                    )

        with q2:

            if st.button(
                "Restore Service",
                key="runtime_restore_btn",
            ):

                if policy is not None:

                    policy.clear_quarantine(
                        selected_service,
                    )

                    st.success(
                        f"Service restored: "
                        f"{selected_service}"
                    )

        with q3:

            if st.button(
                "Analyze Blast Radius",
                key="runtime_blast_radius_btn",
            ):

                if dependency_graph is not None:

                    radius = (
                        dependency_graph
                        .blast_radius(
                            selected_service
                        )
                    )

                    st.json(radius)

    st.markdown("---")

    # ========================================================
    # LIFECYCLE OPERATIONS
    # ========================================================

    st.markdown(
        "## 🔄 Runtime Lifecycle Operations"
    )

    if lifecycle is not None:

        selected_runtime_service = (
            st.selectbox(
                "Lifecycle Service",
                service_names,
                key="runtime_lifecycle_service",
            )
        )

        l1, l2, l3 = st.columns(3)

        with l1:

            if st.button(
                "Restart Service",
                key="runtime_restart_btn",
            ):

                result = (
                    lifecycle.restart_service(
                        selected_runtime_service,
                    )
                )

                st.success(
                    result.message
                )

        with l2:

            if st.button(
                "Stop Service",
                key="runtime_stop_btn",
            ):

                result = (
                    lifecycle.stop_service(
                        selected_runtime_service,
                    )
                )

                st.warning(
                    result.message
                )

        with l3:

            if st.button(
                "Start Service",
                key="runtime_start_btn",
            ):

                result = (
                    lifecycle.start_service(
                        selected_runtime_service,
                    )
                )

                st.success(
                    result.message
                )

    st.markdown("---")

    # ========================================================
    # AUDIT TRAIL
    # ========================================================

    st.markdown(
        "## 📜 Runtime Audit Trail"
    )

    audit_rows: List[Dict[str, Any]] = []

    # Policy events
    if policy is not None:

        try:

            events = policy.list_events(
                limit=100,
            )

            for event in events:

                audit_rows.append({

                    "Time":
                        _fmt_ts(
                            event.get(
                                "created_at_ms"
                            )
                        ),

                    "Source":
                        event.get(
                            "source_service"
                        ),

                    "Type":
                        event.get(
                            "event_type"
                        ),

                    "Severity":
                        event.get(
                            "severity"
                        ),

                    "Message":
                        event.get(
                            "message"
                        ),
                })

        except Exception:
            pass

    # Health signals
    if health is not None:

        try:

            signals = health.list_signals(
                limit=100,
            )

            for signal in signals:

                audit_rows.append({

                    "Time":
                        _fmt_ts(
                            signal.get(
                                "created_at_ms"
                            )
                        ),

                    "Source":
                        signal.get(
                            "service_name"
                        ),

                    "Type":
                        signal.get(
                            "signal_type"
                        ),

                    "Severity":
                        signal.get(
                            "severity"
                        ),

                    "Message":
                        signal.get(
                            "message"
                        ),
                })

        except Exception:
            pass

    if audit_rows:

        audit_rows = sorted(
            audit_rows,
            key=lambda x: x["Time"],
            reverse=True,
        )

        st.dataframe(
            pd.DataFrame(audit_rows),
            use_container_width=True,
            height=420,
        )

    st.markdown("---")

    # ========================================================
    # AUTO REFRESH
    # ========================================================

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="runtime_governance_refresh",
    )

    if auto_refresh:

        time.sleep(5)

        st.rerun()