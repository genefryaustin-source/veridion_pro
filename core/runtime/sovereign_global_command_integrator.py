"""
core/runtime/sovereign_global_command_integrator.py

Sovereign Global Command Integrator

Global sovereign operational command aggregation layer.

Unifies:
- distributed runtime cognition
- adaptive sovereign mesh cognition
- ecosystem resilience cognition
- geopolitical resilience cognition
- sovereignty assurance cognition
- operational governance cognition
- command-center operational intelligence

Produces:
- global command state
- global sovereignty posture
- global continuity posture
- global resilience posture
- global escalation posture
- global strategic operational projection
- replayable command lineage/evidence

IMPORTANT:
This subsystem DOES NOT:
- directly execute operations
- bypass governance
- modify infrastructure
- perform offensive actions

It ONLY:
- aggregate sovereign operational intelligence
- correlate global operational posture
- project command-level survivability
- provide replayable command cognition
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_global_command_integrator"
)

DEFAULT_FORECAST_DEPTH = 12


GLOBAL_COMMAND_STATE_STABLE = (
    "STABLE"
)

GLOBAL_COMMAND_STATE_MONITORING = (
    "MONITORING"
)

GLOBAL_COMMAND_STATE_HEIGHTENED_AWARENESS = (
    "HEIGHTENED_AWARENESS"
)

GLOBAL_COMMAND_STATE_CONTINUITY_PRESSURE = (
    "CONTINUITY_PRESSURE"
)

GLOBAL_COMMAND_STATE_SOVEREIGNTY_PRESSURE = (
    "SOVEREIGNTY_PRESSURE"
)

GLOBAL_COMMAND_STATE_ESCALATION_RISK = (
    "ESCALATION_RISK"
)

GLOBAL_COMMAND_STATE_GLOBAL_CRITICAL = (
    "GLOBAL_CRITICAL"
)

PROJECTION_STABLE = "STABLE"

PROJECTION_RESILIENCE_RECOVERY = (
    "RESILIENCE_RECOVERY"
)

PROJECTION_CONTINUITY_RESTORATION = (
    "CONTINUITY_RESTORATION"
)

PROJECTION_SOVEREIGN_STABILIZATION = (
    "SOVEREIGN_STABILIZATION"
)

PROJECTION_GLOBAL_HARDENING = (
    "GLOBAL_HARDENING"
)

PROJECTION_ESCALATION_CONTAINMENT = (
    "ESCALATION_CONTAINMENT"
)

PROJECTION_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

ACTION_MONITOR = "MONITOR"

ACTION_REBALANCE_CONTINUITY = (
    "REBALANCE_CONTINUITY"
)

ACTION_REINFORCE_SOVEREIGNTY = (
    "REINFORCE_SOVEREIGNTY"
)

ACTION_GLOBAL_RESILIENCE_SURGE = (
    "GLOBAL_RESILIENCE_SURGE"
)

ACTION_ESCALATION_CONTAINMENT = (
    "ESCALATION_CONTAINMENT"
)

ACTION_COMMAND_HARDENING = (
    "COMMAND_HARDENING"
)


class GlobalSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class GlobalOperationalSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    survivability_score: float = (
        100.0
    )

    continuity_score: float = (
        100.0
    )

    sovereignty_score: float = (
        100.0
    )

    resilience_score: float = (
        100.0
    )

    escalation_risk_score: float = (
        0.0
    )

    geopolitical_pressure_score: float = (
        0.0
    )

    ecosystem_risk_score: float = (
        0.0
    )

    mesh_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
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
class GlobalCommandProjection:
    projection_id: str

    projected_state: str

    survivability_projection_score: float
    continuity_projection_score: float
    sovereignty_projection_score: float
    resilience_projection_score: float
    escalation_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GlobalCommandForecastStep:
    step_id: str

    step_index: int

    projected_state: str

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float

    escalation_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GlobalCommandDirective:
    directive_id: str

    directive_name: str

    action_type: str
    priority: str

    expected_survivability_gain: float
    expected_continuity_gain: float
    expected_sovereignty_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignGlobalCommandAssessment:
    assessment_id: str

    global_command_state: str

    recommended_action: str

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float

    escalation_risk_score: float
    geopolitical_pressure_score: float
    ecosystem_risk_score: float
    mesh_risk_score: float
    uncertainty_score: float

    global_risk_score: float

    confidence: float
    explainability_score: float

    signal_count: int
    engine_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    strategic_projection: (
        GlobalCommandProjection
    )

    forecast_steps: List[
        GlobalCommandForecastStep
    ]

    directives: List[
        GlobalCommandDirective
    ]

    operational_topology: Dict[str, Any]

    telemetry_fusion: Dict[str, Any]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


class SovereignGlobalCommandIntegrator:
    """
    Global sovereign operational aggregation layer.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        geopolitical_resilience_engine: Optional[
            Any
        ] = None,
        ecosystem_resilience_engine: Optional[
            Any
        ] = None,
        mesh_autonomy_engine: Optional[
            Any
        ] = None,
        sovereignty_assurance_engine: Optional[
            Any
        ] = None,
        operational_governor: Optional[
            Any
        ] = None,
        command_center_copilot: Optional[
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

        self.geopolitical_resilience_engine = (
            geopolitical_resilience_engine
        )

        self.ecosystem_resilience_engine = (
            ecosystem_resilience_engine
        )

        self.mesh_autonomy_engine = (
            mesh_autonomy_engine
        )

        self.sovereignty_assurance_engine = (
            sovereignty_assurance_engine
        )

        self.operational_governor = (
            operational_governor
        )

        self.command_center_copilot = (
            command_center_copilot
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignGlobalCommandAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            GlobalOperationalSignal
            | Dict[str, Any]
        ],
        *,
        forecast_depth: int = (
            DEFAULT_FORECAST_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignGlobalCommandAssessment
    ):

        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
            )
            for item in signals
        ]

        if not normalized:

            assessment = (
                self._empty_assessment(
                    tenant_id=tenant_id,
                    mission_id=mission_id,
                    case_id=case_id,
                    correlation_id=(
                        correlation_id
                    ),
                )
            )

            self._record_assessment(
                assessment,
                context=context,
            )

            return assessment

        selected = normalized[0]

        survivability = (
            self._avg_score(
                [
                    s.survivability_score
                    for s in normalized
                ],
                default=100.0,
            )
        )

        continuity = (
            self._avg_score(
                [
                    s.continuity_score
                    for s in normalized
                ],
                default=100.0,
            )
        )

        sovereignty = (
            self._avg_score(
                [
                    s.sovereignty_score
                    for s in normalized
                ],
                default=100.0,
            )
        )

        resilience = (
            self._avg_score(
                [
                    s.resilience_score
                    for s in normalized
                ],
                default=100.0,
            )
        )

        escalation_risk = (
            self._avg_score(
                [
                    s
                    .escalation_risk_score
                    for s in normalized
                ]
            )
        )

        geopolitical_pressure = (
            self._avg_score(
                [
                    s
                    .geopolitical_pressure_score
                    for s in normalized
                ]
            )
        )

        ecosystem_risk = (
            self._avg_score(
                [
                    s
                    .ecosystem_risk_score
                    for s in normalized
                ]
            )
        )

        mesh_risk = (
            self._avg_score(
                [
                    s.mesh_risk_score
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

        global_risk = (
            self._global_risk_score(
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_pressure_score=(
                    geopolitical_pressure
                ),
                ecosystem_risk_score=(
                    ecosystem_risk
                ),
                mesh_risk_score=(
                    mesh_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        global_state = (
            self._global_state(
                global_risk_score=(
                    global_risk
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
            )
        )

        recommended_action = (
            self._recommended_action(
                global_command_state=(
                    global_state
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                sovereignty_score=(
                    sovereignty
                ),
                continuity_score=(
                    continuity
                ),
            )
        )

        projection = (
            self._projection(
                global_command_state=(
                    global_state
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                resilience_score=(
                    resilience
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
            )
        )

        directives = (
            self._directives(
                recommended_action=(
                    recommended_action
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
            )
        )

        forecast_steps = (
            self._forecast_steps(
                global_command_state=(
                    global_state
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                resilience_score=(
                    resilience
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                depth=forecast_depth,
            )
        )

        assessment = (
            SovereignGlobalCommandAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                global_command_state=(
                    global_state
                ),
                recommended_action=(
                    recommended_action
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                resilience_score=(
                    resilience
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_pressure_score=(
                    geopolitical_pressure
                ),
                ecosystem_risk_score=(
                    ecosystem_risk
                ),
                mesh_risk_score=(
                    mesh_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                global_risk_score=(
                    global_risk
                ),
                confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                signal_count=len(
                    normalized
                ),
                engine_count=len(
                    {
                        s.source_engine
                        for s in normalized
                    }
                ),
                severity=(
                    selected.severity
                ),
                tenant_id=(
                    tenant_id
                    or selected
                    .tenant_id
                ),
                mission_id=(
                    mission_id
                    or selected
                    .mission_id
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
                forecast_steps=(
                    forecast_steps
                ),
                directives=(
                    directives
                ),
                operational_topology=(
                    self
                    ._operational_topology(
                        normalized
                    )
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        normalized
                    )
                ),
                rationale=(
                    self._rationale(
                        global_command_state=(
                            global_state
                        ),
                        recommended_action=(
                            recommended_action
                        ),
                        global_risk_score=(
                            global_risk
                        ),
                    )
                ),
                metadata={
                    "engines": sorted(
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
    def _global_state(
        *,
        global_risk_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        escalation_risk_score: float,
    ) -> str:

        if (
            global_risk_score >= 85
            or survivability_score <= 30
        ):
            return (
                GLOBAL_COMMAND_STATE_GLOBAL_CRITICAL
            )

        if escalation_risk_score >= 75:
            return (
                GLOBAL_COMMAND_STATE_ESCALATION_RISK
            )

        if sovereignty_score <= 45:
            return (
                GLOBAL_COMMAND_STATE_SOVEREIGNTY_PRESSURE
            )

        if continuity_score <= 45:
            return (
                GLOBAL_COMMAND_STATE_CONTINUITY_PRESSURE
            )

        if global_risk_score >= 60:
            return (
                GLOBAL_COMMAND_STATE_HEIGHTENED_AWARENESS
            )

        if global_risk_score >= 20:
            return (
                GLOBAL_COMMAND_STATE_MONITORING
            )

        return GLOBAL_COMMAND_STATE_STABLE

    # ==========================================================
    # ACTIONS
    # ==========================================================

    @staticmethod
    def _recommended_action(
        *,
        global_command_state: str,
        escalation_risk_score: float,
        sovereignty_score: float,
        continuity_score: float,
    ) -> str:

        if (
            global_command_state
            == GLOBAL_COMMAND_STATE_GLOBAL_CRITICAL
        ):
            return (
                ACTION_GLOBAL_RESILIENCE_SURGE
            )

        if escalation_risk_score >= 70:
            return (
                ACTION_ESCALATION_CONTAINMENT
            )

        if sovereignty_score <= 50:
            return (
                ACTION_REINFORCE_SOVEREIGNTY
            )

        if continuity_score <= 50:
            return (
                ACTION_REBALANCE_CONTINUITY
            )

        if (
            global_command_state
            == GLOBAL_COMMAND_STATE_HEIGHTENED_AWARENESS
        ):
            return (
                ACTION_COMMAND_HARDENING
            )

        return ACTION_MONITOR

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        global_command_state: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        escalation_risk_score: float,
    ) -> GlobalCommandProjection:

        state = PROJECTION_STABLE

        if (
            global_command_state
            == GLOBAL_COMMAND_STATE_GLOBAL_CRITICAL
        ):
            state = (
                PROJECTION_SYSTEMIC_RISK
            )

        elif escalation_risk_score >= 70:
            state = (
                PROJECTION_ESCALATION_CONTAINMENT
            )

        elif sovereignty_score <= 50:
            state = (
                PROJECTION_SOVEREIGN_STABILIZATION
            )

        elif continuity_score <= 50:
            state = (
                PROJECTION_CONTINUITY_RESTORATION
            )

        elif resilience_score <= 60:
            state = (
                PROJECTION_RESILIENCE_RECOVERY
            )

        else:
            state = (
                PROJECTION_GLOBAL_HARDENING
            )

        return GlobalCommandProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=state,
            survivability_projection_score=(
                survivability_score
            ),
            continuity_projection_score=(
                continuity_score
            ),
            sovereignty_projection_score=(
                sovereignty_score
            ),
            resilience_projection_score=(
                resilience_score
            ),
            escalation_projection_score=(
                escalation_risk_score
            ),
            rationale=(
                f"Global command "
                f"projection state "
                f"{state}."
            ),
        )

    # ==========================================================
    # DIRECTIVES
    # ==========================================================

    def _directives(
        self,
        *,
        recommended_action: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
    ) -> List[
        GlobalCommandDirective
    ]:

        return [
            GlobalCommandDirective(
                directive_id=str(
                    uuid.uuid4()
                ),
                directive_name=(
                    recommended_action.lower()
                ),
                action_type=(
                    recommended_action
                ),
                priority=(
                    "HIGH"
                    if recommended_action
                    != ACTION_MONITOR
                    else "LOW"
                ),
                expected_survivability_gain=(
                    max(
                        0.0,
                        100.0
                        - survivability_score,
                    )
                    * 0.25
                ),
                expected_continuity_gain=(
                    max(
                        0.0,
                        100.0
                        - continuity_score,
                    )
                    * 0.25
                ),
                expected_sovereignty_gain=(
                    max(
                        0.0,
                        100.0
                        - sovereignty_score,
                    )
                    * 0.25
                ),
                rationale=(
                    f"Recommended global "
                    f"command action "
                    f"{recommended_action}."
                ),
            )
        ]

    # ==========================================================
    # FORECASTING
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        global_command_state: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        escalation_risk_score: float,
        depth: int,
    ) -> List[
        GlobalCommandForecastStep
    ]:

        steps = []

        for idx in range(max(1, depth)):

            steps.append(
                GlobalCommandForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        global_command_state
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    continuity_score=(
                        continuity_score
                    ),
                    sovereignty_score=(
                        sovereignty_score
                    ),
                    resilience_score=(
                        resilience_score
                    ),
                    escalation_risk_score=(
                        escalation_risk_score
                    ),
                    rationale=(
                        f"Global command "
                        f"forecast step "
                        f"{idx}."
                    ),
                )
            )

            survivability_score = (
                self._clamp_score(
                    survivability_score
                    + 1.0
                )
            )

            continuity_score = (
                self._clamp_score(
                    continuity_score
                    + 1.0
                )
            )

            sovereignty_score = (
                self._clamp_score(
                    sovereignty_score
                    + 0.8
                )
            )

            resilience_score = (
                self._clamp_score(
                    resilience_score
                    + 0.8
                )
            )

            escalation_risk_score = (
                self._clamp_score(
                    escalation_risk_score
                    - 1.0
                )
            )

        return steps

    # ==========================================================
    # TOPOLOGY
    # ==========================================================

    def _operational_topology(
        self,
        signals: Sequence[
            GlobalOperationalSignal
        ],
    ) -> Dict[str, Any]:

        return {
            "signal_count": len(
                signals
            ),
            "engines": sorted(
                {
                    s.source_engine
                    for s in signals
                }
            ),
        }

    def _telemetry_fusion(
        self,
        signals: Sequence[
            GlobalOperationalSignal
        ],
    ) -> Dict[str, Any]:

        return {
            "signal_count": len(
                signals
            ),
            "source_engines": sorted(
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
            SovereignGlobalCommandAssessment
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
                f"⚠️ Global command "
                f"memory write failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _global_risk_score(
        self,
        *,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        escalation_risk_score: float,
        geopolitical_pressure_score: float,
        ecosystem_risk_score: float,
        mesh_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        risk = (
            escalation_risk_score
            + geopolitical_pressure_score
            + ecosystem_risk_score
            + mesh_risk_score
            + uncertainty_score
            + (
                100.0
                - survivability_score
            )
            + (
                100.0
                - continuity_score
            )
            + (
                100.0
                - sovereignty_score
            )
        ) / 8.0

        return self._clamp_score(
            risk
        )

    def _normalize_signal(
        self,
        item: (
            GlobalOperationalSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> GlobalOperationalSignal:

        if isinstance(
            item,
            GlobalOperationalSignal,
        ):
            return item

        return GlobalOperationalSignal(
            signal_id=str(
                item.get(
                    "signal_id"
                )
                or uuid.uuid4()
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
            confidence=self._clamp_probability(
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
            tenant_id=(
                tenant_id
                or item.get(
                    "tenant_id"
                )
            ),
            mission_id=(
                mission_id
                or item.get(
                    "mission_id"
                )
            ),
            case_id=(
                case_id
                or item.get(
                    "case_id"
                )
            ),
            correlation_id=(
                correlation_id
                or item.get(
                    "correlation_id"
                )
            ),
            survivability_score=self._clamp_score(
                item.get(
                    "survivability_score",
                    100.0,
                )
            ),
            continuity_score=self._clamp_score(
                item.get(
                    "continuity_score",
                    100.0,
                )
            ),
            sovereignty_score=self._clamp_score(
                item.get(
                    "sovereignty_score",
                    100.0,
                )
            ),
            resilience_score=self._clamp_score(
                item.get(
                    "resilience_score",
                    100.0,
                )
            ),
            escalation_risk_score=self._clamp_score(
                item.get(
                    "escalation_risk_score",
                    0.0,
                )
            ),
            geopolitical_pressure_score=self._clamp_score(
                item.get(
                    "geopolitical_pressure_score",
                    0.0,
                )
            ),
            ecosystem_risk_score=self._clamp_score(
                item.get(
                    "ecosystem_risk_score",
                    0.0,
                )
            ),
            mesh_risk_score=self._clamp_score(
                item.get(
                    "mesh_risk_score",
                    0.0,
                )
            ),
            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
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
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignGlobalCommandAssessment
    ):

        projection = (
            GlobalCommandProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projected_state=(
                    PROJECTION_STABLE
                ),
                survivability_projection_score=100.0,
                continuity_projection_score=100.0,
                sovereignty_projection_score=100.0,
                resilience_projection_score=100.0,
                escalation_projection_score=0.0,
                rationale=(
                    "No global command "
                    "signals submitted."
                ),
            )
        )

        return (
            SovereignGlobalCommandAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                global_command_state=(
                    GLOBAL_COMMAND_STATE_STABLE
                ),
                recommended_action=(
                    ACTION_MONITOR
                ),
                survivability_score=100.0,
                continuity_score=100.0,
                sovereignty_score=100.0,
                resilience_score=100.0,
                escalation_risk_score=0.0,
                geopolitical_pressure_score=0.0,
                ecosystem_risk_score=0.0,
                mesh_risk_score=0.0,
                uncertainty_score=0.0,
                global_risk_score=0.0,
                confidence=1.0,
                explainability_score=100.0,
                signal_count=0,
                engine_count=0,
                severity="INFO",
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                strategic_projection=(
                    projection
                ),
                forecast_steps=[],
                directives=[],
                operational_topology={},
                telemetry_fusion={},
                rationale=(
                    "No global command "
                    "signals submitted."
                ),
            )
        )

    def _confidence(
        self,
        signals: Sequence[
            GlobalOperationalSignal
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
            GlobalOperationalSignal
        ],
    ) -> float:

        explained = 0

        for signal in signals:

            if signal.summary:
                explained += 1

            if signal.source_engine:
                explained += 1

        base = (
            explained
            / max(
                1,
                len(signals) * 2,
            )
        ) * 100.0

        return self._clamp_score(base)

    @staticmethod
    def _rationale(
        *,
        global_command_state: str,
        recommended_action: str,
        global_risk_score: float,
    ) -> str:

        return (
            f"Sovereign global "
            f"command evaluation "
            f"completed. "
            f"Global state "
            f"{global_command_state}; "
            f"recommended action "
            f"{recommended_action}; "
            f"global risk score "
            f"{global_risk_score:.2f}."
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

    def _avg_score(
        self,
        values: Sequence[float],
        *,
        default: float = 0.0,
    ) -> float:

        if not values:
            return default

        return self._clamp_score(
            statistics.mean(values)
        )


def build_sovereign_global_command_integrator(
    *,
    event_bus: Optional[Any] = None,
    geopolitical_resilience_engine: Optional[
        Any
    ] = None,
    ecosystem_resilience_engine: Optional[
        Any
    ] = None,
    mesh_autonomy_engine: Optional[
        Any
    ] = None,
    sovereignty_assurance_engine: Optional[
        Any
    ] = None,
    operational_governor: Optional[
        Any
    ] = None,
    command_center_copilot: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> (
    SovereignGlobalCommandIntegrator
):

    return (
        SovereignGlobalCommandIntegrator(
            event_bus=event_bus,
            geopolitical_resilience_engine=(
                geopolitical_resilience_engine
            ),
            ecosystem_resilience_engine=(
                ecosystem_resilience_engine
            ),
            mesh_autonomy_engine=(
                mesh_autonomy_engine
            ),
            sovereignty_assurance_engine=(
                sovereignty_assurance_engine
            ),
            operational_governor=(
                operational_governor
            ),
            command_center_copilot=(
                command_center_copilot
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