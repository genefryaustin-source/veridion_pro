"""
core/ai/orchestration/detection_response_router.py

Detection Response Router for Veridion Pro / CUI GovCloud App.

Purpose:
- Bridge detections into autonomous response orchestration
- Normalize detection context
- Route CUI/export-control/credential/phishing/endpoint findings
- Invoke AutonomousResponseEngine
- Attach execution outcomes to cases/alerts where possible
- Emit forensic custody + telemetry events

Safe by default:
- Uses simulation mode unless explicitly disabled
- Does not bypass governance
- Does not directly execute external destructive actions
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.ai.orchestration.autonomous_response_engine import (
    AutonomousResponseResult,
    DEFAULT_AUTONOMY_MODE,
    process_detection,
)

from core.events.event_bus import (
    APPROVAL_REQUIRED,
    EXECUTION_COMPLETED,
    EXECUTION_FAILED,
    POLICY_VIOLATION,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_INFO,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    get_event_bus,
)


# =============================================================================
# Constants
# =============================================================================

ROUTER_SOURCE = "detection_response_router"

CATEGORY_CUI = "CUI"
CATEGORY_EXPORT_CONTROL = "EXPORT_CONTROL"
CATEGORY_ITAR = "ITAR"
CATEGORY_CTI = "CONTROLLED_TECHNICAL_INFORMATION"
CATEGORY_CREDENTIAL = "CREDENTIAL"
CATEGORY_TOKEN = "TOKEN"
CATEGORY_PHISHING = "PHISHING"
CATEGORY_MALWARE = "MALWARE"
CATEGORY_SUSPICIOUS_EMAIL = "SUSPICIOUS_EMAIL"
CATEGORY_ENDPOINT_COMPROMISE = "ENDPOINT_COMPROMISE"
CATEGORY_HOST_COMPROMISE = "HOST_COMPROMISE"
CATEGORY_RANSOMWARE = "RANSOMWARE"


# =============================================================================
# Helpers
# =============================================================================

def _now_ms() -> int:
    return int(time.time() * 1000)


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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _safe_json_loads(value: Any, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    return [value]


def _normalize_categories(detection: Dict[str, Any]) -> List[str]:
    raw = (
        detection.get("categories")
        or detection.get("flags")
        or detection.get("labels")
        or detection.get("classifications")
        or []
    )

    categories = []

    for item in _as_list(raw):
        if item is None:
            continue
        categories.append(str(item).upper().strip())

    return sorted(set([c for c in categories if c]))


def _get_ledger(storage: Any) -> Any:
    if storage is None:
        return None
    return getattr(storage, "ledger", storage)


def _record_custody_event(
    storage: Any,
    *,
    event_type: str,
    actor: str,
    tenant_id: str,
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
        "tenant_id": tenant_id,
        "evidence_id": evidence_id,
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


def _call_ledger_method(
    storage: Any,
    method_name: str,
    default: Any = None,
    *args,
    **kwargs,
) -> Any:
    ledger = _get_ledger(storage)

    if ledger is None:
        return default

    method = getattr(ledger, method_name, None)

    if not callable(method):
        return default

    try:
        return method(*args, **kwargs)
    except Exception:
        return default


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class DetectionRouteContext:
    tenant_id: str = "default"
    actor: str = "detection_response_router"

    case_id: Optional[str] = None
    evidence_id: Optional[str] = None
    alert_id: Optional[str] = None
    run_id: Optional[str] = None

    mailbox: Optional[str] = None
    message_id: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None

    source: str = ROUTER_SOURCE
    autonomy_mode: str = DEFAULT_AUTONOMY_MODE
    simulation_mode: bool = True

    route_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at_ms: int = field(default_factory=_now_ms)


@dataclass
class DetectionRouteResult:
    ok: bool
    route_id: str
    tenant_id: str
    message: str

    severity: str = SEVERITY_INFO
    risk_score: int = 0
    categories: List[str] = field(default_factory=list)

    case_id: Optional[str] = None
    evidence_id: Optional[str] = None
    alert_id: Optional[str] = None
    run_id: Optional[str] = None

    response_results: List[AutonomousResponseResult] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)

    created_at_ms: int = field(default_factory=_now_ms)


# =============================================================================
# Router
# =============================================================================

class DetectionResponseRouter:
    def __init__(
        self,
        storage: Any = None,
        *,
        autonomy_mode: str = DEFAULT_AUTONOMY_MODE,
        simulation_mode: bool = True,
    ) -> None:
        self.storage = storage
        self.autonomy_mode = autonomy_mode
        self.simulation_mode = simulation_mode
        self.event_bus = get_event_bus(storage)

    # -------------------------------------------------------------------------
    # Main Entrypoint
    # -------------------------------------------------------------------------

    def route_detection(
        self,
        detection: Dict[str, Any],
        *,
        context: Optional[DetectionRouteContext] = None,
        tenant_id: Optional[str] = None,
        actor: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        alert_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> DetectionRouteResult:
        context = context or DetectionRouteContext(
            tenant_id=tenant_id or "default",
            actor=actor or ROUTER_SOURCE,
            case_id=case_id,
            evidence_id=evidence_id,
            alert_id=alert_id,
            run_id=run_id,
            autonomy_mode=self.autonomy_mode,
            simulation_mode=self.simulation_mode,
        )

        detection = self.normalize_detection(detection, context=context)

        categories = _normalize_categories(detection)
        severity = self.derive_severity(detection)
        risk_score = self.derive_risk_score(detection)

        detection["categories"] = categories
        detection["severity"] = severity
        detection["risk_score"] = risk_score
        detection["route_id"] = context.route_id

        self._attach_context_fields(detection, context)

        event_ids: List[str] = []

        start_event = self.event_bus.publish(
            event_type="DETECTION_RESPONSE_ROUTED",
            tenant_id=context.tenant_id,
            source=ROUTER_SOURCE,
            severity=severity,
            payload={
                "route_id": context.route_id,
                "case_id": context.case_id,
                "evidence_id": context.evidence_id,
                "alert_id": context.alert_id,
                "run_id": context.run_id,
                "categories": categories,
                "risk_score": risk_score,
                "message": "Detection routed to autonomous response engine.",
            },
        )
        event_ids.append(start_event.event_id)

        _record_custody_event(
            self.storage,
            event_type="DETECTION_RESPONSE_ROUTED",
            actor=context.actor,
            tenant_id=context.tenant_id,
            evidence_id=context.evidence_id,
            case_id=context.case_id,
            alert_id=context.alert_id,
            run_id=context.run_id,
            details={
                "route_id": context.route_id,
                "categories": categories,
                "severity": severity,
                "risk_score": risk_score,
                "simulation_mode": context.simulation_mode,
            },
        )

        if not self.should_route(detection):
            return DetectionRouteResult(
                ok=True,
                route_id=context.route_id,
                tenant_id=context.tenant_id,
                message="Detection did not require autonomous response routing.",
                severity=severity,
                risk_score=risk_score,
                categories=categories,
                case_id=context.case_id,
                evidence_id=context.evidence_id,
                alert_id=context.alert_id,
                run_id=context.run_id,
                response_results=[],
                event_ids=event_ids,
            )

        try:
            response_results = process_detection(
                self.storage,
                detection,
                tenant_id=context.tenant_id,
                actor=context.actor,
                case_id=context.case_id,
                evidence_id=context.evidence_id,
                alert_id=context.alert_id,
                run_id=context.run_id,
                autonomy_mode=context.autonomy_mode,
                simulation_mode=context.simulation_mode,
            )

            for result in response_results:
                event_ids.extend(result.event_ids or [])
                self._attach_response_to_case_or_alert(
                    result=result,
                    context=context,
                    detection=detection,
                )

            status_event_type = self._result_event_type(response_results)

            done_event = self.event_bus.publish(
                event_type=status_event_type,
                tenant_id=context.tenant_id,
                source=ROUTER_SOURCE,
                severity=severity,
                payload={
                    "route_id": context.route_id,
                    "case_id": context.case_id,
                    "evidence_id": context.evidence_id,
                    "alert_id": context.alert_id,
                    "run_id": context.run_id,
                    "response_count": len(response_results),
                    "statuses": [r.status for r in response_results],
                    "message": "Detection response routing completed.",
                },
            )
            event_ids.append(done_event.event_id)

            _record_custody_event(
                self.storage,
                event_type="DETECTION_RESPONSE_COMPLETED",
                actor=context.actor,
                tenant_id=context.tenant_id,
                evidence_id=context.evidence_id,
                case_id=context.case_id,
                alert_id=context.alert_id,
                run_id=context.run_id,
                details={
                    "route_id": context.route_id,
                    "response_count": len(response_results),
                    "results": [
                        self._result_to_dict(result)
                        for result in response_results
                    ],
                },
            )

            ok = all(result.ok for result in response_results) if response_results else True

            return DetectionRouteResult(
                ok=ok,
                route_id=context.route_id,
                tenant_id=context.tenant_id,
                message="Detection routed and processed.",
                severity=severity,
                risk_score=risk_score,
                categories=categories,
                case_id=context.case_id,
                evidence_id=context.evidence_id,
                alert_id=context.alert_id,
                run_id=context.run_id,
                response_results=response_results,
                event_ids=event_ids,
            )

        except Exception as exc:
            fail_event = self.event_bus.publish(
                event_type=EXECUTION_FAILED,
                tenant_id=context.tenant_id,
                source=ROUTER_SOURCE,
                severity=SEVERITY_HIGH,
                payload={
                    "route_id": context.route_id,
                    "case_id": context.case_id,
                    "evidence_id": context.evidence_id,
                    "alert_id": context.alert_id,
                    "run_id": context.run_id,
                    "message": str(exc),
                    "status": "FAILED",
                },
            )
            event_ids.append(fail_event.event_id)

            _record_custody_event(
                self.storage,
                event_type="DETECTION_RESPONSE_FAILED",
                actor=context.actor,
                tenant_id=context.tenant_id,
                evidence_id=context.evidence_id,
                case_id=context.case_id,
                alert_id=context.alert_id,
                run_id=context.run_id,
                details={
                    "route_id": context.route_id,
                    "error": str(exc),
                },
            )

            return DetectionRouteResult(
                ok=False,
                route_id=context.route_id,
                tenant_id=context.tenant_id,
                message=str(exc),
                severity=severity,
                risk_score=risk_score,
                categories=categories,
                case_id=context.case_id,
                evidence_id=context.evidence_id,
                alert_id=context.alert_id,
                run_id=context.run_id,
                response_results=[],
                event_ids=event_ids,
            )

    # -------------------------------------------------------------------------
    # Batch Routing
    # -------------------------------------------------------------------------

    def route_detections(
        self,
        detections: List[Dict[str, Any]],
        *,
        tenant_id: str = "default",
        actor: str = ROUTER_SOURCE,
        case_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> List[DetectionRouteResult]:
        results: List[DetectionRouteResult] = []

        for detection in detections or []:
            context = DetectionRouteContext(
                tenant_id=tenant_id,
                actor=actor,
                case_id=case_id or detection.get("case_id"),
                evidence_id=detection.get("evidence_id"),
                alert_id=detection.get("alert_id"),
                run_id=run_id or detection.get("run_id"),
                mailbox=detection.get("mailbox"),
                message_id=detection.get("message_id") or detection.get("email_id"),
                sender=detection.get("sender"),
                subject=detection.get("subject"),
                autonomy_mode=self.autonomy_mode,
                simulation_mode=self.simulation_mode,
            )

            results.append(
                self.route_detection(
                    detection,
                    context=context,
                )
            )

        return results

    # -------------------------------------------------------------------------
    # Normalization
    # -------------------------------------------------------------------------

    def normalize_detection(
        self,
        detection: Dict[str, Any],
        *,
        context: DetectionRouteContext,
    ) -> Dict[str, Any]:
        detection = detection or {}

        normalized = dict(detection)

        normalized["tenant_id"] = normalized.get("tenant_id") or context.tenant_id
        normalized["case_id"] = normalized.get("case_id") or context.case_id
        normalized["evidence_id"] = normalized.get("evidence_id") or context.evidence_id
        normalized["alert_id"] = normalized.get("alert_id") or context.alert_id
        normalized["run_id"] = normalized.get("run_id") or context.run_id

        normalized["mailbox"] = normalized.get("mailbox") or context.mailbox
        normalized["message_id"] = (
            normalized.get("message_id")
            or normalized.get("email_id")
            or context.message_id
        )
        normalized["sender"] = normalized.get("sender") or context.sender
        normalized["subject"] = normalized.get("subject") or context.subject

        matches = normalized.get("matches") or normalized.get("rule_hits") or []
        normalized["matches"] = matches
        normalized["rule_hits"] = normalized.get("rule_hits") or matches
        normalized["hit_count"] = _safe_int(
            normalized.get("hit_count")
            or normalized.get("hits")
            or len(matches),
            0,
        )

        normalized["categories"] = _normalize_categories(normalized)

        if not normalized["categories"] and normalized["hit_count"] > 0:
            normalized["categories"] = [CATEGORY_CUI]

        normalized["confidence"] = _safe_float(
            normalized.get("confidence"),
            min(0.95, 0.50 + normalized["hit_count"] * 0.05),
        )

        return normalized

    def _attach_context_fields(
        self,
        detection: Dict[str, Any],
        context: DetectionRouteContext,
    ) -> None:
        if context.evidence_id:
            detection["evidence_id"] = context.evidence_id

        if context.alert_id:
            detection["alert_id"] = context.alert_id

        if context.case_id:
            detection["case_id"] = context.case_id

        if context.run_id:
            detection["run_id"] = context.run_id

    # -------------------------------------------------------------------------
    # Routing Logic
    # -------------------------------------------------------------------------

    def should_route(self, detection: Dict[str, Any]) -> bool:
        categories = set(_normalize_categories(detection))
        hit_count = _safe_int(detection.get("hit_count"), 0)
        severity = self.derive_severity(detection)

        if hit_count <= 0 and not categories:
            return False

        route_categories = {
            CATEGORY_CUI,
            CATEGORY_EXPORT_CONTROL,
            CATEGORY_ITAR,
            CATEGORY_CTI,
            CATEGORY_CREDENTIAL,
            CATEGORY_TOKEN,
            CATEGORY_PHISHING,
            CATEGORY_MALWARE,
            CATEGORY_SUSPICIOUS_EMAIL,
            CATEGORY_ENDPOINT_COMPROMISE,
            CATEGORY_HOST_COMPROMISE,
            CATEGORY_RANSOMWARE,
        }

        if categories.intersection(route_categories):
            return True

        if severity in {SEVERITY_HIGH, SEVERITY_CRITICAL}:
            return True

        return False

    def derive_severity(self, detection: Dict[str, Any]) -> str:
        raw = _safe_str(
            detection.get("severity")
            or detection.get("level")
            or detection.get("risk_level"),
            "",
        ).upper()

        if raw in {
            SEVERITY_CRITICAL,
            SEVERITY_HIGH,
            SEVERITY_MEDIUM,
            SEVERITY_LOW,
            SEVERITY_INFO,
        }:
            return raw

        categories = set(_normalize_categories(detection))
        hit_count = _safe_int(detection.get("hit_count"), 0)

        if (
            CATEGORY_RANSOMWARE in categories
            or CATEGORY_EXPORT_CONTROL in categories
            or CATEGORY_ITAR in categories
        ):
            return SEVERITY_CRITICAL

        if (
            CATEGORY_CREDENTIAL in categories
            or CATEGORY_TOKEN in categories
            or CATEGORY_CUI in categories
            or CATEGORY_CTI in categories
            or CATEGORY_ENDPOINT_COMPROMISE in categories
            or CATEGORY_HOST_COMPROMISE in categories
        ):
            return SEVERITY_HIGH

        if (
            CATEGORY_PHISHING in categories
            or CATEGORY_MALWARE in categories
            or CATEGORY_SUSPICIOUS_EMAIL in categories
        ):
            return SEVERITY_MEDIUM

        if hit_count > 0:
            return SEVERITY_MEDIUM

        return SEVERITY_INFO

    def derive_risk_score(self, detection: Dict[str, Any]) -> int:
        categories = set(_normalize_categories(detection))
        severity = self.derive_severity(detection)
        hit_count = _safe_int(detection.get("hit_count"), 0)
        confidence = _safe_float(detection.get("confidence"), 0.0)

        score = 10

        if severity == SEVERITY_CRITICAL:
            score = 90
        elif severity == SEVERITY_HIGH:
            score = 75
        elif severity == SEVERITY_MEDIUM:
            score = 50
        elif severity == SEVERITY_LOW:
            score = 25

        if CATEGORY_EXPORT_CONTROL in categories or CATEGORY_ITAR in categories:
            score = max(score, 95)

        if CATEGORY_RANSOMWARE in categories:
            score = max(score, 98)

        if CATEGORY_CREDENTIAL in categories or CATEGORY_TOKEN in categories:
            score = max(score, 85)

        if CATEGORY_CUI in categories or CATEGORY_CTI in categories:
            score = max(score, 80)

        if CATEGORY_ENDPOINT_COMPROMISE in categories or CATEGORY_HOST_COMPROMISE in categories:
            score = max(score, 88)

        score += min(10, hit_count * 2)

        if confidence >= 0.90:
            score += 5
        elif confidence < 0.50:
            score -= 10

        return max(0, min(100, int(score)))

    def _result_event_type(
        self,
        response_results: List[AutonomousResponseResult],
    ) -> str:
        if not response_results:
            return EXECUTION_COMPLETED

        statuses = {str(r.status).upper() for r in response_results}

        if "FAILED" in statuses:
            return EXECUTION_FAILED

        if "BLOCKED" in statuses:
            return POLICY_VIOLATION

        if "WAITING_APPROVAL" in statuses:
            return APPROVAL_REQUIRED

        return EXECUTION_COMPLETED

    # -------------------------------------------------------------------------
    # Case / Alert Attachment
    # -------------------------------------------------------------------------

    def _attach_response_to_case_or_alert(
        self,
        *,
        result: AutonomousResponseResult,
        context: DetectionRouteContext,
        detection: Dict[str, Any],
    ) -> None:
        payload = {
            "route_id": context.route_id,
            "execution_id": result.execution_id,
            "job_id": result.job_id,
            "action": result.action,
            "status": result.status,
            "message": result.message,
            "rollback_id": result.rollback_id,
            "ok": result.ok,
            "detection_summary": {
                "categories": detection.get("categories"),
                "severity": detection.get("severity"),
                "risk_score": detection.get("risk_score"),
                "hit_count": detection.get("hit_count"),
            },
        }

        if context.case_id:
            self._add_case_event(context.case_id, payload, context)

        if context.alert_id:
            self._add_alert_note(context.alert_id, payload, context)

    def _add_case_event(
        self,
        case_id: str,
        payload: Dict[str, Any],
        context: DetectionRouteContext,
    ) -> None:
        methods = [
            "add_case_event",
            "record_case_event",
            "append_case_event",
        ]

        for method_name in methods:
            result = _call_ledger_method(
                self.storage,
                method_name,
                None,
                case_id=case_id,
                event_type="AUTONOMOUS_RESPONSE",
                actor=context.actor,
                details_json=payload,
                created_at_ms=_now_ms(),
            )
            if result is not None:
                return

        _record_custody_event(
            self.storage,
            event_type="CASE_AUTONOMOUS_RESPONSE_LINKED",
            actor=context.actor,
            tenant_id=context.tenant_id,
            evidence_id=context.evidence_id,
            case_id=case_id,
            alert_id=context.alert_id,
            run_id=context.run_id,
            details=payload,
        )

    def _add_alert_note(
        self,
        alert_id: str,
        payload: Dict[str, Any],
        context: DetectionRouteContext,
    ) -> None:
        methods = [
            "add_alert_event",
            "record_alert_event",
            "append_alert_note",
        ]

        for method_name in methods:
            result = _call_ledger_method(
                self.storage,
                method_name,
                None,
                alert_id=alert_id,
                event_type="AUTONOMOUS_RESPONSE",
                actor=context.actor,
                details_json=payload,
                created_at_ms=_now_ms(),
            )
            if result is not None:
                return

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def _result_to_dict(
        self,
        result: AutonomousResponseResult,
    ) -> Dict[str, Any]:
        try:
            data = asdict(result)
            return data
        except Exception:
            return {
                "ok": getattr(result, "ok", False),
                "execution_id": getattr(result, "execution_id", None),
                "job_id": getattr(result, "job_id", None),
                "action": getattr(result, "action", None),
                "status": getattr(result, "status", None),
                "message": getattr(result, "message", None),
            }


# =============================================================================
# Convenience Functions
# =============================================================================

def get_detection_response_router(
    storage: Any = None,
    *,
    autonomy_mode: str = DEFAULT_AUTONOMY_MODE,
    simulation_mode: bool = True,
) -> DetectionResponseRouter:
    return DetectionResponseRouter(
        storage=storage,
        autonomy_mode=autonomy_mode,
        simulation_mode=simulation_mode,
    )


def route_detection(
    storage: Any,
    detection: Dict[str, Any],
    *,
    tenant_id: str = "default",
    actor: str = ROUTER_SOURCE,
    case_id: Optional[str] = None,
    evidence_id: Optional[str] = None,
    alert_id: Optional[str] = None,
    run_id: Optional[str] = None,
    autonomy_mode: str = DEFAULT_AUTONOMY_MODE,
    simulation_mode: bool = True,
) -> DetectionRouteResult:
    router = get_detection_response_router(
        storage,
        autonomy_mode=autonomy_mode,
        simulation_mode=simulation_mode,
    )

    return router.route_detection(
        detection,
        tenant_id=tenant_id,
        actor=actor,
        case_id=case_id,
        evidence_id=evidence_id,
        alert_id=alert_id,
        run_id=run_id,
    )


def route_detections(
    storage: Any,
    detections: List[Dict[str, Any]],
    *,
    tenant_id: str = "default",
    actor: str = ROUTER_SOURCE,
    case_id: Optional[str] = None,
    run_id: Optional[str] = None,
    autonomy_mode: str = DEFAULT_AUTONOMY_MODE,
    simulation_mode: bool = True,
) -> List[DetectionRouteResult]:
    router = get_detection_response_router(
        storage,
        autonomy_mode=autonomy_mode,
        simulation_mode=simulation_mode,
    )

    return router.route_detections(
        detections,
        tenant_id=tenant_id,
        actor=actor,
        case_id=case_id,
        run_id=run_id,
    )