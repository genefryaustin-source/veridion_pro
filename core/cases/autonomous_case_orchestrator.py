"""
core/cases/autonomous_case_orchestrator.py

Autonomous Case Orchestration Engine.

Bridges:
- autonomous execution
- investigations
- evidence
- escalation
- rollback
- SLA workflows
- export-control routing
- governance feedback

Safe design:
- Does not assume one rigid ledger schema
- Uses existing ledger methods when available
- Falls back to event telemetry when case APIs are unavailable
- Compatible with ActionExecutionRouter
"""

from __future__ import annotations

import time
import uuid
import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

CASE_STATUS_OPEN = "OPEN"
CASE_STATUS_ESCALATED = "ESCALATED"
CASE_STATUS_CONTAINMENT_ACTIVE = "CONTAINMENT_ACTIVE"
CASE_STATUS_ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
CASE_STATUS_LEGAL_REVIEW = "LEGAL_REVIEW"

EVENT_AUTONOMOUS_ACTION = "AUTONOMOUS_ACTION"
EVENT_CONTAINMENT_LINKED = "CONTAINMENT_LINKED"
EVENT_ROLLBACK_SYNCHRONIZED = "ROLLBACK_SYNCHRONIZED"
EVENT_EXPORT_CONTROL_ROUTED = "EXPORT_CONTROL_ROUTED"
EVENT_SLA_ESCALATED = "SLA_ESCALATED"
EVENT_EVIDENCE_SYNCED = "EVIDENCE_SYNCED"
EVENT_GOVERNANCE_FEEDBACK = "GOVERNANCE_FEEDBACK"


