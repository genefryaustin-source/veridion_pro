"""
Bulk Case Service

Enterprise-safe bulk operations for the SOC Command Center.

Supports:
- bulk assignment
- bulk escalation
- bulk close
- bulk status transition
- bulk approval request

This service keeps investigation_queue.py thin and prevents
business logic from being embedded directly in Streamlit UI code.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class BulkActionResult:
    action: str
    requested: int = 0
    succeeded: int = 0
    failed: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)

    def add_success(self, case_id: Any, message: str = "ok", details: Optional[Dict[str, Any]] = None):
        self.succeeded += 1
        self.results.append({
            "case_id": case_id,
            "status": "success",
            "message": message,
            "details": details or {},
        })

    def add_failure(self, case_id: Any, message: str, details: Optional[Dict[str, Any]] = None):
        self.failed += 1
        self.results.append({
            "case_id": case_id,
            "status": "failed",
            "message": message,
            "details": details or {},
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "requested": self.requested,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "results": self.results,
        }


class BulkCaseService:
    """
    Bulk operations wrapper for command-center actions.

    Expected injected services:
        ledger
        assignment_service
        escalation_service
        approval_service
        state_machine

    The service is intentionally defensive so it can work with your existing
    evolving ledger/service methods without breaking the UI.
    """

    def __init__(
        self,
        ledger: Any,
        assignment_service: Any = None,
        escalation_service: Any = None,
        approval_service: Any = None,
        state_machine: Any = None,
    ):
        self.ledger = ledger
        self.assignment_service = assignment_service
        self.escalation_service = escalation_service
        self.approval_service = approval_service
        self.state_machine = state_machine

    # ---------------------------------------------------------------------
    # Public bulk actions
    # ---------------------------------------------------------------------

    def bulk_assign_cases(
        self,
        case_ids: List[Any],
        analyst_id: str,
        assigned_by: str = "system",
        reason: str = "Bulk assignment from Command Center",
    ) -> Dict[str, Any]:
        result = BulkActionResult(action="bulk_assign", requested=len(case_ids))

        for case_id in self._clean_case_ids(case_ids):
            try:
                if not analyst_id:
                    raise ValueError("analyst_id is required")

                self._assign_case(
                    case_id=case_id,
                    analyst_id=analyst_id,
                    assigned_by=assigned_by,
                    reason=reason,
                )

                self._add_case_event(
                    case_id=case_id,
                    event_type="CASE_BULK_ASSIGNED",
                    actor=assigned_by,
                    details={
                        "analyst_id": analyst_id,
                        "reason": reason,
                    },
                )

                result.add_success(case_id, f"Assigned to {analyst_id}")

            except Exception as exc:
                result.add_failure(case_id, str(exc), self._error_details())

        return result.to_dict()

    def bulk_escalate_cases(
        self,
        case_ids: List[Any],
        actor: str = "system",
        reason: str = "Bulk escalation from Command Center",
        escalation_level: Optional[int] = None,
    ) -> Dict[str, Any]:
        result = BulkActionResult(action="bulk_escalate", requested=len(case_ids))

        for case_id in self._clean_case_ids(case_ids):
            try:
                self._escalate_case(
                    case_id=case_id,
                    actor=actor,
                    reason=reason,
                    escalation_level=escalation_level,
                )

                self._add_case_event(
                    case_id=case_id,
                    event_type="CASE_BULK_ESCALATED",
                    actor=actor,
                    details={
                        "reason": reason,
                        "escalation_level": escalation_level,
                    },
                )

                result.add_success(case_id, "Escalated")

            except Exception as exc:
                result.add_failure(case_id, str(exc), self._error_details())

        return result.to_dict()

    def bulk_close_cases(
        self,
        case_ids: List[Any],
        actor: str = "system",
        reason: str = "Bulk close from Command Center",
        require_approval: bool = True,
    ) -> Dict[str, Any]:
        result = BulkActionResult(action="bulk_close", requested=len(case_ids))

        for case_id in self._clean_case_ids(case_ids):
            try:
                if require_approval and self.approval_service is not None:
                    self._request_approval(
                        case_id=case_id,
                        approval_type="CLOSURE_APPROVAL",
                        requested_by=actor,
                        reason=reason,
                    )

                    self._add_case_event(
                        case_id=case_id,
                        event_type="CASE_CLOSURE_APPROVAL_REQUESTED",
                        actor=actor,
                        details={"reason": reason},
                    )

                    result.add_success(case_id, "Closure approval requested")
                else:
                    self._transition_case(
                        case_id=case_id,
                        to_state="CLOSED",
                        actor=actor,
                        reason=reason,
                    )

                    self._add_case_event(
                        case_id=case_id,
                        event_type="CASE_BULK_CLOSED",
                        actor=actor,
                        details={"reason": reason},
                    )

                    result.add_success(case_id, "Closed")

            except Exception as exc:
                result.add_failure(case_id, str(exc), self._error_details())

        return result.to_dict()

    def bulk_transition_cases(
        self,
        case_ids: List[Any],
        to_state: str,
        actor: str = "system",
        reason: str = "Bulk status transition from Command Center",
    ) -> Dict[str, Any]:
        result = BulkActionResult(action="bulk_transition", requested=len(case_ids))

        for case_id in self._clean_case_ids(case_ids):
            try:
                if not to_state:
                    raise ValueError("to_state is required")

                self._transition_case(
                    case_id=case_id,
                    to_state=to_state,
                    actor=actor,
                    reason=reason,
                )

                self._add_case_event(
                    case_id=case_id,
                    event_type="CASE_BULK_TRANSITIONED",
                    actor=actor,
                    details={
                        "to_state": to_state,
                        "reason": reason,
                    },
                )

                result.add_success(case_id, f"Transitioned to {to_state}")

            except Exception as exc:
                result.add_failure(case_id, str(exc), self._error_details())

        return result.to_dict()

    def bulk_request_approval(
        self,
        case_ids: List[Any],
        approval_type: str,
        requested_by: str = "system",
        reason: str = "Bulk approval request from Command Center",
    ) -> Dict[str, Any]:
        result = BulkActionResult(action="bulk_request_approval", requested=len(case_ids))

        for case_id in self._clean_case_ids(case_ids):
            try:
                if not approval_type:
                    raise ValueError("approval_type is required")

                self._request_approval(
                    case_id=case_id,
                    approval_type=approval_type,
                    requested_by=requested_by,
                    reason=reason,
                )

                self._add_case_event(
                    case_id=case_id,
                    event_type="CASE_BULK_APPROVAL_REQUESTED",
                    actor=requested_by,
                    details={
                        "approval_type": approval_type,
                        "reason": reason,
                    },
                )

                result.add_success(case_id, f"Approval requested: {approval_type}")

            except Exception as exc:
                result.add_failure(case_id, str(exc), self._error_details())

        return result.to_dict()

    # ---------------------------------------------------------------------
    # Internal adapters
    # ---------------------------------------------------------------------

    def _assign_case(
        self,
        case_id: Any,
        analyst_id: str,
        assigned_by: str,
        reason: str,
    ) -> None:
        if self.assignment_service is not None:
            for method_name in [
                "assign_case",
                "assign_case_to_user",
                "assign",
            ]:
                method = getattr(self.assignment_service, method_name, None)
                if callable(method):
                    try:
                        method(
                            case_id=case_id,
                            analyst_id=analyst_id,
                            assigned_by=assigned_by,
                            reason=reason,
                        )
                        return
                    except TypeError:
                        method(case_id, analyst_id)
                        return

        for method_name in [
            "assign_case",
            "update_case_assignment",
            "set_case_owner",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        analyst_id=analyst_id,
                        assigned_by=assigned_by,
                        reason=reason,
                    )
                    return
                except TypeError:
                    method(case_id, analyst_id)
                    return

        raise AttributeError("No assignment method found on assignment_service or ledger")

    def _escalate_case(
        self,
        case_id: Any,
        actor: str,
        reason: str,
        escalation_level: Optional[int] = None,
    ) -> None:
        if self.escalation_service is not None:
            for method_name in [
                "auto_escalate_case",
                "escalate_case",
                "manual_escalate_case",
            ]:
                method = getattr(self.escalation_service, method_name, None)
                if callable(method):
                    try:
                        method(
                            case_id=case_id,
                            actor=actor,
                            reason=reason,
                            escalation_level=escalation_level,
                        )
                        return
                    except TypeError:
                        method(case_id=case_id, reason=reason, actor=actor)
                        return

        for method_name in [
            "escalate_case",
            "mark_case_escalated",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        actor=actor,
                        reason=reason,
                        escalation_level=escalation_level,
                    )
                    return
                except TypeError:
                    method(case_id, reason)
                    return

        raise AttributeError("No escalation method found on escalation_service or ledger")

    def _transition_case(
        self,
        case_id: Any,
        to_state: str,
        actor: str,
        reason: str,
    ) -> None:
        if self.state_machine is not None:
            for method_name in [
                "transition",
                "transition_case",
                "apply_transition",
            ]:
                method = getattr(self.state_machine, method_name, None)
                if callable(method):
                    try:
                        method(
                            case_id=case_id,
                            to_state=to_state,
                            actor=actor,
                            reason=reason,
                        )
                        return
                    except TypeError:
                        method(case_id, to_state)
                        return

        for method_name in [
            "update_case_status",
            "set_case_status",
            "transition_case",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        status=to_state,
                        actor=actor,
                        reason=reason,
                    )
                    return
                except TypeError:
                    method(case_id, to_state)
                    return

        raise AttributeError("No transition method found on state_machine or ledger")

    def _request_approval(
        self,
        case_id: Any,
        approval_type: str,
        requested_by: str,
        reason: str,
    ) -> None:
        if self.approval_service is not None:
            for method_name in [
                "request_approval",
                "create_approval_request",
                "request_case_approval",
            ]:
                method = getattr(self.approval_service, method_name, None)
                if callable(method):
                    try:
                        method(
                            case_id=case_id,
                            approval_type=approval_type,
                            requested_by=requested_by,
                            reason=reason,
                        )
                        return
                    except TypeError:
                        method(case_id, approval_type)
                        return

        for method_name in [
            "create_approval_request",
            "request_case_approval",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        approval_type=approval_type,
                        requested_by=requested_by,
                        reason=reason,
                    )
                    return
                except TypeError:
                    method(case_id, approval_type)
                    return

        raise AttributeError("No approval request method found on approval_service or ledger")

    # ---------------------------------------------------------------------
    # Audit/event helpers
    # ---------------------------------------------------------------------

    def _add_case_event(
        self,
        case_id: Any,
        event_type: str,
        actor: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = details or {}
        details.setdefault("source", "BulkCaseService")
        details.setdefault("timestamp_ms", _now_ms())

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
                    except TypeError:
                        pass

        # Fallback for older audit log implementations.
        for method_name in [
            "add_case_audit_log",
            "record_case_audit",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        action=event_type,
                        performed_by=actor,
                        details=str(details),
                    )
                    return
                except TypeError:
                    method(case_id, event_type, actor, str(details))
                    return

    @staticmethod
    def _clean_case_ids(case_ids: List[Any]) -> List[Any]:
        if not case_ids:
            return []

        cleaned = []
        seen = set()

        for case_id in case_ids:
            if case_id is None:
                continue

            case_key = str(case_id)

            if case_key in seen:
                continue

            seen.add(case_key)
            cleaned.append(case_id)

        return cleaned

    @staticmethod
    def _error_details() -> Dict[str, Any]:
        return {
            "traceback": traceback.format_exc(limit=5),
        }