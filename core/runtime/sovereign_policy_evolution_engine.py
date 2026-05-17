"""
core/runtime/sovereign_policy_evolution_engine.py

Sovereign Policy Evolution Engine

Policy evolution cognition layer.

This subsystem:
- converts adaptive learning into policy evolution
- proposes governance threshold adjustments
- proposes survivability policy tuning
- proposes sovereignty control tuning
- proposes resilience prioritization tuning
- proposes orchestration sequencing evolution
- produces replayable policy evolution lineage

IMPORTANT:
This subsystem DOES NOT:
- autonomously override governance
- autonomously deploy policy changes
- bypass human approvals
- directly mutate production controls

It ONLY:
- generate policy evolution recommendations
- optimize governance-safe policies
- optimize survivability-safe policy posture
- produce replayable policy rationale
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_policy_evolution_engine"
)

DEFAULT_EVOLUTION_DEPTH = 10


POLICY_STATE_STABLE = "STABLE"
POLICY_STATE_EVOLVING = "EVOLVING"
POLICY_STATE_RECALIBRATING = (
    "RECALIBRATING"
)
POLICY_STATE_HARDENING = "HARDENING"
POLICY_STATE_RESILIENCE_SHIFT = (
    "RESILIENCE_SHIFT"
)
POLICY_STATE_GOVERNANCE_REVIEW = (
    "GOVERNANCE_REVIEW"
)
POLICY_STATE_SURVIVABILITY_PROTECTION = (
    "SURVIVABILITY_PROTECTION"
)
POLICY_STATE_CRITICAL_RESTRUCTURE = (
    "CRITICAL_RESTRUCTURE"
)


POLICY_RESULT_OPTIMIZED = "OPTIMIZED"
POLICY_RESULT_ADJUSTED = "ADJUSTED"
POLICY_RESULT_RESTRICTED = "RESTRICTED"


class PolicySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class PolicyEvolutionSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    governance_success_score: float = 100.0
    survivability_success_score: float = 100.0
    continuity_success_score: float = 100.0
    resilience_success_score: float = 100.0
    orchestration_success_score: float = 100.0

    governance_drift_score: float = 0.0
    sovereignty_pressure_score: float = 0.0
    escalation_pressure_score: float = 0.0
    continuity_fragmentation_score: float = 0.0

    adaptive_learning_score: float = 100.0
    optimization_opportunity_score: float = 0.0

    blast_radius_score: float = 0.0
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
class PolicyThresholdEvolution:
    threshold_id: str

    threshold_name: str

    current_value: float
    proposed_value: float

    adjustment_delta: float

    approval_required: bool

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class PolicyEvolutionProposal:
    proposal_id: str

    proposal_name: str

    priority: str

    expected_stability_gain: float

    approval_required: bool

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class PolicyProjection:
    projection_id: str

    projected_state: str

    policy_result: str

    governance_projection_score: float
    survivability_projection_score: float
    resilience_projection_score: float
    orchestration_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class PolicyForecastStep:
    step_id: str

    step_index: int

    policy_state: str

    policy_result: str

    governance_score: float
    survivability_score: float
    resilience_score: float
    orchestration_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignPolicyEvolutionAssessment:
    assessment_id: str

    policy_state: str

    policy_result: str

    governance_success_score: float
    survivability_success_score: float
    continuity_success_score: float
    resilience_success_score: float
    orchestration_success_score: float

    governance_drift_score: float
    sovereignty_pressure_score: float
    escalation_pressure_score: float
    continuity_fragmentation_score: float

    adaptive_learning_score: float
    optimization_opportunity_score: float

    blast_radius_score: float
    uncertainty_score: float

    policy_optimization_score: float

    confidence: float
    explainability_score: float

    systemic_risk_probability: float

    signal_count: int
    engine_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    threshold_evolutions: List[
        PolicyThresholdEvolution
    ]

    policy_proposals: List[
        PolicyEvolutionProposal
    ]

    strategic_projection: PolicyProjection

    forecast_steps: List[
        PolicyForecastStep
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


class SovereignPolicyEvolutionEngine:
    """
    Sovereign policy evolution cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        adaptive_learning_engine: Optional[
            Any
        ] = None,
        execution_governance_engine: Optional[
            Any
        ] = None,
        execution_verification_engine: Optional[
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

        self.adaptive_learning_engine = (
            adaptive_learning_engine
        )

        self.execution_governance_engine = (
            execution_governance_engine
        )

        self.execution_verification_engine = (
            execution_verification_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignPolicyEvolutionAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            PolicyEvolutionSignal
            | Dict[str, Any]
        ],
        *,
        evolution_depth: int = (
            DEFAULT_EVOLUTION_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignPolicyEvolutionAssessment
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

        governance_success = (
            self._avg_score(
                [
                    s
                    .governance_success_score
                    for s in normalized
                ]
            )
        )

        survivability_success = (
            self._avg_score(
                [
                    s
                    .survivability_success_score
                    for s in normalized
                ]
            )
        )

        continuity_success = (
            self._avg_score(
                [
                    s
                    .continuity_success_score
                    for s in normalized
                ]
            )
        )

        resilience_success = (
            self._avg_score(
                [
                    s
                    .resilience_success_score
                    for s in normalized
                ]
            )
        )

        orchestration_success = (
            self._avg_score(
                [
                    s
                    .orchestration_success_score
                    for s in normalized
                ]
            )
        )

        governance_drift = (
            self._avg_score(
                [
                    s
                    .governance_drift_score
                    for s in normalized
                ]
            )
        )

        sovereignty_pressure = (
            self._avg_score(
                [
                    s
                    .sovereignty_pressure_score
                    for s in normalized
                ]
            )
        )

        escalation_pressure = (
            self._avg_score(
                [
                    s
                    .escalation_pressure_score
                    for s in normalized
                ]
            )
        )

        continuity_fragmentation = (
            self._avg_score(
                [
                    s
                    .continuity_fragmentation_score
                    for s in normalized
                ]
            )
        )

        adaptive_learning = (
            self._avg_score(
                [
                    s
                    .adaptive_learning_score
                    for s in normalized
                ]
            )
        )

        optimization_opportunity = (
            self._avg_score(
                [
                    s
                    .optimization_opportunity_score
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

        uncertainty = self._avg_score(
            [
                s.uncertainty_score
                for s in normalized
            ]
        )

        policy_optimization = (
            self._policy_optimization_score(
                governance_success_score=(
                    governance_success
                ),
                survivability_success_score=(
                    survivability_success
                ),
                continuity_success_score=(
                    continuity_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                orchestration_success_score=(
                    orchestration_success
                ),
                adaptive_learning_score=(
                    adaptive_learning
                ),
                optimization_opportunity_score=(
                    optimization_opportunity
                ),
                governance_drift_score=(
                    governance_drift
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                governance_drift_score=(
                    governance_drift
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
                blast_radius_score=(
                    blast_radius
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        policy_state = self._policy_state(
            policy_optimization_score=(
                policy_optimization
            ),
            survivability_success_score=(
                survivability_success
            ),
            governance_drift_score=(
                governance_drift
            ),
            resilience_success_score=(
                resilience_success
            ),
        )

        policy_result = (
            self._policy_result(
                policy_state=(
                    policy_state
                ),
                policy_optimization_score=(
                    policy_optimization
                ),
            )
        )

        threshold_evolutions = (
            self._threshold_evolutions(
                governance_drift_score=(
                    governance_drift
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
            )
        )

        policy_proposals = (
            self._policy_proposals(
                policy_state=(
                    policy_state
                ),
                optimization_opportunity_score=(
                    optimization_opportunity
                ),
            )
        )

        projection = self._projection(
            policy_state=(
                policy_state
            ),
            policy_result=(
                policy_result
            ),
            governance_success_score=(
                governance_success
            ),
            survivability_success_score=(
                survivability_success
            ),
            resilience_success_score=(
                resilience_success
            ),
            orchestration_success_score=(
                orchestration_success
            ),
        )

        forecast_steps = (
            self._forecast_steps(
                policy_state=(
                    policy_state
                ),
                policy_result=(
                    policy_result
                ),
                policy_optimization_score=(
                    policy_optimization
                ),
                governance_success_score=(
                    governance_success
                ),
                survivability_success_score=(
                    survivability_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                orchestration_success_score=(
                    orchestration_success
                ),
                depth=evolution_depth,
            )
        )

        assessment = (
            SovereignPolicyEvolutionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                policy_state=(
                    policy_state
                ),
                policy_result=(
                    policy_result
                ),
                governance_success_score=(
                    governance_success
                ),
                survivability_success_score=(
                    survivability_success
                ),
                continuity_success_score=(
                    continuity_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                orchestration_success_score=(
                    orchestration_success
                ),
                governance_drift_score=(
                    governance_drift
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
                adaptive_learning_score=(
                    adaptive_learning
                ),
                optimization_opportunity_score=(
                    optimization_opportunity
                ),
                blast_radius_score=(
                    blast_radius
                ),
                uncertainty_score=(
                    uncertainty
                ),
                policy_optimization_score=(
                    policy_optimization
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
                systemic_risk_probability=(
                    systemic_risk_probability
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
                threshold_evolutions=(
                    threshold_evolutions
                ),
                policy_proposals=(
                    policy_proposals
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
                        policy_state=(
                            policy_state
                        ),
                        policy_result=(
                            policy_result
                        ),
                        policy_optimization_score=(
                            policy_optimization
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
    # POLICY OPTIMIZATION
    # ==========================================================

    def _policy_optimization_score(
        self,
        *,
        governance_success_score: float,
        survivability_success_score: float,
        continuity_success_score: float,
        resilience_success_score: float,
        orchestration_success_score: float,
        adaptive_learning_score: float,
        optimization_opportunity_score: float,
        governance_drift_score: float,
        sovereignty_pressure_score: float,
        escalation_pressure_score: float,
        continuity_fragmentation_score: float,
    ) -> float:

        value = (
            governance_success_score
            + survivability_success_score
            + continuity_success_score
            + resilience_success_score
            + orchestration_success_score
            + adaptive_learning_score
            + optimization_opportunity_score
            + (
                100.0
                - governance_drift_score
            )
            + (
                100.0
                - sovereignty_pressure_score
            )
            + (
                100.0
                - escalation_pressure_score
            )
            + (
                100.0
                - continuity_fragmentation_score
            )
        ) / 11.0

        return self._clamp_score(
            value
        )

    def _systemic_risk_probability(
        self,
        *,
        governance_drift_score: float,
        sovereignty_pressure_score: float,
        escalation_pressure_score: float,
        continuity_fragmentation_score: float,
        blast_radius_score: float,
        uncertainty_score: float,
    ) -> float:

        value = (
            governance_drift_score
            + sovereignty_pressure_score
            + escalation_pressure_score
            + continuity_fragmentation_score
            + blast_radius_score
            + uncertainty_score
        ) / 600.0

        return self._clamp_probability(
            value
        )

    # ==========================================================
    # POLICY STATE
    # ==========================================================

    @staticmethod
    def _policy_state(
        *,
        policy_optimization_score: float,
        survivability_success_score: float,
        governance_drift_score: float,
        resilience_success_score: float,
    ) -> str:

        if (
            policy_optimization_score
            < 40
        ):
            return (
                POLICY_STATE_CRITICAL_RESTRUCTURE
            )

        if (
            survivability_success_score
            < 60
        ):
            return (
                POLICY_STATE_SURVIVABILITY_PROTECTION
            )

        if governance_drift_score > 50:
            return (
                POLICY_STATE_GOVERNANCE_REVIEW
            )

        if resilience_success_score < 70:
            return (
                POLICY_STATE_RESILIENCE_SHIFT
            )

        if (
            policy_optimization_score
            < 75
        ):
            return (
                POLICY_STATE_RECALIBRATING
            )

        if (
            policy_optimization_score
            < 85
        ):
            return (
                POLICY_STATE_EVOLVING
            )

        if (
            policy_optimization_score
            < 92
        ):
            return POLICY_STATE_HARDENING

        return POLICY_STATE_STABLE

    @staticmethod
    def _policy_result(
        *,
        policy_state: str,
        policy_optimization_score: float,
    ) -> str:

        if policy_state in {
            POLICY_STATE_CRITICAL_RESTRUCTURE,
            POLICY_STATE_SURVIVABILITY_PROTECTION,
        }:
            return POLICY_RESULT_RESTRICTED

        if (
            policy_optimization_score
            < 90
        ):
            return POLICY_RESULT_ADJUSTED

        return POLICY_RESULT_OPTIMIZED

    # ==========================================================
    # THRESHOLD EVOLUTION
    # ==========================================================

    def _threshold_evolutions(
        self,
        *,
        governance_drift_score: float,
        sovereignty_pressure_score: float,
        escalation_pressure_score: float,
        continuity_fragmentation_score: float,
    ) -> List[
        PolicyThresholdEvolution
    ]:

        threshold_map = {
            "governance_boundary": (
                governance_drift_score
            ),
            "sovereignty_boundary": (
                sovereignty_pressure_score
            ),
            "escalation_boundary": (
                escalation_pressure_score
            ),
            "continuity_boundary": (
                continuity_fragmentation_score
            ),
        }

        evolutions = []

        for (
            name,
            pressure,
        ) in threshold_map.items():

            current_value = 75.0

            proposed_value = max(
                45.0,
                min(
                    95.0,
                    current_value
                    - (pressure * 0.12),
                ),
            )

            evolutions.append(
                PolicyThresholdEvolution(
                    threshold_id=str(
                        uuid.uuid4()
                    ),
                    threshold_name=name,
                    current_value=(
                        current_value
                    ),
                    proposed_value=(
                        proposed_value
                    ),
                    adjustment_delta=(
                        proposed_value
                        - current_value
                    ),
                    approval_required=True,
                    rationale=(
                        f"Policy threshold "
                        f"{name} evolved "
                        f"from adaptive "
                        f"operational learning."
                    ),
                )
            )

        return evolutions

    # ==========================================================
    # POLICY PROPOSALS
    # ==========================================================

    def _policy_proposals(
        self,
        *,
        policy_state: str,
        optimization_opportunity_score: float,
    ) -> List[
        PolicyEvolutionProposal
    ]:

        proposals = []

        if policy_state in {
            POLICY_STATE_RECALIBRATING,
            POLICY_STATE_EVOLVING,
        }:

            proposals.append(
                PolicyEvolutionProposal(
                    proposal_id=str(
                        uuid.uuid4()
                    ),
                    proposal_name=(
                        "ADAPT_ORCHESTRATION_POLICY"
                    ),
                    priority="HIGH",
                    expected_stability_gain=(
                        optimization_opportunity_score
                    ),
                    approval_required=True,
                    rationale=(
                        "Adaptive policy "
                        "recalibration proposed."
                    ),
                )
            )

        if policy_state in {
            POLICY_STATE_RESILIENCE_SHIFT,
            POLICY_STATE_SURVIVABILITY_PROTECTION,
        }:

            proposals.append(
                PolicyEvolutionProposal(
                    proposal_id=str(
                        uuid.uuid4()
                    ),
                    proposal_name=(
                        "INCREASE_RESILIENCE_GOVERNANCE"
                    ),
                    priority="CRITICAL",
                    expected_stability_gain=90.0,
                    approval_required=True,
                    rationale=(
                        "Resilience-focused "
                        "policy hardening proposed."
                    ),
                )
            )

        if not proposals:

            proposals.append(
                PolicyEvolutionProposal(
                    proposal_id=str(
                        uuid.uuid4()
                    ),
                    proposal_name=(
                        "MAINTAIN_STABLE_POLICY"
                    ),
                    priority="LOW",
                    expected_stability_gain=95.0,
                    approval_required=False,
                    rationale=(
                        "Policy posture stable."
                    ),
                )
            )

        return proposals

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        policy_state: str,
        policy_result: str,
        governance_success_score: float,
        survivability_success_score: float,
        resilience_success_score: float,
        orchestration_success_score: float,
    ) -> PolicyProjection:

        return PolicyProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                policy_state
            ),
            policy_result=(
                policy_result
            ),
            governance_projection_score=(
                governance_success_score
            ),
            survivability_projection_score=(
                survivability_success_score
            ),
            resilience_projection_score=(
                resilience_success_score
            ),
            orchestration_projection_score=(
                orchestration_success_score
            ),
            rationale=(
                "Policy evolution "
                "projection generated."
            ),
        )

    # ==========================================================
    # FORECAST
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        policy_state: str,
        policy_result: str,
        policy_optimization_score: float,
        governance_success_score: float,
        survivability_success_score: float,
        resilience_success_score: float,
        orchestration_success_score: float,
        depth: int,
    ) -> List[
        PolicyForecastStep
    ]:

        steps = []

        for idx in range(
            max(1, int(depth))
        ):

            steps.append(
                PolicyForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    policy_state=(
                        policy_state
                    ),
                    policy_result=(
                        policy_result
                    ),
                    governance_score=(
                        governance_success_score
                    ),
                    survivability_score=(
                        survivability_success_score
                    ),
                    resilience_score=(
                        resilience_success_score
                    ),
                    orchestration_score=(
                        orchestration_success_score
                    ),
                    rationale=(
                        f"Policy forecast "
                        f"step {idx}."
                    ),
                )
            )

            policy_optimization_score = (
                self._clamp_score(
                    policy_optimization_score
                    + 0.5
                )
            )

            governance_success_score = (
                self._clamp_score(
                    governance_success_score
                    + 0.5
                )
            )

            survivability_success_score = (
                self._clamp_score(
                    survivability_success_score
                    + 0.5
                )
            )

            resilience_success_score = (
                self._clamp_score(
                    resilience_success_score
                    + 0.5
                )
            )

            orchestration_success_score = (
                self._clamp_score(
                    orchestration_success_score
                    + 0.5
                )
            )

        return steps

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignPolicyEvolutionAssessment
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
                "SOVEREIGN_POLICY_EVOLUTION"
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
                f"⚠️ Policy evolution "
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
                f"⚠️ Policy evolution "
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
                f"⚠️ Policy evolution "
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
                    "SOVEREIGN_POLICY_EVOLUTION",
                    payload,
                )

        except Exception as exc:

            print(
                f"⚠️ Policy evolution "
                f"event emit failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            PolicyEvolutionSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> PolicyEvolutionSignal:

        if isinstance(
            item,
            PolicyEvolutionSignal,
        ):
            return item

        return PolicyEvolutionSignal(
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
            governance_success_score=self._clamp_score(
                item.get(
                    "governance_success_score",
                    100.0,
                )
            ),
            survivability_success_score=self._clamp_score(
                item.get(
                    "survivability_success_score",
                    100.0,
                )
            ),
            continuity_success_score=self._clamp_score(
                item.get(
                    "continuity_success_score",
                    100.0,
                )
            ),
            resilience_success_score=self._clamp_score(
                item.get(
                    "resilience_success_score",
                    100.0,
                )
            ),
            orchestration_success_score=self._clamp_score(
                item.get(
                    "orchestration_success_score",
                    100.0,
                )
            ),
            governance_drift_score=self._clamp_score(
                item.get(
                    "governance_drift_score",
                    0.0,
                )
            ),
            sovereignty_pressure_score=self._clamp_score(
                item.get(
                    "sovereignty_pressure_score",
                    0.0,
                )
            ),
            escalation_pressure_score=self._clamp_score(
                item.get(
                    "escalation_pressure_score",
                    0.0,
                )
            ),
            continuity_fragmentation_score=self._clamp_score(
                item.get(
                    "continuity_fragmentation_score",
                    0.0,
                )
            ),
            adaptive_learning_score=self._clamp_score(
                item.get(
                    "adaptive_learning_score",
                    100.0,
                )
            ),
            optimization_opportunity_score=self._clamp_score(
                item.get(
                    "optimization_opportunity_score",
                    0.0,
                )
            ),
            blast_radius_score=self._clamp_score(
                item.get(
                    "blast_radius_score",
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
        SovereignPolicyEvolutionAssessment
    ):

        projection = PolicyProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                POLICY_STATE_STABLE
            ),
            policy_result=(
                POLICY_RESULT_OPTIMIZED
            ),
            governance_projection_score=100.0,
            survivability_projection_score=100.0,
            resilience_projection_score=100.0,
            orchestration_projection_score=100.0,
            rationale=(
                "No policy evolution "
                "signals submitted."
            ),
        )

        return (
            SovereignPolicyEvolutionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                policy_state=(
                    POLICY_STATE_STABLE
                ),
                policy_result=(
                    POLICY_RESULT_OPTIMIZED
                ),
                governance_success_score=100.0,
                survivability_success_score=100.0,
                continuity_success_score=100.0,
                resilience_success_score=100.0,
                orchestration_success_score=100.0,
                governance_drift_score=0.0,
                sovereignty_pressure_score=0.0,
                escalation_pressure_score=0.0,
                continuity_fragmentation_score=0.0,
                adaptive_learning_score=100.0,
                optimization_opportunity_score=100.0,
                blast_radius_score=0.0,
                uncertainty_score=0.0,
                policy_optimization_score=100.0,
                confidence=1.0,
                explainability_score=100.0,
                systemic_risk_probability=0.0,
                signal_count=0,
                engine_count=0,
                severity=(
                    PolicySeverity.INFO.value
                ),
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                threshold_evolutions=[],
                policy_proposals=[],
                strategic_projection=(
                    projection
                ),
                forecast_steps=[],
                telemetry_fusion={},
                rationale=(
                    "No policy evolution "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            PolicyEvolutionSignal
        ],
    ) -> PolicyEvolutionSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .optimization_opportunity_score,
                item
                .governance_drift_score,
                item
                .sovereignty_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[
            PolicyEvolutionSignal
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
            PolicyEvolutionSignal
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
            PolicyEvolutionSignal
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
        policy_state: str,
        policy_result: str,
        policy_optimization_score: float,
    ) -> str:

        return (
            f"Sovereign policy "
            f"evolution completed. "
            f"Policy state "
            f"{policy_state}; "
            f"policy result "
            f"{policy_result}; "
            f"optimization score "
            f"{policy_optimization_score:.2f}."
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or PolicySeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in PolicySeverity
        }

        return (
            value
            if value in valid
            else PolicySeverity.INFO.value
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


def build_sovereign_policy_evolution_engine(
    *,
    event_bus: Optional[Any] = None,
    adaptive_learning_engine: Optional[
        Any
    ] = None,
    execution_governance_engine: Optional[
        Any
    ] = None,
    execution_verification_engine: Optional[
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
    SovereignPolicyEvolutionEngine
):

    return (
        SovereignPolicyEvolutionEngine(
            event_bus=event_bus,
            adaptive_learning_engine=(
                adaptive_learning_engine
            ),
            execution_governance_engine=(
                execution_governance_engine
            ),
            execution_verification_engine=(
                execution_verification_engine
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