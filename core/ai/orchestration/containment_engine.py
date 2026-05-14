from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class ContainmentEngine:
    """
    Approval-aware containment coordination engine.

    Coordinates containment actions such as:
    - disable account
    - isolate endpoint
    - suspend access
    - revoke credentials
    - preserve workstation state

    IMPORTANT:
    This engine does not bypass approval.
    High-risk containment actions are gated through approval_executor.
    """

    HIGH_RISK_CONTAINMENT_ACTIONS = {
        "DISABLE_ACCOUNT",
        "ISOLATE_ENDPOINT",
        "CONTAIN_USER",
        "REVOKE_CREDENTIALS",
        "SUSPEND_ACCESS",
        "QUARANTINE_MAILBOX",
    }

    SAFE_CONTAINMENT_ACTIONS = {
        "REQUEST_ENDPOINT_SCAN",
        "REQUEST_ACCESS_REVIEW",
        "PRESERVE_WORKSTATION_STATE",
        "RECOMMEND_CONTAINMENT",
        "CREATE_CONTAINMENT_TASK",
    }

    def __init__(
        self,
        *,
        ledger: Any,
        approval_executor: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
        endpoint_service: Any = None,
        identity_service: Any = None,
        mailbox_service: Any = None,
    ):
        self.ledger = ledger
        self.approval_executor = approval_executor
        self.event_bus = event_bus
        self.live_updates = live_updates
        self.endpoint_service = endpoint_service
        self.identity_service = identity_service
        self.mailbox_service = mailbox_service

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def recommend_containment(
        self,
        *,
        case_id: Any,
        context: Dict[str, Any],
        actor: str = "containment_engine",
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        severity = _upper(context.get("severity"))
        sla = context.get("sla") or {}
        entities = context.get("entities") or []
        campaign = context.get("campaign") or {}
        blast_radius = int(context.get("blast_radius_score") or 0)

        recommendations = []

        if severity == "CRITICAL" or sla.get("breached"):
            recommendations.append(
                self._make_action(
                    action="RECOMMEND_CONTAINMENT",
                    label="Recommend Containment Review",
                    priority="HIGH",
                    reason="Critical severity or SLA breach indicates containment review may be required.",
                    requires_approval=False,
                )
            )

        if campaign.get("campaign_id") or blast_radius >= 70:
            recommendations.append(
                self._make_action(
                    action="REQUEST_ENDPOINT_SCAN",
                    label="Request Endpoint Scan",
                    priority="HIGH",
                    reason="Campaign linkage or high blast radius warrants endpoint inspection.",
                    requires_approval=False,
                )
            )

        if self._has_credential_signal(entities, context):
            recommendations.append(
                self._make_action(
                    action="REVOKE_CREDENTIALS",
                    label="Revoke Credentials",
                    priority="CRITICAL",
                    reason="Credential exposure indicators detected.",
                    requires_approval=True,
                    approval_type="CONTAINMENT_APPROVAL",
                )
            )

        if self._has_user_risk_signal(entities, context):
            recommendations.append(
                self._make_action(
                    action="CONTAIN_USER",
                    label="Contain User",
                    priority="HIGH",
                    reason="User-risk or insider-risk indicators detected.",
                    requires_approval=True,
                    approval_type="CONTAINMENT_APPROVAL",
                )
            )

        if not recommendations:
            recommendations.append(
                self._make_action(
                    action="REQUEST_ACCESS_REVIEW",
                    label="Request Access Review",
                    priority="MEDIUM",
                    reason="No immediate containment trigger detected; access review is recommended.",
                    requires_approval=False,
                )
            )

        self._record_event(
            case_id=case_id,
            event_type="CONTAINMENT_RECOMMENDATIONS_GENERATED",
            actor=actor,
            details={
                "recommendations": recommendations,
                "tenant_id": tenant_id,
            },
        )

        return {
            "case_id": case_id,
            "tenant_id": tenant_id,
            "recommendations": recommendations,
            "generated_at_ms": _now_ms(),
            "engine": "ContainmentEngine",
        }

    def execute_containment_action(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str = "containment_engine",
        tenant_id: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        action_code = _upper(action.get("action") or action.get("label"))

        if dry_run:
            return {
                "status": "dry_run",
                "case_id": case_id,
                "action": action_code,
                "requires_approval": self.requires_approval(action),
                "timestamp_ms": _now_ms(),
            }

        if self.requires_approval(action):
            return self._gate_containment_action(
                case_id=case_id,
                action=action,
                actor=actor,
                tenant_id=tenant_id,
            )

        return self._execute_safe_containment(
            case_id=case_id,
            action=action,
            actor=actor,
            tenant_id=tenant_id,
        )

    def execute_containment_plan(
        self,
        *,
        case_id: Any,
        actions: List[Dict[str, Any]],
        actor: str = "containment_engine",
        tenant_id: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        plan_id = f"CONT-{uuid.uuid4().hex[:12].upper()}"

        results = []

        self._record_event(
            case_id=case_id,
            event_type="CONTAINMENT_PLAN_STARTED",
            actor=actor,
            details={
                "plan_id": plan_id,
                "action_count": len(actions),
                "dry_run": dry_run,
                "tenant_id": tenant_id,
            },
        )

        for idx, action in enumerate(actions):
            result = self.execute_containment_action(
                case_id=case_id,
                action={
                    **action,
                    "step_index": idx + 1,
                    "plan_id": plan_id,
                },
                actor=actor,
                tenant_id=tenant_id,
                dry_run=dry_run,
            )

            results.append(result)

            if result.get("status") in {"approval_required", "failed"}:
                break

        status = self._final_status(results)

        self._record_event(
            case_id=case_id,
            event_type="CONTAINMENT_PLAN_COMPLETED",
            actor=actor,
            details={
                "plan_id": plan_id,
                "status": status,
                "results": results,
                "tenant_id": tenant_id,
            },
        )

        self._publish_realtime(
            event_type="CONTAINMENT_PLAN_COMPLETED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload={
                "plan_id": plan_id,
                "status": status,
                "result_count": len(results),
            },
        )

        return {
            "plan_id": plan_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "status": status,
            "results": results,
            "dry_run": dry_run,
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Approval / Risk
    # ------------------------------------------------------------------

    def requires_approval(self, action: Dict[str, Any]) -> bool:
        action_code = _upper(action.get("action") or action.get("label"))

        if bool(action.get("requires_approval")):
            return True

        return action_code in self.HIGH_RISK_CONTAINMENT_ACTIONS

    def _gate_containment_action(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.approval_executor is not None:
            return self.approval_executor.execute_or_gate(
                case_id=case_id,
                action={
                    **action,
                    "approval_type": action.get("approval_type") or "CONTAINMENT_APPROVAL",
                    "requires_approval": True,
                },
                executor_callback=lambda approved_action: self._execute_safe_containment(
                    case_id=case_id,
                    action={
                        **approved_action,
                        "requires_approval": False,
                    },
                    actor=actor,
                    tenant_id=tenant_id,
                ),
                actor=actor,
                tenant_id=tenant_id,
                dry_run=False,
            )

        self._record_event(
            case_id=case_id,
            event_type="CONTAINMENT_APPROVAL_REQUIRED",
            actor=actor,
            details={
                "action": action,
                "tenant_id": tenant_id,
            },
        )

        self._publish_realtime(
            event_type="CONTAINMENT_APPROVAL_REQUIRED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload={
                "action": action,
                "approval_type": action.get("approval_type") or "CONTAINMENT_APPROVAL",
            },
        )

        return {
            "status": "approval_required",
            "case_id": case_id,
            "action": _upper(action.get("action") or action.get("label")),
            "approval_type": action.get("approval_type") or "CONTAINMENT_APPROVAL",
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Safe Containment Execution
    # ------------------------------------------------------------------

    def _execute_safe_containment(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        action_code = _upper(action.get("action") or action.get("label"))

        try:
            if action_code == "REQUEST_ENDPOINT_SCAN":
                result = self._request_endpoint_scan(
                    case_id=case_id,
                    action=action,
                    actor=actor,
                    tenant_id=tenant_id,
                )

            elif action_code == "REQUEST_ACCESS_REVIEW":
                result = self._request_access_review(
                    case_id=case_id,
                    action=action,
                    actor=actor,
                    tenant_id=tenant_id,
                )

            elif action_code == "PRESERVE_WORKSTATION_STATE":
                result = self._preserve_workstation_state(
                    case_id=case_id,
                    action=action,
                    actor=actor,
                    tenant_id=tenant_id,
                )

            elif action_code in {
                "DISABLE_ACCOUNT",
                "CONTAIN_USER",
                "SUSPEND_ACCESS",
                "REVOKE_CREDENTIALS",
            }:
                result = self._identity_action(
                    case_id=case_id,
                    action=action,
                    actor=actor,
                    tenant_id=tenant_id,
                )

            elif action_code == "ISOLATE_ENDPOINT":
                result = self._endpoint_isolation(
                    case_id=case_id,
                    action=action,
                    actor=actor,
                    tenant_id=tenant_id,
                )

            elif action_code == "QUARANTINE_MAILBOX":
                result = self._mailbox_quarantine(
                    case_id=case_id,
                    action=action,
                    actor=actor,
                    tenant_id=tenant_id,
                )

            else:
                result = self._record_marker(
                    case_id=case_id,
                    actor=actor,
                    marker=f"CONTAINMENT_ACTION_{action_code}",
                    details=action,
                )

            self._record_event(
                case_id=case_id,
                event_type="CONTAINMENT_ACTION_EXECUTED",
                actor=actor,
                details={
                    "action": action,
                    "result": result,
                    "tenant_id": tenant_id,
                },
            )

            self._publish_realtime(
                event_type="CONTAINMENT_ACTION_EXECUTED",
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
                "case_id": case_id,
                "action": action_code,
                "result": result,
                "timestamp_ms": _now_ms(),
            }

        except Exception as exc:
            self._record_event(
                case_id=case_id,
                event_type="CONTAINMENT_ACTION_FAILED",
                actor=actor,
                details={
                    "action": action,
                    "error": str(exc),
                    "tenant_id": tenant_id,
                },
            )

            return {
                "status": "failed",
                "case_id": case_id,
                "action": action_code,
                "error": str(exc),
                "timestamp_ms": _now_ms(),
            }

    # ------------------------------------------------------------------
    # Adapter Actions
    # ------------------------------------------------------------------

    def _request_endpoint_scan(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.endpoint_service is not None:
            for method_name in [
                "request_endpoint_scan",
                "enqueue_endpoint_scan",
                "scan_endpoint_for_case",
            ]:
                method = getattr(self.endpoint_service, method_name, None)

                if callable(method):
                    try:
                        return {
                            "adapter": method_name,
                            "result": method(
                                case_id=case_id,
                                requested_by=actor,
                                tenant_id=tenant_id,
                                details=action,
                            ),
                        }
                    except TypeError:
                        return {
                            "adapter": method_name,
                            "result": method(case_id),
                        }

        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="ENDPOINT_SCAN_REQUESTED",
            details={
                "tenant_id": tenant_id,
                "action": action,
            },
        )

    def _request_access_review(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="ACCESS_REVIEW_REQUESTED",
            details={
                "tenant_id": tenant_id,
                "action": action,
            },
        )

    def _preserve_workstation_state(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.endpoint_service is not None:
            for method_name in [
                "preserve_workstation_state",
                "snapshot_endpoint",
                "preserve_endpoint_state",
            ]:
                method = getattr(self.endpoint_service, method_name, None)

                if callable(method):
                    try:
                        return {
                            "adapter": method_name,
                            "result": method(
                                case_id=case_id,
                                requested_by=actor,
                                tenant_id=tenant_id,
                                details=action,
                            ),
                        }
                    except TypeError:
                        return {
                            "adapter": method_name,
                            "result": method(case_id),
                        }

        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="WORKSTATION_STATE_PRESERVATION_REQUESTED",
            details={
                "tenant_id": tenant_id,
                "action": action,
            },
        )

    def _identity_action(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        action_code = _upper(action.get("action") or action.get("label"))

        if self.identity_service is not None:
            adapter_methods = {
                "DISABLE_ACCOUNT": [
                    "disable_account",
                    "disable_user",
                ],
                "CONTAIN_USER": [
                    "contain_user",
                    "restrict_user",
                ],
                "SUSPEND_ACCESS": [
                    "suspend_access",
                    "restrict_access",
                ],
                "REVOKE_CREDENTIALS": [
                    "revoke_credentials",
                    "rotate_credentials",
                ],
            }

            for method_name in adapter_methods.get(action_code, []):
                method = getattr(self.identity_service, method_name, None)

                if callable(method):
                    try:
                        return {
                            "adapter": method_name,
                            "result": method(
                                case_id=case_id,
                                requested_by=actor,
                                tenant_id=tenant_id,
                                details=action,
                            ),
                        }
                    except TypeError:
                        return {
                            "adapter": method_name,
                            "result": method(case_id),
                        }

        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker=f"IDENTITY_CONTAINMENT_{action_code}_REQUESTED",
            details={
                "tenant_id": tenant_id,
                "action": action,
            },
        )

    def _endpoint_isolation(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.endpoint_service is not None:
            for method_name in [
                "isolate_endpoint",
                "contain_endpoint",
                "network_isolate_endpoint",
            ]:
                method = getattr(self.endpoint_service, method_name, None)

                if callable(method):
                    try:
                        return {
                            "adapter": method_name,
                            "result": method(
                                case_id=case_id,
                                requested_by=actor,
                                tenant_id=tenant_id,
                                details=action,
                            ),
                        }
                    except TypeError:
                        return {
                            "adapter": method_name,
                            "result": method(case_id),
                        }

        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="ENDPOINT_ISOLATION_REQUESTED",
            details={
                "tenant_id": tenant_id,
                "action": action,
            },
        )

    def _mailbox_quarantine(
        self,
        *,
        case_id: Any,
        action: Dict[str, Any],
        actor: str,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.mailbox_service is not None:
            for method_name in [
                "quarantine_mailbox",
                "restrict_mailbox",
                "hold_mailbox",
            ]:
                method = getattr(self.mailbox_service, method_name, None)

                if callable(method):
                    try:
                        return {
                            "adapter": method_name,
                            "result": method(
                                case_id=case_id,
                                requested_by=actor,
                                tenant_id=tenant_id,
                                details=action,
                            ),
                        }
                    except TypeError:
                        return {
                            "adapter": method_name,
                            "result": method(case_id),
                        }

        return self._record_marker(
            case_id=case_id,
            actor=actor,
            marker="MAILBOX_QUARANTINE_REQUESTED",
            details={
                "tenant_id": tenant_id,
                "action": action,
            },
        )

    # ------------------------------------------------------------------
    # Signal Detection
    # ------------------------------------------------------------------

    def _has_credential_signal(
        self,
        entities: List[Any],
        context: Dict[str, Any],
    ) -> bool:
        blob = " ".join([
            str(entities),
            str(context.get("case", {})),
            str(context.get("evidence", [])),
        ]).upper()

        terms = [
            "PASSWORD",
            "TOKEN",
            "API_KEY",
            "SECRET",
            "CREDENTIAL",
        ]

        return any(term in blob for term in terms)

    def _has_user_risk_signal(
        self,
        entities: List[Any],
        context: Dict[str, Any],
    ) -> bool:
        blob = " ".join([
            str(entities),
            str(context.get("case", {})),
            str(context.get("evidence", [])),
            str(context.get("campaign", {})),
        ]).upper()

        terms = [
            "INSIDER",
            "PERSONAL_EMAIL",
            "MASS_DOWNLOAD",
            "USB",
            "EXFILTRATION",
        ]

        return any(term in blob for term in terms)

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
                    source="containment_engine",
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

    def _record_marker(
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

    def _make_action(
        self,
        *,
        action: str,
        label: str,
        priority: str,
        reason: str,
        requires_approval: bool = False,
        approval_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "action": action,
            "label": label,
            "priority": priority,
            "reason": reason,
            "requires_approval": requires_approval,
            "approval_type": approval_type,
            "category": "CONTAINMENT",
            "generated_at_ms": _now_ms(),
            "engine": "ContainmentEngine",
        }

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

        if any(r.get("status") == "dry_run" for r in results):
            return "dry_run"

        return "completed"