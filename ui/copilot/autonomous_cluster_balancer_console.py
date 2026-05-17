"""
ui/copilot/autonomous_cluster_balancer_console.py

Autonomous Cluster Balancer Console.

Purpose:
- runtime fabric stabilization command center
- cluster pressure visibility
- sovereign-aware balancing cognition
- failover planning visibility
- autonomous stabilization monitoring
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
        "OK",
        "ACTIVE",
        "ONLINE",
        "READY",
        "COMPLETED",
        "LOW",
    }:
        return "🟢"

    if value in {
        "DEGRADED",
        "PRESSURE",
        "RUNNING",
        "PENDING",
        "MEDIUM",
        "DRAINING",
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
        "OFFLINE",
        "LOCKDOWN",
        "FROZEN",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def render_autonomous_cluster_balancer_console(
    storage: Any,
) -> None:
    st.markdown("# ⚖️ Runtime Fabric Stabilization")
    st.caption(
        "Adaptive sovereign runtime balancing, cluster stabilization, failover cognition, and fabric pressure management."
    )

    balancer = getattr(
        storage,
        "autonomous_cluster_balancer",
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

    governor = getattr(
        storage,
        "autonomy_governor_v2",
        None,
    )

    sovereign_controller = getattr(
        storage,
        "sovereign_execution_controller",
        None,
    )

    if balancer is None:
        st.error(
            "Autonomous Cluster Balancer is unavailable."
        )
        return

    # ========================================================
    # BALANCER STATUS
    # ========================================================

    st.markdown("## 🌐 Runtime Fabric Status")

    balancer_status = {}
    cluster_health = {}
    routing_status = {}
    sovereignty_status = {}
    governor_status = {}

    try:
        balancer_status = balancer.balancer_status()
    except Exception as exc:
        balancer_status = {"error": str(exc)}

    try:
        if cluster_manager is not None:
            cluster_health = cluster_manager.cluster_health()
    except Exception as exc:
        cluster_health = {"error": str(exc)}

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

    try:
        if governor is not None:
            governor_status = governor.governor_status()
    except Exception as exc:
        governor_status = {"error": str(exc)}

    latest = balancer_status.get(
        "latest_assessment",
        {},
    ) or {}

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Fabric Status",
        f"{_icon(latest.get('status'))} {latest.get('status', 'UNKNOWN')}",
    )

    c2.metric(
        "Risk Score",
        latest.get("risk_score", 0),
    )

    c3.metric(
        "Assessments",
        balancer_status.get("assessment_count", 0),
    )

    c4.metric(
        "Actions",
        balancer_status.get("action_count", 0),
    )

    c5.metric(
        "Cluster Risk",
        f"{_icon(cluster_health.get('risk'))} {cluster_health.get('risk', 'UNKNOWN')}",
    )

    c6.metric(
        "Blocked Routes",
        routing_status.get("blocked", 0),
    )

    st.markdown("---")

    # ========================================================
    # CLUSTER PRESSURE MAP
    # ========================================================

    st.markdown("## 🧱 Cluster Pressure Map")

    if cluster_manager is not None:
        try:
            clusters = cluster_manager.list_clusters()

            rows = []

            for cluster in clusters:
                active = float(cluster.get("active_units", 0) or 0)
                capacity = float(cluster.get("capacity_units", 1) or 1)

                pressure = round(
                    active / max(capacity, 1.0),
                    4,
                )

                rows.append(
                    {
                        "Cluster": cluster.get("cluster_id"),
                        "Name": cluster.get("name"),
                        "Domain": cluster.get("domain_type"),
                        "Region": cluster.get("region"),
                        "Status": f"{_icon(cluster.get('status'))} {cluster.get('status')}",
                        "Risk": f"{_icon(cluster.get('risk_level'))} {cluster.get('risk_level')}",
                        "Health": cluster.get("health_score"),
                        "Pressure": pressure,
                        "Capacity": f"{int(active)}/{int(capacity)}",
                        "Runtimes": len(cluster.get("runtime_ids", [])),
                        "Tags": ", ".join(cluster.get("sovereign_tags", [])[:6]),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=380,
                )
            else:
                st.info("No clusters available.")

        except Exception as exc:
            st.error(f"Cluster pressure map failed: {exc}")
    else:
        st.info("Cluster manager unavailable.")

    st.markdown("---")

    # ========================================================
    # BALANCER ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Balance Assessment")

    if latest:
        assessment_tabs = st.tabs(
            [
                "Assessment",
                "Findings",
                "Telemetry",
                "Recommendations",
            ]
        )

        with assessment_tabs[0]:
            st.json(latest)

        with assessment_tabs[1]:
            findings = latest.get("findings", [])

            rows = []

            for finding in findings:
                rows.append(
                    {
                        "Type": finding.get("finding_type"),
                        "Severity": f"{_icon(finding.get('severity'))} {finding.get('severity')}",
                        "Cluster": finding.get("cluster_id"),
                        "Message": finding.get("message"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=320,
                )
            else:
                st.info("No balancing findings.")

        with assessment_tabs[2]:
            st.json(latest.get("telemetry", {}))

        with assessment_tabs[3]:
            recs = latest.get(
                "recommended_actions",
                [],
            )

            rows = []

            for rec in recs:
                rows.append(
                    {
                        "Action": rec.get("action_type"),
                        "Cluster": rec.get("cluster_id"),
                        "Status": f"{_icon(rec.get('status'))} {rec.get('status')}",
                        "Reason": rec.get("reason"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=280,
                )
            else:
                st.info("No balancing recommendations.")

    else:
        st.info("No balancing assessments available.")

    st.markdown("---")

    # ========================================================
    # FABRIC SIMULATOR
    # ========================================================

    st.markdown("## 🧪 Runtime Fabric Stabilization Simulator")

    s1, s2, s3 = st.columns(3)

    with s1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="balancer_sim_tenant",
        )

    with s2:
        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="balancer_sim_capability",
        )

    with s3:
        dry_run = st.checkbox(
            "Dry Run",
            value=True,
            key="balancer_sim_dry_run",
        )

    sim_tabs = st.tabs(
        [
            "Assessment",
            "Enforcement",
        ]
    )

    with sim_tabs[0]:
        if st.button(
            "Run Fabric Assessment",
            use_container_width=True,
            key="balancer_assess_btn",
        ):
            try:
                assessment = balancer.assess(
                    tenant_id=tenant_id,
                    capability=capability,
                )

                st.json(
                    assessment.to_dict()
                    if hasattr(assessment, "to_dict")
                    else assessment
                )

            except Exception as exc:
                st.error(f"Assessment failed: {exc}")

    with sim_tabs[1]:
        if st.button(
            "Execute Stabilization",
            use_container_width=True,
            key="balancer_execute_btn",
        ):
            try:
                result = balancer.enforce(
                    tenant_id=tenant_id,
                    capability=capability,
                    dry_run=dry_run,
                )

                st.json(result)

            except Exception as exc:
                st.error(f"Stabilization execution failed: {exc}")

    st.markdown("---")

    # ========================================================
    # FAILOVER COGNITION
    # ========================================================

    st.markdown("## 🔄 Cluster Failover Cognition")

    if cluster_manager is not None:
        try:
            plans = cluster_manager.list_failover_plans(
                limit=150,
            )

            rows = []

            for plan in plans:
                rows.append(
                    {
                        "Time": _fmt_ts(plan.get("created_at_ms")),
                        "Plan": plan.get("plan_id"),
                        "Source": plan.get("source_cluster_id"),
                        "Target": plan.get("target_cluster_id"),
                        "Status": f"{_icon(plan.get('status'))} {plan.get('status')}",
                        "Capability": plan.get("capability"),
                        "Reason": plan.get("reason"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No failover plans available.")

        except Exception as exc:
            st.error(f"Failover cognition failed: {exc}")

    st.markdown("---")

    # ========================================================
    # BALANCING ACTIONS
    # ========================================================

    st.markdown("## ⚙️ Autonomous Balancing Actions")

    try:
        actions = balancer.list_actions(limit=200)

        rows = []

        for action in actions:
            rows.append(
                {
                    "Time": _fmt_ts(action.get("created_at_ms")),
                    "Action": action.get("action_type"),
                    "Cluster": action.get("cluster_id"),
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
            st.info("No balancing actions available.")

    except Exception as exc:
        st.error(f"Balancing actions failed: {exc}")

    st.markdown("---")

    # ========================================================
    # FABRIC SIGNALS
    # ========================================================

    st.markdown("## 🌐 Runtime Fabric Signals")

    signal_tabs = st.tabs(
        [
            "Cluster Health",
            "Routing",
            "Sovereignty",
            "Governor",
        ]
    )

    with signal_tabs[0]:
        st.json(cluster_health)

    with signal_tabs[1]:
        st.json(routing_status)

    with signal_tabs[2]:
        st.json(sovereignty_status)

    with signal_tabs[3]:
        st.json(governor_status)

    st.markdown("---")

    # ========================================================
    # MANUAL CLUSTER OPERATIONS
    # ========================================================

    st.markdown("## 🎛️ Manual Cluster Operations")

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
                    key="balancer_manual_cluster",
                )

                reason = st.text_input(
                    "Reason",
                    value="manual_balancer_console_action",
                    key="balancer_manual_reason",
                )

                o1, o2, o3, o4 = st.columns(4)

                with o1:
                    if st.button(
                        "Plan Failover",
                        use_container_width=True,
                        key="manual_failover_btn",
                    ):
                        try:
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

                        except Exception as exc:
                            st.error(f"Failover planning failed: {exc}")

                with o2:
                    if st.button(
                        "Drain Cluster",
                        use_container_width=True,
                        key="manual_drain_btn",
                    ):
                        try:
                            ok = cluster_manager.drain_cluster(
                                selected_cluster,
                                reason=reason,
                            )

                            st.warning({"ok": ok})

                        except Exception as exc:
                            st.error(f"Drain failed: {exc}")

                with o3:
                    if st.button(
                        "Quarantine Cluster",
                        use_container_width=True,
                        key="manual_quarantine_btn",
                    ):
                        try:
                            ok = cluster_manager.quarantine_cluster(
                                selected_cluster,
                                reason=reason,
                            )

                            st.warning({"ok": ok})

                        except Exception as exc:
                            st.error(f"Quarantine failed: {exc}")

                with o4:
                    if st.button(
                        "Restore Cluster",
                        use_container_width=True,
                        key="manual_restore_btn",
                    ):
                        try:
                            ok = cluster_manager.restore_cluster(
                                selected_cluster,
                            )

                            st.success({"ok": ok})

                        except Exception as exc:
                            st.error(f"Restore failed: {exc}")

            else:
                st.info("No clusters available.")

        except Exception as exc:
            st.error(f"Cluster operations unavailable: {exc}")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="autonomous_cluster_balancer_console_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()