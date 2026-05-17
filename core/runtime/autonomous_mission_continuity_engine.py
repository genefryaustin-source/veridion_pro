"""
core/runtime/autonomous_mission_continuity_engine.py

Autonomous Mission Continuity Engine.

Purpose:
- sovereign mission survivability orchestration
- runtime continuity stabilization
- continuity-aware autonomous orchestration
- strategic failover planning
- mission-priority runtime preservation
- sovereign continuity enforcement

Architecture Rules:
- no Streamlit/session_state
- explicit dependency injection
- event-driven orchestration
- deterministic continuity planning
- no hidden runtime state
"""

from __future__ import annotations

import time
import uuid

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


DEFAULT_TENANT = "default"

MISSION_STATUS_STABLE = "STABLE"
MISSION_STATUS_DEGRADED = "DEGRADED"
MISSION_STATUS_CRITICAL = "CRITICAL"
MISSION_STATUS_FAILING = "FAILING"

CONTINUITY_LOW = "LOW"
CONTINUITY_MEDIUM = "MEDIUM"
CONTINUITY_HIGH = "HIGH"
CONTINUITY_CRITICAL = "CRITICAL"

PLAN_PENDING = "PENDING"
PLAN_ACTIVE = "ACTIVE"
PLAN_COMPLETED = "COMPLETED"
PLAN_FAILED = "FAILED"

ACTION_RECOMMEND = "RECOMMEND"
ACTION_ESCALATE = "ESCALATE"
ACTION_RECOVER = "RECOVER"
ACTION_FAILOVER = "FAILOVER"
ACTION_ISOLATE = "ISOLATE"
ACTION_STABILIZE = "STABILIZE"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class MissionContinuityAction:

    action_id: str

    action_type: str

    priority: str

    description: str

    target: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MissionContinuityPlan:

    plan_id: str

    tenant_id: str

    mission_id: str

    mission_status: str

    continuity_risk: str

    continuity_score: float

    runtime_health: Dict[str, Any] = field(default_factory=dict)

    sovereignty_state: Dict[str, Any] = field(default_factory=dict)

    federation_state: Dict[str, Any] = field(default_factory=dict)

    recommendations: List[str] = field(default_factory=list)

    actions: List[MissionContinuityAction] = field(default_factory=list)

    status: str = PLAN_PENDING

    created_at_ms: int = field(default_factory=_now_ms)

    updated_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:

        data = asdict(self)

        data["actions"] = [
            a.to_dict()
            for a in self.actions
        ]

        return data


class AutonomousMissionContinuityEngine:

    """
    Strategic mission survivability engine.
    """

    def __init__(
        self,

        runtime_cognition_orchestrator: Optional[Any] = None,

        autonomous_runtime_intelligence_engine: Optional[Any] = None,

        runtime_recovery_manager: Optional[Any] = None,

        runtime_federation_manager: Optional[Any] = None,

        distributed_runtime_cluster_manager: Optional[Any] = None,

        federated_execution_router: Optional[Any] = None,

        sovereign_execution_controller: Optional[Any] = None,

        predictive_runtime_stability_engine: Optional[Any] = None,

        sovereign_operational_reasoning_engine: Optional[Any] = None,

        adaptive_operational_strategy_engine: Optional[Any] = None,

        autonomy_governor_v2: Optional[Any] = None,

        storage: Optional[Any] = None,

        event_bus: Optional[Any] = None,
    ):

        self.runtime_cognition_orchestrator = (
            runtime_cognition_orchestrator
        )

        self.autonomous_runtime_intelligence_engine = (
            autonomous_runtime_intelligence_engine
        )

        self.runtime_recovery_manager = (
            runtime_recovery_manager
        )

        self.runtime_federation_manager = (
            runtime_federation_manager
        )

        self.distributed_runtime_cluster_manager = (
            distributed_runtime_cluster_manager
        )

        self.federated_execution_router = (
            federated_execution_router
        )

        self.sovereign_execution_controller = (
            sovereign_execution_controller
        )

        self.predictive_runtime_stability_engine = (
            predictive_runtime_stability_engine
        )

        self.sovereign_operational_reasoning_engine = (
            sovereign_operational_reasoning_engine
        )

        self.adaptive_operational_strategy_engine = (
            adaptive_operational_strategy_engine
        )

        self.autonomy_governor_v2 = (
            autonomy_governor_v2
        )

        self.storage = storage

        self.event_bus = event_bus

        self.active_plans: Dict[
            str,
            MissionContinuityPlan
        ] = {}

        self.last_assessment_ms = 0

        self._register_handlers()

    # =====================================================
    # EVENT HANDLERS
    # =====================================================

    def _register_handlers(self) -> None:

        if self.event_bus is None:
            return

        events = [

            "RUNTIME_DEGRADED",

            "FEDERATION_LINK_LOST",

            "EXECUTION_TIMEOUT",

            "WORKER_STALLED",

            "ROLLBACK_TRIGGERED",

            "RECOVERY_TRIGGERED",

            "PREDICTIVE_STABILITY_WARNING",

            "TOPOLOGY_DEGRADATION_DETECTED",

            "SOVEREIGN_BOUNDARY_VIOLATION",

            "MISSION_CONTINUITY_RISK",
        ]

        for event_name in events:

            try:

                self.event_bus.subscribe(
                    event_name,
                    self._handle_runtime_event,
                )

            except Exception:
                pass

    # =====================================================
    # EVENT PROCESSING
    # =====================================================

    def _handle_runtime_event(
        self,
        event: Dict[str, Any],
    ) -> None:

        tenant_id = (
            event.get("tenant_id")
            or DEFAULT_TENANT
        )

        mission_id = (
            event.get("mission_id")
            or "runtime_fabric"
        )

        self.assess_mission_continuity(
            tenant_id=tenant_id,
            mission_id=mission_id,
            trigger_event=event,
        )

    # =====================================================
    # CONTINUITY ASSESSMENT
    # =====================================================

    def assess_mission_continuity(
        self,
        tenant_id: str,
        mission_id: str,
        trigger_event: Optional[
            Dict[str, Any]
        ] = None,
    ) -> MissionContinuityPlan:

        runtime_health = (
            self._collect_runtime_health(
                tenant_id
            )
        )

        sovereignty_state = (
            self._collect_sovereignty_state(
                tenant_id
            )
        )

        federation_state = (
            self._collect_federation_state(
                tenant_id
            )
        )

        continuity_score = (
            self._calculate_continuity_score(
                runtime_health=runtime_health,
                sovereignty_state=sovereignty_state,
                federation_state=federation_state,
            )
        )

        continuity_risk = (
            self._derive_continuity_risk(
                continuity_score
            )
        )

        mission_status = (
            self._derive_mission_status(
                continuity_risk
            )
        )

        plan = MissionContinuityPlan(

            plan_id=(
                f"MISSION-{uuid.uuid4().hex[:12].upper()}"
            ),

            tenant_id=tenant_id,

            mission_id=mission_id,

            mission_status=mission_status,

            continuity_risk=continuity_risk,

            continuity_score=continuity_score,

            runtime_health=runtime_health,

            sovereignty_state=sovereignty_state,

            federation_state=federation_state,
        )

        self._generate_recommendations(
            plan=plan,
            trigger_event=trigger_event,
        )

        self._generate_actions(
            plan=plan,
            trigger_event=trigger_event,
        )

        self.active_plans[
            plan.plan_id
        ] = plan

        self.last_assessment_ms = _now_ms()

        self._emit_plan(plan)

        return plan

    # =====================================================
    # COLLECTION
    # =====================================================

    def _collect_runtime_health(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:

        return {
            "runtime_health": "HEALTHY",
            "tenant_id": tenant_id,
            "timestamp_ms": _now_ms(),
        }

    def _collect_sovereignty_state(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:

        return {
            "sovereignty_state": "STABLE",
            "tenant_id": tenant_id,
        }

    def _collect_federation_state(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:

        return {
            "federation_state": "CONNECTED",
            "tenant_id": tenant_id,
        }

    # =====================================================
    # CONTINUITY MODELS
    # =====================================================

    def _calculate_continuity_score(
        self,
        runtime_health: Dict[str, Any],
        sovereignty_state: Dict[str, Any],
        federation_state: Dict[str, Any],
    ) -> float:

        score = 100.0

        if (
            runtime_health.get("runtime_health")
            != "HEALTHY"
        ):
            score -= 25.0

        if (
            sovereignty_state.get("sovereignty_state")
            != "STABLE"
        ):
            score -= 25.0

        if (
            federation_state.get("federation_state")
            != "CONNECTED"
        ):
            score -= 25.0

        return max(score, 0.0)

    def _derive_continuity_risk(
        self,
        continuity_score: float,
    ) -> str:

        if continuity_score >= 90:
            return CONTINUITY_LOW

        if continuity_score >= 70:
            return CONTINUITY_MEDIUM

        if continuity_score >= 40:
            return CONTINUITY_HIGH

        return CONTINUITY_CRITICAL

    def _derive_mission_status(
        self,
        continuity_risk: str,
    ) -> str:

        mapping = {

            CONTINUITY_LOW:
                MISSION_STATUS_STABLE,

            CONTINUITY_MEDIUM:
                MISSION_STATUS_DEGRADED,

            CONTINUITY_HIGH:
                MISSION_STATUS_CRITICAL,

            CONTINUITY_CRITICAL:
                MISSION_STATUS_FAILING,
        }

        return mapping.get(
            continuity_risk,
            MISSION_STATUS_DEGRADED,
        )

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    def _generate_recommendations(
        self,
        plan: MissionContinuityPlan,
        trigger_event: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if plan.continuity_risk == CONTINUITY_LOW:

            plan.recommendations.append(
                "Maintain current sovereign "
                "runtime posture."
            )

        elif plan.continuity_risk == CONTINUITY_MEDIUM:

            plan.recommendations.append(
                "Increase continuity observation "
                "and runtime monitoring."
            )

        elif plan.continuity_risk == CONTINUITY_HIGH:

            plan.recommendations.append(
                "Prepare strategic failover and "
                "runtime stabilization."
            )

        else:

            plan.recommendations.append(
                "Initiate mission survivability "
                "preservation protocols."
            )

    # =====================================================
    # ACTION GENERATION
    # =====================================================

    def _generate_actions(
        self,
        plan: MissionContinuityPlan,
        trigger_event: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if plan.continuity_risk == CONTINUITY_LOW:

            plan.actions.append(
                MissionContinuityAction(
                    action_id=(
                        f"ACTION-{uuid.uuid4().hex[:10]}"
                    ),
                    action_type=ACTION_RECOMMEND,
                    priority=CONTINUITY_LOW,
                    description=(
                        "Maintain runtime continuity "
                        "observation posture."
                    ),
                )
            )

        elif plan.continuity_risk == CONTINUITY_MEDIUM:

            plan.actions.append(
                MissionContinuityAction(
                    action_id=(
                        f"ACTION-{uuid.uuid4().hex[:10]}"
                    ),
                    action_type=ACTION_STABILIZE,
                    priority=CONTINUITY_MEDIUM,
                    description=(
                        "Increase runtime continuity "
                        "stabilization posture."
                    ),
                )
            )

        elif plan.continuity_risk == CONTINUITY_HIGH:

            plan.actions.append(
                MissionContinuityAction(
                    action_id=(
                        f"ACTION-{uuid.uuid4().hex[:10]}"
                    ),
                    action_type=ACTION_FAILOVER,
                    priority=CONTINUITY_HIGH,
                    description=(
                        "Prepare sovereign failover "
                        "coordination."
                    ),
                )
            )

        else:

            plan.actions.append(
                MissionContinuityAction(
                    action_id=(
                        f"ACTION-{uuid.uuid4().hex[:10]}"
                    ),
                    action_type=ACTION_RECOVER,
                    priority=CONTINUITY_CRITICAL,
                    description=(
                        "Initiate autonomous mission "
                        "survivability recovery."
                    ),
                )
            )

    # =====================================================
    # EVENTS
    # =====================================================

    def _emit_plan(
        self,
        plan: MissionContinuityPlan,
    ) -> None:

        if self.event_bus is None:
            return

        try:

            self.event_bus.emit(
                "MISSION_CONTINUITY_PLAN_UPDATED",
                plan.to_dict(),
            )

        except Exception:
            pass

    # =====================================================
    # ACCESSORS
    # =====================================================

    def get_plan(
        self,
        plan_id: str,
    ) -> Optional[
        MissionContinuityPlan
    ]:

        return self.active_plans.get(
            plan_id
        )

    def list_plans(
        self,
    ) -> List[Dict[str, Any]]:

        return [
            p.to_dict()
            for p in self.active_plans.values()
        ]


# =========================================================
# SINGLETON
# =========================================================

_MISSION_CONTINUITY_ENGINE: Optional[
    AutonomousMissionContinuityEngine
] = None


def get_autonomous_mission_continuity_engine(

    runtime_cognition_orchestrator: Optional[Any] = None,

    autonomous_runtime_intelligence_engine: Optional[Any] = None,

    runtime_recovery_manager: Optional[Any] = None,

    runtime_federation_manager: Optional[Any] = None,

    distributed_runtime_cluster_manager: Optional[Any] = None,

    federated_execution_router: Optional[Any] = None,

    sovereign_execution_controller: Optional[Any] = None,

    predictive_runtime_stability_engine: Optional[Any] = None,

    sovereign_operational_reasoning_engine: Optional[Any] = None,

    adaptive_operational_strategy_engine: Optional[Any] = None,

    autonomy_governor_v2: Optional[Any] = None,

    storage: Optional[Any] = None,

    event_bus: Optional[Any] = None,

    reset: bool = False,

) -> AutonomousMissionContinuityEngine:

    global _MISSION_CONTINUITY_ENGINE

    if (
        _MISSION_CONTINUITY_ENGINE is None
        or reset
    ):

        _MISSION_CONTINUITY_ENGINE = (
            AutonomousMissionContinuityEngine(

                runtime_cognition_orchestrator=(
                    runtime_cognition_orchestrator
                ),

                autonomous_runtime_intelligence_engine=(
                    autonomous_runtime_intelligence_engine
                ),

                runtime_recovery_manager=(
                    runtime_recovery_manager
                ),

                runtime_federation_manager=(
                    runtime_federation_manager
                ),

                distributed_runtime_cluster_manager=(
                    distributed_runtime_cluster_manager
                ),

                federated_execution_router=(
                    federated_execution_router
                ),

                sovereign_execution_controller=(
                    sovereign_execution_controller
                ),

                predictive_runtime_stability_engine=(
                    predictive_runtime_stability_engine
                ),

                sovereign_operational_reasoning_engine=(
                    sovereign_operational_reasoning_engine
                ),

                adaptive_operational_strategy_engine=(
                    adaptive_operational_strategy_engine
                ),

                autonomy_governor_v2=(
                    autonomy_governor_v2
                ),

                storage=storage,

                event_bus=event_bus,
            )
        )

    return _MISSION_CONTINUITY_ENGINE