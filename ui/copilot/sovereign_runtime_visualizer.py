"""
ui/copilot/sovereign_runtime_visualizer.py

Sovereign Runtime Visualizer.

Purpose:
- live sovereign runtime fabric map
- cluster / runtime / domain topology visibility
- federated route visibility
- sovereign domain overlays
- cluster health and failover awareness
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


def _icon(value: str) -> str:
    value = str(value or "").upper()

    if value in {"ACTIVE", "ONLINE", "ALLOWED", "LOCAL", "READY", "LOW"}:
        return "🟢"

    if value in {"DEGRADED", "REQUIRES_APPROVAL", "MEDIUM", "DRAINING"}:
        return "🟡"

    if value in {"HIGH", "QUARANTINED", "FROZEN", "BLOCKED"}:
        return "🟠"

    if value in {"CRITICAL", "OFFLINE", "FAILED", "LOCKDOWN"}:
        return "🔴"

    if value in {"GOVCLOUD", "CLASSIFIED", "AIRGAPPED", "EXPORT_CONTROLLED"}:
        return "🏛️"

    if value in {"CUSTOMER_ISOLATED", "COMMERCIAL"}:
        return "🏢"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def render_sovereign_runtime_visualizer(
    storage: Any,
) -> None:
    st.markdown("# 🛰️ Sovereign Runtime Fabric Map")
    st.caption(
        "Live fabric-level visibility across clusters, runtimes, execution domains, federation, and sovereign routes."
    )

    cluster_manager = getattr(
        storage,
        "distributed_runtime_cluster_manager",
        None,
    )

    federation_manager = getattr(
        storage,
        "runtime_federation_manager",
        None,
    )

    domain_manager = getattr(
        storage,
        "execution_domain_manager",
        None,
    )

    sovereign_controller = getattr(
        storage,
        "sovereign_execution_controller",
        None,
    )

    federated_router = getattr(
        storage,
        "federated_execution_router",
        None,
    )

    supervisor = getattr(
        storage,
        "autonomous_runtime_supervisor",
        None,
    )

    if (
        cluster_manager is None
        and federation_manager is None
        and domain_manager is None
    ):
        st.error(
            "Sovereign runtime fabric services are unavailable."
        )
        return

    # ========================================================
    # FABRIC STATUS
    # ========================================================

    st.markdown("## 🌐 Fabric Status")

    cluster_health = {}
    federation_health = {}
    domain_health = {}
    sovereignty_status = {}
    routing_status = {}
    supervisor_status = {}

    try:
        if cluster_manager is not None:
            cluster_health = cluster_manager.cluster_health()
    except Exception as exc:
        cluster_health = {"error": str(exc)}

    try:
        if federation_manager is not None:
            federation_health = federation_manager.federation_health()
    except Exception as exc:
        federation_health = {"error": str(exc)}

    try:
        if domain_manager is not None:
            domain_health = domain_manager.domain_health()
    except Exception as exc:
        domain_health = {"error": str(exc)}

    try:
        if sovereign_controller is not None:
            sovereignty_status = sovereign_controller.sovereignty_status()
    except Exception as exc:
        sovereignty_status = {"error": str(exc)}

    try:
        if federated_router is not None:
            routing_status = federated_router.routing_status()
    except Exception as exc:
        routing_status = {"error": str(exc)}

    try:
        if supervisor is not None:
            supervisor_status = supervisor.status_snapshot()
    except Exception as exc:
        supervisor_status = {"error": str(exc)}

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Clusters",
        cluster_health.get("total_clusters", 0),
    )

    c2.metric(
        "Runtimes",
        federation_health.get("total_runtimes", 0),
    )

    c3.metric(
        "Domains",
        domain_health.get("total_domains", 0),
    )

    c4.metric(
        "Sovereign Blocks",
        sovereignty_status.get("blocked", 0),
    )

    c5.metric(
        "Federated Routes",
        routing_status.get("federated_routes", 0),
    )

    runtime_mode = supervisor_status.get(
        "runtime_mode",
        "UNKNOWN",
    )

    c6.metric(
        "Runtime Mode",
        f"{_icon(runtime_mode)} {runtime_mode}",
    )

    st.markdown("---")

    # ========================================================
    # CLUSTER MAP
    # ========================================================

    st.markdown("## 🧱 Cluster Fabric")

    if cluster_manager is not None:
        try:
            clusters = cluster_manager.list_clusters()

            cluster_rows = []

            for cluster in clusters:
                cluster_rows.append(
                    {
                        "Cluster": cluster.get("cluster_id"),
                        "Name": cluster.get("name"),
                        "Domain": f"{_icon(cluster.get('domain_type'))} {cluster.get('domain_type')}",
                        "Region": cluster.get("region"),
                        "Status": f"{_icon(cluster.get('status'))} {cluster.get('status')}",
                        "Risk": f"{_icon(cluster.get('risk_level'))} {cluster.get('risk_level')}",
                        "Health": cluster.get("health_score"),
                        "Capacity": f"{cluster.get('active_units', 0)}/{cluster.get('capacity_units', 0)}",
                        "Runtimes": len(cluster.get("runtime_ids", [])),
                        "Tenants": ", ".join(cluster.get("tenant_affinity", [])[:5]),
                        "Sovereign Tags": ", ".join(cluster.get("sovereign_tags", [])[:6]),
                        "Updated": _fmt_ts(cluster.get("updated_at_ms")),
                    }
                )

            if cluster_rows:
                st.dataframe(
                    _safe_df(cluster_rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No runtime clusters registered.")

        except Exception as exc:
            st.error(f"Cluster map failed: {exc}")
    else:
        st.info("Cluster manager unavailable.")

    st.markdown("---")

    # ========================================================
    # RUNTIME MAP
    # ========================================================

    st.markdown("## 🌍 Federated Runtime Nodes")

    if federation_manager is not None:
        try:
            runtimes = federation_manager.list_runtimes()

            runtime_rows = []

            for rt in runtimes:
                capacity = f"{rt.get('active_units', 0)}/{rt.get('capacity_units', 0)}"

                runtime_rows.append(
                    {
                        "Runtime": rt.get("runtime_id"),
                        "Name": rt.get("name"),
                        "Domain": f"{_icon(rt.get('domain_type'))} {rt.get('domain_type')}",
                        "Region": rt.get("region"),
                        "Status": f"{_icon(rt.get('status'))} {rt.get('status')}",
                        "Trust": rt.get("trust_level"),
                        "Health": rt.get("health_score"),
                        "Risk": f"{_icon(rt.get('risk_level'))} {rt.get('risk_level')}",
                        "Capacity": capacity,
                        "Tenants": ", ".join(rt.get("tenant_affinity", [])[:5]),
                        "Capabilities": ", ".join(rt.get("capabilities", [])[:5]),
                        "Heartbeat": _fmt_ts(rt.get("last_heartbeat_ms")),
                    }
                )

            if runtime_rows:
                st.dataframe(
                    _safe_df(runtime_rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No federated runtime nodes registered.")

        except Exception as exc:
            st.error(f"Runtime map failed: {exc}")
    else:
        st.info("Federation manager unavailable.")

    st.markdown("---")

    # ========================================================
    # DOMAIN OVERLAY
    # ========================================================

    st.markdown("## 🛡️ Sovereign Domain Overlay")

    if domain_manager is not None:
        try:
            domains = domain_manager.list_domains()

            domain_rows = []

            for domain in domains:
                domain_rows.append(
                    {
                        "Domain": domain.get("domain_id"),
                        "Name": domain.get("name"),
                        "Type": f"{_icon(domain.get('domain_type'))} {domain.get('domain_type')}",
                        "Status": f"{_icon(domain.get('status'))} {domain.get('status')}",
                        "Region": domain.get("region"),
                        "Trust": domain.get("trust_level"),
                        "Tenants": ", ".join(domain.get("tenant_ids", [])[:5]),
                        "Sensitivities": ", ".join(domain.get("allowed_sensitivities", [])[:6]),
                        "Capabilities": ", ".join(domain.get("allowed_capabilities", [])[:5]),
                        "Approval": domain.get("requires_approval"),
                        "Updated": _fmt_ts(domain.get("updated_at_ms")),
                    }
                )

            if domain_rows:
                st.dataframe(
                    _safe_df(domain_rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No execution domains registered.")

        except Exception as exc:
            st.error(f"Domain overlay failed: {exc}")
    else:
        st.info("Execution domain manager unavailable.")

    st.markdown("---")

    # ========================================================
    # TOPOLOGY JSON / FABRIC GRAPH
    # ========================================================

    st.markdown("## 🕸️ Fabric Topology Data")

    topology_tabs = st.tabs(
        [
            "Cluster Topology",
            "Federation Topology",
            "Combined Summary",
        ]
    )

    with topology_tabs[0]:
        if cluster_manager is not None:
            try:
                st.json(cluster_manager.cluster_topology())
            except Exception as exc:
                st.error(f"Cluster topology failed: {exc}")
        else:
            st.info("Cluster topology unavailable.")

    with topology_tabs[1]:
        if federation_manager is not None:
            try:
                st.json(federation_manager.federation_topology())
            except Exception as exc:
                st.error(f"Federation topology failed: {exc}")
        else:
            st.info("Federation topology unavailable.")

    with topology_tabs[2]:
        st.json(
            {
                "cluster_health": cluster_health,
                "federation_health": federation_health,
                "domain_health": domain_health,
                "sovereignty_status": sovereignty_status,
                "routing_status": routing_status,
                "supervisor_status": supervisor_status,
            }
        )

    st.markdown("---")

    # ========================================================
    # ROUTING ACTIVITY
    # ========================================================

    st.markdown("## 🧭 Sovereign Routing Activity")

    route_tabs = st.tabs(
        [
            "Federated Routes",
            "Sovereign Decisions",
            "Cluster Failover",
        ]
    )

    with route_tabs[0]:
        if federated_router is not None:
            try:
                routes = federated_router.list_decisions(limit=150)

                rows = []

                for route in routes:
                    rows.append(
                        {
                            "Time": _fmt_ts(route.get("created_at_ms")),
                            "Route": f"{_icon(route.get('route_type'))} {route.get('route_type')}",
                            "Allowed": route.get("allowed"),
                            "Tenant": route.get("tenant_id"),
                            "Capability": route.get("capability"),
                            "Runtime": route.get("selected_runtime_id"),
                            "Domain": route.get("selected_domain_id"),
                            "Local": route.get("local_dispatch"),
                            "Reason": route.get("reason"),
                        }
                    )

                if rows:
                    st.dataframe(
                        _safe_df(rows),
                        use_container_width=True,
                        height=360,
                    )
                else:
                    st.info("No federated route decisions yet.")

            except Exception as exc:
                st.error(f"Federated route activity failed: {exc}")
        else:
            st.info("Federated execution router unavailable.")

    with route_tabs[1]:
        if sovereign_controller is not None:
            try:
                decisions = sovereign_controller.list_decisions(limit=150)

                rows = []

                for decision in decisions:
                    rows.append(
                        {
                            "Time": _fmt_ts(decision.get("created_at_ms")),
                            "Decision": f"{_icon(decision.get('decision'))} {decision.get('decision')}",
                            "Allowed": decision.get("allowed"),
                            "Tenant": decision.get("tenant_id"),
                            "Sensitivity": decision.get("sensitivity"),
                            "Capability": decision.get("capability"),
                            "Domain": decision.get("selected_domain_id"),
                            "Runtime": decision.get("selected_runtime_id"),
                            "Reason": decision.get("reason"),
                        }
                    )

                if rows:
                    st.dataframe(
                        _safe_df(rows),
                        use_container_width=True,
                        height=360,
                    )
                else:
                    st.info("No sovereign decisions yet.")

            except Exception as exc:
                st.error(f"Sovereign decision activity failed: {exc}")
        else:
            st.info("Sovereign execution controller unavailable.")

    with route_tabs[2]:
        if cluster_manager is not None:
            try:
                plans = cluster_manager.list_failover_plans(limit=100)

                rows = []

                for plan in plans:
                    rows.append(
                        {
                            "Time": _fmt_ts(plan.get("created_at_ms")),
                            "Plan": plan.get("plan_id"),
                            "Source Cluster": plan.get("source_cluster_id"),
                            "Target Cluster": plan.get("target_cluster_id"),
                            "Status": f"{_icon(plan.get('status'))} {plan.get('status')}",
                            "Tenant": plan.get("tenant_id"),
                            "Capability": plan.get("capability"),
                            "Reason": plan.get("reason"),
                        }
                    )

                if rows:
                    st.dataframe(
                        _safe_df(rows),
                        use_container_width=True,
                        height=320,
                    )
                else:
                    st.info("No cluster failover plans yet.")

            except Exception as exc:
                st.error(f"Cluster failover activity failed: {exc}")
        else:
            st.info("Cluster manager unavailable.")

    st.markdown("---")

    # ========================================================
    # FABRIC SIMULATOR
    # ========================================================

    st.markdown("## 🧪 Fabric Route Simulator")

    s1, s2, s3 = st.columns(3)

    with s1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="fabric_sim_tenant",
        )

    with s2:
        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="fabric_sim_capability",
        )

    with s3:
        sensitivity = st.selectbox(
            "Sensitivity",
            [
                "PUBLIC",
                "INTERNAL",
                "CONFIDENTIAL",
                "CUI",
                "EXPORT_CONTROLLED",
                "CLASSIFIED",
            ],
            index=1,
            key="fabric_sim_sensitivity",
        )

    f1, f2, f3 = st.columns(3)

    with f1:
        require_govcloud = st.checkbox(
            "Require GovCloud",
            value=False,
            key="fabric_sim_govcloud",
        )

    with f2:
        require_high_trust = st.checkbox(
            "Require High Trust",
            value=False,
            key="fabric_sim_high_trust",
        )

    with f3:
        dispatch_local = st.checkbox(
            "Dispatch Local",
            value=False,
            key="fabric_sim_dispatch_local",
        )

    action = st.text_input(
        "Action",
        value="SIMULATE_FABRIC_ROUTE",
        key="fabric_sim_action",
    )

    workload = {
        "action": action,
        "categories": [sensitivity],
        "requires_govcloud": require_govcloud,
        "requires_high_trust": require_high_trust,
        "capability": capability,
        "source": "sovereign_runtime_visualizer",
    }

    if st.button(
        "Simulate Sovereign Fabric Route",
        use_container_width=True,
        key="fabric_route_sim_btn",
    ):
        if federated_router is None:
            st.error("Federated execution router unavailable.")
        else:
            try:
                decision = federated_router.route_workload(
                    tenant_id=tenant_id,
                    workload=workload,
                    capability=capability,
                    action=action,
                    require_govcloud=require_govcloud,
                    require_high_trust=require_high_trust,
                    dispatch_local=dispatch_local,
                )

                st.json(
                    decision.to_dict()
                    if hasattr(decision, "to_dict")
                    else decision
                )

            except Exception as exc:
                st.error(f"Fabric route simulation failed: {exc}")

    st.markdown("---")

    # ========================================================
    # CLUSTER OPERATIONS
    # ========================================================

    st.markdown("## 🎛️ Cluster Operations")

    if cluster_manager is not None:
        try:
            clusters = cluster_manager.list_clusters()
            cluster_ids = [
                c.get("cluster_id")
                for c in clusters
                if c.get("cluster_id")
            ]

            if cluster_ids:
                selected_cluster = st.selectbox(
                    "Cluster",
                    cluster_ids,
                    key="fabric_selected_cluster",
                )

                reason = st.text_input(
                    "Reason",
                    value="manual_fabric_operator_action",
                    key="fabric_cluster_reason",
                )

                o1, o2, o3, o4 = st.columns(4)

                with o1:
                    if st.button(
                        "Drain Cluster",
                        use_container_width=True,
                        key="fabric_drain_cluster",
                    ):
                        ok = cluster_manager.drain_cluster(
                            selected_cluster,
                            reason=reason,
                        )
                        st.warning({"ok": ok})

                with o2:
                    if st.button(
                        "Quarantine Cluster",
                        use_container_width=True,
                        key="fabric_quarantine_cluster",
                    ):
                        ok = cluster_manager.quarantine_cluster(
                            selected_cluster,
                            reason=reason,
                        )
                        st.warning({"ok": ok})

                with o3:
                    if st.button(
                        "Restore Cluster",
                        use_container_width=True,
                        key="fabric_restore_cluster",
                    ):
                        ok = cluster_manager.restore_cluster(
                            selected_cluster,
                        )
                        st.success({"ok": ok})

                with o4:
                    if st.button(
                        "Plan Failover",
                        use_container_width=True,
                        key="fabric_plan_failover",
                    ):
                        plan = cluster_manager.plan_cluster_failover(
                            source_cluster_id=selected_cluster,
                            tenant_id="default",
                            capability="execution_queue",
                        )
                        st.json(
                            plan.to_dict()
                            if hasattr(plan, "to_dict")
                            else plan
                        )

            else:
                st.info("No clusters available.")

        except Exception as exc:
            st.error(f"Cluster operations failed: {exc}")

    st.markdown("---")

    # ========================================================
    # OPERATIONS LOG
    # ========================================================

    st.markdown("## 📜 Fabric Operations Log")

    if cluster_manager is not None:
        try:
            operations = cluster_manager.list_operations(limit=150)

            rows = []

            for op in operations:
                rows.append(
                    {
                        "Time": _fmt_ts(op.get("created_at_ms")),
                        "Operation": op.get("operation_type"),
                        "Cluster": op.get("cluster_id"),
                        "Status": f"{_icon(op.get('status'))} {op.get('status')}",
                        "Tenant": op.get("tenant_id"),
                        "Reason": op.get("reason"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No fabric operations yet.")

        except Exception as exc:
            st.error(f"Operations log failed: {exc}")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="sovereign_runtime_visualizer_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()