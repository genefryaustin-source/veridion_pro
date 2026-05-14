"""
ui/copilot/governance_action_handlers.py

Centralized governance action orchestration layer.

Purpose:
- Approve governed actions
- Reject governed actions
- Emergency override approvals
- Escalate approvals
- Release approved executions
- Trigger rollback chains
- Publish realtime governance events
- Preserve audit trail consistency

This layer sits between:
    UI → Governance Engines → Runtime Orchestration

Why this matters:
- Prevents UI from directly mutating governance state
- Centralizes audit/event publication
- Ensures rollback + execution release are coordinated
- Allows future websocket/API integration
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, Optional

from core.runtime.governance_approval_engine import (
    get_governance_approval_engine,
)

from core.runtime.rollback_orchestrator import (
    get_rollback_orchestrator,
)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _safe_bool(value: Any) -> bool:
    try:
        return bool(value)
    except Exception:
        return False


def _publish_event(
    event_bus: Any,
    *,
    event_type: str,
    tenant_id: Optional[str],
    payload: Dict[str, Any],
    source: str = "governance_action_handlers",
) -> None:
    if event_bus is None:
        return

    try:
        event_bus.publish(
            event_type=event_type,
            tenant_id=tenant_id or "default",
            source=source,
            payload=payload,
        )

    except TypeError:

        try:
            event_bus.publish(
                event_type=event_type,
                payload=payload,
                tenant_id=tenant_id or "default",
                source=source,
            )

        except Exception:
            pass

    except Exception:
        pass


def _broadcast(
    live_updates: Any,
    *,
    tenant_id: Optional[str],
    event_type: str,
    payload: Dict[str, Any],
    actor: str,
) -> None:
    if live_updates is None:
        return

    try:
        live_updates.broadcast_tenant_update(
            tenant_id=tenant_id or "default",
            event_type=event_type,
            payload=payload,
            actor=actor,
        )

    except Exception:
        pass


def _record_case_event(
    ledger: Any,
    *,
    case_id: Any,
    event_type: str,
    actor: str,
    details: Dict[str, Any],
) -> None:
    if ledger is None or case_id is None:
        return

    for method_name in [
        "add_case_event",
        "create_case_event",
        "record_case_event",
    ]:
        method = getattr(ledger, method_name, None)

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


# ----------------------------------------------------------------------
# Base Context
# ----------------------------------------------------------------------

def _build_context(storage: Any) -> Dict[str, Any]:

    ledger = getattr(storage, "ledger", storage)

    event_bus = getattr(
        storage,
        "event_bus",
        None,
    )

    live_updates = getattr(
        storage,
        "live_updates",
        None,
    )

    approval_engine = get_governance_approval_engine(
        storage,
        event_bus=event_bus,
    )

    rollback_orchestrator = None

    try:
        rollback_orchestrator = (
            get_rollback_orchestrator(storage)
        )

    except Exception:
        rollback_orchestrator = None

    return {
        "ledger": ledger,
        "event_bus": event_bus,
        "live_updates": live_updates,
        "approval_engine": approval_engine,
        "rollback_orchestrator": rollback_orchestrator,
    }

class GovernanceActionHandlers:

    @staticmethod
    def approve(*args, **kwargs):
        return approve_action(*args, **kwargs)

    @staticmethod
    def reject(*args, **kwargs):
        return reject_action(*args, **kwargs)

    @staticmethod
    def override(*args, **kwargs):
        return override_action(*args, **kwargs)

    @staticmethod
    def escalate(*args, **kwargs):
        return escalate_approval(*args, **kwargs)

    @staticmethod
    def release(*args, **kwargs):
        return release_execution(*args, **kwargs)

    @staticmethod
    def rollback(*args, **kwargs):
        return rollback_execution(*args, **kwargs)

    @staticmethod
    def bulk_expire(*args, **kwargs):
        return bulk_expire_pending(*args, **kwargs)

    @staticmethod
    def bulk_escalate(*args, **kwargs):
        return bulk_escalate_pending(*args, **kwargs)
# ----------------------------------------------------------------------
# Approve
# ----------------------------------------------------------------------

def approve_action(
    storage: Any,
    *,
    approval_id: str,
    actor: str,
    reason: str = "",
    legal_approval: bool = False,
    second_approval: bool = False,
    release_execution: bool = True,
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        result = approval_engine.approve(
            approval_id,
            actor=actor,
            reason=reason,
            legal_approval=legal_approval,
            second_approval=second_approval,
            release_execution=release_execution,
        )

        request = approval_engine.get_approval_request(
            approval_id
        ) or {}

        payload = {
            "approval_id": approval_id,
            "actor": actor,
            "reason": reason,
            "legal_approval": legal_approval,
            "second_approval": second_approval,
            "release_execution": release_execution,
            "status": getattr(result, "status", None),
            "approved": getattr(result, "approved", False),
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_ACTION_APPROVED",
            tenant_id=request.get("tenant_id"),
            payload=payload,
        )

        _broadcast(
            ctx["live_updates"],
            tenant_id=request.get("tenant_id"),
            event_type="GOVERNANCE_ACTION_APPROVED",
            payload=payload,
            actor=actor,
        )

        _record_case_event(
            ctx["ledger"],
            case_id=request.get("case_id"),
            event_type="GOVERNANCE_ACTION_APPROVED",
            actor=actor,
            details=payload,
        )

        return {
            "ok": getattr(result, "ok", False),
            "status": getattr(result, "status", None),
            "message": getattr(result, "message", ""),
            "approval_id": approval_id,
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
            "approval_id": approval_id,
        }


# ----------------------------------------------------------------------
# Reject
# ----------------------------------------------------------------------

def reject_action(
    storage: Any,
    *,
    approval_id: str,
    actor: str,
    reason: str,
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        result = approval_engine.reject(
            approval_id,
            actor=actor,
            reason=reason,
        )

        request = approval_engine.get_approval_request(
            approval_id
        ) or {}

        payload = {
            "approval_id": approval_id,
            "actor": actor,
            "reason": reason,
            "status": getattr(result, "status", None),
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_ACTION_REJECTED",
            tenant_id=request.get("tenant_id"),
            payload=payload,
        )

        _broadcast(
            ctx["live_updates"],
            tenant_id=request.get("tenant_id"),
            event_type="GOVERNANCE_ACTION_REJECTED",
            payload=payload,
            actor=actor,
        )

        _record_case_event(
            ctx["ledger"],
            case_id=request.get("case_id"),
            event_type="GOVERNANCE_ACTION_REJECTED",
            actor=actor,
            details=payload,
        )

        return {
            "ok": getattr(result, "ok", False),
            "status": getattr(result, "status", None),
            "message": getattr(result, "message", ""),
            "approval_id": approval_id,
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
            "approval_id": approval_id,
        }


# ----------------------------------------------------------------------
# Emergency Override
# ----------------------------------------------------------------------

def override_action(
    storage: Any,
    *,
    approval_id: str,
    actor: str,
    reason: str,
    release_execution: bool = True,
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        result = approval_engine.emergency_override(
            approval_id,
            actor=actor,
            reason=reason,
            release_execution=release_execution,
        )

        request = approval_engine.get_approval_request(
            approval_id
        ) or {}

        payload = {
            "approval_id": approval_id,
            "actor": actor,
            "reason": reason,
            "release_execution": release_execution,
            "status": getattr(result, "status", None),
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_OVERRIDE_APPROVED",
            tenant_id=request.get("tenant_id"),
            payload=payload,
        )

        _broadcast(
            ctx["live_updates"],
            tenant_id=request.get("tenant_id"),
            event_type="GOVERNANCE_OVERRIDE_APPROVED",
            payload=payload,
            actor=actor,
        )

        _record_case_event(
            ctx["ledger"],
            case_id=request.get("case_id"),
            event_type="GOVERNANCE_OVERRIDE_APPROVED",
            actor=actor,
            details=payload,
        )

        return {
            "ok": getattr(result, "ok", False),
            "status": getattr(result, "status", None),
            "message": getattr(result, "message", ""),
            "approval_id": approval_id,
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
            "approval_id": approval_id,
        }


# ----------------------------------------------------------------------
# Escalate Approval
# ----------------------------------------------------------------------

def escalate_approval(
    storage: Any,
    *,
    approval_id: str,
    actor: str,
    reason: str = "",
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        request = approval_engine.get_approval_request(
            approval_id
        )

        if not request:

            return {
                "ok": False,
                "status": "NOT_FOUND",
                "message": "Approval request not found.",
                "approval_id": approval_id,
            }

        approval_engine._update_approval(
            approval_id,
            {
                "status": "ESCALATED",
            },
        )

        approval_engine._record_approval_event(
            approval_id=approval_id,
            tenant_id=request.get("tenant_id"),
            event_type="APPROVAL_ESCALATED",
            actor=actor,
            message="Approval escalated.",
            details={
                "reason": reason,
            },
        )

        payload = {
            "approval_id": approval_id,
            "actor": actor,
            "reason": reason,
            "status": "ESCALATED",
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_APPROVAL_ESCALATED",
            tenant_id=request.get("tenant_id"),
            payload=payload,
        )

        _broadcast(
            ctx["live_updates"],
            tenant_id=request.get("tenant_id"),
            event_type="GOVERNANCE_APPROVAL_ESCALATED",
            payload=payload,
            actor=actor,
        )

        _record_case_event(
            ctx["ledger"],
            case_id=request.get("case_id"),
            event_type="GOVERNANCE_APPROVAL_ESCALATED",
            actor=actor,
            details=payload,
        )

        return {
            "ok": True,
            "status": "ESCALATED",
            "message": "Approval escalated.",
            "approval_id": approval_id,
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
            "approval_id": approval_id,
        }


# ----------------------------------------------------------------------
# Release Execution
# ----------------------------------------------------------------------

def release_execution(
    storage: Any,
    *,
    approval_id: str,
    actor: str,
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        released = approval_engine.release_execution(
            approval_id,
            actor=actor,
        )

        request = approval_engine.get_approval_request(
            approval_id
        ) or {}

        payload = {
            "approval_id": approval_id,
            "actor": actor,
            "released": released,
            "execution_id": request.get(
                "execution_id"
            ),
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_EXECUTION_RELEASED",
            tenant_id=request.get("tenant_id"),
            payload=payload,
        )

        _broadcast(
            ctx["live_updates"],
            tenant_id=request.get("tenant_id"),
            event_type="GOVERNANCE_EXECUTION_RELEASED",
            payload=payload,
            actor=actor,
        )

        _record_case_event(
            ctx["ledger"],
            case_id=request.get("case_id"),
            event_type="GOVERNANCE_EXECUTION_RELEASED",
            actor=actor,
            details=payload,
        )

        return {
            "ok": released,
            "status": (
                "RELEASED"
                if released
                else "NOT_RELEASED"
            ),
            "message": (
                "Execution released."
                if released
                else "Execution release unavailable."
            ),
            "approval_id": approval_id,
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
            "approval_id": approval_id,
        }


# ----------------------------------------------------------------------
# Rollback
# ----------------------------------------------------------------------

def rollback_execution(
    storage: Any,
    *,
    approval_id: str,
    actor: str,
    reason: str,
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    rollback_orchestrator = ctx[
        "rollback_orchestrator"
    ]

    approval_engine = ctx[
        "approval_engine"
    ]

    try:

        request = approval_engine.get_approval_request(
            approval_id
        ) or {}

        execution_id = request.get(
            "execution_id"
        )

        if not execution_id:

            return {
                "ok": False,
                "status": "NO_EXECUTION",
                "message": (
                    "Approval has no execution_id."
                ),
                "approval_id": approval_id,
            }

        if rollback_orchestrator is None:

            return {
                "ok": False,
                "status": "ROLLBACK_UNAVAILABLE",
                "message": (
                    "Rollback orchestrator unavailable."
                ),
                "approval_id": approval_id,
            }

        rollback_result = (
            rollback_orchestrator.execute_rollback(
                execution_id=execution_id,
                actor=actor,
                reason=reason,
            )
        )

        payload = {
            "approval_id": approval_id,
            "execution_id": execution_id,
            "actor": actor,
            "reason": reason,
            "rollback_result": rollback_result,
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_ROLLBACK_TRIGGERED",
            tenant_id=request.get("tenant_id"),
            payload=payload,
        )

        _broadcast(
            ctx["live_updates"],
            tenant_id=request.get("tenant_id"),
            event_type="GOVERNANCE_ROLLBACK_TRIGGERED",
            payload=payload,
            actor=actor,
        )

        _record_case_event(
            ctx["ledger"],
            case_id=request.get("case_id"),
            event_type="GOVERNANCE_ROLLBACK_TRIGGERED",
            actor=actor,
            details=payload,
        )

        return {
            "ok": True,
            "status": "ROLLBACK_TRIGGERED",
            "message": (
                "Rollback execution triggered."
            ),
            "approval_id": approval_id,
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
            "approval_id": approval_id,
        }


# ----------------------------------------------------------------------
# Bulk Actions
# ----------------------------------------------------------------------

def bulk_expire_pending(
    storage: Any,
    *,
    tenant_id: Optional[str] = None,
    actor: str = "governance_action_handlers",
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        rows = approval_engine.expire_stale_approvals(
            tenant_id=tenant_id,
            actor=actor,
        )

        payload = {
            "expired_count": len(rows),
            "tenant_id": tenant_id,
            "actor": actor,
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_BULK_EXPIRE",
            tenant_id=tenant_id,
            payload=payload,
        )

        return {
            "ok": True,
            "status": "COMPLETE",
            "message": (
                f"Expired {len(rows)} approvals."
            ),
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
        }


def bulk_escalate_pending(
    storage: Any,
    *,
    tenant_id: Optional[str] = None,
    actor: str = "governance_action_handlers",
) -> Dict[str, Any]:

    ctx = _build_context(storage)

    approval_engine = ctx["approval_engine"]

    try:

        rows = approval_engine.escalate_pending_approvals(
            tenant_id=tenant_id,
            actor=actor,
        )

        payload = {
            "escalated_count": len(rows),
            "tenant_id": tenant_id,
            "actor": actor,
        }

        _publish_event(
            ctx["event_bus"],
            event_type="GOVERNANCE_BULK_ESCALATE",
            tenant_id=tenant_id,
            payload=payload,
        )

        return {
            "ok": True,
            "status": "COMPLETE",
            "message": (
                f"Escalated {len(rows)} approvals."
            ),
            "payload": payload,
        }

    except Exception as exc:

        traceback.print_exc()

        return {
            "ok": False,
            "status": "ERROR",
            "message": str(exc),
        }