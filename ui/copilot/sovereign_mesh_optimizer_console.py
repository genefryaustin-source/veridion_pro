"""
ui/copilot/sovereign_mesh_optimizer_console.py

Sovereign Mesh Optimizer Console.

Purpose:
- sovereign execution optimization command center
- mesh topology cognition
- sovereign routing optimization visibility
- governance-aware optimization operations
- execution locality intelligence
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

    if value in {
        "HEALTHY",
        "OK",
        "ACTIVE",
        "ONLINE",
        "READY",
        "COMPLETED",
        "LOW",
    }:
        return "🟢"

    if value in {
        "IMPROVABLE",
        "DEGRADED",
        "MEDIUM",
        "RUNNING",
        "PENDING",
        "PRESSURE",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "FAILED",
        "QUARANTINED",
        "BLOCKED",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "LOCKDOWN",
        "OFFLINE",
        "FROZEN",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def render_sovereign_mesh_optimizer_console(
    storage: Any,
) -> None:
    st.markdown("# 🌐 Sovereign Mesh Optimization")
    st.caption(
        "Global sovereign execution optimization, topology intelligence, routing locality, and governance-aware mesh cognition."
    )

    optimizer = getattr(
        storage,
        "sovereign_mesh_optimizer",
        None,
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

    federated_router = getattr(
        storage,
        "federated_execution_router",
        None,
    )

    sovereign_controller = getattr(
        storage,
        "sovereign_execution_controller",
        None,
    )

    governor = getattr(
        storage,
        "autonomy_governor_v2",
        None,
    )

    balancer = getattr(
        storage,
        "autonomous_cluster_balancer",
        None,
    )

    if optimizer is None:
        st.error(
            "Sovereign Mesh Optimizer is unavailable."
        )
        return

    # ========================================================
    # OPTIMIZER STATUS
    # ========================================================

    st.markdown("## 🌐 Mesh Optimization Status")

    optimizer_status = {}
    cluster_health = {}
    federation_health = {}
    routing_status = {}
    sovereignty_status = {}

    try:
        optimizer_status = optimizer.optimizer_status()
    except Exception as exc:
        optimizer_status = {"error": str(exc)}

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
        if federated_router is not None:
            routing_status = federated_router.routing_status()
    except Exception as exc:
        routing_status = {"error": str(exc)}

    try:
        if sovereign_controller is not None:
            sovereignty_status = sovereign_controller.sovereignty_status()
    except Exception as exc:
        sovereignty_status = {"error": str(exc)}

    latest = optimizer_status.get(
        "latest_assessment",
        {},
    ) or {}

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Mesh Status",
        f"{_icon(latest.get('status'))} {latest.get('status', 'UNKNOWN')}",
    )

    c2.metric(
        "Optimization Score",
        latest.get("optimization_score", 0),
    )

    c3.metric(
        "Assessments",
        optimizer_status.get("assessment_count", 0),
    )

    c4.metric(
        "Actions",
        optimizer_status.get("action_count", 0),
    )

    c5.metric(
        "Cross-Runtime Routes",
        routing_status.get("federated_routes", 0),
    )

    c6.metric(
        "Sovereign Blocks",
        sovereignty_status.get("blocked", 0),
    )

    st.markdown("---")

    # ========================================================
    # MESH TOPOLOGY
    # ========================================================

    st.markdown("## 🕸️ Runtime Mesh Topology")

    topology_tabs = st.tabs(
        [
            "Cluster Topology",
            "Federation Topology",
            "Mesh Summary",
        ]
    )

    with topology_tabs[0]:
        try:
            if cluster_manager is not None:
                st.json(
                    cluster_manager.cluster_topology()
                )
            else:
                st.info("Cluster topology unavailable.")
        except Exception as exc:
            st.error(f"Cluster topology failed: {exc}")

    with topology_tabs[1]:
        try:
            if federation_manager is not None:
                st.json(
                    federation_manager.federation_topology()
                )
            else:
                st.info("Federation topology unavailable.")
        except Exception as exc:
            st.error(f"Federation topology failed: {exc}")

    with topology_tabs[2]:
        st.json(
            {
                "cluster_health": cluster_health,
                "federation_health": federation_health,
                "routing_status": routing_status,
                "sovereignty_status": sovereignty_status,
            }
        )

    st.markdown("---")

    # ========================================================
    # EXECUTION LOCALITY
    # ========================================================

    st.markdown("## 📍 Execution Locality Intelligence")

    locality_rows = []

    try:
        if cluster_manager is not None:
            clusters = cluster_manager.list_clusters()

            for cluster in clusters:
                active = float(cluster.get("active_units", 0) or 0)
                capacity = float(cluster.get("capacity_units", 1) or 1)

                locality_rows.append(
                    {
                        "Cluster": cluster.get("cluster_id"),
                        "Region": cluster.get("region"),
                        "Domain": cluster.get("domain_type"),
                        "Health": cluster.get("health_score"),
                        "Risk": f"{_icon(cluster.get('risk_level'))} {cluster.get('risk_level')}",
                        "Pressure": round(
                            active / max(capacity, 1.0),
                            4,
                        ),
                        "Tenants": ", ".join(
                            cluster.get("tenant_affinity", [])[:5]
                        ),
                        "Tags": ", ".join(
                            cluster.get("sovereign_tags", [])[:6]
                        ),
                    }
                )

        if locality_rows:
            st.dataframe(
                _safe_df(locality_rows),
                use_container_width=True,
                height=380,
            )
        else:
            st.info("No locality intelligence available.")

    except Exception as exc:
        st.error(f"Execution locality failed: {exc}")

    st.markdown("---")

    # ========================================================
    # LATEST OPTIMIZATION ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Optimization Assessment")

    if latest:
        assess_tabs = st.tabs(
            [
                "Assessment",
                "Findings",
                "Telemetry",
                "Recommendations",
            ]
        )

        with assess_tabs[0]:
            st.json(latest)

        with assess_tabs[1]:
            findings = latest.get("findings", [])

            rows = []

            for finding in findings:
                rows.append(
                    {
                        "Type": finding.get("finding_type"),
                        "Severity": f"{_icon(finding.get('severity'))} {finding.get('severity')}",
                        "Target": finding.get("target"),
                        "Message": finding.get("message"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No optimization findings.")

        with assess_tabs[2]:
            st.json(latest.get("telemetry", {}))

        with assess_tabs[3]:
            actions = latest.get(
                "recommended_actions",
                [],
            )

            rows = []

            for action in actions:
                rows.append(
                    {
                        "Action": action.get("action_type"),
                        "Target": action.get("target"),
                        "Status": f"{_icon(action.get('status'))} {action.get('status')}",
                        "Reason": action.get("reason"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=320,
                )
            else:
                st.info("No optimization recommendations.")

    else:
        st.info("No optimization assessments available.")

    st.markdown("---")

    # ========================================================
    # ROUTING GRAVITY
    # ========================================================

    st.markdown("## 🧭 Cross-Runtime Routing Gravity")

    try:
        if federated_router is not None:
            decisions = federated_router.list_decisions(
                limit=200,
            )

            rows = []

            for decision in decisions:
                rows.append(
                    {
                        "Time": _fmt_ts(decision.get("created_at_ms")),
                        "Route": decision.get("route_type"),
                        "Allowed": decision.get("allowed"),
                        "Tenant": decision.get("tenant_id"),
                        "Runtime": decision.get("selected_runtime_id"),
                        "Domain": decision.get("selected_domain_id"),
                        "Capability": decision.get("capability"),
                        "Local": decision.get("local_dispatch"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=380,
                )
            else:
                st.info("No routing gravity data available.")

        else:
            st.info("Federated router unavailable.")

    except Exception as exc:
        st.error(f"Routing gravity failed: {exc}")

    st.markdown("---")

    # ========================================================
    # MESH OPTIMIZATION SIMULATOR
    # ========================================================

    st.markdown("## 🧪 Sovereign Mesh Optimization Simulator")

    s1, s2, s3 = st.columns(3)

    with s1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="mesh_opt_tenant",
        )

    with s2:
        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="mesh_opt_capability",
        )

    with s3:
        dry_run = st.checkbox(
            "Dry Run",
            value=True,
            key="mesh_opt_dry_run",
        )

    sim_tabs = st.tabs(
        [
            "Assessment",
            "Optimization",
        ]
    )

    with sim_tabs[0]:
        if st.button(
            "Run Mesh Assessment",
            use_container_width=True,
            key="mesh_opt_assess_btn",
        ):
            try:
                assessment = optimizer.assess(
                    tenant_id=tenant_id,
                    capability=capability,
                )

                st.json(
                    assessment.to_dict()
                    if hasattr(assessment, "to_dict")
                    else assessment
                )

            except Exception as exc:
                st.error(f"Mesh assessment failed: {exc}")

    with sim_tabs[1]:
        if st.button(
            "Execute Mesh Optimization",
            use_container_width=True,
            key="mesh_opt_execute_btn",
        ):
            try:
                result = optimizer.enforce(
                    tenant_id=tenant_id,
                    capability=capability,
                    dry_run=dry_run,
                )

                st.json(result)

            except Exception as exc:
                st.error(f"Mesh optimization failed: {exc}")

    st.markdown("---")

    # ========================================================
    # OPTIMIZATION ACTIONS
    # ========================================================

    st.markdown("## ⚙️ Optimization Actions")

    try:
        actions = optimizer.list_actions(limit=200)

        rows = []

        for action in actions:
            rows.append(
                {
                    "Time": _fmt_ts(action.get("created_at_ms")),
                    "Action": action.get("action_type"),
                    "Target": action.get("target"),
                    "Status": f"{_icon(action.get('status'))} {action.get('status')}",
                    "Reason": action.get("reason"),
                }
            )

        if rows:
            st.dataframe(
                _safe_df(rows),
                use_container_width=True,
                height=420,
            )
        else:
            st.info("No optimization actions available.")

    except Exception as exc:
        st.error(f"Optimization actions failed: {exc}")

    st.markdown("---")

    # ========================================================
    # FABRIC INTELLIGENCE SIGNALS
    # ========================================================

    st.markdown("## 🧠 Runtime Fabric Intelligence Signals")

    signal_tabs = st.tabs(
        [
            "Cluster Health",
            "Federation",
            "Routing",
            "Sovereignty",
            "Governor",
            "Balancer",
        ]
    )

    with signal_tabs[0]:
        st.json(cluster_health)

    with signal_tabs[1]:
        st.json(federation_health)

    with signal_tabs[2]:
        st.json(routing_status)

    with signal_tabs[3]:
        st.json(sovereignty_status)

    with signal_tabs[4]:
        try:
            if governor is not None:
                st.json(
                    governor.governor_status()
                )
            else:
                st.info("Governor unavailable.")
        except Exception as exc:
            st.error(f"Governor status failed: {exc}")

    with signal_tabs[5]:
        try:
            if balancer is not None:
                st.json(
                    balancer.balancer_status()
                )
            else:
                st.info("Balancer unavailable.")
        except Exception as exc:
            st.error(f"Balancer status failed: {exc}")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="sovereign_mesh_optimizer_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()