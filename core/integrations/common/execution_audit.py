from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


class ExecutionAudit:
    """
    Central forensic execution audit layer.

    Responsibilities:
    - unified execution IDs
    - adapter execution records
    - approval lineage
    - rollback lineage
    - execution result tracking
    - execution failure tracking
    - realtime execution events
    - searchable execution history

    Every real integration adapter should route execution events here.
    """

    def __init__(
        self,
        *,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
    ):
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates

    # ------------------------------------------------------------------
    # Execution Lifecycle
    # ------------------------------------------------------------------

    def new_execution_id(self) -> str:
        return f"EXEC-{uuid.uuid4().hex[:12].upper()}"

    def record_execution(
        self,
        *,
        action: str,
        adapter: str,
        actor: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        target_id: Optional[str] = None,
        provider_execution_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        approval_type: Optional[str] = None,
        autonomous_policy: Optional[str] = None,
        rollback_available: bool = False,
        rollback_action: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        execution_id = self.new_execution_id()

        record = {
            "execution_id": execution_id,
            "provider_execution_id": provider_execution_id,
            "adapter": adapter,
            "action": action,
            "actor": actor,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "target_id": target_id,
            "status": "STARTED",
            "approval_id": approval_id,
            "approval_type": approval_type,
            "autonomous_policy": autonomous_policy,
            "rollback_available": rollback_available,
            "rollback_action": rollback_action,
            "metadata": metadata or {},
            "started_at_ms": _now_ms(),
            "updated_at_ms": _now_ms(),
        }

        self._persist_execution(record)

        self._record_case_event(
            case_id=case_id,
            event_type="EXECUTION_STARTED",
            actor=actor,
            details=record,
        )

        self._publish(
            event_type="EXECUTION_STARTED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=record,
        )

        return record

    def record_execution_result(
        self,
        *,
        execution_id: str,
        actor: str,
        result: Dict[str, Any],
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        status: str = "COMPLETED",
    ) -> Dict[str, Any]:
        record = {
            "execution_id": execution_id,
            "status": status,
            "result": result,
            "completed_at_ms": _now_ms(),
            "updated_at_ms": _now_ms(),
        }

        self._update_execution(record)

        self._record_case_event(
            case_id=case_id,
            event_type="EXECUTION_COMPLETED",
            actor=actor,
            details=record,
        )

        self._publish(
            event_type="EXECUTION_COMPLETED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=record,
        )

        return record

    def record_execution_failure(
        self,
        *,
        execution_id: str,
        actor: str,
        error: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "execution_id": execution_id,
            "status": "FAILED",
            "error": error,
            "details": details or {},
            "failed_at_ms": _now_ms(),
            "updated_at_ms": _now_ms(),
        }

        self._update_execution(record)

        self._record_case_event(
            case_id=case_id,
            event_type="EXECUTION_FAILED",
            actor=actor,
            details=record,
        )

        self._publish(
            event_type="EXECUTION_FAILED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=record,
        )

        return record

    # ------------------------------------------------------------------
    # Approval Lineage
    # ------------------------------------------------------------------

    def record_approval_reference(
        self,
        *,
        execution_id: str,
        approval_id: str,
        approval_type: str,
        approved_by: Optional[str] = None,
        approval_status: str = "PENDING",
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "execution_audit",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        record = {
            "execution_id": execution_id,
            "approval_id": approval_id,
            "approval_type": approval_type,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "details": details or {},
            "linked_at_ms": _now_ms(),
            "updated_at_ms": _now_ms(),
        }

        self._persist_approval_reference(record)

        self._record_case_event(
            case_id=case_id,
            event_type="EXECUTION_APPROVAL_LINKED",
            actor=actor,
            details=record,
        )

        self._publish(
            event_type="EXECUTION_APPROVAL_LINKED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=record,
        )

        return record

    # ------------------------------------------------------------------
    # Rollback Lineage
    # ------------------------------------------------------------------

    def record_rollback(
        self,
        *,
        execution_id: str,
        rollback_action: Dict[str, Any],
        actor: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        rollback_execution_id: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        status: str = "ROLLBACK_EXECUTED",
    ) -> Dict[str, Any]:
        rollback_execution_id = (
            rollback_execution_id
            or self.new_execution_id()
        )

        record = {
            "execution_id": execution_id,
            "rollback_execution_id": rollback_execution_id,
            "rollback_action": rollback_action,
            "status": status,
            "result": result or {},
            "actor": actor,
            "rolled_back_at_ms": _now_ms(),
            "updated_at_ms": _now_ms(),
        }

        self._persist_rollback(record)

        self._record_case_event(
            case_id=case_id,
            event_type="ROLLBACK_EXECUTED",
            actor=actor,
            details=record,
        )

        self._publish(
            event_type="ROLLBACK_EXECUTED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=record,
        )

        return record

    # ------------------------------------------------------------------
    # Search / Retrieval
    # ------------------------------------------------------------------

    def get_execution(
        self,
        execution_id: str,
    ) -> Optional[Dict[str, Any]]:
        if self.ledger is None:
            return None

        for method_name in [
            "get_execution_record",
            "get_integration_execution",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    result = method(execution_id)
                    return dict(result) if result else None
                except Exception:
                    pass

        try:
            with self.ledger._connect() as con:
                row = con.execute(
                    """
                    SELECT *
                    FROM integration_executions
                    WHERE execution_id = ?
                    LIMIT 1
                    """,
                    (execution_id,),
                ).fetchone()

                return dict(row) if row else None
        except Exception:
            return None

    def search_executions(
        self,
        *,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        adapter: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if self.ledger is None:
            return []

        try:
            query = """
                SELECT *
                FROM integration_executions
                WHERE 1 = 1
            """

            params: List[Any] = []

            if case_id is not None:
                query += " AND case_id = ?"
                params.append(case_id)

            if tenant_id is not None:
                query += " AND tenant_id = ?"
                params.append(tenant_id)

            if adapter is not None:
                query += " AND adapter = ?"
                params.append(adapter)

            if action is not None:
                query += " AND action = ?"
                params.append(action)

            if status is not None:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY started_at_ms DESC LIMIT ?"
            params.append(limit)

            with self.ledger._connect() as con:
                rows = con.execute(query, params).fetchall()
                return [dict(r) for r in rows]

        except Exception:
            return []

    # ------------------------------------------------------------------
    # Persistence Helpers
    # ------------------------------------------------------------------

    def _persist_execution(
        self,
        record: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        for method_name in [
            "record_integration_execution",
            "add_integration_execution",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    method(**record)
                    return
                except TypeError:
                    try:
                        method(record)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT OR REPLACE INTO integration_executions (
                        execution_id,
                        provider_execution_id,
                        adapter,
                        action,
                        actor,
                        case_id,
                        tenant_id,
                        target_id,
                        status,
                        approval_id,
                        approval_type,
                        autonomous_policy,
                        rollback_available,
                        rollback_action_json,
                        metadata_json,
                        started_at_ms,
                        updated_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("execution_id"),
                        record.get("provider_execution_id"),
                        record.get("adapter"),
                        record.get("action"),
                        record.get("actor"),
                        record.get("case_id"),
                        record.get("tenant_id"),
                        record.get("target_id"),
                        record.get("status"),
                        record.get("approval_id"),
                        record.get("approval_type"),
                        record.get("autonomous_policy"),
                        int(bool(record.get("rollback_available"))),
                        json.dumps(record.get("rollback_action")),
                        json.dumps(record.get("metadata")),
                        record.get("started_at_ms"),
                        record.get("updated_at_ms"),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _update_execution(
        self,
        record: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    UPDATE integration_executions
                    SET
                        status = COALESCE(?, status),
                        result_json = COALESCE(?, result_json),
                        error = COALESCE(?, error),
                        completed_at_ms = COALESCE(?, completed_at_ms),
                        failed_at_ms = COALESCE(?, failed_at_ms),
                        updated_at_ms = ?
                    WHERE execution_id = ?
                    """,
                    (
                        record.get("status"),
                        json.dumps(record.get("result"))
                        if "result" in record
                        else None,
                        record.get("error"),
                        record.get("completed_at_ms"),
                        record.get("failed_at_ms"),
                        record.get("updated_at_ms"),
                        record.get("execution_id"),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _persist_approval_reference(
        self,
        record: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT INTO integration_execution_approvals (
                        id,
                        execution_id,
                        approval_id,
                        approval_type,
                        approval_status,
                        approved_by,
                        details_json,
                        linked_at_ms,
                        updated_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"EXAPP-{uuid.uuid4().hex[:12].upper()}",
                        record.get("execution_id"),
                        record.get("approval_id"),
                        record.get("approval_type"),
                        record.get("approval_status"),
                        record.get("approved_by"),
                        json.dumps(record.get("details")),
                        record.get("linked_at_ms"),
                        record.get("updated_at_ms"),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _persist_rollback(
        self,
        record: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT INTO integration_execution_rollbacks (
                        id,
                        execution_id,
                        rollback_execution_id,
                        rollback_action_json,
                        status,
                        result_json,
                        actor,
                        rolled_back_at_ms,
                        updated_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"RBK-{uuid.uuid4().hex[:12].upper()}",
                        record.get("execution_id"),
                        record.get("rollback_execution_id"),
                        json.dumps(record.get("rollback_action")),
                        record.get("status"),
                        json.dumps(record.get("result")),
                        record.get("actor"),
                        record.get("rolled_back_at_ms"),
                        record.get("updated_at_ms"),
                    ),
                )
                con.commit()
        except Exception:
            pass

    def _ensure_tables(self) -> None:
        if self.ledger is None:
            return

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS integration_executions (
                        execution_id TEXT PRIMARY KEY,
                        provider_execution_id TEXT,
                        adapter TEXT,
                        action TEXT,
                        actor TEXT,
                        case_id TEXT,
                        tenant_id TEXT,
                        target_id TEXT,
                        status TEXT,
                        approval_id TEXT,
                        approval_type TEXT,
                        autonomous_policy TEXT,
                        rollback_available INTEGER DEFAULT 0,
                        rollback_action_json TEXT,
                        metadata_json TEXT,
                        result_json TEXT,
                        error TEXT,
                        started_at_ms INTEGER,
                        completed_at_ms INTEGER,
                        failed_at_ms INTEGER,
                        updated_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS integration_execution_approvals (
                        id TEXT PRIMARY KEY,
                        execution_id TEXT,
                        approval_id TEXT,
                        approval_type TEXT,
                        approval_status TEXT,
                        approved_by TEXT,
                        details_json TEXT,
                        linked_at_ms INTEGER,
                        updated_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS integration_execution_rollbacks (
                        id TEXT PRIMARY KEY,
                        execution_id TEXT,
                        rollback_execution_id TEXT,
                        rollback_action_json TEXT,
                        status TEXT,
                        result_json TEXT,
                        actor TEXT,
                        rolled_back_at_ms INTEGER,
                        updated_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_integration_exec_case
                    ON integration_executions(case_id)
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_integration_exec_tenant
                    ON integration_executions(tenant_id)
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_integration_exec_status
                    ON integration_executions(status)
                    """
                )

                con.commit()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _record_case_event(
        self,
        *,
        case_id: Optional[Any],
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        if self.ledger is None or case_id is None:
            return

        for method_name in [
            "add_case_event",
            "create_case_event",
            "record_case_event",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        event_type=event_type,
                        actor=actor,
                        details=details,
                    )
                    return
                except TypeError:
                    try:
                        method(case_id, event_type, actor, details)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

    def _publish(
        self,
        *,
        event_type: str,
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=actor,
                    source="execution_audit",
                )
            except Exception:
                pass

        if self.live_updates is not None and case_id is not None:
            try:
                self.live_updates.broadcast_case_update(
                    case_id=case_id,
                    tenant_id=tenant_id,
                    event_type=event_type,
                    payload=payload,
                    actor=actor,
                )
            except Exception:
                pass