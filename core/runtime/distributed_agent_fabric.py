"""
core/runtime/distributed_agent_fabric.py

Distributed Agent Fabric for Veridion Pro / CUI GovCloud App.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


STATUS_PENDING = "PENDING"
STATUS_LEASED = "LEASED"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_RETRY = "RETRY"
STATUS_DEAD = "DEAD"

WORKER_HEALTHY = "HEALTHY"
WORKER_DEGRADED = "DEGRADED"
WORKER_DEAD = "DEAD"

EVENT_AGENT_WORKER_REGISTERED = "AGENT_WORKER_REGISTERED"
EVENT_AGENT_TASK_LEASED = "AGENT_TASK_LEASED"
EVENT_AGENT_TASK_REQUEUED = "AGENT_TASK_REQUEUED"
EVENT_AGENT_TASK_FAILED_PERMANENTLY = "AGENT_TASK_FAILED_PERMANENTLY"
EVENT_AGENT_WORKER_HEARTBEAT = "AGENT_WORKER_HEARTBEAT"
EVENT_AGENT_WORKER_DEAD = "AGENT_WORKER_DEAD"

DEFAULT_TENANT = "default"
DEFAULT_LEASE_MS = 120_000
DEFAULT_HEARTBEAT_TIMEOUT_MS = 180_000
DEFAULT_MAX_ATTEMPTS = 5


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _json_loads(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value or "{}")
    except Exception:
        return {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None
    return getattr(storage_or_ledger, "ledger", storage_or_ledger)


@dataclass
class AgentWorker:
    worker_id: str
    tenant_id: str = DEFAULT_TENANT
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 5
    status: str = WORKER_HEALTHY
    hostname: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at_ms: int = field(default_factory=_now_ms)
    last_heartbeat_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentLease:
    lease_id: str
    task_id: str
    worker_id: str
    tenant_id: str
    agent_name: str
    task_type: str
    lease_expires_ms: int
    attempts: int
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DistributedAgentFabric:
    def __init__(
        self,
        storage: Any = None,
        *,
        event_bus: Any = None,
        agent_coordinator: Any = None,
    ) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.agent_coordinator = agent_coordinator or getattr(
            storage,
            "agent_coordinator",
            None,
        )
        self.db_path = self._resolve_db_path()
        self.ensure_schema()

    def _resolve_db_path(self) -> str:
        ledger = self.ledger

        if ledger is not None:
            for attr in ("db_path", "database_path", "path", "_db_path"):
                path = getattr(ledger, attr, None)
                if path:
                    return path

        if isinstance(self.storage, str):
            return self.storage

        return "data/ledger.db"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
        )

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
                CREATE TABLE IF NOT EXISTS agent_workers (
                    worker_id TEXT PRIMARY KEY,
                    tenant_id TEXT DEFAULT 'default',
                    capabilities_json TEXT,
                    max_concurrent_tasks INTEGER DEFAULT 5,
                    status TEXT,
                    hostname TEXT,
                    metadata_json TEXT,
                    registered_at_ms INTEGER NOT NULL,
                    last_heartbeat_ms INTEGER NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS distributed_agent_leases (
                    lease_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    worker_id TEXT NOT NULL,
                    tenant_id TEXT DEFAULT 'default',
                    agent_name TEXT,
                    task_type TEXT,
                    status TEXT,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 5,
                    payload_json TEXT,
                    lease_expires_ms INTEGER NOT NULL,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER,
                    last_error TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_leases_status
                ON distributed_agent_leases(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_leases_worker
                ON distributed_agent_leases(worker_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_leases_expiry
                ON distributed_agent_leases(lease_expires_ms)
                """
            )

            conn.commit()

    def register_worker(
        self,
        *,
        worker_id: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        capabilities: Optional[List[str]] = None,
        max_concurrent_tasks: int = 5,
        hostname: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentWorker:
        worker = AgentWorker(
            worker_id=worker_id or f"AGW-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id or DEFAULT_TENANT,
            capabilities=capabilities or [],
            max_concurrent_tasks=max_concurrent_tasks,
            hostname=hostname,
            metadata=metadata or {},
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO agent_workers (
                    worker_id,
                    tenant_id,
                    capabilities_json,
                    max_concurrent_tasks,
                    status,
                    hostname,
                    metadata_json,
                    registered_at_ms,
                    last_heartbeat_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    worker.worker_id,
                    worker.tenant_id,
                    _json_dumps(worker.capabilities),
                    worker.max_concurrent_tasks,
                    worker.status,
                    worker.hostname,
                    _json_dumps(worker.metadata),
                    worker.registered_at_ms,
                    worker.last_heartbeat_ms,
                ),
            )
            conn.commit()

        self._emit(
            EVENT_AGENT_WORKER_REGISTERED,
            tenant_id=worker.tenant_id,
            payload=worker.to_dict(),
        )

        return worker

    def heartbeat_worker(
        self,
        worker_id: str,
        *,
        status: str = WORKER_HEALTHY,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT worker_id, tenant_id, metadata_json
                FROM agent_workers
                WHERE worker_id=?
                LIMIT 1
                """,
                (worker_id,),
            ).fetchone()

            if not row:
                return False

            tenant_id = row[1]
            existing_metadata = _json_loads(row[2])
            if not isinstance(existing_metadata, dict):
                existing_metadata = {}

            existing_metadata.update(metadata or {})

            conn.execute(
                """
                UPDATE agent_workers
                SET status=?,
                    metadata_json=?,
                    last_heartbeat_ms=?
                WHERE worker_id=?
                """,
                (
                    status,
                    _json_dumps(existing_metadata),
                    _now_ms(),
                    worker_id,
                ),
            )
            conn.commit()

        self._emit(
            EVENT_AGENT_WORKER_HEARTBEAT,
            tenant_id=tenant_id,
            payload={
                "worker_id": worker_id,
                "status": status,
                "metadata": existing_metadata,
            },
        )

        return True

    def detect_dead_workers(
        self,
        *,
        heartbeat_timeout_ms: int = DEFAULT_HEARTBEAT_TIMEOUT_MS,
    ) -> List[str]:
        cutoff = _now_ms() - heartbeat_timeout_ms
        dead_workers: List[str] = []

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT worker_id, tenant_id
                FROM agent_workers
                WHERE last_heartbeat_ms < ?
                  AND status != ?
                """,
                (cutoff, WORKER_DEAD),
            ).fetchall()

            for worker_id, tenant_id in rows:
                conn.execute(
                    """
                    UPDATE agent_workers
                    SET status=?
                    WHERE worker_id=?
                    """,
                    (WORKER_DEAD, worker_id),
                )

                dead_workers.append(worker_id)

                self._emit(
                    EVENT_AGENT_WORKER_DEAD,
                    tenant_id=tenant_id,
                    payload={
                        "worker_id": worker_id,
                        "cutoff_ms": cutoff,
                    },
                )

            conn.commit()

        return dead_workers

    def claim_task(
        self,
        *,
        worker_id: str,
        tenant_id: str = DEFAULT_TENANT,
        lease_ms: int = DEFAULT_LEASE_MS,
    ) -> Optional[AgentLease]:
        worker = self._get_worker(worker_id)

        if not worker:
            return None

        if self._active_worker_leases(worker_id) >= worker.max_concurrent_tasks:
            return None

        task = self._select_pending_task(
            tenant_id=tenant_id,
            capabilities=set(worker.capabilities),
        )

        if not task:
            return None

        task_id = task["task_id"]
        attempts = _safe_int(task.get("attempts"), 0) + 1
        lease_id = f"LEASE-{uuid.uuid4().hex[:12].upper()}"
        now = _now_ms()

        payload = _json_loads(task.get("payload_json"))
        if not isinstance(payload, dict):
            payload = {}

        lease = AgentLease(
            lease_id=lease_id,
            task_id=task_id,
            worker_id=worker_id,
            tenant_id=tenant_id,
            agent_name=task["agent_name"],
            task_type=task["task_type"],
            lease_expires_ms=now + lease_ms,
            attempts=attempts,
            payload=payload,
            created_at_ms=now,
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO distributed_agent_leases (
                    lease_id,
                    task_id,
                    worker_id,
                    tenant_id,
                    agent_name,
                    task_type,
                    status,
                    attempts,
                    max_attempts,
                    payload_json,
                    lease_expires_ms,
                    created_at_ms,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lease.lease_id,
                    lease.task_id,
                    lease.worker_id,
                    lease.tenant_id,
                    lease.agent_name,
                    lease.task_type,
                    STATUS_LEASED,
                    lease.attempts,
                    DEFAULT_MAX_ATTEMPTS,
                    _json_dumps(lease.payload),
                    lease.lease_expires_ms,
                    now,
                    now,
                ),
            )

            conn.execute(
                """
                UPDATE agent_tasks
                SET status=?,
                    updated_at_ms=?
                WHERE task_id=?
                """,
                (STATUS_LEASED, now, task_id),
            )

            conn.commit()

        self._emit(
            EVENT_AGENT_TASK_LEASED,
            tenant_id=tenant_id,
            payload=lease.to_dict(),
        )

        return lease

    def complete_lease(
        self,
        *,
        lease_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        now = _now_ms()

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT task_id, tenant_id
                FROM distributed_agent_leases
                WHERE lease_id=?
                LIMIT 1
                """,
                (lease_id,),
            ).fetchone()

            if not row:
                return False

            task_id, _tenant_id = row

            conn.execute(
                """
                UPDATE distributed_agent_leases
                SET status=?,
                    completed_at_ms=?,
                    updated_at_ms=?
                WHERE lease_id=?
                """,
                (STATUS_COMPLETED, now, now, lease_id),
            )

            conn.execute(
                """
                UPDATE agent_tasks
                SET status=?,
                    result_json=?,
                    completed_at_ms=?,
                    updated_at_ms=?
                WHERE task_id=?
                """,
                (
                    STATUS_COMPLETED,
                    _json_dumps(result or {}),
                    now,
                    now,
                    task_id,
                ),
            )

            conn.commit()

        return True

    def fail_lease(
        self,
        *,
        lease_id: str,
        error: str,
        requeue: bool = True,
    ) -> bool:
        now = _now_ms()

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT task_id, tenant_id, attempts, max_attempts
                FROM distributed_agent_leases
                WHERE lease_id=?
                LIMIT 1
                """,
                (lease_id,),
            ).fetchone()

            if not row:
                return False

            task_id, tenant_id, attempts, max_attempts = row
            attempts = _safe_int(attempts)
            max_attempts = _safe_int(max_attempts, DEFAULT_MAX_ATTEMPTS)
            permanent = attempts >= max_attempts

            lease_status = STATUS_FAILED if permanent else STATUS_RETRY
            task_status = STATUS_FAILED if permanent or not requeue else STATUS_PENDING

            conn.execute(
                """
                UPDATE distributed_agent_leases
                SET status=?,
                    last_error=?,
                    updated_at_ms=?,
                    completed_at_ms=?
                WHERE lease_id=?
                """,
                (
                    lease_status,
                    error,
                    now,
                    now if permanent else None,
                    lease_id,
                ),
            )

            conn.execute(
                """
                UPDATE agent_tasks
                SET status=?,
                    last_error=?,
                    updated_at_ms=?
                WHERE task_id=?
                """,
                (
                    task_status,
                    error,
                    now,
                    task_id,
                ),
            )

            conn.commit()

        self._emit(
            EVENT_AGENT_TASK_FAILED_PERMANENTLY
            if permanent
            else EVENT_AGENT_TASK_REQUEUED,
            tenant_id=tenant_id,
            payload={
                "lease_id": lease_id,
                "task_id": task_id,
                "error": error,
                "attempts": attempts,
                "max_attempts": max_attempts,
                "permanent": permanent,
            },
        )

        return True

    def reclaim_expired_leases(self) -> int:
        now = _now_ms()
        count = 0
        emit_events: List[Dict[str, Any]] = []

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT lease_id, task_id, tenant_id, attempts, max_attempts
                FROM distributed_agent_leases
                WHERE status IN (?, ?, ?)
                  AND lease_expires_ms < ?
                """,
                (STATUS_LEASED, STATUS_RUNNING, STATUS_RETRY, now),
            ).fetchall()

            for lease_id, task_id, tenant_id, attempts, max_attempts in rows:
                attempts = _safe_int(attempts)
                max_attempts = _safe_int(max_attempts, DEFAULT_MAX_ATTEMPTS)

                if attempts >= max_attempts:
                    conn.execute(
                        """
                        UPDATE distributed_agent_leases
                        SET status=?,
                            completed_at_ms=?,
                            updated_at_ms=?,
                            last_error=?
                        WHERE lease_id=?
                        """,
                        (
                            STATUS_FAILED,
                            now,
                            now,
                            "Lease expired and max attempts exceeded.",
                            lease_id,
                        ),
                    )

                    conn.execute(
                        """
                        UPDATE agent_tasks
                        SET status=?,
                            updated_at_ms=?,
                            last_error=?
                        WHERE task_id=?
                        """,
                        (
                            STATUS_FAILED,
                            now,
                            "Lease expired and max attempts exceeded.",
                            task_id,
                        ),
                    )

                else:
                    conn.execute(
                        """
                        UPDATE distributed_agent_leases
                        SET status=?,
                            updated_at_ms=?,
                            last_error=?
                        WHERE lease_id=?
                        """,
                        (
                            STATUS_RETRY,
                            now,
                            "Lease expired; task requeued.",
                            lease_id,
                        ),
                    )

                    conn.execute(
                        """
                        UPDATE agent_tasks
                        SET status=?,
                            updated_at_ms=?
                        WHERE task_id=?
                        """,
                        (
                            STATUS_PENDING,
                            now,
                            task_id,
                        ),
                    )

                    emit_events.append(
                        {
                            "tenant_id": tenant_id,
                            "payload": {
                                "lease_id": lease_id,
                                "task_id": task_id,
                                "reason": "lease_expired",
                            },
                        }
                    )

                count += 1

            conn.commit()

        for event in emit_events:
            self._emit(
                EVENT_AGENT_TASK_REQUEUED,
                tenant_id=event["tenant_id"],
                payload=event["payload"],
            )

        return count

    def list_workers(
        self,
        *,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if tenant_id:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM agent_workers
                    WHERE tenant_id=?
                    ORDER BY last_heartbeat_ms DESC
                    """,
                    (tenant_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM agent_workers
                    ORDER BY last_heartbeat_ms DESC
                    """
                ).fetchall()

            cols = [
                d[1]
                for d in conn.execute(
                    "PRAGMA table_info(agent_workers)"
                ).fetchall()
            ]

        return [dict(zip(cols, row)) for row in rows]

    def list_leases(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM distributed_agent_leases
                    WHERE status=?
                    ORDER BY updated_at_ms DESC
                    LIMIT ?
                    """,
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM distributed_agent_leases
                    ORDER BY updated_at_ms DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

            cols = [
                d[1]
                for d in conn.execute(
                    "PRAGMA table_info(distributed_agent_leases)"
                ).fetchall()
            ]

        return [dict(zip(cols, row)) for row in rows]

    def _get_worker(self, worker_id: str) -> Optional[AgentWorker]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM agent_workers
                WHERE worker_id=?
                LIMIT 1
                """,
                (worker_id,),
            ).fetchone()

            if not row:
                return None

            cols = [
                d[1]
                for d in conn.execute(
                    "PRAGMA table_info(agent_workers)"
                ).fetchall()
            ]

        data = dict(zip(cols, row))

        capabilities = _json_loads(data.get("capabilities_json"))
        if not isinstance(capabilities, list):
            capabilities = []

        return AgentWorker(
            worker_id=data["worker_id"],
            tenant_id=data.get("tenant_id") or DEFAULT_TENANT,
            capabilities=capabilities,
            max_concurrent_tasks=_safe_int(data.get("max_concurrent_tasks"), 5),
            status=data.get("status") or WORKER_HEALTHY,
            hostname=data.get("hostname"),
            metadata=_json_loads(data.get("metadata_json"))
            if isinstance(_json_loads(data.get("metadata_json")), dict)
            else {},
            registered_at_ms=_safe_int(data.get("registered_at_ms"), _now_ms()),
            last_heartbeat_ms=_safe_int(data.get("last_heartbeat_ms"), _now_ms()),
        )

    def _active_worker_leases(self, worker_id: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*)
                FROM distributed_agent_leases
                WHERE worker_id=?
                  AND status IN (?, ?)
                """,
                (worker_id, STATUS_LEASED, STATUS_RUNNING),
            ).fetchone()

        return int(row[0] if row else 0)

    def _select_pending_task(
        self,
        *,
        tenant_id: str,
        capabilities: set[str],
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM agent_tasks
                WHERE status=?
                  AND tenant_id=?
                ORDER BY
                    CASE priority
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                        ELSE 5
                    END,
                    created_at_ms ASC
                LIMIT 100
                """,
                (STATUS_PENDING, tenant_id),
            ).fetchall()

            cols = [
                d[1]
                for d in conn.execute(
                    "PRAGMA table_info(agent_tasks)"
                ).fetchall()
            ]

        for row in rows:
            task = dict(zip(cols, row))
            agent_name = task.get("agent_name")

            if not capabilities or agent_name in capabilities:
                return task

        return None

    def _emit(
        self,
        event_type: str,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
        severity: str = "INFO",
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="distributed_agent_fabric",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="distributed_agent_fabric",
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_FABRIC: Optional[DistributedAgentFabric] = None


def get_distributed_agent_fabric(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
    agent_coordinator: Any = None,
) -> DistributedAgentFabric:
    global _DEFAULT_FABRIC

    if reset or _DEFAULT_FABRIC is None:
        _DEFAULT_FABRIC = DistributedAgentFabric(
            storage=storage,
            event_bus=event_bus,
            agent_coordinator=agent_coordinator,
        )

    return _DEFAULT_FABRIC