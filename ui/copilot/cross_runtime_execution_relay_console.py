"""
ui/copilot/cross_runtime_execution_relay_console.py

Cross Runtime Execution Relay Console.

Purpose:
- sovereign execution continuity command center
- cross-runtime relay visibility
- runtime transfer monitoring
- relay approval/block/failure visibility
- failover relay simulation
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

    if value in {"AUTHORIZED", "COMPLETED", "ONLINE", "READY"}:
        return "🟢"
    if value in {"PENDING", "IN_PROGRESS", "REQUIRES_APPROVAL"}:
        return "🟡"
    if value in {"BLOCKED", "FAILED", "OFFLINE", "QUARANTINED"}:
        return "🔴"
    return "⚪"


def _safe_df(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def render_cross_runtime_execution_relay_console(storage: Any) -> None:
    st.markdown("# 🔁 Cross-Runtime Execution Relay")
    st.caption(
        "Sovereign execution continuity, relay planning, failover transfer, and runtime portability."
    )

    relay = getattr(storage, "cross_runtime_execution_relay", None)
    federation = getattr(storage, "runtime_federation_manager", None)
    router = getattr(storage, "federated_execution_router", None)
    optimizer = getattr(storage, "sovereign_mesh_optimizer", None)

    if relay is None:
        st.error("Cross Runtime Execution Relay is unavailable.")
        return

    # ========================================================
    # STATUS
    # ========================================================

    st.markdown("## 🌐 Relay Status")

    try:
        status = relay.relay_status()
    except Exception as exc:
        status = {"error": str(exc)}

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Relays", status.get("relay_count", 0))
    c2.metric("Authorized", status.get("authorized", 0))
    c3.metric("Approvals", status.get("requires_approval", 0))
    c4.metric("Blocked", status.get("blocked", 0))
    c5.metric("Completed", status.get("completed", 0))
    c6.metric("Failed", status.get("failed", 0))

    st.markdown("---")

    # ========================================================
    # RELAYS
    # ========================================================

    st.markdown("## 📦 Relay Envelopes")

    try:
        relays = relay.list_relays(limit=250)

        rows = []
        for item in relays:
            rows.append(
                {
                    "Time": _fmt_ts(item.get("created_at_ms")),
                    "Relay": item.get("relay_id"),
                    "Status": f"{_icon(item.get('status'))} {item.get('status')}",
                    "Tenant": item.get("tenant_id"),
                    "Source": item.get("source_runtime_id"),
                    "Target": item.get("target_runtime_id"),
                    "Reason": item.get("reason"),
                    "Error": item.get("error"),
                }
            )

        if rows:
            st.dataframe(_safe_df(rows), use_container_width=True, height=420)
        else:
            st.info("No relay envelopes available.")

    except Exception as exc:
        st.error(f"Failed to load relay envelopes: {exc}")

    st.markdown("---")

    # ========================================================
    # RELAY RESULTS
    # ========================================================

    st.markdown("## ✅ Relay Results")

    try:
        results = relay.list_results(limit=250)

        rows = []
        for result in results:
            rows.append(
                {
                    "Time": _fmt_ts(result.get("completed_at_ms")),
                    "Relay": result.get("relay_id"),
                    "Status": f"{_icon(result.get('status'))} {result.get('status')}",
                    "OK": result.get("ok"),
                    "Target Runtime": result.get("target_runtime_id"),
                    "Target Job": result.get("target_job_id"),
                    "Message": result.get("message"),
                }
            )

        if rows:
            st.dataframe(_safe_df(rows), use_container_width=True, height=360)
        else:
            st.info("No relay results available.")

    except Exception as exc:
        st.error(f"Failed to load relay results: {exc}")

    st.markdown("---")

    # ========================================================
    # RELAY SIMULATOR
    # ========================================================

    st.markdown("## 🧪 Relay Simulator")

    r1, r2, r3 = st.columns(3)

    with r1:
        tenant_id = st.text_input(
            "Tenant ID",
            value="default",
            key="relay_sim_tenant",
        )

    with r2:
        source_runtime_id = st.text_input(
            "Source Runtime",
            value="local-runtime",
            key="relay_sim_source_runtime",
        )

    with r3:
        target_runtime_id = st.text_input(
            "Target Runtime",
            value="",
            key="relay_sim_target_runtime",
        )

    s1, s2 = st.columns(2)

    with s1:
        capability = st.text_input(
            "Capability",
            value="execution_queue",
            key="relay_sim_capability",
        )

    with s2:
        reason = st.selectbox(
            "Reason",
            [
                "MANUAL",
                "FAILOVER",
                "OPTIMIZATION",
                "RECOVERY",
                "SOVEREIGN_REROUTE",
            ],
            index=0,
            key="relay_sim_reason",
        )

    action = st.text_input(
        "Workload Action",
        value="SIMULATE_CROSS_RUNTIME_RELAY",
        key="relay_sim_action",
    )

    force = st.checkbox(
        "Force Execution",
        value=False,
        key="relay_sim_force",
    )

    workload = {
        "action": action,
        "capability": capability,
        "source": "cross_runtime_execution_relay_console",
    }

    execution_state = {
        "execution_id": "simulated-execution",
        "job_id": "simulated-job",
        "graph_id": "simulated-graph",
    }

    sim_tabs = st.tabs(["Plan Relay", "Execute Relay"])

    with sim_tabs[0]:
        if st.button(
            "Plan Relay",
            use_container_width=True,
            key="plan_relay_btn",
        ):
            try:
                planned = relay.plan_relay(
                    tenant_id=tenant_id,
                    source_runtime_id=source_runtime_id,
                    target_runtime_id=target_runtime_id or None,
                    workload=workload,
                    execution_state=execution_state,
                    reason=reason,
                    capability=capability,
                )

                st.json(
                    planned.to_dict()
                    if hasattr(planned, "to_dict")
                    else planned
                )

            except Exception as exc:
                st.error(f"Relay planning failed: {exc}")

    with sim_tabs[1]:
        if st.button(
            "Plan + Execute Relay",
            use_container_width=True,
            key="execute_relay_btn",
        ):
            try:
                result = relay.relay_execution(
                    tenant_id=tenant_id,
                    source_runtime_id=source_runtime_id,
                    target_runtime_id=target_runtime_id or None,
                    workload=workload,
                    execution_state=execution_state,
                    reason=reason,
                    capability=capability,
                    force=force,
                )

                st.json(
                    result.to_dict()
                    if hasattr(result, "to_dict")
                    else result
                )

            except Exception as exc:
                st.error(f"Relay execution failed: {exc}")

    st.markdown("---")

    # ========================================================
    # FAILOVER RELAY
    # ========================================================

    st.markdown("## 🔄 Failed Runtime Relay")

    runtime_ids = ["local-runtime"]

    try:
        if federation is not None:
            runtime_ids = [
                r.get("runtime_id")
                for r in federation.list_runtimes()
                if r.get("runtime_id")
            ] or runtime_ids
    except Exception:
        pass

    failed_runtime = st.selectbox(
        "Failed Runtime",
        runtime_ids,
        key="relay_failed_runtime",
    )

    if st.button(
        "Relay Failed Runtime",
        use_container_width=True,
        key="relay_failed_runtime_btn",
    ):
        try:
            result = relay.relay_failed_runtime(
                failed_runtime_id=failed_runtime,
                tenant_id="default",
                workload={
                    "action": "FAILED_RUNTIME_RELAY_FROM_CONSOLE",
                    "failed_runtime_id": failed_runtime,
                },
                execution_state={
                    "execution_id": "failed-runtime-continuity",
                },
                capability="execution_queue",
            )

            st.json(
                result.to_dict()
                if hasattr(result, "to_dict")
                else result
            )

        except Exception as exc:
            st.error(f"Failed runtime relay failed: {exc}")

    st.markdown("---")

    # ========================================================
    # CONTEXT SIGNALS
    # ========================================================

    st.markdown("## 🧠 Continuity Signals")

    tabs = st.tabs(
        [
            "Federation",
            "Router",
            "Optimizer",
            "Relay Status",
        ]
    )

    with tabs[0]:
        try:
            if federation is not None:
                st.json(federation.federation_health())
            else:
                st.info("Federation unavailable.")
        except Exception as exc:
            st.error(f"Federation signal failed: {exc}")

    with tabs[1]:
        try:
            if router is not None:
                st.json(router.routing_status())
            else:
                st.info("Federated router unavailable.")
        except Exception as exc:
            st.error(f"Router signal failed: {exc}")

    with tabs[2]:
        try:
            if optimizer is not None:
                st.json(optimizer.optimizer_status())
            else:
                st.info("Mesh optimizer unavailable.")
        except Exception as exc:
            st.error(f"Optimizer signal failed: {exc}")

    with tabs[3]:
        st.json(status)

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=False,
        key="cross_runtime_relay_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()