@dataclass
class CaseOrchestrationResult:
    success: bool
    case_id: Optional[Any] = None
    status: str = "UNKNOWN"
    severity: str = SEVERITY_MEDIUM
    created_case: bool = False
    linked_evidence: List[Any] = field(default_factory=list)
    linked_graph_id: Optional[str] = None
    escalation_required: bool = False
    legal_required: bool = False
    rollback_detected: bool = False
    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutonomousCaseOrchestrator:
    """
    Operational case-continuity layer for autonomous cyber operations.
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.storage = storage
        self.config = config or {}
        self.ledger = getattr(storage, "ledger", storage)

    # ========================================================
    # EVENTING
    # ========================================================

    def emit_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="autonomous_case_orchestrator",
        )

    # ========================================================
    # MAIN ENTRYPOINT
    # ========================================================

    def record_autonomous_action(
        self,
        action_result: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> CaseOrchestrationResult:
        """
        Called by ActionExecutionRouter after every autonomous action.
        """

        context = context or {}

        try:
            normalized = self._normalize_action_result(action_result)
            severity = self._derive_severity(normalized, context)

            case_id, created = self._resolve_or_create_case(
                normalized=normalized,
                context=context,
                severity=severity,
            )

            result = CaseOrchestrationResult(
                success=True,
                case_id=case_id,
                status=CASE_STATUS_OPEN,
                severity=severity,
                created_case=created,
                linked_graph_id=context.get("graph_id") or normalized.get("graph_id"),
                escalation_required=bool(
                    normalized.get("requires_escalation")
                    or severity in {SEVERITY_HIGH, SEVERITY_CRITICAL}
                ),
                legal_required=bool(
                    normalized.get("requires_legal")
                    or self._is_export_control(context)
                ),
                rollback_detected=self._is_rollback(normalized, context),
                metadata={
                    "action": normalized,
                    "context": self._safe_context(context),
                },
            )

            self._link_execution_to_case(case_id, normalized, context)
            self._sync_evidence(case_id, normalized, context)
            self._sync_graph(case_id, normalized, context)

            if result.rollback_detected:
                self._synchronize_rollback(case_id, normalized, context)
                result.status = CASE_STATUS_ROLLBACK_REQUIRED

            if self._is_export_control(context) or result.legal_required:
                self._route_export_control(case_id, normalized, context)
                result.status = CASE_STATUS_LEGAL_REVIEW

            if result.escalation_required:
                self._orchestrate_sla_and_escalation(case_id, normalized, context)
                if result.status == CASE_STATUS_OPEN:
                    result.status = CASE_STATUS_ESCALATED

            self._emit_governance_feedback(case_id, normalized, context, result)

            self.emit_event(
                "AUTONOMOUS_CASE_ORCHESTRATION_COMPLETED",
                result.__dict__,
            )

            return result

        except Exception:
            error = traceback.format_exc()

            self.emit_event(
                "AUTONOMOUS_CASE_ORCHESTRATION_FAILED",
                {
                    "error": error,
                    "context": self._safe_context(context),
                },
            )

            return CaseOrchestrationResult(
                success=False,
                error=error,
                message="Autonomous case orchestration failed.",
            )

    # ========================================================
    # CASE RESOLUTION / CREATION
    # ========================================================

    def _resolve_or_create_case(
        self,
        normalized: Dict[str, Any],
        context: Dict[str, Any],
        severity: str,
    ) -> tuple[Optional[Any], bool]:
        explicit_case_id = (
            context.get("case_id")
            or normalized.get("case_id")
            or normalized.get("metadata", {}).get("case_id")
        )

        if explicit_case_id:
            return explicit_case_id, False

        evidence_id = self._extract_evidence_id(normalized, context)

        if evidence_id:
            found = self._safe_call(
                "find_case_by_evidence",
                evidence_id,
            )
            if found:
                return found, False

        alert_id = context.get("alert_id") or normalized.get("alert_id")

        if alert_id:
            found = self._safe_call("find_case_by_alert", alert_id)
            if found:
                return found, False

        title = self._build_case_title(normalized, context, severity)

        case_id = self._create_case(
            title=title,
            severity=severity,
            context=context,
            normalized=normalized,
        )

        return case_id, bool(case_id)

    def _create_case(
        self,
        title: str,
        severity: str,
        context: Dict[str, Any],
        normalized: Dict[str, Any],
    ) -> Optional[Any]:
        metadata = {
            "created_by": "autonomous_case_orchestrator",
            "graph_id": context.get("graph_id") or normalized.get("graph_id"),
            "execution_id": normalized.get("execution_id"),
            "agent_name": normalized.get("agent_name"),
            "action": normalized.get("action"),
            "tenant_id": context.get("tenant_id"),
            "category": context.get("category"),
            "export_control": self._is_export_control(context),
        }

        method_attempts = [
            ("create_case", (title, severity, json.dumps(metadata))),
            ("create_investigation_case", (title, severity, metadata)),
            ("ensure_case", (title, severity, metadata)),
        ]

        for method_name, args in method_attempts:
            case_id = self._safe_call(method_name, *args)
            if case_id:
                self.emit_event(
                    "AUTONOMOUS_CASE_CREATED",
                    {
                        "case_id": case_id,
                        "title": title,
                        "severity": severity,
                        "metadata": metadata,
                    },
                )
                return case_id

        self.emit_event(
            "AUTONOMOUS_CASE_CREATE_FALLBACK",
            {
                "title": title,
                "severity": severity,
                "metadata": metadata,
                "reason": "ledger_case_create_method_unavailable",
            },
        )

        return None

    # ========================================================
    # LINKAGE
    # ========================================================

    def _link_execution_to_case(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        payload = {
            "case_id": case_id,
            "execution_id": normalized.get("execution_id"),
            "agent_name": normalized.get("agent_name"),
            "action": normalized.get("action"),
            "connector": normalized.get("routed_connector"),
            "target": normalized.get("target"),
            "success": normalized.get("success"),
            "status": normalized.get("status"),
            "policy_decision": normalized.get("policy_decision"),
            "graph_id": context.get("graph_id") or normalized.get("graph_id"),
        }

        self._add_case_event(
            case_id,
            EVENT_AUTONOMOUS_ACTION,
            payload,
        )

        self.emit_event(
            "AUTONOMOUS_EXECUTION_LINKED_TO_CASE",
            payload,
        )

    def _sync_evidence(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        evidence_ids = []

        for key in ("evidence_id", "evidence_ids"):
            value = context.get(key) or normalized.get(key)
            if isinstance(value, list):
                evidence_ids.extend(value)
            elif value:
                evidence_ids.append(value)

        evidence_ids = list(dict.fromkeys(evidence_ids))

        for evidence_id in evidence_ids:
            self._safe_call("add_case_evidence", case_id, evidence_id)
            self._add_case_event(
                case_id,
                EVENT_EVIDENCE_SYNCED,
                {
                    "case_id": case_id,
                    "evidence_id": evidence_id,
                    "source": "autonomous_case_orchestrator",
                },
            )

        if evidence_ids:
            self.emit_event(
                "AUTONOMOUS_CASE_EVIDENCE_SYNCED",
                {
                    "case_id": case_id,
                    "evidence_ids": evidence_ids,
                },
            )

        entities = context.get("entities") or normalized.get("entities") or []
        if entities:
            self._add_case_event(
                case_id,
                "EVIDENCE_ENTITIES_LINKED",
                {
                    "case_id": case_id,
                    "entities": entities,
                },
            )

    def _sync_graph(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        graph_id = context.get("graph_id") or normalized.get("graph_id")
        if not graph_id:
            return

        self._add_case_event(
            case_id,
            "EXECUTION_GRAPH_LINKED",
            {
                "case_id": case_id,
                "graph_id": graph_id,
                "execution_id": normalized.get("execution_id"),
                "action": normalized.get("action"),
            },
        )

        self.emit_event(
            "EXECUTION_GRAPH_LINKED_TO_CASE",
            {
                "case_id": case_id,
                "graph_id": graph_id,
            },
        )

    # ========================================================
    # ROLLBACK
    # ========================================================

    def _synchronize_rollback(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        payload = {
            "case_id": case_id,
            "execution_id": normalized.get("execution_id"),
            "action": normalized.get("action"),
            "rollback_action": normalized.get("rollback_action"),
            "rollback_connector": normalized.get("rollback_connector"),
            "rollback_data": normalized.get("rollback_data"),
            "governance_impact": "increase_drift",
        }

        self._add_case_event(case_id, EVENT_ROLLBACK_SYNCHRONIZED, payload)

        self._safe_call(
            "update_case_status",
            case_id,
            CASE_STATUS_ROLLBACK_REQUIRED,
        )

        self.emit_event("AUTONOMOUS_CASE_ROLLBACK_SYNCED", payload)

    # ========================================================
    # EXPORT / LEGAL ROUTING
    # ========================================================

    def _route_export_control(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        payload = {
            "case_id": case_id,
            "category": context.get("category"),
            "requires_legal": True,
            "requires_executive_visibility": True,
            "verification_frequency": "MAXIMUM",
            "reason": "export_control_or_legal_policy",
        }

        self._add_case_event(case_id, EVENT_EXPORT_CONTROL_ROUTED, payload)

        self._safe_call("update_case_status", case_id, CASE_STATUS_LEGAL_REVIEW)
        self._safe_call("update_case_severity", case_id, SEVERITY_CRITICAL)

        self.emit_event("EXPORT_CONTROL_CASE_ROUTED", payload)

    # ========================================================
    # SLA / ESCALATION
    # ========================================================

    def _orchestrate_sla_and_escalation(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> None:
        payload = {
            "case_id": case_id,
            "severity": self._derive_severity(normalized, context),
            "action": normalized.get("action"),
            "agent_name": normalized.get("agent_name"),
            "requires_legal": normalized.get("requires_legal"),
            "requires_escalation": normalized.get("requires_escalation"),
            "sla_pressure": self._derive_sla_pressure(normalized, context),
        }

        self._add_case_event(case_id, EVENT_SLA_ESCALATED, payload)

        self._safe_call("update_case_status", case_id, CASE_STATUS_ESCALATED)

        self.emit_event("AUTONOMOUS_CASE_ESCALATED", payload)

    # ========================================================
    # GOVERNANCE FEEDBACK
    # ========================================================

    def _emit_governance_feedback(
        self,
        case_id: Optional[Any],
        normalized: Dict[str, Any],
        context: Dict[str, Any],
        result: CaseOrchestrationResult,
    ) -> None:
        payload = {
            "case_id": case_id,
            "success": result.success,
            "severity": result.severity,
            "created_case": result.created_case,
            "rollback_detected": result.rollback_detected,
            "legal_required": result.legal_required,
            "escalation_required": result.escalation_required,
            "policy_decision": normalized.get("policy_decision"),
            "agent_name": normalized.get("agent_name"),
            "action": normalized.get("action"),
        }

        self._add_case_event(case_id, EVENT_GOVERNANCE_FEEDBACK, payload)

        self.emit_event("CASE_GOVERNANCE_FEEDBACK_EMITTED", payload)

    # ========================================================
    # SLA MONITORING ENTRYPOINT
    # ========================================================

    def monitor_sla_pressure(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Optional callable for worker/scheduler use.

        Uses ledger methods if available.
        """

        try:
            breaches = []

            if hasattr(self.ledger, "detect_case_sla_breaches"):
                breaches = self.ledger.detect_case_sla_breaches(tenant_id=tenant_id)
            elif hasattr(self.ledger, "detect_sla_breaches"):
                breaches = self.ledger.detect_sla_breaches()

            count = len(breaches or [])

            for breach in breaches or []:
                case_id = (
                    breach.get("case_id")
                    if isinstance(breach, dict)
                    else getattr(breach, "case_id", None)
                )

                self._add_case_event(
                    case_id,
                    EVENT_SLA_ESCALATED,
                    {
                        "case_id": case_id,
                        "breach": breach,
                        "source": "sla_monitor",
                    },
                )

                self._safe_call("update_case_status", case_id, CASE_STATUS_ESCALATED)

            payload = {
                "tenant_id": tenant_id,
                "breach_count": count,
            }

            self.emit_event("CASE_SLA_PRESSURE_MONITORED", payload)

            return payload

        except Exception:
            payload = {
                "tenant_id": tenant_id,
                "error": traceback.format_exc(),
            }
            self.emit_event("CASE_SLA_PRESSURE_MONITOR_FAILED", payload)
            return payload

    # ========================================================
    # HELPERS
    # ========================================================

    def _normalize_action_result(self, action_result: Any) -> Dict[str, Any]:
        if isinstance(action_result, dict):
            return action_result

        if hasattr(action_result, "__dict__"):
            data = action_result.__dict__.copy()

            connector_result = data.get("connector_result")
            if connector_result is not None and hasattr(connector_result, "__dict__"):
                data["connector_result"] = connector_result.__dict__.copy()

            return data

        return {"raw": str(action_result)}

    def _derive_severity(
        self,
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        explicit = (
            context.get("severity")
            or normalized.get("severity")
            or normalized.get("metadata", {}).get("severity")
        )

        if explicit:
            return str(explicit).upper()

        if self._is_export_control(context):
            return SEVERITY_CRITICAL

        action = str(normalized.get("action") or "").lower()

        if action in {"endpoint_quarantine", "contain_host", "token_revocation", "disable_user"}:
            return SEVERITY_HIGH

        if not normalized.get("success", True):
            return SEVERITY_HIGH

        return SEVERITY_MEDIUM

    def _derive_sla_pressure(
        self,
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        severity = self._derive_severity(normalized, context)

        if severity == SEVERITY_CRITICAL:
            return "MAXIMUM"
        if severity == SEVERITY_HIGH:
            return "ELEVATED"
        return "NORMAL"

    def _is_export_control(self, context: Dict[str, Any]) -> bool:
        category = str(context.get("category") or "").upper()
        text = json.dumps(context, default=str).lower()

        return (
            bool(context.get("export_control"))
            or category == "EXPORT_CONTROL"
            or "itar" in text
            or "ear99" in text
            or "export controlled" in text
            or "export-control" in text
            or "usml" in text
        )

    def _is_rollback(
        self,
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:
        action = str(normalized.get("action") or "").lower()
        event_type = str(context.get("event_type") or "").upper()

        return (
            "rollback" in action
            or "ROLLBACK" in event_type
            or bool(context.get("rollback"))
            or bool(normalized.get("rollback_detected"))
        )

    def _extract_evidence_id(
        self,
        normalized: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Any]:
        value = (
            context.get("evidence_id")
            or normalized.get("evidence_id")
            or normalized.get("metadata", {}).get("evidence_id")
        )

        if isinstance(value, list):
            return value[0] if value else None

        return value

    def _build_case_title(
        self,
        normalized: Dict[str, Any],
        context: Dict[str, Any],
        severity: str,
    ) -> str:
        action = normalized.get("action") or "autonomous_action"
        target = normalized.get("target") or context.get("target") or context.get("mailbox") or context.get("endpoint") or context.get("user")

        if self._is_export_control(context):
            return f"Critical Export-Control Autonomous Incident: {target or action}"

        if severity == SEVERITY_CRITICAL:
            return f"Critical Autonomous SOC Incident: {target or action}"

        return f"Autonomous SOC Case: {action} - {target or 'Unknown Target'}"

    def _add_case_event(
        self,
        case_id: Optional[Any],
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        if not case_id:
            self.emit_event(
                "CASE_EVENT_FALLBACK",
                {
                    "event_type": event_type,
                    "payload": payload,
                    "reason": "case_id_unavailable",
                },
            )
            return

        attempts = [
            ("add_case_event", (case_id, event_type, json.dumps(payload))),
            ("record_case_event", (case_id, event_type, payload)),
            ("add_case_timeline_event", (case_id, event_type, payload)),
        ]

        for method_name, args in attempts:
            ok = self._safe_call(method_name, *args)
            if ok is not None:
                return

        self.emit_event(
            "CASE_EVENT_RECORDED_FALLBACK",
            {
                "case_id": case_id,
                "event_type": event_type,
                "payload": payload,
            },
        )

    def _safe_call(self, method_name: str, *args, **kwargs) -> Any:
        if self.ledger is None:
            return None

        fn = getattr(self.ledger, method_name, None)

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

    def _safe_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {
            "password",
            "token",
            "access_token",
            "refresh_token",
            "secret",
            "client_secret",
            "api_key",
        }

        clean = {}

        for key, value in context.items():
            if key.lower() in sensitive:
                clean[key] = "***REDACTED***"
            else:
                clean[key] = value

        return clean