"""
core/runtime/sovereign_execution_verification_engine.py

Sovereign Execution Verification Engine

Post-execution sovereign operational verification cognition.

This subsystem:
- verifies orchestration outcomes
- verifies governance compliance
- verifies survivability preservation
- verifies sovereignty preservation
- verifies continuity preservation
- verifies resilience stabilization
- verifies recovery effectiveness
- verifies escalation containment effectiveness
- produces replayable verification lineage

IMPORTANT:
This subsystem DOES NOT:
- autonomously execute destructive operations
- bypass governance boundaries
- mutate infrastructure directly
- override human approvals

It ONLY:
- validate operational outcomes
- verify governance-safe execution
- verify survivability-safe outcomes
- produce replayable verification rationale
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_execution_verification_engine"
)

DEFAULT_VERIFICATION_DEPTH = 10


VERIFICATION_STATE_VERIFIED = "VERIFIED"
VERIFICATION_STATE_MONITORING = (
    "MONITORING"
)
VERIFICATION_STATE_PARTIAL_SUCCESS = (
    "PARTIAL_SUCCESS"
)
VERIFICATION_STATE_STABILIZING = (
    "STABILIZING"
)
VERIFICATION_STATE_GOVERNANCE_DRIFT = (
    "GOVERNANCE_DRIFT"
)
VERIFICATION_STATE_SURVIVABILITY_PRESSURE = (
    "SURVIVABILITY_PRESSURE"
)
VERIFICATION_STATE_RECOVERY_FAILURE = (
    "RECOVERY_FAILURE"
)
VERIFICATION_STATE_CRITICAL_FAILURE = (
    "CRITICAL_FAILURE"
)


VERIFICATION_RESULT_SUCCESS = "SUCCESS"
VERIFICATION_RESULT_PARTIAL = "PARTIAL"
VERIFICATION_RESULT_FAILED = "FAILED"


class VerificationSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class VerificationSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    executed_phase: Optional[str] = None

    strategic_risk_score: float = 0.0
    survivability_risk_score: float = 0.0
    sovereignty_risk_score: float = 0.0
    continuity_risk_score: float = 0.0
    escalation_risk_score: float = 0.0

    resilience_exhaustion_score: float = 0.0

    survivability_score: float = 100.0
    recovery_capacity_score: float = 100.0

    governance_compliance_score: float = 100.0
    execution_success_score: float = 100.0
    recovery_effectiveness_score: float = 100.0
    stabilization_effectiveness_score: float = 100.0

    blast_radius_score: float = 0.0
    autonomy_pressure_score: float = 0.0
    uncertainty_score: float = 0.0

    governance_boundary_respected: bool = True
    approvals_respected: bool = True
    autonomy_limits_respected: bool = True

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class VerificationValidation:
    validation_id: str

    validation_name: str

    passed: bool

    score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class VerificationDirective:
    directive_id: str

    directive_name: str

    verification_result: str

    sequencing_order: int

    requires_followup: bool

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class VerificationProjection:
    projection_id: str

    projected_state: str

    verification_result: str

    governance_projection_score: float
    survivability_projection_score: float
    continuity_projection_score: float
    recovery_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class VerificationForecastStep:
    step_id: str

    step_index: int

    verification_state: str

    verification_result: str

    governance_risk_score: float
    survivability_score: float
    recovery_capacity_score: float

    continuity_risk_score: float
    sovereignty_risk_score: float
    escalation_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignExecutionVerificationAssessment:
    assessment_id: str

    verification_state: str

    verification_result: str

    strategic_risk_score: float
    survivability_risk_score: float
    sovereignty_risk_score: float
    continuity_risk_score: float
    escalation_risk_score: float

    resilience_exhaustion_score: float

    survivability_score: float
    recovery_capacity_score: float

    governance_compliance_score: float
    execution_success_score: float
    recovery_effectiveness_score: float
    stabilization_effectiveness_score: float

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
        VerificationValidation
    ]

    directives: List[
        VerificationDirective
    ]

    strategic_projection: (
        VerificationProjection
    )

    forecast_steps: List[
        VerificationForecastStep
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


class SovereignExecutionVerificationEngine:
    """
    Sovereign autonomous verification cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        execution_governance_engine: Optional[
            Any
        ] = None,
        orchestration_engine: Optional[
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

        self.execution_governance_engine = (
            execution_governance_engine
        )

        self.orchestration_engine = (
            orchestration_engine
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
            SovereignExecutionVerificationAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            VerificationSignal
            | Dict[str, Any]
        ],
        *,
        verification_depth: int = (
            DEFAULT_VERIFICATION_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignExecutionVerificationAssessment
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

        governance_compliance = (
            self._avg_score(
                [
                    s
                    .governance_compliance_score
                    for s in normalized
                ]
            )
        )

        execution_success = (
            self._avg_score(
                [
                    s
                    .execution_success_score
                    for s in normalized
                ]
            )
        )

        recovery_effectiveness = (
            self._avg_score(
                [
                    s
                    .recovery_effectiveness_score
                    for s in normalized
                ]
            )
        )

        stabilization_effectiveness = (
            self._avg_score(
                [
                    s
                    .stabilization_effectiveness_score
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
                governance_compliance_score=(
                    governance_compliance
                ),
                execution_success_score=(
                    execution_success
                ),
                recovery_effectiveness_score=(
                    recovery_effectiveness
                ),
                stabilization_effectiveness_score=(
                    stabilization_effectiveness
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

        verification_state = (
            self._verification_state(
                governance_risk_score=(
                    governance_risk
                ),
                governance_compliance_score=(
                    governance_compliance
                ),
                execution_success_score=(
                    execution_success
                ),
                survivability_score=(
                    survivability
                ),
                recovery_effectiveness_score=(
                    recovery_effectiveness
                ),
            )
        )

        verification_result = (
            self._verification_result(
                verification_state=(
                    verification_state
                ),
                governance_compliance_score=(
                    governance_compliance
                ),
                execution_success_score=(
                    execution_success
                ),
            )
        )

        validations = self._validations(
            governance_compliance_score=(
                governance_compliance
            ),
            execution_success_score=(
                execution_success
            ),
            recovery_effectiveness_score=(
                recovery_effectiveness
            ),
            stabilization_effectiveness_score=(
                stabilization_effectiveness
            ),
            blast_radius_score=(
                blast_radius
            ),
            governance_boundary_respected=all(
                s
                .governance_boundary_respected
                for s in normalized
            ),
            approvals_respected=all(
                s.approvals_respected
                for s in normalized
            ),
            autonomy_limits_respected=all(
                s
                .autonomy_limits_respected
                for s in normalized
            ),
        )

        directives = self._directives(
            verification_result=(
                verification_result
            ),
            verification_state=(
                verification_state
            ),
        )

        projection = self._projection(
            verification_state=(
                verification_state
            ),
            verification_result=(
                verification_result
            ),
            governance_compliance_score=(
                governance_compliance
            ),
            survivability_score=(
                survivability
            ),
            continuity_risk_score=(
                continuity_risk
            ),
            recovery_effectiveness_score=(
                recovery_effectiveness
            ),
        )

        forecast_steps = (
            self._forecast_steps(
                verification_state=(
                    verification_state
                ),
                verification_result=(
                    verification_result
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
                depth=verification_depth,
            )
        )

        assessment = (
            SovereignExecutionVerificationAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                verification_state=(
                    verification_state
                ),
                verification_result=(
                    verification_result
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
                governance_compliance_score=(
                    governance_compliance
                ),
                execution_success_score=(
                    execution_success
                ),
                recovery_effectiveness_score=(
                    recovery_effectiveness
                ),
                stabilization_effectiveness_score=(
                    stabilization_effectiveness
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
                        verification_state=(
                            verification_state
                        ),
                        verification_result=(
                            verification_result
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
        blast_radius_score: float,
        uncertainty_score: float,
    ) -> float:

        value = (
            strategic_risk_score
            + survivability_risk_score
            + sovereignty_risk_score
            + continuity_risk_score
            + escalation_risk_score
            + blast_radius_score
            + uncertainty_score
        ) / 700.0

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
        governance_compliance_score: float,
        execution_success_score: float,
        recovery_effectiveness_score: float,
        stabilization_effectiveness_score: float,
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
            + (
                100.0
                - governance_compliance_score
            )
            + (
                100.0
                - execution_success_score
            )
            + (
                100.0
                - recovery_effectiveness_score
            )
            + (
                100.0
                - stabilization_effectiveness_score
            )
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
        ) / 15.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATE
    # ==========================================================

    @staticmethod
    def _verification_state(
        *,
        governance_risk_score: float,
        governance_compliance_score: float,
        execution_success_score: float,
        survivability_score: float,
        recovery_effectiveness_score: float,
    ) -> str:

        if (
            governance_risk_score >= 85
            or survivability_score <= 30
        ):
            return (
                VERIFICATION_STATE_CRITICAL_FAILURE
            )

        if (
            governance_compliance_score
            < 60
        ):
            return (
                VERIFICATION_STATE_GOVERNANCE_DRIFT
            )

        if execution_success_score < 60:
            return (
                VERIFICATION_STATE_RECOVERY_FAILURE
            )

        if survivability_score < 70:
            return (
                VERIFICATION_STATE_SURVIVABILITY_PRESSURE
            )

        if recovery_effectiveness_score < 75:
            return (
                VERIFICATION_STATE_STABILIZING
            )

        if governance_risk_score >= 50:
            return (
                VERIFICATION_STATE_PARTIAL_SUCCESS
            )

        if governance_risk_score >= 25:
            return (
                VERIFICATION_STATE_MONITORING
            )

        return VERIFICATION_STATE_VERIFIED

    @staticmethod
    def _verification_result(
        *,
        verification_state: str,
        governance_compliance_score: float,
        execution_success_score: float,
    ) -> str:

        if verification_state in {
            VERIFICATION_STATE_CRITICAL_FAILURE,
            VERIFICATION_STATE_RECOVERY_FAILURE,
        }:
            return (
                VERIFICATION_RESULT_FAILED
            )

        if (
            governance_compliance_score
            < 80
            or execution_success_score
            < 80
        ):
            return (
                VERIFICATION_RESULT_PARTIAL
            )

        return VERIFICATION_RESULT_SUCCESS

    # ==========================================================
    # VALIDATIONS
    # ==========================================================

    def _validations(
        self,
        *,
        governance_compliance_score: float,
        execution_success_score: float,
        recovery_effectiveness_score: float,
        stabilization_effectiveness_score: float,
        blast_radius_score: float,
        governance_boundary_respected: bool,
        approvals_respected: bool,
        autonomy_limits_respected: bool,
    ) -> List[
        VerificationValidation
    ]:

        checks = [
            (
                "governance_compliance",
                governance_compliance_score >= 75,
                governance_compliance_score,
            ),
            (
                "execution_success",
                execution_success_score >= 75,
                execution_success_score,
            ),
            (
                "recovery_effectiveness",
                recovery_effectiveness_score
                >= 75,
                recovery_effectiveness_score,
            ),
            (
                "stabilization_effectiveness",
                stabilization_effectiveness_score
                >= 75,
                stabilization_effectiveness_score,
            ),
            (
                "blast_radius_control",
                blast_radius_score < 80,
                blast_radius_score,
            ),
            (
                "governance_boundaries",
                governance_boundary_respected,
                100.0
                if governance_boundary_respected
                else 0.0,
            ),
            (
                "approval_enforcement",
                approvals_respected,
                100.0
                if approvals_respected
                else 0.0,
            ),
            (
                "autonomy_limits",
                autonomy_limits_respected,
                100.0
                if autonomy_limits_respected
                else 0.0,
            ),
        ]

        validations = []

        for (
            name,
            passed,
            score,
        ) in checks:

            validations.append(
                VerificationValidation(
                    validation_id=str(
                        uuid.uuid4()
                    ),
                    validation_name=name,
                    passed=bool(
                        passed
                    ),
                    score=float(score),
                    rationale=(
                        f"Verification "
                        f"validation "
                        f"{name} executed."
                    ),
                )
            )

        return validations

    # ==========================================================
    # DIRECTIVES
    # ==========================================================

    def _directives(
        self,
        *,
        verification_result: str,
        verification_state: str,
    ) -> List[
        VerificationDirective
    ]:

        directives = []

        if (
            verification_result
            == VERIFICATION_RESULT_FAILED
        ):

            directives.append(
                VerificationDirective(
                    directive_id=str(
                        uuid.uuid4()
                    ),
                    directive_name=(
                        "ROLLBACK_AND_REVIEW"
                    ),
                    verification_result=(
                        verification_result
                    ),
                    sequencing_order=1,
                    requires_followup=True,
                    rationale=(
                        "Verification "
                        "failure requires "
                        "rollback review."
                    ),
                )
            )

        elif (
            verification_result
            == VERIFICATION_RESULT_PARTIAL
        ):

            directives.append(
                VerificationDirective(
                    directive_id=str(
                        uuid.uuid4()
                    ),
                    directive_name=(
                        "CONTINUE_MONITORING"
                    ),
                    verification_result=(
                        verification_result
                    ),
                    sequencing_order=1,
                    requires_followup=True,
                    rationale=(
                        "Partial "
                        "verification "
                        "requires monitoring."
                    ),
                )
            )

        else:

            directives.append(
                VerificationDirective(
                    directive_id=str(
                        uuid.uuid4()
                    ),
                    directive_name=(
                        "VERIFICATION_COMPLETE"
                    ),
                    verification_result=(
                        verification_result
                    ),
                    sequencing_order=1,
                    requires_followup=False,
                    rationale=(
                        "Verification "
                        "successful."
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
        verification_state: str,
        verification_result: str,
        governance_compliance_score: float,
        survivability_score: float,
        continuity_risk_score: float,
        recovery_effectiveness_score: float,
    ) -> VerificationProjection:

        return VerificationProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                verification_state
            ),
            verification_result=(
                verification_result
            ),
            governance_projection_score=(
                governance_compliance_score
            ),
            survivability_projection_score=(
                survivability_score
            ),
            continuity_projection_score=(
                100.0
                - continuity_risk_score
            ),
            recovery_projection_score=(
                recovery_effectiveness_score
            ),
            rationale=(
                "Verification "
                "projection generated."
            ),
        )

    # ==========================================================
    # FORECAST
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        verification_state: str,
        verification_result: str,
        governance_risk_score: float,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        depth: int,
    ) -> List[
        VerificationForecastStep
    ]:

        steps = []

        for idx in range(
            max(1, int(depth))
        ):

            steps.append(
                VerificationForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    verification_state=(
                        verification_state
                    ),
                    verification_result=(
                        verification_result
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
                        f"Verification "
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
            SovereignExecutionVerificationAssessment
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
                "SOVEREIGN_EXECUTION_VERIFICATION"
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
                f"⚠️ Verification "
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
                f"⚠️ Verification "
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
                f"⚠️ Verification "
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
                    "SOVEREIGN_EXECUTION_VERIFICATION",
                    payload,
                )

        except Exception as exc:

            print(
                f"⚠️ Verification "
                f"event emit failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            VerificationSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> VerificationSignal:

        if isinstance(
            item,
            VerificationSignal,
        ):
            return item

        return VerificationSignal(
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
            executed_phase=item.get(
                "executed_phase"
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
            governance_compliance_score=self._clamp_score(
                item.get(
                    "governance_compliance_score",
                    100.0,
                )
            ),
            execution_success_score=self._clamp_score(
                item.get(
                    "execution_success_score",
                    100.0,
                )
            ),
            recovery_effectiveness_score=self._clamp_score(
                item.get(
                    "recovery_effectiveness_score",
                    100.0,
                )
            ),
            stabilization_effectiveness_score=self._clamp_score(
                item.get(
                    "stabilization_effectiveness_score",
                    100.0,
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
            governance_boundary_respected=bool(
                item.get(
                    "governance_boundary_respected",
                    True,
                )
            ),
            approvals_respected=bool(
                item.get(
                    "approvals_respected",
                    True,
                )
            ),
            autonomy_limits_respected=bool(
                item.get(
                    "autonomy_limits_respected",
                    True,
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
        SovereignExecutionVerificationAssessment
    ):

        projection = (
            VerificationProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projected_state=(
                    VERIFICATION_STATE_VERIFIED
                ),
                verification_result=(
                    VERIFICATION_RESULT_SUCCESS
                ),
                governance_projection_score=100.0,
                survivability_projection_score=100.0,
                continuity_projection_score=100.0,
                recovery_projection_score=100.0,
                rationale=(
                    "No verification "
                    "signals submitted."
                ),
            )
        )

        return (
            SovereignExecutionVerificationAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                verification_state=(
                    VERIFICATION_STATE_VERIFIED
                ),
                verification_result=(
                    VERIFICATION_RESULT_SUCCESS
                ),
                strategic_risk_score=0.0,
                survivability_risk_score=0.0,
                sovereignty_risk_score=0.0,
                continuity_risk_score=0.0,
                escalation_risk_score=0.0,
                resilience_exhaustion_score=0.0,
                survivability_score=100.0,
                recovery_capacity_score=100.0,
                governance_compliance_score=100.0,
                execution_success_score=100.0,
                recovery_effectiveness_score=100.0,
                stabilization_effectiveness_score=100.0,
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
                    VerificationSeverity.INFO.value
                ),
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                validations=[],
                directives=[],
                strategic_projection=(
                    projection
                ),
                forecast_steps=[],
                telemetry_fusion={},
                rationale=(
                    "No verification "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            VerificationSignal
        ],
    ) -> VerificationSignal:

        return sorted(
            signals,
            key=lambda item: (
                item.strategic_risk_score,
                item.survivability_risk_score,
                item.blast_radius_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[
            VerificationSignal
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
            "executed_phases": sorted(
                {
                    s.executed_phase
                    for s in signals
                    if s.executed_phase
                }
            ),
        }

    def _confidence(
        self,
        signals: Sequence[
            VerificationSignal
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
            VerificationSignal
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
        verification_state: str,
        verification_result: str,
        governance_risk_score: float,
    ) -> str:

        return (
            f"Sovereign execution "
            f"verification completed. "
            f"Verification state "
            f"{verification_state}; "
            f"verification result "
            f"{verification_result}; "
            f"governance risk "
            f"{governance_risk_score:.2f}."
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or VerificationSeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in VerificationSeverity
        }

        return (
            value
            if value in valid
            else VerificationSeverity.INFO.value
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


def build_sovereign_execution_verification_engine(
    *,
    event_bus: Optional[Any] = None,
    execution_governance_engine: Optional[
        Any
    ] = None,
    orchestration_engine: Optional[Any] = None,
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
    SovereignExecutionVerificationEngine
):

    return (
        SovereignExecutionVerificationEngine(
            event_bus=event_bus,
            execution_governance_engine=(
                execution_governance_engine
            ),
            orchestration_engine=(
                orchestration_engine
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