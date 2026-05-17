"""
core/runtime/autonomous_mission_simulation_engine.py

Autonomous Mission Simulation Engine

Mission-aware sovereign simulation cognition layer.

This subsystem simulates:
- mission success probability
- mission degradation probability
- mission continuity preservation
- mission survivability
- strategic objective preservation
- governance tradeoffs
- containment tradeoffs
- recovery mission outcomes
- alternate mission futures

IMPORTANT:
This subsystem DOES NOT:
- execute real containment
- mutate infrastructure
- trigger recovery actions
- change autonomy mode directly

It ONLY:
- evaluates mission-oriented simulation signals
- simulates mission futures
- scores objective preservation
- recommends mission-aware controls
- records replayable mission simulation lineage/evidence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "autonomous_mission_simulation_engine"

MISSION_STATE_STABLE = "STABLE"
MISSION_STATE_DEGRADED = "DEGRADED"
MISSION_STATE_AT_RISK = "AT_RISK"
MISSION_STATE_CRITICAL = "CRITICAL"
MISSION_STATE_FAILED = "FAILED"

MISSION_OUTCOME_SUCCESS = "SUCCESS"
MISSION_OUTCOME_PARTIAL = "PARTIAL"
MISSION_OUTCOME_FAILURE = "FAILURE"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_MISSION_REVIEW = "MISSION_REVIEW"
RECOMMENDATION_PRESERVE_CONTINUITY = "PRESERVE_CONTINUITY"
RECOMMENDATION_RECOVERY_MISSION = "RECOVERY_MISSION"
RECOMMENDATION_GOVERNANCE_ESCALATION = "GOVERNANCE_ESCALATION"
RECOMMENDATION_CONTAINMENT_REVIEW = "CONTAINMENT_REVIEW"
RECOMMENDATION_SURVIVABILITY_MODE = "SURVIVABILITY_MODE"
RECOMMENDATION_MISSION_FAILOVER = "MISSION_FAILOVER"

DEFAULT_MISSION_HORIZON = 5


class MissionDomain(str, Enum):
    CONTINUITY = "CONTINUITY"
    CONTAINMENT = "CONTAINMENT"
    GOVERNANCE = "GOVERNANCE"
    RECOVERY = "RECOVERY"
    SURVIVABILITY = "SURVIVABILITY"
    EXECUTION = "EXECUTION"
    TENANT = "TENANT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class MissionSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class MissionObjective:
    objective_id: str
    name: str
    priority: int = 5
    success_weight: float = 1.0
    required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MissionSimulationSignal:
    mission_signal_id: str
    signal_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    mission_priority: int = 5

    mission_success_probability: float = 1.0
    mission_degradation_probability: float = 0.0
    continuity_preservation_probability: float = 1.0
    governance_failure_probability: float = 0.0
    containment_failure_probability: float = 0.0
    recovery_success_probability: float = 1.0
    survivability_probability: float = 1.0

    operational_pressure_score: float = 0.0
    strategic_conflict_score: float = 0.0
    objective_risk_score: float = 0.0

    objectives: List[MissionObjective] = field(default_factory=list)

    payload: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class MissionFutureBranch:
    branch_id: str
    branch_name: str
    mission_state: str
    projected_outcome: str
    mission_success_probability: float
    continuity_probability: float
    survivability_probability: float
    recovery_probability: float
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class MissionSimulationStep:
    step_id: str
    step_index: int
    mission_state: str
    projected_outcome: str
    mission_success_probability: float
    mission_degradation_probability: float
    continuity_preservation_probability: float
    survivability_probability: float
    governance_failure_probability: float
    containment_failure_probability: float
    recovery_success_probability: float
    objective_risk_score: float
    strategic_conflict_score: float
    branches: List[MissionFutureBranch] = field(default_factory=list)
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class AutonomousMissionSimulationAssessment:
    assessment_id: str

    mission_id: Optional[str]
    mission_state: str
    projected_outcome: str
    recommendation: str

    mission_success_probability: float
    mission_degradation_probability: float
    continuity_preservation_probability: float
    governance_failure_probability: float
    containment_failure_probability: float
    recovery_success_probability: float
    survivability_probability: float

    operational_pressure_score: float
    strategic_conflict_score: float
    objective_risk_score: float
    mission_risk_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    mission_horizon: int
    simulation_steps: List[MissionSimulationStep]

    recommended_controls: List[str]
    recommended_actions: List[Dict[str, Any]]

    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class AutonomousMissionSimulationSnapshot:
    engine_name: str
    total_signals_seen: int
    total_assessments_created: int
    last_assessment_id: Optional[str]
    last_mission_state: Optional[str]
    last_mission_risk_score: Optional[float]
    last_updated_ms: int


class AutonomousMissionSimulationEngine:
    """
    Mission-aware autonomous simulation cognition engine.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_simulation_engine: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.operational_simulation_engine = operational_simulation_engine
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._signals_seen = 0
        self._assessments: List[AutonomousMissionSimulationAssessment] = []

    def evaluate(
        self,
        signals: Sequence[MissionSimulationSignal | Dict[str, Any]],
        *,
        mission_horizon: int = DEFAULT_MISSION_HORIZON,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AutonomousMissionSimulationAssessment:
        normalized = [
            self._normalize_signal(
                item,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:
            assessment = self._empty_assessment(
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_assessment(assessment, context=context)
            return assessment

        selected = self._select_primary_signal(normalized)

        mission_success = self._avg_probability(
            [item.mission_success_probability for item in normalized]
        )
        mission_degradation = self._avg_probability(
            [item.mission_degradation_probability for item in normalized]
        )
        continuity = self._avg_probability(
            [item.continuity_preservation_probability for item in normalized]
        )
        governance_failure = self._avg_probability(
            [item.governance_failure_probability for item in normalized]
        )
        containment_failure = self._avg_probability(
            [item.containment_failure_probability for item in normalized]
        )
        recovery_success = self._avg_probability(
            [item.recovery_success_probability for item in normalized]
        )
        survivability = self._avg_probability(
            [item.survivability_probability for item in normalized]
        )

        operational_pressure = self._avg_score(
            [item.operational_pressure_score for item in normalized]
        )
        strategic_conflict = self._avg_score(
            [item.strategic_conflict_score for item in normalized]
        )
        objective_risk = self._avg_score(
            [item.objective_risk_score for item in normalized]
        )

        mission_risk = self._mission_risk_score(
            mission_success_probability=mission_success,
            mission_degradation_probability=mission_degradation,
            continuity_preservation_probability=continuity,
            governance_failure_probability=governance_failure,
            containment_failure_probability=containment_failure,
            recovery_success_probability=recovery_success,
            survivability_probability=survivability,
            operational_pressure_score=operational_pressure,
            strategic_conflict_score=strategic_conflict,
            objective_risk_score=objective_risk,
        )

        mission_state = self._mission_state(
            mission_risk_score=mission_risk,
            mission_success_probability=mission_success,
            continuity_preservation_probability=continuity,
        )

        projected_outcome = self._projected_outcome(
            mission_state=mission_state,
            mission_success_probability=mission_success,
            survivability_probability=survivability,
        )

        recommendation = self._recommendation(
            mission_state=mission_state,
            mission_risk_score=mission_risk,
            governance_failure_probability=governance_failure,
            containment_failure_probability=containment_failure,
            recovery_success_probability=recovery_success,
            continuity_preservation_probability=continuity,
        )

        simulation_steps = self._simulate_mission_steps(
            mission_success_probability=mission_success,
            mission_degradation_probability=mission_degradation,
            continuity_preservation_probability=continuity,
            governance_failure_probability=governance_failure,
            containment_failure_probability=containment_failure,
            recovery_success_probability=recovery_success,
            survivability_probability=survivability,
            objective_risk_score=objective_risk,
            strategic_conflict_score=strategic_conflict,
            horizon=mission_horizon,
        )

        assessment = AutonomousMissionSimulationAssessment(
            assessment_id=str(uuid.uuid4()),
            mission_id=mission_id or selected.mission_id,
            mission_state=mission_state,
            projected_outcome=projected_outcome,
            recommendation=recommendation,
            mission_success_probability=mission_success,
            mission_degradation_probability=mission_degradation,
            continuity_preservation_probability=continuity,
            governance_failure_probability=governance_failure,
            containment_failure_probability=containment_failure,
            recovery_success_probability=recovery_success,
            survivability_probability=survivability,
            operational_pressure_score=operational_pressure,
            strategic_conflict_score=strategic_conflict,
            objective_risk_score=objective_risk,
            mission_risk_score=mission_risk,
            selected_signal_id=selected.mission_signal_id,
            selected_signal_type=selected.signal_type,
            severity=selected.severity,
            confidence=selected.confidence,
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            mission_horizon=mission_horizon,
            simulation_steps=simulation_steps,
            recommended_controls=self._recommended_controls(
                mission_state=mission_state,
                recommendation=recommendation,
            ),
            recommended_actions=self._recommended_actions(
                mission_state=mission_state,
                recommendation=recommendation,
            ),
            rationale=self._build_rationale(
                mission_state=mission_state,
                projected_outcome=projected_outcome,
                recommendation=recommendation,
                mission_success_probability=mission_success,
                continuity_preservation_probability=continuity,
                survivability_probability=survivability,
                mission_risk_score=mission_risk,
                signal_count=len(normalized),
                horizon=mission_horizon,
            ),
            metadata={
                "evaluated_signal_ids": [
                    item.mission_signal_id for item in normalized
                ],
                "objective_count": sum(len(item.objectives) for item in normalized),
                "source_engines": sorted({item.source_engine for item in normalized}),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[MissionSimulationSignal | Dict[str, Any]],
        *,
        mission_horizon: int = DEFAULT_MISSION_HORIZON,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AutonomousMissionSimulationAssessment:
        return self.evaluate(
            signals,
            mission_horizon=mission_horizon,
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def create_signal(
        self,
        *,
        signal_type: str,
        domain: str,
        source_engine: str,
        severity: str,
        confidence: float,
        summary: str,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        mission_priority: int = 5,
        mission_success_probability: float = 1.0,
        mission_degradation_probability: float = 0.0,
        continuity_preservation_probability: float = 1.0,
        governance_failure_probability: float = 0.0,
        containment_failure_probability: float = 0.0,
        recovery_success_probability: float = 1.0,
        survivability_probability: float = 1.0,
        operational_pressure_score: float = 0.0,
        strategic_conflict_score: float = 0.0,
        objective_risk_score: float = 0.0,
        objectives: Optional[List[MissionObjective]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> MissionSimulationSignal:
        return MissionSimulationSignal(
            mission_signal_id=str(uuid.uuid4()),
            signal_type=str(signal_type or "UNKNOWN").upper(),
            domain=self._safe_domain(domain),
            source_engine=source_engine or "unknown_engine",
            severity=self._safe_severity(severity),
            confidence=self._clamp_probability(confidence),
            summary=summary or "",
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            mission_priority=max(1, min(10, int(mission_priority))),
            mission_success_probability=self._clamp_probability(
                mission_success_probability
            ),
            mission_degradation_probability=self._clamp_probability(
                mission_degradation_probability
            ),
            continuity_preservation_probability=self._clamp_probability(
                continuity_preservation_probability
            ),
            governance_failure_probability=self._clamp_probability(
                governance_failure_probability
            ),
            containment_failure_probability=self._clamp_probability(
                containment_failure_probability
            ),
            recovery_success_probability=self._clamp_probability(
                recovery_success_probability
            ),
            survivability_probability=self._clamp_probability(
                survivability_probability
            ),
            operational_pressure_score=self._clamp_score(operational_pressure_score),
            strategic_conflict_score=self._clamp_score(strategic_conflict_score),
            objective_risk_score=self._clamp_score(objective_risk_score),
            objectives=list(objectives or []),
            payload=dict(payload or {}),
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[AutonomousMissionSimulationAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    def snapshot(self) -> AutonomousMissionSimulationSnapshot:
        latest = self._assessments[-1] if self._assessments else None
        return AutonomousMissionSimulationSnapshot(
            engine_name=self.engine_name,
            total_signals_seen=self._signals_seen,
            total_assessments_created=len(self._assessments),
            last_assessment_id=latest.assessment_id if latest else None,
            last_mission_state=latest.mission_state if latest else None,
            last_mission_risk_score=latest.mission_risk_score if latest else None,
            last_updated_ms=int(time.time() * 1000),
        )

    def _simulate_mission_steps(
        self,
        *,
        mission_success_probability: float,
        mission_degradation_probability: float,
        continuity_preservation_probability: float,
        governance_failure_probability: float,
        containment_failure_probability: float,
        recovery_success_probability: float,
        survivability_probability: float,
        objective_risk_score: float,
        strategic_conflict_score: float,
        horizon: int,
    ) -> List[MissionSimulationStep]:
        steps: List[MissionSimulationStep] = []

        success = mission_success_probability
        degradation = mission_degradation_probability
        continuity = continuity_preservation_probability
        governance_failure = governance_failure_probability
        containment_failure = containment_failure_probability
        recovery = recovery_success_probability
        survivability = survivability_probability
        objective_risk = objective_risk_score
        strategic_conflict = strategic_conflict_score

        for index in range(max(1, int(horizon))):
            risk = self._mission_risk_score(
                mission_success_probability=success,
                mission_degradation_probability=degradation,
                continuity_preservation_probability=continuity,
                governance_failure_probability=governance_failure,
                containment_failure_probability=containment_failure,
                recovery_success_probability=recovery,
                survivability_probability=survivability,
                operational_pressure_score=objective_risk,
                strategic_conflict_score=strategic_conflict,
                objective_risk_score=objective_risk,
            )

            state = self._mission_state(
                mission_risk_score=risk,
                mission_success_probability=success,
                continuity_preservation_probability=continuity,
            )

            outcome = self._projected_outcome(
                mission_state=state,
                mission_success_probability=success,
                survivability_probability=survivability,
            )

            branches = self._build_branches(
                state=state,
                success=success,
                continuity=continuity,
                survivability=survivability,
                recovery=recovery,
            )

            steps.append(
                MissionSimulationStep(
                    step_id=str(uuid.uuid4()),
                    step_index=index,
                    mission_state=state,
                    projected_outcome=outcome,
                    mission_success_probability=success,
                    mission_degradation_probability=degradation,
                    continuity_preservation_probability=continuity,
                    survivability_probability=survivability,
                    governance_failure_probability=governance_failure,
                    containment_failure_probability=containment_failure,
                    recovery_success_probability=recovery,
                    objective_risk_score=objective_risk,
                    strategic_conflict_score=strategic_conflict,
                    branches=branches,
                    rationale=(
                        f"Mission simulation step {index} projected {state} "
                        f"with outcome {outcome}."
                    ),
                )
            )

            degradation = self._clamp_probability(degradation + 0.03 + (risk / 5000))
            success = self._clamp_probability(success - 0.02 - (risk / 6000))
            continuity = self._clamp_probability(continuity - 0.015 - (risk / 7000))
            survivability = self._clamp_probability(survivability - 0.015 - (risk / 7000))
            governance_failure = self._clamp_probability(governance_failure + 0.015)
            containment_failure = self._clamp_probability(containment_failure + 0.012)
            recovery = self._clamp_probability(recovery - 0.012)
            objective_risk = self._clamp_score(objective_risk + 2.0)
            strategic_conflict = self._clamp_score(strategic_conflict + 1.5)

        return steps

    def _build_branches(
        self,
        *,
        state: str,
        success: float,
        continuity: float,
        survivability: float,
        recovery: float,
    ) -> List[MissionFutureBranch]:
        return [
            MissionFutureBranch(
                branch_id=str(uuid.uuid4()),
                branch_name="continuity_preservation_path",
                mission_state=MISSION_STATE_STABLE if continuity >= 0.75 else state,
                projected_outcome=(
                    MISSION_OUTCOME_SUCCESS
                    if success >= 0.75 and continuity >= 0.75
                    else MISSION_OUTCOME_PARTIAL
                ),
                mission_success_probability=self._clamp_probability(success + 0.05),
                continuity_probability=self._clamp_probability(continuity + 0.08),
                survivability_probability=self._clamp_probability(survivability + 0.05),
                recovery_probability=self._clamp_probability(recovery + 0.05),
                rationale="Projected mission continuity preservation branch.",
            ),
            MissionFutureBranch(
                branch_id=str(uuid.uuid4()),
                branch_name="mission_degradation_path",
                mission_state=MISSION_STATE_CRITICAL,
                projected_outcome=MISSION_OUTCOME_FAILURE,
                mission_success_probability=self._clamp_probability(success - 0.20),
                continuity_probability=self._clamp_probability(continuity - 0.20),
                survivability_probability=self._clamp_probability(survivability - 0.20),
                recovery_probability=self._clamp_probability(recovery - 0.10),
                rationale="Projected mission degradation branch.",
            ),
        ]

    def _mission_risk_score(
        self,
        *,
        mission_success_probability: float,
        mission_degradation_probability: float,
        continuity_preservation_probability: float,
        governance_failure_probability: float,
        containment_failure_probability: float,
        recovery_success_probability: float,
        survivability_probability: float,
        operational_pressure_score: float,
        strategic_conflict_score: float,
        objective_risk_score: float,
    ) -> float:
        risk = 0.0
        risk += (1.0 - mission_success_probability) * 20
        risk += mission_degradation_probability * 15
        risk += (1.0 - continuity_preservation_probability) * 15
        risk += governance_failure_probability * 10
        risk += containment_failure_probability * 10
        risk += (1.0 - recovery_success_probability) * 10
        risk += (1.0 - survivability_probability) * 10
        risk += operational_pressure_score * 0.04
        risk += strategic_conflict_score * 0.03
        risk += objective_risk_score * 0.03
        return self._clamp_score(risk)

    @staticmethod
    def _mission_state(
        *,
        mission_risk_score: float,
        mission_success_probability: float,
        continuity_preservation_probability: float,
    ) -> str:
        if mission_success_probability <= 0.20 or mission_risk_score >= 90:
            return MISSION_STATE_FAILED
        if mission_risk_score >= 75:
            return MISSION_STATE_CRITICAL
        if mission_risk_score >= 55:
            return MISSION_STATE_AT_RISK
        if mission_risk_score >= 30 or continuity_preservation_probability <= 0.60:
            return MISSION_STATE_DEGRADED
        return MISSION_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        mission_state: str,
        mission_success_probability: float,
        survivability_probability: float,
    ) -> str:
        if mission_state == MISSION_STATE_FAILED:
            return MISSION_OUTCOME_FAILURE
        if mission_success_probability < 0.55 or survivability_probability < 0.55:
            return MISSION_OUTCOME_PARTIAL
        return MISSION_OUTCOME_SUCCESS

    @staticmethod
    def _recommendation(
        *,
        mission_state: str,
        mission_risk_score: float,
        governance_failure_probability: float,
        containment_failure_probability: float,
        recovery_success_probability: float,
        continuity_preservation_probability: float,
    ) -> str:
        if mission_state in {MISSION_STATE_FAILED, MISSION_STATE_CRITICAL}:
            return RECOMMENDATION_RECOVERY_MISSION
        if continuity_preservation_probability <= 0.55:
            return RECOMMENDATION_PRESERVE_CONTINUITY
        if governance_failure_probability >= 0.65:
            return RECOMMENDATION_GOVERNANCE_ESCALATION
        if containment_failure_probability >= 0.65:
            return RECOMMENDATION_CONTAINMENT_REVIEW
        if recovery_success_probability <= 0.45:
            return RECOMMENDATION_MISSION_FAILOVER
        if mission_risk_score >= 50:
            return RECOMMENDATION_SURVIVABILITY_MODE
        if mission_risk_score >= 30:
            return RECOMMENDATION_MISSION_REVIEW
        return RECOMMENDATION_NONE

    @staticmethod
    def _recommended_controls(
        *,
        mission_state: str,
        recommendation: str,
    ) -> List[str]:
        controls = ["lineage_recording", "evidence_recording"]

        if mission_state != MISSION_STATE_STABLE:
            controls.append("mission_review")

        if recommendation in {
            RECOMMENDATION_RECOVERY_MISSION,
            RECOMMENDATION_GOVERNANCE_ESCALATION,
            RECOMMENDATION_MISSION_FAILOVER,
        }:
            controls.append("governance_review")

        if recommendation == RECOMMENDATION_CONTAINMENT_REVIEW:
            controls.append("containment_review")

        return list(dict.fromkeys(controls))

    @staticmethod
    def _recommended_actions(
        *,
        mission_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:
        actions = [
            {"action": "record_mission_simulation_lineage"},
            {"action": "record_mission_simulation_evidence"},
        ]

        if recommendation != RECOMMENDATION_NONE:
            actions.append(
                {
                    "action": "review_mission_posture",
                    "recommendation": recommendation,
                }
            )

        if mission_state in {MISSION_STATE_CRITICAL, MISSION_STATE_FAILED}:
            actions.append({"action": "prepare_mission_recovery_plan"})

        if recommendation == RECOMMENDATION_PRESERVE_CONTINUITY:
            actions.append({"action": "prioritize_mission_continuity"})

        return actions

    @staticmethod
    def _build_rationale(
        *,
        mission_state: str,
        projected_outcome: str,
        recommendation: str,
        mission_success_probability: float,
        continuity_preservation_probability: float,
        survivability_probability: float,
        mission_risk_score: float,
        signal_count: int,
        horizon: int,
    ) -> str:
        return (
            f"Autonomous mission simulation evaluated {signal_count} signal(s) "
            f"across {horizon} mission step(s). Mission state {mission_state}; "
            f"projected outcome {projected_outcome}; recommendation {recommendation}. "
            f"Mission success probability {mission_success_probability:.2f}; "
            f"continuity preservation probability "
            f"{continuity_preservation_probability:.2f}; survivability probability "
            f"{survivability_probability:.2f}; mission risk score "
            f"{mission_risk_score:.2f}."
        )

    def _record_assessment(
        self,
        assessment: AutonomousMissionSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._assessments.append(assessment)
        self._write_to_memory(assessment, context=context)
        self._write_to_lineage(assessment, context=context)
        self._write_to_evidence(assessment, context=context)
        self._emit_event(assessment, context=context)

    def _write_to_memory(
        self,
        assessment: AutonomousMissionSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.operational_memory_engine is None:
            return

        payload = {
            "type": "AUTONOMOUS_MISSION_SIMULATION_ASSESSMENT",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.operational_memory_engine, "append_memory"):
                self.operational_memory_engine.append_memory(payload)
            elif hasattr(self.operational_memory_engine, "record"):
                self.operational_memory_engine.record(payload)
        except Exception as exc:
            print(f"⚠️ Mission simulation memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: AutonomousMissionSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": "MISSION_SIMULATION",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "context": {
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.lineage_engine, "record_lineage"):
                self.lineage_engine.record_lineage(payload)
        except Exception as exc:
            print(f"⚠️ Mission simulation lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: AutonomousMissionSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.fedramp_evidence_lineage_engine is None:
            return

        payload = {
            "evidence_type": "MISSION_SIMULATION",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "evidence_payload": {
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.fedramp_evidence_lineage_engine, "record_evidence"):
                self.fedramp_evidence_lineage_engine.record_evidence(payload)
        except Exception as exc:
            print(f"⚠️ Mission simulation evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: AutonomousMissionSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "AUTONOMOUS_MISSION_SIMULATION_ASSESSMENT",
            "engine_name": self.engine_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "AUTONOMOUS_MISSION_SIMULATION_ASSESSMENT",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Mission simulation event emit failed: {exc}")

    def _normalize_signal(
        self,
        item: MissionSimulationSignal | Dict[str, Any],
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> MissionSimulationSignal:
        if isinstance(item, MissionSimulationSignal):
            return item

        return MissionSimulationSignal(
            mission_signal_id=str(item.get("mission_signal_id") or uuid.uuid4()),
            signal_type=str(item.get("signal_type") or "UNKNOWN").upper(),
            domain=self._safe_domain(item.get("domain")),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            mission_id=mission_id or item.get("mission_id"),
            tenant_id=tenant_id or item.get("tenant_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            mission_priority=max(1, min(10, int(item.get("mission_priority", 5) or 5))),
            mission_success_probability=self._clamp_probability(
                item.get("mission_success_probability", 1.0)
            ),
            mission_degradation_probability=self._clamp_probability(
                item.get("mission_degradation_probability", 0.0)
            ),
            continuity_preservation_probability=self._clamp_probability(
                item.get("continuity_preservation_probability", 1.0)
            ),
            governance_failure_probability=self._clamp_probability(
                item.get("governance_failure_probability", 0.0)
            ),
            containment_failure_probability=self._clamp_probability(
                item.get("containment_failure_probability", 0.0)
            ),
            recovery_success_probability=self._clamp_probability(
                item.get("recovery_success_probability", 1.0)
            ),
            survivability_probability=self._clamp_probability(
                item.get("survivability_probability", 1.0)
            ),
            operational_pressure_score=self._clamp_score(
                item.get("operational_pressure_score", 0.0)
            ),
            strategic_conflict_score=self._clamp_score(
                item.get("strategic_conflict_score", 0.0)
            ),
            objective_risk_score=self._clamp_score(
                item.get("objective_risk_score", 0.0)
            ),
            objectives=[
                obj if isinstance(obj, MissionObjective) else MissionObjective(**obj)
                for obj in (item.get("objectives") or [])
                if isinstance(obj, (MissionObjective, dict))
            ],
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> AutonomousMissionSimulationAssessment:
        return AutonomousMissionSimulationAssessment(
            assessment_id=str(uuid.uuid4()),
            mission_id=mission_id,
            mission_state=MISSION_STATE_STABLE,
            projected_outcome=MISSION_OUTCOME_SUCCESS,
            recommendation=RECOMMENDATION_NONE,
            mission_success_probability=1.0,
            mission_degradation_probability=0.0,
            continuity_preservation_probability=1.0,
            governance_failure_probability=0.0,
            containment_failure_probability=0.0,
            recovery_success_probability=1.0,
            survivability_probability=1.0,
            operational_pressure_score=0.0,
            strategic_conflict_score=0.0,
            objective_risk_score=0.0,
            mission_risk_score=0.0,
            selected_signal_id=None,
            selected_signal_type=None,
            severity=MissionSeverity.INFO.value,
            confidence=1.0,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            mission_horizon=0,
            simulation_steps=[],
            recommended_controls=["lineage_recording", "evidence_recording"],
            recommended_actions=[{"action": "continue_mission_operations"}],
            rationale="No mission simulation signals submitted.",
            metadata={},
        )

    @staticmethod
    def _select_primary_signal(
        signals: Sequence[MissionSimulationSignal],
    ) -> MissionSimulationSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.objective_risk_score,
                item.strategic_conflict_score,
                item.mission_degradation_probability,
                1.0 - item.mission_success_probability,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or MissionDomain.UNKNOWN.value).upper()
        valid = {item.value for item in MissionDomain}
        return value if value in valid else MissionDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or MissionSeverity.INFO.value).upper()
        valid = {item.value for item in MissionSeverity}
        return value if value in valid else MissionSeverity.INFO.value

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(100.0, score))

    @staticmethod
    def _clamp_probability(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def _avg_probability(values: Sequence[float]) -> float:
        if not values:
            return 0.0
        return max(0.0, min(1.0, sum(values) / len(values)))

    @staticmethod
    def _avg_score(values: Sequence[float]) -> float:
        if not values:
            return 0.0
        return max(0.0, min(100.0, sum(values) / len(values)))


def build_autonomous_mission_simulation_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_simulation_engine: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> AutonomousMissionSimulationEngine:
    return AutonomousMissionSimulationEngine(
        event_bus=event_bus,
        operational_simulation_engine=operational_simulation_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )