"""
core/runtime/sovereign_execution_router.py

Sovereign Execution Router

Governed execution handoff layer between:

    execution alignment / governance / resilience / evidence lineage
        ↓
    sovereign execution router
        ↓
    connector execution fabric

IMPORTANT:
This router DOES NOT execute connector actions.

It does NOT:
- call Microsoft Graph
- isolate endpoints
- revoke sessions
- quarantine mailboxes
- delete data
- mutate external systems

It ONLY:
- validates execution handoff readiness
- selects execution route targets
- packages governed execution requests
- attaches safety, lineage, rollback, verification, and compliance metadata
- optionally hands the package to connector_execution_fabric if injected
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

DEFAULT_ROUTER_NAME = "sovereign_execution_router"

ROUTE_STATUS_READY = "READY"
ROUTE_STATUS_BLOCKED = "BLOCKED"
ROUTE_STATUS_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
ROUTE_STATUS_REQUIRES_GOVERNANCE = "REQUIRES_GOVERNANCE"
ROUTE_STATUS_REQUIRES_ROLLBACK_PLAN = "REQUIRES_ROLLBACK_PLAN"
ROUTE_STATUS_REQUIRES_CONTINUITY_REVIEW = "REQUIRES_CONTINUITY_REVIEW"
ROUTE_STATUS_DEFERRED = "DEFERRED"
ROUTE_STATUS_DEGRADED = "DEGRADED"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"

BLAST_RADIUS_LOW = "LOW"
BLAST_RADIUS_MEDIUM = "MEDIUM"
BLAST_RADIUS_HIGH = "HIGH"
BLAST_RADIUS_CRITICAL = "CRITICAL"


# ============================================================
# ENUMS
# ============================================================

class ExecutionRouteType(str, Enum):
    OBSERVABILITY = "OBSERVABILITY"
    GOVERNANCE_QUEUE = "GOVERNANCE_QUEUE"
    APPROVAL_QUEUE = "APPROVAL_QUEUE"
    CONNECTOR_FABRIC = "CONNECTOR_FABRIC"
    CASE_ORCHESTRATION = "CASE_ORCHESTRATION"
    ROLLBACK_ORCHESTRATION = "ROLLBACK_ORCHESTRATION"
    CONTINUITY_REVIEW = "CONTINUITY_REVIEW"
    BLOCKED_REGISTER = "BLOCKED_REGISTER"
    DEFERRED_QUEUE = "DEFERRED_QUEUE"


class ExecutionConnectorTarget(str, Enum):
    MICROSOFT_GRAPH = "MICROSOFT_GRAPH"
    GOOGLE_WORKSPACE = "GOOGLE_WORKSPACE"
    CROWDSTRIKE = "CROWDSTRIKE"
    SENTINELONE = "SENTINELONE"
    AWS = "AWS"
    LOCAL_AGENT = "LOCAL_AGENT"
    GENERIC_CONNECTOR = "GENERIC_CONNECTOR"
    NONE = "NONE"


class ExecutionActionType(str, Enum):
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


class RouteSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class SovereignExecutionRouteRequest:
    """
    Request entering the execution router.

    This should be created from:
    - execution alignment verdicts
    - governance approvals
    - resilience posture
    - continuity review
    - rollback readiness
    """

    route_request_id: str
    source_engine: str
    action_type: str
    severity: str
    confidence: float
    mission_priority: int
    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    alignment_verdict_id: Optional[str] = None
    governance_approval_id: Optional[str] = None
    resilience_decision_id: Optional[str] = None
    continuity_review_id: Optional[str] = None
    rollback_plan_id: Optional[str] = None
    evidence_chain_id: Optional[str] = None

    autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY
    blast_radius: str = BLAST_RADIUS_LOW

    allowed: bool = False
    blocked: bool = False
    governance_required: bool = False
    human_approval_required: bool = False
    legal_approval_required: bool = False
    rollback_required: bool = False
    rollback_available: bool = False
    continuity_review_required: bool = False
    verification_required: bool = True
    degraded_mode: bool = False
    failover_allowed: bool = True

    requested_connector: Optional[str] = None
    fallback_connectors: List[str] = field(default_factory=list)

    lineage_event_ids: List[str] = field(default_factory=list)
    evidence_event_ids: List[str] = field(default_factory=list)
    control_ids: List[str] = field(default_factory=list)

    payload: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignExecutionPackage:
    """
    Governed execution handoff package.

    This package may be handed to connector_execution_fabric,
    but this router does not execute it directly.
    """

    execution_package_id: str
    route_request_id: str
    route_status: str

    action_type: str
    selected_route: str
    selected_connector: str
    fallback_connectors: List[str]

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    severity: str
    confidence: float
    mission_priority: int
    autonomy_mode: str
    blast_radius: str

    governance_metadata: Dict[str, Any]
    safety_metadata: Dict[str, Any]
    rollback_metadata: Dict[str, Any]
    verification_metadata: Dict[str, Any]
    lineage_metadata: Dict[str, Any]
    compliance_metadata: Dict[str, Any]

    payload: Dict[str, Any]
    constraints: List[str]
    recommended_next_steps: List[Dict[str, Any]]
    rationale: str

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignExecutionRouterSnapshot:
    """
    Lightweight runtime diagnostics snapshot.
    """

    router_name: str
    total_requests_seen: int
    total_packages_created: int
    last_execution_package_id: Optional[str]
    last_route_status: Optional[str]
    last_selected_connector: Optional[str]
    last_updated_ms: int


# ============================================================
# ROUTER
# ============================================================

class SovereignExecutionRouter:
    """
    Deterministic governed execution handoff router.

    Design guarantees:
    - no direct connector execution
    - no external system mutation
    - explicit dependency injection
    - deterministic package creation
    - replayable routing metadata
    """

    def __init__(
        self,
        *,
        router_name: str = DEFAULT_ROUTER_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
        connector_execution_fabric: Optional[Any] = None,
        auto_handoff_to_connector_fabric: bool = False,
    ) -> None:
        self.router_name = router_name
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine
        self.connector_execution_fabric = connector_execution_fabric
        self.auto_handoff_to_connector_fabric = auto_handoff_to_connector_fabric

        self._requests_seen = 0
        self._packages: List[SovereignExecutionPackage] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def route(
        self,
        request: SovereignExecutionRouteRequest | Dict[str, Any],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignExecutionPackage:
        """
        Route a governed execution request into a handoff package.
        """

        normalized = self._normalize_request(request)
        self._requests_seen += 1

        route_status = self._determine_route_status(normalized)
        selected_route = self._determine_route(normalized, route_status)
        selected_connector = self._select_connector(normalized, selected_route)

        package = SovereignExecutionPackage(
            execution_package_id=str(uuid.uuid4()),
            route_request_id=normalized.route_request_id,
            route_status=route_status,
            action_type=normalized.action_type,
            selected_route=selected_route,
            selected_connector=selected_connector,
            fallback_connectors=list(normalized.fallback_connectors),
            tenant_id=normalized.tenant_id,
            case_id=normalized.case_id,
            correlation_id=normalized.correlation_id,
            severity=normalized.severity,
            confidence=normalized.confidence,
            mission_priority=normalized.mission_priority,
            autonomy_mode=normalized.autonomy_mode,
            blast_radius=normalized.blast_radius,
            governance_metadata=self._governance_metadata(normalized),
            safety_metadata=self._safety_metadata(normalized, route_status),
            rollback_metadata=self._rollback_metadata(normalized),
            verification_metadata=self._verification_metadata(normalized),
            lineage_metadata=self._lineage_metadata(normalized),
            compliance_metadata=self._compliance_metadata(normalized),
            payload=dict(normalized.payload),
            constraints=list(normalized.constraints),
            recommended_next_steps=self._recommended_next_steps(
                normalized,
                route_status,
                selected_route,
                selected_connector,
            ),
            rationale=self._build_rationale(
                normalized,
                route_status,
                selected_route,
                selected_connector,
            ),
        )

        self._record_package(package, context=context)
        self._optional_connector_fabric_handoff(package, context=context)

        return package

    def submit(
        self,
        request: SovereignExecutionRouteRequest | Dict[str, Any],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignExecutionPackage:
        """
        Compatibility alias.
        """

        return self.route(request, context=context)

    def create_request(
        self,
        *,
        source_engine: str,
        action_type: str,
        severity: str,
        confidence: float,
        mission_priority: int,
        summary: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        alignment_verdict_id: Optional[str] = None,
        governance_approval_id: Optional[str] = None,
        resilience_decision_id: Optional[str] = None,
        continuity_review_id: Optional[str] = None,
        rollback_plan_id: Optional[str] = None,
        evidence_chain_id: Optional[str] = None,
        autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY,
        blast_radius: str = BLAST_RADIUS_LOW,
        allowed: bool = False,
        blocked: bool = False,
        governance_required: bool = False,
        human_approval_required: bool = False,
        legal_approval_required: bool = False,
        rollback_required: bool = False,
        rollback_available: bool = False,
        continuity_review_required: bool = False,
        verification_required: bool = True,
        degraded_mode: bool = False,
        failover_allowed: bool = True,
        requested_connector: Optional[str] = None,
        fallback_connectors: Optional[Sequence[str]] = None,
        lineage_event_ids: Optional[Sequence[str]] = None,
        evidence_event_ids: Optional[Sequence[str]] = None,
        control_ids: Optional[Sequence[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        constraints: Optional[Sequence[str]] = None,
    ) -> SovereignExecutionRouteRequest:
        """
        Convenience constructor.
        """

        return SovereignExecutionRouteRequest(
            route_request_id=str(uuid.uuid4()),
            source_engine=source_engine or "unknown_engine",
            action_type=self._safe_action_type(action_type),
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            mission_priority=max(0, int(mission_priority)),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            alignment_verdict_id=alignment_verdict_id,
            governance_approval_id=governance_approval_id,
            resilience_decision_id=resilience_decision_id,
            continuity_review_id=continuity_review_id,
            rollback_plan_id=rollback_plan_id,
            evidence_chain_id=evidence_chain_id,
            autonomy_mode=self._safe_autonomy_mode(autonomy_mode),
            blast_radius=self._safe_blast_radius(blast_radius),
            allowed=allowed,
            blocked=blocked,
            governance_required=governance_required,
            human_approval_required=human_approval_required,
            legal_approval_required=legal_approval_required,
            rollback_required=rollback_required,
            rollback_available=rollback_available,
            continuity_review_required=continuity_review_required,
            verification_required=verification_required,
            degraded_mode=degraded_mode,
            failover_allowed=failover_allowed,
            requested_connector=self._safe_connector(
                requested_connector,
                allow_none=True,
            ),
            fallback_connectors=[
                self._safe_connector(item)
                for item in list(fallback_connectors or [])
            ],
            lineage_event_ids=list(lineage_event_ids or []),
            evidence_event_ids=list(evidence_event_ids or []),
            control_ids=[
                str(control_id or "").upper().strip()
                for control_id in list(control_ids or [])
            ],
            payload=dict(payload or {}),
            constraints=list(constraints or []),
        )

    def create_request_from_alignment_verdict(
        self,
        verdict: Any,
        *,
        payload: Optional[Dict[str, Any]] = None,
        requested_connector: Optional[str] = None,
        fallback_connectors: Optional[Sequence[str]] = None,
    ) -> SovereignExecutionRouteRequest:
        """
        Build a route request from a compatible alignment verdict object/dict.
        """

        get = verdict.get if isinstance(verdict, dict) else lambda k, d=None: getattr(verdict, k, d)

        return self.create_request(
            source_engine="sovereign_execution_alignment_engine",
            action_type=str(get("action_type", "UNKNOWN") or "UNKNOWN"),
            severity=str(get("severity", "INFO") or "INFO"),
            confidence=float(get("confidence", 0.0) or 0.0),
            mission_priority=int(get("mission_priority", 0) or 0),
            summary=str(get("rationale", "") or ""),
            tenant_id=get("tenant_id"),
            case_id=get("case_id"),
            correlation_id=get("correlation_id"),
            alignment_verdict_id=get("verdict_id"),
            autonomy_mode=str(get("autonomy_mode", AUTONOMY_SUPERVISED_AUTONOMY)),
            blast_radius=str(get("blast_radius", BLAST_RADIUS_LOW)),
            allowed=bool(get("allowed", False)),
            blocked=bool(get("blocked", False)),
            governance_required=bool(get("governance_required", False)),
            human_approval_required=bool(get("human_approval_required", False)),
            legal_approval_required=bool(get("legal_approval_required", False)),
            rollback_required=bool(get("rollback_plan_required", False)),
            rollback_available=False,
            continuity_review_required=bool(
                get("continuity_review_required", False)
            ),
            verification_required=bool(get("verification_required", True)),
            requested_connector=requested_connector,
            fallback_connectors=fallback_connectors or [],
            payload=payload or {"alignment_verdict": verdict},
            constraints=list(get("required_controls", []) or []),
        )

    def get_recent_packages(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignExecutionPackage]:
        """
        Return recent packages newest-first.
        """

        limit = max(1, int(limit))
        return list(reversed(self._packages[-limit:]))

    def snapshot(self) -> SovereignExecutionRouterSnapshot:
        """
        Return lightweight router snapshot.
        """

        last = self._packages[-1] if self._packages else None

        return SovereignExecutionRouterSnapshot(
            router_name=self.router_name,
            total_requests_seen=self._requests_seen,
            total_packages_created=len(self._packages),
            last_execution_package_id=(
                last.execution_package_id if last else None
            ),
            last_route_status=last.route_status if last else None,
            last_selected_connector=last.selected_connector if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # ROUTING LOGIC
    # --------------------------------------------------------

    def _determine_route_status(
        self,
        request: SovereignExecutionRouteRequest,
    ) -> str:
        if request.autonomy_mode == AUTONOMY_LOCKDOWN:
            return ROUTE_STATUS_BLOCKED

        if request.blocked:
            return ROUTE_STATUS_BLOCKED

        if not request.allowed:
            return ROUTE_STATUS_DEFERRED

        if request.continuity_review_required:
            return ROUTE_STATUS_REQUIRES_CONTINUITY_REVIEW

        if request.rollback_required and not request.rollback_available:
            return ROUTE_STATUS_REQUIRES_ROLLBACK_PLAN

        if request.legal_approval_required or request.human_approval_required:
            if not request.governance_approval_id:
                return ROUTE_STATUS_REQUIRES_APPROVAL

        if request.governance_required:
            if not request.governance_approval_id:
                return ROUTE_STATUS_REQUIRES_GOVERNANCE

        if request.degraded_mode:
            return ROUTE_STATUS_DEGRADED

        return ROUTE_STATUS_READY

    def _determine_route(
        self,
        request: SovereignExecutionRouteRequest,
        route_status: str,
    ) -> str:
        if route_status == ROUTE_STATUS_BLOCKED:
            return ExecutionRouteType.BLOCKED_REGISTER.value

        if route_status == ROUTE_STATUS_REQUIRES_APPROVAL:
            return ExecutionRouteType.APPROVAL_QUEUE.value

        if route_status == ROUTE_STATUS_REQUIRES_GOVERNANCE:
            return ExecutionRouteType.GOVERNANCE_QUEUE.value

        if route_status == ROUTE_STATUS_REQUIRES_ROLLBACK_PLAN:
            return ExecutionRouteType.ROLLBACK_ORCHESTRATION.value

        if route_status == ROUTE_STATUS_REQUIRES_CONTINUITY_REVIEW:
            return ExecutionRouteType.CONTINUITY_REVIEW.value

        if route_status == ROUTE_STATUS_DEFERRED:
            return ExecutionRouteType.DEFERRED_QUEUE.value

        if request.action_type in {
            ExecutionActionType.OBSERVE.value,
            ExecutionActionType.INVESTIGATE.value,
            ExecutionActionType.ENRICH.value,
            ExecutionActionType.NOTIFY.value,
            ExecutionActionType.ESCALATE.value,
        }:
            return ExecutionRouteType.CASE_ORCHESTRATION.value

        return ExecutionRouteType.CONNECTOR_FABRIC.value

    def _select_connector(
        self,
        request: SovereignExecutionRouteRequest,
        selected_route: str,
    ) -> str:
        if selected_route != ExecutionRouteType.CONNECTOR_FABRIC.value:
            return ExecutionConnectorTarget.NONE.value

        if request.requested_connector:
            return self._safe_connector(request.requested_connector)

        action = request.action_type

        if action in {
            ExecutionActionType.REVOKE_SESSION.value,
            ExecutionActionType.DISABLE_USER.value,
        }:
            return ExecutionConnectorTarget.MICROSOFT_GRAPH.value

        if action in {
            ExecutionActionType.QUARANTINE_EMAIL.value,
            ExecutionActionType.DELETE_EMAIL.value,
            ExecutionActionType.PURGE_MAILBOX.value,
        }:
            return ExecutionConnectorTarget.MICROSOFT_GRAPH.value

        if action == ExecutionActionType.ISOLATE_ENDPOINT.value:
            return ExecutionConnectorTarget.CROWDSTRIKE.value

        if action == ExecutionActionType.BLOCK_NETWORK_TRAFFIC.value:
            return ExecutionConnectorTarget.AWS.value

        if action == ExecutionActionType.ROLLBACK.value:
            return ExecutionConnectorTarget.GENERIC_CONNECTOR.value

        return ExecutionConnectorTarget.GENERIC_CONNECTOR.value

    # --------------------------------------------------------
    # METADATA PACKAGING
    # --------------------------------------------------------

    @staticmethod
    def _governance_metadata(
        request: SovereignExecutionRouteRequest,
    ) -> Dict[str, Any]:
        return {
            "governance_required": request.governance_required,
            "human_approval_required": request.human_approval_required,
            "legal_approval_required": request.legal_approval_required,
            "governance_approval_id": request.governance_approval_id,
            "alignment_verdict_id": request.alignment_verdict_id,
            "autonomy_mode": request.autonomy_mode,
        }

    @staticmethod
    def _safety_metadata(
        request: SovereignExecutionRouteRequest,
        route_status: str,
    ) -> Dict[str, Any]:
        return {
            "route_status": route_status,
            "blocked": request.blocked,
            "allowed": request.allowed,
            "blast_radius": request.blast_radius,
            "degraded_mode": request.degraded_mode,
            "failover_allowed": request.failover_allowed,
            "resilience_decision_id": request.resilience_decision_id,
            "constraints": list(request.constraints),
        }

    @staticmethod
    def _rollback_metadata(
        request: SovereignExecutionRouteRequest,
    ) -> Dict[str, Any]:
        return {
            "rollback_required": request.rollback_required,
            "rollback_available": request.rollback_available,
            "rollback_plan_id": request.rollback_plan_id,
        }

    @staticmethod
    def _verification_metadata(
        request: SovereignExecutionRouteRequest,
    ) -> Dict[str, Any]:
        return {
            "verification_required": request.verification_required,
            "continuity_review_required": request.continuity_review_required,
            "continuity_review_id": request.continuity_review_id,
        }

    @staticmethod
    def _lineage_metadata(
        request: SovereignExecutionRouteRequest,
    ) -> Dict[str, Any]:
        return {
            "lineage_event_ids": list(request.lineage_event_ids),
            "correlation_id": request.correlation_id,
            "source_engine": request.source_engine,
        }

    @staticmethod
    def _compliance_metadata(
        request: SovereignExecutionRouteRequest,
    ) -> Dict[str, Any]:
        return {
            "evidence_event_ids": list(request.evidence_event_ids),
            "evidence_chain_id": request.evidence_chain_id,
            "control_ids": list(request.control_ids),
        }

    # --------------------------------------------------------
    # RECOMMENDATIONS / RATIONALE
    # --------------------------------------------------------

    def _recommended_next_steps(
        self,
        request: SovereignExecutionRouteRequest,
        route_status: str,
        selected_route: str,
        selected_connector: str,
    ) -> List[Dict[str, Any]]:
        steps: List[Dict[str, Any]] = []

        if route_status == ROUTE_STATUS_BLOCKED:
            steps.append(
                {
                    "step": "do_not_execute",
                    "reason": "Execution routing is blocked.",
                }
            )

        elif route_status == ROUTE_STATUS_REQUIRES_APPROVAL:
            steps.append(
                {
                    "step": "create_or_wait_for_approval",
                    "reason": "Human/legal approval is required.",
                }
            )

        elif route_status == ROUTE_STATUS_REQUIRES_GOVERNANCE:
            steps.append(
                {
                    "step": "route_to_governance_queue",
                    "reason": "Governance approval is required.",
                }
            )

        elif route_status == ROUTE_STATUS_REQUIRES_ROLLBACK_PLAN:
            steps.append(
                {
                    "step": "attach_rollback_plan",
                    "reason": "Rollback is required before execution handoff.",
                }
            )

        elif route_status == ROUTE_STATUS_REQUIRES_CONTINUITY_REVIEW:
            steps.append(
                {
                    "step": "perform_continuity_review",
                    "reason": "Continuity review is required.",
                }
            )

        elif route_status == ROUTE_STATUS_DEFERRED:
            steps.append(
                {
                    "step": "defer_execution",
                    "reason": "Execution request is not currently allowed.",
                }
            )

        elif route_status in {ROUTE_STATUS_READY, ROUTE_STATUS_DEGRADED}:
            steps.append(
                {
                    "step": "handoff_to_selected_route",
                    "route": selected_route,
                    "connector": selected_connector,
                }
            )

        if request.verification_required:
            steps.append(
                {
                    "step": "attach_verification_requirement",
                    "reason": "Post-execution verification is required.",
                }
            )

        steps.append(
            {
                "step": "record_execution_routing_lineage",
                "reason": "Routing decision must be replayable.",
            }
        )

        steps.append(
            {
                "step": "record_compliance_evidence",
                "reason": "Routing decision contributes to audit evidence.",
            }
        )

        return steps

    def _build_rationale(
        self,
        request: SovereignExecutionRouteRequest,
        route_status: str,
        selected_route: str,
        selected_connector: str,
    ) -> str:
        return (
            f"Execution route request from {request.source_engine} for action "
            f"{request.action_type} evaluated under autonomy mode "
            f"{request.autonomy_mode}. Route status {route_status}; selected "
            f"route {selected_route}; selected connector {selected_connector}. "
            f"Blast radius {request.blast_radius}; severity {request.severity}; "
            f"confidence {request.confidence:.2f}."
        )

    # --------------------------------------------------------
    # RECORDING / HANDOFF
    # --------------------------------------------------------

    def _record_package(
        self,
        package: SovereignExecutionPackage,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._packages.append(package)

        self._write_to_operational_memory(package, context=context)
        self._write_to_lineage(package, context=context)
        self._write_to_fedramp_evidence(package, context=context)
        self._emit_event(package, context=context)

    def _optional_connector_fabric_handoff(
        self,
        package: SovereignExecutionPackage,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Optional handoff to connector execution fabric.

        Still not direct connector execution from this router.
        """

        if not self.auto_handoff_to_connector_fabric:
            return

        if self.connector_execution_fabric is None:
            return

        if package.selected_route != ExecutionRouteType.CONNECTOR_FABRIC.value:
            return

        if package.route_status not in {
            ROUTE_STATUS_READY,
            ROUTE_STATUS_DEGRADED,
        }:
            return

        try:
            if hasattr(self.connector_execution_fabric, "submit"):
                self.connector_execution_fabric.submit(
                    package,
                    context=context or {},
                )
            elif hasattr(self.connector_execution_fabric, "route"):
                self.connector_execution_fabric.route(
                    package,
                    context=context or {},
                )
            elif hasattr(self.connector_execution_fabric, "execute"):
                self.connector_execution_fabric.execute(
                    package,
                    context=context or {},
                )
        except Exception as exc:
            print(
                "⚠️ Sovereign execution router connector-fabric "
                f"handoff failed: {exc}"
            )

    def _write_to_operational_memory(
        self,
        package: SovereignExecutionPackage,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "SOVEREIGN_EXECUTION_PACKAGE",
            "execution_package": self._package_to_dict(package),
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
            print(f"⚠️ Sovereign execution router memory write failed: {exc}")

    def _write_to_lineage(
        self,
        package: SovereignExecutionPackage,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "EXECUTION",
            "lineage_status": "RECORDED",
            "source_engine": self.router_name,
            "summary": package.rationale,
            "severity": package.severity,
            "confidence": package.confidence,
            "mission_priority": package.mission_priority,
            "tenant_id": package.tenant_id,
            "case_id": package.case_id,
            "correlation_id": package.correlation_id,
            "parent_event_ids": list(
                package.lineage_metadata.get("lineage_event_ids", [])
            ),
            "constraints": list(package.constraints),
            "verification_requirements": [
                "post_execution_verification"
                if package.verification_metadata.get("verification_required")
                else "verification_not_required"
            ],
            "context": {
                "type": "SOVEREIGN_EXECUTION_PACKAGE",
                "execution_package": self._package_to_dict(package),
                "context": context or {},
            },
            "metadata": {
                "execution_package_id": package.execution_package_id,
                "route_status": package.route_status,
                "selected_route": package.selected_route,
                "selected_connector": package.selected_connector,
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
            print(f"⚠️ Sovereign execution router lineage write failed: {exc}")

    def _write_to_fedramp_evidence(
        self,
        package: SovereignExecutionPackage,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        evidence = self.fedramp_evidence_lineage_engine
        if evidence is None:
            return

        payload = {
            "evidence_type": "DECISION_ROUTE_PLAN",
            "evidence_status": "RECORDED",
            "source_engine": self.router_name,
            "summary": package.rationale,
            "severity": package.severity,
            "confidence": package.confidence,
            "mission_priority": package.mission_priority,
            "tenant_id": package.tenant_id,
            "case_id": package.case_id,
            "correlation_id": package.correlation_id,
            "lineage_event_ids": list(
                package.lineage_metadata.get("lineage_event_ids", [])
            ),
            "parent_evidence_event_ids": list(
                package.compliance_metadata.get("evidence_event_ids", [])
            ),
            "related_control_ids": list(
                package.compliance_metadata.get("control_ids", [])
            ),
            "constraints": list(package.constraints),
            "evidence_payload": {
                "type": "SOVEREIGN_EXECUTION_PACKAGE",
                "execution_package": self._package_to_dict(package),
                "context": context or {},
            },
            "metadata": {
                "execution_package_id": package.execution_package_id,
                "route_status": package.route_status,
                "selected_route": package.selected_route,
                "selected_connector": package.selected_connector,
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
            print(f"⚠️ Sovereign execution router evidence write failed: {exc}")

    def _emit_event(
        self,
        package: SovereignExecutionPackage,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGN_EXECUTION_PACKAGE_CREATED",
            "router_name": self.router_name,
            "execution_package": self._package_to_dict(package),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_EXECUTION_PACKAGE_CREATED",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "SOVEREIGN_EXECUTION_PACKAGE_CREATED",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Sovereign execution router event emit failed: {exc}")

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_request(
        self,
        request: SovereignExecutionRouteRequest | Dict[str, Any],
    ) -> SovereignExecutionRouteRequest:
        if isinstance(request, SovereignExecutionRouteRequest):
            return request

        return SovereignExecutionRouteRequest(
            route_request_id=str(request.get("route_request_id") or uuid.uuid4()),
            source_engine=str(request.get("source_engine") or "unknown_engine"),
            action_type=self._safe_action_type(request.get("action_type")),
            severity=self._safe_severity(request.get("severity")),
            confidence=self._clamp_confidence(request.get("confidence", 0.0)),
            mission_priority=max(
                0,
                int(request.get("mission_priority", 0) or 0),
            ),
            summary=str(request.get("summary") or ""),
            tenant_id=request.get("tenant_id"),
            case_id=request.get("case_id"),
            correlation_id=request.get("correlation_id"),
            alignment_verdict_id=request.get("alignment_verdict_id"),
            governance_approval_id=request.get("governance_approval_id"),
            resilience_decision_id=request.get("resilience_decision_id"),
            continuity_review_id=request.get("continuity_review_id"),
            rollback_plan_id=request.get("rollback_plan_id"),
            evidence_chain_id=request.get("evidence_chain_id"),
            autonomy_mode=self._safe_autonomy_mode(
                request.get("autonomy_mode")
            ),
            blast_radius=self._safe_blast_radius(
                request.get("blast_radius")
            ),
            allowed=bool(request.get("allowed", False)),
            blocked=bool(request.get("blocked", False)),
            governance_required=bool(request.get("governance_required", False)),
            human_approval_required=bool(
                request.get("human_approval_required", False)
            ),
            legal_approval_required=bool(
                request.get("legal_approval_required", False)
            ),
            rollback_required=bool(request.get("rollback_required", False)),
            rollback_available=bool(request.get("rollback_available", False)),
            continuity_review_required=bool(
                request.get("continuity_review_required", False)
            ),
            verification_required=bool(
                request.get("verification_required", True)
            ),
            degraded_mode=bool(request.get("degraded_mode", False)),
            failover_allowed=bool(request.get("failover_allowed", True)),
            requested_connector=self._safe_connector(
                request.get("requested_connector"),
                allow_none=True,
            ),
            fallback_connectors=[
                self._safe_connector(item)
                for item in list(request.get("fallback_connectors", []) or [])
            ],
            lineage_event_ids=list(request.get("lineage_event_ids", []) or []),
            evidence_event_ids=list(request.get("evidence_event_ids", []) or []),
            control_ids=[
                str(control_id or "").upper().strip()
                for control_id in list(request.get("control_ids", []) or [])
            ],
            payload=dict(request.get("payload", {}) or {}),
            constraints=list(request.get("constraints", []) or []),
        )

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    @staticmethod
    def _package_to_dict(
        package: SovereignExecutionPackage,
    ) -> Dict[str, Any]:
        return asdict(package)

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_action_type(value: Any) -> str:
        value = str(value or ExecutionActionType.UNKNOWN.value).upper()
        valid = {item.value for item in ExecutionActionType}
        return value if value in valid else ExecutionActionType.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or RouteSeverity.INFO.value).upper()
        valid = {item.value for item in RouteSeverity}
        return value if value in valid else RouteSeverity.INFO.value

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
    def _safe_connector(
        value: Any,
        *,
        allow_none: bool = False,
    ) -> Optional[str] | str:
        if value is None and allow_none:
            return None

        value = str(value or ExecutionConnectorTarget.GENERIC_CONNECTOR.value).upper()
        valid = {item.value for item in ExecutionConnectorTarget}

        return value if value in valid else ExecutionConnectorTarget.GENERIC_CONNECTOR.value

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_execution_router(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
    connector_execution_fabric: Optional[Any] = None,
    auto_handoff_to_connector_fabric: bool = False,
) -> SovereignExecutionRouter:
    """
    Factory for explicit dependency injection.
    """

    return SovereignExecutionRouter(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
        connector_execution_fabric=connector_execution_fabric,
        auto_handoff_to_connector_fabric=auto_handoff_to_connector_fabric,
    )