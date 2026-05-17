"""
core/runtime/sovereign_execution_governance_engine.py

Sovereign Execution Governance Engine

Governance-gated sovereign operational execution cognition.

This subsystem:
- validates orchestration execution plans
- enforces governance boundaries
- enforces survivability-safe sequencing
- enforces sovereignty-safe sequencing
- enforces continuity-safe sequencing
- enforces resilience-safe sequencing
- produces replayable execution governance lineage

IMPORTANT:
This subsystem DOES NOT:
- autonomously perform destructive operations
- bypass governance approval
- override sovereignty boundaries
- mutate infrastructure directly

It ONLY:
- validate execution governance posture
- approve/deny safe sequencing
- coordinate governance-safe execution flows
- produce replayable governance rationale
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_execution_governance_engine"
)

DEFAULT_GOVERNANCE_DEPTH = 10


EXECUTION_STATE_APPROVED = "APPROVED"
EXECUTION_STATE_MONITORING = "MONITORING"
EXECUTION_STATE_GOVERNANCE_REVIEW = (
    "GOVERNANCE_REVIEW"
)
EXECUTION_STATE_LIMITED_APPROVAL = (
    "LIMITED_APPROVAL"
)
EXECUTION_STATE_CONDITIONAL_APPROVAL = (
    "CONDITIONAL_APPROVAL"
)
EXECUTION_STATE_DENIED = "DENIED"
EXECUTION_STATE_CRITICAL_DENIAL = (
    "CRITICAL_DENIAL"
)


PHASE_MONITOR = "MONITOR"
PHASE_COMMAND_HARDENING = (
    "COMMAND_HARDENING"
)
PHASE_ESCALATION_CONTAINMENT = (
    "ESCALATION_CONTAINMENT"
)
PHASE_CONTINUITY_RESTORATION = (
    "CONTINUITY_RESTORATION"
)
PHASE_SOVEREIGNTY_STABILIZATION = (
    "SOVEREIGNTY_STABILIZATION"
)
PHASE_RESILIENCE_SURGE = (
    "RESILIENCE_SURGE"
)
PHASE_STRATEGIC_RECOVERY = (
    "STRATEGIC_RECOVERY"
)
PHASE_GLOBAL_STABILIZATION = (
    "GLOBAL_STABILIZATION"
)


APPROVAL_APPROVED = "APPROVED"
APPROVAL_CONDITIONAL = "CONDITIONAL"
APPROVAL_REVIEW = "REVIEW"
APPROVAL_DENIED = "DENIED"


class GovernanceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class ExecutionGovernanceSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    requested_phase: Optional[str] = None

    strategic_risk_score: float = 0.0
    survivability_risk_score: float = 0.0
    sovereignty_risk_score: float = 0.0
    continuity_risk_score: float = 0.0
    escalation_risk_score: float = 0.0
    resilience_exhaustion_score: float = 0.0

    survivability_score: float = 100.0
    recovery_capacity_score: float = 100.0

    governance_complexity_score: float = 0.0
    blast_radius_score: float = 0.0
    autonomy_pressure_score: float = 0.0
    uncertainty_score: float = 0.0

    requires_human_approval: bool = False
    requires_legal_review: bool = False

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class GovernanceValidation:
    validation_id: str

    validation_name: str

    passed: bool

    score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GovernanceExecutionPhase:
    phase_id: str

    phase_name: str

    sequencing_order: int

    approval_state: str

    governance_required: bool
    human_approval_required: bool
    legal_review_required: bool

    expected_risk_reduction: float
    expected_recovery_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GovernanceDirective:
    directive_id: str

    directive_name: str

    approval_state: str

    sequencing_order: int

    governance_required: bool
    safe_mode: bool

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GovernanceProjection:
    projection_id: str

    projected_state: str

    primary_phase: str

    governance_safety_projection_score: float
    survivability_projection_score: float
    sovereignty_projection_score: float
    continuity_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GovernanceForecastStep:
    step_id: str

    step_index: int

    execution_state: str

    active_phase: str

    governance_risk_score: float
    survivability_score: float
    recovery_capacity_score: float

    sovereignty_risk_score: float
    continuity_risk_score: float
    escalation_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignExecutionGovernanceAssessment:
    assessment_id: str

    execution_state: str

    primary_phase: str

    approval_state: str

    strategic_risk_score: float
    survivability_risk_score: float
    sovereignty_risk_score: float
    continuity_risk_score: float
    escalation_risk_score: float
    resilience_exhaustion_score: float

    survivability_score: float
    recovery_capacity_score: float

    governance_complexity_score: float
    blast_radius_score: float
    autonomy_pressure_score: float
    uncertainty_score: float

    governance_risk_score: float

    recovery_probability: float
    systemic_risk_probability: float

    confidence: float
    explainability_score: float

    signal_count: int
    engine_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    validations: List[
        GovernanceValidation
    ]

    phases: List[
        GovernanceExecutionPhase
    ]

    directives: List[
        GovernanceDirective
    ]

    strategic_projection: (
        GovernanceProjection
    )

    forecast_steps: List[
        GovernanceForecastStep
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


class SovereignExecutionGovernanceEngine:
    """
    Sovereign autonomous execution governance cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        autonomous_orchestration_engine: Optional[
            Any
        ] = None,
        operational_governor: Optional[
            Any
        ] = None,
        blast_radius_analyzer: Optional[
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

        self.autonomous_orchestration_engine = (
            autonomous_orchestration_engine
        )

        self.operational_governor = (
            operational_governor
        )

        self.blast_radius_analyzer = (
            blast_radius_analyzer
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
            SovereignExecutionGovernanceAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            ExecutionGovernanceSignal
            | Dict[str, Any]
        ],
        *,
        governance_depth: int = (
            DEFAULT_GOVERNANCE_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignExecutionGovernanceAssessment
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

        survivability_risk = (
            self._avg_score(
                [
                    s
                    .survivability_risk_score
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

        continuity_risk = (
            self._avg_score(
                [
                    s
                    .continuity_risk_score
                    for s in normalized
                ]
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

        governance_complexity = (
            self._avg_score(
                [
                    s
                    .governance_complexity_score
                    for s in normalized
                ]
            )
        )

        blast_radius = self._avg_score(
            [
                s.blast_radius_score
                for s in normalized
            ]
        )

        autonomy_pressure = (
            self._avg_score(
                [
                    s
                    .autonomy_pressure_score
                    for s in normalized
                ]
            )
        )

        uncertainty = self._avg_score(
            [
                s.uncertainty_score
                for s in normalized
            ]
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

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                strategic_risk_score=(
                    strategic_risk
                ),
                survivability_risk_score=(
                    survivability_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                governance_complexity_score=(
                    governance_complexity
                ),
                blast_radius_score=(
                    blast_radius
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        governance_risk = (
            self._governance_risk_score(
                strategic_risk_score=(
                    strategic_risk
                ),
                survivability_risk_score=(
                    survivability_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                governance_complexity_score=(
                    governance_complexity
                ),
                blast_radius_score=(
                    blast_radius
                ),
                autonomy_pressure_score=(
                    autonomy_pressure
                ),
                uncertainty_score=(
                    uncertainty
                ),
                recovery_probability=(
                    recovery_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                survivability_score=(
                    survivability
                ),
            )
        )

        execution_state = (
            self._execution_state(
                governance_risk_score=(
                    governance_risk
                ),
                survivability_risk_score=(
                    survivability_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                blast_radius_score=(
                    blast_radius
                ),
                survivability_score=(
                    survivability
                ),
            )
        )

        approval_state = (
            self._approval_state(
                execution_state=(
                    execution_state
                ),
                requires_human_approval=(
                    selected
                    .requires_human_approval
                ),
                requires_legal_review=(
                    selected
                    .requires_legal_review
                ),
                blast_radius_score=(
                    blast_radius
                ),
            )
        )

        primary_phase = (
            self._primary_phase(
                requested_phase=(
                    selected.requested_phase
                ),
                execution_state=(
                    execution_state
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                recovery_probability=(
                    recovery_probability
                ),
            )
        )

        validations = self._validations(
            execution_state=(
                execution_state
            ),
            governance_risk_score=(
                governance_risk
            ),
            survivability_risk_score=(
                survivability_risk
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
            blast_radius_score=(
                blast_radius
            ),
        )

        phases = self._phases(
            primary_phase=(
                primary_phase
            ),
            approval_state=(
                approval_state
            ),
            governance_risk_score=(
                governance_risk
            ),
            recovery_capacity_score=(
                recovery_capacity
            ),
            blast_radius_score=(
                blast_radius
            ),
            requires_human_approval=(
                selected
                .requires_human_approval
            ),
            requires_legal_review=(
                selected
                .requires_legal_review
            ),
        )

        directives = self._directives(
            approval_state=(
                approval_state
            ),
            phases=phases,
        )

        projection = self._projection(
            execution_state=(
                execution_state
            ),
            primary_phase=(
                primary_phase
            ),
            governance_risk_score=(
                governance_risk
            ),
            survivability_score=(
                survivability
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
        )

        forecast_steps = (
            self._forecast_steps(
                execution_state=(
                    execution_state
                ),
                primary_phase=(
                    primary_phase
                ),
                governance_risk_score=(
                    governance_risk
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
                escalation_risk_score=(
                    escalation_risk
                ),
                depth=governance_depth,
            )
        )

        assessment = (
            SovereignExecutionGovernanceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                execution_state=(
                    execution_state
                ),
                primary_phase=(
                    primary_phase
                ),
                approval_state=(
                    approval_state
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                survivability_risk_score=(
                    survivability_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                escalation_risk_score=(
                    escalation_risk
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
                governance_complexity_score=(
                    governance_complexity
                ),
                blast_radius_score=(
                    blast_radius
                ),
                autonomy_pressure_score=(
                    autonomy_pressure
                ),
                uncertainty_score=(
                    uncertainty
                ),
                governance_risk_score=(
                    governance_risk
                ),
                recovery_probability=(
                    recovery_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
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
                validations=(
                    validations
                ),
                phases=phases,
                directives=(
                    directives
                ),
                strategic_projection=(
                    projection
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
                        execution_state=(
                            execution_state
                        ),
                        approval_state=(
                            approval_state
                        ),
                        primary_phase=(
                            primary_phase
                        ),
                        governance_risk_score=(
                            governance_risk
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
    # RISK
    # ==========================================================

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

    def _systemic_risk_probability(
        self,
        *,
        strategic_risk_score: float,
        survivability_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        governance_complexity_score: float,
        blast_radius_score: float,
        uncertainty_score: float,
    ) -> float:

        value = (
            strategic_risk_score
            + survivability_risk_score
            + sovereignty_risk_score
            + continuity_risk_score
            + escalation_risk_score
            + governance_complexity_score
            + blast_radius_score
            + uncertainty_score
        ) / 800.0

        return self._clamp_probability(
            value
        )

    def _governance_risk_score(
        self,
        *,
        strategic_risk_score: float,
        survivability_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        governance_complexity_score: float,
        blast_radius_score: float,
        autonomy_pressure_score: float,
        uncertainty_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
        survivability_score: float,
    ) -> float:

        risk = (
            strategic_risk_score
            + survivability_risk_score
            + sovereignty_risk_score
            + continuity_risk_score
            + escalation_risk_score
            + governance_complexity_score
            + blast_radius_score
            + autonomy_pressure_score
            + uncertainty_score
            + (
                (
                    1.0
                    - recovery_probability
                )
                * 100.0
            )
            + (
                systemic_risk_probability
                * 100.0
            )
            + (
                100.0
                - survivability_score
            )
        ) / 12.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATE
    # ==========================================================

    @staticmethod
    def _execution_state(
        *,
        governance_risk_score: float,
        survivability_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        blast_radius_score: float,
        survivability_score: float,
    ) -> str:

        if (
            governance_risk_score >= 85
            or survivability_score <= 30
            or blast_radius_score >= 85
        ):
            return (
                EXECUTION_STATE_CRITICAL_DENIAL
            )

        if (
            survivability_risk_score >= 75
        ):
            return (
                EXECUTION_STATE_DENIED
            )

        if sovereignty_risk_score >= 70:
            return (
                EXECUTION_STATE_GOVERNANCE_REVIEW
            )

        if continuity_risk_score >= 70:
            return (
                EXECUTION_STATE_CONDITIONAL_APPROVAL
            )

        if escalation_risk_score >= 65:
            return (
                EXECUTION_STATE_LIMITED_APPROVAL
            )

        if governance_risk_score >= 50:
            return (
                EXECUTION_STATE_MONITORING
            )

        return EXECUTION_STATE_APPROVED

    @staticmethod
    def _approval_state(
        *,
        execution_state: str,
        requires_human_approval: bool,
        requires_legal_review: bool,
        blast_radius_score: float,
    ) -> str:

        if execution_state in {
            EXECUTION_STATE_DENIED,
            EXECUTION_STATE_CRITICAL_DENIAL,
        }:
            return APPROVAL_DENIED

        if (
            requires_human_approval
            or requires_legal_review
            or blast_radius_score >= 70
        ):
            return APPROVAL_REVIEW

        if execution_state in {
            EXECUTION_STATE_LIMITED_APPROVAL,
            EXECUTION_STATE_CONDITIONAL_APPROVAL,
        }:
            return APPROVAL_CONDITIONAL

        return APPROVAL_APPROVED

    # ==========================================================
    # PHASES
    # ==========================================================

    @staticmethod
    def _primary_phase(
        *,
        requested_phase: Optional[str],
        execution_state: str,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        recovery_probability: float,
    ) -> str:

        if requested_phase:
            return requested_phase

        if execution_state in {
            EXECUTION_STATE_CRITICAL_DENIAL,
            EXECUTION_STATE_DENIED,
        }:
            return PHASE_MONITOR

        if sovereignty_risk_score >= 70:
            return (
                PHASE_SOVEREIGNTY_STABILIZATION
            )

        if continuity_risk_score >= 70:
            return (
                PHASE_CONTINUITY_RESTORATION
            )

        if escalation_risk_score >= 65:
            return (
                PHASE_ESCALATION_CONTAINMENT
            )

        if recovery_probability >= 0.75:
            return (
                PHASE_STRATEGIC_RECOVERY
            )

        return PHASE_COMMAND_HARDENING

    # ==========================================================
    # VALIDATIONS
    # ==========================================================

    def _validations(
        self,
        *,
        execution_state: str,
        governance_risk_score: float,
        survivability_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        blast_radius_score: float,
    ) -> List[GovernanceValidation]:

        checks = [
            (
                "governance_risk",
                governance_risk_score < 75,
                governance_risk_score,
            ),
            (
                "survivability_risk",
                survivability_risk_score < 75,
                survivability_risk_score,
            ),
            (
                "sovereignty_risk",
                sovereignty_risk_score < 75,
                sovereignty_risk_score,
            ),
            (
                "continuity_risk",
                continuity_risk_score < 75,
                continuity_risk_score,
            ),
            (
                "blast_radius",
                blast_radius_score < 80,
                blast_radius_score,
            ),
        ]

        validations = []

        for (
            name,
            passed,
            score,
        ) in checks:

            validations.append(
                GovernanceValidation(
                    validation_id=str(
                        uuid.uuid4()
                    ),
                    validation_name=name,
                    passed=passed,
                    score=score,
                    rationale=(
                        f"Validation {name} "
                        f"under execution "
                        f"state {execution_state}."
                    ),
                )
            )

        return validations

    # ==========================================================
    # PHASE OBJECTS
    # ==========================================================

    def _phases(
        self,
        *,
        primary_phase: str,
        approval_state: str,
        governance_risk_score: float,
        recovery_capacity_score: float,
        blast_radius_score: float,
        requires_human_approval: bool,
        requires_legal_review: bool,
    ) -> List[
        GovernanceExecutionPhase
    ]:

        sequence = self._phase_sequence(
            primary_phase
        )

        phases = []

        for idx, phase_name in enumerate(
            sequence,
            start=1,
        ):

            phases.append(
                GovernanceExecutionPhase(
                    phase_id=str(
                        uuid.uuid4()
                    ),
                    phase_name=phase_name,
                    sequencing_order=idx,
                    approval_state=(
                        approval_state
                    ),
                    governance_required=True,
                    human_approval_required=(
                        requires_human_approval
                    ),
                    legal_review_required=(
                        requires_legal_review
                    ),
                    expected_risk_reduction=(
                        governance_risk_score
                        * 0.10
                    ),
                    expected_recovery_gain=(
                        max(
                            0.0,
                            100.0
                            - recovery_capacity_score,
                        )
                        * 0.10
                    ),
                    rationale=(
                        f"Governance phase "
                        f"{phase_name} "
                        f"sequenced."
                    ),
                    metadata={
                        "blast_radius_score": (
                            blast_radius_score
                        )
                    },
                )
            )

        return phases

    @staticmethod
    def _phase_sequence(
        primary_phase: str,
    ) -> List[str]:

        mapping = {
            PHASE_COMMAND_HARDENING: [
                PHASE_COMMAND_HARDENING,
                PHASE_STRATEGIC_RECOVERY,
            ],
            PHASE_ESCALATION_CONTAINMENT: [
                PHASE_ESCALATION_CONTAINMENT,
                PHASE_COMMAND_HARDENING,
                PHASE_STRATEGIC_RECOVERY,
            ],
            PHASE_CONTINUITY_RESTORATION: [
                PHASE_CONTINUITY_RESTORATION,
                PHASE_RESILIENCE_SURGE,
                PHASE_STRATEGIC_RECOVERY,
            ],
            PHASE_SOVEREIGNTY_STABILIZATION: [
                PHASE_SOVEREIGNTY_STABILIZATION,
                PHASE_CONTINUITY_RESTORATION,
                PHASE_STRATEGIC_RECOVERY,
            ],
            PHASE_GLOBAL_STABILIZATION: [
                PHASE_ESCALATION_CONTAINMENT,
                PHASE_SOVEREIGNTY_STABILIZATION,
                PHASE_CONTINUITY_RESTORATION,
                PHASE_RESILIENCE_SURGE,
                PHASE_STRATEGIC_RECOVERY,
            ],
        }

        return mapping.get(
            primary_phase,
            [PHASE_MONITOR],
        )

    # ==========================================================
    # DIRECTIVES
    # ==========================================================

    def _directives(
        self,
        *,
        approval_state: str,
        phases: Sequence[
            GovernanceExecutionPhase
        ],
    ) -> List[
        GovernanceDirective
    ]:

        directives = []

        for phase in phases:

            directives.append(
                GovernanceDirective(
                    directive_id=str(
                        uuid.uuid4()
                    ),
                    directive_name=(
                        phase.phase_name
                    ),
                    approval_state=(
                        approval_state
                    ),
                    sequencing_order=(
                        phase
                        .sequencing_order
                    ),
                    governance_required=True,
                    safe_mode=True,
                    rationale=(
                        f"Directive for "
                        f"{phase.phase_name}."
                    ),
                )
            )

        return directives

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        execution_state: str,
        primary_phase: str,
        governance_risk_score: float,
        survivability_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> GovernanceProjection:

        return GovernanceProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                execution_state
            ),
            primary_phase=(
                primary_phase
            ),
            governance_safety_projection_score=(
                100.0
                - governance_risk_score
            ),
            survivability_projection_score=(
                survivability_score
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
                f"Governance projection "
                f"selected "
                f"{primary_phase}."
            ),
        )

    # ==========================================================
    # FORECAST
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        execution_state: str,
        primary_phase: str,
        governance_risk_score: float,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        depth: int,
    ) -> List[
        GovernanceForecastStep
    ]:

        steps = []

        for idx in range(
            max(1, int(depth))
        ):

            steps.append(
                GovernanceForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    execution_state=(
                        execution_state
                    ),
                    active_phase=(
                        primary_phase
                    ),
                    governance_risk_score=(
                        governance_risk_score
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
                    escalation_risk_score=(
                        escalation_risk_score
                    ),
                    rationale=(
                        f"Governance "
                        f"forecast step "
                        f"{idx}."
                    ),
                )
            )

            governance_risk_score = (
                self._clamp_score(
                    governance_risk_score
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

            escalation_risk_score = (
                self._clamp_score(
                    escalation_risk_score
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
            SovereignExecutionGovernanceAssessment
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
            "type": (
                "SOVEREIGN_EXECUTION_GOVERNANCE"
            ),
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
                f"⚠️ Governance "
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
                f"⚠️ Governance "
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
                f"⚠️ Governance "
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
                    "SOVEREIGN_EXECUTION_GOVERNANCE",
                    payload,
                )

        except Exception as exc:

            print(
                f"⚠️ Governance "
                f"event emit failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            ExecutionGovernanceSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> ExecutionGovernanceSignal:

        if isinstance(
            item,
            ExecutionGovernanceSignal,
        ):
            return item

        return ExecutionGovernanceSignal(
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
            requested_phase=item.get(
                "requested_phase"
            ),
            strategic_risk_score=self._clamp_score(
                item.get(
                    "strategic_risk_score",
                    0.0,
                )
            ),
            survivability_risk_score=self._clamp_score(
                item.get(
                    "survivability_risk_score",
                    0.0,
                )
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get(
                    "sovereignty_risk_score",
                    0.0,
                )
            ),
            continuity_risk_score=self._clamp_score(
                item.get(
                    "continuity_risk_score",
                    0.0,
                )
            ),
            escalation_risk_score=self._clamp_score(
                item.get(
                    "escalation_risk_score",
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
            governance_complexity_score=self._clamp_score(
                item.get(
                    "governance_complexity_score",
                    0.0,
                )
            ),
            blast_radius_score=self._clamp_score(
                item.get(
                    "blast_radius_score",
                    0.0,
                )
            ),
            autonomy_pressure_score=self._clamp_score(
                item.get(
                    "autonomy_pressure_score",
                    0.0,
                )
            ),
            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),
            requires_human_approval=bool(
                item.get(
                    "requires_human_approval",
                    False,
                )
            ),
            requires_legal_review=bool(
                item.get(
                    "requires_legal_review",
                    False,
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
        SovereignExecutionGovernanceAssessment
    ):

        projection = GovernanceProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                EXECUTION_STATE_APPROVED
            ),
            primary_phase=PHASE_MONITOR,
            governance_safety_projection_score=100.0,
            survivability_projection_score=100.0,
            sovereignty_projection_score=100.0,
            continuity_projection_score=100.0,
            rationale=(
                "No governance "
                "signals submitted."
            ),
        )

        return (
            SovereignExecutionGovernanceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                execution_state=(
                    EXECUTION_STATE_APPROVED
                ),
                primary_phase=PHASE_MONITOR,
                approval_state=(
                    APPROVAL_APPROVED
                ),
                strategic_risk_score=0.0,
                survivability_risk_score=0.0,
                sovereignty_risk_score=0.0,
                continuity_risk_score=0.0,
                escalation_risk_score=0.0,
                resilience_exhaustion_score=0.0,
                survivability_score=100.0,
                recovery_capacity_score=100.0,
                governance_complexity_score=0.0,
                blast_radius_score=0.0,
                autonomy_pressure_score=0.0,
                uncertainty_score=0.0,
                governance_risk_score=0.0,
                recovery_probability=1.0,
                systemic_risk_probability=0.0,
                confidence=1.0,
                explainability_score=100.0,
                signal_count=0,
                engine_count=0,
                severity=(
                    GovernanceSeverity.INFO.value
                ),
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                validations=[],
                phases=[],
                directives=[],
                strategic_projection=(
                    projection
                ),
                forecast_steps=[],
                telemetry_fusion={},
                rationale=(
                    "No governance "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            ExecutionGovernanceSignal
        ],
    ) -> ExecutionGovernanceSignal:

        return sorted(
            signals,
            key=lambda item: (
                item.strategic_risk_score,
                item.blast_radius_score,
                item.survivability_risk_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[
            ExecutionGovernanceSignal
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
            "requested_phases": sorted(
                {
                    s.requested_phase
                    for s in signals
                    if s.requested_phase
                }
            ),
        }

    def _confidence(
        self,
        signals: Sequence[
            ExecutionGovernanceSignal
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
            ExecutionGovernanceSignal
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
        execution_state: str,
        approval_state: str,
        primary_phase: str,
        governance_risk_score: float,
    ) -> str:

        return (
            f"Sovereign execution "
            f"governance completed. "
            f"Execution state "
            f"{execution_state}; "
            f"approval state "
            f"{approval_state}; "
            f"primary phase "
            f"{primary_phase}; "
            f"governance risk "
            f"{governance_risk_score:.2f}."
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or GovernanceSeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in GovernanceSeverity
        }

        return (
            value
            if value in valid
            else GovernanceSeverity.INFO.value
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


def build_sovereign_execution_governance_engine(
    *,
    event_bus: Optional[Any] = None,
    autonomous_orchestration_engine: Optional[
        Any
    ] = None,
    operational_governor: Optional[
        Any
    ] = None,
    blast_radius_analyzer: Optional[
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
    SovereignExecutionGovernanceEngine
):

    return (
        SovereignExecutionGovernanceEngine(
            event_bus=event_bus,
            autonomous_orchestration_engine=(
                autonomous_orchestration_engine
            ),
            operational_governor=(
                operational_governor
            ),
            blast_radius_analyzer=(
                blast_radius_analyzer
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