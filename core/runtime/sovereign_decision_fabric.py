"""
core/runtime/sovereign_decision_fabric.py

Sovereign Decision Fabric

The sovereign decision fabric is the governed routing layer between:

    cognition / coordination / continuity / memory
        ↓
    decision normalization + prioritization + governance gating
        ↓
    execution alignment / execution router / connector fabric

IMPORTANT:
This fabric does NOT execute connector actions.
It does NOT isolate endpoints, quarantine mailboxes, revoke sessions,
delete data, or mutate external systems.

It only:
- accepts sovereign decision inputs
- normalizes them
- prioritizes them
- gates them
- routes them
- emits deterministic handoff plans
- records audit-ready routing lineage
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

SEVERITY_INFO = "INFO"
SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

STATUS_ACCEPTED = "ACCEPTED"
STATUS_DEFERRED = "DEFERRED"
STATUS_BLOCKED = "BLOCKED"
STATUS_REQUIRES_GOVERNANCE = "REQUIRES_GOVERNANCE"
STATUS_REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"
STATUS_READY_FOR_EXECUTION_ALIGNMENT = "READY_FOR_EXECUTION_ALIGNMENT"

DEFAULT_FABRIC_NAME = "sovereign_decision_fabric"


class DecisionSource(str, Enum):
    COGNITION = "COGNITION"
    COORDINATION = "COORDINATION"
    CONTINUITY = "CONTINUITY"
    GOVERNANCE = "GOVERNANCE"
    MEMORY = "MEMORY"
    CASE = "CASE"
    COMPLIANCE = "COMPLIANCE"
    SECURITY = "SECURITY"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


class DecisionIntent(str, Enum):
    OBSERVE = "OBSERVE"
    RECOMMEND = "RECOMMEND"
    PRIORITIZE = "PRIORITIZE"
    ALIGN = "ALIGN"
    ESCALATE = "ESCALATE"
    CONTAIN = "CONTAIN"
    INVESTIGATE = "INVESTIGATE"
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    BLOCK = "BLOCK"
    RECORD = "RECORD"
    EXECUTION_HANDOFF = "EXECUTION_HANDOFF"


class DecisionRoute(str, Enum):
    GOVERNANCE_REVIEW = "GOVERNANCE_REVIEW"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    EXECUTION_ALIGNMENT = "EXECUTION_ALIGNMENT"
    OPERATIONAL_MEMORY = "OPERATIONAL_MEMORY"
    CASE_ORCHESTRATION = "CASE_ORCHESTRATION"
    COMPLIANCE_LINEAGE = "COMPLIANCE_LINEAGE"
    BLOCKED = "BLOCKED"
    OBSERVABILITY = "OBSERVABILITY"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class SovereignDecisionInput:
    """
    Normalized decision input entering the fabric.
    """

    decision_input_id: str
    source: str
    source_engine: str
    intent: str
    severity: str
    confidence: float
    mission_priority: int
    summary: str
    payload: Dict[str, Any] = field(default_factory=dict)

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    requires_governance: bool = False
    requires_human_approval: bool = False
    requires_execution_alignment: bool = True
    allow_autonomous_handoff: bool = False

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignDecisionRoutePlan:
    """
    Fabric-generated routing plan.

    This is a handoff plan, not an execution result.
    """

    route_plan_id: str
    status: str
    selected_input_id: Optional[str]
    selected_source: Optional[str]
    selected_source_engine: Optional[str]
    selected_intent: Optional[str]
    severity: str
    confidence: float
    mission_priority: int
    routes: List[str]
    handoff_targets: List[str]
    recommended_actions: List[Dict[str, Any]]
    blocked_reason: Optional[str]
    governance_required: bool
    human_approval_required: bool
    execution_alignment_required: bool
    rationale: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    suppressed_input_ids: List[str] = field(default_factory=list)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignDecisionFabricSnapshot:
    """
    Runtime snapshot for UI/diagnostics.
    """

    fabric_name: str
    total_inputs_seen: int
    total_route_plans_created: int
    last_route_plan_id: Optional[str]
    last_status: Optional[str]
    last_severity: Optional[str]
    last_updated_ms: int


# ============================================================
# FABRIC
# ============================================================

class SovereignDecisionFabric:
    """
    Deterministic sovereign routing layer.

    Design guarantees:
    - no connector execution
    - no Streamlit/session dependency
    - no implicit global state
    - explicit dependency injection
    - append-only route plan history
    """

    def __init__(
        self,
        *,
        fabric_name: str = DEFAULT_FABRIC_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        governance_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        execution_alignment_engine: Optional[Any] = None,
    ) -> None:
        self.fabric_name = fabric_name
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.governance_engine = governance_engine
        self.lineage_engine = lineage_engine
        self.execution_alignment_engine = execution_alignment_engine

        self._inputs_seen = 0
        self._route_plans: List[SovereignDecisionRoutePlan] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def submit(
        self,
        inputs: Sequence[SovereignDecisionInput | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignDecisionRoutePlan:
        """
        Submit one or more decisions into the fabric.

        Returns a deterministic route plan.
        """

        normalized = [
            self._normalize_input(
                item,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in inputs
        ]

        self._inputs_seen += len(normalized)

        if not normalized:
            plan = self._empty_route_plan(
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_route_plan(plan, context=context)
            return plan

        selected = self._select_highest_priority_input(normalized)
        suppressed = [
            item.decision_input_id
            for item in normalized
            if item.decision_input_id != selected.decision_input_id
        ]

        status = self._determine_status(selected)
        routes = self._determine_routes(selected, status)
        handoff_targets = self._determine_handoff_targets(routes)

        plan = SovereignDecisionRoutePlan(
            route_plan_id=str(uuid.uuid4()),
            status=status,
            selected_input_id=selected.decision_input_id,
            selected_source=selected.source,
            selected_source_engine=selected.source_engine,
            selected_intent=selected.intent,
            severity=selected.severity,
            confidence=selected.confidence,
            mission_priority=selected.mission_priority,
            routes=routes,
            handoff_targets=handoff_targets,
            recommended_actions=self._build_recommended_actions(
                selected,
                status,
                routes,
            ),
            blocked_reason=self._blocked_reason(selected, status),
            governance_required=selected.requires_governance,
            human_approval_required=selected.requires_human_approval,
            execution_alignment_required=(
                selected.requires_execution_alignment
            ),
            rationale=self._build_rationale(
                selected=selected,
                inputs=normalized,
                status=status,
                routes=routes,
            ),
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            suppressed_input_ids=suppressed,
        )

        self._record_route_plan(plan, context=context)
        return plan

    def create_input(
        self,
        *,
        source: str,
        source_engine: str,
        intent: str,
        severity: str,
        confidence: float,
        mission_priority: int,
        summary: str,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        requires_governance: bool = False,
        requires_human_approval: bool = False,
        requires_execution_alignment: bool = True,
        allow_autonomous_handoff: bool = False,
    ) -> SovereignDecisionInput:
        """
        Convenience constructor for normalized fabric input.
        """

        return SovereignDecisionInput(
            decision_input_id=str(uuid.uuid4()),
            source=self._safe_source(source),
            source_engine=source_engine or "unknown_engine",
            intent=self._safe_intent(intent),
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            mission_priority=max(0, int(mission_priority)),
            summary=summary or "",
            payload=payload or {},
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            requires_governance=requires_governance,
            requires_human_approval=requires_human_approval,
            requires_execution_alignment=requires_execution_alignment,
            allow_autonomous_handoff=allow_autonomous_handoff,
        )

    def get_recent_route_plans(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignDecisionRoutePlan]:
        """
        Return recent route plans newest-first.
        """

        limit = max(1, int(limit))
        return list(reversed(self._route_plans[-limit:]))

    def snapshot(self) -> SovereignDecisionFabricSnapshot:
        """
        Return current fabric status.
        """

        last = self._route_plans[-1] if self._route_plans else None

        return SovereignDecisionFabricSnapshot(
            fabric_name=self.fabric_name,
            total_inputs_seen=self._inputs_seen,
            total_route_plans_created=len(self._route_plans),
            last_route_plan_id=last.route_plan_id if last else None,
            last_status=last.status if last else None,
            last_severity=last.severity if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # ROUTING LOGIC
    # --------------------------------------------------------

    def _select_highest_priority_input(
        self,
        inputs: Sequence[SovereignDecisionInput],
    ) -> SovereignDecisionInput:
        """
        Deterministic decision ranking.

        Priority:
        1. severity
        2. mission priority
        3. governance sensitivity
        4. human approval sensitivity
        5. confidence
        6. oldest first for stable arbitration
        """

        return sorted(
            inputs,
            key=lambda item: (
                self._severity_weight(item.severity),
                item.mission_priority,
                1 if item.requires_governance else 0,
                1 if item.requires_human_approval else 0,
                item.confidence,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _determine_status(
        self,
        selected: SovereignDecisionInput,
    ) -> str:
        """
        Determine route plan status.
        """

        if selected.intent == DecisionIntent.BLOCK.value:
            return STATUS_BLOCKED

        if selected.requires_human_approval:
            return STATUS_REQUIRES_HUMAN_APPROVAL

        if selected.requires_governance:
            return STATUS_REQUIRES_GOVERNANCE

        if selected.requires_execution_alignment:
            return STATUS_READY_FOR_EXECUTION_ALIGNMENT

        return STATUS_ACCEPTED

    def _determine_routes(
        self,
        selected: SovereignDecisionInput,
        status: str,
    ) -> List[str]:
        """
        Determine logical routes for the selected decision.
        """

        routes: List[str] = []

        if status == STATUS_BLOCKED:
            routes.append(DecisionRoute.BLOCKED.value)
            routes.append(DecisionRoute.OPERATIONAL_MEMORY.value)
            routes.append(DecisionRoute.COMPLIANCE_LINEAGE.value)
            return routes

        if status == STATUS_REQUIRES_HUMAN_APPROVAL:
            routes.append(DecisionRoute.HUMAN_APPROVAL.value)
            routes.append(DecisionRoute.OPERATIONAL_MEMORY.value)
            routes.append(DecisionRoute.COMPLIANCE_LINEAGE.value)
            return routes

        if status == STATUS_REQUIRES_GOVERNANCE:
            routes.append(DecisionRoute.GOVERNANCE_REVIEW.value)
            routes.append(DecisionRoute.OPERATIONAL_MEMORY.value)
            routes.append(DecisionRoute.COMPLIANCE_LINEAGE.value)
            return routes

        if status == STATUS_READY_FOR_EXECUTION_ALIGNMENT:
            routes.append(DecisionRoute.EXECUTION_ALIGNMENT.value)
            routes.append(DecisionRoute.OPERATIONAL_MEMORY.value)
            routes.append(DecisionRoute.COMPLIANCE_LINEAGE.value)

            if selected.case_id:
                routes.append(DecisionRoute.CASE_ORCHESTRATION.value)

            return routes

        routes.append(DecisionRoute.OBSERVABILITY.value)
        routes.append(DecisionRoute.OPERATIONAL_MEMORY.value)
        return routes

    def _determine_handoff_targets(
        self,
        routes: Sequence[str],
    ) -> List[str]:
        """
        Convert abstract routes into handoff targets.
        """

        targets: List[str] = []

        mapping = {
            DecisionRoute.GOVERNANCE_REVIEW.value: "governance_engine",
            DecisionRoute.HUMAN_APPROVAL.value: "approval_queue",
            DecisionRoute.EXECUTION_ALIGNMENT.value: (
                "sovereign_execution_alignment_engine"
            ),
            DecisionRoute.OPERATIONAL_MEMORY.value: (
                "sovereign_operational_memory_engine"
            ),
            DecisionRoute.CASE_ORCHESTRATION.value: (
                "autonomous_case_orchestrator"
            ),
            DecisionRoute.COMPLIANCE_LINEAGE.value: (
                "sovereign_operational_lineage_engine"
            ),
            DecisionRoute.BLOCKED.value: "blocked_decision_register",
            DecisionRoute.OBSERVABILITY.value: "runtime_observability",
        }

        for route in routes:
            target = mapping.get(route)
            if target and target not in targets:
                targets.append(target)

        return targets

    # --------------------------------------------------------
    # RECORDING / EVENTS / HANDOFF HOOKS
    # --------------------------------------------------------

    def _record_route_plan(
        self,
        plan: SovereignDecisionRoutePlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Append route plan and notify external observers when available.
        """

        self._route_plans.append(plan)

        self._write_to_operational_memory(plan, context=context)
        self._write_to_lineage(plan, context=context)
        self._emit_event(plan, context=context)
        self._optional_execution_alignment_handoff(plan, context=context)

    def _write_to_operational_memory(
        self,
        plan: SovereignDecisionRoutePlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "SOVEREIGN_DECISION_ROUTE_PLAN",
            "route_plan": self._route_plan_to_dict(plan),
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
            print(f"⚠️ Decision fabric memory write failed: {exc}")

    def _write_to_lineage(
        self,
        plan: SovereignDecisionRoutePlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "type": "SOVEREIGN_DECISION_FABRIC_ROUTE",
            "route_plan": self._route_plan_to_dict(plan),
            "context": context or {},
        }

        try:
            if hasattr(lineage, "record_lineage"):
                lineage.record_lineage(payload)
            elif hasattr(lineage, "append_lineage"):
                lineage.append_lineage(payload)
            elif hasattr(lineage, "record"):
                lineage.record(payload)
        except Exception as exc:
            print(f"⚠️ Decision fabric lineage write failed: {exc}")

    def _emit_event(
        self,
        plan: SovereignDecisionRoutePlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGN_DECISION_ROUTE_PLAN_CREATED",
            "fabric": self.fabric_name,
            "route_plan": self._route_plan_to_dict(plan),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_DECISION_ROUTE_PLAN_CREATED",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "SOVEREIGN_DECISION_ROUTE_PLAN_CREATED",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Decision fabric event emit failed: {exc}")

    def _optional_execution_alignment_handoff(
        self,
        plan: SovereignDecisionRoutePlan,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Optional handoff to execution alignment engine.

        This is NOT connector execution.
        It only passes the route plan to the next policy/alignment layer.
        """

        if self.execution_alignment_engine is None:
            return

        if (
            DecisionRoute.EXECUTION_ALIGNMENT.value
            not in plan.routes
        ):
            return

        try:
            if hasattr(self.execution_alignment_engine, "align_route_plan"):
                self.execution_alignment_engine.align_route_plan(
                    plan,
                    context=context or {},
                )
            elif hasattr(self.execution_alignment_engine, "submit"):
                self.execution_alignment_engine.submit(
                    plan,
                    context=context or {},
                )
        except Exception as exc:
            print(
                "⚠️ Decision fabric execution-alignment handoff "
                f"failed: {exc}"
            )

    # --------------------------------------------------------
    # RECOMMENDATIONS / RATIONALE
    # --------------------------------------------------------

    def _build_recommended_actions(
        self,
        selected: SovereignDecisionInput,
        status: str,
        routes: Sequence[str],
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        if status == STATUS_BLOCKED:
            actions.append(
                {
                    "action": "register_blocked_decision",
                    "reason": "Decision intent requested BLOCK.",
                    "source_engine": selected.source_engine,
                }
            )
            return actions

        if status == STATUS_REQUIRES_HUMAN_APPROVAL:
            actions.append(
                {
                    "action": "create_human_approval_request",
                    "source_engine": selected.source_engine,
                    "intent": selected.intent,
                    "summary": selected.summary,
                }
            )

        if status == STATUS_REQUIRES_GOVERNANCE:
            actions.append(
                {
                    "action": "route_to_governance_review",
                    "source_engine": selected.source_engine,
                    "intent": selected.intent,
                    "summary": selected.summary,
                }
            )

        if status == STATUS_READY_FOR_EXECUTION_ALIGNMENT:
            actions.append(
                {
                    "action": "submit_to_execution_alignment",
                    "source_engine": selected.source_engine,
                    "intent": selected.intent,
                    "summary": selected.summary,
                }
            )

        if DecisionRoute.OPERATIONAL_MEMORY.value in routes:
            actions.append(
                {
                    "action": "append_to_operational_memory",
                    "reason": "Decision route plan must remain replayable.",
                }
            )

        if DecisionRoute.COMPLIANCE_LINEAGE.value in routes:
            actions.append(
                {
                    "action": "record_compliance_lineage",
                    "reason": (
                        "Decision route contributes to audit and "
                        "FedRAMP/CMMC evidence lineage."
                    ),
                }
            )

        return actions

    def _blocked_reason(
        self,
        selected: SovereignDecisionInput,
        status: str,
    ) -> Optional[str]:
        if status != STATUS_BLOCKED:
            return None

        return (
            f"Selected decision input {selected.decision_input_id} "
            "was blocked by fabric routing policy."
        )

    def _build_rationale(
        self,
        *,
        selected: SovereignDecisionInput,
        inputs: Sequence[SovereignDecisionInput],
        status: str,
        routes: Sequence[str],
    ) -> str:
        return (
            f"Selected decision input from {selected.source_engine} "
            f"with source {selected.source}, intent {selected.intent}, "
            f"severity {selected.severity}, mission priority "
            f"{selected.mission_priority}, and confidence "
            f"{selected.confidence:.2f}. Status: {status}. "
            f"Routes: {', '.join(routes)}. "
            f"Arbitrated across {len(inputs)} input(s)."
        )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_input(
        self,
        item: SovereignDecisionInput | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignDecisionInput:
        if isinstance(item, SovereignDecisionInput):
            return item

        return SovereignDecisionInput(
            decision_input_id=str(
                item.get("decision_input_id") or uuid.uuid4()
            ),
            source=self._safe_source(item.get("source")),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            intent=self._safe_intent(item.get("intent")),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_confidence(item.get("confidence", 0.0)),
            mission_priority=max(
                0,
                int(item.get("mission_priority", 0) or 0),
            ),
            summary=str(item.get("summary") or ""),
            payload=dict(item.get("payload") or {}),
            tenant_id=tenant_id or item.get("tenant_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            requires_governance=bool(
                item.get("requires_governance", False)
            ),
            requires_human_approval=bool(
                item.get("requires_human_approval", False)
            ),
            requires_execution_alignment=bool(
                item.get("requires_execution_alignment", True)
            ),
            allow_autonomous_handoff=bool(
                item.get("allow_autonomous_handoff", False)
            ),
        )

    def _empty_route_plan(
        self,
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignDecisionRoutePlan:
        return SovereignDecisionRoutePlan(
            route_plan_id=str(uuid.uuid4()),
            status=STATUS_DEFERRED,
            selected_input_id=None,
            selected_source=None,
            selected_source_engine=None,
            selected_intent=None,
            severity=SEVERITY_INFO,
            confidence=0.0,
            mission_priority=0,
            routes=[DecisionRoute.OBSERVABILITY.value],
            handoff_targets=["runtime_observability"],
            recommended_actions=[],
            blocked_reason=None,
            governance_required=False,
            human_approval_required=False,
            execution_alignment_required=False,
            rationale="No sovereign decision inputs were submitted.",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            suppressed_input_ids=[],
        )

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    @staticmethod
    def _route_plan_to_dict(
        plan: SovereignDecisionRoutePlan,
    ) -> Dict[str, Any]:
        return {
            "route_plan_id": plan.route_plan_id,
            "status": plan.status,
            "selected_input_id": plan.selected_input_id,
            "selected_source": plan.selected_source,
            "selected_source_engine": plan.selected_source_engine,
            "selected_intent": plan.selected_intent,
            "severity": plan.severity,
            "confidence": plan.confidence,
            "mission_priority": plan.mission_priority,
            "routes": list(plan.routes),
            "handoff_targets": list(plan.handoff_targets),
            "recommended_actions": list(plan.recommended_actions),
            "blocked_reason": plan.blocked_reason,
            "governance_required": plan.governance_required,
            "human_approval_required": plan.human_approval_required,
            "execution_alignment_required": (
                plan.execution_alignment_required
            ),
            "rationale": plan.rationale,
            "tenant_id": plan.tenant_id,
            "case_id": plan.case_id,
            "correlation_id": plan.correlation_id,
            "suppressed_input_ids": list(plan.suppressed_input_ids),
            "created_at_ms": plan.created_at_ms,
        }

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_source(value: Any) -> str:
        value = str(value or DecisionSource.UNKNOWN.value).upper()
        valid = {item.value for item in DecisionSource}
        return value if value in valid else DecisionSource.UNKNOWN.value

    @staticmethod
    def _safe_intent(value: Any) -> str:
        value = str(value or DecisionIntent.OBSERVE.value).upper()
        valid = {item.value for item in DecisionIntent}
        return value if value in valid else DecisionIntent.OBSERVE.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or SEVERITY_INFO).upper()
        valid = {
            SEVERITY_INFO,
            SEVERITY_LOW,
            SEVERITY_MEDIUM,
            SEVERITY_HIGH,
            SEVERITY_CRITICAL,
        }
        return value if value in valid else SEVERITY_INFO

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))

    @staticmethod
    def _severity_weight(severity: str) -> int:
        return {
            SEVERITY_INFO: 0,
            SEVERITY_LOW: 1,
            SEVERITY_MEDIUM: 2,
            SEVERITY_HIGH: 3,
            SEVERITY_CRITICAL: 4,
        }.get(str(severity).upper(), 0)


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_decision_fabric(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    execution_alignment_engine: Optional[Any] = None,
) -> SovereignDecisionFabric:
    """
    Factory for explicit dependency injection.
    """

    return SovereignDecisionFabric(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        governance_engine=governance_engine,
        lineage_engine=lineage_engine,
        execution_alignment_engine=execution_alignment_engine,
    )