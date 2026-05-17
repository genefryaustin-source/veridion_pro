"""
core/runtime/sovereign_command_center_copilot.py

Sovereign Command Center Copilot

Unified sovereign operational intelligence aggregation layer.

This subsystem aggregates:
- runtime cognition
- simulation cognition
- forecasting cognition
- evolution cognition
- war-gaming cognition
- battle management cognition
- adversarial reasoning cognition
- autonomous defense cognition
- operational governance cognition
- sovereignty assurance cognition

IMPORTANT:
This subsystem DOES NOT:
- execute destructive operations
- bypass governance
- mutate infrastructure directly
- autonomously attack systems
- override sovereignty protections

It ONLY:
- aggregate sovereign operational intelligence
- unify explainability streams
- coordinate replayable strategic lineage
- produce strategic operational projections
- feed command center visibility layers
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
    "sovereign_command_center_copilot"
)

DEFAULT_TIMELINE_DEPTH = 24


COPILOT_STATE_STABLE = "STABLE"

COPILOT_STATE_MONITORING = (
    "MONITORING"
)

COPILOT_STATE_ELEVATED = (
    "ELEVATED"
)

COPILOT_STATE_ESCALATED = (
    "ESCALATED"
)

COPILOT_STATE_SOVEREIGN_REVIEW = (
    "SOVEREIGN_REVIEW"
)

COPILOT_STATE_MISSION_CONTINUITY = (
    "MISSION_CONTINUITY"
)

PROJECTION_STABLE = "STABLE"

PROJECTION_ADAPTIVE_DEFENSE = (
    "ADAPTIVE_DEFENSE"
)

PROJECTION_GOVERNANCE_ESCALATION = (
    "GOVERNANCE_ESCALATION"
)

PROJECTION_SOVEREIGN_REINFORCEMENT = (
    "SOVEREIGN_REINFORCEMENT"
)

PROJECTION_MISSION_SHIELD = (
    "MISSION_SHIELD"
)

RECOMMENDATION_MONITOR = "MONITOR"

RECOMMENDATION_REVIEW = (
    "REVIEW"
)

RECOMMENDATION_ESCALATE = (
    "ESCALATE"
)

RECOMMENDATION_RESTRICT_AUTONOMY = (
    "RESTRICT_AUTONOMY"
)

RECOMMENDATION_ENABLE_CONTINUITY = (
    "ENABLE_CONTINUITY"
)

RECOMMENDATION_ENABLE_SOVEREIGN_PROTECTION = (
    "ENABLE_SOVEREIGN_PROTECTION"
)


class CopilotSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CopilotDomain(str, Enum):
    RUNTIME = "RUNTIME"
    GOVERNANCE = "GOVERNANCE"
    DEFENSE = "DEFENSE"
    WAR_GAMING = "WAR_GAMING"
    THREAT = "THREAT"
    ASSURANCE = "ASSURANCE"
    MISSION = "MISSION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CopilotSignal:
    signal_id: str

    source_engine: str
    domain: str

    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    operational_risk_score: float = (
        0.0
    )

    governance_risk_score: float = (
        0.0
    )

    sovereignty_risk_score: float = (
        0.0
    )

    resilience_risk_score: float = (
        0.0
    )

    mission_continuity_risk_score: float = (
        0.0
    )

    escalation_pressure_score: float = (
        0.0
    )

    survivability_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
    )

    explainability: List[str] = field(
        default_factory=list
    )

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class StrategicTimelineEvent:
    event_id: str

    event_type: str
    source_engine: str

    summary: str

    severity: str

    created_at_ms: int

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class StrategicProjection:
    projection_id: str

    projection_state: str

    operational_projection_score: float
    governance_projection_score: float
    sovereignty_projection_score: float
    continuity_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignCommandCenterAssessment:
    assessment_id: str

    copilot_state: str
    projected_state: str

    recommendation: str

    operational_risk_score: float
    governance_risk_score: float
    sovereignty_risk_score: float
    resilience_risk_score: float
    continuity_risk_score: float

    survivability_score: float

    explainability_score: float

    confidence: float
    uncertainty_score: float

    severity: str

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    strategic_projection: StrategicProjection

    timeline_events: List[
        StrategicTimelineEvent
    ]

    operational_stream: Dict[str, Any]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


class SovereignCommandCenterCopilot:
    """
    Unified sovereign operational intelligence layer.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        runtime_cognition_engine: Optional[
            Any
        ] = None,
        simulation_engine: Optional[Any] = None,
        forecasting_engine: Optional[Any] = None,
        evolution_engine: Optional[Any] = None,
        war_gaming_engine: Optional[Any] = None,
        battle_management_engine: Optional[
            Any
        ] = None,
        adversarial_reasoning_engine: Optional[
            Any
        ] = None,
        autonomous_defense_director: Optional[
            Any
        ] = None,
        operational_governor: Optional[
            Any
        ] = None,
        sovereignty_assurance_engine: Optional[
            Any
        ] = None,
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

        self.runtime_cognition_engine = (
            runtime_cognition_engine
        )

        self.simulation_engine = (
            simulation_engine
        )

        self.forecasting_engine = (
            forecasting_engine
        )

        self.evolution_engine = (
            evolution_engine
        )

        self.war_gaming_engine = (
            war_gaming_engine
        )

        self.battle_management_engine = (
            battle_management_engine
        )

        self.adversarial_reasoning_engine = (
            adversarial_reasoning_engine
        )

        self.autonomous_defense_director = (
            autonomous_defense_director
        )

        self.operational_governor = (
            operational_governor
        )

        self.sovereignty_assurance_engine = (
            sovereignty_assurance_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignCommandCenterAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            CopilotSignal
            | Dict[str, Any]
        ],
        *,
        timeline_depth: int = (
            DEFAULT_TIMELINE_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignCommandCenterAssessment
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

        operational_risk = (
            self._avg_score(
                [
                    s
                    .operational_risk_score
                    for s in normalized
                ]
            )
        )

        governance_risk = (
            self._avg_score(
                [
                    s
                    .governance_risk_score
                    for s in normalized
                ]
            )
        )

        sovereignty_risk = (
            self._avg_score(
                [
                    s
                    .sovereignty_risk_score
                    for s in normalized
                ]
            )
        )

        resilience_risk = (
            self._avg_score(
                [
                    s
                    .resilience_risk_score
                    for s in normalized
                ]
            )
        )

        continuity_risk = (
            self._avg_score(
                [
                    s
                    .mission_continuity_risk_score
                    for s in normalized
                ]
            )
        )

        survivability_score = (
            self._avg_score(
                [
                    100.0
                    - s
                    .survivability_risk_score
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

        copilot_state = (
            self._copilot_state(
                operational_risk_score=(
                    operational_risk
                ),
                governance_risk_score=(
                    governance_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
            )
        )

        recommendation = (
            self._recommendation(
                copilot_state=(
                    copilot_state
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
            )
        )

        projection = (
            self._projection(
                operational_risk_score=(
                    operational_risk
                ),
                governance_risk_score=(
                    governance_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
            )
        )

        timeline_events = (
            self._timeline_events(
                normalized,
                limit=timeline_depth,
            )
        )

        operational_stream = (
            self._operational_stream(
                normalized
            )
        )

        assessment = (
            SovereignCommandCenterAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                copilot_state=(
                    copilot_state
                ),
                projected_state=(
                    projection
                    .projection_state
                ),
                recommendation=(
                    recommendation
                ),
                operational_risk_score=(
                    operational_risk
                ),
                governance_risk_score=(
                    governance_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                resilience_risk_score=(
                    resilience_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                survivability_score=(
                    survivability_score
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                uncertainty_score=(
                    uncertainty
                ),
                severity=(
                    selected.severity
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
                strategic_projection=(
                    projection
                ),
                timeline_events=(
                    timeline_events
                ),
                operational_stream=(
                    operational_stream
                ),
                rationale=(
                    self._build_rationale(
                        copilot_state=(
                            copilot_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                        projected_state=(
                            projection
                            .projection_state
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
    def _copilot_state(
        *,
        operational_risk_score: float,
        governance_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> str:

        if sovereignty_risk_score >= 75:
            return (
                COPILOT_STATE_SOVEREIGN_REVIEW
            )

        if continuity_risk_score >= 75:
            return (
                COPILOT_STATE_MISSION_CONTINUITY
            )

        if governance_risk_score >= 70:
            return (
                COPILOT_STATE_ESCALATED
            )

        if operational_risk_score >= 50:
            return (
                COPILOT_STATE_ELEVATED
            )

        if operational_risk_score >= 25:
            return (
                COPILOT_STATE_MONITORING
            )

        return COPILOT_STATE_STABLE

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        copilot_state: str,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> str:

        if (
            copilot_state
            == COPILOT_STATE_SOVEREIGN_REVIEW
        ):
            return (
                RECOMMENDATION_ENABLE_SOVEREIGN_PROTECTION
            )

        if (
            copilot_state
            == COPILOT_STATE_MISSION_CONTINUITY
        ):
            return (
                RECOMMENDATION_ENABLE_CONTINUITY
            )

        if (
            copilot_state
            == COPILOT_STATE_ESCALATED
        ):
            return (
                RECOMMENDATION_ESCALATE
            )

        if sovereignty_risk_score >= 60:
            return (
                RECOMMENDATION_RESTRICT_AUTONOMY
            )

        if continuity_risk_score >= 60:
            return (
                RECOMMENDATION_ENABLE_CONTINUITY
            )

        if (
            copilot_state
            == COPILOT_STATE_ELEVATED
        ):
            return (
                RECOMMENDATION_REVIEW
            )

        return RECOMMENDATION_MONITOR

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        operational_risk_score: float,
        governance_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> StrategicProjection:

        state = PROJECTION_STABLE

        if sovereignty_risk_score >= 75:
            state = (
                PROJECTION_SOVEREIGN_REINFORCEMENT
            )

        elif continuity_risk_score >= 75:
            state = (
                PROJECTION_MISSION_SHIELD
            )

        elif governance_risk_score >= 70:
            state = (
                PROJECTION_GOVERNANCE_ESCALATION
            )

        elif operational_risk_score >= 50:
            state = (
                PROJECTION_ADAPTIVE_DEFENSE
            )

        return StrategicProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projection_state=state,
            operational_projection_score=(
                operational_risk_score
            ),
            governance_projection_score=(
                governance_risk_score
            ),
            sovereignty_projection_score=(
                sovereignty_risk_score
            ),
            continuity_projection_score=(
                continuity_risk_score
            ),
            rationale=(
                f"Projected strategic "
                f"state {state}."
            ),
        )

    # ==========================================================
    # TIMELINE
    # ==========================================================

    def _timeline_events(
        self,
        signals: Sequence[
            CopilotSignal
        ],
        *,
        limit: int,
    ) -> List[
        StrategicTimelineEvent
    ]:

        events = []

        for signal in signals[:limit]:

            events.append(
                StrategicTimelineEvent(
                    event_id=str(
                        uuid.uuid4()
                    ),
                    event_type=(
                        signal.domain
                    ),
                    source_engine=(
                        signal.source_engine
                    ),
                    summary=(
                        signal.summary
                    ),
                    severity=(
                        signal.severity
                    ),
                    created_at_ms=(
                        signal.created_at_ms
                    ),
                )
            )

        return events

    # ==========================================================
    # STREAM
    # ==========================================================

    def _operational_stream(
        self,
        signals: Sequence[
            CopilotSignal
        ],
    ) -> Dict[str, Any]:

        return {
            "signal_count": len(
                signals
            ),
            "domains": sorted(
                {
                    s.domain
                    for s in signals
                }
            ),
            "engines": sorted(
                {
                    s.source_engine
                    for s in signals
                }
            ),
        }

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignCommandCenterAssessment
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
                self.operational_memory_engine
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
                f"⚠️ Copilot memory write failed: {exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            CopilotSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> CopilotSignal:

        if isinstance(item, CopilotSignal):
            return item

        return CopilotSignal(
            signal_id=str(
                uuid.uuid4()
            ),
            source_engine=str(
                item.get(
                    "source_engine",
                    "unknown_engine",
                )
            ),
            domain=str(
                item.get(
                    "domain",
                    "UNKNOWN",
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
            operational_risk_score=float(
                item.get(
                    "operational_risk_score",
                    0.0,
                )
            ),
            governance_risk_score=float(
                item.get(
                    "governance_risk_score",
                    0.0,
                )
            ),
            sovereignty_risk_score=float(
                item.get(
                    "sovereignty_risk_score",
                    0.0,
                )
            ),
            resilience_risk_score=float(
                item.get(
                    "resilience_risk_score",
                    0.0,
                )
            ),
            mission_continuity_risk_score=float(
                item.get(
                    "mission_continuity_risk_score",
                    0.0,
                )
            ),
            escalation_pressure_score=float(
                item.get(
                    "escalation_pressure_score",
                    0.0,
                )
            ),
            survivability_risk_score=float(
                item.get(
                    "survivability_risk_score",
                    0.0,
                )
            ),
            uncertainty_score=float(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),
            explainability=list(
                item.get(
                    "explainability",
                    [],
                )
            ),
            payload=dict(
                item.get(
                    "payload",
                    {},
                )
            ),
        )

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignCommandCenterAssessment
    ):

        projection = (
            StrategicProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projection_state=(
                    PROJECTION_STABLE
                ),
                operational_projection_score=0.0,
                governance_projection_score=0.0,
                sovereignty_projection_score=0.0,
                continuity_projection_score=0.0,
                rationale=(
                    "No signals submitted."
                ),
            )
        )

        return (
            SovereignCommandCenterAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                copilot_state=(
                    COPILOT_STATE_STABLE
                ),
                projected_state=(
                    PROJECTION_STABLE
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                operational_risk_score=0.0,
                governance_risk_score=0.0,
                sovereignty_risk_score=0.0,
                resilience_risk_score=0.0,
                continuity_risk_score=0.0,
                survivability_score=100.0,
                explainability_score=100.0,
                confidence=1.0,
                uncertainty_score=0.0,
                severity="INFO",
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                strategic_projection=(
                    projection
                ),
                timeline_events=[],
                operational_stream={},
                rationale=(
                    "No copilot signals submitted."
                ),
                metadata={},
            )
        )

    def _build_rationale(
        self,
        *,
        copilot_state: str,
        recommendation: str,
        projected_state: str,
    ) -> str:

        return (
            f"Sovereign command center "
            f"copilot evaluation "
            f"completed. "
            f"State {copilot_state}; "
            f"recommendation "
            f"{recommendation}; "
            f"projected state "
            f"{projected_state}."
        )

    def _confidence(
        self,
        signals: Sequence[
            CopilotSignal
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
            CopilotSignal
        ],
    ) -> float:

        explained = sum(
            len(s.explainability)
            for s in signals
        )

        return self._clamp_score(
            explained * 10.0
        )

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


def build_sovereign_command_center_copilot(
    *,
    event_bus: Optional[Any] = None,
    runtime_cognition_engine: Optional[
        Any
    ] = None,
    simulation_engine: Optional[Any] = None,
    forecasting_engine: Optional[Any] = None,
    evolution_engine: Optional[Any] = None,
    war_gaming_engine: Optional[Any] = None,
    battle_management_engine: Optional[
        Any
    ] = None,
    adversarial_reasoning_engine: Optional[
        Any
    ] = None,
    autonomous_defense_director: Optional[
        Any
    ] = None,
    operational_governor: Optional[
        Any
    ] = None,
    sovereignty_assurance_engine: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignCommandCenterCopilot:

    return (
        SovereignCommandCenterCopilot(
            event_bus=event_bus,
            runtime_cognition_engine=(
                runtime_cognition_engine
            ),
            simulation_engine=(
                simulation_engine
            ),
            forecasting_engine=(
                forecasting_engine
            ),
            evolution_engine=(
                evolution_engine
            ),
            war_gaming_engine=(
                war_gaming_engine
            ),
            battle_management_engine=(
                battle_management_engine
            ),
            adversarial_reasoning_engine=(
                adversarial_reasoning_engine
            ),
            autonomous_defense_director=(
                autonomous_defense_director
            ),
            operational_governor=(
                operational_governor
            ),
            sovereignty_assurance_engine=(
                sovereignty_assurance_engine
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
