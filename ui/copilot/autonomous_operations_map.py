"""
ui/copilot/autonomous_operations_map.py

Autonomous Operations Map.

Realtime SOC neural map for:
- distributed workers
- execution jobs
- leases
- rollback chains
- queue pressure
- autonomy/backpressure state
- watchdog recovery
- tenant runtime health
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


def _fmt_ts(ms: Optional[int]) -> str:
    if not ms:
        return "-"
    try:
        return time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(int(ms) / 1000),
        )
    except Exception:
        return str(ms)


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value or {}, indent=2, default=str)
    except Exception:
        return "{}"


def _status_icon(status: str) -> str:
    status = str(status or "").upper()

    if status in {"ONLINE", "IDLE", "COMPLETED", "NORMAL", "ALLOW"}:
        return "🟢"

    if status in {"BUSY", "RUNNING", "LEASED", "ELEVATED", "THROTTLE"}:
        return "🟡"

    if status in {"RETRY", "DEGRADED", "HIGH", "PAUSE"}:
        return "🟠"

    if status in {"FAILED", "DEAD_LETTER", "OFFLINE", "QUARANTINED", "CRITICAL", "FREEZE"}:
        return "🔴"

    return "⚪"


def render_autonomous_operations_map(storage: Any) -> None:
    st.markdown("# 🧠 Autonomous Operations Map")
    st.caption("Realtime SOC neural map for workers, jobs, leases, rollbacks, and autonomy pressure.")

    queue = getattr(storage, "execution_queue", None)
    workers = getattr(storage, "worker_orchestrator", None)
    watchdog = getattr(storage, "lease_watchdog", None)
    router = getattr(storage, "execution_router", None)
    backpressure = getattr(storage, "backpressure_controller", None)

    if queue is None:
        st.error("Execution queue is unavailable.")
        return

    # ========================================================
    # TOP-LEVEL HEALTH
    # ========================================================

    queue_stats = queue.stats() if hasattr(queue, "stats") else {}

    worker_stats = (
        workers.worker_stats()
        if workers is not None and hasattr(workers, "worker_stats")
        else {}
    )

    pressure = None

    if backpressure is not None and hasattr(backpressure, "evaluate"):
        try:
            pressure = backpressure.evaluate(
                tenant_id="default",
                context={
                    "source": "autonomous_operations_map",
                },
            )
        except Exception:
            pressure = None

    st.markdown("## 🛰️ Runtime Command Status")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Queue Total", queue_stats.get("total", 0))
    c2.metric("Running", queue_stats.get("running", 0))
    c3.metric("Retry", queue_stats.get("retry", 0))
    c4.metric("Dead Letter", queue_stats.get("dead_letter", 0))

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Workers", worker_stats.get("total_workers", 0))
    c6.metric("Active Jobs", worker_stats.get("active_jobs", 0))
    c7.metric("Quarantined", worker_stats.get("quarantined", 0))

    if pressure is not None:
        c8.metric(
            "Pressure",
            f"{_status_icon(pressure.pressure_level)} {pressure.pressure_level}",
        )
    else:
        c8.metric("Pressure", "Unknown")

    st.markdown("---")

    # ========================================================
    # AUTONOMY PRESSURE PANEL
    # ========================================================

    st.markdown("## 🧯 Autonomy Pressure / Backpressure")

    if pressure is None:
        st.info("Backpressure controller is unavailable or has not been wired into storage.")
    else:
        p1, p2, p3, p4 = st.columns(4)

        p1.metric("Decision", f"{_status_icon(pressure.decision)} {pressure.decision}")
        p2.metric("Allowed", "Yes" if pressure.allowed else "No")
        p3.metric("Throttle", f"{pressure.throttle_seconds}s")
        p4.metric("Route Budget", pressure.max_routes)

        st.markdown("### Findings")

        findings = getattr(pressure, "findings", []) or []

        if findings:
            st.dataframe(
                pd.DataFrame(findings),
                use_container_width=True,
                height=220,
            )
        else:
            st.success("No active pressure findings.")

        with st.expander("Backpressure Decision Payload"):
            st.json(pressure.to_dict())

    st.markdown("---")

    # ========================================================
    # WORKER MAP
    # ========================================================

    st.markdown("## 👷 Distributed Worker Map")

    worker_rows: List[Dict[str, Any]] = []

    if workers is not None and hasattr(workers, "list_workers"):
        try:
            all_workers = workers.list_workers()
        except Exception:
            all_workers = []

        for w in all_workers:
            worker_rows.append(
                {
                    "Node": f"{_status_icon(w.status)} {w.worker_id}",
                    "Status": w.status,
                    "Active Jobs": w.active_jobs,
                    "Max Jobs": w.max_concurrent_jobs,
                    "Load %": round(
                        (int(w.active_jobs or 0) / max(int(w.max_concurrent_jobs or 1), 1)) * 100,
                        2,
                    ),
                    "Capabilities": ", ".join(w.capabilities or []),
                    "Tenant Affinity": ", ".join(w.tenant_affinity or []),
                    "Heartbeat": _fmt_ts(w.last_heartbeat_ms),
                    "Error": w.last_error,
                }
            )

    if worker_rows:
        st.dataframe(
            pd.DataFrame(worker_rows),
            use_container_width=True,
            height=320,
        )
    else:
        st.info("No workers registered yet.")

    st.markdown("---")

    # ========================================================
    # EXECUTION GRAPH / JOB MAP
    # ========================================================

    st.markdown("## ⚙️ Live Execution Graph")

    jobs = queue.list_jobs(limit=500) if hasattr(queue, "list_jobs") else []

    job_rows: List[Dict[str, Any]] = []

    for job in jobs:
        job_rows.append(
            {
                "Flow": f"{job.get('tenant_id')} → {job.get('worker_id') or 'unassigned'} → {job.get('job_type')}",
                "Job": job.get("job_id"),
                "Type": job.get("job_type"),
                "Action": job.get("action"),
                "Status": f"{_status_icon(job.get('status'))} {job.get('status')}",
                "Tenant": job.get("tenant_id"),
                "Worker": job.get("worker_id"),
                "Priority": job.get("priority"),
                "Attempts": f"{job.get('attempts')}/{job.get('max_attempts')}",
                "Lease Expires": _fmt_ts(job.get("lease_expires_ms")),
                "Updated": _fmt_ts(job.get("updated_at_ms")),
                "Error": job.get("last_error"),
            }
        )

    if job_rows:
        st.dataframe(
            pd.DataFrame(job_rows),
            use_container_width=True,
            height=420,
        )
    else:
        st.info("No jobs currently in the distributed execution queue.")

    st.markdown("---")

    # ========================================================
    # LEASE / STUCK EXECUTION VIEW
    # ========================================================

    st.markdown("## 🔐 Lease & Stuck Execution View")

    now_ms = int(time.time() * 1000)

    lease_rows = []

    for job in jobs:
        status = str(job.get("status") or "").upper()

        if status not in {"LEASED", "RUNNING"}:
            continue

        lease_expires = job.get("lease_expires_ms")

        remaining = (
            int(lease_expires) - now_ms
            if lease_expires
            else None
        )

        lease_rows.append(
            {
                "Job": job.get("job_id"),
                "Status": job.get("status"),
                "Worker": job.get("worker_id"),
                "Tenant": job.get("tenant_id"),
                "Lease Remaining(ms)": remaining,
                "Expired": bool(remaining is not None and remaining < 0),
                "Updated": _fmt_ts(job.get("updated_at_ms")),
            }
        )

    if lease_rows:
        st.dataframe(
            pd.DataFrame(lease_rows),
            use_container_width=True,
            height=260,
        )
    else:
        st.success("No active leased/running jobs.")

    st.markdown("---")

    # ========================================================
    # ROLLBACK / FAILURE MAP
    # ========================================================

    st.markdown("## 🔁 Rollback & Failure Map")

    failure_rows = []

    for job in jobs:
        status = str(job.get("status") or "").upper()

        if status not in {"FAILED", "RETRY", "DEAD_LETTER"}:
            continue

        failure_rows.append(
            {
                "Job": job.get("job_id"),
                "Type": job.get("job_type"),
                "Action": job.get("action"),
                "Status": f"{_status_icon(status)} {status}",
                "Tenant": job.get("tenant_id"),
                "Worker": job.get("worker_id"),
                "Attempts": f"{job.get('attempts')}/{job.get('max_attempts')}",
                "Error": job.get("last_error"),
            }
        )

    if failure_rows:
        st.dataframe(
            pd.DataFrame(failure_rows),
            use_container_width=True,
            height=260,
        )
    else:
        st.success("No failed/retry/dead-letter jobs currently visible.")

    st.markdown("---")

    # ========================================================
    # TENANT RUNTIME VIEW
    # ========================================================

    st.markdown("## 🏢 Tenant Runtime Isolation View")

    tenant_summary: Dict[str, Dict[str, Any]] = {}

    for job in jobs:
        tenant = job.get("tenant_id") or "default"
        status = str(job.get("status") or "UNKNOWN")

        if tenant not in tenant_summary:
            tenant_summary[tenant] = {
                "Tenant": tenant,
                "Total Jobs": 0,
                "Running": 0,
                "Retry": 0,
                "Dead Letter": 0,
                "Workers": set(),
            }

        tenant_summary[tenant]["Total Jobs"] += 1

        if status == "RUNNING":
            tenant_summary[tenant]["Running"] += 1

        if status == "RETRY":
            tenant_summary[tenant]["Retry"] += 1

        if status == "DEAD_LETTER":
            tenant_summary[tenant]["Dead Letter"] += 1

        if job.get("worker_id"):
            tenant_summary[tenant]["Workers"].add(job.get("worker_id"))

    tenant_rows = []

    for data in tenant_summary.values():
        data = dict(data)
        data["Workers"] = ", ".join(sorted(data["Workers"]))
        tenant_rows.append(data)

    if tenant_rows:
        st.dataframe(
            pd.DataFrame(tenant_rows),
            use_container_width=True,
            height=260,
        )
    else:
        st.info("No tenant execution activity yet.")

    st.markdown("---")

    # ========================================================
    # WATCHDOG / ROUTER CONTROLS
    # ========================================================

    st.markdown("## 🛡️ Runtime Controls")

    rc1, rc2, rc3, rc4 = st.columns(4)

    with rc1:
        if watchdog is not None and st.button("Run Watchdog", key="ops_map_run_watchdog"):
            result = watchdog.run_cycle()
            st.success("Watchdog cycle completed.")
            st.json(result)

    with rc2:
        if router is not None and st.button("Route One Job", key="ops_map_route_one"):
            decision = router.route_next()
            st.json(decision.to_dict())

    with rc3:
        if queue is not None and st.button("Recover Expired Leases", key="ops_map_recover_leases"):
            recovered = queue.requeue_expired_leases()
            st.success(f"Recovered {recovered} expired leases.")

    with rc4:
        if st.button("Refresh Map", key="ops_map_refresh"):
            st.rerun()

    st.markdown("---")

    # ========================================================
    # JOB INSPECTOR
    # ========================================================

    st.markdown("## 🔬 Job Inspector")

    job_ids = [j.get("job_id") for j in jobs if j.get("job_id")]

    selected_job = st.selectbox(
        "Select Job",
        job_ids if job_ids else ["None"],
        key="ops_map_selected_job",
    )

    if selected_job != "None":
        job = next((j for j in jobs if j.get("job_id") == selected_job), None)

        if job:
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### Job Metadata")
                st.json(job)

            with c2:
                st.markdown("### Payload")
                st.code(
                    _safe_json(job.get("payload")),
                    language="json",
                )

    st.markdown("---")

    # ========================================================
    # EVENT STREAM APPROXIMATION
    # ========================================================

    st.markdown("## 📡 Live Runtime Stream")

    stream_rows = []

    for job in sorted(
        jobs,
        key=lambda j: int(j.get("updated_at_ms") or 0),
        reverse=True,
    )[:75]:
        stream_rows.append(
            {
                "Time": _fmt_ts(job.get("updated_at_ms")),
                "Event": f"{job.get('status')} {job.get('job_type')}",
                "Job": job.get("job_id"),
                "Worker": job.get("worker_id"),
                "Tenant": job.get("tenant_id"),
                "Action": job.get("action"),
                "Error": job.get("last_error"),
            }
        )

    if stream_rows:
        st.dataframe(
            pd.DataFrame(stream_rows),
            use_container_width=True,
            height=320,
        )
    else:
        st.info("No runtime stream events available.")

    auto_refresh = st.checkbox(
        "Auto refresh every 5 seconds",
        value=False,
        key="ops_map_auto_refresh",
    )

    if auto_refresh:
        time.sleep(5)
        st.rerun()