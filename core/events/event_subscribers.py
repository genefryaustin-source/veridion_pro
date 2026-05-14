"""
core/events/event_subscribers.py

Event Subscribers / Automation Reactions for Veridion Pro / CUI GovCloud App.

Purpose:
- Convert emitted events into automated orchestration reactions.
- Bridge event_bus, websocket_hub, approval workflows, rollback orchestration,
  case escalation, and execution release.

Examples:
- APPROVAL_APPROVED -> release execution
- ROLLBACK_FAILED -> escalate case
- VERIFICATION_FAILED -> trigger rollback
- SLA_BREACH -> escalate approval/case
- EXECUTION_COMPLETED -> broadcast realtime update

Safe design:
- Defensive imports
- No hard failure if optional modules are unavailable
- Idempotent-ish handlers where possible
- Compatible with both Event dataclass objects and raw dict events
"""

from __future__ import annotations

import json
import time
import traceback
from typing import Any, Callable, Dict, List, Optional


# =============================================================================
# Optional imports
# =============================================================================

try:
    from core.events.event_bus import get_event_bus
except Exception:
    get_event_bus = None

try:
    from core.events.websocket_hub import (
        broadcast_event,
        broadcast_case_event,
        broadcast_approval_event,
        broadcast_execution_event,
    )
except Exception:
    def broadcast_event(*args, **kwargs):  # type: ignore
        return None

    def broadcast_case_event(*args, **kwargs):  # type: ignore
        return None

    def broadcast_approval_event(*args, **kwargs):  # type: ignore
        return None

    def broadcast_execution_event(*args, **kwargs):  # type: ignore
        return None

try:
    from core.runtime.governance_approval_engine import (
        get_governance_approval_engine,
    )
except Exception:
    get_governance_approval_engine = None

try:
    from core.ai.orchestration.rollback_orchestrator import (
        get_rollback_orchestrator,
    )
except Exception:
    get_rollback_orchestrator = None


# =============================================================================
# Event names
# =============================================================================

APPROVAL_REQUEST_CREATED = "APPROVAL_REQUEST_CREATED"
APPROVAL_GRANTED = "APPROVAL_GRANTED"
APPROVAL_REJECTED = "APPROVAL_REJECTED"
APPROVED_EXECUTION_RELEASED = "APPROVED_EXECUTION_RELEASED"
APPROVED_EXECUTION_RELEASE_FAILED = "APPROVED_EXECUTION_RELEASE_FAILED"

GOVERNANCE_ACTION_APPROVED = "GOVERNANCE_ACTION_APPROVED"
GOVERNANCE_ACTION_REJECTED = "GOVERNANCE_ACTION_REJECTED"
GOVERNANCE_OVERRIDE_APPROVED = "GOVERNANCE_OVERRIDE_APPROVED"
GOVERNANCE_EXECUTION_RELEASED = "GOVERNANCE_EXECUTION_RELEASED"

EXECUTION_STARTED = "EXECUTION_STARTED"
EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
EXECUTION_FAILED = "EXECUTION_FAILED"
EXECUTION_VERIFICATION_FAILED = "EXECUTION_VERIFICATION_FAILED"
CONTAINMENT_VERIFICATION_FAILED = "CONTAINMENT_VERIFICATION_FAILED"

ROLLBACK_TRIGGERED = "ROLLBACK_TRIGGERED"
ROLLBACK_STARTED = "ROLLBACK_STARTED"
ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"
ROLLBACK_FAILED = "ROLLBACK_FAILED"
ROLLBACK_VERIFICATION_FAILED = "ROLLBACK_VERIFICATION_FAILED"
ROLLBACK_ESCALATED = "ROLLBACK_ESCALATED"

SLA_BREACH = "SLA_BREACH"
SLA_ESCALATED = "SLA_ESCALATED"

CASE_ESCALATED = "CASE_ESCALATED"
POLICY_VIOLATION = "POLICY_VIOLATION"
AI_ACTION_BLOCKED = "AI_ACTION_BLOCKED"

SEVERITY_INFO = "INFO"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


# =============================================================================
# Helpers
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


def _event_to_dict(event: Any) -> Dict[str, Any]:
    if event is None:
        return {}

    if isinstance(event, dict):
        return event

    if hasattr(event, "to_dict") and callable(event.to_dict):
        try:
            return event.to_dict()
        except Exception:
            pass

    if hasattr(event, "__dict__"):
        try:
            return dict(event.__dict__)
        except Exception:
            pass

    return {"raw": str(event)}


def _payload(event: Any) -> Dict[str, Any]:
    data = _event_to_dict(event)
    payload = data.get("payload") or {}

    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except Exception:
            return {"raw_payload": payload}

    if isinstance(payload, dict):
        return payload

    return {}


def _event_type(event: Any) -> str:
    data = _event_to_dict(event)
    return str(data.get("event_type") or data.get("type") or "").upper()


def _tenant_id(event: Any, payload: Optional[Dict[str, Any]] = None) -> str:
    data = _event_to_dict(event)
    payload = payload or _payload(event)
    return str(
        data.get("tenant_id")
        or payload.get("tenant_id")
        or "default"
    )


def _source(event: Any) -> str:
    data = _event_to_dict(event)
    return str(data.get("source") or "event_subscribers")


def _severity(event: Any, payload: Optional[Dict[str, Any]] = None) -> str:
    data = _event_to_dict(event)
    payload = payload or _payload(event)
    return str(
        data.get("severity")
        or payload.get("severity")
        or SEVERITY_INFO
    ).upper()


def _safe_call(fn: Optional[Callable], *args, **kwargs) -> Any:
    if not callable(fn):
        return None

    try:
        return fn(*args, **kwargs)
    except TypeError:
        try:
            return fn(*args)
        except Exception:
            return None
    except Exception:
        return None


def _get_ledger(storage: Any) -> Any:
    if storage is None:
        return None
    return getattr(storage, "ledger", storage)


def _record_case_event(
    storage: Any,
    *,
    case_id: Any,
    event_type: str,
    actor: str,
    details: Dict[str, Any],
) -> None:
    ledger = _get_ledger(storage)

    if ledger is None or not case_id:
        return

    for method_name in (
        "add_case_event",
        "create_case_event",
        "record_case_event",
        "add_case_timeline_event",
    ):
        method = getattr(ledger, method_name, None)

        if not callable(method):
            continue

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


def _record_custody_event(
    storage: Any,
    *,
    event_type: str,
    actor: str,
    tenant_id: str,
    evidence_id: Any = None,
    case_id: Any = None,
    alert_id: Any = None,
    execution_id: Any = None,
    rollback_id: Any = None,
    approval_id: Any = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    ledger = _get_ledger(storage)
    if ledger is None:
        return

    fn = getattr(ledger, "record_custody_event", None)
    if not callable(fn):
        return

    payload = {
        "tenant_id": tenant_id,
        "case_id": case_id,
        "alert_id": alert_id,
        "execution_id": execution_id,
        "rollback_id": rollback_id,
        "approval_id": approval_id,
        **(details or {}),
    }

    try:
        fn(
            run_id=None,
            evidence_id=evidence_id,
            event_type=event_type,
            actor=actor,
            timestamp_ms=_now_ms(),
            details_json=payload,
        )
    except TypeError:
        try:
            fn(
                None,
                evidence_id,
                event_type,
                actor,
                _now_ms(),
                payload,
            )
        except Exception:
            pass
    except Exception:
        pass


def _update_case_status(
    storage: Any,
    *,
    case_id: Any,
    status: str,
    actor: str,
    reason: str,
) -> None:
    ledger = _get_ledger(storage)

    if ledger is None or not case_id:
        return

    for method_name in (
        "update_case_status",
        "set_case_status",
        "change_case_status",
    ):
        fn = getattr(ledger, method_name, None)
        if not callable(fn):
            continue

        try:
            fn(case_id=case_id, status=status, actor=actor, reason=reason)
            return
        except TypeError:
            try:
                fn(case_id, status)
                return
            except Exception:
                pass
        except Exception:
            pass


def _update_case_severity(
    storage: Any,
    *,
    case_id: Any,
    severity: str,
    actor: str,
    reason: str,
) -> None:
    ledger = _get_ledger(storage)

    if ledger is None or not case_id:
        return

    for method_name in (
        "update_case_severity",
        "set_case_severity",
        "escalate_case",
    ):
        fn = getattr(ledger, method_name, None)
        if not callable(fn):
            continue

        try:
            fn(case_id=case_id, severity=severity, actor=actor, reason=reason)
            return
        except TypeError:
            try:
                fn(case_id, severity)
                return
            except Exception:
                pass
        except Exception:
            pass


def _broadcast_common(event: Any) -> None:
    data = _event_to_dict(event)
    payload = _payload(event)
    evt = _event_type(event)
    tenant = _tenant_id(event, payload)
    severity = _severity(event, payload)
    source = _source(event)

    case_id = payload.get("case_id")
    approval_id = payload.get("approval_id")
    execution_id = payload.get("execution_id")

    try:
        broadcast_event(
            event_type=evt,
            payload=payload,
            tenant_id=tenant,
            source=source,
            severity=severity,
            fanout_tenant=True,
        )
    except Exception:
        pass

    if case_id:
        try:
            broadcast_case_event(
                case_id=case_id,
                event_type=evt,
                payload=payload,
                tenant_id=tenant,
                source=source,
                severity=severity,
            )
        except Exception:
            pass

    if approval_id:
        try:
            broadcast_approval_event(
                approval_id=approval_id,
                event_type=evt,
                payload=payload,
                tenant_id=tenant,
                source=source,
                severity=severity,
            )
        except Exception:
            pass

    if execution_id:
        try:
            broadcast_execution_event(
                execution_id=execution_id,
                event_type=evt,
                payload=payload,
                tenant_id=tenant,
                source=source,
                severity=severity,
            )
        except Exception:
            pass


# =============================================================================
# Subscriber class
# =============================================================================

class EventSubscribers:
    """
    Registers event handlers onto event_bus and performs orchestration reactions.
    """

    def __init__(self, storage: Any = None, event_bus: Any = None) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)

        if event_bus is not None:
            self.event_bus = event_bus
        elif get_event_bus is not None:
            self.event_bus = get_event_bus(storage)
        else:
            self.event_bus = None

        self._registered = False

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self) -> bool:
        if self.event_bus is None:
            return False

        if self._registered:
            return True

        subscribe = getattr(self.event_bus, "subscribe", None)
        if not callable(subscribe):
            return False

        # Realtime fanout for all events.
        _safe_call(subscribe, "*", self.handle_realtime_fanout)

        # Approval workflow.
        for evt in (
            APPROVAL_GRANTED,
            GOVERNANCE_ACTION_APPROVED,
            GOVERNANCE_OVERRIDE_APPROVED,
        ):
            _safe_call(subscribe, evt, self.handle_approval_approved)

        _safe_call(subscribe, APPROVAL_REJECTED, self.handle_approval_rejected)
        _safe_call(subscribe, GOVERNANCE_ACTION_REJECTED, self.handle_approval_rejected)

        # Execution lifecycle.
        _safe_call(subscribe, EXECUTION_COMPLETED, self.handle_execution_completed)
        _safe_call(subscribe, EXECUTION_FAILED, self.handle_execution_failed)

        # Verification failures.
        _safe_call(subscribe, EXECUTION_VERIFICATION_FAILED, self.handle_verification_failed)
        _safe_call(subscribe, CONTAINMENT_VERIFICATION_FAILED, self.handle_verification_failed)

        # Rollback lifecycle.
        _safe_call(subscribe, ROLLBACK_FAILED, self.handle_rollback_failed)
        _safe_call(subscribe, ROLLBACK_VERIFICATION_FAILED, self.handle_rollback_failed)
        _safe_call(subscribe, ROLLBACK_COMPLETED, self.handle_rollback_completed)

        # SLA / policy.
        _safe_call(subscribe, SLA_BREACH, self.handle_sla_breach)
        _safe_call(subscribe, POLICY_VIOLATION, self.handle_policy_violation)
        _safe_call(subscribe, AI_ACTION_BLOCKED, self.handle_policy_violation)

        self._registered = True
        return True

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def handle_realtime_fanout(self, event: Any) -> None:
        _broadcast_common(event)

    def handle_approval_approved(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")
        approval_id = payload.get("approval_id")

        if not approval_id:
            return

        if get_governance_approval_engine is not None:
            engine = get_governance_approval_engine(self.storage, event_bus=self.event_bus)
            _safe_call(engine.release_execution, approval_id, actor=actor)

        _record_custody_event(
            self.storage,
            event_type="EVENT_APPROVAL_RELEASE_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=payload.get("case_id"),
            alert_id=payload.get("alert_id"),
            execution_id=payload.get("execution_id"),
            approval_id=approval_id,
            details={
                "source_event": _event_type(event),
                "payload": payload,
            },
        )

    def handle_approval_rejected(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")

        case_id = payload.get("case_id")
        approval_id = payload.get("approval_id")

        _record_case_event(
            self.storage,
            case_id=case_id,
            event_type="GOVERNANCE_APPROVAL_REJECTED",
            actor=actor,
            details={
                "approval_id": approval_id,
                "payload": payload,
            },
        )

        _record_custody_event(
            self.storage,
            event_type="EVENT_APPROVAL_REJECTED_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=payload.get("execution_id"),
            approval_id=approval_id,
            details=payload,
        )

    def handle_execution_completed(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")
        case_id = payload.get("case_id")
        execution_id = payload.get("execution_id")

        _record_case_event(
            self.storage,
            case_id=case_id,
            event_type="EXECUTION_COMPLETED",
            actor=actor,
            details=payload,
        )

        _record_custody_event(
            self.storage,
            event_type="EVENT_EXECUTION_COMPLETED_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=execution_id,
            details=payload,
        )

    def handle_execution_failed(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")
        case_id = payload.get("case_id")
        execution_id = payload.get("execution_id")

        _record_case_event(
            self.storage,
            case_id=case_id,
            event_type="EXECUTION_FAILED",
            actor=actor,
            details=payload,
        )

        if case_id:
            _update_case_status(
                self.storage,
                case_id=case_id,
                status="ESCALATED",
                actor=actor,
                reason="Execution failed.",
            )

            _update_case_severity(
                self.storage,
                case_id=case_id,
                severity=SEVERITY_HIGH,
                actor=actor,
                reason="Execution failed.",
            )

        _record_custody_event(
            self.storage,
            event_type="EVENT_EXECUTION_FAILED_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=execution_id,
            details=payload,
        )

    def handle_verification_failed(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")

        case_id = payload.get("case_id")
        execution_id = payload.get("execution_id")
        rollback_id = payload.get("rollback_id")

        triggered = False
        error = None

        if get_rollback_orchestrator is not None and rollback_id:
            orchestrator = get_rollback_orchestrator(self.storage)
            result = _safe_call(orchestrator.execute_rollback, rollback_id, actor=actor)
            triggered = bool(getattr(result, "ok", False) or (isinstance(result, dict) and result.get("ok")))

        elif get_rollback_orchestrator is not None:
            error = "No rollback_id available for verification failure."

        _record_case_event(
            self.storage,
            case_id=case_id,
            event_type="VERIFICATION_FAILED_ROLLBACK_ATTEMPTED",
            actor=actor,
            details={
                "execution_id": execution_id,
                "rollback_id": rollback_id,
                "triggered": triggered,
                "error": error,
                "payload": payload,
            },
        )

        _record_custody_event(
            self.storage,
            event_type="EVENT_VERIFICATION_FAILED_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=execution_id,
            rollback_id=rollback_id,
            details={
                "triggered": triggered,
                "error": error,
                "payload": payload,
            },
        )

    def handle_rollback_failed(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")

        case_id = payload.get("case_id")
        rollback_id = payload.get("rollback_id")
        execution_id = payload.get("execution_id")

        if case_id:
            _update_case_status(
                self.storage,
                case_id=case_id,
                status="ROLLBACK_REQUIRED",
                actor=actor,
                reason="Rollback failed or rollback verification failed.",
            )

            _update_case_severity(
                self.storage,
                case_id=case_id,
                severity=SEVERITY_CRITICAL,
                actor=actor,
                reason="Rollback failure requires critical escalation.",
            )

        _record_case_event(
            self.storage,
            case_id=case_id,
            event_type="ROLLBACK_FAILED_ESCALATED",
            actor=actor,
            details=payload,
        )

        _record_custody_event(
            self.storage,
            event_type="EVENT_ROLLBACK_FAILED_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=execution_id,
            rollback_id=rollback_id,
            details=payload,
        )

    def handle_rollback_completed(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")

        _record_case_event(
            self.storage,
            case_id=payload.get("case_id"),
            event_type="ROLLBACK_COMPLETED",
            actor=actor,
            details=payload,
        )

        _record_custody_event(
            self.storage,
            event_type="EVENT_ROLLBACK_COMPLETED_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=payload.get("case_id"),
            alert_id=payload.get("alert_id"),
            execution_id=payload.get("execution_id"),
            rollback_id=payload.get("rollback_id"),
            details=payload,
        )

    def handle_sla_breach(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")

        case_id = payload.get("case_id")

        if case_id:
            _update_case_status(
                self.storage,
                case_id=case_id,
                status="ESCALATED",
                actor=actor,
                reason="SLA breach detected.",
            )

            _record_case_event(
                self.storage,
                case_id=case_id,
                event_type="SLA_BREACH_ESCALATED",
                actor=actor,
                details=payload,
            )

        _record_custody_event(
            self.storage,
            event_type="EVENT_SLA_BREACH_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=payload.get("execution_id"),
            details=payload,
        )

    def handle_policy_violation(self, event: Any) -> None:
        payload = _payload(event)
        tenant = _tenant_id(event, payload)
        actor = str(payload.get("actor") or "event_subscribers")

        case_id = payload.get("case_id")

        _record_case_event(
            self.storage,
            case_id=case_id,
            event_type="POLICY_VIOLATION_ESCALATED",
            actor=actor,
            details=payload,
        )

        _record_custody_event(
            self.storage,
            event_type="EVENT_POLICY_VIOLATION_HANDLED",
            actor=actor,
            tenant_id=tenant,
            evidence_id=payload.get("evidence_id"),
            case_id=case_id,
            alert_id=payload.get("alert_id"),
            execution_id=payload.get("execution_id"),
            approval_id=payload.get("approval_id"),
            details=payload,
        )


# =============================================================================
# Global registration helpers
# =============================================================================

_DEFAULT_SUBSCRIBERS: Optional[EventSubscribers] = None


def register_event_subscribers(storage: Any = None, event_bus: Any = None, reset: bool = False) -> EventSubscribers:
    global _DEFAULT_SUBSCRIBERS

    if reset or _DEFAULT_SUBSCRIBERS is None:
        _DEFAULT_SUBSCRIBERS = EventSubscribers(
            storage=storage,
            event_bus=event_bus,
        )

    _DEFAULT_SUBSCRIBERS.register()
    return _DEFAULT_SUBSCRIBERS


def get_event_subscribers(storage: Any = None, event_bus: Any = None) -> EventSubscribers:
    global _DEFAULT_SUBSCRIBERS

    if _DEFAULT_SUBSCRIBERS is None:
        return register_event_subscribers(storage=storage, event_bus=event_bus)

    return _DEFAULT_SUBSCRIBERS


def dispatch_event(
    event_type: str,
    payload: Optional[Dict[str, Any]] = None,
    *,
    source: str = "event_subscribers",
    tenant_id: str = "default",
    severity: str = SEVERITY_INFO,
    storage: Any = None,
) -> None:
    """
    Compatibility helper for older modules that call dispatch_event directly.
    """

    if get_event_bus is not None:
        try:
            bus = get_event_bus(storage)
            bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source=source,
                severity=severity,
                payload=payload or {},
            )
            return
        except Exception:
            pass

    try:
        broadcast_event(
            event_type=event_type,
            payload=payload or {},
            tenant_id=tenant_id,
            source=source,
            severity=severity,
        )
    except Exception:
        pass