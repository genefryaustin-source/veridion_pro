"""
ui/copilot/distributed_agent_fabric_console.py

Distributed Agent Fabric Console
for Veridion Pro / CUI GovCloud.

Provides:
- distributed worker visibility
- lease orchestration telemetry
- tenant-aware execution routing
- autonomous workload balancing
- lease recovery visibility
- distributed retry monitoring
- worker heartbeat monitoring
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from core.runtime.distributed_agent_fabric import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_LEASED,
    STATUS_PENDING,
    STATUS_RETRY,
    STATUS_RUNNING,
    WORKER_DEAD,
    WORKER_DEGRADED,
    WORKER_HEALTHY,
)


SEVERITY_COLORS = {
    "HEALTHY": "#22c55e",
    "DEGRADED": "#f59e0b",
    "DEAD": "#dc2626",
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_json(value: Any) -> Dict[str, Any]:

    if isinstance(value, dict):
        return value

    try:
        return json.loads(value or "{}")

    except Exception:
        return {}


# ---------------------------------------------------------------------
# MAIN RENDER
# ---------------------------------------------------------------------

def render_distributed_agent_fabric_console(
    storage: Any,
) -> None:

    st.markdown(
        """
        ## 🌐 Distributed Agent Fabric

        Realtime distributed autonomous execution fabric.
        """
    )

    fabric = getattr(
        storage,
        "distributed_agent_fabric",
        None,
    )

    if fabric is None:

        st.error(
            "Distributed agent fabric unavailable."
        )

        return

    workers = fabric.list_workers()

    leases = fabric.list_leases(
        limit=500
    )

    metrics = _build_metrics(
        workers,
        leases,
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Workers",
        metrics["workers"],
    )

    c2.metric(
        "Healthy",
        metrics["healthy"],
    )

    c3.metric(
        "Running Leases",
        metrics["running"],
    )

    c4.metric(
        "Retries",
        metrics["retries"],
    )

    c5.metric(
        "Failures",
        metrics["failures"],
    )

    st.divider()

    # -------------------------------------------------------------
    # WORKERS
    # -------------------------------------------------------------

    st.markdown(
        "### 🖥️ Distributed Workers"
    )

    if not workers:

        st.warning(
            "No workers registered."
        )

    else:

        for idx, worker in enumerate(
            workers
        ):

            _render_worker_card(
                worker,
                idx,
            )

    st.divider()

    # -------------------------------------------------------------
    # LEASES
    # -------------------------------------------------------------

    st.markdown(
        "### 🔐 Distributed Leases"
    )

    lease_rows = [
        _lease_row(l)
        for l in leases
    ]

    if lease_rows:

        st.dataframe(
            pd.DataFrame(
                lease_rows
            ),
            use_container_width=True,
            height=420,
        )

    else:

        st.info(
            "No leases available."
        )

    st.divider()

    # -------------------------------------------------------------
    # ACTIVE EXECUTION
    # -------------------------------------------------------------

    st.markdown(
        "### 🚀 Active Distributed Execution"
    )

    active = [
        l
        for l in leases
        if l.get("status")
        in (
            STATUS_LEASED,
            STATUS_RUNNING,
        )
    ]

    if not active:

        st.success(
            "No active distributed execution."
        )

    else:

        for idx, lease in enumerate(
            active[:50]
        ):

            _render_lease_card(
                lease,
                idx,
            )

    st.divider()

    # -------------------------------------------------------------
    # FABRIC CONTROLS
    # -------------------------------------------------------------

    st.markdown(
        "### 🛠️ Fabric Recovery Controls"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "♻️ Reclaim Expired Leases",
            key="fabric_reclaim_button",
        ):

            try:

                reclaimed = (
                    fabric.reclaim_expired_leases()
                )

                st.success(
                    f"Reclaimed leases: {reclaimed}"
                )

            except Exception as exc:

                st.error(str(exc))

    with c2:

        if st.button(
            "💀 Detect Dead Workers",
            key="fabric_dead_worker_button",
        ):

            try:

                dead = (
                    fabric.detect_dead_workers()
                )

                st.warning(
                    f"Dead workers: {dead}"
                )

            except Exception as exc:

                st.error(str(exc))


# ---------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------

def _build_metrics(
    workers: List[Dict[str, Any]],
    leases: List[Dict[str, Any]],
) -> Dict[str, int]:

    return {

        "workers": len(workers),

        "healthy": sum(
            1
            for w in workers
            if w.get("status")
            == WORKER_HEALTHY
        ),

        "running": sum(
            1
            for l in leases
            if l.get("status")
            in (
                STATUS_LEASED,
                STATUS_RUNNING,
            )
        ),

        "retries": sum(
            1
            for l in leases
            if l.get("status")
            == STATUS_RETRY
        ),

        "failures": sum(
            1
            for l in leases
            if l.get("status")
            == STATUS_FAILED
        ),
    }


# ---------------------------------------------------------------------
# WORKER CARD
# ---------------------------------------------------------------------

def _render_worker_card(
    worker: Dict[str, Any],
    idx: int,
) -> None:

    status = str(
        worker.get(
            "status",
            WORKER_HEALTHY,
        )
    ).upper()

    color = SEVERITY_COLORS.get(
        status,
        "#64748b",
    )

    st.markdown(
        f'''
        <div style="
            border-left: 6px solid {color};
            background:#111827;
            padding:14px;
            border-radius:10px;
            margin-bottom:12px;
            color:white;
        ">
            <div style="
                font-size:18px;
                font-weight:900;
            ">
                🌐 {worker.get("worker_id")}
            </div>

            <div style="margin-top:8px;">
                <b>Status:</b> {status}<br>
                <b>Tenant:</b> {worker.get("tenant_id")}<br>
                <b>Hostname:</b> {worker.get("hostname")}<br>
                <b>Last Heartbeat:</b> {worker.get("last_heartbeat_ms")}<br>
                <b>Max Tasks:</b> {worker.get("max_concurrent_tasks")}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# LEASE CARD
# ---------------------------------------------------------------------

def _render_lease_card(
    lease: Dict[str, Any],
    idx: int,
) -> None:

    status = lease.get(
        "status"
    )

    color = "#3b82f6"

    if status == STATUS_FAILED:
        color = "#dc2626"

    elif status == STATUS_RETRY:
        color = "#f59e0b"

    elif status == STATUS_COMPLETED:
        color = "#22c55e"

    st.markdown(
        f'''
        <div style="
            border-left: 6px solid {color};
            background:#0f172a;
            padding:14px;
            border-radius:10px;
            margin-bottom:10px;
            color:white;
        ">
            <div style="
                font-size:16px;
                font-weight:900;
            ">
                🔐 {lease.get("lease_id")}
            </div>

            <div style="margin-top:8px;">
                <b>Status:</b> {status}<br>
                <b>Worker:</b> {lease.get("worker_id")}<br>
                <b>Task:</b> {lease.get("task_id")}<br>
                <b>Agent:</b> {lease.get("agent_name")}<br>
                <b>Attempts:</b> {lease.get("attempts")}
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# ROW
# ---------------------------------------------------------------------

def _lease_row(
    lease: Dict[str, Any],
) -> Dict[str, Any]:

    return {

        "lease_id": lease.get(
            "lease_id"
        ),

        "task_id": lease.get(
            "task_id"
        ),

        "worker_id": lease.get(
            "worker_id"
        ),

        "agent": lease.get(
            "agent_name"
        ),

        "task_type": lease.get(
            "task_type"
        ),

        "status": lease.get(
            "status"
        ),

        "attempts": lease.get(
            "attempts"
        ),

        "tenant_id": lease.get(
            "tenant_id"
        ),

        "lease_expires_ms": lease.get(
            "lease_expires_ms"
        ),
    }