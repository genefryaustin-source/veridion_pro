"""
core/runtime/sovereign_operational_command_mesh.py

Sovereign Operational Command Mesh

Unified sovereign operational command cognition layer.

This subsystem coordinates:
- sovereign operational command posture
- mission continuity coordination
- autonomous defense command routing
- resilience command orchestration
- escalation governance coordination
- strategic operational prioritization
- replayable command lineage
- command-level survivability cognition

IMPORTANT:
This subsystem DOES NOT:
- launch offensive cyber operations
- autonomously execute destructive actions
- provide offensive targeting
- generate exploit logic
- bypass governance controls

It ONLY:
- coordinate sovereign operational defense posture
- route operational command directives
- orchestrate resilience command decisions
- coordinate mission-preserving defense actions
- produce replayable operational command lineage
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
    "sovereign_operational_command_mesh"
)

DEFAULT_COMMAND_DEPTH = 12


COMMAND_STATE_STABLE = "STABLE"

COMMAND_STATE_MONITORING = (
    "MONITORING"
)

COMMAND_STATE_HARDENING = (
    "HARDENING"
)

COMMAND_STATE_COORDINATED_RESPONSE = (
    "COORDINATED_RESPONSE"
)

COMMAND_STATE_ESCALATED = (
    "ESCALATED"
)

COMMAND_STATE_MISSION_SHIELD = (
    "MISSION_SHIELD"
)

COMMAND_STATE_STRATEGIC_CONTINUITY = (
    "STRATEGIC_CONTINUITY"
)

COMMAND_PRIORITY_LOW = "LOW"
COMMAND_PRIORITY_MEDIUM = "MEDIUM"
COMMAND_PRIORITY_HIGH = "HIGH"
COMMAND_PRIORITY_CRITICAL = (
    "CRITICAL"
)

RECOMMENDATION_MONITOR = "MONITOR"

RECOMMENDATION_REINFORCE = (
    "REINFORCE"
)

RECOMMENDATION_ESCALATE = (
    "ESCALATE"
)

RECOMMENDATION_COORDINATE = (
    "COORDINATE"
)

RECOMMENDATION_REALIGN = (
    "REALIGN"
)

RECOMMENDATION_CONTINUITY_SHIELD = (
    "CONTINUITY_SHIELD"
)


class CommandSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CommandDomain(str, Enum):
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
class OperationalCommandDirective:
    directive_id: str

    directive_name: str
    priority: str
    domain: str

    confidence_score: float
    operational_impact_score: float
    survivability_impact_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class OperationalCommandSignal:
    command_signal_id: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    operational_pressure_score: float = (
        0.0
    )

    escalation_pressure_score: float = (
        0.0
    )

    survivability_pressure_score: float = (
        0.0
    )

    continuity_risk_score: float = (
        0.0
    )

    governance_pressure_score: float = (
        0.0
    )

    resilience_pressure_score: float = (
        0.0
    )

    coordination_complexity_score: float = (
        0.0
    )

    adversarial_pressure_score: float = (
        0.0
    )

    strategic_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
    )

    directives: List[
        OperationalCommandDirective
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
class OperationalCommandSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    recommendation: str

    survivability_score: float
    resilience_score: float
    continuity_score: float
    escalation_score: float

    operational_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignOperationalCommandAssessment:
    assessment_id: str

    command_state: str
    recommendation: str

    survivability_score: float
    resilience_score: float
    continuity_score: float
    escalation_score: float

    strategic_risk_score: float
    uncertainty_score: float

    operational_risk_score: float

    explainability_score: float
    command_confidence: float

    severity: str
    confidence: float

    command_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        OperationalCommandSimulationStep
    ]

    command_topology: Dict[str, Any]

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


class SovereignOperationalCommandMesh:
    """
    Sovereign operational command cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        autonomous_defense_director: Optional[
            Any
        ] = None,
        adversarial_reasoning_engine: Optional[
            Any
        ] = None,
        threat_evolution_engine: Optional[
            Any
        ] = None,
        resilience_mesh: Optional[Any] = None,
        battle_management_engine: Optional[
            Any
        ] = None,
        war_gaming_engine: Optional[Any] = None,
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

        self.autonomous_defense_director = (
            autonomous_defense_director
        )

        self.adversarial_reasoning_engine = (
            adversarial_reasoning_engine
        )

        self.threat_evolution_engine = (
            threat_evolution_engine
        )

        self.resilience_mesh = (
            resilience_mesh
        )

        self.battle_management_engine = (
            battle_management_engine
        )

        self.war_gaming_engine = (
            war_gaming_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignOperationalCommandAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            OperationalCommandSignal
            | Dict[str, Any]
        ],
        *,
        command_depth: int = (
            DEFAULT_COMMAND_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalCommandAssessment
    ):

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
                    .resilience_pressure_score
                    for s in normalized
                ]
            )
        )

        continuity = (
            self._avg_score(
                [
                    100.0
                    - s
                    .continuity_risk_score
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

        operational_risk = (
            self._operational_risk_score(
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

        command_state = (
            self._command_state(
                operational_risk_score=(
                    operational_risk
                ),
                survivability_score=(
                    survivability
                ),
                resilience_score=(
                    resilience
                ),
                continuity_score=(
                    continuity
                ),
            )
        )

        recommendation = (
            self._recommendation(
                command_state=(
                    command_state
                ),
                escalation_score=(
                    escalation
                ),
                continuity_score=(
                    continuity
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
                command_state=(
                    command_state
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
                continuity_score=(
                    continuity
                ),
                escalation_score=(
                    escalation
                ),
                command_depth=(
                    command_depth
                ),
            )
        )

        assessment = (
            SovereignOperationalCommandAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                command_state=(
                    command_state
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
                continuity_score=(
                    continuity
                ),
                escalation_score=(
                    escalation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                operational_risk_score=(
                    operational_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                command_confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                command_depth=(
                    command_depth
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
                command_topology=(
                    topology
                ),
                recommended_controls=[
                    (
                        "operational_command_review"
                    ),
                    (
                        "mission_continuity_tracking"
                    ),
                ],
                recommended_actions=[
                    {
                        "action": (
                            "review_operational_posture"
                        )
                    },
                    {
                        "action": (
                            "review_continuity_state"
                        )
                    },
                ],
                rationale=(
                    self._build_rationale(
                        command_state=(
                            command_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                        operational_risk_score=(
                            operational_risk
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
    def _command_state(
        *,
        operational_risk_score: float,
        survivability_score: float,
        resilience_score: float,
        continuity_score: float,
    ) -> str:

        if continuity_score <= 40:
            return (
                COMMAND_STATE_MISSION_SHIELD
            )

        if resilience_score <= 45:
            return (
                COMMAND_STATE_COORDINATED_RESPONSE
            )

        if operational_risk_score >= 75:
            return (
                COMMAND_STATE_ESCALATED
            )

        if survivability_score <= 55:
            return (
                COMMAND_STATE_HARDENING
            )

        if operational_risk_score >= 50:
            return (
                COMMAND_STATE_MONITORING
            )

        return COMMAND_STATE_STABLE

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        command_state: str,
        escalation_score: float,
        continuity_score: float,
    ) -> str:

        if (
            command_state
            == COMMAND_STATE_ESCALATED
        ):
            return (
                RECOMMENDATION_ESCALATE
            )

        if (
            command_state
            == COMMAND_STATE_COORDINATED_RESPONSE
        ):
            return (
                RECOMMENDATION_COORDINATE
            )

        if (
            command_state
            == COMMAND_STATE_MISSION_SHIELD
        ):
            return (
                RECOMMENDATION_CONTINUITY_SHIELD
            )

        if escalation_score >= 65:
            return (
                RECOMMENDATION_REALIGN
            )

        if continuity_score <= 60:
            return (
                RECOMMENDATION_CONTINUITY_SHIELD
            )

        if (
            command_state
            == COMMAND_STATE_HARDENING
        ):
            return (
                RECOMMENDATION_REINFORCE
            )

        return RECOMMENDATION_MONITOR

    # ==========================================================
    # RISK
    # ==========================================================

    def _operational_risk_score(
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
            OperationalCommandSignal
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
        command_state: str,
        recommendation: str,
        survivability_score: float,
        resilience_score: float,
        continuity_score: float,
        escalation_score: float,
        command_depth: int,
    ) -> List[
        OperationalCommandSimulationStep
    ]:

        steps = []

        for idx in range(
            max(1, command_depth)
        ):

            steps.append(
                OperationalCommandSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        command_state
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
                    continuity_score=(
                        continuity_score
                    ),
                    escalation_score=(
                        escalation_score
                    ),
                    operational_risk_score=(
                        self
                        ._operational_risk_score(
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
                        f"Operational command "
                        f"projection step "
                        f"{idx}."
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
            SovereignOperationalCommandAssessment
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
                f"⚠️ Operational command memory write failed: {exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            OperationalCommandSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> OperationalCommandSignal:

        if isinstance(
            item,
            OperationalCommandSignal,
        ):
            return item

        return OperationalCommandSignal(
            command_signal_id=str(
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
    ) -> (
        SovereignOperationalCommandAssessment
    ):

        return (
            SovereignOperationalCommandAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                command_state=(
                    COMMAND_STATE_STABLE
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                survivability_score=100.0,
                resilience_score=100.0,
                continuity_score=100.0,
                escalation_score=0.0,
                strategic_risk_score=0.0,
                uncertainty_score=0.0,
                operational_risk_score=0.0,
                explainability_score=100.0,
                command_confidence=1.0,
                severity="INFO",
                confidence=1.0,
                command_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                command_topology={},
                recommended_controls=[],
                recommended_actions=[],
                rationale=(
                    "No operational command "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _build_rationale(
        self,
        *,
        command_state: str,
        recommendation: str,
        operational_risk_score: float,
    ) -> str:

        return (
            f"Sovereign operational "
            f"command evaluation "
            f"completed. "
            f"Command state "
            f"{command_state}; "
            f"recommendation "
            f"{recommendation}; "
            f"risk score "
            f"{operational_risk_score:.2f}."
        )

    def _confidence(
        self,
        signals: Sequence[
            OperationalCommandSignal
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
            OperationalCommandSignal
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


def build_sovereign_operational_command_mesh(
    *,
    event_bus: Optional[Any] = None,
    autonomous_defense_director: Optional[
        Any
    ] = None,
    adversarial_reasoning_engine: Optional[
        Any
    ] = None,
    threat_evolution_engine: Optional[
        Any
    ] = None,
    resilience_mesh: Optional[Any] = None,
    battle_management_engine: Optional[
        Any
    ] = None,
    war_gaming_engine: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignOperationalCommandMesh:

    return (
        SovereignOperationalCommandMesh(
            event_bus=event_bus,
            autonomous_defense_director=(
                autonomous_defense_director
            ),
            adversarial_reasoning_engine=(
                adversarial_reasoning_engine
            ),
            threat_evolution_engine=(
                threat_evolution_engine
            ),
            resilience_mesh=resilience_mesh,
            battle_management_engine=(
                battle_management_engine
            ),
            war_gaming_engine=(
                war_gaming_engine
            ),
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )