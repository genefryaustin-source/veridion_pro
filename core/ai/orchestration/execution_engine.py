"""
core/ai/orchestration/execution_engine.py
"""

from __future__ import annotations

import time
import uuid
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

from core.events.event_bus import (
    get_event_bus,
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    ROLLBACK_TRIGGERED,
)

from core.ai.orchestration.plugin_registry import PluginRegistry

from core.ai.orchestration.autonomy_modes import (
    MANUAL,
    LOCKDOWN,
    get_autonomy_mode,
)


SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

MODE_MANUAL = "manual"
MODE_BALANCED = "balanced"
MODE_AGGRESSIVE = "aggressive"

STATUS_DECIDED = "DECIDED"
STATUS_PENDING_APPROVAL = "PENDING_APPROVAL"
STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_EXECUTING = "EXECUTING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
STATUS_ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"

ACTION_ENDPOINT_ISOLATION = "endpoint_isolation"
ACTION_MAILBOX_QUARANTINE = "mailbox_quarantine"
ACTION_USER_DISABLEMENT = "user_disablement"
ACTION_SESSION_REVOCATION = "session_revocation"
ACTION_NETWORK_SEGMENTATION = "network_segmentation"
ACTION_EVIDENCE_SEALING = "evidence_sealing"
ACTION_NOOP = "noop"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _norm(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _upper(value: Any, default: str = "") -> str:
    return _norm(value, default).upper()


def _lower(value: Any, default: str = "") -> str:
    return _norm(value, default).lower()


def _new_execution_id() -> str:
    return f"exe_{uuid.uuid4().hex}"


@dataclass
class ExecutionPolicy:
    tenant_id: Optional[str] = None
    tenant_mode: str = MODE_BALANCED
    low_confidence_threshold: float = 0.65
    auto_execute_threshold: float = 0.90
    require_approval_for_high: bool = True
    require_approval_for_critical: bool = True
    require_legal_for_export_control: bool = True
    require_manager_for_destructive: bool = True
    allow_aggressive_auto_containment: bool = False
    allow_noop_auto_execute: bool = True
    destructive_actions: List[str] = field(default_factory=lambda: [
        ACTION_ENDPOINT_ISOLATION,
        ACTION_MAILBOX_QUARANTINE,
        ACTION_USER_DISABLEMENT,
        ACTION_NETWORK_SEGMENTATION,
        ACTION_SESSION_REVOCATION,
    ])


@dataclass
class ExecutionRequest:
    recommendation: str
    action: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    evidence_id: Optional[str] = None
    run_id: Optional[str] = None

    severity: str = SEVERITY_MEDIUM
    risk: Optional[str] = None
    confidence: float = 0.0

    actor: str = "ai_orchestrator"
    target_type: Optional[str] = None
    target_id: Optional[str] = None

    categories: List[str] = field(default_factory=list)

    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    execution_id: str
    decision_id: str
    status: str
    action: str
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    rollback_id: Optional[str] = None
    execution_trace_id: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class ExecutionEngine:
    def __init__(
        self,
        storage: Any,
        policy: Optional[ExecutionPolicy] = None,
        autonomy_mode: str = MANUAL,
    ):
        self.storage = storage
        self.governance = storage.governance
        self.policy = policy or ExecutionPolicy()
        self.event_bus = get_event_bus()
        self.plugin_registry = PluginRegistry(storage)
        self.autonomy_mode = autonomy_mode

    def submit_decision(self, request: ExecutionRequest) -> ExecutionResult:
        execution_id = _new_execution_id()

        self._trace(
            stage="EXECUTION_STARTED",
            status="STARTED",
            request=request,
            action=request.action,
            message="Execution engine received autonomous decision request.",
            payload={
                "execution_id": execution_id,
                "recommendation": request.recommendation,
                "confidence": request.confidence,
                "severity": request.severity,
                "categories": request.categories,
            },
        )

        policy_result = self.evaluate_policy(request)

        mode_eval = self._evaluate_autonomy_mode(request)

        policy_result["autonomy_mode"] = self.autonomy_mode
        policy_result["mode_evaluation"] = mode_eval

        decision_id = self.governance.record_orchestration_decision(
            recommendation=request.recommendation,
            final_action=request.action,
            tenant_id=request.tenant_id,
            case_id=request.case_id,
            evidence_id=request.evidence_id,
            run_id=request.run_id,
            actor=request.actor,
            confidence=request.confidence,
            risk=request.risk,
            severity=_upper(request.severity, SEVERITY_MEDIUM),
            status=STATUS_DECIDED,
            outcome=None,
            requires_approval=policy_result["requires_approval"],
            rollback_available=policy_result["rollback_available"],
            policy_context=policy_result,
            details={
                "execution_id": execution_id,
                "target_type": request.target_type,
                "target_id": request.target_id,
                "metadata": request.metadata,
            },
        )

        self._event(
            event_type="EXECUTION_STARTED",
            request=request,
            decision_id=decision_id,
            action=request.action,
            status="STARTED",
            details={
                "execution_id": execution_id,
                "policy_result": policy_result,
            },
        )

        self._trace(
            stage="POLICY_EVALUATION",
            status="COMPLETED",
            request=request,
            decision_id=decision_id,
            action=request.action,
            message="Policy evaluation completed.",
            payload=policy_result,
        )

        if not mode_eval.get("allowed"):
            self._event(
                event_type="AUTONOMY_POLICY_BLOCK",
                request=request,
                decision_id=decision_id,
                action=request.action,
                status="BLOCKED",
                details=mode_eval,
            )

            return ExecutionResult(
                execution_id=execution_id,
                decision_id=decision_id,
                status="BLOCKED",
                action=request.action,
                message=mode_eval.get("reason"),
                details={
                    "policy_result": policy_result,
                    "mode_evaluation": mode_eval,
                },
            )

        if policy_result["requires_approval"]:
            approval_id = self._route_for_approval(
                request=request,
                decision_id=decision_id,
                execution_id=execution_id,
                policy_result=policy_result,
            )

            return ExecutionResult(
                execution_id=execution_id,
                decision_id=decision_id,
                status=STATUS_PENDING_APPROVAL,
                action=request.action,
                requires_approval=True,
                approval_request_id=approval_id,
                message="Execution paused pending approval.",
                details={"policy_result": policy_result},
            )

        return self._execute_now(
            request=request,
            decision_id=decision_id,
            execution_id=execution_id,
            policy_result=policy_result,
        )

    def evaluate_policy(self, request: ExecutionRequest) -> Dict[str, Any]:
        severity = _upper(request.severity, SEVERITY_MEDIUM)
        action = _lower(request.action)
        categories = {_upper(c) for c in request.categories or []}
        confidence = float(request.confidence or 0.0)
        tenant_mode = _lower(self.policy.tenant_mode, MODE_BALANCED)

        destructive = action in self.policy.destructive_actions

        export_control = bool(categories.intersection({
            "EXPORT_CONTROL",
            "ITAR",
            "EAR",
            "CONTROLLED_TECHNICAL_INFORMATION",
            "CTI",
        }))

        reasons = []
        requires_approval = False
        requires_legal = False
        requires_manager = False
        should_escalate = False
        rollback_available = destructive

        if confidence < self.policy.low_confidence_threshold:
            requires_approval = True
            should_escalate = True
            reasons.append("low_confidence")

        if severity == SEVERITY_CRITICAL and self.policy.require_approval_for_critical:
            requires_approval = True
            reasons.append("critical_severity")

        if severity == SEVERITY_HIGH and self.policy.require_approval_for_high:
            requires_approval = True
            reasons.append("high_severity")

        if export_control and self.policy.require_legal_for_export_control:
            requires_approval = True
            requires_legal = True
            should_escalate = True
            reasons.append("export_control_legal_review")

        if destructive and self.policy.require_manager_for_destructive:
            requires_approval = True
            requires_manager = True
            reasons.append("destructive_action_manager_review")

        if action == ACTION_NOOP and self.policy.allow_noop_auto_execute:
            requires_approval = False
            reasons.append("noop_auto_allowed")

        if tenant_mode == MODE_MANUAL:
            requires_approval = True
            reasons.append("tenant_manual_mode")

        if (
            tenant_mode == MODE_AGGRESSIVE
            and self.policy.allow_aggressive_auto_containment
            and confidence >= self.policy.auto_execute_threshold
            and not export_control
        ):
            requires_approval = False
            reasons.append("aggressive_auto_containment_allowed")

        return {
            "tenant_mode": tenant_mode,
            "severity": severity,
            "confidence": confidence,
            "action": action,
            "destructive": destructive,
            "export_control": export_control,
            "requires_approval": requires_approval,
            "requires_legal": requires_legal,
            "requires_manager": requires_manager,
            "should_escalate": should_escalate,
            "rollback_available": rollback_available,
            "reasons": reasons,
            "evaluated_at_ms": _now_ms(),
        }

    def _route_for_approval(
        self,
        request: ExecutionRequest,
        decision_id: str,
        execution_id: str,
        policy_result: Dict[str, Any],
    ) -> str:
        self._trace(
            stage="APPROVAL_ROUTING",
            status="PENDING",
            request=request,
            decision_id=decision_id,
            action=request.action,
            message="Execution requires approval before actioning.",
            payload={
                "execution_id": execution_id,
                "policy_result": policy_result,
            },
        )

        approval_id = self.governance.create_approval_request(
            action=request.action,
            tenant_id=request.tenant_id,
            case_id=request.case_id,
            evidence_id=request.evidence_id,
            decision_id=decision_id,
            request_type="AUTONOMOUS_EXECUTION_APPROVAL",
            risk=request.risk,
            severity=_upper(request.severity, SEVERITY_MEDIUM),
            requested_by="execution_engine",
            assigned_reviewer=self._select_reviewer(policy_result),
            requires_legal=policy_result.get("requires_legal", False),
            requires_manager=policy_result.get("requires_manager", False),
            rollback_available=policy_result.get("rollback_available", False),
            metadata={
                "execution_id": execution_id,
                "recommendation": request.recommendation,
                "target_type": request.target_type,
                "target_id": request.target_id,
                "policy_result": policy_result,
            },
        )

        self._event(
            event_type="EXECUTION_PENDING_APPROVAL",
            request=request,
            decision_id=decision_id,
            approval_request_id=approval_id,
            action=request.action,
            status=STATUS_PENDING_APPROVAL,
            requires_approval=True,
            rollback_available=policy_result.get("rollback_available", False),
            details={
                "execution_id": execution_id,
                "policy_result": policy_result,
            },
        )

        return approval_id

    def approve_and_execute(
        self,
        approval_request_id: str,
        reviewed_by: str = "analyst",
        review_comment: Optional[str] = None,
    ) -> ExecutionResult:
        approval = self.governance.get_approval_request(approval_request_id)

        if not approval:
            raise ValueError(f"Approval request not found: {approval_request_id}")

        self.governance.update_approval_status(
            request_id=approval_request_id,
            status=STATUS_APPROVED,
            reviewed_by=reviewed_by,
            review_comment=review_comment,
        )

        decision_id = approval.get("decision_id")
        decision = self.governance.get_decision(decision_id) if decision_id else None

        request = ExecutionRequest(
            recommendation=(decision or {}).get("recommendation") or approval.get("action"),
            action=approval.get("action"),
            tenant_id=approval.get("tenant_id"),
            case_id=approval.get("case_id"),
            evidence_id=approval.get("evidence_id"),
            severity=approval.get("severity") or SEVERITY_MEDIUM,
            risk=approval.get("risk"),
            confidence=float((decision or {}).get("confidence") or 0.0),
            actor="execution_engine",
            reason=review_comment,
            metadata={
                "approval_request_id": approval_request_id,
                "approved_by": reviewed_by,
            },
        )

        execution_id = _new_execution_id()

        self._event(
            event_type="EXECUTION_APPROVED",
            request=request,
            decision_id=decision_id,
            approval_request_id=approval_request_id,
            action=request.action,
            status=STATUS_APPROVED,
            actor=reviewed_by,
            details={
                "execution_id": execution_id,
                "review_comment": review_comment,
            },
        )

        return self._execute_now(
            request=request,
            decision_id=decision_id,
            execution_id=execution_id,
            policy_result={
                "approved_by": reviewed_by,
                "approval_request_id": approval_request_id,
                "rollback_available": True,
                "approval_path": True,
            },
        )

    def reject_execution(
        self,
        approval_request_id: str,
        reviewed_by: str = "analyst",
        review_comment: Optional[str] = None,
    ) -> bool:
        approval = self.governance.get_approval_request(approval_request_id)

        if not approval:
            raise ValueError(f"Approval request not found: {approval_request_id}")

        ok = self.governance.update_approval_status(
            request_id=approval_request_id,
            status=STATUS_REJECTED,
            reviewed_by=reviewed_by,
            review_comment=review_comment,
        )

        self.governance.record_analyst_override(
            decision_id=approval.get("decision_id"),
            analyst=reviewed_by,
            original_action=approval.get("action"),
            override_action="REJECT_EXECUTION",
            reason=review_comment,
            tenant_id=approval.get("tenant_id"),
            case_id=approval.get("case_id"),
            evidence_id=approval.get("evidence_id"),
            severity=approval.get("severity"),
            details={"approval_request_id": approval_request_id},
        )

        return ok

    def _execute_now(
        self,
        request: ExecutionRequest,
        decision_id: str,
        execution_id: str,
        policy_result: Dict[str, Any],
    ) -> ExecutionResult:
        self._trace(
            stage="EXECUTION",
            status="STARTED",
            request=request,
            decision_id=decision_id,
            action=request.action,
            message="Execution started.",
            payload={
                "execution_id": execution_id,
                "policy_result": policy_result,
            },
        )

        self._event(
            event_type="EXECUTION_STARTED_ACTIONING",
            request=request,
            decision_id=decision_id,
            action=request.action,
            status=STATUS_EXECUTING,
            details={"execution_id": execution_id},
        )

        try:
            action_result = self._dispatch_action(request)

            verification = self._verify_execution(
                request=request,
                action_result=action_result,
            )

            if not verification.get("success"):
                rollback_id = self._trigger_rollback(
                    request=request,
                    decision_id=decision_id,
                    execution_id=execution_id,
                    reason=verification.get("message", "Execution verification failed."),
                    verification=verification,
                )

                return ExecutionResult(
                    execution_id=execution_id,
                    decision_id=decision_id,
                    status=STATUS_ROLLBACK_REQUIRED,
                    action=request.action,
                    rollback_id=rollback_id,
                    message="Execution failed verification; rollback required.",
                    details={
                        "action_result": action_result,
                        "verification": verification,
                    },
                )

            self._trace(
                stage="VERIFICATION",
                status="COMPLETED",
                request=request,
                decision_id=decision_id,
                action=request.action,
                message="Execution verification completed successfully.",
                payload={
                    "execution_id": execution_id,
                    "verification": verification,
                },
            )

            self.event_bus.publish(
                EXECUTION_COMPLETED,
                payload={
                    "decision_id": decision_id,
                    "execution_id": execution_id,
                    "action_result": action_result,
                    "verification": verification,
                },
                tenant_id=request.tenant_id,
                actor=request.actor,
                source="execution_engine",
            )

            self._event(
                event_type="EXECUTION_COMPLETED",
                request=request,
                decision_id=decision_id,
                action=request.action,
                status=STATUS_COMPLETED,
                rollback_available=policy_result.get("rollback_available", False),
                details={
                    "execution_id": execution_id,
                    "action_result": action_result,
                    "verification": verification,
                },
            )

            return ExecutionResult(
                execution_id=execution_id,
                decision_id=decision_id,
                status=STATUS_COMPLETED,
                action=request.action,
                message="Execution completed successfully.",
                details={
                    "action_result": action_result,
                    "verification": verification,
                },
            )

        except Exception as e:
            self.event_bus.publish(
                EXECUTION_FAILED,
                payload={
                    "decision_id": decision_id,
                    "execution_id": execution_id,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                tenant_id=request.tenant_id,
                actor=request.actor,
                source="execution_engine",
            )

            rollback_id = self._trigger_rollback(
                request=request,
                decision_id=decision_id,
                execution_id=execution_id,
                reason=str(e),
                verification={
                    "success": False,
                    "message": str(e),
                    "exception": type(e).__name__,
                },
            )

            self._event(
                event_type="EXECUTION_FAILED",
                request=request,
                decision_id=decision_id,
                action=request.action,
                status=STATUS_FAILED,
                details={
                    "execution_id": execution_id,
                    "error": str(e),
                    "rollback_id": rollback_id,
                },
            )

            return ExecutionResult(
                execution_id=execution_id,
                decision_id=decision_id,
                status=STATUS_FAILED,
                action=request.action,
                rollback_id=rollback_id,
                message=f"Execution failed: {e}",
                details={"error": str(e)},
            )

    def _dispatch_action(
        self,
        request: ExecutionRequest,
    ) -> Dict[str, Any]:
        action = _lower(request.action)

        plugin = self.plugin_registry.get(action)

        if not plugin:
            return {
                "success": False,
                "action": request.action,
                "message": f"No plugin registered for action: {request.action}",
                "plugin_found": False,
                "simulated": False,
            }

        try:
            result = plugin.execute(request)

            if not isinstance(result, dict):
                return {
                    "success": False,
                    "action": request.action,
                    "message": f"Plugin returned invalid result type: {type(result)}",
                    "plugin": plugin.__class__.__name__,
                }

            result.setdefault("plugin", plugin.__class__.__name__)
            result.setdefault("action", request.action)
            result.setdefault("executed_at_ms", _now_ms())

            return result

        except Exception as e:
            return {
                "success": False,
                "action": request.action,
                "plugin": plugin.__class__.__name__,
                "message": str(e),
                "exception": type(e).__name__,
                "simulated": False,
                "executed_at_ms": _now_ms(),
            }

    def _verify_execution(
        self,
        request: ExecutionRequest,
        action_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        action = _lower(request.action)

        plugin = self.plugin_registry.get(action)

        if not plugin:
            return {
                "success": False,
                "message": f"No verification plugin registered for action: {request.action}",
                "plugin_found": False,
            }

        try:
            result = plugin.verify(request, action_result)

            if not isinstance(result, dict):
                return {
                    "success": False,
                    "message": "Plugin verification returned invalid result type.",
                    "plugin": plugin.__class__.__name__,
                }

            result.setdefault("plugin", plugin.__class__.__name__)
            result.setdefault("verified_at_ms", _now_ms())

            return result

        except Exception as e:
            return {
                "success": False,
                "plugin": plugin.__class__.__name__,
                "message": str(e),
                "exception": type(e).__name__,
                "verified_at_ms": _now_ms(),
            }

    def _trigger_rollback(
        self,
        request: ExecutionRequest,
        decision_id: str,
        execution_id: str,
        reason: str,
        verification: Optional[Dict[str, Any]] = None,
    ) -> str:
        self._trace(
            stage="ROLLBACK",
            status="REQUIRED",
            request=request,
            decision_id=decision_id,
            action=request.action,
            message="Rollback required.",
            payload={
                "execution_id": execution_id,
                "reason": reason,
                "verification": verification or {},
            },
        )

        action = _lower(request.action)

        plugin = self.plugin_registry.get(action)

        if plugin:
            try:
                rollback_result = plugin.rollback(
                    request,
                    {
                        "decision_id": decision_id,
                        "execution_id": execution_id,
                        "verification": verification,
                    },
                )

                if not isinstance(rollback_result, dict):
                    rollback_result = {
                        "success": False,
                        "plugin": plugin.__class__.__name__,
                        "message": "Plugin rollback returned invalid result type.",
                    }

            except Exception as e:
                rollback_result = {
                    "success": False,
                    "plugin": plugin.__class__.__name__,
                    "message": str(e),
                    "exception": type(e).__name__,
                }

        else:
            rollback_result = {
                "success": False,
                "message": f"No rollback plugin registered for action: {request.action}",
                "plugin_found": False,
            }

        rollback_id = self.governance.record_rollback_event(
            rollback_action=rollback_result.get(
                "rollback_action",
                f"rollback_{request.action}",
            ),
            rollback_reason=reason,
            tenant_id=request.tenant_id,
            case_id=request.case_id,
            evidence_id=request.evidence_id,
            decision_id=decision_id,
            status=STATUS_ROLLBACK_REQUIRED,
            severity=_upper(request.severity, SEVERITY_HIGH),
            actor="execution_engine",
            requires_approval=True,
            rollback_payload={
                "execution_id": execution_id,
                "original_action": request.action,
                "target_type": request.target_type,
                "target_id": request.target_id,
                "rollback_result": rollback_result,
            },
            verification=verification or {},
        )

        self.event_bus.publish(
            ROLLBACK_TRIGGERED,
            payload={
                "rollback_id": rollback_id,
                "decision_id": decision_id,
                "reason": reason,
                "rollback_result": rollback_result,
            },
            tenant_id=request.tenant_id,
            actor="execution_engine",
            source="execution_engine",
        )

        self._event(
            event_type="ROLLBACK_TRIGGERED",
            request=request,
            decision_id=decision_id,
            rollback_id=rollback_id,
            action=rollback_result.get(
                "rollback_action",
                f"rollback_{request.action}",
            ),
            status=STATUS_ROLLBACK_REQUIRED,
            rollback_available=True,
            details={
                "execution_id": execution_id,
                "reason": reason,
                "rollback_result": rollback_result,
            },
        )

        return rollback_id

    def complete_rollback(
        self,
        rollback_id: str,
        actor: str = "execution_engine",
        verification: Optional[Dict[str, Any]] = None,
    ) -> bool:
        ok = self.governance.update_rollback_status(
            rollback_id=rollback_id,
            status=STATUS_ROLLBACK_COMPLETED,
            actor=actor,
            verification=verification or {
                "success": True,
                "message": "Rollback completed.",
                "completed_at_ms": _now_ms(),
            },
        )

        if ok:
            self.event_bus.publish(
                "ROLLBACK_COMPLETED",
                payload={
                    "rollback_id": rollback_id,
                    "verification": verification or {},
                },
                actor=actor,
                source="execution_engine",
            )

        return ok

    def _trace(
        self,
        stage: str,
        status: str,
        request: ExecutionRequest,
        action: Optional[str] = None,
        decision_id: Optional[str] = None,
        message: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload = payload or {}

        trace_id = self.governance.record_execution_trace(
            stage=stage,
            status=status,
            tenant_id=request.tenant_id,
            case_id=request.case_id,
            evidence_id=request.evidence_id,
            decision_id=decision_id,
            actor="execution_engine",
            action=action,
            message=message,
            payload=payload,
        )

        try:
            self.event_bus.publish(
                f"TRACE_{stage}",
                payload={
                    "trace_id": trace_id,
                    "decision_id": decision_id,
                    "stage": stage,
                    "status": status,
                    "message": message,
                    "payload": payload,
                },
                tenant_id=request.tenant_id,
                actor="execution_engine",
                source="execution_engine_trace",
            )
        except Exception:
            traceback.print_exc()

        return trace_id

    def _event(
        self,
        event_type: str,
        request: ExecutionRequest,
        action: Optional[str] = None,
        decision_id: Optional[str] = None,
        approval_request_id: Optional[str] = None,
        rollback_id: Optional[str] = None,
        status: Optional[str] = None,
        actor: str = "execution_engine",
        requires_approval: bool = False,
        rollback_available: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        details = details or {}

        event_id = self.governance.record_governance_event(
            event_type=event_type,
            tenant_id=request.tenant_id,
            case_id=request.case_id,
            evidence_id=request.evidence_id,
            decision_id=decision_id,
            approval_request_id=approval_request_id,
            rollback_id=rollback_id,
            severity=_upper(request.severity, SEVERITY_MEDIUM),
            status=status,
            actor=actor,
            action=action,
            target_type=request.target_type,
            target_id=request.target_id,
            requires_approval=requires_approval,
            rollback_available=rollback_available,
            details=details,
        )

        try:
            self.event_bus.publish(
                event_type,
                payload={
                    "event_id": event_id,
                    "decision_id": decision_id,
                    "approval_request_id": approval_request_id,
                    "rollback_id": rollback_id,
                    "status": status,
                    "action": action,
                    "severity": _upper(request.severity, SEVERITY_MEDIUM),
                    "requires_approval": requires_approval,
                    "rollback_available": rollback_available,
                    "details": details,
                },
                tenant_id=request.tenant_id,
                actor=actor,
                source="execution_engine",
            )
        except Exception:
            traceback.print_exc()

        return event_id

    def _evaluate_autonomy_mode(
        self,
        request: ExecutionRequest,
    ) -> Dict[str, Any]:
        mode = get_autonomy_mode(self.autonomy_mode)

        action = _lower(request.action)

        severity = _upper(request.severity, SEVERITY_MEDIUM)

        if mode.name == LOCKDOWN:
            return {
                "allowed": True,
                "auto_execute": True,
                "require_approval": False,
                "reason": "LOCKDOWN mode enabled.",
            }

        if mode.name == MANUAL:
            return {
                "allowed": False,
                "auto_execute": False,
                "require_approval": True,
                "reason": "Manual mode requires approval.",
            }

        if severity in {SEVERITY_CRITICAL, SEVERITY_HIGH} and not mode.allow_high_risk_actions:
            return {
                "allowed": False,
                "auto_execute": False,
                "require_approval": True,
                "reason": "High-risk actions restricted in current autonomy mode.",
            }

        if "endpoint" in action and not mode.allow_endpoint_actions:
            return {
                "allowed": False,
                "auto_execute": False,
                "require_approval": True,
                "reason": "Endpoint actions restricted in current autonomy mode.",
            }

        if ("disable" in action or "session" in action) and not mode.allow_identity_actions:
            return {
                "allowed": False,
                "auto_execute": False,
                "require_approval": True,
                "reason": "Identity actions restricted in current autonomy mode.",
            }

        if "mail" in action and not mode.allow_mail_actions:
            return {
                "allowed": False,
                "auto_execute": False,
                "require_approval": True,
                "reason": "Mail actions restricted in current autonomy mode.",
            }

        return {
            "allowed": True,
            "auto_execute": mode.auto_execute,
            "require_approval": mode.require_approval,
            "reason": f"{mode.name} policy evaluation passed.",
        }

    def _select_reviewer(self, policy_result: Dict[str, Any]) -> str:
        if policy_result.get("requires_legal"):
            return "legal"

        if policy_result.get("requires_manager"):
            return "manager"

        if policy_result.get("should_escalate"):
            return "senior_analyst"

        return "analyst"


def get_execution_engine(
    storage: Any,
    policy: Optional[ExecutionPolicy] = None,
    autonomy_mode: str = MANUAL,
) -> ExecutionEngine:
    return ExecutionEngine(
        storage=storage,
        policy=policy,
        autonomy_mode=autonomy_mode,
    )