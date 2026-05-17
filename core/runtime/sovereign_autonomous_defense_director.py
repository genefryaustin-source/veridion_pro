"""
core/runtime/sovereign_autonomous_defense_director.py

Sovereign Autonomous Defense Director

Autonomous sovereign defense coordination cognition layer.

This subsystem coordinates:
- strategic defense posture
- resilience allocation
- survivability optimization
- containment prioritization
- mission continuity defense
- adaptive counter-evolution defense
- autonomous defense escalation
- sovereign resilience reinforcement

IMPORTANT:
This subsystem DOES NOT:
- launch offensive cyber operations
- execute destructive actions
- generate malware
- provide offensive intrusion capability
- autonomously attack external systems

It ONLY:
- coordinate defensive posture
- prioritize defensive actions
- orchestrate resilience strategies
- direct mission-preserving defense operations
- record replayable defense lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from enum import Enum

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
)


DEFAULT_ENGINE_NAME = (
    "sovereign_autonomous_defense_director"
)

DEFAULT_DEFENSE_DEPTH = 10


DEFENSE_STATE_STABLE = "STABLE"
DEFENSE_STATE_HARDENING = (
    "HARDENING"
)
DEFENSE_STATE_ADAPTIVE = (
    "ADAPTIVE"
)
DEFENSE_STATE_ESCALATED = (
    "ESCALATED"
)
DEFENSE_STATE_RESILIENCE_SURGE = (
    "RESILIENCE_SURGE"
)
DEFENSE_STATE_MISSION_PROTECTION = (
    "MISSION_PROTECTION"
)

DEFENSE_PRIORITY_LOW = "LOW"
DEFENSE_PRIORITY_MEDIUM = "MEDIUM"
DEFENSE_PRIORITY_HIGH = "HIGH"
DEFENSE_PRIORITY_CRITICAL = (
    "CRITICAL"
)

RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_HARDEN = "HARDEN"
RECOMMENDATION_COUNTER_ADAPT = (
    "COUNTER_ADAPT"
)
RECOMMENDATION_ESCALATE = (
    "ESCALATE"
)
RECOMMENDATION_REBALANCE = (
    "REBALANCE"
)
RECOMMENDATION_MISSION_SHIELD = (
    "MISSION_SHIELD"
)


class DefenseSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DefenseDomain(str, Enum):
    ENDPOINT = "ENDPOINT"
    IDENTITY = "IDENTITY"
    CLOUD = "CLOUD"
    NETWORK = "NETWORK"
    EMAIL = "EMAIL"
    DATA = "DATA"
    GOVERNANCE = "GOVERNANCE"
    MISSION = "MISSION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class DefenseDirective:
    directive_id: str

    directive_name: str
    priority: str
    domain: str

    confidence_score: float
    survivability_impact_score: float
    resilience_impact_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class DefenseSignal:
    defense_signal_id: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    survivability_pressure_score: float = (
        0.0
    )

    resilience_degradation_score: float = (
        0.0
    )

    adversarial_adaptation_score: float = (
        0.0
    )

    containment_failure_risk_score: float = (
        0.0
    )

    escalation_pressure_score: float = (
        0.0
    )

    mission_continuity_risk_score: float = (
        0.0
    )

    governance_pressure_score: float = (
        0.0
    )

    infrastructure_instability_score: float = (
        0.0
    )

    strategic_risk_score: float = (
        0.0
    )

    uncertainty_score: float = 0.0

    directives: List[
        DefenseDirective
    ] = field(default_factory=list)

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class DefenseSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    recommendation: str

    survivability_score: float
    resilience_score: float
    escalation_score: float
    mission_continuity_score: float

    defense_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignDefenseAssessment:
    assessment_id: str

    defense_state: str
    recommendation: str

    survivability_score: float
    resilience_score: float
    escalation_score: float
    mission_continuity_score: float

    strategic_risk_score: float
    uncertainty_score: float

    defense_risk_score: float

    explainability_score: float
    defense_confidence: float

    severity: str
    confidence: float

    defense_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        DefenseSimulationStep
    ]

    defense_topology: Dict[str, Any]

    recommended_controls: List[str]

    recommended_actions: List[
        Dict[str, Any]
    ]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


class SovereignAutonomousDefenseDirector:
    """
    Sovereign autonomous defense cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        adversarial_reasoning_engine: Optional[
            Any
        ] = None,
        threat_evolution_engine: Optional[
            Any
        ] = None,
        resilience_mesh: Optional[Any] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[
            Any
        ] = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.adversarial_reasoning_engine = (
            adversarial_reasoning_engine
        )

        self.threat_evolution_engine = (
            threat_evolution_engine
        )

        self.resilience_mesh = (
            resilience_mesh
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignDefenseAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            DefenseSignal
            | Dict[str, Any]
        ],
        *,
        defense_depth: int = (
            DEFAULT_DEFENSE_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignDefenseAssessment:

        normalized = [
            self._normalize_signal(
                item,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
            )
            for item in signals
        ]

        if not normalized:
            return self._empty_assessment(
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
            )

        selected = normalized[0]

        survivability = (
            self._avg_score(
                [
                    100.0
                    - s
                    .survivability_pressure_score
                    for s in normalized
                ]
            )
        )

        resilience = (
            self._avg_score(
                [
                    100.0
                    - s
                    .resilience_degradation_score
                    for s in normalized
                ]
            )
        )

        escalation = (
            self._avg_score(
                [
                    s
                    .escalation_pressure_score
                    for s in normalized
                ]
            )
        )

        mission_continuity = (
            self._avg_score(
                [
                    100.0
                    - s
                    .mission_continuity_risk_score
                    for s in normalized
                ]
            )
        )

        strategic_risk = (
            self._avg_score(
                [
                    s
                    .strategic_risk_score
                    for s in normalized
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    s.uncertainty_score
                    for s in normalized
                ]
            )
        )

        defense_risk = (
            self._defense_risk_score(
                escalation_score=(
                    escalation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        defense_state = (
            self._defense_state(
                defense_risk_score=(
                    defense_risk
                ),
                survivability_score=(
                    survivability
                ),
                resilience_score=(
                    resilience
                ),
                mission_continuity_score=(
                    mission_continuity
                ),
            )
        )

        recommendation = (
            self._recommendation(
                defense_state=(
                    defense_state
                ),
                escalation_score=(
                    escalation
                ),
                mission_continuity_score=(
                    mission_continuity
                ),
            )
        )

        topology = (
            self._build_topology(
                normalized
            )
        )

        steps = (
            self._build_steps(
                defense_state=(
                    defense_state
                ),
                recommendation=(
                    recommendation
                ),
                survivability_score=(
                    survivability
                ),
                resilience_score=(
                    resilience
                ),
                escalation_score=(
                    escalation
                ),
                mission_continuity_score=(
                    mission_continuity
                ),
                defense_depth=(
                    defense_depth
                ),
            )
        )

        assessment = (
            SovereignDefenseAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                defense_state=(
                    defense_state
                ),
                recommendation=(
                    recommendation
                ),
                survivability_score=(
                    survivability
                ),
                resilience_score=(
                    resilience
                ),
                escalation_score=(
                    escalation
                ),
                mission_continuity_score=(
                    mission_continuity
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                defense_risk_score=(
                    defense_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                defense_confidence=(
                    self
                    ._confidence(
                        normalized
                    )
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                defense_depth=(
                    defense_depth
                ),
                mission_id=(
                    mission_id
                    or selected
                    .mission_id
                ),
                tenant_id=(
                    tenant_id
                    or selected
                    .tenant_id
                ),
                case_id=(
                    case_id
                    or selected.case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected
                    .correlation_id
                ),
                simulation_steps=steps,
                defense_topology=(
                    topology
                ),
                recommended_controls=[
                    (
                        "autonomous_defense_review"
                    ),
                    (
                        "resilience_posture_tracking"
                    ),
                ],
                recommended_actions=[
                    {
                        "action": (
                            "review_defense_posture"
                        )
                    },
                    {
                        "action": (
                            "review_resilience_state"
                        )
                    },
                ],
                rationale=(
                    self._build_rationale(
                        defense_state=(
                            defense_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                        defense_risk_score=(
                            defense_risk
                        ),
                    )
                ),
                metadata={
                    "source_engines": sorted(
                        {
                            s.source_engine
                            for s in normalized
                        }
                    )
                },
            )
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        return assessment

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _defense_state(
        *,
        defense_risk_score: float,
        survivability_score: float,
        resilience_score: float,
        mission_continuity_score: float,
    ) -> str:

        if mission_continuity_score <= 40:
            return (
                DEFENSE_STATE_MISSION_PROTECTION
            )

        if resilience_score <= 45:
            return (
                DEFENSE_STATE_RESILIENCE_SURGE
            )

        if defense_risk_score >= 75:
            return (
                DEFENSE_STATE_ESCALATED
            )

        if survivability_score <= 55:
            return (
                DEFENSE_STATE_ADAPTIVE
            )

        if defense_risk_score >= 45:
            return (
                DEFENSE_STATE_HARDENING
            )

        return DEFENSE_STATE_STABLE

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        defense_state: str,
        escalation_score: float,
        mission_continuity_score: float,
    ) -> str:

        if (
            defense_state
            == DEFENSE_STATE_ESCALATED
        ):
            return (
                RECOMMENDATION_ESCALATE
            )

        if (
            defense_state
            == DEFENSE_STATE_RESILIENCE_SURGE
        ):
            return (
                RECOMMENDATION_REBALANCE
            )

        if (
            defense_state
            == DEFENSE_STATE_MISSION_PROTECTION
        ):
            return (
                RECOMMENDATION_MISSION_SHIELD
            )

        if escalation_score >= 65:
            return (
                RECOMMENDATION_COUNTER_ADAPT
            )

        if mission_continuity_score <= 60:
            return (
                RECOMMENDATION_MISSION_SHIELD
            )

        if (
            defense_state
            == DEFENSE_STATE_HARDENING
        ):
            return (
                RECOMMENDATION_HARDEN
            )

        return RECOMMENDATION_MONITOR

    # ==========================================================
    # RISK
    # ==========================================================

    def _defense_risk_score(
        self,
        *,
        escalation_score: float,
        strategic_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        risk = (
            escalation_score
            + strategic_risk_score
            + uncertainty_score
        ) / 3.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # TOPOLOGY
    # ==========================================================

    def _build_topology(
        self,
        signals: Sequence[
            DefenseSignal
        ],
    ) -> Dict[str, Any]:

        directives = []

        for signal in signals:
            for directive in (
                signal.directives or []
            ):
                directives.append(
                    {
                        "directive_id": (
                            directive
                            .directive_id
                        ),
                        "directive_name": (
                            directive
                            .directive_name
                        ),
                        "priority": (
                            directive.priority
                        ),
                        "domain": (
                            directive.domain
                        ),
                    }
                )

        return {
            "directive_count": len(
                directives
            ),
            "directives": directives,
        }

    # ==========================================================
    # SIMULATION
    # ==========================================================

    def _build_steps(
        self,
        *,
        defense_state: str,
        recommendation: str,
        survivability_score: float,
        resilience_score: float,
        escalation_score: float,
        mission_continuity_score: float,
        defense_depth: int,
    ) -> List[
        DefenseSimulationStep
    ]:

        steps = []

        for idx in range(
            max(1, defense_depth)
        ):

            steps.append(
                DefenseSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        defense_state
                    ),
                    recommendation=(
                        recommendation
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    resilience_score=(
                        resilience_score
                    ),
                    escalation_score=(
                        escalation_score
                    ),
                    mission_continuity_score=(
                        mission_continuity_score
                    ),
                    defense_risk_score=(
                        self
                        ._defense_risk_score(
                            escalation_score=(
                                escalation_score
                            ),
                            strategic_risk_score=(
                                escalation_score
                            ),
                            uncertainty_score=(
                                10.0
                            ),
                        )
                    ),
                    rationale=(
                        f"Defense projection "
                        f"step {idx}."
                    ),
                )
            )

        return steps

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignDefenseAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        payload = {
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if (
                self
                .operational_memory_engine
                and hasattr(
                    self
                    .operational_memory_engine,
                    "append_memory",
                )
            ):
                self.operational_memory_engine.append_memory(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Defense memory write failed: {exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            DefenseSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> DefenseSignal:

        if isinstance(item, DefenseSignal):
            return item

        return DefenseSignal(
            defense_signal_id=str(
                uuid.uuid4()
            ),
            source_engine=str(
                item.get(
                    "source_engine",
                    "unknown_engine",
                )
            ),
            severity=str(
                item.get(
                    "severity",
                    "INFO",
                )
            ),
            confidence=float(
                item.get(
                    "confidence",
                    0.0,
                )
            ),
            summary=str(
                item.get(
                    "summary",
                    "",
                )
            ),
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
        )

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignDefenseAssessment:

        return (
            SovereignDefenseAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                defense_state=(
                    DEFENSE_STATE_STABLE
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                survivability_score=100.0,
                resilience_score=100.0,
                escalation_score=0.0,
                mission_continuity_score=100.0,
                strategic_risk_score=0.0,
                uncertainty_score=0.0,
                defense_risk_score=0.0,
                explainability_score=100.0,
                defense_confidence=1.0,
                severity="INFO",
                confidence=1.0,
                defense_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                defense_topology={},
                recommended_controls=[],
                recommended_actions=[],
                rationale=(
                    "No defense signals submitted."
                ),
                metadata={},
            )
        )

    def _build_rationale(
        self,
        *,
        defense_state: str,
        recommendation: str,
        defense_risk_score: float,
    ) -> str:

        return (
            f"Sovereign autonomous defense "
            f"evaluation completed. "
            f"Defense state "
            f"{defense_state}; "
            f"recommendation "
            f"{recommendation}; "
            f"risk score "
            f"{defense_risk_score:.2f}."
        )

    def _confidence(
        self,
        signals: Sequence[
            DefenseSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean(
                [
                    s.confidence
                    for s in signals
                ]
            )
        )

    def _explainability_score(
        self,
        signals: Sequence[
            DefenseSignal
        ],
    ) -> float:

        return 100.0

    @staticmethod
    def _clamp_score(
        value: Any,
    ) -> float:

        try:
            score = float(value)

        except Exception:
            score = 0.0

        return max(
            0.0,
            min(100.0, score),
        )

    @staticmethod
    def _clamp_probability(
        value: Any,
    ) -> float:

        try:
            score = float(value)

        except Exception:
            score = 0.0

        return max(
            0.0,
            min(1.0, score),
        )

    @staticmethod
    def _avg_score(
        values: Sequence[float],
    ) -> float:

        if not values:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                statistics.mean(values),
            ),
        )


def build_sovereign_autonomous_defense_director(
    *,
    event_bus: Optional[Any] = None,
    adversarial_reasoning_engine: Optional[
        Any
    ] = None,
    threat_evolution_engine: Optional[
        Any
    ] = None,
    resilience_mesh: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignAutonomousDefenseDirector:

    return (
        SovereignAutonomousDefenseDirector(
            event_bus=event_bus,
            adversarial_reasoning_engine=(
                adversarial_reasoning_engine
            ),
            threat_evolution_engine=(
                threat_evolution_engine
            ),
            resilience_mesh=resilience_mesh,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )