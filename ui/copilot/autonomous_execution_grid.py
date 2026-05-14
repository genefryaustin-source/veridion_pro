"""
ui/copilot/autonomous_execution_grid.py

Autonomous Execution Grid.

Operational nerve center for:
- distributed execution visibility
- queue pressure
- sandbox decisions
- connector routing
- rollback chains
- dead-letter monitoring
- graph execution visibility
- tenant isolation visibility
- autonomy governance telemetry
"""

from __future__ import annotations

import json
from collections import Counter
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

try:
    from core.events.websocket_hub import get_websocket_hub
except Exception:
    def get_websocket_hub():
        return None


# ============================================================
# MAIN RENDER
# ============================================================

def render_autonomous_execution_grid(
    storage: Optional[Any] = None,
    queue: Optional[Any] = None,
) -> None:

    st.subheader("⚡ Autonomous Execution Grid")
    st.caption(
        "Distributed execution telemetry, sandbox governance, "
        "connector routing, rollback visibility, and tenant isolation."
    )

    queue = queue or _build_queue()

    if queue is None:
        st.error("DistributedExecutionQueue unavailable.")
        return

    # ========================================================
    # LOAD JOBS
    # ========================================================

    jobs = _safe_list_jobs(queue, limit=500)

    if not jobs:
        st.info("No execution jobs available.")
        return

    rows = [_job_to_row(j) for j in jobs]
    df = pd.DataFrame(rows)

    # ========================================================
    # FILTERS
    # ========================================================

    st.markdown("### 🎛️ Execution Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        tenant_filter = st.selectbox(
            "Tenant",
            ["ALL"] + sorted(df["tenant_id"].dropna().astype(str).unique().tolist()),
            key="execution_grid_tenant_filter",
        )

    with col2:
        status_filter = st.selectbox(
            "Status",
            ["ALL"] + sorted(df["status"].dropna().astype(str).unique().tolist()),
            key="execution_grid_status_filter",
        )

    with col3:
        job_type_filter = st.selectbox(
            "Job Type",
            ["ALL"] + sorted(df["job_type"].dropna().astype(str).unique().tolist()),
            key="execution_grid_job_type_filter",
        )

    with col4:
        connector_filter = st.selectbox(
            "Connector",
            ["ALL"] + sorted(df["connector"].dropna().astype(str).unique().tolist()),
            key="execution_grid_connector_filter",
        )

    filtered_df = df.copy()

    if tenant_filter != "ALL":
        filtered_df = filtered_df[
            filtered_df["tenant_id"].astype(str) == tenant_filter
        ]

    if status_filter != "ALL":
        filtered_df = filtered_df[
            filtered_df["status"].astype(str) == status_filter
        ]

    if job_type_filter != "ALL":
        filtered_df = filtered_df[
            filtered_df["job_type"].astype(str) == job_type_filter
        ]

    if connector_filter != "ALL":
        filtered_df = filtered_df[
            filtered_df["connector"].astype(str) == connector_filter
        ]

    # ========================================================
    # EXECUTION METRICS
    # ========================================================

    st.markdown("### 📊 Distributed Execution Metrics")

    stats = _build_stats(filtered_df)

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Pending", stats["pending"])
    c2.metric("Running", stats["running"])
    c3.metric("Retry", stats["retry"])
    c4.metric("Dead Letter", stats["dead_letter"])
    c5.metric("Completed", stats["completed"])
    c6.metric("Failed", stats["failed"])

    # ========================================================
    # SANDBOX VISIBILITY
    # ========================================================

    st.markdown("### 🛡️ Sandbox Governance")

    sandbox_col1, sandbox_col2, sandbox_col3 = st.columns(3)

    sandbox_col1.metric(
        "Sandbox Blocked",
        int(filtered_df["sandbox_blocked"].sum())
        if "sandbox_blocked" in filtered_df.columns
        else 0,
    )

    sandbox_col2.metric(
        "Approval Required",
        int(filtered_df["approval_required"].sum())
        if "approval_required" in filtered_df.columns
        else 0,
    )

    sandbox_col3.metric(
        "Rollback Supported",
        int(filtered_df["rollback_supported"].sum())
        if "rollback_supported" in filtered_df.columns
        else 0,
    )

    # ========================================================
    # QUEUE PRESSURE
    # ========================================================

    st.markdown("### 🔥 Queue Pressure")

    queue_pressure = _queue_pressure_summary(filtered_df)

    qp1, qp2, qp3, qp4 = st.columns(4)

    qp1.metric("Queued", queue_pressure["queued"])
    qp2.metric("Leased", queue_pressure["leased"])
    qp3.metric("Workers", queue_pressure["workers"])
    qp4.metric("Tenants", queue_pressure["tenants"])

    # ========================================================
    # ACTIVE EXECUTIONS
    # ========================================================

    st.markdown("### ⚡ Active Executions")

    active_df = filtered_df[
        filtered_df["status"].isin([
            STATUS_PENDING,
            STATUS_LEASED,
            STATUS_RUNNING,
            STATUS_RETRY,
        ])
    ]

    if active_df.empty:
        st.success("No active distributed executions.")
    else:
        st.dataframe(
            active_df[
                [
                    "job_id",
                    "tenant_id",
                    "job_type",
                    "status",
                    "agent_name",
                    "action",
                    "connector",
                    "target",
                    "worker_id",
                    "attempts",
                    "priority",
                ]
            ],
            use_container_width=True,
            height=350,
        )

    # ========================================================
    # DEAD LETTER QUEUE
    # ========================================================

    st.markdown("### ☠️ Dead Letter Queue")

    dead_df = filtered_df[
        filtered_df["status"] == STATUS_DEAD_LETTER
    ]

    if dead_df.empty:
        st.success("No dead-letter jobs.")
    else:
        st.error(f"{len(dead_df)} dead-letter jobs detected.")

        st.dataframe(
            dead_df[
                [
                    "job_id",
                    "tenant_id",
                    "job_type",
                    "action",
                    "connector",
                    "attempts",
                    "last_error",
                ]
            ],
            use_container_width=True,
            height=250,
        )

    # ========================================================
    # TENANT ISOLATION
    # ========================================================

    st.markdown("### 🏢 Tenant Isolation Visibility")

    tenant_counts = (
        filtered_df.groupby("tenant_id")
        .size()
        .reset_index(name="executions")
        .sort_values("executions", ascending=False)
    )

    st.dataframe(
        tenant_counts,
        use_container_width=True,
        height=220,
    )

    # ========================================================
    # CONNECTOR ROUTING
    # ========================================================

    st.markdown("### 🔌 Connector Routing")

    connector_summary = (
        filtered_df.groupby(["connector", "status"])
        .size()
        .reset_index(name="count")
    )

    st.dataframe(
        connector_summary,
        use_container_width=True,
        height=220,
    )

    # ========================================================
    # ROLLBACK VISIBILITY
    # ========================================================

    st.markdown("### 🔄 Rollback Chains")

    rollback_df = filtered_df[
        filtered_df["rollback_supported"] == True
    ]

    if rollback_df.empty:
        st.info("No rollback-enabled executions.")
    else:
        st.dataframe(
            rollback_df[
                [
                    "job_id",
                    "action",
                    "connector",
                    "rollback_action",
                    "tenant_id",
                    "status",
                ]
            ],
            use_container_width=True,
            height=250,
        )

    # ========================================================
    # EXECUTION DETAILS
    # ========================================================

    st.markdown("### 🔍 Execution Inspection")

    selected_job = st.selectbox(
        "Select Execution",
        filtered_df["job_id"].tolist(),
        key="execution_grid_job_select",
    )

    if selected_job:

        selected_row = filtered_df[
            filtered_df["job_id"] == selected_job
        ]

        if not selected_row.empty:

            row = selected_row.iloc[0].to_dict()

            with st.expander("Execution Details", expanded=True):

                st.json(
                    {
                        k: _safe_json(v)
                        for k, v in row.items()
                    }
                )

            try:
                events = queue.list_events(selected_job)

                if events:
                    st.markdown("### 📜 Execution Timeline")

                    timeline_df = pd.DataFrame(events)

                    st.dataframe(
                        timeline_df,
                        use_container_width=True,
                        height=300,
                    )

            except Exception as e:
                st.warning(f"Unable to load execution events: {e}")

    # ========================================================
    # LIVE STREAM
    # ========================================================

    st.markdown("### 📡 Live Stream Status")

    hub = get_websocket_hub()

    if hub is not None:

        try:
            stats = hub.get_stats()

            ws1, ws2, ws3 = st.columns(3)

            ws1.metric(
                "Connected Clients",
                stats.get("connected_clients", 0),
            )

            ws2.metric(
                "Messages Published",
                stats.get("messages_published", 0),
            )

            ws3.metric(
                "Active Channels",
                stats.get("channels", 0),
            )

        except Exception as e:
            st.warning(f"Websocket telemetry unavailable: {e}")


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


def _safe_list_jobs(queue, limit=500):

    try:
        return queue.list_jobs(limit=limit)
    except Exception:
        return []


def _job_to_row(job) -> Dict[str, Any]:

    payload = getattr(job, "payload", {}) or {}

    context = payload.get("context", {}) or {}

    return {
        "job_id": getattr(job, "job_id", None),
        "tenant_id": getattr(job, "tenant_id", None),
        "job_type": getattr(job, "job_type", None),
        "status": getattr(job, "status", None),
        "priority": getattr(job, "priority", None),
        "attempts": getattr(job, "attempts", None),
        "worker_id": getattr(job, "worker_id", None),
        "lease_expires_ms": getattr(job, "lease_expires_ms", None),
        "created_at_ms": getattr(job, "created_at_ms", None),
        "updated_at_ms": getattr(job, "updated_at_ms", None),
        "available_at_ms": getattr(job, "available_at_ms", None),
        "last_error": getattr(job, "last_error", None),
        "agent_name": payload.get("agent_name"),
        "action": payload.get("action"),
        "connector": context.get("connector"),
        "target": context.get("target"),
        "graph_id": context.get("graph_id"),
        "case_id": context.get("case_id"),
        "severity": context.get("severity"),
        "sandbox_blocked": bool(
            context.get("sandbox_decision") == "BLOCK"
        ),
        "approval_required": bool(
            context.get("approval_required")
        ),
        "rollback_supported": bool(
            context.get("rollback_supported")
        ),
        "rollback_action": context.get("rollback_action"),
    }


def _build_stats(df: pd.DataFrame) -> Dict[str, int]:

    counter = Counter(df["status"].tolist())

    return {
        "pending": counter.get(STATUS_PENDING, 0),
        "leased": counter.get(STATUS_LEASED, 0),
        "running": counter.get(STATUS_RUNNING, 0),
        "completed": counter.get(STATUS_COMPLETED, 0),
        "failed": counter.get(STATUS_FAILED, 0),
        "retry": counter.get(STATUS_RETRY, 0),
        "dead_letter": counter.get(STATUS_DEAD_LETTER, 0),
    }


def _queue_pressure_summary(df: pd.DataFrame) -> Dict[str, int]:

    queued = len(
        df[
            df["status"].isin([
                STATUS_PENDING,
                STATUS_RETRY,
            ])
        ]
    )

    leased = len(
        df[
            df["status"].isin([
                STATUS_LEASED,
                STATUS_RUNNING,
            ])
        ]
    )

    workers = (
        df["worker_id"]
        .dropna()
        .astype(str)
        .nunique()
    )

    tenants = (
        df["tenant_id"]
        .dropna()
        .astype(str)
        .nunique()
    )

    return {
        "queued": int(queued),
        "leased": int(leased),
        "workers": int(workers),
        "tenants": int(tenants),
    }


def _safe_json(value):

    try:
        json.dumps(value, default=str)
        return value
    except Exception:
        return str(value)