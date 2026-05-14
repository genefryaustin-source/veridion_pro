from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class ApprovalAwareExecutor:
    """
    Safe AI execution layer.

    Responsibilities:
    - approval gating
    - execution holds
    - legal approvals
    - export-control approvals
    - containment approvals
    - closure approvals
    - audit logging
    - realtime event publishing

    This prevents AI from bypassing governance.
    """

    HIGH_RISK_ACTIONS = {
        "CLOSE_CASE",
        "MERGE_INVESTIGATIONS",
        "CONTAIN_USER",
        "DISABLE_ACCOUNT",
        "ISOLATE_ENDPOINT",
        "EXPORT_EVIDENCE",
        "DELETE_EVIDENCE",
        "EVIDENCE_DISPOSITION",
        "REVOKE_CREDENTIALS",
        "INITIATE_CONTAINMENT_REVIEW",
    }

    LEGAL_REVIEW_ACTIONS = {
        "REQUEST_LEGAL_REVIEW",
        "REQUEST_EXPORT_REVIEW",
        "EXPORT_EVIDENCE",
        "EVIDENCE_DISPOSITION",
    }

    SAFE_ACTIONS = {
        "ESCALATE_CASE",
        "ASSIGN_ANALYST",
        "REASSIGN_TIER_3",
        "PRESERVE_EVIDENCE",
        "REQUEST_ENDPOINT_SCAN",
        "LINK_RELATED_CASES",
        "CLUSTER_EVIDENCE",
        "INCREASE_SLA_PRIORITY",
    }

    def __init__(
        self,
        *,
        ledger: Any,
        approval_service: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
    ):
        self.ledger = ledger
        self.approval_service = approval_service
        self.event_bus = event_bus
        self.live_updates = live_updates

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def evaluate_action(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str = "ai_executor",
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        action_code = self._action_code(action)

        requires_approval = self.requires_approval(
            action=action,
        )

        approval_type = self.get_required_approval_type(
            action=action,
        ) if requires_approval else None

        return {
            "case_id": case_id,
            "action": action_code,
            "requires_approval": requires_approval,
            "approval_type": approval_type,
            "allowed_to_execute": not requires_approval,
            "risk_level": self.classify_action_risk(action),
            "actor": actor,
            "tenant_id": tenant_id,
            "evaluated_at_ms": _now_ms(),
        }

    def execute_or_gate(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        executor_callback: Any,
        actor: str = "ai_executor",
        tenant_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes action only if safe.

        If approval is required:
        - creates approval request
        - records hold
        - publishes event
        - returns paused status
        """

        evaluation = self.evaluate_action(
            case_id=case_id,
            action=action,
            actor=actor,
            tenant_id=tenant_id,
        )

        action_code = evaluation["action"]

        if dry_run:
            return {
                "status": "dry_run",
                "evaluation": evaluation,
                "timestamp_ms": _now_ms(),
            }

        if evaluation["requires_approval"]:
            approval = self.request_approval(
                case_id=case_id,
                action=action,
                actor=actor,
                tenant_id=tenant_id,
                approval_type=evaluation["approval_type"],
            )

            self.record_execution_hold(
                case_id=case_id,
                action=action,
                actor=actor,
                approval=approval,
            )

            self.publish_event(
                event_type="AI_EXECUTION_HELD_FOR_APPROVAL",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "action": action_code,
                    "approval": approval,
                    "evaluation": evaluation,
                },
            )

            return {
                "status": "approval_required",
                "evaluation": evaluation,
                "approval": approval,
                "timestamp_ms": _now_ms(),
            }

        try:
            result = executor_callback(action)

            self.record_audit_event(
                case_id=case_id,
                event_type="AI_ACTION_EXECUTED",
                actor=actor,
                details={
                    "action": action,
                    "evaluation": evaluation,
                    "result": result,
                },
            )

            self.publish_event(
                event_type="AI_ACTION_EXECUTED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "action": action_code,
                    "result": result,
                },
            )

            return {
                "status": "executed",
                "evaluation": evaluation,
                "result": result,
                "timestamp_ms": _now_ms(),
            }

        except Exception as exc:
            self.record_audit_event(
                case_id=case_id,
                event_type="AI_ACTION_EXECUTION_FAILED",
                actor=actor,
                details={
                    "action": action,
                    "evaluation": evaluation,
                    "error": str(exc),
                },
            )

            return {
                "status": "failed",
                "evaluation": evaluation,
                "error": str(exc),
                "timestamp_ms": _now_ms(),
            }

    # ------------------------------------------------------------------
    # Approval Rules
    # ------------------------------------------------------------------

    def requires_approval(
        self,
        *,
        action: Dict[str, Any],
    ) -> bool:
        action_code = self._action_code(action)

        if bool(action.get("requires_approval")):
            return True

        if action_code in self.HIGH_RISK_ACTIONS:
            return True

        if action_code in self.LEGAL_REVIEW_ACTIONS:
            return True

        if action.get("approval_type"):
            return True

        return False

    def classify_action_risk(
        self,
        action: Dict[str, Any],
    ) -> str:
        action_code = self._action_code(action)

        if action_code in self.HIGH_RISK_ACTIONS:
            return "HIGH"

        if action_code in self.LEGAL_REVIEW_ACTIONS:
            return "HIGH"

        if action_code in self.SAFE_ACTIONS:
            return "LOW"

        return "MEDIUM"

    def get_required_approval_type(
        self,
        *,
        action: Dict[str, Any],
    ) -> str:
        existing = action.get("approval_type")

        if existing:
            return existing

        action_code = self._action_code(action)

        if "LEGAL" in action_code:
            return "LEGAL_REVIEW"

        if "EXPORT" in action_code:
            return "EXPORT_CONTROL_REVIEW"

        if "CONTAIN" in action_code:
            return "CONTAINMENT_APPROVAL"

        if "MERGE" in action_code:
            return "CASE_MERGE_APPROVAL"

        if "CLOSE" in action_code:
            return "CLOSURE_APPROVAL"

        if "DELETE" in action_code or "DISPOSITION" in action_code:
            return "EVIDENCE_DISPOSITION_APPROVAL"

        return "AI_ACTION_APPROVAL"

    # ------------------------------------------------------------------
    # Approval Request
    # ------------------------------------------------------------------

    def request_approval(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
        approval_type: str,
    ) -> Dict[str, Any]:
        approval_id = f"APR-{uuid.uuid4().hex[:12].upper()}"

        payload = {
            "approval_id": approval_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "approval_type": approval_type,
            "action": action,
            "requested_by": actor,
            "requested_at_ms": _now_ms(),
            "status": "PENDING",
        }

        if self.approval_service is not None:
            for method_name in [
                "request_approval",
                "create_approval_request",
                "request_case_approval",
            ]:
                method = getattr(self.approval_service, method_name, None)

                if callable(method):
                    try:
                        result = method(
                            case_id=case_id,
                            approval_type=approval_type,
                            requested_by=actor,
                            reason=action.get("reason") or "AI approval gate",
                            details=payload,
                        )

                        payload["adapter"] = method_name
                        payload["result"] = result

                        return payload

                    except TypeError:
                        try:
                            result = method(case_id, approval_type)
                            payload["adapter"] = method_name
                            payload["result"] = result
                            return payload
                        except Exception:
                            pass

                    except Exception:
                        pass

        self.record_audit_event(
            case_id=case_id,
            event_type="AI_APPROVAL_REQUESTED",
            actor=actor,
            details=payload,
        )

        return payload

    # ------------------------------------------------------------------
    # Resume After Approval
    # ------------------------------------------------------------------

    def resume_if_approved(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        approval: Dict[str, Any],
        executor_callback: Any,
        actor: str = "approval_executor",
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        status = _upper(
            approval.get("status")
        )

        if status not in {
            "APPROVED",
            "GRANTED",
        }:
            return {
                "status": "not_approved",
                "approval_status": status,
                "timestamp_ms": _now_ms(),
            }

        try:
            result = executor_callback(action)

            self.record_audit_event(
                case_id=case_id,
                event_type="AI_APPROVED_ACTION_EXECUTED",
                actor=actor,
                details={
                    "action": action,
                    "approval": approval,
                    "result": result,
                },
            )

            self.publish_event(
                event_type="AI_APPROVED_ACTION_EXECUTED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "action": self._action_code(action),
                    "approval": approval,
                    "result": result,
                },
            )

            return {
                "status": "executed",
                "approval": approval,
                "result": result,
                "timestamp_ms": _now_ms(),
            }

        except Exception as exc:
            self.record_audit_event(
                case_id=case_id,
                event_type="AI_APPROVED_ACTION_FAILED",
                actor=actor,
                details={
                    "action": action,
                    "approval": approval,
                    "error": str(exc),
                },
            )

            return {
                "status": "failed",
                "approval": approval,
                "error": str(exc),
                "timestamp_ms": _now_ms(),
            }

    # ------------------------------------------------------------------
    # Holds / Audit
    # ------------------------------------------------------------------

    def record_execution_hold(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        approval: Dict[str, Any],
    ) -> None:
        self.record_audit_event(
            case_id=case_id,
            event_type="AI_EXECUTION_HOLD_CREATED",
            actor=actor,
            details={
                "action": action,
                "approval": approval,
            },
        )

    def record_audit_event(
        self,
        *,
        case_id: Any,
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
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

    # ------------------------------------------------------------------
    # Realtime
    # ------------------------------------------------------------------

    def publish_event(
        self,
        *,
        event_type: str,
        case_id: Any,
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
                    source="approval_aware_executor",
                )
            except Exception:
                pass

        if self.live_updates is not None:
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _action_code(
        self,
        action: Dict[str, Any],
    ) -> str:
        return _upper(
            action.get("action")
            or action.get("code")
            or action.get("label")
        )