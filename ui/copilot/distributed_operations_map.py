"""
ui/copilot/distributed_operations_map.py

Distributed Operations Map.

Visual topology layer for:
- workers
- leases
- active graphs
- rollback propagation
- failover routing
- connector topology
- tenant segmentation
- execution pressure
"""

from __future__ import annotations

import time
import json
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


try:
    from core.runtime.distributed_execution_queue import (
        DistributedExecutionQueue,
        STATUS_PENDING,
        STATUS_LEASED,
        STATUS_RUNNING,
        STATUS_COMPLETED,
        STATUS_FAILED,
        STATUS_RETRY,
        STATUS_DEAD_LETTER,
    )
except Exception:
    DistributedExecutionQueue = None
    STATUS_PENDING = "PENDING"
    STATUS_LEASED = "LEASED"
    STATUS_RUNNING = "RUNNING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"
    STATUS_RETRY = "RETRY"
    STATUS_DEAD_LETTER = "DEAD_LETTER"


try:
    from core.connectors.connector_registry import get_connector_registry
except Exception:
    get_connector_registry = None


try:
    from core.connectors.connector_health_monitor import get_connector_health_monitor
except Exception:
    get_connector_health_monitor = None


try:
    from core.runtime.lease_watchdog import run_lease_watchdog_once
except Exception:
    run_lease_watchdog_once = None


# ============================================================
# MAIN RENDER
# ============================================================

def render_distributed_operations_map(
    storage: Optional[Any] = None,
    queue: Optional[Any] = None,
) -> None:

    st.subheader("🗺️ Distributed Operations Map")
    st.caption(
        "Topology view for workers, leases, graph execution, rollback propagation, "
        "connector failover, tenant segmentation, and execution pressure."
    )

    queue = queue or _build_queue()

    if queue is None:
        st.error("DistributedExecutionQueue unavailable.")
        return

    jobs = _safe_list_jobs(queue, limit=1000)
    rows = [_job_to_row(j) for j in jobs]
    df = pd.DataFrame(rows)

    if df.empty:
        st.info("No distributed execution jobs available yet.")
        _render_connector_topology()
        return

    # ========================================================
    # TOPLINE PRESSURE
    # ========================================================

    st.markdown("### 🌐 Operations Topology Summary")

    summary = _build_summary(df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Tenants", summary["tenants"])
    c2.metric("Workers", summary["workers"])
    c3.metric("Active Jobs", summary["active_jobs"])
    c4.metric("Queued", summary["queued"])
    c5.metric("Retries", summary["retries"])
    c6.metric("Dead Letter", summary["dead_letters"])

    st.markdown("---")

    # ========================================================
    # MAP FILTERS
    # ========================================================

    st.markdown("### 🎛️ Map Filters")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        tenant_filter = st.selectbox(
            "Tenant",
            ["ALL"] + sorted(df["tenant_id"].dropna().astype(str).unique().tolist()),
            key="ops_map_tenant_filter",
        )

    with f2:
        status_filter = st.selectbox(
            "Status",
            ["ALL"] + sorted(df["status"].dropna().astype(str).unique().tolist()),
            key="ops_map_status_filter",
        )

    with f3:
        worker_filter = st.selectbox(
            "Worker",
            ["ALL"] + sorted(df["worker_id"].dropna().astype(str).unique().tolist()),
            key="ops_map_worker_filter",
        )

    with f4:
        connector_filter = st.selectbox(
            "Connector",
            ["ALL"] + sorted(df["connector"].dropna().astype(str).unique().tolist()),
            key="ops_map_connector_filter",
        )

    filtered = df.copy()

    if tenant_filter != "ALL":
        filtered = filtered[filtered["tenant_id"].astype(str) == tenant_filter]

    if status_filter != "ALL":
        filtered = filtered[filtered["status"].astype(str) == status_filter]

    if worker_filter != "ALL":
        filtered = filtered[filtered["worker_id"].astype(str) == worker_filter]

    if connector_filter != "ALL":
        filtered = filtered[filtered["connector"].astype(str) == connector_filter]

    # ========================================================
    # TOPOLOGY TABS
    # ========================================================

    tabs = st.tabs(
        [
            "Tenant Map",
            "Worker / Lease Map",
            "Graph Map",
            "Rollback Map",
            "Connector Topology",
            "Watchdog",
        ]
    )

    with tabs[0]:
        _render_tenant_map(filtered)

    with tabs[1]:
        _render_worker_lease_map(filtered)

    with tabs[2]:
        _render_graph_map(filtered)

    with tabs[3]:
        _render_rollback_map(filtered)

    with tabs[4]:
        _render_connector_topology()

    with tabs[5]:
        _render_watchdog_controls(queue, storage)


# ============================================================
# TENANT MAP
# ============================================================

def _render_tenant_map(df: pd.DataFrame) -> None:
    st.markdown("### 🏢 Tenant Segmentation")

    tenant_rows = []

    for tenant_id, group in df.groupby("tenant_id"):
        statuses = Counter(group["status"].tolist())

        tenant_rows.append(
            {
                "Tenant": tenant_id,
                "Executions": len(group),
                "Active": int(group["status"].isin([STATUS_PENDING, STATUS_LEASED, STATUS_RUNNING, STATUS_RETRY]).sum()),
                "Running": statuses.get(STATUS_RUNNING, 0),
                "Retry": statuses.get(STATUS_RETRY, 0),
                "Dead Letter": statuses.get(STATUS_DEAD_LETTER, 0),
                "Workers": group["worker_id"].dropna().astype(str).nunique(),
                "Graphs": group["graph_id"].dropna().astype(str).nunique(),
                "Connectors": group["connector"].dropna().astype(str).nunique(),
            }
        )

    tenant_df = pd.DataFrame(tenant_rows)

    if tenant_df.empty:
        st.info("No tenant execution data.")
        return

    st.dataframe(
        tenant_df.sort_values("Executions", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    st.markdown("#### Tenant Pressure")

    pressure_rows = []

    for _, row in tenant_df.iterrows():
        pressure = _pressure_score(
            active=row["Active"],
            retry=row["Retry"],
            dead=row["Dead Letter"],
        )

        pressure_rows.append(
            {
                "Tenant": row["Tenant"],
                "Pressure Score": pressure,
                "Pressure Level": _pressure_level(pressure),
            }
        )

    st.dataframe(
        pd.DataFrame(pressure_rows).sort_values("Pressure Score", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=220,
    )


# ============================================================
# WORKER / LEASE MAP
# ============================================================

def _render_worker_lease_map(df: pd.DataFrame) -> None:
    st.markdown("### 🧑‍🏭 Worker / Lease Ownership")

    active = df[df["status"].isin([STATUS_LEASED, STATUS_RUNNING])]

    if active.empty:
        st.success("No leased/running jobs currently held by workers.")
    else:
        worker_rows = []

        for worker_id, group in active.groupby("worker_id"):
            worker_rows.append(
                {
                    "Worker": worker_id,
                    "Leased / Running": len(group),
                    "Tenants": group["tenant_id"].dropna().astype(str).nunique(),
                    "Graphs": group["graph_id"].dropna().astype(str).nunique(),
                    "Oldest Lease Age (sec)": _oldest_age_seconds(group, "updated_at_ms"),
                    "Connectors": ", ".join(sorted(group["connector"].dropna().astype(str).unique().tolist())),
                }
            )

        st.dataframe(
            pd.DataFrame(worker_rows).sort_values("Leased / Running", ascending=False),
            use_container_width=True,
            hide_index=True,
            height=300,
        )

    st.markdown("#### Lease Detail")

    lease_cols = [
        "job_id",
        "tenant_id",
        "worker_id",
        "job_type",
        "status",
        "action",
        "connector",
        "target",
        "lease_expires_ms",
        "attempts",
    ]

    available_cols = [c for c in lease_cols if c in df.columns]

    st.dataframe(
        df[df["status"].isin([STATUS_LEASED, STATUS_RUNNING])][available_cols],
        use_container_width=True,
        hide_index=True,
        height=300,
    )


# ============================================================
# GRAPH MAP
# ============================================================

def _render_graph_map(df: pd.DataFrame) -> None:
    st.markdown("### 🧬 Graph Execution Paths")

    graph_df = df[df["graph_id"].notna() & (df["graph_id"].astype(str) != "")]

    if graph_df.empty:
        st.info("No graph-linked executions found.")
        return

    graph_rows = []

    for graph_id, group in graph_df.groupby("graph_id"):
        statuses = Counter(group["status"].tolist())

        graph_rows.append(
            {
                "Graph ID": graph_id,
                "Tenant": _first(group, "tenant_id"),
                "Executions": len(group),
                "Running": statuses.get(STATUS_RUNNING, 0),
                "Retry": statuses.get(STATUS_RETRY, 0),
                "Failed": statuses.get(STATUS_FAILED, 0),
                "Dead Letter": statuses.get(STATUS_DEAD_LETTER, 0),
                "Actions": " → ".join(group["action"].dropna().astype(str).tolist()[:8]),
                "Connectors": " → ".join(group["connector"].dropna().astype(str).tolist()[:8]),
            }
        )

    st.dataframe(
        pd.DataFrame(graph_rows).sort_values("Executions", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    selected_graph = st.selectbox(
        "Inspect Graph",
        sorted(graph_df["graph_id"].dropna().astype(str).unique().tolist()),
        key="ops_map_graph_select",
    )

    if selected_graph:
        selected = graph_df[graph_df["graph_id"].astype(str) == selected_graph]

        st.markdown("#### Graph Node / Action Chain")

        st.dataframe(
            selected[
                [
                    "job_id",
                    "tenant_id",
                    "job_type",
                    "status",
                    "agent_name",
                    "action",
                    "connector",
                    "target",
                    "attempts",
                    "last_error",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=300,
        )


# ============================================================
# ROLLBACK MAP
# ============================================================

def _render_rollback_map(df: pd.DataFrame) -> None:
    st.markdown("### 🔄 Rollback Propagation")

    rollback_df = df[
        (df["job_type"].astype(str).str.upper() == "ROLLBACK")
        | (df["rollback_action"].notna() & (df["rollback_action"].astype(str) != ""))
        | (df["action"].astype(str).str.contains("rollback", case=False, na=False))
    ]

    if rollback_df.empty:
        st.info("No rollback propagation detected.")
        return

    c1, c2, c3 = st.columns(3)

    c1.metric("Rollback Jobs", len(rollback_df))
    c2.metric("Rollback Tenants", rollback_df["tenant_id"].dropna().astype(str).nunique())
    c3.metric("Rollback Graphs", rollback_df["graph_id"].dropna().astype(str).nunique())

    st.dataframe(
        rollback_df[
            [
                "job_id",
                "tenant_id",
                "graph_id",
                "case_id",
                "status",
                "action",
                "rollback_action",
                "connector",
                "target",
                "attempts",
                "last_error",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=350,
    )


# ============================================================
# CONNECTOR TOPOLOGY
# ============================================================

def _render_connector_topology() -> None:
    st.markdown("### 🔌 Connector Routing Topology")

    registry = get_connector_registry() if get_connector_registry else None
    monitor = get_connector_health_monitor() if get_connector_health_monitor else None

    if registry is None:
        st.warning("Connector registry unavailable.")
        return

    registrations = registry.list_connectors()

    if not registrations:
        st.info("No connectors registered.")
        return

    rows = []

    for reg in registrations:
        connector_name = (
                reg.get("connector_id")
                or reg.get("name")
                or "unknown"
        )

        health = monitor.get_state(
            connector_name
        )

        rows.append(
            {
                "Connector": (
                    reg.get("connector_id")
                    or reg.get("name")
                    or "unknown"
                ),
                "Enabled": reg.enabled,
                "Quarantined": reg.quarantined,
                "Priority": reg.priority,
                "Capabilities": ", ".join(reg.capabilities),
                "Tenant Scope": ", ".join(reg.tenant_scope or []),
                "Health": getattr(health, "health", "UNKNOWN") if health else "UNKNOWN",
                "Failures": getattr(health, "failure_count", 0) if health else 0,
                "Retries": getattr(health, "retry_count", 0) if health else 0,
                "Latency(ms)": round(getattr(health, "avg_latency_ms", 0.0), 2) if health else 0,
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        height=350,
    )

    st.markdown("#### Capability Failover Chains")

    capabilities = set()

    for reg in registrations:
        capabilities.update(reg.capabilities)

    topo = []

    for capability in sorted(capabilities):
        topo.append(
            {
                "Capability": capability,
                "Failover Chain": " → ".join(registry.get_failover_chain(capability)),
            }
        )

    st.dataframe(
        pd.DataFrame(topo),
        use_container_width=True,
        hide_index=True,
        height=250,
    )


# ============================================================
# WATCHDOG
# ============================================================

def _render_watchdog_controls(queue: Any, storage: Optional[Any]) -> None:
    st.markdown("### 🐕 Lease Watchdog")

    if run_lease_watchdog_once is None:
        st.warning("Lease watchdog unavailable.")
        return

    if st.button("Run Watchdog Scan", key="ops_map_run_watchdog"):
        result = run_lease_watchdog_once(queue=queue, storage=storage)

        if result.get("success"):
            st.success(f"Watchdog scan completed. Findings: {result.get('finding_count', 0)}")
        else:
            st.error("Watchdog scan failed.")

        st.json(result)


# ============================================================
# HELPERS
# ============================================================

def _build_queue():
    if DistributedExecutionQueue is None:
        return None

    try:
        return DistributedExecutionQueue()
    except Exception:
        return None


def _safe_list_jobs(queue: Any, limit: int = 1000) -> List[Any]:
    try:
        return queue.list_jobs(limit=limit)
    except Exception:
        return []


def _job_to_row(job: Any) -> Dict[str, Any]:
    payload = getattr(job, "payload", {}) or {}
    context = payload.get("context", {}) or {}

    if not isinstance(context, dict):
        context = {}

    return {
        "job_id": getattr(job, "job_id", None),
        "job_type": getattr(job, "job_type", None),
        "tenant_id": getattr(job, "tenant_id", None),
        "status": getattr(job, "status", None),
        "priority": getattr(job, "priority", None),
        "attempts": getattr(job, "attempts", None),
        "max_attempts": getattr(job, "max_attempts", None),
        "worker_id": getattr(job, "worker_id", None),
        "lease_expires_ms": getattr(job, "lease_expires_ms", None),
        "created_at_ms": getattr(job, "created_at_ms", None),
        "updated_at_ms": getattr(job, "updated_at_ms", None),
        "available_at_ms": getattr(job, "available_at_ms", None),
        "last_error": getattr(job, "last_error", None),
        "agent_name": payload.get("agent_name"),
        "action": payload.get("action") or context.get("action"),
        "connector": context.get("connector"),
        "target": context.get("target") or context.get("endpoint") or context.get("mailbox") or context.get("user"),
        "graph_id": payload.get("graph_id") or context.get("graph_id"),
        "case_id": payload.get("case_id") or context.get("case_id"),
        "severity": context.get("severity"),
        "rollback_action": payload.get("rollback_action") or context.get("rollback_action"),
    }


def _build_summary(df: pd.DataFrame) -> Dict[str, int]:
    active_statuses = [STATUS_PENDING, STATUS_LEASED, STATUS_RUNNING, STATUS_RETRY]

    return {
        "tenants": int(df["tenant_id"].dropna().astype(str).nunique()),
        "workers": int(df["worker_id"].dropna().astype(str).nunique()),
        "active_jobs": int(df["status"].isin(active_statuses).sum()),
        "queued": int(df["status"].isin([STATUS_PENDING, STATUS_RETRY]).sum()),
        "retries": int((df["status"] == STATUS_RETRY).sum()),
        "dead_letters": int((df["status"] == STATUS_DEAD_LETTER).sum()),
    }


def _pressure_score(active: int, retry: int, dead: int) -> int:
    return int((active * 2) + (retry * 5) + (dead * 10))


def _pressure_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 40:
        return "HIGH"
    if score >= 15:
        return "MEDIUM"
    return "LOW"


def _oldest_age_seconds(df: pd.DataFrame, col: str) -> int:
    if df.empty or col not in df.columns:
        return 0

    vals = [
        int(v)
        for v in df[col].dropna().tolist()
        if str(v).isdigit()
    ]

    if not vals:
        return 0

    oldest = min(vals)
    return int((time.time() * 1000 - oldest) / 1000)


def _first(df: pd.DataFrame, col: str) -> Any:
    try:
        values = df[col].dropna().tolist()
        return values[0] if values else None
    except Exception:
        return None