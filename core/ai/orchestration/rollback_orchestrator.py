"""
core/ai/orchestration/rollback_orchestrator.py

Rollback Orchestrator for Veridion Pro / CUI GovCloud App.

Purpose:
- Execute rollback chains
- Verify rollback success
- Recover failed containment actions
- Handle staged rollback workflows
- Escalate failed rollback conditions
- Preserve forensic auditability

This is a GOVERNANCE-SAFE rollback layer:
- no direct destructive execution outside plugins
- all rollback actions are evented + auditable
- rollback verification is mandatory
- rollback escalation paths are built-in
"""

from __future__ import annotations

import json
import time
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.ai.orchestration.action_plugins import (
    get_action_plugin_registry,
)

from core.events.event_bus import (
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    POLICY_VIOLATION,
    ROLLBACK_COMPLETED,
    ROLLBACK_ESCALATED,
    ROLLBACK_FAILED,
    ROLLBACK_STARTED,
    ROLLBACK_VERIFICATION_FAILED,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_INFO,
    SEVERITY_MEDIUM,
    get_event_bus,
)

from core.runtime.execution_state_store import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_RUNNING,
    ExecutionStateStore,
)


# =============================================================================
# Constants
# =============================================================================

ROLLBACK_SOURCE = "rollback_orchestrator"

ROLLBACK_STATUS_READY = "READY"
ROLLBACK_STATUS_RUNNING = "RUNNING"
ROLLBACK_STATUS_COMPLETED = "COMPLETED"
ROLLBACK_STATUS_FAILED = "FAILED"
ROLLBACK_STATUS_ESCALATED = "ESCALATED"

MAX_ROLLBACK_ATTEMPTS = 3


# =============================================================================
# Helpers
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_json_loads(
    value: Any,
    default: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    if default is None:
        default = {}

    if value is None:
        return default

    if isinstance(value, dict):
        return value

    try:
        return json.loads(value)
    except Exception:
        return default


def _safe_json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


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


def _get_ledger(storage: Any):
    if storage is None:
        return None

    return getattr(storage, "ledger", storage)


def _record_custody_event(
    storage: Any,
    *,
    event_type: str,
    actor: str,
    tenant_id: str,
    execution_id: Optional[str] = None,
    rollback_id: Optional[str] = None,
    evidence_id: Optional[str] = None,
    case_id: Optional[str] = None,
    alert_id: Optional[str] = None,
    run_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:

    ledger = _get_ledger(storage)

    if ledger is None:
        return

    method = getattr(ledger, "record_custody_event", None)

    if not callable(method):
        return

    payload = {
        "execution_id": execution_id,
        "rollback_id": rollback_id,
        "case_id": case_id,
        "alert_id": alert_id,
        **(details or {}),
    }

    try:

        method(
            run_id=run_id,
            evidence_id=evidence_id,
            event_type=event_type,
            actor=actor,
            timestamp_ms=_now_ms(),
            details_json=payload,
        )

    except TypeError:

        try:
            method(
                run_id,
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


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class RollbackExecutionResult:
    ok: bool

    rollback_id: str
    execution_id: str

    action: str
    status: str

    plugin_id: Optional[str] = None

    message: str = ""

    verification_ok: bool = False
    escalation_required: bool = False

    attempts: int = 0

    details: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=_now_ms)


# =============================================================================
# Rollback Orchestrator
# =============================================================================

class RollbackOrchestrator:

    def __init__(
        self,
        storage: Any = None,
    ) -> None:

        self.storage = storage

        self.event_bus = get_event_bus(storage)

        self.state_store = ExecutionStateStore(storage)

        self.plugin_registry = get_action_plugin_registry()

    # -------------------------------------------------------------------------
    # MAIN ENTRYPOINT
    # -------------------------------------------------------------------------

    def execute_rollback(
        self,
        rollback_id: str,
        *,
        actor: str = ROLLBACK_SOURCE,
    ) -> RollbackExecutionResult:

        rollback = self.state_store.get_rollback_chain(
            rollback_id=rollback_id,
        )

        if not rollback:

            return RollbackExecutionResult(
                ok=False,
                rollback_id=rollback_id,
                execution_id="UNKNOWN",
                action="UNKNOWN",
                status=ROLLBACK_STATUS_FAILED,
                message="Rollback chain not found.",
            )

        execution_id = rollback.get("execution_id")

        payload = _safe_json_loads(
            rollback.get("payload_json"),
        )

        action = _safe_str(payload.get("action"))

        tenant_id = _safe_str(
            rollback.get("tenant_id"),
            "default",
        )

        attempts = _safe_int(
            rollback.get("attempts"),
            0,
        )

        self.event_bus.publish(
            event_type=ROLLBACK_STARTED,
            tenant_id=tenant_id,
            source=ROLLBACK_SOURCE,
            severity=SEVERITY_MEDIUM,
            payload={
                "rollback_id": rollback_id,
                "execution_id": execution_id,
                "action": action,
                "attempt": attempts + 1,
            },
        )

        _record_custody_event(
            self.storage,
            event_type="ROLLBACK_STARTED",
            actor=actor,
            tenant_id=tenant_id,
            execution_id=execution_id,
            rollback_id=rollback_id,
            details={
                "action": action,
                "attempt": attempts + 1,
            },
        )

        self.state_store.update_rollback_chain(
            rollback_id=rollback_id,
            status=ROLLBACK_STATUS_RUNNING,
            attempts=attempts + 1,
        )

        plugin = self.plugin_registry.get_plugin_for_action(
            action,
        )

        if not plugin:

            return self._fail_rollback(
                rollback_id=rollback_id,
                execution_id=execution_id,
                action=action,
                tenant_id=tenant_id,
                message=f"No plugin registered for rollback action: {action}",
            )

        try:

            rollback_result = plugin.rollback(payload)

            if not rollback_result.ok:

                return self._fail_rollback(
                    rollback_id=rollback_id,
                    execution_id=execution_id,
                    action=action,
                    tenant_id=tenant_id,
                    message=rollback_result.message,
                    details=asdict(rollback_result),
                )

            verification = plugin.verify(payload)

            if not verification.ok:

                return self._verification_failed(
                    rollback_id=rollback_id,
                    execution_id=execution_id,
                    action=action,
                    tenant_id=tenant_id,
                    message=verification.message,
                    details=asdict(verification),
                )

            self.state_store.update_rollback_chain(
                rollback_id=rollback_id,
                status=ROLLBACK_STATUS_COMPLETED,
                completed_at_ms=_now_ms(),
                details={
                    "rollback_result": asdict(rollback_result),
                    "verification": asdict(verification),
                },
            )

            self.event_bus.publish(
                event_type=ROLLBACK_COMPLETED,
                tenant_id=tenant_id,
                source=ROLLBACK_SOURCE,
                severity=SEVERITY_INFO,
                payload={
                    "rollback_id": rollback_id,
                    "execution_id": execution_id,
                    "action": action,
                    "message": rollback_result.message,
                },
            )

            _record_custody_event(
                self.storage,
                event_type="ROLLBACK_COMPLETED",
                actor=actor,
                tenant_id=tenant_id,
                execution_id=execution_id,
                rollback_id=rollback_id,
                details={
                    "rollback_result": asdict(rollback_result),
                    "verification": asdict(verification),
                },
            )

            return RollbackExecutionResult(
                ok=True,
                rollback_id=rollback_id,
                execution_id=execution_id,
                action=action,
                plugin_id=plugin.plugin_id,
                status=ROLLBACK_STATUS_COMPLETED,
                message=rollback_result.message,
                verification_ok=True,
                attempts=attempts + 1,
                details={
                    "rollback_result": asdict(rollback_result),
                    "verification": asdict(verification),
                },
            )

        except Exception as exc:

            traceback.print_exc()

            return self._fail_rollback(
                rollback_id=rollback_id,
                execution_id=execution_id,
                action=action,
                tenant_id=tenant_id,
                message=str(exc),
                details={
                    "traceback": traceback.format_exc(),
                },
            )

    # -------------------------------------------------------------------------
    # STAGED ROLLBACK EXECUTION
    # -------------------------------------------------------------------------

    def execute_rollback_chain(
        self,
        rollback_ids: List[str],
        *,
        actor: str = ROLLBACK_SOURCE,
    ) -> List[RollbackExecutionResult]:

        results = []

        for rollback_id in rollback_ids:

            result = self.execute_rollback(
                rollback_id,
                actor=actor,
            )

            results.append(result)

            if not result.ok:

                self.event_bus.publish(
                    event_type=ROLLBACK_ESCALATED,
                    tenant_id="default",
                    source=ROLLBACK_SOURCE,
                    severity=SEVERITY_HIGH,
                    payload={
                        "rollback_id": rollback_id,
                        "execution_id": result.execution_id,
                        "message": "Rollback chain escalation triggered.",
                    },
                )

                break

        return results

    # -------------------------------------------------------------------------
    # FAILED CONTAINMENT RECOVERY
    # -------------------------------------------------------------------------

    def recover_failed_containment(
        self,
        *,
        max_attempts: int = MAX_ROLLBACK_ATTEMPTS,
    ) -> List[RollbackExecutionResult]:

        pending = self.state_store.list_failed_rollbacks(
            max_attempts=max_attempts,
        )

        results = []

        for rollback in pending:

            rollback_id = rollback.get("rollback_id")

            if not rollback_id:
                continue

            result = self.execute_rollback(
                rollback_id,
            )

            results.append(result)

        return results

    # -------------------------------------------------------------------------
    # ROLLBACK GOVERNANCE ESCALATION
    # -------------------------------------------------------------------------

    def escalate_failed_rollback(
        self,
        rollback_id: str,
        *,
        reason: str,
        actor: str = ROLLBACK_SOURCE,
    ) -> None:

        rollback = self.state_store.get_rollback_chain(
            rollback_id=rollback_id,
        )

        if not rollback:
            return

        execution_id = rollback.get("execution_id")

        tenant_id = rollback.get("tenant_id") or "default"

        self.state_store.update_rollback_chain(
            rollback_id=rollback_id,
            status=ROLLBACK_STATUS_ESCALATED,
            escalation_reason=reason,
        )

        self.event_bus.publish(
            event_type=ROLLBACK_ESCALATED,
            tenant_id=tenant_id,
            source=ROLLBACK_SOURCE,
            severity=SEVERITY_CRITICAL,
            payload={
                "rollback_id": rollback_id,
                "execution_id": execution_id,
                "reason": reason,
            },
        )

        _record_custody_event(
            self.storage,
            event_type="ROLLBACK_ESCALATED",
            actor=actor,
            tenant_id=tenant_id,
            execution_id=execution_id,
            rollback_id=rollback_id,
            details={
                "reason": reason,
            },
        )

    # -------------------------------------------------------------------------
    # INTERNAL FAILURE HANDLERS
    # -------------------------------------------------------------------------

    def _verification_failed(
        self,
        *,
        rollback_id: str,
        execution_id: str,
        action: str,
        tenant_id: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> RollbackExecutionResult:

        self.state_store.update_rollback_chain(
            rollback_id=rollback_id,
            status=ROLLBACK_STATUS_FAILED,
            last_error=message,
        )

        self.event_bus.publish(
            event_type=ROLLBACK_VERIFICATION_FAILED,
            tenant_id=tenant_id,
            source=ROLLBACK_SOURCE,
            severity=SEVERITY_HIGH,
            payload={
                "rollback_id": rollback_id,
                "execution_id": execution_id,
                "action": action,
                "message": message,
            },
        )

        return RollbackExecutionResult(
            ok=False,
            rollback_id=rollback_id,
            execution_id=execution_id,
            action=action,
            status=ROLLBACK_STATUS_FAILED,
            verification_ok=False,
            escalation_required=True,
            message=message,
            details=details or {},
        )

    def _fail_rollback(
        self,
        *,
        rollback_id: str,
        execution_id: str,
        action: str,
        tenant_id: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> RollbackExecutionResult:

        self.state_store.update_rollback_chain(
            rollback_id=rollback_id,
            status=ROLLBACK_STATUS_FAILED,
            last_error=message,
        )

        self.event_bus.publish(
            event_type=ROLLBACK_FAILED,
            tenant_id=tenant_id,
            source=ROLLBACK_SOURCE,
            severity=SEVERITY_HIGH,
            payload={
                "rollback_id": rollback_id,
                "execution_id": execution_id,
                "action": action,
                "message": message,
            },
        )

        return RollbackExecutionResult(
            ok=False,
            rollback_id=rollback_id,
            execution_id=execution_id,
            action=action,
            status=ROLLBACK_STATUS_FAILED,
            verification_ok=False,
            escalation_required=True,
            message=message,
            details=details or {},
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def get_rollback_orchestrator(
    storage: Any = None,
) -> RollbackOrchestrator:

    return RollbackOrchestrator(
        storage=storage,
    )


def execute_rollback(
    storage: Any,
    rollback_id: str,
    *,
    actor: str = ROLLBACK_SOURCE,
) -> RollbackExecutionResult:

    orchestrator = get_rollback_orchestrator(
        storage,
    )

    return orchestrator.execute_rollback(
        rollback_id,
        actor=actor,
    )


def execute_rollback_chain(
    storage: Any,
    rollback_ids: List[str],
    *,
    actor: str = ROLLBACK_SOURCE,
) -> List[RollbackExecutionResult]:

    orchestrator = get_rollback_orchestrator(
        storage,
    )

    return orchestrator.execute_rollback_chain(
        rollback_ids,
        actor=actor,
    )


def recover_failed_containment(
    storage: Any,
    *,
    max_attempts: int = MAX_ROLLBACK_ATTEMPTS,
) -> List[RollbackExecutionResult]:

    orchestrator = get_rollback_orchestrator(
        storage,
    )

    return orchestrator.recover_failed_containment(
        max_attempts=max_attempts,
    )