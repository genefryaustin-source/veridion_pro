"""
core/runtime/execution_graph_engine.py

Distributed Execution Graph Engine.

Purpose:
- graph-native autonomous operations
- DAG execution
- dependency-aware node scheduling
- distributed queue-backed node execution
- approval/verification/rollback node support
- graph state persistence
- crash/replay recovery
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


GRAPH_PENDING = "PENDING"
GRAPH_RUNNING = "RUNNING"
GRAPH_COMPLETED = "COMPLETED"
GRAPH_FAILED = "FAILED"
GRAPH_BLOCKED = "BLOCKED"
GRAPH_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"

NODE_PENDING = "PENDING"
NODE_READY = "READY"
NODE_QUEUED = "QUEUED"
NODE_RUNNING = "RUNNING"
NODE_COMPLETED = "COMPLETED"
NODE_FAILED = "FAILED"
NODE_BLOCKED = "BLOCKED"
NODE_SKIPPED = "SKIPPED"
NODE_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"

NODE_TYPE_ACTION = "ACTION"
NODE_TYPE_APPROVAL = "APPROVAL"
NODE_TYPE_VERIFICATION = "VERIFICATION"
NODE_TYPE_ROLLBACK = "ROLLBACK"
NODE_TYPE_CONNECTOR = "CONNECTOR"
NODE_TYPE_AI_DECISION = "AI_DECISION"
NODE_TYPE_WAIT = "WAIT"
NODE_TYPE_BRANCH = "BRANCH"
NODE_TYPE_MERGE = "MERGE"

DEFAULT_DB_PATH = "data/distributed_execution_queue.db"
DEFAULT_TENANT = "default"


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


@dataclass
class GraphExecutionResult:
    graph_id: str
    status: str
    ok: bool
    message: str
    queued_nodes: int = 0
    completed_nodes: int = 0
    failed_nodes: int = 0
    blocked_nodes: int = 0
    approval_required_nodes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionGraphEngine:
    def __init__(
        self,
        *,
        db_path: str = DEFAULT_DB_PATH,
        queue: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.db_path = db_path
        self.storage = storage
        self.queue = queue or getattr(storage, "execution_queue", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
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
                CREATE TABLE IF NOT EXISTS execution_graphs (
                    graph_id TEXT PRIMARY KEY,
                    tenant_id TEXT DEFAULT 'default',
                    name TEXT,
                    status TEXT,
                    context_json TEXT,
                    result_json TEXT,
                    created_by TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER,
                    last_error TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_graph_nodes (
                    node_id TEXT PRIMARY KEY,
                    graph_id TEXT NOT NULL,
                    tenant_id TEXT DEFAULT 'default',
                    node_type TEXT,
                    name TEXT,
                    action TEXT,
                    status TEXT,
                    payload_json TEXT,
                    result_json TEXT,
                    job_id TEXT,
                    worker_id TEXT,
                    sequence INTEGER DEFAULT 0,
                    requires_approval INTEGER DEFAULT 0,
                    approval_id TEXT,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER,
                    last_error TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_graph_edges (
                    edge_id TEXT PRIMARY KEY,
                    graph_id TEXT NOT NULL,
                    from_node_id TEXT NOT NULL,
                    to_node_id TEXT NOT NULL,
                    condition_json TEXT,
                    created_at_ms INTEGER NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_graph_nodes_graph
                ON execution_graph_nodes(graph_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_graph_nodes_status
                ON execution_graph_nodes(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_graph_edges_graph
                ON execution_graph_edges(graph_id)
                """
            )

            conn.commit()

    # ========================================================
    # GRAPH CREATION
    # ========================================================

    def create_graph(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        name: str = "Autonomous Execution Graph",
        nodes: List[Dict[str, Any]],
        edges: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        created_by: str = "execution_graph_engine",
    ) -> str:
        graph_id = f"GRAPH-{uuid.uuid4().hex[:12].upper()}"
        now = _now_ms()

        edges = edges or []

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO execution_graphs (
                    graph_id,
                    tenant_id,
                    name,
                    status,
                    context_json,
                    result_json,
                    created_by,
                    created_at_ms,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    graph_id,
                    tenant_id or DEFAULT_TENANT,
                    name,
                    GRAPH_PENDING,
                    _json_dumps(context or {}),
                    "{}",
                    created_by,
                    now,
                    now,
                ),
            )

            for idx, node in enumerate(nodes):
                node_id = node.get("node_id") or f"NODE-{uuid.uuid4().hex[:12].upper()}"

                conn.execute(
                    """
                    INSERT INTO execution_graph_nodes (
                        node_id,
                        graph_id,
                        tenant_id,
                        node_type,
                        name,
                        action,
                        status,
                        payload_json,
                        result_json,
                        sequence,
                        requires_approval,
                        approval_id,
                        attempts,
                        max_attempts,
                        created_at_ms,
                        updated_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        node_id,
                        graph_id,
                        tenant_id or DEFAULT_TENANT,
                        str(node.get("node_type") or NODE_TYPE_ACTION).upper(),
                        node.get("name") or node_id,
                        node.get("action"),
                        node.get("status") or NODE_PENDING,
                        _json_dumps(node.get("payload") or node.get("payload_json") or {}),
                        "{}",
                        int(node.get("sequence") if node.get("sequence") is not None else idx),
                        int(bool(node.get("requires_approval"))),
                        node.get("approval_id"),
                        int(node.get("attempts") or 0),
                        int(node.get("max_attempts") or 3),
                        now,
                        now,
                    ),
                )

            for edge in edges:
                conn.execute(
                    """
                    INSERT INTO execution_graph_edges (
                        edge_id,
                        graph_id,
                        from_node_id,
                        to_node_id,
                        condition_json,
                        created_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        edge.get("edge_id") or f"EDGE-{uuid.uuid4().hex[:12].upper()}",
                        graph_id,
                        edge["from_node_id"],
                        edge["to_node_id"],
                        _json_dumps(edge.get("condition") or {}),
                        now,
                    ),
                )

            conn.commit()

        self._emit(
            "EXECUTION_GRAPH_CREATED",
            tenant_id=tenant_id,
            payload={
                "graph_id": graph_id,
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
        )

        return graph_id

    # ========================================================
    # GRAPH EXECUTION
    # ========================================================

    def execute_graph(
        self,
        graph_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        graph_id = graph_context.get("graph_id")

        if not graph_id:
            graph_id = self.create_graph(
                tenant_id=graph_context.get("tenant_id") or DEFAULT_TENANT,
                name=graph_context.get("name") or "Queued Execution Graph",
                nodes=graph_context.get("nodes") or [],
                edges=graph_context.get("edges") or [],
                context=graph_context,
                created_by=graph_context.get("actor") or "execution_graph_engine",
            )

        result = self.run_graph(
            graph_id,
            actor=graph_context.get("actor") or "execution_graph_engine",
        )

        return result.to_dict()

    def run_graph(
        self,
        graph_id: str,
        *,
        actor: str = "execution_graph_engine",
        max_nodes: int = 100,
    ) -> GraphExecutionResult:
        graph = self.get_graph(graph_id)

        if not graph:
            return GraphExecutionResult(
                graph_id=graph_id,
                status=GRAPH_FAILED,
                ok=False,
                message="Graph not found.",
            )

        tenant_id = graph.get("tenant_id") or DEFAULT_TENANT

        self._update_graph_status(graph_id, GRAPH_RUNNING)

        self._emit(
            "EXECUTION_GRAPH_STARTED",
            tenant_id=tenant_id,
            payload={
                "graph_id": graph_id,
                "actor": actor,
            },
        )

        queued_nodes = 0
        completed_nodes = 0
        failed_nodes = 0
        blocked_nodes = 0
        approval_nodes = 0

        for _ in range(max_nodes):
            ready_nodes = self._find_ready_nodes(graph_id)

            if not ready_nodes:
                break

            progressed = False

            for node in ready_nodes:
                status = self._execute_node(
                    graph_id=graph_id,
                    node=node,
                    graph=graph,
                    actor=actor,
                )

                progressed = True

                if status == NODE_QUEUED:
                    queued_nodes += 1
                elif status == NODE_COMPLETED:
                    completed_nodes += 1
                elif status == NODE_FAILED:
                    failed_nodes += 1
                elif status == NODE_BLOCKED:
                    blocked_nodes += 1
                elif status == NODE_APPROVAL_REQUIRED:
                    approval_nodes += 1

            if not progressed:
                break

        final_status = self._derive_graph_status(graph_id)

        ok = final_status == GRAPH_COMPLETED

        result = GraphExecutionResult(
            graph_id=graph_id,
            status=final_status,
            ok=ok,
            message=f"Graph execution status: {final_status}",
            queued_nodes=queued_nodes,
            completed_nodes=completed_nodes,
            failed_nodes=failed_nodes,
            blocked_nodes=blocked_nodes,
            approval_required_nodes=approval_nodes,
        )

        self._complete_graph_if_terminal(graph_id, result)

        self._emit(
            "EXECUTION_GRAPH_UPDATED",
            tenant_id=tenant_id,
            payload=result.to_dict(),
        )

        return result

    # ========================================================
    # NODE EXECUTION
    # ========================================================

    def _execute_node(
        self,
        *,
        graph_id: str,
        node: Dict[str, Any],
        graph: Dict[str, Any],
        actor: str,
    ) -> str:
        node_id = node["node_id"]
        node_type = str(node.get("node_type") or NODE_TYPE_ACTION).upper()
        tenant_id = node.get("tenant_id") or graph.get("tenant_id") or DEFAULT_TENANT

        if bool(node.get("requires_approval")):
            self._update_node(
                node_id,
                status=NODE_APPROVAL_REQUIRED,
                result={
                    "message": "Node requires approval before execution.",
                },
            )

            return NODE_APPROVAL_REQUIRED

        if node_type == NODE_TYPE_APPROVAL:
            self._update_node(
                node_id,
                status=NODE_APPROVAL_REQUIRED,
                result={
                    "message": "Approval node reached.",
                },
            )

            return NODE_APPROVAL_REQUIRED

        if node_type in {NODE_TYPE_BRANCH, NODE_TYPE_MERGE, NODE_TYPE_WAIT}:
            self._update_node(
                node_id,
                status=NODE_COMPLETED,
                result={
                    "message": f"{node_type} node completed.",
                },
                completed=True,
            )

            return NODE_COMPLETED

        if self.queue is None:
            self._update_node(
                node_id,
                status=NODE_FAILED,
                result={
                    "message": "Execution queue unavailable.",
                },
                error="Execution queue unavailable.",
                completed=True,
            )

            return NODE_FAILED

        payload = _json_loads(node.get("payload_json"))

        job_payload = {
            **payload,
            "graph_id": graph_id,
            "node_id": node_id,
            "node_type": node_type,
            "graph_context": _json_loads(graph.get("context_json")),
        }

        job_id = None

        if node_type == NODE_TYPE_ROLLBACK:
            job_id = self.queue.enqueue_rollback(
                rollback_payload=job_payload,
                tenant_id=tenant_id,
                priority=int(node.get("sequence") or 100),
            )

        elif node_type == NODE_TYPE_VERIFICATION:
            job_id = self.queue.enqueue_action(
                agent_name="verification_agent",
                action=node.get("action") or "VERIFY",
                context=job_payload,
                tenant_id=tenant_id,
                priority=int(node.get("sequence") or 100),
            )

        else:
            job_id = self.queue.enqueue_action(
                agent_name=payload.get("agent_name") or node.get("action") or "execution_graph_node",
                action=node.get("action") or node_type,
                context=job_payload,
                tenant_id=tenant_id,
                priority=int(node.get("sequence") or 100),
            )

        self._update_node(
            node_id,
            status=NODE_QUEUED,
            result={
                "message": "Node queued for distributed execution.",
                "job_id": job_id,
            },
            job_id=job_id,
        )

        self._emit(
            "EXECUTION_GRAPH_NODE_QUEUED",
            tenant_id=tenant_id,
            payload={
                "graph_id": graph_id,
                "node_id": node_id,
                "job_id": job_id,
                "node_type": node_type,
            },
        )

        return NODE_QUEUED

    # ========================================================
    # RECOVERY / SYNC
    # ========================================================

    def sync_queued_nodes(self, graph_id: str) -> Dict[str, Any]:
        nodes = self.list_nodes(graph_id)
        updated = 0

        if self.queue is None:
            return {"updated": 0, "reason": "queue_unavailable"}

        for node in nodes:
            if node.get("status") not in {NODE_QUEUED, NODE_RUNNING}:
                continue

            job_id = node.get("job_id")

            if not job_id:
                continue

            job = self.queue.get_job(job_id)

            if not job:
                continue

            job_status = getattr(job, "status", None)
            worker_id = getattr(job, "worker_id", None)

            if job_status == "COMPLETED":
                self._update_node(
                    node["node_id"],
                    status=NODE_COMPLETED,
                    result=getattr(job, "result", {}),
                    worker_id=worker_id,
                    completed=True,
                )
                updated += 1

            elif job_status in {"FAILED", "DEAD_LETTER"}:
                self._update_node(
                    node["node_id"],
                    status=NODE_FAILED,
                    result=getattr(job, "result", {}),
                    worker_id=worker_id,
                    error=getattr(job, "last_error", None),
                    completed=True,
                )
                updated += 1

            elif job_status in {"LEASED", "RUNNING"}:
                self._update_node(
                    node["node_id"],
                    status=NODE_RUNNING,
                    worker_id=worker_id,
                )
                updated += 1

        final_status = self._derive_graph_status(graph_id)
        self._update_graph_status(graph_id, final_status)

        return {
            "graph_id": graph_id,
            "updated": updated,
            "status": final_status,
        }

    def recover_graph(self, graph_id: str) -> GraphExecutionResult:
        sync = self.sync_queued_nodes(graph_id)

        if sync.get("status") in {
            GRAPH_COMPLETED,
            GRAPH_FAILED,
            GRAPH_BLOCKED,
            GRAPH_APPROVAL_REQUIRED,
        }:
            return GraphExecutionResult(
                graph_id=graph_id,
                status=sync.get("status"),
                ok=sync.get("status") == GRAPH_COMPLETED,
                message="Graph recovered to terminal state.",
                metadata=sync,
            )

        return self.run_graph(graph_id)

    # ========================================================
    # READS
    # ========================================================

    def get_graph(self, graph_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM execution_graphs
                WHERE graph_id=?
                LIMIT 1
                """,
                (graph_id,),
            ).fetchone()

        return dict(row) if row else None

    def list_graphs(
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
                FROM execution_graphs
                {where}
                ORDER BY updated_at_ms DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [dict(r) for r in rows]

    def list_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM execution_graph_nodes
                WHERE graph_id=?
                ORDER BY sequence ASC, created_at_ms ASC
                """,
                (graph_id,),
            ).fetchall()

        return [dict(r) for r in rows]

    def list_edges(self, graph_id: str) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM execution_graph_edges
                WHERE graph_id=?
                ORDER BY created_at_ms ASC
                """,
                (graph_id,),
            ).fetchall()

        return [dict(r) for r in rows]

    def graph_snapshot(self, graph_id: str) -> Dict[str, Any]:
        return {
            "graph": self.get_graph(graph_id),
            "nodes": self.list_nodes(graph_id),
            "edges": self.list_edges(graph_id),
        }

    # ========================================================
    # STATUS LOGIC
    # ========================================================

    def _find_ready_nodes(self, graph_id: str) -> List[Dict[str, Any]]:
        nodes = self.list_nodes(graph_id)
        edges = self.list_edges(graph_id)

        terminal = {
            NODE_COMPLETED,
            NODE_FAILED,
            NODE_BLOCKED,
            NODE_APPROVAL_REQUIRED,
            NODE_SKIPPED,
            NODE_QUEUED,
            NODE_RUNNING,
        }

        completed = {
            n["node_id"]
            for n in nodes
            if n.get("status") == NODE_COMPLETED
        }

        blocked_ids = {
            n["node_id"]
            for n in nodes
            if n.get("status") in terminal
        }

        deps: Dict[str, Set[str]] = {}

        for edge in edges:
            deps.setdefault(edge["to_node_id"], set()).add(edge["from_node_id"])

        ready = []

        for node in nodes:
            node_id = node["node_id"]

            if node_id in blocked_ids:
                continue

            required = deps.get(node_id, set())

            if required.issubset(completed):
                ready.append(node)

        return ready

    def _derive_graph_status(self, graph_id: str) -> str:
        nodes = self.list_nodes(graph_id)

        if not nodes:
            return GRAPH_COMPLETED

        statuses = {n.get("status") for n in nodes}

        if NODE_FAILED in statuses:
            return GRAPH_FAILED

        if NODE_BLOCKED in statuses:
            return GRAPH_BLOCKED

        if NODE_APPROVAL_REQUIRED in statuses:
            return GRAPH_APPROVAL_REQUIRED

        if all(s == NODE_COMPLETED for s in statuses):
            return GRAPH_COMPLETED

        if any(s in {NODE_RUNNING, NODE_QUEUED, NODE_READY} for s in statuses):
            return GRAPH_RUNNING

        return GRAPH_RUNNING

    # ========================================================
    # UPDATES
    # ========================================================

    def _update_graph_status(self, graph_id: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE execution_graphs
                SET status=?,
                    updated_at_ms=?
                WHERE graph_id=?
                """,
                (
                    status,
                    _now_ms(),
                    graph_id,
                ),
            )
            conn.commit()

    def _complete_graph_if_terminal(
        self,
        graph_id: str,
        result: GraphExecutionResult,
    ) -> None:
        completed_at = (
            _now_ms()
            if result.status in {
                GRAPH_COMPLETED,
                GRAPH_FAILED,
                GRAPH_BLOCKED,
                GRAPH_APPROVAL_REQUIRED,
            }
            else None
        )

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE execution_graphs
                SET status=?,
                    result_json=?,
                    updated_at_ms=?,
                    completed_at_ms=?
                WHERE graph_id=?
                """,
                (
                    result.status,
                    _json_dumps(result.to_dict()),
                    _now_ms(),
                    completed_at,
                    graph_id,
                ),
            )
            conn.commit()

    def _update_node(
        self,
        node_id: str,
        *,
        status: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        job_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        error: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        current = self._get_node(node_id)

        if not current:
            return

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE execution_graph_nodes
                SET status=?,
                    result_json=?,
                    job_id=?,
                    worker_id=?,
                    updated_at_ms=?,
                    completed_at_ms=?,
                    last_error=?
                WHERE node_id=?
                """,
                (
                    status or current.get("status"),
                    _json_dumps(result) if result is not None else current.get("result_json"),
                    job_id if job_id is not None else current.get("job_id"),
                    worker_id if worker_id is not None else current.get("worker_id"),
                    _now_ms(),
                    _now_ms() if completed else current.get("completed_at_ms"),
                    error if error is not None else current.get("last_error"),
                    node_id,
                ),
            )
            conn.commit()

    def _get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM execution_graph_nodes
                WHERE node_id=?
                LIMIT 1
                """,
                (node_id,),
            ).fetchone()

        return dict(row) if row else None

    # ========================================================
    # EVENTS
    # ========================================================

    def _emit(
        self,
        event_type: str,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="execution_graph_engine",
                severity="INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="execution_graph_engine",
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_GRAPH_ENGINE: Optional[ExecutionGraphEngine] = None


def get_execution_graph_engine(
    *,
    db_path: str = DEFAULT_DB_PATH,
    queue: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> ExecutionGraphEngine:
    global _DEFAULT_GRAPH_ENGINE

    if reset or _DEFAULT_GRAPH_ENGINE is None:
        _DEFAULT_GRAPH_ENGINE = ExecutionGraphEngine(
            db_path=db_path,
            queue=queue,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_GRAPH_ENGINE