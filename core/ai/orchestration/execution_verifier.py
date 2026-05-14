"""
core/ai/orchestration/execution_verifier.py

Verification layer for autonomous execution.

Purpose:
- validate containment success
- validate rollback success
- detect partial failures
- recommend escalation
- recommend confidence adjustment
- emit forensic verification records

This is intentionally adapter-safe. Real EDR, IAM, mailbox, and network
verification adapters can be wired in later.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from core.events.event_bus import (
    get_event_bus,
    VERIFICATION_COMPLETED,
    VERIFICATION_FAILED,
)

def _now_ms() -> int:
    return int(time.time() * 1000)


def _lower(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip().lower()


def _upper(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip().upper()


@dataclass
class VerificationResult:
    success: bool
    status: str
    action: str
    message: str
    partial_failure: bool = False
    should_escalate: bool = False
    rollback_required: bool = False
    confidence_adjustment: float = 0.0
    checked_at_ms: int = field(default_factory=_now_ms)
    details: Dict[str, Any] = field(default_factory=dict)


class ExecutionVerifier:
    """
    Verifies execution and rollback outcomes.

    Usage:
        verifier = ExecutionVerifier(storage)
        result = verifier.verify_execution(
            action="endpoint_isolation",
            action_result={...},
            decision_id="dec_...",
        )
    """

    def __init__(self, storage: Any):
        self.storage = storage
        self.governance = storage.governance
        self.event_bus = get_event_bus()

    # ========================================================
    # EXECUTION VERIFICATION
    # ========================================================

    def verify_execution(
        self,
        action: str,
        action_result: Dict[str, Any],
        decision_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        severity: str = "MEDIUM",
    ) -> VerificationResult:
        action_key = _lower(action)

        if action_key in {"endpoint_isolation", "isolate_endpoint"}:
            result = self._verify_endpoint_isolation(action_result)

        elif action_key in {"mailbox_quarantine", "quarantine_mailbox"}:
            result = self._verify_mailbox_quarantine(action_result)

        elif action_key in {"user_disablement", "disable_user"}:
            result = self._verify_user_disablement(action_result)

        elif action_key in {"session_revocation", "revoke_sessions"}:
            result = self._verify_session_revocation(action_result)

        elif action_key in {"network_segmentation", "segment_network"}:
            result = self._verify_network_segmentation(action_result)

        elif action_key in {"evidence_sealing", "seal_evidence"}:
            result = self._verify_evidence_sealing(action_result)

        elif action_key == "noop":
            result = VerificationResult(
                success=True,
                status="VERIFIED",
                action=action,
                message="No-op action verified.",
                details={"action_result": action_result},
            )

        else:
            result = VerificationResult(
                success=False,
                status="UNKNOWN_ACTION",
                action=action,
                message=f"No verification handler registered for action: {action}",
                partial_failure=True,
                should_escalate=True,
                rollback_required=True,
                confidence_adjustment=-0.15,
                details={"action_result": action_result},
            )

        self._record_verification_trace(
            result=result,
            decision_id=decision_id,
            case_id=case_id,
            evidence_id=evidence_id,
            tenant_id=tenant_id,
            target_type=target_type,
            target_id=target_id,
            severity=severity,
        )

        return result

    # ========================================================
    # ROLLBACK VERIFICATION
    # ========================================================

    def verify_rollback(
        self,
        rollback_action: str,
        rollback_result: Dict[str, Any],
        rollback_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        severity: str = "HIGH",
    ) -> VerificationResult:
        action_key = _lower(rollback_action)

        success = bool(rollback_result.get("success"))
        partial = bool(rollback_result.get("partial_failure"))

        result = VerificationResult(
            success=success and not partial,
            status="ROLLBACK_VERIFIED" if success and not partial else "ROLLBACK_FAILED",
            action=rollback_action,
            message=rollback_result.get(
                "message",
                "Rollback verified." if success else "Rollback verification failed.",
            ),
            partial_failure=partial,
            should_escalate=not success or partial,
            rollback_required=False,
            confidence_adjustment=0.05 if success and not partial else -0.25,
            details={
                "rollback_id": rollback_id,
                "rollback_result": rollback_result,
            },
        )

        self.governance.record_execution_trace(
            stage="ROLLBACK_VERIFICATION",
            status=result.status,
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            actor="execution_verifier",
            action=rollback_action,
            message=result.message,
            payload=result.__dict__,
        )

        if rollback_id:
            self.governance.update_rollback_status(
                rollback_id=rollback_id,
                status="ROLLBACK_COMPLETED" if result.success else "ROLLBACK_FAILED",
                actor="execution_verifier",
                verification=result.__dict__,
            )

        self.governance.record_governance_event(
            event_type="ROLLBACK_VERIFICATION_COMPLETED",
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            rollback_id=rollback_id,
            severity=_upper(severity, "HIGH"),
            status=result.status,
            actor="execution_verifier",
            action=rollback_action,
            rollback_available=False,
            details=result.__dict__,
        )
        # ----------------------------------------------------
        # EVENT BUS EMISSION
        # ----------------------------------------------------

        if result.success:

            self.event_bus.publish(
                "ROLLBACK_VERIFICATION_COMPLETED",
                payload={
                    "rollback_id": rollback_id,
                    "decision_id": decision_id,
                    "verification": result.__dict__,
                },
                tenant_id=tenant_id,
                actor="execution_verifier",
                source="execution_verifier",
            )

        else:

            self.event_bus.publish(
                "ROLLBACK_VERIFICATION_FAILED",
                payload={
                    "rollback_id": rollback_id,
                    "decision_id": decision_id,
                    "verification": result.__dict__,
                    "reason": result.message,
                },
                tenant_id=tenant_id,
                actor="execution_verifier",
                source="execution_verifier",
            )
        return result

    # ========================================================
    # ACTION-SPECIFIC VERIFIERS
    # ========================================================

    def _verify_endpoint_isolation(self, action_result: Dict[str, Any]) -> VerificationResult:
        success = bool(action_result.get("success"))

        return VerificationResult(
            success=success,
            status="VERIFIED" if success else "FAILED",
            action="endpoint_isolation",
            message=(
                "Endpoint isolation verified."
                if success
                else action_result.get("message", "Endpoint isolation failed verification.")
            ),
            partial_failure=bool(action_result.get("partial_failure")),
            should_escalate=not success,
            rollback_required=not success,
            confidence_adjustment=0.03 if success else -0.20,
            details={"action_result": action_result},
        )

    def _verify_mailbox_quarantine(self, action_result: Dict[str, Any]) -> VerificationResult:
        success = bool(action_result.get("success"))

        return VerificationResult(
            success=success,
            status="VERIFIED" if success else "FAILED",
            action="mailbox_quarantine",
            message=(
                "Mailbox quarantine verified."
                if success
                else action_result.get("message", "Mailbox quarantine failed verification.")
            ),
            partial_failure=bool(action_result.get("partial_failure")),
            should_escalate=not success,
            rollback_required=not success,
            confidence_adjustment=0.03 if success else -0.20,
            details={"action_result": action_result},
        )

    def _verify_user_disablement(self, action_result: Dict[str, Any]) -> VerificationResult:
        success = bool(action_result.get("success"))

        return VerificationResult(
            success=success,
            status="VERIFIED" if success else "FAILED",
            action="user_disablement",
            message=(
                "User disablement verified."
                if success
                else action_result.get("message", "User disablement failed verification.")
            ),
            partial_failure=bool(action_result.get("partial_failure")),
            should_escalate=not success,
            rollback_required=not success,
            confidence_adjustment=0.04 if success else -0.25,
            details={"action_result": action_result},
        )

    def _verify_session_revocation(self, action_result: Dict[str, Any]) -> VerificationResult:
        success = bool(action_result.get("success"))

        return VerificationResult(
            success=success,
            status="VERIFIED" if success else "FAILED",
            action="session_revocation",
            message=(
                "Session revocation verified."
                if success
                else action_result.get("message", "Session revocation failed verification.")
            ),
            partial_failure=bool(action_result.get("partial_failure")),
            should_escalate=not success,
            rollback_required=False,
            confidence_adjustment=0.02 if success else -0.10,
            details={"action_result": action_result},
        )

    def _verify_network_segmentation(self, action_result: Dict[str, Any]) -> VerificationResult:
        success = bool(action_result.get("success"))

        return VerificationResult(
            success=success,
            status="VERIFIED" if success else "FAILED",
            action="network_segmentation",
            message=(
                "Network segmentation verified."
                if success
                else action_result.get("message", "Network segmentation failed verification.")
            ),
            partial_failure=bool(action_result.get("partial_failure")),
            should_escalate=not success,
            rollback_required=not success,
            confidence_adjustment=0.03 if success else -0.25,
            details={"action_result": action_result},
        )

    def _verify_evidence_sealing(self, action_result: Dict[str, Any]) -> VerificationResult:
        success = bool(action_result.get("success"))

        return VerificationResult(
            success=success,
            status="VERIFIED" if success else "FAILED",
            action="evidence_sealing",
            message=(
                "Evidence sealing verified."
                if success
                else action_result.get("message", "Evidence sealing failed verification.")
            ),
            partial_failure=False,
            should_escalate=not success,
            rollback_required=False,
            confidence_adjustment=0.02 if success else -0.15,
            details={"action_result": action_result},
        )

    # ========================================================
    # FORENSIC RECORDING
    # ========================================================

    def _record_verification_trace(
        self,
        result: VerificationResult,
        decision_id: Optional[str],
        case_id: Optional[str],
        evidence_id: Optional[str],
        tenant_id: Optional[str],
        target_type: Optional[str],
        target_id: Optional[str],
        severity: str,
    ) -> None:
        self.governance.record_execution_trace(
            stage="VERIFICATION",
            status=result.status,
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            actor="execution_verifier",
            action=result.action,
            message=result.message,
            payload={
                "target_type": target_type,
                "target_id": target_id,
                "result": result.__dict__,
            },
        )

        self.governance.record_governance_event(
            event_type="EXECUTION_VERIFICATION_COMPLETED",
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            severity=_upper(severity, "MEDIUM"),
            status=result.status,
            actor="execution_verifier",
            action=result.action,
            target_type=target_type,
            target_id=target_id,
            rollback_available=result.rollback_required,
            details={
                "success": result.success,
                "partial_failure": result.partial_failure,
                "should_escalate": result.should_escalate,
                "rollback_required": result.rollback_required,
                "confidence_adjustment": result.confidence_adjustment,
                "message": result.message,
                "checked_at_ms": result.checked_at_ms,
            },
        )

        # ----------------------------------------------------
        # EVENT BUS EMISSION
        # ----------------------------------------------------

        if result.success:

            self.event_bus.publish(
                VERIFICATION_COMPLETED,
                payload={
                    "decision_id": decision_id,
                    "action": result.action,
                    "status": result.status,
                    "verification": result.__dict__,
                },
                tenant_id=tenant_id,
                actor="execution_verifier",
                source="execution_verifier",
            )

        else:

            self.event_bus.publish(
                VERIFICATION_FAILED,
                payload={
                    "decision_id": decision_id,
                    "action": result.action,
                    "status": result.status,
                    "verification": result.__dict__,
                    "reason": result.message,
                },
                tenant_id=tenant_id,
                actor="execution_verifier",
                source="execution_verifier",
            )

def get_execution_verifier(storage: Any) -> ExecutionVerifier:
    return ExecutionVerifier(storage)