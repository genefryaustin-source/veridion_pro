"""
ui/copilot/execution_control_plane_console.py

Execution Control Plane Console for Veridion Pro / CUI GovCloud App.

Purpose:
- Live execution visibility
- Worker health visibility
- Governance state visibility
- Rollback monitoring
- Execution graph review
- Event timeline / operational stream

Safe defaults:
- Read-only by default
- Defensive DB/table/method handling
- No destructive action is performed unless action handlers are later wired in
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


# =============================================================================
# Constants
# =============================================================================

PAGE_TITLE = "Execution Control Plane"
PAGE_ICON = "🛰️"

STATUS_RUNNING = {"RUNNING", "IN_PROGRESS", "ACTIVE", "EXECUTING"}
STATUS_FAILED = {"FAILED", "ERROR", "DEGRADED"}
STATUS_WAITING = {"WAITING_APPROVAL", "APPROVAL_REQUIRED", "BLOCKED"}
STATUS_ROLLBACK = {"ROLLING_BACK", "ROLLBACK_PENDING", "ROLLBACK_FAILED"}
STATUS_COMPLETE = {"COMPLETED", "SUCCESS", "DONE"}

HEALTHY_HEARTBEAT_MS = 60_000
STALE_HEARTBEAT_MS = 180_000
DEAD_HEARTBEAT_MS = 300_000


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ConsoleData:
    executions: pd.DataFrame
    workers: pd.DataFrame
    rollbacks: pd.DataFrame
    governance: pd.DataFrame
    graphs: pd.DataFrame
    events: pd.DataFrame
    leases: pd.DataFrame


# =============================================================================
# Utility Helpers
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_json_loads(value: Any, default: Any = None) -> Any:
    if default is None:
        default = {}

    if value is None:
        return default

    if isinstance(value, (dict, list)):
        return value

    if not isinstance(value, str):
        return default

    try:
        return json.loads(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _normalize_status(value: Any) -> str:
    status = _safe_str(value, "UNKNOWN").upper().strip()
    return status if status else "UNKNOWN"


def _status_badge(status: Any) -> str:
    status = _normalize_status(status)

    if status in STATUS_RUNNING:
        color = "#2563eb"
        label = status
    elif status in STATUS_COMPLETE:
        color = "#16a34a"
        label = status
    elif status in STATUS_FAILED:
        color = "#dc2626"
        label = status
    elif status in STATUS_WAITING:
        color = "#ca8a04"
        label = status
    elif status in STATUS_ROLLBACK:
        color = "#9333ea"
        label = status
    else:
        color = "#64748b"
        label = status

    return (
        f"<span style='background:{color}; color:white; padding:4px 9px; "
        f"border-radius:999px; font-size:12px; font-weight:700;'>{label}</span>"
    )


def _severity_badge(severity: Any) -> str:
    severity = _safe_str(severity, "UNKNOWN").upper().strip()

    color_map = {
        "CRITICAL": "#991b1b",
        "HIGH": "#dc2626",
        "MEDIUM": "#f59e0b",
        "LOW": "#2563eb",
        "INFO": "#64748b",
        "UNKNOWN": "#64748b",
    }

    color = color_map.get(severity, "#64748b")

    return (
        f"<span style='background:{color}; color:white; padding:4px 9px; "
        f"border-radius:999px; font-size:12px; font-weight:700;'>{severity}</span>"
    )


def _risk_badge(value: Any) -> str:
    score = _safe_int(value, 0)

    if score >= 85:
        color = "#991b1b"
        label = "CRITICAL"
    elif score >= 65:
        color = "#dc2626"
        label = "HIGH"
    elif score >= 35:
        color = "#f59e0b"
        label = "MEDIUM"
    else:
        color = "#16a34a"
        label = "LOW"

    return (
        f"<span style='background:{color}; color:white; padding:4px 9px; "
        f"border-radius:999px; font-size:12px; font-weight:700;'>{label} {score}</span>"
    )


def _heartbeat_state(last_seen_ms: Any) -> Tuple[str, int]:
    last_seen = _safe_int(last_seen_ms, 0)
    age = max(0, _now_ms() - last_seen) if last_seen else 999_999_999

    if age <= HEALTHY_HEARTBEAT_MS:
        return "HEALTHY", age
    if age <= STALE_HEARTBEAT_MS:
        return "STALE", age
    if age <= DEAD_HEARTBEAT_MS:
        return "DEGRADED", age
    return "DEAD", age


def _format_age(ms: Any) -> str:
    value = _safe_int(ms, 0)

    if value <= 0:
        return "unknown"

    seconds = value // 1000

    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


def _format_timestamp_ms(ms: Any) -> str:
    value = _safe_int(ms, 0)

    if value <= 0:
        return ""

    try:
        return pd.to_datetime(value, unit="ms").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


def _get_ledger(storage: Any) -> Any:
    if storage is None:
        return None
    return getattr(storage, "ledger", storage)


def _get_connection(storage: Any) -> Optional[sqlite3.Connection]:
    ledger = _get_ledger(storage)

    if ledger is None:
        return None

    for attr in ("conn", "_conn", "connection", "_connection", "db"):
        conn = getattr(ledger, attr, None)
        if isinstance(conn, sqlite3.Connection):
            return conn

    db_path = None

    for attr in ("db_path", "database_path", "path", "_db_path"):
        value = getattr(ledger, attr, None)
        if value:
            db_path = value
            break

    if not db_path:
        db_path = getattr(storage, "db_path", None)

    if db_path:
        try:
            return sqlite3.connect(db_path, check_same_thread=False)
        except Exception:
            return None

    return None


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    try:
        row = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?
            LIMIT 1
            """,
            (table_name,),
        ).fetchone()
        return row is not None
    except Exception:
        return False


