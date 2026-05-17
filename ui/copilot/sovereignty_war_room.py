"""
ui/copilot/sovereignty_war_room.py

Sovereignty War Room.

Purpose:
- sovereign execution command center
- execution domain visibility
- sovereign route decision review
- blocked workload visibility
- federation route awareness
- GovCloud / air-gapped / export-controlled enforcement visibility
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


def _status_icon(value: str) -> str:
    value = str(value or "").upper()

    if value in {"ALLOWED", "ACTIVE", "ONLINE", "LOCAL", "FEDERATED"}:
        return "🟢"

    if value in {"REQUIRES_APPROVAL", "DEGRADED"}:
        return "🟡"

    if value in {"BLOCKED", "QUARANTINED", "FROZEN", "OFFLINE", "FAILED"}:
        return "🔴"

    if value in {"GOVCLOUD", "CLASSIFIED", "AIRGAPPED", "EXPORT_CONTROLLED"}:
        return "🏛️"

    return "⚪"


def render_sovereignty_war_room(storage: Any) -> None:
    st.markdown("# 🏛️ Sovereignty War Room")
    st.caption("Sovereign execution command center for domains, routing, federation, and enforcement.")

    domain_manager = getattr(storage, "execution_domain_manager", None)
    sovereign_controller = getattr(storage, "sovereign_execution_controller", None)
    federated_router = getattr(storage, "federated_execution_router", None)
    federation_manager = getattr(storage, "runtime_federation_manager", None)

    if sovereign_controller is None and domain_manager is None:
        st.error("Sovereign execution services are unavailable.")
        return

    # ========================================================
    # TOP STATUS
    # ========================================================

    st.markdown("## 🌐 Sovereign Runtime Status")

    sovereignty_status = (
        sovereign_controller.sovereignty_status()
        if sovereign_controller is not None
        and hasattr(sovereign_controller, "sovereignty_status")
        else {}
    )

    domain_health = (
        domain_manager.domain_health()
        if domain_manager is not None
        and hasattr(domain_manager, "domain_health")
        else {}
    )

    route_status = (
        federated_router.routing_status()
        if federated_router is not None
        and hasattr(federated_router, "routing_status")
        else {}
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Sovereign Mode",
        sovereignty_status.get("sovereign_mode", "UNKNOWN"),
    )

    c2.metric(
        "Allowed",
        sovereignty_status.get("allowed", 0),
    )

    c3.metric(
        "Blocked",
        sovereignty_status.get("blocked", 0),
    )

    c4.metric(
        "Approvals",
        sovereignty_status.get("requires_approval", 0),
    )

    c5.metric(
        "Domain Risk",
        domain_health.get("risk", "UNKNOWN"),
    )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric("Route Decisions", route_status.get("decision_count", 0))
    r2.metric("Local Routes", route_status.get("local_routes", 0))
    r3.metric("Federated Routes", route_status.get("federated_routes", 0))
    r4.metric(
        "Federation",
        "Available" if route_status.get("federation_available") else "Local Only",
    )

    st.markdown("---")

    # ========================================================
    # DOMAIN HEALTH
    # ========================================================

    st.markdown("## 🧱 Execution Domain Health")

    if domain_health:
        d1, d2, d3, d4, d5, d6 = st.columns(6)

        d1.metric("Domains", domain_health.get("total_domains", 0))
        d2.metric("Active", domain_health.get("active", 0))
        d3.metric("Degraded", domain_health.get("degraded", 0))
        d4.metric("Quarantined", domain_health.get("quarantined", 0))
        d5.metric("Frozen", domain_health.get("frozen", 0))
        d6.metric("Offline", domain_health.get("offline", 0))

    if domain_manager is not None:
        try:
            domains = domain_manager.list_domains()

            if domains:
                rows = []

                for d in domains:
                    rows.append(
                        {
                            "Domain": d.get("domain_id"),
                            "Name": d.get("name"),
                            "Type": f"{_status_icon(d.get('domain_type'))} {d.get('domain_type')}",
                            "Status": f"{_status_icon(d.get('status'))} {d.get('status')}",
                            "Region": d.get("region"),
                            "Trust": d.get("trust_level"),
                            "Tenants": ", ".join(d.get("tenant_ids", [])[:6]),
                            "Sensitivities": ", ".join(d.get("allowed_sensitivities", [])[:6]),
                            "Approval": d.get("requires_approval"),
                            "Updated": _fmt_ts(d.get("updated_at_ms")),
                            "Error": d.get("last_error"),
                        }
                    )

                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No execution domains registered.")

        except Exception as exc:
            st.error(f"Failed to load execution domains: {exc}")

    st.markdown("---")

    # ========================================================
    # SOVEREIGN DECISIONS
    # ========================================================

    st.markdown("## ⚖️ Sovereign Execution Decisions")

    if sovereign_controller is not None:
        try:
            decisions = sovereign_controller.list_decisions(limit=250)

            if decisions:
                rows = []

                for d in decisions:
                    rows.append(
                        {
                            "Time": _fmt_ts(d.get("created_at_ms")),
                            "Decision": f"{_status_icon(d.get('decision'))} {d.get('decision')}",
                            "Allowed": d.get("allowed"),
                            "Tenant": d.get("tenant_id"),
                            "Sensitivity": d.get("sensitivity"),
                            "Capability": d.get("capability"),
                            "Domain": d.get("selected_domain_id"),
                            "Runtime": d.get("selected_runtime_id"),
                            "Approval": d.get("requires_approval"),
                            "Reason": d.get("reason"),
                        }
                    )

                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    height=420,
                )
            else:
                st.info("No sovereign execution decisions yet.")

        except Exception as exc:
            st.error(f"Failed to load sovereign decisions: {exc}")

    st.markdown("---")

    # ========================================================
    # FEDERATED ROUTE DECISIONS
    # ========================================================

    st.markdown("## 🧭 Federated Sovereign Routes")

    if federated_router is not None:
        try:
            routes = federated_router.list_decisions(limit=250)

            if routes:
                rows = []

                for r in routes:
                    rows.append(
                        {
                            "Time": _fmt_ts(r.get("created_at_ms")),
                            "Route": f"{_status_icon(r.get('route_type'))} {r.get('route_type')}",
                            "Allowed": r.get("allowed"),
                            "Tenant": r.get("tenant_id"),
                            "Capability": r.get("capability"),
                            "Runtime": r.get("selected_runtime_id"),
                            "Domain": r.get("selected_domain_id"),
                            "Local": r.get("local_dispatch"),
                            "Approval": r.get("requires_approval"),
                            "Reason": r.get("reason"),
                        }
                    )

                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    height=420,
                )
            else:
                st.info("No federated sovereign route decisions yet.")

        except Exception as exc:
            st.error(f"Failed to load federated route decisions: {exc}")

    else:
        st.info("Federated execution router is unavailable.")

    st.markdown("---")

    # ========================================================
    # WORKLOAD SIMULATOR
    # ========================================================

    st.markdown("## 🧪 Sovereign Workload Simulator")

    s1, s2, s3 = st.columns(3)

    with s1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="sov_sim_tenant",
        )

    with s2:
        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="sov_sim_capability",
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
            key="sov_sim_sensitivity",
        )

    w1, w2, w3 = st.columns(3)

    with w1:
        requires_govcloud = st.checkbox(
            "Requires GovCloud",
            value=False,
            key="sov_sim_govcloud",
        )

    with w2:
        requires_airgap = st.checkbox(
            "Requires Airgap",
            value=False,
            key="sov_sim_airgap",
        )

    with w3:
        high_trust = st.checkbox(
            "Requires High Trust",
            value=False,
            key="sov_sim_high_trust",
        )

    action = st.text_input(
        "Action",
        value="SIMULATE_SOVEREIGN_EXECUTION",
        key="sov_sim_action",
    )

    workload = {
        "action": action,
        "categories": [sensitivity],
        "requires_govcloud": requires_govcloud,
        "requires_airgap": requires_airgap,
        "requires_high_trust": high_trust,
        "capability": capability,
        "source": "sovereignty_war_room",
    }

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Authorize Sovereign Execution",
            use_container_width=True,
            key="sov_authorize_btn",
        ):
            if sovereign_controller is None:
                st.error("Sovereign controller unavailable.")
            else:
                try:
                    decision = sovereign_controller.authorize_execution(
                        tenant_id=tenant_id,
                        workload=workload,
                        capability=capability,
                        require_govcloud=requires_govcloud,
                        require_high_trust=high_trust,
                        actor="sovereignty_war_room",
                    )

                    st.json(
                        decision.to_dict()
                        if hasattr(decision, "to_dict")
                        else decision
                    )

                except Exception as exc:
                    st.error(f"Sovereign authorization failed: {exc}")

    with col2:
        if st.button(
            "Route Federated Workload",
            use_container_width=True,
            key="sov_route_btn",
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
                        require_govcloud=requires_govcloud,
                        require_high_trust=high_trust,
                        dispatch_local=False,
                    )

                    st.json(
                        decision.to_dict()
                        if hasattr(decision, "to_dict")
                        else decision
                    )

                except Exception as exc:
                    st.error(f"Federated route failed: {exc}")

    st.markdown("---")

    # ========================================================
    # DOMAIN CONTROLS
    # ========================================================

    st.markdown("## 🚨 Domain Controls")

    if domain_manager is not None:
        domains = domain_manager.list_domains()
        domain_ids = [d.get("domain_id") for d in domains if d.get("domain_id")]

        if domain_ids:
            selected_domain = st.selectbox(
                "Execution Domain",
                domain_ids,
                key="sov_control_domain",
            )

            reason = st.text_input(
                "Reason",
                value="manual_sovereignty_operator_action",
                key="sov_control_reason",
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button(
                    "Freeze Domain",
                    use_container_width=True,
                    key="freeze_domain_btn",
                ):
                    result = (
                        sovereign_controller.freeze_domain(selected_domain, reason=reason)
                        if sovereign_controller is not None
                        else {"ok": domain_manager.freeze_domain(selected_domain, reason=reason)}
                    )
                    st.warning(result)

            with c2:
                if st.button(
                    "Quarantine Domain",
                    use_container_width=True,
                    key="quarantine_domain_btn",
                ):
                    result = (
                        sovereign_controller.quarantine_domain(selected_domain, reason=reason)
                        if sovereign_controller is not None
                        else {"ok": domain_manager.quarantine_domain(selected_domain, reason=reason)}
                    )
                    st.warning(result)

            with c3:
                if st.button(
                    "Restore Domain",
                    use_container_width=True,
                    key="restore_domain_btn",
                ):
                    result = (
                        sovereign_controller.restore_domain(selected_domain)
                        if sovereign_controller is not None
                        else {"ok": domain_manager.restore_domain(selected_domain)}
                    )
                    st.success(result)

        else:
            st.info("No domains available for control.")

    st.markdown("---")

    # ========================================================
    # FEDERATION CONTEXT
    # ========================================================

    st.markdown("## 🌐 Federation Context")

    if federation_manager is not None:
        try:
            fed_health = federation_manager.federation_health()
            st.json(fed_health)

            with st.expander("Federated Runtime Topology"):
                st.json(federation_manager.federation_topology())

        except Exception as exc:
            st.error(f"Failed to load federation context: {exc}")
    else:
        st.info("Federation manager is unavailable or disabled.")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="sovereignty_war_room_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()