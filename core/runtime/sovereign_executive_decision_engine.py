"""
core/runtime/sovereign_executive_decision_engine.py

Sovereign Executive Decision Engine

Sovereign executive strategic decision layer.

Synthesizes:
- strategic operational priorities
- survivability pathways
- sovereignty preservation pathways
- continuity restoration pathways
- resilience stabilization pathways
- escalation containment pathways
- strategic recovery sequencing

Produces:
- executive operational directives
- strategic stabilization sequencing
- recovery coordination sequencing
- replayable executive decision lineage
- governance-grade executive rationale

IMPORTANT:
This subsystem DOES NOT:
- autonomously execute destructive actions
- bypass governance
- override sovereignty controls
- mutate infrastructure directly

It ONLY:
- synthesize executive strategic cognition
- prioritize strategic pathways
- coordinate executive sequencing
- produce governance-grade decision rationale
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_executive_decision_engine"
)

DEFAULT_EXECUTION_DEPTH = 10


EXECUTIVE_STATE_STABLE = "STABLE"

EXECUTIVE_STATE_MONITORING = (
    "MONITORING"
)

EXECUTIVE_STATE_ELEVATED = (
    "ELEVATED"
)

EXECUTIVE_STATE_ESCALATION = (
    "ESCALATION"
)

EXECUTIVE_STATE_CONTINUITY_CRITICAL = (
    "CONTINUITY_CRITICAL"
)

EXECUTIVE_STATE_SOVEREIGNTY_CRITICAL = (
    "SOVEREIGNTY_CRITICAL"
)

EXECUTIVE_STATE_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

EXECUTIVE_STATE_GLOBAL_CRITICAL = (
    "GLOBAL_CRITICAL"
)


PATHWAY_SURVIVABILITY = (
    "SURVIVABILITY"
)

PATHWAY_CONTINUITY = (
    "CONTINUITY"
)

PATHWAY_SOVEREIGNTY = (
    "SOVEREIGNTY"
)

PATHWAY_RESILIENCE = (
    "RESILIENCE"
)

PATHWAY_ESCALATION_CONTAINMENT = (
    "ESCALATION_CONTAINMENT"
)

PATHWAY_RECOVERY = (
    "RECOVERY"
)

PATHWAY_GLOBAL_STABILIZATION = (
    "GLOBAL_STABILIZATION"
)


DIRECTIVE_MONITOR = "MONITOR"

DIRECTIVE_COMMAND_HARDENING = (
    "COMMAND_HARDENING"
)

DIRECTIVE_ESCALATION_CONTAINMENT = (
    "ESCALATION_CONTAINMENT"
)

DIRECTIVE_CONTINUITY_RESTORATION = (
    "CONTINUITY_RESTORATION"
)

DIRECTIVE_SOVEREIGNTY_STABILIZATION = (
    "SOVEREIGNTY_STABILIZATION"
)

DIRECTIVE_RESILIENCE_SURGE = (
    "RESILIENCE_SURGE"
)

DIRECTIVE_STRATEGIC_RECOVERY = (
    "STRATEGIC_RECOVERY"
)

DIRECTIVE_GLOBAL_STABILIZATION = (
    "GLOBAL_STABILIZATION"
)


class ExecutiveSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ExecutiveDecisionSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    strategic_risk_score: float = 0.0
    continuity_risk_score: float = 0.0
    sovereignty_risk_score: float = 0.0
    escalation_risk_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    resilience_exhaustion_score: float = 0.0

    survivability_score: float = 100.0
    recovery_capacity_score: float = 100.0

    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class ExecutivePathway:
    pathway_id: str

    pathway_name: str

    priority: str

    expected_survivability_gain: float
    expected_recovery_gain: float
    expected_sovereignty_gain: float
    expected_continuity_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ExecutiveDirective:
    directive_id: str

    directive_name: str

    action_type: str

    priority: str

    sequencing_order: int

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ExecutiveDecisionProjection:
    projection_id: str

    projected_state: str

    primary_pathway: str

    survivability_projection_score: float
    recovery_projection_score: float
    sovereignty_projection_score: float
    continuity_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ExecutiveDecisionForecastStep:
    step_id: str

    step_index: int

    executive_state: str

    selected_pathway: str

    strategic_risk_score: float
    survivability_score: float
    recovery_capacity_score: float
    sovereignty_risk_score: float
    continuity_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignExecutiveDecisionAssessment:
    assessment_id: str

    executive_state: str

    selected_pathway: str

    primary_directive: str

    strategic_risk_score: float
    continuity_risk_score: float
    sovereignty_risk_score: float
    escalation_risk_score: float
    geopolitical_risk_score: float
    resilience_exhaustion_score: float

    survivability_score: float
    recovery_capacity_score: float

    uncertainty_score: float

    systemic_risk_probability: float
    recovery_probability: float

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
        ExecutiveDecisionProjection
    )

    pathways: List[
        ExecutivePathway
    ]

    directives: List[
        ExecutiveDirective
    ]

    forecast_steps: List[
        ExecutiveDecisionForecastStep
    ]

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


class SovereignExecutiveDecisionEngine:
    """
    Sovereign executive strategic governance cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        strategic_synthesis_engine: Optional[
            Any
        ] = None,
        global_risk_forecasting_engine: Optional[
            Any
        ] = None,
        global_command_integrator: Optional[
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

        self.strategic_synthesis_engine = (
            strategic_synthesis_engine
        )

        self.global_risk_forecasting_engine = (
            global_risk_forecasting_engine
        )

        self.global_command_integrator = (
            global_command_integrator
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
            SovereignExecutiveDecisionAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            ExecutiveDecisionSignal
            | Dict[str, Any]
        ],
        *,
        execution_depth: int = (
            DEFAULT_EXECUTION_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignExecutiveDecisionAssessment
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

        selected = self._select_primary_signal(
            normalized
        )

        strategic_risk = self._avg_score(
            [
                s.strategic_risk_score
                for s in normalized
            ]
        )

        continuity_risk = self._avg_score(
            [
                s.continuity_risk_score
                for s in normalized
            ]
        )

        sovereignty_risk = self._avg_score(
            [
                s.sovereignty_risk_score
                for s in normalized
            ]
        )

        escalation_risk = self._avg_score(
            [
                s.escalation_risk_score
                for s in normalized
            ]
        )

        geopolitical_risk = self._avg_score(
            [
                s.geopolitical_risk_score
                for s in normalized
            ]
        )

        resilience_exhaustion = (
            self._avg_score(
                [
                    s
                    .resilience_exhaustion_score
                    for s in normalized
                ]
            )
        )

        survivability = self._avg_score(
            [
                s.survivability_score
                for s in normalized
            ],
            default=100.0,
        )

        recovery_capacity = (
            self._avg_score(
                [
                    s.recovery_capacity_score
                    for s in normalized
                ],
                default=100.0,
            )
        )

        uncertainty = self._avg_score(
            [
                s.uncertainty_score
                for s in normalized
            ]
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                strategic_risk_score=(
                    strategic_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        recovery_probability = (
            self._recovery_probability(
                survivability_score=(
                    survivability
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
            )
        )

        executive_state = (
            self._executive_state(
                strategic_risk_score=(
                    strategic_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                survivability_score=(
                    survivability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        selected_pathway = (
            self._select_pathway(
                executive_state=(
                    executive_state
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                recovery_probability=(
                    recovery_probability
                ),
            )
        )

        primary_directive = (
            self._primary_directive(
                selected_pathway=(
                    selected_pathway
                ),
                executive_state=(
                    executive_state
                ),
            )
        )

        projection = self._projection(
            executive_state=(
                executive_state
            ),
            selected_pathway=(
                selected_pathway
            ),
            survivability_score=(
                survivability
            ),
            recovery_capacity_score=(
                recovery_capacity
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
        )

        pathways = self._pathways(
            selected_pathway=(
                selected_pathway
            ),
            survivability_score=(
                survivability
            ),
            recovery_capacity_score=(
                recovery_capacity
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
        )

        directives = self._directives(
            primary_directive=(
                primary_directive
            ),
            selected_pathway=(
                selected_pathway
            ),
        )

        forecast_steps = (
            self._forecast_steps(
                executive_state=(
                    executive_state
                ),
                selected_pathway=(
                    selected_pathway
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                survivability_score=(
                    survivability
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                depth=execution_depth,
            )
        )

        assessment = (
            SovereignExecutiveDecisionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                executive_state=(
                    executive_state
                ),
                selected_pathway=(
                    selected_pathway
                ),
                primary_directive=(
                    primary_directive
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                survivability_score=(
                    survivability
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                uncertainty_score=(
                    uncertainty
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                recovery_probability=(
                    recovery_probability
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
                pathways=pathways,
                directives=(
                    directives
                ),
                forecast_steps=(
                    forecast_steps
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        normalized
                    )
                ),
                rationale=(
                    self._rationale(
                        executive_state=(
                            executive_state
                        ),
                        selected_pathway=(
                            selected_pathway
                        ),
                        primary_directive=(
                            primary_directive
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
    # STATE
    # ==========================================================

    @staticmethod
    def _executive_state(
        *,
        strategic_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        survivability_score: float,
        systemic_risk_probability: float,
    ) -> str:

        if (
            strategic_risk_score >= 85
            or survivability_score <= 30
        ):
            return (
                EXECUTIVE_STATE_GLOBAL_CRITICAL
            )

        if systemic_risk_probability >= 0.75:
            return (
                EXECUTIVE_STATE_SYSTEMIC_RISK
            )

        if sovereignty_risk_score >= 70:
            return (
                EXECUTIVE_STATE_SOVEREIGNTY_CRITICAL
            )

        if continuity_risk_score >= 70:
            return (
                EXECUTIVE_STATE_CONTINUITY_CRITICAL
            )

        if escalation_risk_score >= 65:
            return (
                EXECUTIVE_STATE_ESCALATION
            )

        if strategic_risk_score >= 50:
            return (
                EXECUTIVE_STATE_ELEVATED
            )

        if strategic_risk_score >= 25:
            return (
                EXECUTIVE_STATE_MONITORING
            )

        return EXECUTIVE_STATE_STABLE

    # ==========================================================
    # PATHWAYS
    # ==========================================================

    @staticmethod
    def _select_pathway(
        *,
        executive_state: str,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        recovery_probability: float,
    ) -> str:

        if (
            executive_state
            == EXECUTIVE_STATE_GLOBAL_CRITICAL
        ):
            return (
                PATHWAY_GLOBAL_STABILIZATION
            )

        if sovereignty_risk_score >= 70:
            return (
                PATHWAY_SOVEREIGNTY
            )

        if continuity_risk_score >= 70:
            return (
                PATHWAY_CONTINUITY
            )

        if escalation_risk_score >= 65:
            return (
                PATHWAY_ESCALATION_CONTAINMENT
            )

        if recovery_probability >= 0.75:
            return PATHWAY_RECOVERY

        return PATHWAY_SURVIVABILITY

    # ==========================================================
    # DIRECTIVES
    # ==========================================================

    @staticmethod
    def _primary_directive(
        *,
        selected_pathway: str,
        executive_state: str,
    ) -> str:

        if (
            executive_state
            == EXECUTIVE_STATE_GLOBAL_CRITICAL
        ):
            return (
                DIRECTIVE_GLOBAL_STABILIZATION
            )

        mapping = {
            PATHWAY_SURVIVABILITY: (
                DIRECTIVE_COMMAND_HARDENING
            ),
            PATHWAY_CONTINUITY: (
                DIRECTIVE_CONTINUITY_RESTORATION
            ),
            PATHWAY_SOVEREIGNTY: (
                DIRECTIVE_SOVEREIGNTY_STABILIZATION
            ),
            PATHWAY_ESCALATION_CONTAINMENT: (
                DIRECTIVE_ESCALATION_CONTAINMENT
            ),
            PATHWAY_RECOVERY: (
                DIRECTIVE_STRATEGIC_RECOVERY
            ),
            PATHWAY_GLOBAL_STABILIZATION: (
                DIRECTIVE_GLOBAL_STABILIZATION
            ),
            PATHWAY_RESILIENCE: (
                DIRECTIVE_RESILIENCE_SURGE
            ),
        }

        return mapping.get(
            selected_pathway,
            DIRECTIVE_MONITOR,
        )

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        executive_state: str,
        selected_pathway: str,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> ExecutiveDecisionProjection:

        return ExecutiveDecisionProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                executive_state
            ),
            primary_pathway=(
                selected_pathway
            ),
            survivability_projection_score=(
                survivability_score
            ),
            recovery_projection_score=(
                recovery_capacity_score
            ),
            sovereignty_projection_score=(
                100.0
                - sovereignty_risk_score
            ),
            continuity_projection_score=(
                100.0
                - continuity_risk_score
            ),
            rationale=(
                f"Executive decision "
                f"projection selected "
                f"{selected_pathway}."
            ),
        )

    # ==========================================================
    # PATHWAY OBJECTS
    # ==========================================================

    def _pathways(
        self,
        *,
        selected_pathway: str,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> List[
        ExecutivePathway
    ]:

        return [
            ExecutivePathway(
                pathway_id=str(
                    uuid.uuid4()
                ),
                pathway_name=(
                    selected_pathway
                ),
                priority="HIGH",
                expected_survivability_gain=(
                    max(
                        0.0,
                        100.0
                        - survivability_score,
                    )
                    * 0.25
                ),
                expected_recovery_gain=(
                    max(
                        0.0,
                        100.0
                        - recovery_capacity_score,
                    )
                    * 0.25
                ),
                expected_sovereignty_gain=(
                    sovereignty_risk_score
                    * 0.25
                ),
                expected_continuity_gain=(
                    continuity_risk_score
                    * 0.25
                ),
                rationale=(
                    f"Executive pathway "
                    f"{selected_pathway} "
                    f"selected."
                ),
            )
        ]

    # ==========================================================
    # DIRECTIVE OBJECTS
    # ==========================================================

    def _directives(
        self,
        *,
        primary_directive: str,
        selected_pathway: str,
    ) -> List[
        ExecutiveDirective
    ]:

        return [
            ExecutiveDirective(
                directive_id=str(
                    uuid.uuid4()
                ),
                directive_name=(
                    primary_directive
                ),
                action_type=(
                    selected_pathway
                ),
                priority="CRITICAL",
                sequencing_order=1,
                rationale=(
                    f"Primary executive "
                    f"directive "
                    f"{primary_directive}."
                ),
            )
        ]

    # ==========================================================
    # FORECASTING
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        executive_state: str,
        selected_pathway: str,
        strategic_risk_score: float,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        depth: int,
    ) -> List[
        ExecutiveDecisionForecastStep
    ]:

        steps = []

        for idx in range(
            max(1, int(depth))
        ):

            steps.append(
                ExecutiveDecisionForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    executive_state=(
                        executive_state
                    ),
                    selected_pathway=(
                        selected_pathway
                    ),
                    strategic_risk_score=(
                        strategic_risk_score
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    recovery_capacity_score=(
                        recovery_capacity_score
                    ),
                    sovereignty_risk_score=(
                        sovereignty_risk_score
                    ),
                    continuity_risk_score=(
                        continuity_risk_score
                    ),
                    rationale=(
                        f"Executive "
                        f"forecast step "
                        f"{idx}."
                    ),
                )
            )

            strategic_risk_score = (
                self._clamp_score(
                    strategic_risk_score
                    - 0.8
                )
            )

            survivability_score = (
                self._clamp_score(
                    survivability_score
                    + 0.8
                )
            )

            recovery_capacity_score = (
                self._clamp_score(
                    recovery_capacity_score
                    + 0.8
                )
            )

            sovereignty_risk_score = (
                self._clamp_score(
                    sovereignty_risk_score
                    - 0.8
                )
            )

            continuity_risk_score = (
                self._clamp_score(
                    continuity_risk_score
                    - 0.8
                )
            )

        return steps

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignExecutiveDecisionAssessment
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

        self._write_memory(payload)

        self._write_lineage(payload)

        self._write_evidence(payload)

        self._emit_event(payload)

    def _write_memory(
        self,
        payload: Dict[str, Any],
    ) -> None:

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
                f"⚠️ Executive "
                f"memory write failed: "
                f"{exc}"
            )

    def _write_lineage(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.lineage_engine
                and hasattr(
                    self.lineage_engine,
                    "record_lineage",
                )
            ):
                self.lineage_engine.record_lineage(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Executive "
                f"lineage write failed: "
                f"{exc}"
            )

    def _write_evidence(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.fedramp_evidence_lineage_engine
                and hasattr(
                    self
                    .fedramp_evidence_lineage_engine,
                    "record_evidence",
                )
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Executive "
                f"evidence write failed: "
                f"{exc}"
            )

    def _emit_event(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.event_bus
                and hasattr(
                    self.event_bus,
                    "emit",
                )
            ):
                self.event_bus.emit(
                    "SOVEREIGN_EXECUTIVE_DECISION",
                    payload,
                )

        except Exception as exc:

            print(
                f"⚠️ Executive "
                f"event emit failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _systemic_risk_probability(
        self,
        *,
        strategic_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        geopolitical_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        value = (
            strategic_risk_score
            + continuity_risk_score
            + sovereignty_risk_score
            + escalation_risk_score
            + geopolitical_risk_score
            + uncertainty_score
        ) / 600.0

        return self._clamp_probability(
            value
        )

    def _recovery_probability(
        self,
        *,
        survivability_score: float,
        recovery_capacity_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        resilience_exhaustion_score: float,
    ) -> float:

        value = (
            survivability_score
            + recovery_capacity_score
            + (
                100.0
                - continuity_risk_score
            )
            + (
                100.0
                - sovereignty_risk_score
            )
            + (
                100.0
                - resilience_exhaustion_score
            )
        ) / 500.0

        return self._clamp_probability(
            value
        )

    def _normalize_signal(
        self,
        item: (
            ExecutiveDecisionSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> ExecutiveDecisionSignal:

        if isinstance(
            item,
            ExecutiveDecisionSignal,
        ):
            return item

        return ExecutiveDecisionSignal(
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
            severity=self._safe_severity(
                item.get("severity")
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
            strategic_risk_score=self._clamp_score(
                item.get(
                    "strategic_risk_score",
                    0.0,
                )
            ),
            continuity_risk_score=self._clamp_score(
                item.get(
                    "continuity_risk_score",
                    0.0,
                )
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get(
                    "sovereignty_risk_score",
                    0.0,
                )
            ),
            escalation_risk_score=self._clamp_score(
                item.get(
                    "escalation_risk_score",
                    0.0,
                )
            ),
            geopolitical_risk_score=self._clamp_score(
                item.get(
                    "geopolitical_risk_score",
                    0.0,
                )
            ),
            resilience_exhaustion_score=self._clamp_score(
                item.get(
                    "resilience_exhaustion_score",
                    0.0,
                )
            ),
            survivability_score=self._clamp_score(
                item.get(
                    "survivability_score",
                    100.0,
                )
            ),
            recovery_capacity_score=self._clamp_score(
                item.get(
                    "recovery_capacity_score",
                    100.0,
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
                or {}
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
        SovereignExecutiveDecisionAssessment
    ):

        projection = (
            ExecutiveDecisionProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projected_state=(
                    EXECUTIVE_STATE_STABLE
                ),
                primary_pathway=(
                    PATHWAY_SURVIVABILITY
                ),
                survivability_projection_score=100.0,
                recovery_projection_score=100.0,
                sovereignty_projection_score=100.0,
                continuity_projection_score=100.0,
                rationale=(
                    "No executive "
                    "signals submitted."
                ),
            )
        )

        return (
            SovereignExecutiveDecisionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                executive_state=(
                    EXECUTIVE_STATE_STABLE
                ),
                selected_pathway=(
                    PATHWAY_SURVIVABILITY
                ),
                primary_directive=(
                    DIRECTIVE_MONITOR
                ),
                strategic_risk_score=0.0,
                continuity_risk_score=0.0,
                sovereignty_risk_score=0.0,
                escalation_risk_score=0.0,
                geopolitical_risk_score=0.0,
                resilience_exhaustion_score=0.0,
                survivability_score=100.0,
                recovery_capacity_score=100.0,
                uncertainty_score=0.0,
                systemic_risk_probability=0.0,
                recovery_probability=1.0,
                confidence=1.0,
                explainability_score=100.0,
                signal_count=0,
                engine_count=0,
                severity=(
                    ExecutiveSeverity.INFO.value
                ),
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                strategic_projection=(
                    projection
                ),
                pathways=[],
                directives=[],
                forecast_steps=[],
                telemetry_fusion={},
                rationale=(
                    "No executive "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            ExecutiveDecisionSignal
        ],
    ) -> ExecutiveDecisionSignal:

        return sorted(
            signals,
            key=lambda item: (
                item.strategic_risk_score,
                item.sovereignty_risk_score,
                item.continuity_risk_score,
                item.escalation_risk_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[
            ExecutiveDecisionSignal
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

    def _confidence(
        self,
        signals: Sequence[
            ExecutiveDecisionSignal
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
            ExecutiveDecisionSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        explained = 0

        for signal in signals:

            if signal.summary:
                explained += 1

            if signal.source_engine:
                explained += 1

            if signal.payload:
                explained += 1

        return self._clamp_score(
            (
                explained
                / (len(signals) * 3)
            )
            * 100.0
        )

    @staticmethod
    def _rationale(
        *,
        executive_state: str,
        selected_pathway: str,
        primary_directive: str,
    ) -> str:

        return (
            f"Sovereign executive "
            f"decision completed. "
            f"Executive state "
            f"{executive_state}; "
            f"pathway "
            f"{selected_pathway}; "
            f"directive "
            f"{primary_directive}."
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or ExecutiveSeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in ExecutiveSeverity
        }

        return (
            value
            if value in valid
            else ExecutiveSeverity.INFO.value
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


def build_sovereign_executive_decision_engine(
    *,
    event_bus: Optional[Any] = None,
    strategic_synthesis_engine: Optional[
        Any
    ] = None,
    global_risk_forecasting_engine: Optional[
        Any
    ] = None,
    global_command_integrator: Optional[
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
) -> (
    SovereignExecutiveDecisionEngine
):

    return (
        SovereignExecutiveDecisionEngine(
            event_bus=event_bus,
            strategic_synthesis_engine=(
                strategic_synthesis_engine
            ),
            global_risk_forecasting_engine=(
                global_risk_forecasting_engine
            ),
            global_command_integrator=(
                global_command_integrator
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