"""
ui/copilot/distributed_execution_queue_console.py

Distributed Execution Queue Console.

Provides:
- live queue visibility
- dead-letter operations
- lease visibility
- worker ownership
- retry analytics
- execution stream
- replay/requeue controls
- worker quarantine controls
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from core.runtime.distributed_execution_queue import (
    STATUS_PENDING,
    STATUS_RETRY,
    STATUS_LEASED,
    STATUS_RUNNING,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_DEAD_LETTER,
)

from core.runtime.worker_orchestrator import (
    WORKER_STATUS_QUARANTINED,
)


# ============================================================
# HELPERS
# ============================================================

def _fmt_ts(ms: Optional[int]) -> str:
    if not ms:
        return "-"

    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(ms / 1000),
        )
    except Exception:
        return str(ms)


def _lease_age_ms(job: Dict[str, Any]) -> Optional[int]:
    lease_expires = job.get("lease_expires_ms")

    if not lease_expires:
        return None

    return int(lease_expires) - int(time.time() * 1000)


def _job_color(status: str) -> str:
    mapping = {
        STATUS_PENDING: "#1E88E5",
        STATUS_RETRY: "#FB8C00",
        STATUS_LEASED: "#8E24AA",
        STATUS_RUNNING: "#43A047",
        STATUS_COMPLETED: "#00ACC1",
        STATUS_FAILED: "#E53935",
        STATUS_DEAD_LETTER: "#B71C1C",
    }

    return mapping.get(status, "#9E9E9E")


# ============================================================
# MAIN CONSOLE
# ============================================================

def render_distributed_execution_queue_console(
    storage: Any,
) -> None:

    st.markdown("# ⚙️ Distributed Execution Queue")

    queue = getattr(
        storage,
        "execution_queue",
        None,
    )

    orchestrator = getattr(
        storage,
        "worker_orchestrator",
        None,
    )

    watchdog = getattr(
        storage,
        "lease_watchdog",
        None,
    )

    if queue is None:
        st.error("Execution queue unavailable.")
        return

    # ========================================================
    # METRICS
    # ========================================================

    stats = queue.stats()

    st.markdown("## 📊 Queue Metrics")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Pending",
        stats.get("pending", 0),
    )

    c2.metric(
        "Running",
        stats.get("running", 0),
    )

    c3.metric(
        "Retry",
        stats.get("retry", 0),
    )

    c4.metric(
        "Dead Letter",
        stats.get("dead_letter", 0),
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Leased",
        stats.get("leased", 0),
    )

    c6.metric(
        "Completed",
        stats.get("completed", 0),
    )

    c7.metric(
        "Failed",
        stats.get("failed", 0),
    )

    c8.metric(
        "Total",
        stats.get("total", 0),
    )

    st.markdown("---")

    # ========================================================
    # FILTERS
    # ========================================================

    st.markdown("## 🔍 Queue Filters")

    fc1, fc2, fc3 = st.columns(3)

    status_filter = fc1.selectbox(
        "Status",
        [
            "ALL",
            STATUS_PENDING,
            STATUS_RETRY,
            STATUS_LEASED,
            STATUS_RUNNING,
            STATUS_COMPLETED,
            STATUS_FAILED,
            STATUS_DEAD_LETTER,
        ],
        key="queue_status_filter",
    )

    tenant_filter = fc2.text_input(
        "Tenant",
        key="queue_tenant_filter",
    )

    limit = fc3.slider(
        "Limit",
        min_value=25,
        max_value=1000,
        value=250,
        step=25,
        key="queue_limit",
    )

    jobs = queue.list_jobs(
        status=None if status_filter == "ALL" else status_filter,
        tenant_id=tenant_filter or None,
        limit=limit,
    )

    # ========================================================
    # LIVE JOB TABLE
    # ========================================================

    st.markdown("## 🧠 Live Execution Jobs")

    rows = []

    for job in jobs:

        lease_remaining = _lease_age_ms(job)

        rows.append({

            "Job ID":
                job.get("job_id"),

            "Type":
                job.get("job_type"),

            "Tenant":
                job.get("tenant_id"),

            "Status":
                job.get("status"),

            "Priority":
                job.get("priority"),

            "Worker":
                job.get("worker_id"),

            "Attempts":
                f"{job.get('attempts')}/{job.get('max_attempts')}",

            "Lease Remaining(ms)":
                lease_remaining,

            "Created":
                _fmt_ts(
                    job.get("created_at_ms")
                ),

            "Updated":
                _fmt_ts(
                    job.get("updated_at_ms")
                ),

            "Completed":
                _fmt_ts(
                    job.get("completed_at_ms")
                ),

            "Error":
                job.get("last_error"),
        })

    jobs_df = pd.DataFrame(rows)

    st.dataframe(
        jobs_df,
        use_container_width=True,
        height=450,
    )

    st.markdown("---")

    # ========================================================
    # DEAD LETTER CENTER
    # ========================================================

    st.markdown("## ☠️ Dead Letter Operations")

    dead_letter_jobs = [

        j for j in jobs

        if j.get("status") == STATUS_DEAD_LETTER
    ]

    dead_ids = [
        j.get("job_id")
        for j in dead_letter_jobs
    ]

    selected_dead = st.selectbox(
        "Dead Letter Job",
        dead_ids if dead_ids else ["None"],
        key="dead_letter_select",
    )

    if selected_dead != "None":

        dead_job = next(
            (
                j for j in dead_letter_jobs
                if j.get("job_id") == selected_dead
            ),
            None,
        )

        if dead_job:

            st.json(dead_job)

            dc1, dc2, dc3 = st.columns(3)

            with dc1:

                if st.button(
                    "Replay Job",
                    key="replay_dead_job_btn",
                ):

                    queue.enqueue(
                        job_type=dead_job.get("job_type"),
                        tenant_id=dead_job.get("tenant_id"),
                        priority=dead_job.get("priority"),
                        agent_name=dead_job.get("agent_name"),
                        action=dead_job.get("action"),
                        payload=dead_job.get("payload"),
                    )

                    st.success("Replay queued.")

            with dc2:

                if st.button(
                    "Trigger Rollback",
                    key="dead_job_rollback_btn",
                ):

                    queue.enqueue_rollback(
                        rollback_payload={
                            "source_job": dead_job,
                            "reason": "dead_letter_recovery",
                        },
                        tenant_id=dead_job.get("tenant_id"),
                        priority=1,
                    )

                    st.warning("Rollback job queued.")

            with dc3:

                if st.button(
                    "Inspect Payload",
                    key="inspect_dead_payload_btn",
                ):

                    st.code(
                        json.dumps(
                            dead_job.get("payload"),
                            indent=2,
                            default=str,
                        ),
                        language="json",
                    )

    st.markdown("---")

    # ========================================================
    # LEASE VISIBILITY
    # ========================================================

    st.markdown("## 🔐 Lease Visibility")

    leased_jobs = [

        j for j in jobs

        if j.get("status") in {
            STATUS_LEASED,
            STATUS_RUNNING,
        }
    ]

    lease_rows = []

    now_ms = int(time.time() * 1000)

    for job in leased_jobs:

        lease_expires = job.get("lease_expires_ms")

        remaining = (
            int(lease_expires) - now_ms
            if lease_expires
            else None
        )

        lease_rows.append({

            "Job ID":
                job.get("job_id"),

            "Worker":
                job.get("worker_id"),

            "Status":
                job.get("status"),

            "Lease Expires":
                _fmt_ts(
                    lease_expires
                ),

            "Remaining(ms)":
                remaining,

            "Attempts":
                job.get("attempts"),
        })

    lease_df = pd.DataFrame(lease_rows)

    st.dataframe(
        lease_df,
        use_container_width=True,
        height=250,
    )

    st.markdown("---")

    # ========================================================
    # WORKER OWNERSHIP
    # ========================================================

    st.markdown("## 👷 Worker Ownership")

    if orchestrator is not None:

        workers = orchestrator.list_workers()

        worker_rows = []

        for worker in workers:

            worker_rows.append({

                "Worker":
                    worker.worker_id,

                "Status":
                    worker.status,

                "Capabilities":
                    ", ".join(
                        worker.capabilities
                    ),

                "Tenant Affinity":
                    ", ".join(
                        worker.tenant_affinity
                    ),

                "Active Jobs":
                    worker.active_jobs,

                "Concurrency":
                    worker.max_concurrent_jobs,

                "Heartbeat":
                    _fmt_ts(
                        worker.last_heartbeat_ms
                    ),

                "Last Error":
                    worker.last_error,
            })

        worker_df = pd.DataFrame(worker_rows)

        st.dataframe(
            worker_df,
            use_container_width=True,
            height=350,
        )

        st.markdown("### 🚨 Worker Controls")

        worker_ids = [
            w.worker_id
            for w in workers
        ]

        selected_worker = st.selectbox(
            "Worker",
            worker_ids if worker_ids else ["None"],
            key="worker_control_select",
        )

        wc1, wc2 = st.columns(2)

        with wc1:

            if st.button(
                "Quarantine Worker",
                key="quarantine_worker_btn",
            ):

                orchestrator.quarantine_worker(
                    selected_worker,
                    reason="manual_console_quarantine",
                )

                st.warning(
                    f"{selected_worker} quarantined."
                )

        with wc2:

            if st.button(
                "Release Quarantine",
                key="release_worker_quarantine_btn",
            ):

                orchestrator.release_worker_quarantine(
                    selected_worker,
                )

                st.success(
                    f"{selected_worker} restored."
                )

    st.markdown("---")

    # ========================================================
    # RETRY ANALYTICS
    # ========================================================

    st.markdown("## 🔁 Retry Analytics")

    retry_jobs = [

        j for j in jobs

        if (
            int(j.get("attempts") or 0) > 1
        )
    ]

    retry_rows = []

    for job in retry_jobs:

        retry_rows.append({

            "Job":
                job.get("job_id"),

            "Type":
                job.get("job_type"),

            "Attempts":
                job.get("attempts"),

            "Max Attempts":
                job.get("max_attempts"),

            "Status":
                job.get("status"),

            "Worker":
                job.get("worker_id"),

            "Error":
                job.get("last_error"),
        })

    retry_df = pd.DataFrame(retry_rows)

    st.dataframe(
        retry_df,
        use_container_width=True,
        height=250,
    )

    st.markdown("---")

    # ========================================================
    # WATCHDOG OPERATIONS
    # ========================================================

    st.markdown("## 🛡️ Lease Watchdog")

    if watchdog is not None:

        if st.button(
            "Run Watchdog Recovery Cycle",
            key="run_watchdog_cycle_btn",
        ):

            results = watchdog.run_cycle()

            st.success("Watchdog cycle completed.")

            st.json(results)

    st.markdown("---")

    # ========================================================
    # EXECUTION STREAM
    # ========================================================

    st.markdown("## 📡 Execution Stream")

    execution_stream = []

    for job in jobs[:50]:

        execution_stream.append({

            "Timestamp":
                _fmt_ts(
                    job.get("updated_at_ms")
                ),

            "Job":
                job.get("job_id"),

            "Status":
                job.get("status"),

            "Worker":
                job.get("worker_id"),

            "Action":
                job.get("action"),

            "Tenant":
                job.get("tenant_id"),
        })

    stream_df = pd.DataFrame(execution_stream)

    st.dataframe(
        stream_df,
        use_container_width=True,
        height=300,
    )

    st.markdown("---")

    # ========================================================
    # SYSTEM ACTIONS
    # ========================================================

    st.markdown("## ⚡ Queue Controls")

    qc1, qc2, qc3 = st.columns(3)

    with qc1:

        if st.button(
            "Recover Expired Leases",
            key="recover_expired_leases_btn",
        ):

            recovered = queue.requeue_expired_leases()

            st.success(
                f"Recovered {recovered} expired leases."
            )

    with qc2:

        if st.button(
            "Refresh Queue",
            key="refresh_queue_btn",
        ):

            st.rerun()

    with qc3:

        auto_refresh = st.checkbox(
            "Auto Refresh",
            value=False,
            key="queue_auto_refresh",
        )

    if auto_refresh:

        time.sleep(5)

        st.rerun()