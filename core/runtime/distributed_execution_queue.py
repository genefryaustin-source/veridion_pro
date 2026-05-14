"""
core/runtime/distributed_execution_queue.py

Durable Distributed Execution Queue.

Provides:
- queue-backed autonomous execution
- durable jobs
- lease management
- retries
- dead-letter handling
- tenant-aware routing
- worker affinity
- priority execution
- action / graph / rollback jobs
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


JOB_TYPE_ACTION = "ACTION"
JOB_TYPE_GRAPH = "GRAPH"
JOB_TYPE_ROLLBACK = "ROLLBACK"

STATUS_PENDING = "PENDING"
STATUS_RETRY = "RETRY"
STATUS_LEASED = "LEASED"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_DEAD_LETTER = "DEAD_LETTER"

DEFAULT_DB_PATH = "data/distributed_execution_queue.db"
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_LEASE_MS = 120_000


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _json_loads(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value

    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


@dataclass
class DistributedJob:
    job_id: str
    job_type: str
    tenant_id: str = "default"
    priority: int = 100
    status: str = STATUS_PENDING
    agent_name: Optional[str] = None
    action: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    tenant_context_json: Optional[str] = None
    worker_id: Optional[str] = None
    lease_expires_ms: Optional[int] = None
    attempts: int = 0
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    result: Dict[str, Any] = field(default_factory=dict)
    last_error: Optional[str] = None
    created_at_ms: int = field(default_factory=_now_ms)
    updated_at_ms: int = field(default_factory=_now_ms)
    completed_at_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DistributedExecutionQueue:
    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
    ) -> None:
        self.db_path = db_path
        self.ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row

        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass

        return conn

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS distributed_jobs (
                    job_id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    tenant_id TEXT DEFAULT 'default',
                    priority INTEGER DEFAULT 100,
                    status TEXT NOT NULL,
                    agent_name TEXT,
                    action TEXT,
                    payload_json TEXT,
                    tenant_context_json TEXT,
                    worker_id TEXT,
                    lease_expires_ms INTEGER,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 5,
                    result_json TEXT,
                    last_error TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER
                )
                """
            )

            existing_cols = {
                row[1]
                for row in conn.execute(
                    "PRAGMA table_info(distributed_jobs)"
                ).fetchall()
            }

            required_columns = {
                "tenant_context_json": "ALTER TABLE distributed_jobs ADD COLUMN tenant_context_json TEXT",
                "worker_id": "ALTER TABLE distributed_jobs ADD COLUMN worker_id TEXT",
                "lease_expires_ms": "ALTER TABLE distributed_jobs ADD COLUMN lease_expires_ms INTEGER",
                "attempts": "ALTER TABLE distributed_jobs ADD COLUMN attempts INTEGER DEFAULT 0",
                "max_attempts": "ALTER TABLE distributed_jobs ADD COLUMN max_attempts INTEGER DEFAULT 5",
                "result_json": "ALTER TABLE distributed_jobs ADD COLUMN result_json TEXT",
                "last_error": "ALTER TABLE distributed_jobs ADD COLUMN last_error TEXT",
                "completed_at_ms": "ALTER TABLE distributed_jobs ADD COLUMN completed_at_ms INTEGER",
            }

            for col, sql in required_columns.items():
                if col not in existing_cols:
                    try:
                        conn.execute(sql)
                    except Exception:
                        pass

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_status_priority
                ON distributed_jobs(status, priority, created_at_ms)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_tenant_status
                ON distributed_jobs(tenant_id, status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_worker
                ON distributed_jobs(worker_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_jobs_lease
                ON distributed_jobs(lease_expires_ms)
                """
            )

            conn.commit()

    # ========================================================
    # ENQUEUE
    # ========================================================

    def enqueue_action(
        self,
        *,
        agent_name: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
        tenant_context_json: Optional[str] = None,
        priority: int = 100,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> str:
        return self.enqueue(
            job_type=JOB_TYPE_ACTION,
            tenant_id=tenant_id,
            priority=priority,
            agent_name=agent_name,
            action=action,
            payload=context or {},
            tenant_context_json=tenant_context_json,
            max_attempts=max_attempts,
        )

    def enqueue_graph(
        self,
        *,
        graph_context: Dict[str, Any],
        tenant_id: str = "default",
        tenant_context_json: Optional[str] = None,
        priority: int = 50,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> str:
        return self.enqueue(
            job_type=JOB_TYPE_GRAPH,
            tenant_id=tenant_id,
            priority=priority,
            payload=graph_context or {},
            tenant_context_json=tenant_context_json,
            max_attempts=max_attempts,
        )

    def enqueue_rollback(
        self,
        *,
        rollback_payload: Dict[str, Any],
        tenant_id: str = "default",
        tenant_context_json: Optional[str] = None,
        priority: int = 1,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> str:
        return self.enqueue(
            job_type=JOB_TYPE_ROLLBACK,
            tenant_id=tenant_id,
            priority=priority,
            action=rollback_payload.get("action") or "ROLLBACK",
            payload=rollback_payload or {},
            tenant_context_json=tenant_context_json,
            max_attempts=max_attempts,
        )

    def enqueue(
        self,
        *,
        job_type: str,
        tenant_id: str = "default",
        priority: int = 100,
        agent_name: Optional[str] = None,
        action: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        tenant_context_json: Optional[str] = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> str:
        job_id = f"JOB-{uuid.uuid4().hex[:12].upper()}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO distributed_jobs (
                    job_id,
                    job_type,
                    tenant_id,
                    priority,
                    status,
                    agent_name,
                    action,
                    payload_json,
                    tenant_context_json,
                    attempts,
                    max_attempts,
                    result_json,
                    created_at_ms,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    job_type,
                    tenant_id or "default",
                    int(priority),
                    STATUS_PENDING,
                    agent_name,
                    action,
                    _json_dumps(payload or {}),
                    tenant_context_json,
                    0,
                    int(max_attempts),
                    "{}",
                    now,
                    now,
                ),
            )
            conn.commit()

        return job_id

    # ========================================================
    # LEASING
    # ========================================================

    def lease_next(
        self,
        *,
        worker_id: str,
        tenant_id: Optional[str] = None,
        lease_ms: int = DEFAULT_LEASE_MS,
    ) -> Optional[DistributedJob]:
        now = _now_ms()
        lease_expires = now + int(lease_ms)

        clauses = [
            "status IN (?, ?)",
            "(lease_expires_ms IS NULL OR lease_expires_ms < ?)",
        ]
        params: List[Any] = [
            STATUS_PENDING,
            STATUS_RETRY,
            now,
        ]

        if tenant_id:
            clauses.append("tenant_id=?")
            params.append(tenant_id)

        where = " AND ".join(clauses)

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")

            row = conn.execute(
                f"""
                SELECT *
                FROM distributed_jobs
                WHERE {where}
                ORDER BY priority ASC, created_at_ms ASC
                LIMIT 1
                """,
                params,
            ).fetchone()

            if not row:
                conn.commit()
                return None

            job_id = row["job_id"]
            attempts = int(row["attempts"] or 0) + 1

            conn.execute(
                """
                UPDATE distributed_jobs
                SET status=?,
                    worker_id=?,
                    attempts=?,
                    lease_expires_ms=?,
                    updated_at_ms=?
                WHERE job_id=?
                """,
                (
                    STATUS_LEASED,
                    worker_id,
                    attempts,
                    lease_expires,
                    now,
                    job_id,
                ),
            )

            conn.commit()

            updated = conn.execute(
                """
                SELECT *
                FROM distributed_jobs
                WHERE job_id=?
                LIMIT 1
                """,
                (job_id,),
            ).fetchone()

        return self._row_to_job(updated) if updated else None

    def mark_running(
        self,
        job_id: str,
        worker_id: str,
    ) -> bool:
        now = _now_ms()

        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE distributed_jobs
                SET status=?,
                    worker_id=?,
                    updated_at_ms=?
                WHERE job_id=?
                """,
                (
                    STATUS_RUNNING,
                    worker_id,
                    now,
                    job_id,
                ),
            )
            conn.commit()

        return cur.rowcount > 0

    def renew_lease(
        self,
        job_id: str,
        worker_id: str,
        *,
        lease_ms: int = DEFAULT_LEASE_MS,
    ) -> bool:
        now = _now_ms()
        lease_expires = now + int(lease_ms)

        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE distributed_jobs
                SET lease_expires_ms=?,
                    updated_at_ms=?
                WHERE job_id=?
                  AND worker_id=?
                  AND status IN (?, ?)
                """,
                (
                    lease_expires,
                    now,
                    job_id,
                    worker_id,
                    STATUS_LEASED,
                    STATUS_RUNNING,
                ),
            )
            conn.commit()

        return cur.rowcount > 0

    # ========================================================
    # COMPLETION / FAILURE
    # ========================================================

    def complete(
        self,
        job_id: str,
        worker_id: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        now = _now_ms()

        params: List[Any] = [
            STATUS_COMPLETED,
            _json_dumps(result or {}),
            now,
            now,
            job_id,
        ]

        worker_clause = ""

        if worker_id:
            worker_clause = "AND worker_id=?"
            params.append(worker_id)

        with self._connect() as conn:
            cur = conn.execute(
                f"""
                UPDATE distributed_jobs
                SET status=?,
                    result_json=?,
                    updated_at_ms=?,
                    completed_at_ms=?,
                    lease_expires_ms=NULL
                WHERE job_id=?
                {worker_clause}
                """,
                params,
            )
            conn.commit()

        return cur.rowcount > 0

    def fail(
        self,
        job_id: str,
        worker_id: Optional[str] = None,
        error: str = "",
    ) -> bool:
        job = self.get_job(job_id)

        if not job:
            return False

        attempts = int(job.attempts or 0)
        max_attempts = int(job.max_attempts or DEFAULT_MAX_ATTEMPTS)

        final_status = (
            STATUS_DEAD_LETTER
            if attempts >= max_attempts
            else STATUS_RETRY
        )

        now = _now_ms()

        params: List[Any] = [
            final_status,
            error,
            now,
            now if final_status == STATUS_DEAD_LETTER else None,
            job_id,
        ]

        worker_clause = ""

        if worker_id:
            worker_clause = "AND worker_id=?"
            params.append(worker_id)

        with self._connect() as conn:
            cur = conn.execute(
                f"""
                UPDATE distributed_jobs
                SET status=?,
                    last_error=?,
                    updated_at_ms=?,
                    completed_at_ms=?,
                    lease_expires_ms=NULL
                WHERE job_id=?
                {worker_clause}
                """,
                params,
            )
            conn.commit()

        return cur.rowcount > 0

    def requeue_expired_leases(self) -> int:
        now = _now_ms()
        count = 0

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT job_id, attempts, max_attempts
                FROM distributed_jobs
                WHERE status IN (?, ?)
                  AND lease_expires_ms IS NOT NULL
                  AND lease_expires_ms < ?
                """,
                (
                    STATUS_LEASED,
                    STATUS_RUNNING,
                    now,
                ),
            ).fetchall()

            for row in rows:
                attempts = int(row["attempts"] or 0)
                max_attempts = int(row["max_attempts"] or DEFAULT_MAX_ATTEMPTS)

                if attempts >= max_attempts:
                    status = STATUS_DEAD_LETTER
                    completed_at_ms = now
                    error = "Lease expired and max attempts exceeded."
                else:
                    status = STATUS_RETRY
                    completed_at_ms = None
                    error = "Lease expired; job requeued."

                conn.execute(
                    """
                    UPDATE distributed_jobs
                    SET status=?,
                        worker_id=NULL,
                        lease_expires_ms=NULL,
                        last_error=?,
                        updated_at_ms=?,
                        completed_at_ms=?
                    WHERE job_id=?
                    """,
                    (
                        status,
                        error,
                        now,
                        completed_at_ms,
                        row["job_id"],
                    ),
                )

                count += 1

            conn.commit()

        return count

    # ========================================================
    # EXECUTION
    # ========================================================

    def execute_job(
        self,
        job: DistributedJob,
        *,
        worker_id: str,
        storage: Any = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.mark_running(job.job_id, worker_id)

        config = config or {}
        dry_run = bool(config.get("dry_run", True))

        try:
            if dry_run:
                return {
                    "success": True,
                    "status": "DRY_RUN_COMPLETED",
                    "job_id": job.job_id,
                    "job_type": job.job_type,
                    "message": "Dry-run execution completed.",
                    "payload": job.payload,
                }

            if job.job_type == JOB_TYPE_ACTION:
                return self._execute_action_job(job, storage=storage)

            if job.job_type == JOB_TYPE_GRAPH:
                return self._execute_graph_job(job, storage=storage)

            if job.job_type == JOB_TYPE_ROLLBACK:
                return self._execute_rollback_job(job, storage=storage)

            return {
                "success": False,
                "status": "UNKNOWN_JOB_TYPE",
                "error": f"Unknown job type: {job.job_type}",
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "EXECUTION_ERROR",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }

    def _execute_action_job(
        self,
        job: DistributedJob,
        *,
        storage: Any = None,
    ) -> Dict[str, Any]:
        router = getattr(storage, "action_execution_router", None)

        if router is not None and hasattr(router, "execute"):
            result = router.execute(
                agent_name=job.agent_name,
                action=job.action,
                context=job.payload,
                tenant_id=job.tenant_id,
            )
            return result if isinstance(result, dict) else {"success": True, "result": result}

        return {
            "success": True,
            "status": "ACTION_ROUTED_SIMULATION",
            "job_id": job.job_id,
            "agent_name": job.agent_name,
            "action": job.action,
            "message": "No action router available; simulated execution.",
        }

    def _execute_graph_job(
        self,
        job: DistributedJob,
        *,
        storage: Any = None,
    ) -> Dict[str, Any]:
        graph_engine = getattr(storage, "execution_graph_engine", None)

        if graph_engine is not None and hasattr(graph_engine, "execute_graph"):
            result = graph_engine.execute_graph(job.payload)
            return result if isinstance(result, dict) else {"success": True, "result": result}

        return {
            "success": True,
            "status": "GRAPH_ROUTED_SIMULATION",
            "job_id": job.job_id,
            "message": "No graph engine available; simulated graph execution.",
        }

    def _execute_rollback_job(
        self,
        job: DistributedJob,
        *,
        storage: Any = None,
    ) -> Dict[str, Any]:
        try:
            from core.runtime.execution_state_store import ExecutionStateStore
            from core.ai.orchestration.rollback_orchestrator import get_rollback_orchestrator

            rollback_id = job.payload.get("rollback_id")

            if not rollback_id:
                store = ExecutionStateStore(storage)
                rollback_id = store.create_rollback_chain(
                    execution_id=job.payload.get("execution_id"),
                    tenant_id=job.tenant_id,
                    payload=job.payload,
                )

            orchestrator = get_rollback_orchestrator(storage)
            result = orchestrator.execute_rollback(rollback_id)

            return {
                "success": bool(result.ok),
                "status": result.status,
                "rollback_id": rollback_id,
                "result": result.__dict__,
            }

        except Exception as exc:
            return {
                "success": False,
                "status": "ROLLBACK_EXECUTION_ERROR",
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }

    # ========================================================
    # READS
    # ========================================================

    def get_job(self, job_id: str) -> Optional[DistributedJob]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM distributed_jobs
                WHERE job_id=?
                LIMIT 1
                """,
                (job_id,),
            ).fetchone()

        return self._row_to_job(row) if row else None

    def list_jobs(
        self,
        *,
        status: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []

        if status:
            clauses.append("status=?")
            params.append(status)

        if tenant_id:
            clauses.append("tenant_id=?")
            params.append(tenant_id)

        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT *
                FROM distributed_jobs
                {where}
                ORDER BY priority ASC, updated_at_ms DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [
            self._row_to_job(row).to_dict()
            for row in rows
            if row
        ]

    def stats(self) -> Dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT status, COUNT(*) AS count
                FROM distributed_jobs
                GROUP BY status
                """
            ).fetchall()

        by_status = {
            row["status"]: int(row["count"])
            for row in rows
        }

        return {
            "total": sum(by_status.values()),
            "pending": by_status.get(STATUS_PENDING, 0),
            "retry": by_status.get(STATUS_RETRY, 0),
            "leased": by_status.get(STATUS_LEASED, 0),
            "running": by_status.get(STATUS_RUNNING, 0),
            "completed": by_status.get(STATUS_COMPLETED, 0),
            "failed": by_status.get(STATUS_FAILED, 0),
            "dead_letter": by_status.get(STATUS_DEAD_LETTER, 0),
            "by_status": by_status,
        }

    def _row_to_job(self, row: sqlite3.Row) -> DistributedJob:
        return DistributedJob(
            job_id=row["job_id"],
            job_type=row["job_type"],
            tenant_id=row["tenant_id"] or "default",
            priority=int(row["priority"] or 100),
            status=row["status"],
            agent_name=row["agent_name"],
            action=row["action"],
            payload=_json_loads(row["payload_json"]),
            tenant_context_json=row["tenant_context_json"],
            worker_id=row["worker_id"],
            lease_expires_ms=row["lease_expires_ms"],
            attempts=int(row["attempts"] or 0),
            max_attempts=int(row["max_attempts"] or DEFAULT_MAX_ATTEMPTS),
            result=_json_loads(row["result_json"]),
            last_error=row["last_error"],
            created_at_ms=int(row["created_at_ms"] or _now_ms()),
            updated_at_ms=int(row["updated_at_ms"] or _now_ms()),
            completed_at_ms=row["completed_at_ms"],
        )


_DEFAULT_QUEUE: Optional[DistributedExecutionQueue] = None


def get_distributed_execution_queue(
    db_path: str = DEFAULT_DB_PATH,
    *,
    reset: bool = False,
) -> DistributedExecutionQueue:
    global _DEFAULT_QUEUE

    if reset or _DEFAULT_QUEUE is None:
        _DEFAULT_QUEUE = DistributedExecutionQueue(
            db_path=db_path,
        )

    return _DEFAULT_QUEUE