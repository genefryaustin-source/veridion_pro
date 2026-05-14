from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class RollbackManager:
    """
    Central orchestration rollback manager.

    Responsibilities:
    - rollback chains
    - rollback dependency trees
    - containment reversal
    - identity restoration
    - mailbox restoration
    - endpoint release
    - orchestration recovery
    - rollback lineage tracking

    Integrates directly with:
    - ExecutionAudit
    - ApprovalGate
    - ContainmentEngine
    - Integration adapters
    """

    REVERSAL_ACTIONS = {
        "DISABLE_USER": "ENABLE_USER",
        "SUSPEND_USER": "UNSUSPEND_USER",
        "DEACTIVATE_USER": "ENABLE_USER",
        "ISOLATE_ENDPOINT": "RELEASE_ENDPOINT",
        "REMOTE_LOCK": "UNLOCK_DEVICE",
        "QUARANTINE_MAILBOX": "RESTORE_MAILBOX",
        "MOVE_MESSAGE_TO_JUNK": "RESTORE_MESSAGE",
        "RETIRE_DEVICE": "RESTORE_DEVICE",
        "PURGE_MESSAGE": "RESTORE_MESSAGE",
    }

    def __init__(
        self,
        *,
        ledger: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        execution_audit: Any = None,
        adapters: Optional[Dict[str, Any]] = None,
    ):
        self.ledger = ledger
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.execution_audit = execution_audit
        self.adapters = adapters or {}

    # ------------------------------------------------------------------
    # Rollback Planning
    # ------------------------------------------------------------------

    def build_rollback_plan(
        self,
        *,
        execution_id: str,
        action: str,
        adapter: str,
        target_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        rollback_id = (
            f"RBPLAN-{uuid.uuid4().hex[:12].upper()}"
        )

        reverse_action = self.REVERSAL_ACTIONS.get(
            _upper(action)
        )

        reversible = reverse_action is not None

        rollback_action = {
            "action": reverse_action,
            "adapter": adapter,
            "target_id": target_id,
            "metadata": metadata or {},
        }

        dependency_tree = (
            dependencies or []
        )

        plan = {
            "rollback_plan_id": rollback_id,
            "execution_id": execution_id,
            "original_action": action,
            "reverse_action": reverse_action,
            "adapter": adapter,
            "target_id": target_id,
            "reversible": reversible,
            "rollback_action": rollback_action,
            "dependency_tree": dependency_tree,
            "created_at_ms": _now_ms(),
        }

        self._persist_plan(plan)

        return plan

    # ------------------------------------------------------------------
    # Rollback Execution
    # ------------------------------------------------------------------

    def execute_rollback(
        self,
        *,
        rollback_plan_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        actor: str = "rollback_manager",
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        plan = None

        if rollback_plan_id:
            plan = self.get_rollback_plan(
                rollback_plan_id=rollback_plan_id
            )

        elif execution_id:
            plan = self.get_rollback_plan_by_execution(
                execution_id=execution_id
            )

        if not plan:
            return {
                "status": "failed",
                "error": "Rollback plan not found.",
                "timestamp_ms": _now_ms(),
            }

        if not plan.get("reversible"):
            return {
                "status": "failed",
                "error": "Execution is not reversible.",
                "plan": plan,
                "timestamp_ms": _now_ms(),
            }

        adapter_name = plan.get("adapter")
        reverse_action = _upper(
            plan.get("reverse_action")
        )

        adapter = self.adapters.get(
            adapter_name
        )

        if adapter is None:
            return {
                "status": "failed",
                "error": f"Adapter not registered: {adapter_name}",
                "timestamp_ms": _now_ms(),
            }

        method_name = self._resolve_method_name(
            reverse_action
        )

        method = getattr(
            adapter,
            method_name,
            None,
        )

        if not callable(method):
            return {
                "status": "failed",
                "error": (
                    f"Rollback method not found: "
                    f"{method_name}"
                ),
                "timestamp_ms": _now_ms(),
            }

        rollback_execution_id = (
            f"RBEXEC-{uuid.uuid4().hex[:12].upper()}"
        )

        details = {
            "rollback_execution_id": rollback_execution_id,
            "rollback_plan_id": plan.get(
                "rollback_plan_id"
            ),
            "execution_id": plan.get(
                "execution_id"
            ),
            "reverse_action": reverse_action,
            "adapter": adapter_name,
            "target_id": plan.get(
                "target_id"
            ),
            "actor": actor,
            "dry_run": dry_run,
            "started_at_ms": _now_ms(),
        }

        self._record_event(
            case_id=case_id,
            event_type="ROLLBACK_STARTED",
            actor=actor,
            details=details,
        )

        self._publish(
            event_type="ROLLBACK_STARTED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload=details,
        )

        try:
            if dry_run:
                result = {
                    "status": "dry_run",
                    "rollback_execution_id": rollback_execution_id,
                    "plan": plan,
                    "timestamp_ms": _now_ms(),
                }

            else:
                target_id = plan.get("target_id")

                kwargs = self._build_method_kwargs(
                    reverse_action=reverse_action,
                    target_id=target_id,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=actor,
                )

                adapter_result = method(**kwargs)

                result = {
                    "status": "completed",
                    "rollback_execution_id": rollback_execution_id,
                    "adapter_result": adapter_result,
                    "plan": plan,
                    "completed_at_ms": _now_ms(),
                }

            self._persist_rollback_execution(
                result
            )

            if self.execution_audit is not None:
                try:
                    self.execution_audit.record_rollback(
                        execution_id=plan.get(
                            "execution_id"
                        ),
                        rollback_execution_id=rollback_execution_id,
                        rollback_action=plan.get(
                            "rollback_action"
                        ),
                        actor=actor,
                        case_id=case_id,
                        tenant_id=tenant_id,
                        result=result,
                    )
                except Exception:
                    pass

            self._record_event(
                case_id=case_id,
                event_type="ROLLBACK_COMPLETED",
                actor=actor,
                details=result,
            )

            self._publish(
                event_type="ROLLBACK_COMPLETED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=result,
            )

            return result

        except Exception as exc:
            failure = {
                "status": "failed",
                "rollback_execution_id": rollback_execution_id,
                "error": str(exc),
                "plan": plan,
                "failed_at_ms": _now_ms(),
            }

            self._record_event(
                case_id=case_id,
                event_type="ROLLBACK_FAILED",
                actor=actor,
                details=failure,
            )

            self._publish(
                event_type="ROLLBACK_FAILED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=failure,
            )

            return failure

    # ------------------------------------------------------------------
    # Dependency Trees
    # ------------------------------------------------------------------

    def build_dependency_tree(
        self,
        *,
        actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        tree_id = (
            f"RBTREE-{uuid.uuid4().hex[:12].upper()}"
        )

        nodes = []

        for idx, action in enumerate(actions):
            nodes.append(
                {
                    "node_id": (
                        f"NODE-{idx + 1}"
                    ),
                    "action": action.get(
                        "action"
                    ),
                    "adapter": action.get(
                        "adapter"
                    ),
                    "depends_on": action.get(
                        "depends_on",
                        [],
                    ),
                    "rollback_action": self.REVERSAL_ACTIONS.get(
                        _upper(
                            action.get(
                                "action"
                            )
                        )
                    ),
                }
            )

        return {
            "tree_id": tree_id,
            "nodes": nodes,
            "created_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Recovery Workflows
    # ------------------------------------------------------------------

    def recover_identity_access(
        self,
        *,
        user_id: str,
        adapter: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "rollback_manager",
    ) -> Dict[str, Any]:
        return self.execute_manual_reversal(
            action="ENABLE_USER",
            adapter=adapter,
            target_id=user_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
        )

    def recover_endpoint(
        self,
        *,
        device_id: str,
        adapter: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "rollback_manager",
    ) -> Dict[str, Any]:
        return self.execute_manual_reversal(
            action="RELEASE_ENDPOINT",
            adapter=adapter,
            target_id=device_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
        )

    def recover_mailbox(
        self,
        *,
        mailbox_id: str,
        adapter: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "rollback_manager",
    ) -> Dict[str, Any]:
        return self.execute_manual_reversal(
            action="RESTORE_MAILBOX",
            adapter=adapter,
            target_id=mailbox_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
        )

    # ------------------------------------------------------------------
    # Manual Reversal
    # ------------------------------------------------------------------

    def execute_manual_reversal(
        self,
        *,
        action: str,
        adapter: str,
        target_id: str,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        actor: str = "rollback_manager",
    ) -> Dict[str, Any]:
        adapter_obj = self.adapters.get(
            adapter
        )

        if adapter_obj is None:
            return {
                "status": "failed",
                "error": f"Adapter not registered: {adapter}",
            }

        method_name = self._resolve_method_name(
            action
        )

        method = getattr(
            adapter_obj,
            method_name,
            None,
        )

        if not callable(method):
            return {
                "status": "failed",
                "error": (
                    f"Reverse method not found: "
                    f"{method_name}"
                ),
            }

        kwargs = self._build_method_kwargs(
            reverse_action=action,
            target_id=target_id,
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
        )

        try:
            result = method(**kwargs)

            payload = {
                "status": "completed",
                "action": action,
                "adapter": adapter,
                "target_id": target_id,
                "result": result,
                "timestamp_ms": _now_ms(),
            }

            self._publish(
                event_type="MANUAL_ROLLBACK_COMPLETED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload=payload,
            )

            return payload

        except Exception as exc:
            return {
                "status": "failed",
                "error": str(exc),
                "timestamp_ms": _now_ms(),
            }

    # ------------------------------------------------------------------
    # Plan Retrieval
    # ------------------------------------------------------------------

    def get_rollback_plan(
        self,
        *,
        rollback_plan_id: str,
    ) -> Optional[Dict[str, Any]]:
        if self.ledger is None:
            return None

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                row = con.execute(
                    """
                    SELECT *
                    FROM rollback_plans
                    WHERE rollback_plan_id = ?
                    LIMIT 1
                    """,
                    (rollback_plan_id,),
                ).fetchone()

                return dict(row) if row else None

        except Exception:
            return None

    def get_rollback_plan_by_execution(
        self,
        *,
        execution_id: str,
    ) -> Optional[Dict[str, Any]]:
        if self.ledger is None:
            return None

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                row = con.execute(
                    """
                    SELECT *
                    FROM rollback_plans
                    WHERE execution_id = ?
                    LIMIT 1
                    """,
                    (execution_id,),
                ).fetchone()

                return dict(row) if row else None

        except Exception:
            return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_plan(
        self,
        plan: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT INTO rollback_plans (
                        rollback_plan_id,
                        execution_id,
                        original_action,
                        reverse_action,
                        adapter,
                        target_id,
                        reversible,
                        rollback_action_json,
                        dependency_tree_json,
                        created_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        plan.get(
                            "rollback_plan_id"
                        ),
                        plan.get(
                            "execution_id"
                        ),
                        plan.get(
                            "original_action"
                        ),
                        plan.get(
                            "reverse_action"
                        ),
                        plan.get("adapter"),
                        plan.get("target_id"),
                        int(
                            bool(
                                plan.get(
                                    "reversible"
                                )
                            )
                        ),
                        json.dumps(
                            plan.get(
                                "rollback_action"
                            )
                        ),
                        json.dumps(
                            plan.get(
                                "dependency_tree"
                            )
                        ),
                        plan.get(
                            "created_at_ms"
                        ),
                    ),
                )

                con.commit()

        except Exception:
            pass

    def _persist_rollback_execution(
        self,
        payload: Dict[str, Any],
    ) -> None:
        if self.ledger is None:
            return

        self._ensure_tables()

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    INSERT INTO rollback_executions (
                        rollback_execution_id,
                        payload_json,
                        created_at_ms
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        payload.get(
                            "rollback_execution_id"
                        ),
                        json.dumps(payload),
                        _now_ms(),
                    ),
                )

                con.commit()

        except Exception:
            pass

    def _ensure_tables(
        self,
    ) -> None:
        if self.ledger is None:
            return

        try:
            with self.ledger._connect() as con:
                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rollback_plans (
                        rollback_plan_id TEXT PRIMARY KEY,
                        execution_id TEXT,
                        original_action TEXT,
                        reverse_action TEXT,
                        adapter TEXT,
                        target_id TEXT,
                        reversible INTEGER DEFAULT 0,
                        rollback_action_json TEXT,
                        dependency_tree_json TEXT,
                        created_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rollback_executions (
                        rollback_execution_id TEXT PRIMARY KEY,
                        payload_json TEXT,
                        created_at_ms INTEGER
                    )
                    """
                )

                con.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_rollback_execution
                    ON rollback_plans(execution_id)
                    """
                )

                con.commit()

        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_method_name(
        self,
        action: str,
    ) -> str:
        mapping = {
            "ENABLE_USER": "enable_user",
            "UNSUSPEND_USER": "unsuspend_user",
            "RELEASE_ENDPOINT": "release_endpoint",
            "UNLOCK_DEVICE": "unlock_device",
            "RESTORE_MAILBOX": "restore_mailbox",
            "RESTORE_MESSAGE": "restore_message",
            "RESTORE_DEVICE": "restore_device",
        }

        return mapping.get(
            _upper(action),
            str(action).lower(),
        )

    def _build_method_kwargs(
        self,
        *,
        reverse_action: str,
        target_id: Optional[str],
        case_id: Optional[Any],
        tenant_id: Optional[str],
        actor: str,
    ) -> Dict[str, Any]:
        reverse_action = _upper(reverse_action)

        kwargs = {
            "case_id": case_id,
            "tenant_id": tenant_id,
            "actor": actor,
            "reason": "RollbackManager execution",
            "dry_run": False,
        }

        if reverse_action in {
            "ENABLE_USER",
            "UNSUSPEND_USER",
        }:
            kwargs["user_id"] = target_id

        elif reverse_action in {
            "RELEASE_ENDPOINT",
            "UNLOCK_DEVICE",
            "RESTORE_DEVICE",
        }:
            kwargs["device_id"] = target_id

        elif reverse_action in {
            "RESTORE_MAILBOX",
        }:
            kwargs["mailbox_id"] = target_id

        elif reverse_action in {
            "RESTORE_MESSAGE",
        }:
            kwargs["message_id"] = target_id

        return kwargs

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _record_event(
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
            method = getattr(
                self.ledger,
                method_name,
                None,
            )

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
                        method(
                            case_id,
                            event_type,
                            actor,
                            details,
                        )
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
                    source="rollback_manager",
                )
            except Exception:
                pass

        if self.live_updates is not None:
            try:
                if case_id is not None:
                    self.live_updates.broadcast_case_update(
                        case_id=case_id,
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload=payload,
                        actor=actor,
                    )
                elif tenant_id is not None:
                    self.live_updates.broadcast_tenant_update(
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload=payload,
                        actor=actor,
                    )
            except Exception:
                pass