def _read_table(
    conn: Optional[sqlite3.Connection],
    table_name: str,
    columns: Optional[List[str]] = None,
    order_by: Optional[str] = None,
    limit: int = 500,
) -> pd.DataFrame:
    if conn is None:
        return pd.DataFrame()

    try:
        if not _table_exists(conn, table_name):
            return pd.DataFrame()

        col_expr = "*"
        if columns:
            col_expr = ", ".join(columns)

        sql = f"SELECT {col_expr} FROM {table_name}"

        if order_by:
            sql += f" ORDER BY {order_by}"

        if limit:
            sql += f" LIMIT {int(limit)}"

        return pd.read_sql_query(sql, conn)
    except Exception:
        return pd.DataFrame()


def _call_ledger_method(storage: Any, method_name: str, default: Any = None, *args, **kwargs) -> Any:
    ledger = _get_ledger(storage)

    if ledger is None:
        return default

    method = getattr(ledger, method_name, None)

    if not callable(method):
        return default

    try:
        return method(*args, **kwargs)
    except Exception:
        return default


def _to_dataframe(value: Any) -> pd.DataFrame:
    if value is None:
        return pd.DataFrame()

    if isinstance(value, pd.DataFrame):
        return value

    if isinstance(value, list):
        try:
            return pd.DataFrame(value)
        except Exception:
            return pd.DataFrame()

    if isinstance(value, dict):
        try:
            if "rows" in value and isinstance(value["rows"], list):
                return pd.DataFrame(value["rows"])
            return pd.DataFrame([value])
        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()


def _ensure_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    if df is None or df.empty:
        df = pd.DataFrame()

    for col in columns:
        if col not in df.columns:
            df[col] = None

    return df


# =============================================================================
# Data Loading
# =============================================================================

def _load_executions(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_execution_control_plane_jobs", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "pipeline_jobs",
            "execution_jobs",
            "executions",
            "execution_control_plane_jobs",
        ):
            df = _read_table(
                conn,
                table,
                order_by="updated_at_ms DESC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "job_id",
            "execution_id",
            "tenant_id",
            "stage",
            "status",
            "worker_id",
            "case_id",
            "evidence_id",
            "alert_id",
            "attempts",
            "max_attempts",
            "created_at_ms",
            "updated_at_ms",
            "lease_expires_ms",
            "last_error",
            "payload_json",
        ],
    )

    if "job_id" not in df.columns or df["job_id"].isna().all():
        df["job_id"] = df.get("execution_id")

    df["status_norm"] = df["status"].apply(_normalize_status)
    df["updated_at"] = df["updated_at_ms"].apply(_format_timestamp_ms)
    df["created_at"] = df["created_at_ms"].apply(_format_timestamp_ms)

    return df


def _load_workers(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_workers", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "worker_registry",
            "workers",
            "worker_heartbeats",
            "runtime_workers",
        ):
            df = _read_table(
                conn,
                table,
                order_by="last_heartbeat_ms DESC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "worker_id",
            "tenant_id",
            "hostname",
            "status",
            "capabilities_json",
            "active_jobs",
            "last_heartbeat_ms",
            "quarantined",
            "created_at_ms",
            "updated_at_ms",
        ],
    )

    if "last_heartbeat_ms" not in df.columns:
        df["last_heartbeat_ms"] = df.get("updated_at_ms")

    health_values = df["last_heartbeat_ms"].apply(_heartbeat_state)
    df["health"] = health_values.apply(lambda x: x[0])
    df["heartbeat_age_ms"] = health_values.apply(lambda x: x[1])
    df["heartbeat_age"] = df["heartbeat_age_ms"].apply(_format_age)
    df["last_seen"] = df["last_heartbeat_ms"].apply(_format_timestamp_ms)

    return df


def _load_rollbacks(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_rollback_chains", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "rollback_chains",
            "rollback_jobs",
            "execution_rollbacks",
        ):
            df = _read_table(
                conn,
                table,
                order_by="updated_at_ms DESC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "rollback_id",
            "chain_id",
            "job_id",
            "execution_id",
            "tenant_id",
            "status",
            "reason",
            "verification_status",
            "created_at_ms",
            "updated_at_ms",
            "last_error",
            "payload_json",
        ],
    )

    if "rollback_id" not in df.columns or df["rollback_id"].isna().all():
        df["rollback_id"] = df.get("chain_id")

    df["status_norm"] = df["status"].apply(_normalize_status)
    df["updated_at"] = df["updated_at_ms"].apply(_format_timestamp_ms)

    return df


def _load_governance(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_governance_decisions", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "governance_decisions",
            "approval_requests",
            "autonomy_decisions",
            "policy_violations",
        ):
            df = _read_table(
                conn,
                table,
                order_by="created_at_ms DESC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "decision_id",
            "request_id",
            "job_id",
            "execution_id",
            "tenant_id",
            "action",
            "status",
            "severity",
            "risk_score",
            "autonomy_mode",
            "policy_id",
            "reason",
            "created_at_ms",
            "updated_at_ms",
            "payload_json",
        ],
    )

    if "decision_id" not in df.columns or df["decision_id"].isna().all():
        df["decision_id"] = df.get("request_id")

    df["status_norm"] = df["status"].apply(_normalize_status)
    df["created_at"] = df["created_at_ms"].apply(_format_timestamp_ms)

    return df


def _load_graphs(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_execution_graphs", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "execution_graphs",
            "graph_executions",
            "execution_graph_nodes",
        ):
            df = _read_table(
                conn,
                table,
                order_by="updated_at_ms DESC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "graph_id",
            "job_id",
            "execution_id",
            "tenant_id",
            "status",
            "current_node",
            "node_count",
            "completed_nodes",
            "failed_nodes",
            "created_at_ms",
            "updated_at_ms",
            "graph_json",
            "last_error",
        ],
    )

    df["status_norm"] = df["status"].apply(_normalize_status)
    df["updated_at"] = df["updated_at_ms"].apply(_format_timestamp_ms)

    return df


def _load_events(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_execution_events", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "execution_events",
            "pipeline_events",
            "runtime_events",
            "event_log",
            "custody_events",
        ):
            df = _read_table(
                conn,
                table,
                order_by="created_at_ms DESC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "event_id",
            "job_id",
            "execution_id",
            "tenant_id",
            "event_type",
            "stage",
            "status",
            "severity",
            "message",
            "created_at_ms",
            "actor",
            "details_json",
        ],
    )

    df["status_norm"] = df["status"].apply(_normalize_status)
    df["created_at"] = df["created_at_ms"].apply(_format_timestamp_ms)

    return df


def _load_leases(storage: Any, conn: Optional[sqlite3.Connection]) -> pd.DataFrame:
    method_data = _call_ledger_method(storage, "list_worker_leases", None)
    df = _to_dataframe(method_data)

    if df.empty:
        for table in (
            "worker_leases",
            "execution_leases",
            "runtime_leases",
        ):
            df = _read_table(
                conn,
                table,
                order_by="lease_expires_ms ASC",
                limit=1000,
            )
            if not df.empty:
                break

    df = _ensure_columns(
        df,
        [
            "lease_id",
            "job_id",
            "execution_id",
            "worker_id",
            "tenant_id",
            "status",
            "lease_started_ms",
            "lease_expires_ms",
            "renewed_at_ms",
            "created_at_ms",
            "updated_at_ms",
        ],
    )

    now = _now_ms()
    df["lease_remaining_ms"] = df["lease_expires_ms"].apply(lambda x: _safe_int(x, 0) - now)
    df["lease_state"] = df["lease_remaining_ms"].apply(
        lambda x: "EXPIRED" if _safe_int(x, 0) <= 0 else "ACTIVE"
    )
    df["lease_remaining"] = df["lease_remaining_ms"].apply(
        lambda x: "expired" if _safe_int(x, 0) <= 0 else _format_age(x)
    )

    return df


@st.cache_data(ttl=5, show_spinner=False)
def _load_console_data_cached(cache_key: str) -> ConsoleData:
    return ConsoleData(
        executions=pd.DataFrame(),
        workers=pd.DataFrame(),
        rollbacks=pd.DataFrame(),
        governance=pd.DataFrame(),
        graphs=pd.DataFrame(),
        events=pd.DataFrame(),
        leases=pd.DataFrame(),
    )


def load_console_data(storage: Any) -> ConsoleData:
    conn = _get_connection(storage)

    return ConsoleData(
        executions=_load_executions(storage, conn),
        workers=_load_workers(storage, conn),
        rollbacks=_load_rollbacks(storage, conn),
        governance=_load_governance(storage, conn),
        graphs=_load_graphs(storage, conn),
        events=_load_events(storage, conn),
        leases=_load_leases(storage, conn),
    )


# =============================================================================
# Filtering
# =============================================================================

def _render_filters(data: ConsoleData) -> Dict[str, Any]:
    st.markdown("### Filters")

    tenant_values: List[str] = []

    for df in (
        data.executions,
        data.workers,
        data.rollbacks,
        data.governance,
        data.graphs,
        data.events,
        data.leases,
    ):
        if df is not None and not df.empty and "tenant_id" in df.columns:
            tenant_values.extend(
                [
                    _safe_str(v)
                    for v in df["tenant_id"].dropna().unique().tolist()
                    if _safe_str(v)
                ]
            )

    tenants = sorted(set(tenant_values))

    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 2])

    with c1:
        tenant = st.selectbox(
            "Tenant",
            ["All"] + tenants,
            key="ecpc_filter_tenant",
        )

    with c2:
        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "RUNNING",
                "FAILED",
                "WAITING_APPROVAL",
                "ROLLING_BACK",
                "COMPLETED",
                "BLOCKED",
                "UNKNOWN",
            ],
            key="ecpc_filter_status",
        )

    with c3:
        severity = st.selectbox(
            "Severity",
            ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "UNKNOWN"],
            key="ecpc_filter_severity",
        )

    with c4:
        search = st.text_input(
            "Search job, worker, case, evidence, message",
            key="ecpc_filter_search",
            placeholder="job_id, worker_id, case_id, evidence_id, message...",
        )

    return {
        "tenant": tenant,
        "status": status_filter,
        "severity": severity,
        "search": search.strip(),
    }


def _apply_common_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    tenant = filters.get("tenant")
    status = filters.get("status")
    severity = filters.get("severity")
    search = filters.get("search")

    if tenant and tenant != "All" and "tenant_id" in result.columns:
        result = result[result["tenant_id"].astype(str) == tenant]

    if status and status != "All":
        status_cols = [c for c in ("status_norm", "status", "lease_state", "health") if c in result.columns]
        if status_cols:
            mask = False
            for col in status_cols:
                mask = mask | (result[col].astype(str).str.upper() == status.upper())
            result = result[mask]

    if severity and severity != "All" and "severity" in result.columns:
        result = result[result["severity"].astype(str).str.upper() == severity.upper()]

    if search:
        search_lower = search.lower()
        searchable_cols = [
            c
            for c in result.columns
            if c
            in {
                "job_id",
                "execution_id",
                "worker_id",
                "case_id",
                "evidence_id",
                "alert_id",
                "message",
                "reason",
                "last_error",
                "event_type",
                "stage",
                "action",
            }
        ]

        if searchable_cols:
            mask = False
            for col in searchable_cols:
                mask = mask | result[col].astype(str).str.lower().str.contains(search_lower, na=False)
            result = result[mask]

    return result


# =============================================================================
# UI Components
# =============================================================================

def _render_header() -> None:
    st.markdown(
        """
        <div style="
            padding: 18px 22px;
            border-radius: 18px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #334155 100%);
            color: white;
            margin-bottom: 18px;
            box-shadow: 0 12px 30px rgba(15,23,42,0.25);
        ">
            <div style="font-size: 13px; opacity: 0.8; letter-spacing: 0.12em; font-weight: 800;">
                VERIDION PRO GOVCLOUD
            </div>
            <div style="font-size: 32px; font-weight: 900; margin-top: 4px;">
                🛰️ Execution Control Plane Console
            </div>
            <div style="font-size: 15px; opacity: 0.9; margin-top: 8px;">
                Live oversight for autonomous execution, worker health, governance gates, rollback chains, and forensic event telemetry.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_summary_cards(data: ConsoleData) -> None:
    executions = data.executions
    workers = data.workers
    rollbacks = data.rollbacks
    governance = data.governance
    leases = data.leases

    active_count = 0
    failed_count = 0
    approval_count = 0
    rollback_count = 0
    worker_count = 0
    dead_worker_count = 0
    expired_lease_count = 0

    if executions is not None and not executions.empty:
        active_count = executions["status_norm"].isin(STATUS_RUNNING).sum()
        failed_count = executions["status_norm"].isin(STATUS_FAILED).sum()
        approval_count = executions["status_norm"].isin(STATUS_WAITING).sum()

    if governance is not None and not governance.empty and "status_norm" in governance.columns:
        approval_count += governance["status_norm"].isin(STATUS_WAITING).sum()

    if rollbacks is not None and not rollbacks.empty and "status_norm" in rollbacks.columns:
        rollback_count = rollbacks["status_norm"].isin(STATUS_ROLLBACK | STATUS_RUNNING | STATUS_FAILED).sum()

    if workers is not None and not workers.empty:
        worker_count = len(workers)
        dead_worker_count = workers["health"].isin(["DEAD", "DEGRADED"]).sum()

    if leases is not None and not leases.empty and "lease_state" in leases.columns:
        expired_lease_count = (leases["lease_state"] == "EXPIRED").sum()

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    c1.metric("Active Executions", active_count)
    c2.metric("Failed", failed_count)
    c3.metric("Approval Required", approval_count)
    c4.metric("Rollback Activity", rollback_count)
    c5.metric("Workers", worker_count)
    c6.metric("Dead/Degraded", dead_worker_count)
    c7.metric("Expired Leases", expired_lease_count)


def _render_autonomy_banner(data: ConsoleData) -> None:
    governance = data.governance

    mode = "UNKNOWN"
    highest_risk = 0
    blocked = 0

    if governance is not None and not governance.empty:
        if "autonomy_mode" in governance.columns:
            modes = governance["autonomy_mode"].dropna().astype(str).tolist()
            if modes:
                mode = modes[0].upper()

        if "risk_score" in governance.columns:
            highest_risk = int(pd.to_numeric(governance["risk_score"], errors="coerce").fillna(0).max())

        if "status_norm" in governance.columns:
            blocked = governance["status_norm"].isin(["BLOCKED", "DENIED", "REJECTED"]).sum()

    if highest_risk >= 85 or blocked > 0:
        border = "#dc2626"
        bg = "#fef2f2"
        label = "Restricted / High Governance Attention"
    elif highest_risk >= 65:
        border = "#f59e0b"
        bg = "#fffbeb"
        label = "Elevated Governance Monitoring"
    else:
        border = "#16a34a"
        bg = "#f0fdf4"
        label = "Normal Governance Monitoring"

    st.markdown(
        f"""
        <div style="
            border: 1px solid {border};
            background: {bg};
            border-radius: 16px;
            padding: 14px 18px;
            margin: 12px 0 18px 0;
        ">
            <div style="font-size: 14px; font-weight: 900; color: {border};">
                Autonomy Status: {label}
            </div>
            <div style="font-size: 13px; margin-top: 4px; color: #334155;">
                Current Mode: <b>{mode}</b> · Highest Risk Score: <b>{highest_risk}</b> · Blocked Decisions: <b>{blocked}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_table(df: pd.DataFrame, title: str, key: str, height: int = 360) -> None:
    st.markdown(f"### {title}")

    if df is None or df.empty:
        st.info(f"No {title.lower()} found yet.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        key=f"ecpc_table_{key}",
    )


def _render_execution_actions(row: pd.Series, idx: int) -> None:
    job_id = _safe_str(row.get("job_id") or row.get("execution_id") or f"row_{idx}")

    st.markdown("#### Safe Controls")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("Pause", key=f"ecpc_pause_{job_id}_{idx}", disabled=True):
            pass

    with c2:
        if st.button("Resume", key=f"ecpc_resume_{job_id}_{idx}", disabled=True):
            pass

    with c3:
        if st.button("Rollback", key=f"ecpc_rollback_{job_id}_{idx}", disabled=True):
            pass

    with c4:
        if st.button("Escalate", key=f"ecpc_escalate_{job_id}_{idx}", disabled=True):
            pass

    with c5:
        if st.button("Replay", key=f"ecpc_replay_{job_id}_{idx}", disabled=True):
            pass

    st.caption(
        "Action buttons are intentionally disabled until "
        "`ui/copilot/governance_action_handlers.py` is wired in."
    )


def _render_execution_detail_panel(df: pd.DataFrame) -> None:
    if df is None or df.empty:
        return

    st.markdown("### Execution Detail")

    options = []

    for idx, row in df.iterrows():
        job_id = _safe_str(row.get("job_id") or row.get("execution_id") or idx)
        status = _safe_str(row.get("status") or row.get("status_norm"))
        stage = _safe_str(row.get("stage"))
        options.append((idx, f"{job_id} · {stage} · {status}"))

    selected = st.selectbox(
        "Select execution",
        options,
        format_func=lambda x: x[1],
        key="ecpc_execution_detail_select",
    )

    selected_idx = selected[0]
    row = df.loc[selected_idx]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_status_badge(row.get("status")), unsafe_allow_html=True)
    c2.metric("Attempts", _safe_int(row.get("attempts"), 0))
    c3.metric("Max Attempts", _safe_int(row.get("max_attempts"), 0))
    c4.metric("Lease Expires", _format_timestamp_ms(row.get("lease_expires_ms")))

    _render_execution_actions(row, selected_idx)

    with st.expander("Execution Payload / Error Details", expanded=False):
        payload = _safe_json_loads(row.get("payload_json"), {})
        last_error = row.get("last_error")

        if last_error:
            st.error(_safe_str(last_error))

        st.json(payload)


def _render_overview_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    executions = _apply_common_filters(data.executions, filters)
    workers = _apply_common_filters(data.workers, filters)
    governance = _apply_common_filters(data.governance, filters)
    rollbacks = _apply_common_filters(data.rollbacks, filters)
    events = _apply_common_filters(data.events, filters)

    _render_summary_cards(
        ConsoleData(
            executions=executions,
            workers=workers,
            governance=governance,
            rollbacks=rollbacks,
            graphs=data.graphs,
            events=events,
            leases=data.leases,
        )
    )

    _render_autonomy_banner(data)

    c1, c2 = st.columns([1.4, 1])

    with c1:
        if executions.empty:
            st.info("No active execution records found.")
        else:
            show_cols = [
                c
                for c in [
                    "job_id",
                    "tenant_id",
                    "stage",
                    "status",
                    "worker_id",
                    "case_id",
                    "attempts",
                    "updated_at",
                    "last_error",
                ]
                if c in executions.columns
            ]
            _render_table(executions[show_cols].head(25), "Recent Executions", "overview_executions", 320)

    with c2:
        if workers.empty:
            st.info("No worker records found.")
        else:
            show_cols = [
                c
                for c in [
                    "worker_id",
                    "tenant_id",
                    "health",
                    "status",
                    "heartbeat_age",
                    "active_jobs",
                ]
                if c in workers.columns
            ]
            _render_table(workers[show_cols].head(25), "Worker Health", "overview_workers", 320)

    st.markdown("### Latest Operational Events")

    if events.empty:
        st.info("No operational events found.")
    else:
        show_cols = [
            c
            for c in [
                "created_at",
                "event_type",
                "stage",
                "status",
                "severity",
                "job_id",
                "message",
            ]
            if c in events.columns
        ]
        st.dataframe(events[show_cols].head(50), use_container_width=True, height=320)


def _render_executions_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    executions = _apply_common_filters(data.executions, filters)

    if executions.empty:
        st.info("No executions found.")
        return

    show_cols = [
        c
        for c in [
            "job_id",
            "execution_id",
            "tenant_id",
            "stage",
            "status",
            "worker_id",
            "case_id",
            "evidence_id",
            "alert_id",
            "attempts",
            "max_attempts",
            "created_at",
            "updated_at",
            "last_error",
        ]
        if c in executions.columns
    ]

    _render_table(executions[show_cols], "Executions", "executions", 420)
    _render_execution_detail_panel(executions)


def _render_workers_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    workers = _apply_common_filters(data.workers, filters)

    if workers.empty:
        st.info("No workers found.")
        return

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Workers", len(workers))
    c2.metric("Healthy", (workers["health"] == "HEALTHY").sum())
    c3.metric("Stale/Degraded", workers["health"].isin(["STALE", "DEGRADED"]).sum())
    c4.metric("Dead", (workers["health"] == "DEAD").sum())

    show_cols = [
        c
        for c in [
            "worker_id",
            "tenant_id",
            "hostname",
            "health",
            "status",
            "heartbeat_age",
            "last_seen",
            "active_jobs",
            "quarantined",
            "capabilities_json",
        ]
        if c in workers.columns
    ]

    _render_table(workers[show_cols], "Distributed Worker Cluster", "workers", 440)

    with st.expander("Worker Capability Detail", expanded=False):
        for idx, row in workers.iterrows():
            worker_id = _safe_str(row.get("worker_id") or f"worker_{idx}")
            capabilities = _safe_json_loads(row.get("capabilities_json"), [])

            st.markdown(f"#### {worker_id}")
            st.write(
                {
                    "tenant_id": row.get("tenant_id"),
                    "health": row.get("health"),
                    "status": row.get("status"),
                    "heartbeat_age": row.get("heartbeat_age"),
                    "capabilities": capabilities,
                }
            )


