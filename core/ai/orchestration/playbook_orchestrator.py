from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class PlaybookOrchestrator:
    """
    Approval-aware AI playbook orchestration engine.

    Converts AI recommendations into governed operational workflows.

    Handles:
    - playbook execution
    - multi-step orchestration
    - approval gates
    - audit events
    - realtime events
    - safe AI action tracking
    """

    APPROVAL_REQUIRED_ACTIONS = {
        "CLOSE_CASE",
        "MERGE_INVESTIGATIONS",
        "CONTAIN_USER",
        "DISABLE_ACCOUNT",
        "ISOLATE_ENDPOINT",
        "EXPORT_EVIDENCE",
        "DELETE_EVIDENCE",
        "EVIDENCE_DISPOSITION",
        "REQUEST_LEGAL_REVIEW",
        "REQUEST_EXPORT_REVIEW",
        "INITIATE_CONTAINMENT_REVIEW",
    }

    SAFE_AUTO_ACTIONS = {
        "ESCALATE_CASE",
        "ASSIGN_ANALYST",
        "REASSIGN_TIER_3",
        "PRESERVE_EVIDENCE",
        "LINK_RELATED_CASES",
        "CLUSTER_EVIDENCE",
        "REQUEST_ENDPOINT_SCAN",
        "INCREASE_SLA_PRIORITY",
        "QUEUE_REFRESH_REQUIRED",
    }

    def __init__(
        self,
        *,
        ledger: Any,
        playbook_service: Any = None,
        approval_service: Any = None,
        escalation_service: Any = None,
        assignment_service: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
    ):
        self.ledger = ledger
        self.playbook_service = playbook_service
        self.approval_service = approval_service
        self.escalation_service = escalation_service
        self.assignment_service = assignment_service
        self.event_bus = event_bus
        self.live_updates = live_updates

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_playbook(
        self,
        *,
        case_id: Any,
        playbook: str,
        actor: str = "ai_orchestrator",
        tenant_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        orchestration_id = self._new_orchestration_id()

        self._record_event(
            case_id=case_id,
            event_type="AI_PLAYBOOK_STARTED",
            actor=actor,
            details={
                "orchestration_id": orchestration_id,
                "playbook": playbook,
                "dry_run": dry_run,
            },
        )

        actions = self._load_playbook_actions(playbook)

        results = []

        for idx, action in enumerate(actions):
            result = self.execute_action(
                case_id=case_id,
                action=action,
                actor=actor,
                tenant_id=tenant_id,
                orchestration_id=orchestration_id,
                step_index=idx + 1,
                dry_run=dry_run,
            )

            results.append(result)

            if result.get("status") == "failed":
                break

            if result.get("status") == "approval_required":
                # Pause playbook execution until approval is granted.
                break

        status = self._final_status(results)

        self._record_event(
            case_id=case_id,
            event_type="AI_PLAYBOOK_COMPLETED" if status == "completed" else "AI_PLAYBOOK_PAUSED",
            actor=actor,
            details={
                "orchestration_id": orchestration_id,
                "playbook": playbook,
                "status": status,
                "results": results,
            },
        )

        self._publish_realtime(
            event_type="AI_PLAYBOOK_COMPLETED" if status == "completed" else "AI_PLAYBOOK_PAUSED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload={
                "orchestration_id": orchestration_id,
                "playbook": playbook,
                "status": status,
            },
        )

        return {
            "orchestration_id": orchestration_id,
            "case_id": case_id,
            "playbook": playbook,
            "status": status,
            "results": results,
            "dry_run": dry_run,
            "generated_at_ms": _now_ms(),
        }

    def execute_recommendation(
        self,
        *,
        case_id: Any,
        recommendation: Dict[str, Any],
        actor: str = "ai_orchestrator",
        tenant_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        orchestration_id = self._new_orchestration_id()

        return self.execute_action(
            case_id=case_id,
            action=recommendation,
            actor=actor,
            tenant_id=tenant_id,
            orchestration_id=orchestration_id,
            step_index=1,
            dry_run=dry_run,
        )

    def execute_actions(
        self,
        *,
        case_id: Any,
        actions: List[Dict[str, Any]],
        actor: str = "ai_orchestrator",
        tenant_id: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        orchestration_id = self._new_orchestration_id()

        results = []

        self._record_event(
            case_id=case_id,
            event_type="AI_ORCHESTRATION_STARTED",
            actor=actor,
            details={
                "orchestration_id": orchestration_id,
                "action_count": len(actions),
                "dry_run": dry_run,
            },
        )

        for idx, action in enumerate(actions):
            result = self.execute_action(
                case_id=case_id,
                action=action,
                actor=actor,
                tenant_id=tenant_id,
                orchestration_id=orchestration_id,
                step_index=idx + 1,
                dry_run=dry_run,
            )

            results.append(result)

            if result.get("status") in {"failed", "approval_required"}:
                break

        status = self._final_status(results)

        self._record_event(
            case_id=case_id,
            event_type="AI_ORCHESTRATION_COMPLETED" if status == "completed" else "AI_ORCHESTRATION_PAUSED",
            actor=actor,
            details={
                "orchestration_id": orchestration_id,
                "status": status,
                "results": results,
            },
        )

        return {
            "orchestration_id": orchestration_id,
            "case_id": case_id,
            "status": status,
            "results": results,
            "dry_run": dry_run,
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Action Execution
    # ------------------------------------------------------------------

    def execute_action(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
        orchestration_id: str,
        step_index: int,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        action_code = _upper(
            action.get("action")
            or action.get("code")
            or action.get("label")
        )

        requires_approval = bool(
            action.get("requires_approval")
        ) or action_code in self.APPROVAL_REQUIRED_ACTIONS

        result = {
            "orchestration_id": orchestration_id,
            "case_id": case_id,
            "step_index": step_index,
            "action": action_code,
            "label": action.get("label"),
            "status": "pending",
            "requires_approval": requires_approval,
            "dry_run": dry_run,
            "timestamp_ms": _now_ms(),
        }

        self._record_event(
            case_id=case_id,
            event_type="AI_ACTION_STARTED",
            actor=actor,
            details={
                "orchestration_id": orchestration_id,
                "step_index": step_index,
                "action": action,
                "dry_run": dry_run,
            },
        )

        if requires_approval:
            approval = self._request_approval(
                case_id=case_id,
                action=action,
                actor=actor,
                tenant_id=tenant_id,
                orchestration_id=orchestration_id,
                dry_run=dry_run,
            )

            result["status"] = "approval_required"
            result["approval"] = approval

            self._record_event(
                case_id=case_id,
                event_type="AI_APPROVAL_REQUIRED",
                actor=actor,
                details={
                    "orchestration_id": orchestration_id,
                    "step_index": step_index,
                    "action": action,
                    "approval": approval,
                },
            )

            self._publish_realtime(
                event_type="AI_APPROVAL_REQUIRED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "orchestration_id": orchestration_id,
                    "action": action_code,
                    "approval": approval,
                },
            )

            return result

        if dry_run:
            result["status"] = "dry_run"
            return result

        try:
            execution = self._execute_safe_action(
                case_id=case_id,
                action_code=action_code,
                action=action,
                actor=actor,
                tenant_id=tenant_id,
            )

            result["status"] = "completed"
            result["execution"] = execution

            self._record_event(
                case_id=case_id,
                event_type="AI_ACTION_EXECUTED",
                actor=actor,
                details={
                    "orchestration_id": orchestration_id,
                    "step_index": step_index,
                    "action": action_code,
                    "execution": execution,
                },
            )

            self._publish_realtime(
                event_type="AI_ACTION_EXECUTED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "orchestration_id": orchestration_id,
                    "action": action_code,
                    "execution": execution,
                },
            )

        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)

            self._record_event(
                case_id=case_id,
                event_type="AI_ACTION_FAILED",
                actor=actor,
                details={
                    "orchestration_id": orchestration_id,
                    "step_index": step_index,
                    "action": action_code,
                    "error": str(exc),
                },
            )

        return result

    # ------------------------------------------------------------------
    # Safe Actions
    # ------------------------------------------------------------------

    def _execute_safe_action(
        self,
        *,
        case_id: Any,
        action_code: str,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if action_code == "ESCALATE_CASE":
            return self._escalate_case(
                case_id=case_id,
                actor=actor,
                tenant_id=tenant_id,
                reason=action.get("reason") or "AI orchestrator escalation",
            )

        if action_code in {"ASSIGN_ANALYST", "REASSIGN_TIER_3"}:
            return self._assign_case(
                case_id=case_id,
                actor=actor,
                tenant_id=tenant_id,
                analyst=action.get("analyst") or action.get("assigned_to"),
                reason=action.get("reason") or "AI orchestrator assignment",
            )

        if action_code == "PRESERVE_EVIDENCE":
            return self._preserve_evidence(
                case_id=case_id,
                actor=actor,
                reason=action.get("reason") or "AI orchestrator evidence preservation",
            )

        if action_code == "LINK_RELATED_CASES":
            return self._record_operational_marker(
                case_id=case_id,
                actor=actor,
                marker="RELATED_CASE_LINK_RECOMMENDED",
                details=action,
            )

        if action_code == "CLUSTER_EVIDENCE":
            return self._record_operational_marker(
                case_id=case_id,
                actor=actor,
                marker="EVIDENCE_CLUSTERING_RECOMMENDED",
                details=action,
            )

        if action_code == "REQUEST_ENDPOINT_SCAN":
            return self._record_operational_marker(
                case_id=case_id,
                actor=actor,
                marker="ENDPOINT_SCAN_REQUESTED",
                details=action,
            )

        if action_code == "INCREASE_SLA_PRIORITY":
            return self._record_operational_marker(
                case_id=case_id,
                actor=actor,
                marker="SLA_PRIORITY_INCREASED",
                details=action,
            )

        return self._record_operational_marker(
            case_id=case_id,
            actor=actor,
            marker=f"AI_SAFE_ACTION_{action_code}",
            details=action,
        )

    # ------------------------------------------------------------------
    # Operational Adapters
    # ------------------------------------------------------------------

    def _escalate_case(
        self,
        *,
        case_id: Any,
        actor: str,
        tenant_id: Optional[str],
        reason: str,
    ) -> Dict[str, Any]:
        if self.escalation_service is not None:
            for method_name in [
                "auto_escalate_case",
                "escalate_case",
                "manual_escalate_case",
            ]:
                method = getattr(self.escalation_service, method_name, None)
                if callable(method):
                    try:
                        result = method(
                            case_id=case_id,
                            actor=actor,
                            reason=reason,
                        )
                        return {
                            "adapter": method_name,
                            "result": result,
                        }
                    except TypeError:
                        result = method(case_id, reason)
                        return {
                            "adapter": method_name,
                            "result": result,
                        }

        return self._record_operational_marker(
            case_id=case_id,
            actor=actor,
            marker="CASE_ESCALATION_RECOMMENDED",
            details={
                "reason": reason,
                "tenant_id": tenant_id,
            },
        )

    def _assign_case(
        self,
        *,
        case_id: Any,
        actor: str,
        tenant_id: Optional[str],
        analyst: Optional[str],
        reason: str,
    ) -> Dict[str, Any]:
        if not analyst:
            return self._record_operational_marker(
                case_id=case_id,
                actor=actor,
                marker="CASE_ASSIGNMENT_RECOMMENDED",
                details={
                    "reason": reason,
                    "tenant_id": tenant_id,
                },
            )

        if self.assignment_service is not None:
            for method_name in [
                "assign_case",
                "assign_case_to_user",
                "assign",
            ]:
                method = getattr(self.assignment_service, method_name, None)
                if callable(method):
                    try:
                        result = method(
                            case_id=case_id,
                            analyst_id=analyst,
                            assigned_by=actor,
                            reason=reason,
                        )
                        return {
                            "adapter": method_name,
                            "result": result,
                        }
                    except TypeError:
                        result = method(case_id, analyst)
                        return {
                            "adapter": method_name,
                            "result": result,
                        }

        return self._record_operational_marker(
            case_id=case_id,
            actor=actor,
            marker="CASE_ASSIGNMENT_RECOMMENDED",
            details={
                "analyst": analyst,
                "reason": reason,
                "tenant_id": tenant_id,
            },
        )

    def _preserve_evidence(
        self,
        *,
        case_id: Any,
        actor: str,
        reason: str,
    ) -> Dict[str, Any]:
        for method_name in [
            "preserve_case_evidence",
            "mark_case_evidence_preserved",
            "lock_case_evidence",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    result = method(
                        case_id=case_id,
                        actor=actor,
                        reason=reason,
                    )
                    return {
                        "adapter": method_name,
                        "result": result,
                    }
                except TypeError:
                    result = method(case_id)
                    return {
                        "adapter": method_name,
                        "result": result,
                    }

        return self._record_operational_marker(
            case_id=case_id,
            actor=actor,
            marker="EVIDENCE_PRESERVATION_REQUESTED",
            details={
                "reason": reason,
            },
        )

    # ------------------------------------------------------------------
    # Approvals
    # ------------------------------------------------------------------

    def _request_approval(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
        orchestration_id: str,
        dry_run: bool,
    ) -> Dict[str, Any]:
        approval_type = (
            action.get("approval_type")
            or self._default_approval_type(action)
        )

        approval_payload = {
            "orchestration_id": orchestration_id,
            "case_id": case_id,
            "action": action,
            "approval_type": approval_type,
            "tenant_id": tenant_id,
            "requested_by": actor,
            "dry_run": dry_run,
            "requested_at_ms": _now_ms(),
        }

        if dry_run:
            return {
                "status": "dry_run",
                "approval_type": approval_type,
                "payload": approval_payload,
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
                            reason=action.get("reason") or "AI orchestration approval gate",
                            details=approval_payload,
                        )
                        return {
                            "status": "requested",
                            "adapter": method_name,
                            "approval_type": approval_type,
                            "result": result,
                        }
                    except TypeError:
                        result = method(case_id, approval_type)
                        return {
                            "status": "requested",
                            "adapter": method_name,
                            "approval_type": approval_type,
                            "result": result,
                        }

        self._record_event(
            case_id=case_id,
            event_type="AI_APPROVAL_REQUESTED",
            actor=actor,
            details=approval_payload,
        )

        return {
            "status": "requested_event_only",
            "approval_type": approval_type,
            "payload": approval_payload,
        }

    def resume_after_approval(
        self,
        *,
        case_id: Any,
        orchestration_id: str,
        approved_action: Dict[str, Any],
        actor: str = "approval_executor",
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes a previously approval-gated action after approval.
        """

        return self.execute_action(
            case_id=case_id,
            action={
                **approved_action,
                "requires_approval": False,
            },
            actor=actor,
            tenant_id=tenant_id,
            orchestration_id=orchestration_id,
            step_index=_safe_int(approved_action.get("step_index"), 1),
            dry_run=False,
        )

    # ------------------------------------------------------------------
    # Playbook Loading
    # ------------------------------------------------------------------

    def _load_playbook_actions(
        self,
        playbook: str,
    ) -> List[Dict[str, Any]]:
        if self.playbook_service is not None:
            method = getattr(self.playbook_service, "generate_playbook_actions", None)

            if callable(method):
                try:
                    return method(playbook_name=playbook)
                except TypeError:
                    try:
                        return method(playbook)
                    except Exception:
                        pass

        # Minimal fallback playbooks
        playbook_key = _upper(playbook)

        if "EXPORT" in playbook_key:
            return [
                {
                    "action": "ESCALATE_CASE",
                    "label": "Escalate Case",
                    "priority": "CRITICAL",
                    "reason": "Export-control playbook started.",
                },
                {
                    "action": "REQUEST_LEGAL_REVIEW",
                    "label": "Request Legal Review",
                    "priority": "CRITICAL",
                    "requires_approval": True,
                    "approval_type": "LEGAL_REVIEW",
                    "reason": "Export-control playbook requires legal review.",
                },
                {
                    "action": "PRESERVE_EVIDENCE",
                    "label": "Preserve Evidence",
                    "priority": "CRITICAL",
                    "reason": "Preserve evidence for export-control investigation.",
                },
            ]

        if "INSIDER" in playbook_key:
            return [
                {
                    "action": "REQUEST_ENDPOINT_SCAN",
                    "label": "Request Endpoint Scan",
                    "priority": "HIGH",
                    "reason": "Insider-threat playbook started.",
                },
                {
                    "action": "INITIATE_CONTAINMENT_REVIEW",
                    "label": "Initiate Containment Review",
                    "priority": "HIGH",
                    "requires_approval": True,
                    "approval_type": "CONTAINMENT_APPROVAL",
                    "reason": "Containment requires approval.",
                },
            ]

        return [
            {
                "action": "PRESERVE_EVIDENCE",
                "label": "Preserve Evidence",
                "priority": "MEDIUM",
                "reason": "Default playbook evidence preservation.",
            }
        ]

    # ------------------------------------------------------------------
    # Events / Realtime
    # ------------------------------------------------------------------

    def _record_event(
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

    def _publish_realtime(
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
                    source="playbook_orchestrator",
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

    def _record_operational_marker(
        self,
        *,
        case_id: Any,
        actor: str,
        marker: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._record_event(
            case_id=case_id,
            event_type=marker,
            actor=actor,
            details=details,
        )

        return {
            "marker": marker,
            "recorded": True,
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _default_approval_type(
        self,
        action: Dict[str, Any],
    ) -> str:
        action_code = _upper(action.get("action") or action.get("label"))

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

        return "AI_ACTION_APPROVAL"

    def _final_status(
        self,
        results: List[Dict[str, Any]],
    ) -> str:
        if not results:
            return "no_actions"

        if any(r.get("status") == "failed" for r in results):
            return "failed"

        if any(r.get("status") == "approval_required" for r in results):
            return "paused_for_approval"

        if all(r.get("status") in {"completed", "dry_run"} for r in results):
            return "completed"

        return "partial"

    def _new_orchestration_id(self) -> str:
        return f"ORCH-{uuid.uuid4().hex[:12].upper()}"