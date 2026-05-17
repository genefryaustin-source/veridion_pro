"""
core/connectors/connector_failover_orchestrator.py

Connector Failover Orchestrator

Sovereign failover cognition layer for connector execution.

This module decides:
- whether failover is allowed
- which fallback route should be attempted
- whether governance must be tightened
- whether autonomy should be reduced
- whether continuity review is required
- whether execution should be blocked

IMPORTANT:
This orchestrator DOES NOT execute connectors directly.

It does NOT:
- call Microsoft Graph
- call CrowdStrike
- call AWS
- mutate external systems
- perform connector execution

It ONLY:
- evaluates failover posture
- produces deterministic failover plans
- records memory/lineage/evidence
- optionally hands failover plans back to execution fabric/router
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_ORCHESTRATOR_NAME = "connector_failover_orchestrator"

FAILOVER_ALLOWED = "ALLOWED"
FAILOVER_BLOCKED = "BLOCKED"
FAILOVER_REQUIRES_GOVERNANCE = "REQUIRES_GOVERNANCE"
FAILOVER_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
FAILOVER_REQUIRES_CONTINUITY_REVIEW = "REQUIRES_CONTINUITY_REVIEW"
FAILOVER_REQUIRES_VERIFICATION_ARBITRATION = "REQUIRES_VERIFICATION_ARBITRATION"
FAILOVER_DEFERRED = "DEFERRED"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"

BLAST_RADIUS_LOW = "LOW"
BLAST_RADIUS_MEDIUM = "MEDIUM"
BLAST_RADIUS_HIGH = "HIGH"
BLAST_RADIUS_CRITICAL = "CRITICAL"

CONNECTOR_HEALTH_HEALTHY = "HEALTHY"
CONNECTOR_HEALTH_DEGRADED = "DEGRADED"
CONNECTOR_HEALTH_UNAVAILABLE = "UNAVAILABLE"
CONNECTOR_HEALTH_UNKNOWN = "UNKNOWN"


# ============================================================
# ENUMS
# ============================================================

class FailoverActionType(str, Enum):
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    ENRICH = "ENRICH"
    ESCALATE = "ESCALATE"
    NOTIFY = "NOTIFY"
    CONTAIN = "CONTAIN"
    ISOLATE_ENDPOINT = "ISOLATE_ENDPOINT"
    REVOKE_SESSION = "REVOKE_SESSION"
    DISABLE_USER = "DISABLE_USER"
    QUARANTINE_EMAIL = "QUARANTINE_EMAIL"
    DELETE_EMAIL = "DELETE_EMAIL"
    PURGE_MAILBOX = "PURGE_MAILBOX"
    BLOCK_NETWORK_TRAFFIC = "BLOCK_NETWORK_TRAFFIC"
    UPDATE_POLICY = "UPDATE_POLICY"
    ROLLBACK = "ROLLBACK"
    UNKNOWN = "UNKNOWN"


class FailoverConnectorTarget(str, Enum):
    MICROSOFT_GRAPH = "MICROSOFT_GRAPH"
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    CROWDSTRIKE = "CROWDSTRIKE"
    SENTINELONE = "SENTINELONE"
    AWS = "AWS"
    LOCAL_AGENT = "LOCAL_AGENT"
    GENERIC_CONNECTOR = "GENERIC_CONNECTOR"
    NONE = "NONE"


class FailoverReason(str, Enum):
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    CONNECTOR_DEGRADED = "CONNECTOR_DEGRADED"
    CONNECTOR_TIMEOUT = "CONNECTOR_TIMEOUT"
    CONNECTOR_AUTH_FAILURE = "CONNECTOR_AUTH_FAILURE"
    CONNECTOR_THROTTLED = "CONNECTOR_THROTTLED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    PARTIAL_EXECUTION = "PARTIAL_EXECUTION"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    GOVERNANCE_DEGRADED = "GOVERNANCE_DEGRADED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ConnectorFailoverRequest:
    """
    Failover evaluation request.
    """

    failover_request_id: str
    source_engine: str
    action_type: str
    failed_connector: str
    fallback_connectors: List[str]
    failover_reason: str
    severity: str
    confidence: float
    blast_radius: str
    autonomy_mode: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None
    execution_package_id: Optional[str] = None
    connector_result_id: Optional[str] = None

    governance_required: bool = False
    human_approval_required: bool = False
    legal_approval_required: bool = False
    continuity_sensitive: bool = False
    verification_failed: bool = False
    partial_execution_detected: bool = False
    rollback_available: bool = False
    tenant_failover_policy: str = "STANDARD"

    connector_health: Dict[str, str] = field(default_factory=dict)
    lineage_event_ids: List[str] = field(default_factory=list)
    evidence_event_ids: List[str] = field(default_factory=list)
    control_ids: List[str] = field(default_factory=list)

    payload: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class ConnectorFailoverPlan:
    """
    Deterministic failover plan.

    This is NOT an execution result.
    """

    failover_plan_id: str
    failover_request_id: str
    status: str

    action_type: str
    failed_connector: str
    selected_fallback_connector: str
    fallback_connectors: List[str]
    attempted_connectors: List[str]

    recommended_autonomy_mode: str
    governance_required: bool
    human_approval_required: bool
    continuity_review_required: bool
    verification_arbitration_required: bool
    rollback_recommended: bool

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]
    execution_package_id: Optional[str]
    connector_result_id: Optional[str]

    severity: str
    confidence: float
    blast_radius: str
    failover_reason: str

    constraints: List[str]
    recommended_next_steps: List[Dict[str, Any]]
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class ConnectorFailoverOrchestratorSnapshot:
    orchestrator_name: str
    total_requests_seen: int
    total_plans_created: int
    last_failover_plan_id: Optional[str]
    last_status: Optional[str]
    last_selected_fallback_connector: Optional[str]
    last_updated_ms: int


class ConnectorFailoverOrchestrator:
    """
    Connector failover cognition layer.

    Design guarantees:
    - no direct connector execution
    - deterministic failover planning
    - explicit dependency injection
    - replayable failover lineage
    """

    def __init__(
        self,
        *,
        orchestrator_name: str = DEFAULT_ORCHESTRATOR_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
        connector_execution_fabric: Optional[Any] = None,
        auto_handoff_to_execution_fabric: bool = False,
    ) -> None:
        self.orchestrator_name = orchestrator_name
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine
        self.connector_execution_fabric = connector_execution_fabric
        self.auto_handoff_to_execution_fabric = auto_handoff_to_execution_fabric

        self._requests_seen = 0
        self._plans: List[ConnectorFailoverPlan] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        request: ConnectorFailoverRequest | Dict[str, Any],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConnectorFailoverPlan:
        """
        Evaluate failover request and produce deterministic plan.
        """

        normalized = self._normalize_request(request)
        self._requests_seen += 1

        status = self._determine_status(normalized)
        selected_fallback = self._select_fallback_connector(normalized, status)
        recommended_autonomy = self._recommended_autonomy_mode(
            normalized,
            status,
        )

        plan = ConnectorFailoverPlan(
            failover_plan_id=str(uuid.uuid4()),
            failover_request_id=normalized.failover_request_id,
            status=status,
            action_type=normalized.action_type,
            failed_connector=normalized.failed_connector,
            selected_fallback_connector=selected_fallback,
            fallback_connectors=list(normalized.fallback_connectors),
            attempted_connectors=self._attempted_connectors(normalized),
            recommended_autonomy_mode=recommended_autonomy,
            governance_required=self._governance_required(normalized, status),
            human_approval_required=self._human_approval_required(
                normalized,
                status,
            ),
            continuity_review_required=(
                status == FAILOVER_REQUIRES_CONTINUITY_REVIEW
            ),
            verification_arbitration_required=(
                status == FAILOVER_REQUIRES_VERIFICATION_ARBITRATION
            ),
            rollback_recommended=self._rollback_recommended(normalized, status),
            tenant_id=normalized.tenant_id,
            case_id=normalized.case_id,
            correlation_id=normalized.correlation_id,
            execution_package_id=normalized.execution_package_id,
            connector_result_id=normalized.connector_result_id,
            severity=normalized.severity,
            confidence=normalized.confidence,
            blast_radius=normalized.blast_radius,
            failover_reason=normalized.failover_reason,
            constraints=self._constraints(normalized, status),
            recommended_next_steps=self._recommended_next_steps(
                normalized,
                status,
                selected_fallback,
                recommended_autonomy,
            ),
            rationale=self._build_rationale(
                normalized,
                status,
                selected_fallback,
                recommended_autonomy,
            ),
            metadata={
                "tenant_failover_policy": normalized.tenant_failover_policy,
                "connector_health": dict(normalized.connector_health),
                "lineage_event_ids": list(normalized.lineage_event_ids),
                "evidence_event_ids": list(normalized.evidence_event_ids),
                "control_ids": list(normalized.control_ids),
            },
        )

        self._record_plan(plan, context=context)
        self._optional_execution_fabric_handoff(plan, context=context)

        return plan

    def submit(
        self,
        request: ConnectorFailoverRequest | Dict[str, Any],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ConnectorFailoverPlan:
        """
        Compatibility alias.
        """

        return self.evaluate(request, context=context)

    def create_request(
        self,
        *,
        source_engine: str,
        action_type: str,
        failed_connector: str,
        fallback_connectors: Sequence[str],
        failover_reason: str,
        severity: str,
        confidence: float,
        blast_radius: str,
        autonomy_mode: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        execution_package_id: Optional[str] = None,
        connector_result_id: Optional[str] = None,
        governance_required: bool = False,
        human_approval_required: bool = False,
        legal_approval_required: bool = False,
        continuity_sensitive: bool = False,
        verification_failed: bool = False,
        partial_execution_detected: bool = False,
        rollback_available: bool = False,
        tenant_failover_policy: str = "STANDARD",
        connector_health: Optional[Dict[str, str]] = None,
        lineage_event_ids: Optional[Sequence[str]] = None,
        evidence_event_ids: Optional[Sequence[str]] = None,
        control_ids: Optional[Sequence[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        constraints: Optional[Sequence[str]] = None,
    ) -> ConnectorFailoverRequest:
        """
        Convenience constructor.
        """

        return ConnectorFailoverRequest(
            failover_request_id=str(uuid.uuid4()),
            source_engine=source_engine or "unknown_engine",
            action_type=self._safe_action_type(action_type),
            failed_connector=self._safe_connector(failed_connector),
            fallback_connectors=[
                self._safe_connector(item)
                for item in list(fallback_connectors or [])
            ],
            failover_reason=self._safe_failover_reason(failover_reason),
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            blast_radius=self._safe_blast_radius(blast_radius),
            autonomy_mode=self._safe_autonomy_mode(autonomy_mode),
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            execution_package_id=execution_package_id,
            connector_result_id=connector_result_id,
            governance_required=governance_required,
            human_approval_required=human_approval_required,
            legal_approval_required=legal_approval_required,
            continuity_sensitive=continuity_sensitive,
            verification_failed=verification_failed,
            partial_execution_detected=partial_execution_detected,
            rollback_available=rollback_available,
            tenant_failover_policy=str(tenant_failover_policy or "STANDARD").upper(),
            connector_health={
                self._safe_connector(k): str(v or CONNECTOR_HEALTH_UNKNOWN).upper()
                for k, v in dict(connector_health or {}).items()
            },
            lineage_event_ids=list(lineage_event_ids or []),
            evidence_event_ids=list(evidence_event_ids or []),
            control_ids=[
                str(item or "").upper().strip()
                for item in list(control_ids or [])
            ],
            payload=dict(payload or {}),
            constraints=list(constraints or []),
        )

    def create_request_from_execution_result(
        self,
        result: Any,
        *,
        execution_package: Optional[Any] = None,
        fallback_connectors: Optional[Sequence[str]] = None,
        connector_health: Optional[Dict[str, str]] = None,
    ) -> ConnectorFailoverRequest:
        """
        Build failover request from connector execution result and optional package.
        """

        rget = result.get if isinstance(result, dict) else lambda k, d=None: getattr(result, k, d)
        package_dict = self._to_dict(execution_package) if execution_package is not None else {}

        return self.create_request(
            source_engine="connector_execution_fabric",
            action_type=str(rget("action_type", package_dict.get("action_type", "UNKNOWN"))),
            failed_connector=str(rget("selected_connector", "GENERIC_CONNECTOR")),
            fallback_connectors=fallback_connectors
            or package_dict.get("fallback_connectors", [])
            or [],
            failover_reason=(
                FailoverReason.VERIFICATION_FAILED.value
                if rget("verification_succeeded", None) is False
                else FailoverReason.EXECUTION_FAILED.value
            ),
            severity=str(package_dict.get("severity", "MEDIUM")),
            confidence=0.75,
            blast_radius=str(package_dict.get("blast_radius", BLAST_RADIUS_MEDIUM)),
            autonomy_mode=str(package_dict.get("autonomy_mode", AUTONOMY_SUPERVISED_AUTONOMY)),
            tenant_id=rget("tenant_id", package_dict.get("tenant_id")),
            case_id=rget("case_id", package_dict.get("case_id")),
            correlation_id=rget("correlation_id", package_dict.get("correlation_id")),
            execution_package_id=rget(
                "execution_package_id",
                package_dict.get("execution_package_id"),
            ),
            connector_result_id=rget("result_id"),
            governance_required=bool(
                package_dict.get("governance_metadata", {}).get(
                    "governance_required",
                    False,
                )
            ),
            human_approval_required=bool(
                package_dict.get("governance_metadata", {}).get(
                    "human_approval_required",
                    False,
                )
            ),
            legal_approval_required=bool(
                package_dict.get("governance_metadata", {}).get(
                    "legal_approval_required",
                    False,
                )
            ),
            continuity_sensitive=bool(
                package_dict.get("verification_metadata", {}).get(
                    "continuity_review_required",
                    False,
                )
            ),
            verification_failed=bool(rget("verification_succeeded", None) is False),
            partial_execution_detected=bool(
                rget("connector_response", {}).get(
                    "partial_execution_detected",
                    False,
                )
            ),
            rollback_available=bool(
                package_dict.get("rollback_metadata", {}).get(
                    "rollback_available",
                    False,
                )
            ),
            connector_health=connector_health or {},
            lineage_event_ids=list(
                package_dict.get("lineage_metadata", {}).get(
                    "lineage_event_ids",
                    [],
                )
            ),
            evidence_event_ids=list(
                package_dict.get("compliance_metadata", {}).get(
                    "evidence_event_ids",
                    [],
                )
            ),
            control_ids=list(
                package_dict.get("compliance_metadata", {}).get(
                    "control_ids",
                    [],
                )
            ),
            payload={
                "connector_result": self._to_dict(result),
                "execution_package": package_dict,
            },
        )

    def get_recent_plans(
        self,
        *,
        limit: int = 25,
    ) -> List[ConnectorFailoverPlan]:
        limit = max(1, int(limit))
        return list(reversed(self._plans[-limit:]))

    def snapshot(self) -> ConnectorFailoverOrchestratorSnapshot:
        last = self._plans[-1] if self._plans else None

        return ConnectorFailoverOrchestratorSnapshot(
            orchestrator_name=self.orchestrator_name,
            total_requests_seen=self._requests_seen,
            total_plans_created=len(self._plans),
            last_failover_plan_id=last.failover_plan_id if last else None,
            last_status=last.status if last else None,
            last_selected_fallback_connector=(
                last.selected_fallback_connector if last else None
            ),
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # FAILOVER DECISIONING
    # --------------------------------------------------------

    def _determine_status(
        self,
        request: ConnectorFailoverRequest,
    ) -> str:
        if request.autonomy_mode == AUTONOMY_LOCKDOWN:
            return FAILOVER_BLOCKED

        if not request.fallback_connectors:
            return FAILOVER_DEFERRED

        if request.partial_execution_detected:
            return FAILOVER_REQUIRES_VERIFICATION_ARBITRATION

        if request.verification_failed:
            if request.action_type in {
                FailoverActionType.DISABLE_USER.value,
                FailoverActionType.PURGE_MAILBOX.value,
                FailoverActionType.DELETE_EMAIL.value,
                FailoverActionType.BLOCK_NETWORK_TRAFFIC.value,
            }:
                return FAILOVER_REQUIRES_VERIFICATION_ARBITRATION

        if request.continuity_sensitive:
            return FAILOVER_REQUIRES_CONTINUITY_REVIEW

        if request.legal_approval_required:
            return FAILOVER_REQUIRES_APPROVAL

        if request.human_approval_required:
            return FAILOVER_REQUIRES_APPROVAL

        if request.governance_required:
            return FAILOVER_REQUIRES_GOVERNANCE

        if request.blast_radius == BLAST_RADIUS_CRITICAL:
            return FAILOVER_REQUIRES_APPROVAL

        if request.blast_radius == BLAST_RADIUS_HIGH:
            if request.autonomy_mode not in {
                AUTONOMY_SUPERVISED_AUTONOMY,
                AUTONOMY_FULL_AUTONOMY,
            }:
                return FAILOVER_REQUIRES_APPROVAL

        if request.action_type in {
            FailoverActionType.PURGE_MAILBOX.value,
            FailoverActionType.DELETE_EMAIL.value,
            FailoverActionType.UPDATE_POLICY.value,
        }:
            return FAILOVER_REQUIRES_GOVERNANCE

        if str(request.tenant_failover_policy).upper() in {
            "STRICT",
            "MANUAL_ONLY",
        }:
            return FAILOVER_REQUIRES_APPROVAL

        return FAILOVER_ALLOWED

    def _select_fallback_connector(
        self,
        request: ConnectorFailoverRequest,
        status: str,
    ) -> str:
        if status != FAILOVER_ALLOWED:
            return FailoverConnectorTarget.NONE.value

        for connector in request.fallback_connectors:
            if connector == request.failed_connector:
                continue

            health = request.connector_health.get(
                connector,
                CONNECTOR_HEALTH_UNKNOWN,
            )

            if health in {
                CONNECTOR_HEALTH_HEALTHY,
                CONNECTOR_HEALTH_UNKNOWN,
            }:
                return connector

        for connector in request.fallback_connectors:
            if connector != request.failed_connector:
                return connector

        return FailoverConnectorTarget.NONE.value

    def _recommended_autonomy_mode(
        self,
        request: ConnectorFailoverRequest,
        status: str,
    ) -> str:
        if status == FAILOVER_BLOCKED:
            return AUTONOMY_LOCKDOWN

        if status in {
            FAILOVER_REQUIRES_APPROVAL,
            FAILOVER_REQUIRES_GOVERNANCE,
            FAILOVER_REQUIRES_CONTINUITY_REVIEW,
            FAILOVER_REQUIRES_VERIFICATION_ARBITRATION,
        }:
            return self._reduce_autonomy(request.autonomy_mode)

        if request.failover_reason in {
            FailoverReason.GOVERNANCE_DEGRADED.value,
            FailoverReason.VERIFICATION_FAILED.value,
        }:
            return self._reduce_autonomy(request.autonomy_mode)

        return request.autonomy_mode

    def _governance_required(
        self,
        request: ConnectorFailoverRequest,
        status: str,
    ) -> bool:
        return (
            request.governance_required
            or status == FAILOVER_REQUIRES_GOVERNANCE
            or status == FAILOVER_REQUIRES_APPROVAL
            or request.action_type
            in {
                FailoverActionType.PURGE_MAILBOX.value,
                FailoverActionType.DELETE_EMAIL.value,
                FailoverActionType.UPDATE_POLICY.value,
            }
        )

    def _human_approval_required(
        self,
        request: ConnectorFailoverRequest,
        status: str,
    ) -> bool:
        return (
            request.human_approval_required
            or request.legal_approval_required
            or status == FAILOVER_REQUIRES_APPROVAL
            or request.blast_radius == BLAST_RADIUS_CRITICAL
        )

    def _rollback_recommended(
        self,
        request: ConnectorFailoverRequest,
        status: str,
    ) -> bool:
        return (
            request.partial_execution_detected
            or request.verification_failed
            or status
            in {
                FAILOVER_REQUIRES_VERIFICATION_ARBITRATION,
                FAILOVER_BLOCKED,
            }
        ) and not request.rollback_available

    def _constraints(
        self,
        request: ConnectorFailoverRequest,
        status: str,
    ) -> List[str]:
        constraints = list(request.constraints)

        if status == FAILOVER_REQUIRES_GOVERNANCE:
            constraints.append("governance_revalidation")

        if status == FAILOVER_REQUIRES_APPROVAL:
            constraints.append("human_approval_required")

        if status == FAILOVER_REQUIRES_CONTINUITY_REVIEW:
            constraints.append("continuity_review_required")

        if status == FAILOVER_REQUIRES_VERIFICATION_ARBITRATION:
            constraints.append("verification_arbitration_required")

        if request.partial_execution_detected:
            constraints.append("partial_execution_detected")

        if request.verification_failed:
            constraints.append("verification_failed")

        if request.blast_radius in {BLAST_RADIUS_HIGH, BLAST_RADIUS_CRITICAL}:
            constraints.append("high_blast_radius_failover")

        if request.tenant_failover_policy != "STANDARD":
            constraints.append(
                f"tenant_failover_policy_{request.tenant_failover_policy}"
            )

        return list(dict.fromkeys(constraints))

    def _attempted_connectors(
        self,
        request: ConnectorFailoverRequest,
    ) -> List[str]:
        attempted = [request.failed_connector]
        return list(dict.fromkeys(attempted))

    def _recommended_next_steps(
        self,
        request: ConnectorFailoverRequest,
        status: str,
        selected_fallback: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:
        steps: List[Dict[str, Any]] = []

        if status == FAILOVER_ALLOWED:
            steps.append(
                {
                    "step": "route_to_fallback_connector",
                    "fallback_connector": selected_fallback,
                }
            )

        if status == FAILOVER_BLOCKED:
            steps.append(
                {
                    "step": "block_failover",
                    "reason": "Failover is not allowed under current posture.",
                }
            )

        if status == FAILOVER_REQUIRES_GOVERNANCE:
            steps.append(
                {
                    "step": "route_to_governance_revalidation",
                    "reason": "Governance must be revalidated before failover.",
                }
            )

        if status == FAILOVER_REQUIRES_APPROVAL:
            steps.append(
                {
                    "step": "request_human_approval",
                    "reason": "Approval required before failover.",
                }
            )

        if status == FAILOVER_REQUIRES_CONTINUITY_REVIEW:
            steps.append(
                {
                    "step": "perform_continuity_review",
                    "reason": "Failover may affect mission continuity.",
                }
            )

        if status == FAILOVER_REQUIRES_VERIFICATION_ARBITRATION:
            steps.append(
                {
                    "step": "start_verification_arbitration",
                    "reason": "Execution state may be inconsistent.",
                }
            )

        if recommended_autonomy != request.autonomy_mode:
            steps.append(
                {
                    "step": "recommend_autonomy_change",
                    "from": request.autonomy_mode,
                    "to": recommended_autonomy,
                }
            )

        if self._rollback_recommended(request, status):
            steps.append(
                {
                    "step": "prepare_or_attach_rollback",
                    "reason": "Rollback recommended before further execution.",
                }
            )

        steps.append(
            {
                "step": "record_failover_lineage",
                "reason": "Failover decision must be replayable.",
            }
        )

        steps.append(
            {
                "step": "record_failover_compliance_evidence",
                "reason": "Failover contributes to audit evidence.",
            }
        )

        return steps

    def _build_rationale(
        self,
        request: ConnectorFailoverRequest,
        status: str,
        selected_fallback: str,
        recommended_autonomy: str,
    ) -> str:
        return (
            f"Failover request for action {request.action_type} from failed "
            f"connector {request.failed_connector}. Reason: "
            f"{request.failover_reason}. Blast radius {request.blast_radius}; "
            f"autonomy {request.autonomy_mode}; tenant policy "
            f"{request.tenant_failover_policy}. Status: {status}; selected "
            f"fallback: {selected_fallback}; recommended autonomy: "
            f"{recommended_autonomy}."
        )

    # --------------------------------------------------------
    # RECORDING / HANDOFF
    # --------------------------------------------------------

    def _record_plan(
        self,
        plan: ConnectorFailoverPlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._plans.append(plan)
        self._write_to_memory(plan, context=context)
        self._write_to_lineage(plan, context=context)
        self._write_to_evidence(plan, context=context)
        self._emit_event(plan, context=context)

    def _optional_execution_fabric_handoff(
        self,
        plan: ConnectorFailoverPlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Optional handoff to execution fabric.

        This does not execute connectors here. It only hands off a plan.
        """

        if not self.auto_handoff_to_execution_fabric:
            return

        if self.connector_execution_fabric is None:
            return

        if plan.status != FAILOVER_ALLOWED:
            return

        try:
            if hasattr(self.connector_execution_fabric, "submit_failover_plan"):
                self.connector_execution_fabric.submit_failover_plan(
                    plan,
                    context=context or {},
                )
            elif hasattr(self.connector_execution_fabric, "submit"):
                self.connector_execution_fabric.submit(
                    plan,
                    context=context or {},
                )
        except Exception as exc:
            print(
                "⚠️ Connector failover orchestrator handoff failed: "
                f"{exc}"
            )

    def _write_to_memory(
        self,
        plan: ConnectorFailoverPlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "CONNECTOR_FAILOVER_PLAN",
            "plan": asdict(plan),
            "context": context or {},
        }

        try:
            if hasattr(memory, "append_memory"):
                memory.append_memory(payload)
            elif hasattr(memory, "record"):
                memory.record(payload)
            elif hasattr(memory, "write"):
                memory.write(payload)
        except Exception as exc:
            print(f"⚠️ Connector failover memory write failed: {exc}")

    def _write_to_lineage(
        self,
        plan: ConnectorFailoverPlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "EXECUTION",
            "lineage_status": "RECORDED",
            "source_engine": self.orchestrator_name,
            "summary": plan.rationale,
            "severity": plan.severity,
            "confidence": plan.confidence,
            "mission_priority": 0,
            "tenant_id": plan.tenant_id,
            "case_id": plan.case_id,
            "correlation_id": plan.correlation_id,
            "parent_event_ids": list(
                plan.metadata.get("lineage_event_ids", [])
            ),
            "constraints": list(plan.constraints),
            "verification_requirements": [
                "verification_arbitration_required"
                if plan.verification_arbitration_required
                else "standard_verification"
            ],
            "context": {
                "type": "CONNECTOR_FAILOVER_PLAN",
                "plan": asdict(plan),
                "context": context or {},
            },
            "metadata": {
                "failover_plan_id": plan.failover_plan_id,
                "status": plan.status,
                "selected_fallback_connector": (
                    plan.selected_fallback_connector
                ),
                "rollback_recommended": plan.rollback_recommended,
            },
        }

        try:
            if hasattr(lineage, "record_lineage"):
                lineage.record_lineage(payload)
            elif hasattr(lineage, "append_lineage"):
                lineage.append_lineage(payload)
            elif hasattr(lineage, "record"):
                lineage.record(payload)
        except Exception as exc:
            print(f"⚠️ Connector failover lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        plan: ConnectorFailoverPlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        evidence = self.fedramp_evidence_lineage_engine
        if evidence is None:
            return

        payload = {
            "evidence_type": "RESILIENCE_DECISION",
            "evidence_status": "RECORDED",
            "source_engine": self.orchestrator_name,
            "summary": plan.rationale,
            "severity": plan.severity,
            "confidence": plan.confidence,
            "mission_priority": 0,
            "tenant_id": plan.tenant_id,
            "case_id": plan.case_id,
            "correlation_id": plan.correlation_id,
            "lineage_event_ids": list(
                plan.metadata.get("lineage_event_ids", [])
            ),
            "parent_evidence_event_ids": list(
                plan.metadata.get("evidence_event_ids", [])
            ),
            "related_control_ids": list(
                plan.metadata.get("control_ids", [])
            ),
            "constraints": list(plan.constraints),
            "evidence_payload": {
                "type": "CONNECTOR_FAILOVER_PLAN",
                "plan": asdict(plan),
                "context": context or {},
            },
            "metadata": {
                "failover_plan_id": plan.failover_plan_id,
                "status": plan.status,
                "selected_fallback_connector": (
                    plan.selected_fallback_connector
                ),
                "rollback_recommended": plan.rollback_recommended,
            },
        }

        try:
            if hasattr(evidence, "record_evidence"):
                evidence.record_evidence(payload)
            elif hasattr(evidence, "append_evidence"):
                evidence.append_evidence(payload)
            elif hasattr(evidence, "record"):
                evidence.record(payload)
        except Exception as exc:
            print(f"⚠️ Connector failover evidence write failed: {exc}")

    def _emit_event(
        self,
        plan: ConnectorFailoverPlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "CONNECTOR_FAILOVER_PLAN_CREATED",
            "orchestrator_name": self.orchestrator_name,
            "plan": asdict(plan),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "CONNECTOR_FAILOVER_PLAN_CREATED",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "CONNECTOR_FAILOVER_PLAN_CREATED",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Connector failover event emit failed: {exc}")

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_request(
        self,
        request: ConnectorFailoverRequest | Dict[str, Any],
    ) -> ConnectorFailoverRequest:
        if isinstance(request, ConnectorFailoverRequest):
            return request

        return ConnectorFailoverRequest(
            failover_request_id=str(
                request.get("failover_request_id") or uuid.uuid4()
            ),
            source_engine=str(request.get("source_engine") or "unknown_engine"),
            action_type=self._safe_action_type(request.get("action_type")),
            failed_connector=self._safe_connector(
                request.get("failed_connector")
            ),
            fallback_connectors=[
                self._safe_connector(item)
                for item in list(request.get("fallback_connectors", []) or [])
            ],
            failover_reason=self._safe_failover_reason(
                request.get("failover_reason")
            ),
            severity=self._safe_severity(request.get("severity")),
            confidence=self._clamp_confidence(request.get("confidence", 0.0)),
            blast_radius=self._safe_blast_radius(request.get("blast_radius")),
            autonomy_mode=self._safe_autonomy_mode(
                request.get("autonomy_mode")
            ),
            tenant_id=request.get("tenant_id"),
            case_id=request.get("case_id"),
            correlation_id=request.get("correlation_id"),
            execution_package_id=request.get("execution_package_id"),
            connector_result_id=request.get("connector_result_id"),
            governance_required=bool(
                request.get("governance_required", False)
            ),
            human_approval_required=bool(
                request.get("human_approval_required", False)
            ),
            legal_approval_required=bool(
                request.get("legal_approval_required", False)
            ),
            continuity_sensitive=bool(
                request.get("continuity_sensitive", False)
            ),
            verification_failed=bool(
                request.get("verification_failed", False)
            ),
            partial_execution_detected=bool(
                request.get("partial_execution_detected", False)
            ),
            rollback_available=bool(
                request.get("rollback_available", False)
            ),
            tenant_failover_policy=str(
                request.get("tenant_failover_policy") or "STANDARD"
            ).upper(),
            connector_health={
                self._safe_connector(k): str(v or CONNECTOR_HEALTH_UNKNOWN).upper()
                for k, v in dict(
                    request.get("connector_health", {}) or {}
                ).items()
            },
            lineage_event_ids=list(
                request.get("lineage_event_ids", []) or []
            ),
            evidence_event_ids=list(
                request.get("evidence_event_ids", []) or []
            ),
            control_ids=[
                str(item or "").upper().strip()
                for item in list(request.get("control_ids", []) or [])
            ],
            payload=dict(request.get("payload", {}) or {}),
            constraints=list(request.get("constraints", []) or []),
        )

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _reduce_autonomy(current: str) -> str:
        current = str(current or AUTONOMY_SUPERVISED_AUTONOMY).upper()

        order = [
            AUTONOMY_LOCKDOWN,
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
        ]

        if current not in order:
            return AUTONOMY_ASSISTED

        idx = order.index(current)
        return order[max(0, idx - 1)]

    @staticmethod
    def _safe_action_type(value: Any) -> str:
        value = str(value or FailoverActionType.UNKNOWN.value).upper()
        valid = {item.value for item in FailoverActionType}
        return value if value in valid else FailoverActionType.UNKNOWN.value

    @staticmethod
    def _safe_connector(value: Any) -> str:
        value = str(value or FailoverConnectorTarget.GENERIC_CONNECTOR.value).upper()
        valid = {item.value for item in FailoverConnectorTarget}
        return value if value in valid else value

    @staticmethod
    def _safe_failover_reason(value: Any) -> str:
        value = str(value or FailoverReason.UNKNOWN.value).upper()
        valid = {item.value for item in FailoverReason}
        return value if value in valid else FailoverReason.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or "INFO").upper()
        valid = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
        return value if value in valid else "INFO"

    @staticmethod
    def _safe_blast_radius(value: Any) -> str:
        value = str(value or BLAST_RADIUS_LOW).upper()
        valid = {
            BLAST_RADIUS_LOW,
            BLAST_RADIUS_MEDIUM,
            BLAST_RADIUS_HIGH,
            BLAST_RADIUS_CRITICAL,
        }
        return value if value in valid else BLAST_RADIUS_LOW

    @staticmethod
    def _safe_autonomy_mode(value: Any) -> str:
        value = str(value or AUTONOMY_SUPERVISED_AUTONOMY).upper()
        valid = {
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
            AUTONOMY_LOCKDOWN,
        }
        return value if value in valid else AUTONOMY_SUPERVISED_AUTONOMY

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def _to_dict(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return dict(value)
        if hasattr(value, "__dataclass_fields__"):
            return asdict(value)
        if hasattr(value, "__dict__"):
            return dict(value.__dict__)
        return {"value": value}


# ============================================================
# FACTORY
# ============================================================

def build_connector_failover_orchestrator(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    connector_execution_fabric: Optional[Any] = None,
    auto_handoff_to_execution_fabric: bool = False,
) -> ConnectorFailoverOrchestrator:
    """
    Factory for explicit dependency injection.
    """

    return ConnectorFailoverOrchestrator(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
        connector_execution_fabric=connector_execution_fabric,
        auto_handoff_to_execution_fabric=auto_handoff_to_execution_fabric,
    )