def _render_governance_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    governance = _apply_common_filters(data.governance, filters)

    if governance.empty:
        st.info("No governance decisions or approval records found.")
        return

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Governance Items", len(governance))

    if "status_norm" in governance.columns:
        c2.metric("Waiting Approval", governance["status_norm"].isin(STATUS_WAITING).sum())
        c3.metric("Blocked/Rejected", governance["status_norm"].isin(["BLOCKED", "DENIED", "REJECTED"]).sum())
    else:
        c2.metric("Waiting Approval", 0)
        c3.metric("Blocked/Rejected", 0)

    if "risk_score" in governance.columns:
        c4.metric("Highest Risk", int(pd.to_numeric(governance["risk_score"], errors="coerce").fillna(0).max()))
    else:
        c4.metric("Highest Risk", 0)

    render_df = governance.copy()

    if "status" in render_df.columns:
        render_df["status_badge"] = render_df["status"].apply(_status_badge)

    if "severity" in render_df.columns:
        render_df["severity_badge"] = render_df["severity"].apply(_severity_badge)

    if "risk_score" in render_df.columns:
        render_df["risk_badge"] = render_df["risk_score"].apply(_risk_badge)

    show_cols = [
        c
        for c in [
            "decision_id",
            "request_id",
            "job_id",
            "tenant_id",
            "action",
            "status",
            "severity",
            "risk_score",
            "autonomy_mode",
            "policy_id",
            "reason",
            "created_at",
        ]
        if c in render_df.columns
    ]

    _render_table(render_df[show_cols], "Governance Queue", "governance", 440)

    with st.expander("Governance Decision Payloads", expanded=False):
        for idx, row in governance.head(20).iterrows():
            decision_id = _safe_str(row.get("decision_id") or row.get("request_id") or idx)
            st.markdown(f"#### Decision {decision_id}")
            st.json(_safe_json_loads(row.get("payload_json"), {}))


def _render_rollback_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    rollbacks = _apply_common_filters(data.rollbacks, filters)

    if rollbacks.empty:
        st.info("No rollback chains found.")
        return

    c1, c2, c3 = st.columns(3)

    c1.metric("Rollback Chains", len(rollbacks))

    if "status_norm" in rollbacks.columns:
        c2.metric("Active Rollbacks", rollbacks["status_norm"].isin(STATUS_ROLLBACK | STATUS_RUNNING).sum())
        c3.metric("Failed Rollbacks", rollbacks["status_norm"].isin(STATUS_FAILED).sum())
    else:
        c2.metric("Active Rollbacks", 0)
        c3.metric("Failed Rollbacks", 0)

    show_cols = [
        c
        for c in [
            "rollback_id",
            "chain_id",
            "job_id",
            "execution_id",
            "tenant_id",
            "status",
            "reason",
            "verification_status",
            "updated_at",
            "last_error",
        ]
        if c in rollbacks.columns
    ]

    _render_table(rollbacks[show_cols], "Rollback Operations", "rollbacks", 440)

    with st.expander("Rollback Payloads", expanded=False):
        for idx, row in rollbacks.head(20).iterrows():
            rollback_id = _safe_str(row.get("rollback_id") or row.get("chain_id") or idx)
            st.markdown(f"#### Rollback {rollback_id}")
            st.json(_safe_json_loads(row.get("payload_json"), {}))


def _render_graphs_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    graphs = _apply_common_filters(data.graphs, filters)

    if graphs.empty:
        st.info("No execution graphs found.")
        return

    show_cols = [
        c
        for c in [
            "graph_id",
            "job_id",
            "execution_id",
            "tenant_id",
            "status",
            "current_node",
            "node_count",
            "completed_nodes",
            "failed_nodes",
            "updated_at",
            "last_error",
        ]
        if c in graphs.columns
    ]

    _render_table(graphs[show_cols], "Execution Graphs", "graphs", 360)

    st.markdown("### Graph Detail")

    graph_options = []

    for idx, row in graphs.iterrows():
        graph_id = _safe_str(row.get("graph_id") or row.get("job_id") or idx)
        status = _safe_str(row.get("status"))
        graph_options.append((idx, f"{graph_id} · {status}"))

    selected = st.selectbox(
        "Select graph",
        graph_options,
        format_func=lambda x: x[1],
        key="ecpc_graph_select",
    )

    row = graphs.loc[selected[0]]
    graph_json = _safe_json_loads(row.get("graph_json"), {})

    c1, c2, c3 = st.columns(3)
    c1.metric("Nodes", _safe_int(row.get("node_count"), 0))
    c2.metric("Completed", _safe_int(row.get("completed_nodes"), 0))
    c3.metric("Failed", _safe_int(row.get("failed_nodes"), 0))

    st.json(graph_json)


def _render_event_stream_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    events = _apply_common_filters(data.events, filters)

    if events.empty:
        st.info("No event stream records found.")
        return

    show_cols = [
        c
        for c in [
            "created_at",
            "event_type",
            "stage",
            "status",
            "severity",
            "tenant_id",
            "job_id",
            "execution_id",
            "actor",
            "message",
        ]
        if c in events.columns
    ]

    _render_table(events[show_cols], "Operational Event Stream", "events", 520)

    with st.expander("Raw Event Details", expanded=False):
        for idx, row in events.head(40).iterrows():
            event_id = _safe_str(row.get("event_id") or idx)
            event_type = _safe_str(row.get("event_type") or "EVENT")
            created_at = _safe_str(row.get("created_at"))
            message = _safe_str(row.get("message"))

            st.markdown(f"#### {event_type} · {created_at}")
            if message:
                st.write(message)

            st.json(_safe_json_loads(row.get("details_json"), {}))


def _render_leases_tab(data: ConsoleData, filters: Dict[str, Any]) -> None:
    leases = _apply_common_filters(data.leases, filters)

    if leases.empty:
        st.info("No worker leases found.")
        return

    c1, c2, c3 = st.columns(3)

    c1.metric("Leases", len(leases))
    c2.metric("Active", (leases["lease_state"] == "ACTIVE").sum())
    c3.metric("Expired", (leases["lease_state"] == "EXPIRED").sum())

    show_cols = [
        c
        for c in [
            "lease_id",
            "job_id",
            "execution_id",
            "worker_id",
            "tenant_id",
            "status",
            "lease_state",
            "lease_remaining",
            "lease_started_ms",
            "lease_expires_ms",
            "renewed_at_ms",
        ]
        if c in leases.columns
    ]

    render_df = leases[show_cols].copy()

    for col in ("lease_started_ms", "lease_expires_ms", "renewed_at_ms"):
        if col in render_df.columns:
            render_df[col.replace("_ms", "")] = render_df[col].apply(_format_timestamp_ms)
            render_df = render_df.drop(columns=[col])

    _render_table(render_df, "Lease Monitor", "leases", 460)


# =============================================================================
# Public Render Function
# =============================================================================

def render_execution_control_plane_console(storage: Any) -> None:
    """
    Main render entrypoint.

    Usage inside Command Center:

        from ui.copilot.execution_control_plane_console import (
            render_execution_control_plane_console,
        )

        render_execution_control_plane_console(storage)
    """

    _render_header()

    refresh_col, safe_col = st.columns([1, 4])

    with refresh_col:
        if st.button("Refresh", key="ecpc_refresh_button"):
            st.cache_data.clear()
            st.rerun()

    with safe_col:
        st.caption(
            "Read-only mode enabled. Operational actions require governance handlers before activation."
        )

    try:
        data = load_console_data(storage)
    except Exception as exc:
        st.error(f"Unable to load execution control plane data: {exc}")
        data = ConsoleData(
            executions=pd.DataFrame(),
            workers=pd.DataFrame(),
            rollbacks=pd.DataFrame(),
            governance=pd.DataFrame(),
            graphs=pd.DataFrame(),
            events=pd.DataFrame(),
            leases=pd.DataFrame(),
        )

    filters = _render_filters(data)

    tab_overview, tab_executions, tab_workers, tab_governance, tab_rollback, tab_graphs, tab_leases, tab_events = st.tabs(
        [
            "Overview",
            "Executions",
            "Workers",
            "Governance",
            "Rollback",
            "Graph View",
            "Leases",
            "Event Stream",
        ]
    )

    with tab_overview:
        _render_overview_tab(data, filters)

    with tab_executions:
        _render_executions_tab(data, filters)

    with tab_workers:
        _render_workers_tab(data, filters)

    with tab_governance:
        _render_governance_tab(data, filters)

    with tab_rollback:
        _render_rollback_tab(data, filters)

    with tab_graphs:
        _render_graphs_tab(data, filters)

    with tab_leases:
        _render_leases_tab(data, filters)

    with tab_events:
        _render_event_stream_tab(data, filters)


# Backward-compatible alias
render_control_plane_console = render_execution_control_plane_console