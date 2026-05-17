"""
core/runtime/sovereign_cyber_defense_simulation_mesh.py

Sovereign Cyber Defense Simulation Mesh

Simulation-only cyber-defense cognition layer.

This subsystem simulates:
- attack propagation
- lateral movement
- privilege escalation
- containment pressure
- defense exhaustion
- mission degradation under attack
- resilience degradation under attack
- autonomous defense coordination outcomes
- alternate attack / defense branches

IMPORTANT:
This subsystem DOES NOT:
- scan networks
- exploit systems
- execute containment
- trigger firewall changes
- isolate endpoints
- mutate infrastructure

It ONLY:
- models cyber-defense scenarios
- forecasts simulated attack/defense outcomes
- evaluates mission survivability under attack
- records replayable cyber-defense simulation lineage/evidence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "sovereign_cyber_defense_simulation_mesh"

CYBER_STATE_STABLE = "STABLE"
CYBER_STATE_CONTESTED = "CONTESTED"
CYBER_STATE_DEGRADED = "DEGRADED"
CYBER_STATE_COMPROMISE_RISK = "COMPROMISE_RISK"
CYBER_STATE_MISSION_IMPACT = "MISSION_IMPACT"
CYBER_STATE_CONTAINMENT_FAILURE_RISK = "CONTAINMENT_FAILURE_RISK"

CYBER_OUTCOME_DEFENDED = "DEFENDED"
CYBER_OUTCOME_CONTAINED = "CONTAINED"
CYBER_OUTCOME_PARTIAL_CONTAINMENT = "PARTIAL_CONTAINMENT"
CYBER_OUTCOME_DEGRADED = "DEGRADED"
CYBER_OUTCOME_COMPROMISE_RISK = "COMPROMISE_RISK"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_DEFENSE_REVIEW = "DEFENSE_REVIEW"
RECOMMENDATION_CONTAINMENT_REVIEW = "CONTAINMENT_REVIEW"
RECOMMENDATION_RESILIENCE_REVIEW = "RESILIENCE_REVIEW"
RECOMMENDATION_MISSION_CONTINUITY_REVIEW = "MISSION_CONTINUITY_REVIEW"
RECOMMENDATION_GOVERNANCE_ESCALATION = "GOVERNANCE_ESCALATION"

DEFAULT_SIMULATION_DEPTH = 6


class CyberDefenseDomain(str, Enum):
    ENDPOINT = "ENDPOINT"
    NETWORK = "NETWORK"
    IDENTITY = "IDENTITY"
    EMAIL = "EMAIL"
    CLOUD = "CLOUD"
    DATA = "DATA"
    GOVERNANCE = "GOVERNANCE"
    MISSION = "MISSION"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class CyberDefenseSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CyberScenarioType(str, Enum):
    ATTACK_PROPAGATION = "ATTACK_PROPAGATION"
    LATERAL_MOVEMENT = "LATERAL_MOVEMENT"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    CONTAINMENT_STRESS = "CONTAINMENT_STRESS"
    DEFENSE_EXHAUSTION = "DEFENSE_EXHAUSTION"
    MISSION_IMPACT = "MISSION_IMPACT"
    RECOVERY_UNDER_ATTACK = "RECOVERY_UNDER_ATTACK"
    MULTI_DOMAIN_ATTACK = "MULTI_DOMAIN_ATTACK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CyberDefenseSimulationSignal:
    cyber_signal_id: str
    scenario_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    attack_pressure_score: float = 0.0
    propagation_risk_score: float = 0.0
    lateral_movement_risk_score: float = 0.0
    privilege_escalation_risk_score: float = 0.0
    containment_strength_score: float = 100.0
    defense_capacity_score: float = 100.0
    detection_confidence_score: float = 100.0
    resilience_score: float = 100.0
    mission_impact_score: float = 0.0
    governance_pressure_score: float = 0.0
    recovery_readiness_score: float = 100.0
    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class CyberDefenseBranch:
    branch_id: str
    branch_name: str
    projected_state: str
    projected_outcome: str

    compromise_probability: float
    containment_probability: float
    mission_survivability_probability: float
    recovery_probability: float

    branch_score: float
    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class CyberDefenseSimulationStep:
    step_id: str
    step_index: int

    projected_state: str
    projected_outcome: str

    attack_pressure_score: float
    propagation_risk_score: float
    lateral_movement_risk_score: float
    privilege_escalation_risk_score: float
    containment_strength_score: float
    defense_capacity_score: float
    detection_confidence_score: float
    resilience_score: float
    mission_impact_score: float
    governance_pressure_score: float
    recovery_readiness_score: float
    uncertainty_score: float

    compromise_probability: float
    containment_probability: float
    mission_survivability_probability: float
    recovery_probability: float

    cyber_risk_score: float

    branches: List[CyberDefenseBranch] = field(default_factory=list)
    rationale: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignCyberDefenseSimulationAssessment:
    assessment_id: str

    cyber_state: str
    projected_outcome: str
    recommendation: str

    attack_pressure_score: float
    propagation_risk_score: float
    lateral_movement_risk_score: float
    privilege_escalation_risk_score: float
    containment_strength_score: float
    defense_capacity_score: float
    detection_confidence_score: float
    resilience_score: float
    mission_impact_score: float
    governance_pressure_score: float
    recovery_readiness_score: float
    uncertainty_score: float

    compromise_probability: float
    containment_probability: float
    mission_survivability_probability: float
    recovery_probability: float

    cyber_risk_score: float
    explainability_score: float
    simulation_confidence: float

    selected_signal_id: Optional[str]
    selected_scenario_type: Optional[str]

    severity: str
    confidence: float

    simulation_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[CyberDefenseSimulationStep]

    recommended_controls: List[str]
    recommended_actions: List[Dict[str, Any]]

    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignCyberDefenseSimulationSnapshot:
    engine_name: str
    total_signals_seen: int
    total_assessments_created: int
    last_assessment_id: Optional[str]
    last_cyber_state: Optional[str]
    last_cyber_risk_score: Optional[float]
    last_updated_ms: int


class SovereignCyberDefenseSimulationMesh:
    """
    Sovereign cyber-defense battlefield simulation mesh.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_simulation_engine: Optional[Any] = None,
        mission_simulation_engine: Optional[Any] = None,
        forecasting_engine: Optional[Any] = None,
        runtime_evolution_engine: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.operational_simulation_engine = operational_simulation_engine
        self.mission_simulation_engine = mission_simulation_engine
        self.forecasting_engine = forecasting_engine
        self.runtime_evolution_engine = runtime_evolution_engine
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._signals_seen = 0
        self._assessments: List[SovereignCyberDefenseSimulationAssessment] = []

    def evaluate(
        self,
        signals: Sequence[CyberDefenseSimulationSignal | Dict[str, Any]],
        *,
        simulation_depth: int = DEFAULT_SIMULATION_DEPTH,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignCyberDefenseSimulationAssessment:
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

        attack_pressure = self._avg_score([s.attack_pressure_score for s in normalized])
        propagation_risk = self._avg_score([s.propagation_risk_score for s in normalized])
        lateral_risk = self._avg_score([s.lateral_movement_risk_score for s in normalized])
        privilege_risk = self._avg_score([s.privilege_escalation_risk_score for s in normalized])
        containment_strength = self._avg_score([s.containment_strength_score for s in normalized])
        defense_capacity = self._avg_score([s.defense_capacity_score for s in normalized])
        detection_confidence = self._avg_score([s.detection_confidence_score for s in normalized])
        resilience = self._avg_score([s.resilience_score for s in normalized])
        mission_impact = self._avg_score([s.mission_impact_score for s in normalized])
        governance_pressure = self._avg_score([s.governance_pressure_score for s in normalized])
        recovery_readiness = self._avg_score([s.recovery_readiness_score for s in normalized])
        uncertainty = self._avg_score([s.uncertainty_score for s in normalized])

        compromise_probability = self._compromise_probability(
            attack_pressure_score=attack_pressure,
            propagation_risk_score=propagation_risk,
            lateral_movement_risk_score=lateral_risk,
            privilege_escalation_risk_score=privilege_risk,
            containment_strength_score=containment_strength,
            defense_capacity_score=defense_capacity,
            detection_confidence_score=detection_confidence,
            resilience_score=resilience,
            uncertainty_score=uncertainty,
        )

        containment_probability = self._containment_probability(
            containment_strength_score=containment_strength,
            defense_capacity_score=defense_capacity,
            detection_confidence_score=detection_confidence,
            attack_pressure_score=attack_pressure,
            propagation_risk_score=propagation_risk,
        )

        mission_survivability_probability = self._mission_survivability_probability(
            resilience_score=resilience,
            mission_impact_score=mission_impact,
            compromise_probability=compromise_probability,
        )

        recovery_probability = self._recovery_probability(
            recovery_readiness_score=recovery_readiness,
            resilience_score=resilience,
            compromise_probability=compromise_probability,
            uncertainty_score=uncertainty,
        )

        cyber_risk = self._cyber_risk_score(
            attack_pressure_score=attack_pressure,
            propagation_risk_score=propagation_risk,
            lateral_movement_risk_score=lateral_risk,
            privilege_escalation_risk_score=privilege_risk,
            mission_impact_score=mission_impact,
            governance_pressure_score=governance_pressure,
            compromise_probability=compromise_probability,
            containment_probability=containment_probability,
            mission_survivability_probability=mission_survivability_probability,
            recovery_probability=recovery_probability,
        )

        cyber_state = self._cyber_state(
            cyber_risk_score=cyber_risk,
            compromise_probability=compromise_probability,
            containment_probability=containment_probability,
            mission_survivability_probability=mission_survivability_probability,
        )

        projected_outcome = self._projected_outcome(
            cyber_state=cyber_state,
            compromise_probability=compromise_probability,
            containment_probability=containment_probability,
        )

        recommendation = self._recommendation(
            cyber_state=cyber_state,
            mission_impact_score=mission_impact,
            governance_pressure_score=governance_pressure,
            containment_probability=containment_probability,
            recovery_probability=recovery_probability,
        )

        simulation_steps = self._simulate_cyber_defense_steps(
            attack_pressure_score=attack_pressure,
            propagation_risk_score=propagation_risk,
            lateral_movement_risk_score=lateral_risk,
            privilege_escalation_risk_score=privilege_risk,
            containment_strength_score=containment_strength,
            defense_capacity_score=defense_capacity,
            detection_confidence_score=detection_confidence,
            resilience_score=resilience,
            mission_impact_score=mission_impact,
            governance_pressure_score=governance_pressure,
            recovery_readiness_score=recovery_readiness,
            uncertainty_score=uncertainty,
            depth=simulation_depth,
        )

        assessment = SovereignCyberDefenseSimulationAssessment(
            assessment_id=str(uuid.uuid4()),
            cyber_state=cyber_state,
            projected_outcome=projected_outcome,
            recommendation=recommendation,
            attack_pressure_score=attack_pressure,
            propagation_risk_score=propagation_risk,
            lateral_movement_risk_score=lateral_risk,
            privilege_escalation_risk_score=privilege_risk,
            containment_strength_score=containment_strength,
            defense_capacity_score=defense_capacity,
            detection_confidence_score=detection_confidence,
            resilience_score=resilience,
            mission_impact_score=mission_impact,
            governance_pressure_score=governance_pressure,
            recovery_readiness_score=recovery_readiness,
            uncertainty_score=uncertainty,
            compromise_probability=compromise_probability,
            containment_probability=containment_probability,
            mission_survivability_probability=mission_survivability_probability,
            recovery_probability=recovery_probability,
            cyber_risk_score=cyber_risk,
            explainability_score=self._explainability_score(normalized),
            simulation_confidence=self._simulation_confidence(normalized),
            selected_signal_id=selected.cyber_signal_id,
            selected_scenario_type=selected.scenario_type,
            severity=selected.severity,
            confidence=selected.confidence,
            simulation_depth=simulation_depth,
            mission_id=mission_id or selected.mission_id,
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            simulation_steps=simulation_steps,
            recommended_controls=self._recommended_controls(
                cyber_state=cyber_state,
                recommendation=recommendation,
            ),
            recommended_actions=self._recommended_actions(
                cyber_state=cyber_state,
                recommendation=recommendation,
            ),
            rationale=self._build_rationale(
                cyber_state=cyber_state,
                projected_outcome=projected_outcome,
                recommendation=recommendation,
                cyber_risk_score=cyber_risk,
                compromise_probability=compromise_probability,
                containment_probability=containment_probability,
                mission_survivability_probability=mission_survivability_probability,
                recovery_probability=recovery_probability,
                signal_count=len(normalized),
                simulation_depth=simulation_depth,
            ),
            metadata={
                "source_engines": sorted({s.source_engine for s in normalized}),
                "domains": sorted({s.domain for s in normalized}),
                "scenario_types": sorted({s.scenario_type for s in normalized}),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[CyberDefenseSimulationSignal | Dict[str, Any]],
        *,
        simulation_depth: int = DEFAULT_SIMULATION_DEPTH,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignCyberDefenseSimulationAssessment:
        return self.evaluate(
            signals,
            simulation_depth=simulation_depth,
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def create_signal(
        self,
        *,
        scenario_type: str,
        domain: str,
        source_engine: str,
        severity: str,
        confidence: float,
        summary: str,
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        attack_pressure_score: float = 0.0,
        propagation_risk_score: float = 0.0,
        lateral_movement_risk_score: float = 0.0,
        privilege_escalation_risk_score: float = 0.0,
        containment_strength_score: float = 100.0,
        defense_capacity_score: float = 100.0,
        detection_confidence_score: float = 100.0,
        resilience_score: float = 100.0,
        mission_impact_score: float = 0.0,
        governance_pressure_score: float = 0.0,
        recovery_readiness_score: float = 100.0,
        uncertainty_score: float = 0.0,
        payload: Optional[Dict[str, Any]] = None,
    ) -> CyberDefenseSimulationSignal:
        return CyberDefenseSimulationSignal(
            cyber_signal_id=str(uuid.uuid4()),
            scenario_type=self._safe_scenario_type(scenario_type),
            domain=self._safe_domain(domain),
            source_engine=source_engine or "unknown_engine",
            severity=self._safe_severity(severity),
            confidence=self._clamp_probability(confidence),
            summary=summary or "",
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            attack_pressure_score=self._clamp_score(attack_pressure_score),
            propagation_risk_score=self._clamp_score(propagation_risk_score),
            lateral_movement_risk_score=self._clamp_score(lateral_movement_risk_score),
            privilege_escalation_risk_score=self._clamp_score(privilege_escalation_risk_score),
            containment_strength_score=self._clamp_score(containment_strength_score),
            defense_capacity_score=self._clamp_score(defense_capacity_score),
            detection_confidence_score=self._clamp_score(detection_confidence_score),
            resilience_score=self._clamp_score(resilience_score),
            mission_impact_score=self._clamp_score(mission_impact_score),
            governance_pressure_score=self._clamp_score(governance_pressure_score),
            recovery_readiness_score=self._clamp_score(recovery_readiness_score),
            uncertainty_score=self._clamp_score(uncertainty_score),
            payload=dict(payload or {}),
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignCyberDefenseSimulationAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    def snapshot(self) -> SovereignCyberDefenseSimulationSnapshot:
        latest = self._assessments[-1] if self._assessments else None
        return SovereignCyberDefenseSimulationSnapshot(
            engine_name=self.engine_name,
            total_signals_seen=self._signals_seen,
            total_assessments_created=len(self._assessments),
            last_assessment_id=latest.assessment_id if latest else None,
            last_cyber_state=latest.cyber_state if latest else None,
            last_cyber_risk_score=latest.cyber_risk_score if latest else None,
            last_updated_ms=int(time.time() * 1000),
        )

    def _simulate_cyber_defense_steps(
        self,
        *,
        attack_pressure_score: float,
        propagation_risk_score: float,
        lateral_movement_risk_score: float,
        privilege_escalation_risk_score: float,
        containment_strength_score: float,
        defense_capacity_score: float,
        detection_confidence_score: float,
        resilience_score: float,
        mission_impact_score: float,
        governance_pressure_score: float,
        recovery_readiness_score: float,
        uncertainty_score: float,
        depth: int,
    ) -> List[CyberDefenseSimulationStep]:
        steps: List[CyberDefenseSimulationStep] = []

        for index in range(max(1, int(depth))):
            compromise = self._compromise_probability(
                attack_pressure_score=attack_pressure_score,
                propagation_risk_score=propagation_risk_score,
                lateral_movement_risk_score=lateral_movement_risk_score,
                privilege_escalation_risk_score=privilege_escalation_risk_score,
                containment_strength_score=containment_strength_score,
                defense_capacity_score=defense_capacity_score,
                detection_confidence_score=detection_confidence_score,
                resilience_score=resilience_score,
                uncertainty_score=uncertainty_score,
            )

            containment = self._containment_probability(
                containment_strength_score=containment_strength_score,
                defense_capacity_score=defense_capacity_score,
                detection_confidence_score=detection_confidence_score,
                attack_pressure_score=attack_pressure_score,
                propagation_risk_score=propagation_risk_score,
            )

            mission_survivability = self._mission_survivability_probability(
                resilience_score=resilience_score,
                mission_impact_score=mission_impact_score,
                compromise_probability=compromise,
            )

            recovery = self._recovery_probability(
                recovery_readiness_score=recovery_readiness_score,
                resilience_score=resilience_score,
                compromise_probability=compromise,
                uncertainty_score=uncertainty_score,
            )

            risk = self._cyber_risk_score(
                attack_pressure_score=attack_pressure_score,
                propagation_risk_score=propagation_risk_score,
                lateral_movement_risk_score=lateral_movement_risk_score,
                privilege_escalation_risk_score=privilege_escalation_risk_score,
                mission_impact_score=mission_impact_score,
                governance_pressure_score=governance_pressure_score,
                compromise_probability=compromise,
                containment_probability=containment,
                mission_survivability_probability=mission_survivability,
                recovery_probability=recovery,
            )

            state = self._cyber_state(
                cyber_risk_score=risk,
                compromise_probability=compromise,
                containment_probability=containment,
                mission_survivability_probability=mission_survivability,
            )

            outcome = self._projected_outcome(
                cyber_state=state,
                compromise_probability=compromise,
                containment_probability=containment,
            )

            branches = self._build_branches(
                cyber_state=state,
                compromise_probability=compromise,
                containment_probability=containment,
                mission_survivability_probability=mission_survivability,
                recovery_probability=recovery,
                cyber_risk_score=risk,
            )

            steps.append(
                CyberDefenseSimulationStep(
                    step_id=str(uuid.uuid4()),
                    step_index=index,
                    projected_state=state,
                    projected_outcome=outcome,
                    attack_pressure_score=attack_pressure_score,
                    propagation_risk_score=propagation_risk_score,
                    lateral_movement_risk_score=lateral_movement_risk_score,
                    privilege_escalation_risk_score=privilege_escalation_risk_score,
                    containment_strength_score=containment_strength_score,
                    defense_capacity_score=defense_capacity_score,
                    detection_confidence_score=detection_confidence_score,
                    resilience_score=resilience_score,
                    mission_impact_score=mission_impact_score,
                    governance_pressure_score=governance_pressure_score,
                    recovery_readiness_score=recovery_readiness_score,
                    uncertainty_score=uncertainty_score,
                    compromise_probability=compromise,
                    containment_probability=containment,
                    mission_survivability_probability=mission_survivability,
                    recovery_probability=recovery,
                    cyber_risk_score=risk,
                    branches=branches,
                    rationale=(
                        f"Cyber-defense simulation step {index} projected "
                        f"{state} with outcome {outcome}."
                    ),
                )
            )

            attack_pressure_score = self._clamp_score(attack_pressure_score + 4.0)
            propagation_risk_score = self._clamp_score(propagation_risk_score + 3.5)
            lateral_movement_risk_score = self._clamp_score(lateral_movement_risk_score + 3.0)
            privilege_escalation_risk_score = self._clamp_score(privilege_escalation_risk_score + 2.5)
            governance_pressure_score = self._clamp_score(governance_pressure_score + 2.0)
            mission_impact_score = self._clamp_score(mission_impact_score + 2.5)
            uncertainty_score = self._clamp_score(uncertainty_score + 1.5)

            containment_strength_score = self._clamp_score(containment_strength_score - 2.5)
            defense_capacity_score = self._clamp_score(defense_capacity_score - 2.0)
            detection_confidence_score = self._clamp_score(detection_confidence_score - 1.0)
            resilience_score = self._clamp_score(resilience_score - 1.8)
            recovery_readiness_score = self._clamp_score(recovery_readiness_score - 1.5)

        return steps

    def _build_branches(
        self,
        *,
        cyber_state: str,
        compromise_probability: float,
        containment_probability: float,
        mission_survivability_probability: float,
        recovery_probability: float,
        cyber_risk_score: float,
    ) -> List[CyberDefenseBranch]:
        return [
            CyberDefenseBranch(
                branch_id=str(uuid.uuid4()),
                branch_name="coordinated_containment_path",
                projected_state=CYBER_STATE_CONTESTED,
                projected_outcome=CYBER_OUTCOME_CONTAINED,
                compromise_probability=self._clamp_probability(compromise_probability - 0.20),
                containment_probability=self._clamp_probability(containment_probability + 0.20),
                mission_survivability_probability=self._clamp_probability(
                    mission_survivability_probability + 0.15
                ),
                recovery_probability=self._clamp_probability(recovery_probability + 0.10),
                branch_score=self._clamp_score(100.0 - cyber_risk_score + 15.0),
                rationale="Projected coordinated containment and recovery branch.",
            ),
            CyberDefenseBranch(
                branch_id=str(uuid.uuid4()),
                branch_name="adversary_propagation_path",
                projected_state=CYBER_STATE_COMPROMISE_RISK,
                projected_outcome=CYBER_OUTCOME_COMPROMISE_RISK,
                compromise_probability=self._clamp_probability(compromise_probability + 0.25),
                containment_probability=self._clamp_probability(containment_probability - 0.20),
                mission_survivability_probability=self._clamp_probability(
                    mission_survivability_probability - 0.20
                ),
                recovery_probability=self._clamp_probability(recovery_probability - 0.15),
                branch_score=self._clamp_score(100.0 - cyber_risk_score - 20.0),
                rationale="Projected adversary propagation branch.",
            ),
        ]

    def _compromise_probability(
        self,
        *,
        attack_pressure_score: float,
        propagation_risk_score: float,
        lateral_movement_risk_score: float,
        privilege_escalation_risk_score: float,
        containment_strength_score: float,
        defense_capacity_score: float,
        detection_confidence_score: float,
        resilience_score: float,
        uncertainty_score: float,
    ) -> float:
        risk = (
            attack_pressure_score
            + propagation_risk_score
            + lateral_movement_risk_score
            + privilege_escalation_risk_score
            + uncertainty_score
            + (100.0 - containment_strength_score)
            + (100.0 - defense_capacity_score)
            + (100.0 - detection_confidence_score)
            + (100.0 - resilience_score)
        ) / 900.0
        return self._clamp_probability(risk)

    def _containment_probability(
        self,
        *,
        containment_strength_score: float,
        defense_capacity_score: float,
        detection_confidence_score: float,
        attack_pressure_score: float,
        propagation_risk_score: float,
    ) -> float:
        score = (
            containment_strength_score
            + defense_capacity_score
            + detection_confidence_score
            + (100.0 - attack_pressure_score)
            + (100.0 - propagation_risk_score)
        ) / 500.0
        return self._clamp_probability(score)

    def _mission_survivability_probability(
        self,
        *,
        resilience_score: float,
        mission_impact_score: float,
        compromise_probability: float,
    ) -> float:
        score = (
            resilience_score
            + (100.0 - mission_impact_score)
            + (100.0 - (compromise_probability * 100.0))
        ) / 300.0
        return self._clamp_probability(score)

    def _recovery_probability(
        self,
        *,
        recovery_readiness_score: float,
        resilience_score: float,
        compromise_probability: float,
        uncertainty_score: float,
    ) -> float:
        score = (
            recovery_readiness_score
            + resilience_score
            + (100.0 - (compromise_probability * 100.0))
            + (100.0 - uncertainty_score)
        ) / 400.0
        return self._clamp_probability(score)

    def _cyber_risk_score(
        self,
        *,
        attack_pressure_score: float,
        propagation_risk_score: float,
        lateral_movement_risk_score: float,
        privilege_escalation_risk_score: float,
        mission_impact_score: float,
        governance_pressure_score: float,
        compromise_probability: float,
        containment_probability: float,
        mission_survivability_probability: float,
        recovery_probability: float,
    ) -> float:
        risk = (
            attack_pressure_score
            + propagation_risk_score
            + lateral_movement_risk_score
            + privilege_escalation_risk_score
            + mission_impact_score
            + governance_pressure_score
            + (compromise_probability * 100.0)
            + ((1.0 - containment_probability) * 100.0)
            + ((1.0 - mission_survivability_probability) * 100.0)
            + ((1.0 - recovery_probability) * 100.0)
        ) / 10.0
        return self._clamp_score(risk)

    @staticmethod
    def _cyber_state(
        *,
        cyber_risk_score: float,
        compromise_probability: float,
        containment_probability: float,
        mission_survivability_probability: float,
    ) -> str:
        if containment_probability <= 0.25:
            return CYBER_STATE_CONTAINMENT_FAILURE_RISK
        if mission_survivability_probability <= 0.35:
            return CYBER_STATE_MISSION_IMPACT
        if compromise_probability >= 0.70 or cyber_risk_score >= 80:
            return CYBER_STATE_COMPROMISE_RISK
        if cyber_risk_score >= 60:
            return CYBER_STATE_DEGRADED
        if cyber_risk_score >= 35:
            return CYBER_STATE_CONTESTED
        return CYBER_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        cyber_state: str,
        compromise_probability: float,
        containment_probability: float,
    ) -> str:
        if cyber_state in {
            CYBER_STATE_COMPROMISE_RISK,
            CYBER_STATE_CONTAINMENT_FAILURE_RISK,
        }:
            return CYBER_OUTCOME_COMPROMISE_RISK
        if containment_probability >= 0.75 and compromise_probability <= 0.35:
            return CYBER_OUTCOME_CONTAINED
        if cyber_state == CYBER_STATE_DEGRADED:
            return CYBER_OUTCOME_DEGRADED
        if cyber_state == CYBER_STATE_CONTESTED:
            return CYBER_OUTCOME_PARTIAL_CONTAINMENT
        return CYBER_OUTCOME_DEFENDED

    @staticmethod
    def _recommendation(
        *,
        cyber_state: str,
        mission_impact_score: float,
        governance_pressure_score: float,
        containment_probability: float,
        recovery_probability: float,
    ) -> str:
        if cyber_state == CYBER_STATE_CONTAINMENT_FAILURE_RISK:
            return RECOMMENDATION_CONTAINMENT_REVIEW
        if mission_impact_score >= 70:
            return RECOMMENDATION_MISSION_CONTINUITY_REVIEW
        if governance_pressure_score >= 70:
            return RECOMMENDATION_GOVERNANCE_ESCALATION
        if recovery_probability <= 0.45:
            return RECOMMENDATION_RESILIENCE_REVIEW
        if containment_probability <= 0.55:
            return RECOMMENDATION_CONTAINMENT_REVIEW
        if cyber_state in {CYBER_STATE_DEGRADED, CYBER_STATE_COMPROMISE_RISK}:
            return RECOMMENDATION_DEFENSE_REVIEW
        if cyber_state == CYBER_STATE_CONTESTED:
            return RECOMMENDATION_MONITOR
        return RECOMMENDATION_NONE

    @staticmethod
    def _recommended_controls(
        *,
        cyber_state: str,
        recommendation: str,
    ) -> List[str]:
        controls = ["lineage_recording", "evidence_recording"]

        if cyber_state != CYBER_STATE_STABLE:
            controls.append("cyber_defense_review")

        if recommendation in {
            RECOMMENDATION_CONTAINMENT_REVIEW,
            RECOMMENDATION_GOVERNANCE_ESCALATION,
            RECOMMENDATION_MISSION_CONTINUITY_REVIEW,
        }:
            controls.append("governance_review")

        if recommendation == RECOMMENDATION_CONTAINMENT_REVIEW:
            controls.append("containment_review")

        return list(dict.fromkeys(controls))

    @staticmethod
    def _recommended_actions(
        *,
        cyber_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:
        actions = [
            {"action": "record_cyber_defense_simulation_lineage"},
            {"action": "record_cyber_defense_simulation_evidence"},
        ]

        if recommendation != RECOMMENDATION_NONE:
            actions.append(
                {
                    "action": "review_cyber_defense_posture",
                    "recommendation": recommendation,
                }
            )

        if cyber_state in {
            CYBER_STATE_COMPROMISE_RISK,
            CYBER_STATE_CONTAINMENT_FAILURE_RISK,
        }:
            actions.append({"action": "prepare_simulated_containment_options"})

        if cyber_state == CYBER_STATE_MISSION_IMPACT:
            actions.append({"action": "prepare_mission_continuity_review"})

        return actions

    @staticmethod
    def _build_rationale(
        *,
        cyber_state: str,
        projected_outcome: str,
        recommendation: str,
        cyber_risk_score: float,
        compromise_probability: float,
        containment_probability: float,
        mission_survivability_probability: float,
        recovery_probability: float,
        signal_count: int,
        simulation_depth: int,
    ) -> str:
        return (
            f"Sovereign cyber-defense simulation evaluated {signal_count} signal(s) "
            f"across {simulation_depth} simulation step(s). Cyber state {cyber_state}; "
            f"projected outcome {projected_outcome}; recommendation {recommendation}. "
            f"Cyber risk score {cyber_risk_score:.2f}; compromise probability "
            f"{compromise_probability:.2f}; containment probability "
            f"{containment_probability:.2f}; mission survivability probability "
            f"{mission_survivability_probability:.2f}; recovery probability "
            f"{recovery_probability:.2f}."
        )

    def _record_assessment(
        self,
        assessment: SovereignCyberDefenseSimulationAssessment,
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
        assessment: SovereignCyberDefenseSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.operational_memory_engine is None:
            return

        payload = {
            "type": "SOVEREIGN_CYBER_DEFENSE_SIMULATION_ASSESSMENT",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.operational_memory_engine, "append_memory"):
                self.operational_memory_engine.append_memory(payload)
            elif hasattr(self.operational_memory_engine, "record"):
                self.operational_memory_engine.record(payload)
        except Exception as exc:
            print(f"⚠️ Cyber-defense simulation memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: SovereignCyberDefenseSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": "CYBER_DEFENSE_SIMULATION",
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
            print(f"⚠️ Cyber-defense simulation lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: SovereignCyberDefenseSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.fedramp_evidence_lineage_engine is None:
            return

        payload = {
            "evidence_type": "CYBER_DEFENSE_SIMULATION",
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
            print(f"⚠️ Cyber-defense simulation evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: SovereignCyberDefenseSimulationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGN_CYBER_DEFENSE_SIMULATION_ASSESSMENT",
            "engine_name": self.engine_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_CYBER_DEFENSE_SIMULATION_ASSESSMENT",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Cyber-defense simulation event emit failed: {exc}")

    def _normalize_signal(
        self,
        item: CyberDefenseSimulationSignal | Dict[str, Any],
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> CyberDefenseSimulationSignal:
        if isinstance(item, CyberDefenseSimulationSignal):
            return item

        return CyberDefenseSimulationSignal(
            cyber_signal_id=str(item.get("cyber_signal_id") or uuid.uuid4()),
            scenario_type=self._safe_scenario_type(item.get("scenario_type")),
            domain=self._safe_domain(item.get("domain")),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            mission_id=mission_id or item.get("mission_id"),
            tenant_id=tenant_id or item.get("tenant_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            attack_pressure_score=self._clamp_score(item.get("attack_pressure_score", 0.0)),
            propagation_risk_score=self._clamp_score(item.get("propagation_risk_score", 0.0)),
            lateral_movement_risk_score=self._clamp_score(
                item.get("lateral_movement_risk_score", 0.0)
            ),
            privilege_escalation_risk_score=self._clamp_score(
                item.get("privilege_escalation_risk_score", 0.0)
            ),
            containment_strength_score=self._clamp_score(
                item.get("containment_strength_score", 100.0)
            ),
            defense_capacity_score=self._clamp_score(
                item.get("defense_capacity_score", 100.0)
            ),
            detection_confidence_score=self._clamp_score(
                item.get("detection_confidence_score", 100.0)
            ),
            resilience_score=self._clamp_score(item.get("resilience_score", 100.0)),
            mission_impact_score=self._clamp_score(item.get("mission_impact_score", 0.0)),
            governance_pressure_score=self._clamp_score(
                item.get("governance_pressure_score", 0.0)
            ),
            recovery_readiness_score=self._clamp_score(
                item.get("recovery_readiness_score", 100.0)
            ),
            uncertainty_score=self._clamp_score(item.get("uncertainty_score", 0.0)),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignCyberDefenseSimulationAssessment:
        return SovereignCyberDefenseSimulationAssessment(
            assessment_id=str(uuid.uuid4()),
            cyber_state=CYBER_STATE_STABLE,
            projected_outcome=CYBER_OUTCOME_DEFENDED,
            recommendation=RECOMMENDATION_NONE,
            attack_pressure_score=0.0,
            propagation_risk_score=0.0,
            lateral_movement_risk_score=0.0,
            privilege_escalation_risk_score=0.0,
            containment_strength_score=100.0,
            defense_capacity_score=100.0,
            detection_confidence_score=100.0,
            resilience_score=100.0,
            mission_impact_score=0.0,
            governance_pressure_score=0.0,
            recovery_readiness_score=100.0,
            uncertainty_score=0.0,
            compromise_probability=0.0,
            containment_probability=1.0,
            mission_survivability_probability=1.0,
            recovery_probability=1.0,
            cyber_risk_score=0.0,
            explainability_score=100.0,
            simulation_confidence=1.0,
            selected_signal_id=None,
            selected_scenario_type=None,
            severity=CyberDefenseSeverity.INFO.value,
            confidence=1.0,
            simulation_depth=0,
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            simulation_steps=[],
            recommended_controls=["lineage_recording", "evidence_recording"],
            recommended_actions=[{"action": "continue_cyber_defense_monitoring"}],
            rationale="No cyber-defense simulation signals submitted.",
            metadata={},
        )

    @staticmethod
    def _select_primary_signal(
        signals: Sequence[CyberDefenseSimulationSignal],
    ) -> CyberDefenseSimulationSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.attack_pressure_score,
                item.propagation_risk_score,
                item.lateral_movement_risk_score,
                item.privilege_escalation_risk_score,
                item.mission_impact_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _explainability_score(
        self,
        signals: Sequence[CyberDefenseSimulationSignal],
    ) -> float:
        if not signals:
            return 0.0

        explained = 0
        for item in signals:
            if item.summary:
                explained += 1
            if item.source_engine:
                explained += 1
            if item.scenario_type:
                explained += 1

        return self._clamp_score((explained / (len(signals) * 3)) * 100)

    def _simulation_confidence(
        self,
        signals: Sequence[CyberDefenseSimulationSignal],
    ) -> float:
        if not signals:
            return 0.0
        return self._clamp_probability(
            sum(item.confidence for item in signals) / len(signals)
        )

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or CyberDefenseDomain.UNKNOWN.value).upper()
        valid = {item.value for item in CyberDefenseDomain}
        return value if value in valid else CyberDefenseDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or CyberDefenseSeverity.INFO.value).upper()
        valid = {item.value for item in CyberDefenseSeverity}
        return value if value in valid else CyberDefenseSeverity.INFO.value

    @staticmethod
    def _safe_scenario_type(value: Any) -> str:
        value = str(value or CyberScenarioType.UNKNOWN.value).upper()
        valid = {item.value for item in CyberScenarioType}
        return value if value in valid else CyberScenarioType.UNKNOWN.value

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
    def _avg_score(values: Sequence[float]) -> float:
        if not values:
            return 0.0
        return max(0.0, min(100.0, sum(values) / len(values)))


def build_sovereign_cyber_defense_simulation_mesh(
    *,
    event_bus: Optional[Any] = None,
    operational_simulation_engine: Optional[Any] = None,
    mission_simulation_engine: Optional[Any] = None,
    forecasting_engine: Optional[Any] = None,
    runtime_evolution_engine: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignCyberDefenseSimulationMesh:
    return SovereignCyberDefenseSimulationMesh(
        event_bus=event_bus,
        operational_simulation_engine=operational_simulation_engine,
        mission_simulation_engine=mission_simulation_engine,
        forecasting_engine=forecasting_engine,
        runtime_evolution_engine=runtime_evolution_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )