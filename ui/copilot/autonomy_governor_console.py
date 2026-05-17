"""
ui/copilot/autonomy_governor_console.py

Autonomy Governor Console.

Purpose:
- adaptive governance intelligence command center
- runtime governance cognition
- sovereign governance pressure visibility
- adaptive autonomy management
- governance action simulation and enforcement
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
        "LOW",
        "ACTIVE",
        "ALLOWED",
        "COMPLETED",
        "READY",
        "FULL_AUTONOMY",
    }:
        return "🟢"

    if value in {
        "MEDIUM",
        "SUPERVISED_AUTONOMY",
        "ASSISTED",
        "RUNNING",
        "PENDING",
    }:
        return "🟡"

    if value in {
        "HIGH",
        "DEGRADED",
        "REQUIRES_APPROVAL",
        "FAILED",
    }:
        return "🟠"

    if value in {
        "CRITICAL",
        "LOCKDOWN",
        "BLOCKED",
        "QUARANTINED",
        "FROZEN",
    }:
        return "🔴"

    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def render_autonomy_governor_console(
    storage: Any,
) -> None:
    st.markdown("# 🧠 Adaptive Governance Intelligence")
    st.caption(
        "Adaptive sovereign governance command center for runtime fabric intelligence and autonomy control."
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

    cluster_manager = getattr(
        storage,
        "distributed_runtime_cluster_manager",
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

    policy_manager = getattr(
        storage,
        "runtime_policy_manager",
        None,
    )

    if governor is None:
        st.error(
            "Autonomy Governor V2 is unavailable."
        )
        return

    # ========================================================
    # GOVERNOR STATUS
    # ========================================================

    st.markdown("## 🌐 Governance Status")

    governor_status = {}
    sovereignty_status = {}
    cluster_health = {}
    routing_status = {}
    supervisor_status = {}

    try:
        governor_status = governor.governor_status()
    except Exception as exc:
        governor_status = {"error": str(exc)}

    try:
        if sovereign_controller is not None:
            sovereignty_status = sovereign_controller.sovereignty_status()
    except Exception as exc:
        sovereignty_status = {"error": str(exc)}

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
        if supervisor is not None:
            supervisor_status = supervisor.status_snapshot()
    except Exception as exc:
        supervisor_status = {"error": str(exc)}

    current_mode = governor_status.get(
        "tenant_mode",
        "UNKNOWN",
    )

    latest = governor_status.get(
        "latest_assessment",
        {},
    ) or {}

    risk_level = latest.get(
        "risk_level",
        "UNKNOWN",
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Autonomy Mode",
        f"{_icon(current_mode)} {current_mode}",
    )

    c2.metric(
        "Risk Level",
        f"{_icon(risk_level)} {risk_level}",
    )

    c3.metric(
        "Risk Score",
        latest.get("risk_score", 0),
    )

    c4.metric(
        "Assessments",
        governor_status.get("assessment_count", 0),
    )

    c5.metric(
        "Actions",
        governor_status.get("action_count", 0),
    )

    c6.metric(
        "Sovereign Blocks",
        sovereignty_status.get("blocked", 0),
    )

    st.markdown("---")

    # ========================================================
    # GOVERNANCE PRESSURE
    # ========================================================

    st.markdown("## ⚖️ Governance Pressure")

    p1, p2, p3, p4, p5 = st.columns(5)

    p1.metric(
        "Cluster Risk",
        f"{_icon(cluster_health.get('risk'))} {cluster_health.get('risk', 'UNKNOWN')}",
    )

    p2.metric(
        "Federated Routes",
        routing_status.get("federated_routes", 0),
    )

    p3.metric(
        "Blocked Routes",
        routing_status.get("blocked", 0),
    )

    p4.metric(
        "Approval Pressure",
        sovereignty_status.get("requires_approval", 0),
    )

    runtime_mode = supervisor_status.get(
        "runtime_mode",
        "UNKNOWN",
    )

    p5.metric(
        "Supervisor",
        f"{_icon(runtime_mode)} {runtime_mode}",
    )

    st.markdown("---")

    # ========================================================
    # LATEST ASSESSMENT
    # ========================================================

    st.markdown("## 📊 Latest Governance Assessment")

    if latest:
        top_tabs = st.tabs(
            [
                "Assessment",
                "Findings",
                "Telemetry",
                "Recommendations",
            ]
        )

        with top_tabs[0]:
            st.json(latest)

        with top_tabs[1]:
            findings = latest.get("findings", [])

            if findings:
                rows = []

                for finding in findings:
                    rows.append(
                        {
                            "Type": finding.get("type"),
                            "Severity": f"{_icon(finding.get('severity'))} {finding.get('severity')}",
                            "Details": str(finding),
                        }
                    )

                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=320,
                )
            else:
                st.info("No governance findings.")

        with top_tabs[2]:
            st.json(latest.get("telemetry", {}))

        with top_tabs[3]:
            recs = latest.get("recommended_actions", [])

            if recs:
                rows = []

                for rec in recs:
                    rows.append(
                        {
                            "Action": rec.get("action"),
                            "Reason": rec.get("reason"),
                            "Target": rec.get("target"),
                        }
                    )

                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=280,
                )
            else:
                st.info("No governance recommendations.")

    else:
        st.info("No governance assessments available.")

    st.markdown("---")

    # ========================================================
    # AUTONOMY MODE CONTROL
    # ========================================================

    st.markdown("## 🎛️ Autonomy Mode Control")

    modes = [
        "MANUAL",
        "ASSISTED",
        "SUPERVISED_AUTONOMY",
        "FULL_AUTONOMY",
        "LOCKDOWN",
    ]

    selected_mode = st.selectbox(
        "Target Mode",
        modes,
        index=max(
            0,
            modes.index(current_mode)
            if current_mode in modes
            else 2,
        ),
        key="autonomy_governor_mode_select",
    )

    reason = st.text_input(
        "Reason",
        value="manual_governance_operator_update",
        key="autonomy_governor_reason",
    )

    if st.button(
        "Apply Autonomy Mode",
        use_container_width=True,
        key="apply_autonomy_mode_btn",
    ):
        try:
            result = governor.set_autonomy_mode(
                tenant_id="default",
                mode=selected_mode,
                reason=reason,
            )

            st.success(result)

        except Exception as exc:
            st.error(f"Failed to update autonomy mode: {exc}")

    st.markdown("---")

    # ========================================================
    # GOVERNANCE SIMULATOR
    # ========================================================

    st.markdown("## 🧪 Governance Simulation")

    s1, s2, s3 = st.columns(3)

    with s1:
        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="gov_sim_capability",
        )

    with s2:
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
            key="gov_sim_sensitivity",
        )

    with s3:
        requested_mode = st.selectbox(
            "Requested Mode",
            modes,
            index=2,
            key="gov_sim_requested_mode",
        )

    sim_tabs = st.tabs(
        [
            "Assessment Only",
            "Dry Run Enforcement",
            "Live Enforcement",
        ]
    )

    workload = {
        "action": "GOVERNANCE_SIMULATION",
        "capability": capability,
        "categories": [sensitivity],
        "source": "autonomy_governor_console",
    }

    with sim_tabs[0]:
        if st.button(
            "Run Governance Assessment",
            use_container_width=True,
            key="gov_assess_btn",
        ):
            try:
                assessment = governor.assess(
                    tenant_id="default",
                    requested_mode=requested_mode,
                    workload=workload,
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
            "Run Dry-Run Enforcement",
            use_container_width=True,
            key="gov_dry_run_btn",
        ):
            try:
                result = governor.enforce(
                    tenant_id="default",
                    workload=workload,
                    dry_run=True,
                )

                st.json(result)

            except Exception as exc:
                st.error(f"Dry-run enforcement failed: {exc}")

    with sim_tabs[2]:
        warning = st.checkbox(
            "I understand this may modify runtime governance state.",
            value=False,
            key="gov_live_warning",
        )

        if st.button(
            "Execute Governance Enforcement",
            use_container_width=True,
            key="gov_live_enforcement_btn",
            disabled=not warning,
        ):
            try:
                result = governor.enforce(
                    tenant_id="default",
                    workload=workload,
                    dry_run=False,
                )

                st.json(result)

            except Exception as exc:
                st.error(f"Live enforcement failed: {exc}")

    st.markdown("---")

    # ========================================================
    # GOVERNANCE HISTORY
    # ========================================================

    st.markdown("## 📜 Governance Assessment History")

    history_tabs = st.tabs(
        [
            "Assessments",
            "Governance Actions",
        ]
    )

    with history_tabs[0]:
        try:
            assessments = governor.list_assessments(limit=200)

            rows = []

            for assessment in assessments:
                rows.append(
                    {
                        "Time": _fmt_ts(assessment.get("created_at_ms")),
                        "Risk": f"{_icon(assessment.get('risk_level'))} {assessment.get('risk_level')}",
                        "Risk Score": assessment.get("risk_score"),
                        "Current Mode": assessment.get("autonomy_mode"),
                        "Recommended": assessment.get("recommended_mode"),
                        "Allowed": assessment.get("allowed"),
                        "Reason": assessment.get("reason"),
                    }
                )

            if rows:
                st.dataframe(
                    _safe_df(rows),
                    use_container_width=True,
                    height=420,
                )
            else:
                st.info("No governance assessments available.")

        except Exception as exc:
            st.error(f"Failed to load governance assessments: {exc}")

    with history_tabs[1]:
        try:
            actions = governor.list_actions(limit=200)

            rows = []

            for action in actions:
                rows.append(
                    {
                        "Time": _fmt_ts(action.get("created_at_ms")),
                        "Action": action.get("action_type"),
                        "Status": f"{_icon(action.get('status'))} {action.get('status')}",
                        "Target": action.get("target"),
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
                st.info("No governance actions available.")

        except Exception as exc:
            st.error(f"Failed to load governance actions: {exc}")

    st.markdown("---")

    # ========================================================
    # FABRIC SIGNALS
    # ========================================================

    st.markdown("## 🌐 Runtime Fabric Signals")

    signal_tabs = st.tabs(
        [
            "Cluster Health",
            "Sovereignty",
            "Routing",
            "Policies",
        ]
    )

    with signal_tabs[0]:
        st.json(cluster_health)

    with signal_tabs[1]:
        st.json(sovereignty_status)

    with signal_tabs[2]:
        st.json(routing_status)

    with signal_tabs[3]:
        try:
            if policy_manager is not None:
                st.json(policy_manager.policy_status())
            else:
                st.info("Policy manager unavailable.")
        except Exception as exc:
            st.error(f"Policy status unavailable: {exc}")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="autonomy_governor_console_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()