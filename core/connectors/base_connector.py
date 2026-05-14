"""
core/connectors/base_connector.py

Base connector framework for Veridion Pro / CUI GovCloud App.

Purpose:
- Standard contract for real execution connectors
- Auth lifecycle
- Capability declaration
- Safe execution wrapper
- Verification hooks
- Rollback hooks
- Blast-radius estimation
- Event publishing
- Audit-friendly execution results

All real connectors should inherit from BaseConnector.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from core.runtime.execution_verifier import (
    schedule_verification,
)
from core.runtime.safety_guardrails import check_action_safety

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_VERIFICATION_FAILED = "VERIFICATION_FAILED"
STATUS_ROLLBACK_READY = "ROLLBACK_READY"
STATUS_ROLLBACK_FAILED = "ROLLBACK_FAILED"
STATUS_SIMULATED = "SIMULATED"

SEVERITY_INFO = "INFO"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class ConnectorCapability:
    name: str
    supported: bool = False
    requires_approval: bool = True
    supports_rollback: bool = False
    destructive: bool = False
    description: str = ""


@dataclass
class ConnectorExecutionResult:
    ok: bool
    connector_id: str
    action: str
    status: str
    message: str

    execution_id: str = field(default_factory=lambda: f"CONN-EXEC-{uuid.uuid4().hex[:12].upper()}")
    tenant_id: str = "default"
    target_id: Optional[str] = None

    simulated: bool = True
    verification_ok: Optional[bool] = None
    rollback_available: bool = False
    rollback_payload: Dict[str, Any] = field(default_factory=dict)

    raw: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConnectorAuthState:
    authenticated: bool = False
    auth_type: str = "none"
    token_expires_at_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseConnector:
    connector_id: str = "base"
    connector_name: str = "Base Connector"
    vendor: str = "generic"

    def __init__(
            self,
            *,
            tenant_id: str = "default",
            config: Optional[Dict[str, Any]] = None,
            event_bus: Any = None,
            storage: Any = None,
            simulation_mode: bool = True,
    ) -> None:
        self.tenant_id = tenant_id or "default"
        self.config = config or {}
        self.event_bus = event_bus
        self.simulation_mode = simulation_mode
        self.auth_state = ConnectorAuthState()
        self.storage = storage
    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def capabilities(self) -> Dict[str, ConnectorCapability]:
        return {}

    def supports(self, action: str) -> bool:
        action = str(action or "").upper()
        capability = self.capabilities().get(action)
        return bool(capability and capability.supported)

    def requires_approval(self, action: str) -> bool:
        capability = self.capabilities().get(str(action or "").upper())
        return True if capability is None else bool(capability.requires_approval)

    def supports_rollback(self, action: str) -> bool:
        capability = self.capabilities().get(str(action or "").upper())
        return False if capability is None else bool(capability.supports_rollback)

    def is_destructive(self, action: str) -> bool:
        capability = self.capabilities().get(str(action or "").upper())
        return True if capability is None else bool(capability.destructive)

    # ------------------------------------------------------------------
    # Auth lifecycle
    # ------------------------------------------------------------------

    def authenticate(self) -> ConnectorAuthState:
        self.auth_state = ConnectorAuthState(
            authenticated=True,
            auth_type="simulation" if self.simulation_mode else "configured",
            metadata={"simulation_mode": self.simulation_mode},
        )
        return self.auth_state

    def refresh_auth(self) -> ConnectorAuthState:
        return self.authenticate()

    def is_authenticated(self) -> bool:
        return bool(self.auth_state.authenticated)

    def ensure_authenticated(self) -> ConnectorAuthState:
        if not self.is_authenticated():
            return self.authenticate()
        return self.auth_state

    # ------------------------------------------------------------------
    # Execution lifecycle
    # ------------------------------------------------------------------

    def execute(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str = "connector",
        execution_id: Optional[str] = None,
    ) -> ConnectorExecutionResult:
        action = str(action or "").upper()
        execution_id = execution_id or f"CONN-EXEC-{uuid.uuid4().hex[:12].upper()}"
        # ------------------------------------------------------------------
        # HARD SAFETY GUARDRAIL CHECK
        # ------------------------------------------------------------------

        try:
            safety_decision = check_action_safety(
                self.storage,
                tenant_id=self.tenant_id,
                action=action,
                payload=payload,
                actor=actor,
                execution_id=execution_id,
                connector_id=self.connector_id,
                autonomous=True,
            )

            if safety_decision.blocked:
                result = ConnectorExecutionResult(
                    ok=False,
                    connector_id=self.connector_id,
                    action=action,
                    status=STATUS_FAILED,
                    message=safety_decision.reason,
                    execution_id=execution_id,
                    tenant_id=self.tenant_id,
                    simulated=self.simulation_mode,
                    raw={
                        "safety_decision": safety_decision.to_dict(),
                    },
                )

                self._emit_result(
                    "CONNECTOR_EXECUTION_BLOCKED_BY_SAFETY",
                    result,
                )

                return result

            if safety_decision.requires_executive_approval:
                result = ConnectorExecutionResult(
                    ok=False,
                    connector_id=self.connector_id,
                    action=action,
                    status="EXECUTIVE_APPROVAL_REQUIRED",
                    message=safety_decision.reason,
                    execution_id=execution_id,
                    tenant_id=self.tenant_id,
                    simulated=self.simulation_mode,
                    raw={
                        "safety_decision": safety_decision.to_dict(),
                    },
                )

                self._emit_result(
                    "CONNECTOR_EXECUTION_REQUIRES_EXECUTIVE_APPROVAL",
                    result,
                )

                return result

        except Exception as safety_exc:
            result = ConnectorExecutionResult(
                ok=False,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_FAILED,
                message=f"Safety guardrail check failed: {safety_exc}",
                execution_id=execution_id,
                tenant_id=self.tenant_id,
                simulated=self.simulation_mode,
                raw={
                    "error": str(safety_exc),
                },
            )

            self._emit_result(
                "CONNECTOR_EXECUTION_SAFETY_CHECK_FAILED",
                result,
            )

            return result
        self._emit(
            "CONNECTOR_EXECUTION_STARTED",
            {
                "execution_id": execution_id,
                "connector_id": self.connector_id,
                "action": action,
                "actor": actor,
                "tenant_id": self.tenant_id,
            },
        )

        if not self.supports(action):
            result = ConnectorExecutionResult(
                ok=False,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_FAILED,
                message=f"{self.connector_name} does not support action: {action}",
                execution_id=execution_id,
                tenant_id=self.tenant_id,
                simulated=self.simulation_mode,
            )
            # ---------------------------------------------------------
            # AUTO VERIFICATION SCHEDULING
            # ---------------------------------------------------------

            try:

                schedule_verification(
                    storage=getattr(
                        self,
                        "storage",
                        None,
                    ),
                    tenant_id=self.tenant_id,
                    action=action,
                    connector_id=self.connector_id,
                    execution_id=result.execution_id,
                    payload=payload,
                    execution_result=result.to_dict(),
                    created_by=actor,
                )

            except Exception as verification_exc:

                self._emit(
                    "VERIFICATION_SCHEDULING_FAILED",
                    {
                        "execution_id": result.execution_id,
                        "connector_id": self.connector_id,
                        "action": action,
                        "error": str(
                            verification_exc
                        ),
                    },
                    severity=SEVERITY_HIGH,
                )

            # ---------------------------------------------------------
            # FINAL EXECUTION EVENT
            # ---------------------------------------------------------

            self._emit_result(
                "CONNECTOR_EXECUTION_COMPLETED",
                result,
            )

            return result

        try:
            self.ensure_authenticated()

            if self.simulation_mode:
                result = self._simulate_execute(
                    action=action,
                    payload=payload,
                    actor=actor,
                    execution_id=execution_id,
                )
            else:
                result = self._execute_real(
                    action=action,
                    payload=payload,
                    actor=actor,
                    execution_id=execution_id,
                )

            verify_result = self.verify(
                action=action,
                payload=payload,
                execution_result=result,
                actor=actor,
            )

            result.verification_ok = verify_result.ok

            if not verify_result.ok:
                result.ok = False
                result.status = STATUS_VERIFICATION_FAILED
                result.message = verify_result.message
                self._emit_result("CONNECTOR_VERIFICATION_FAILED", result)
                return result

            self._emit_result("CONNECTOR_EXECUTION_COMPLETED", result)
            return result

        except Exception as exc:
            result = ConnectorExecutionResult(
                ok=False,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_FAILED,
                message=str(exc),
                execution_id=execution_id,
                tenant_id=self.tenant_id,
                simulated=self.simulation_mode,
                raw={"error": str(exc)},
            )
            self._emit_result("CONNECTOR_EXECUTION_FAILED", result)
            return result

    def _execute_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:
        raise NotImplementedError(
            f"{self.connector_name} must implement _execute_real()"
        )

    def _simulate_execute(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:
        target_id = (
            payload.get("target_id")
            or payload.get("user_id")
            or payload.get("endpoint_id")
            or payload.get("device_id")
            or payload.get("message_id")
            or payload.get("ip")
        )

        rollback_payload = self.build_rollback_payload(
            action=action,
            payload=payload,
        )

        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_SIMULATED,
            message=f"Simulated {action} via {self.connector_name}.",
            execution_id=execution_id,
            tenant_id=self.tenant_id,
            target_id=target_id,
            simulated=True,
            rollback_available=bool(rollback_payload),
            rollback_payload=rollback_payload,
            raw={
                "actor": actor,
                "payload": payload,
                "simulation_mode": True,
            },
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        execution_result: ConnectorExecutionResult,
        actor: str = "connector",
    ) -> ConnectorExecutionResult:
        if self.simulation_mode:
            return ConnectorExecutionResult(
                ok=True,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_COMPLETED,
                message="Simulated verification passed.",
                execution_id=execution_result.execution_id,
                tenant_id=self.tenant_id,
                target_id=execution_result.target_id,
                simulated=True,
                verification_ok=True,
            )

        return self._verify_real(
            action=action,
            payload=payload,
            execution_result=execution_result,
            actor=actor,
        )

    def _verify_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        execution_result: ConnectorExecutionResult,
        actor: str,
    ) -> ConnectorExecutionResult:
        return ConnectorExecutionResult(
            ok=True,
            connector_id=self.connector_id,
            action=action,
            status=STATUS_COMPLETED,
            message="No real verification implemented.",
            execution_id=execution_result.execution_id,
            tenant_id=self.tenant_id,
            target_id=execution_result.target_id,
            simulated=False,
            verification_ok=True,
        )

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------

    def build_rollback_payload(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {}

    def rollback(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str = "connector",
        execution_id: Optional[str] = None,
    ) -> ConnectorExecutionResult:
        action = str(action or "").upper()
        execution_id = execution_id or f"CONN-RB-{uuid.uuid4().hex[:12].upper()}"

        self._emit(
            "CONNECTOR_ROLLBACK_STARTED",
            {
                "execution_id": execution_id,
                "connector_id": self.connector_id,
                "action": action,
                "tenant_id": self.tenant_id,
                "actor": actor,
            },
        )

        try:
            self.ensure_authenticated()

            if self.simulation_mode:
                result = ConnectorExecutionResult(
                    ok=True,
                    connector_id=self.connector_id,
                    action=action,
                    status=STATUS_SIMULATED,
                    message=f"Simulated rollback {action} via {self.connector_name}.",
                    execution_id=execution_id,
                    tenant_id=self.tenant_id,
                    simulated=True,
                    verification_ok=True,
                    raw={"payload": payload},
                )
            else:
                result = self._rollback_real(
                    action=action,
                    payload=payload,
                    actor=actor,
                    execution_id=execution_id,
                )

            self._emit_result("CONNECTOR_ROLLBACK_COMPLETED", result)
            return result

        except Exception as exc:
            result = ConnectorExecutionResult(
                ok=False,
                connector_id=self.connector_id,
                action=action,
                status=STATUS_ROLLBACK_FAILED,
                message=str(exc),
                execution_id=execution_id,
                tenant_id=self.tenant_id,
                simulated=self.simulation_mode,
                raw={"error": str(exc)},
            )
            self._emit_result("CONNECTOR_ROLLBACK_FAILED", result)
            return result

    def _rollback_real(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> ConnectorExecutionResult:
        raise NotImplementedError(
            f"{self.connector_name} must implement _rollback_real()"
        )

    # ------------------------------------------------------------------
    # Blast-radius estimation
    # ------------------------------------------------------------------

    def estimate_blast_radius(
        self,
        *,
        action: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        target_count = 1

        for key in ("targets", "user_ids", "device_ids", "message_ids", "ips"):
            if isinstance(payload.get(key), list):
                target_count = max(target_count, len(payload[key]))

        destructive = self.is_destructive(action)

        return {
            "connector_id": self.connector_id,
            "action": str(action or "").upper(),
            "tenant_id": self.tenant_id,
            "target_count": target_count,
            "destructive": destructive,
            "risk": "HIGH" if destructive or target_count > 10 else "MEDIUM",
            "requires_approval": self.requires_approval(action),
        }

    # ------------------------------------------------------------------
    # Event helpers
    # ------------------------------------------------------------------

    def _emit(self, event_type: str, payload: Dict[str, Any], severity: str = SEVERITY_INFO) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=self.tenant_id,
                source=f"connector:{self.connector_id}",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=self.tenant_id,
                    source=f"connector:{self.connector_id}",
                )
            except Exception:
                pass
        except Exception:
            pass

    def _emit_result(self, event_type: str, result: ConnectorExecutionResult) -> None:
        severity = SEVERITY_INFO if result.ok else SEVERITY_HIGH
        self._emit(
            event_type,
            {
                "execution_id": result.execution_id,
                "connector_id": result.connector_id,
                "action": result.action,
                "status": result.status,
                "message": result.message,
                "tenant_id": result.tenant_id,
                "target_id": result.target_id,
                "simulated": result.simulated,
                "verification_ok": result.verification_ok,
                "rollback_available": result.rollback_available,
                "rollback_payload": result.rollback_payload,
            },
            severity=severity,
        )