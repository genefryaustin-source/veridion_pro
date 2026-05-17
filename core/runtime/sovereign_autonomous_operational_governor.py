"""
core/runtime/sovereign_autonomous_operational_governor.py

Sovereign Autonomous Operational Governor

Sovereign operational governance cognition layer.

This subsystem governs:
- autonomous operational boundaries
- mission-risk tolerances
- survivability governance
- escalation governance
- delegation governance
- sovereign continuity protections
- cross-tenant operational isolation
- replayable governance lineage

IMPORTANT:
This subsystem DOES NOT:
- execute destructive operations
- bypass governance approvals
- disable safety systems
- launch offensive cyber actions
- override tenant sovereignty protections

It ONLY:
- govern operational autonomy
- enforce sovereign operational constraints
- coordinate governance protections
- evaluate operational authority boundaries
- produce replayable governance lineage/evidence
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
    "sovereign_autonomous_operational_governor"
)

DEFAULT_GOVERNANCE_DEPTH = 12


GOVERNANCE_STATE_STABLE = "STABLE"

GOVERNANCE_STATE_REVIEW = (
    "REVIEW"
)

GOVERNANCE_STATE_RESTRICTED = (
    "RESTRICTED"
)

GOVERNANCE_STATE_ESCALATED = (
    "ESCALATED"
)

GOVERNANCE_STATE_CONTINUITY_LOCK = (
    "CONTINUITY_LOCK"
)

GOVERNANCE_STATE_SOVEREIGN_PROTECTION = (
    "SOVEREIGN_PROTECTION"
)

RECOMMENDATION_MONITOR = "MONITOR"

RECOMMENDATION_GOVERNANCE_REVIEW = (
    "GOVERNANCE_REVIEW"
)

RECOMMENDATION_RESTRICT_AUTONOMY = (
    "RESTRICT_AUTONOMY"
)

RECOMMENDATION_ESCALATE_AUTHORITY = (
    "ESCALATE_AUTHORITY"
)

RECOMMENDATION_ENABLE_CONTINUITY_PROTECTION = (
    "ENABLE_CONTINUITY_PROTECTION"
)

RECOMMENDATION_ENABLE_SOVEREIGN_PROTECTION = (
    "ENABLE_SOVEREIGN_PROTECTION"
)


class GovernanceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class GovernanceDomain(str, Enum):
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
class GovernanceDirective:
    directive_id: str

    directive_name: str
    priority: str
    domain: str

    authority_level: str

    confidence_score: float
    sovereignty_impact_score: float
    mission_impact_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GovernanceSignal:
    governance_signal_id: str

    source_engine: str
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

    autonomy_pressure_score: float = (
        0.0
    )

    escalation_pressure_score: float = (
        0.0
    )

    survivability_risk_score: float = (
        0.0
    )

    continuity_risk_score: float = (
        0.0
    )

    governance_violation_risk_score: float = (
        0.0
    )

    tenant_isolation_risk_score: float = (
        0.0
    )

    sovereignty_risk_score: float = (
        0.0
    )

    strategic_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
    )

    directives: List[
        GovernanceDirective
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
class GovernanceSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    recommendation: str

    sovereignty_score: float
    continuity_score: float
    survivability_score: float
    escalation_score: float

    governance_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignOperationalGovernanceAssessment:
    assessment_id: str

    governance_state: str
    recommendation: str

    sovereignty_score: float
    continuity_score: float
    survivability_score: float
    escalation_score: float

    strategic_risk_score: float
    uncertainty_score: float

    governance_risk_score: float

    explainability_score: float
    governance_confidence: float

    severity: str
    confidence: float

    governance_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        GovernanceSimulationStep
    ]

    governance_topology: Dict[str, Any]

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


class SovereignAutonomousOperationalGovernor:
    """
    Sovereign operational governance cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        operational_command_mesh: Optional[
            Any
        ] = None,
        autonomous_defense_director: Optional[
            Any
        ] = None,
        adversarial_reasoning_engine: Optional[
            Any
        ] = None,
        governance_guardrails_engine: Optional[
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

        self.operational_command_mesh = (
            operational_command_mesh
        )

        self.autonomous_defense_director = (
            autonomous_defense_director
        )

        self.adversarial_reasoning_engine = (
            adversarial_reasoning_engine
        )

        self.governance_guardrails_engine = (
            governance_guardrails_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignOperationalGovernanceAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            GovernanceSignal
            | Dict[str, Any]
        ],
        *,
        governance_depth: int = (
            DEFAULT_GOVERNANCE_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalGovernanceAssessment
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

        sovereignty_score = (
            self._avg_score(
                [
                    100.0
                    - s
                    .sovereignty_risk_score
                    for s in normalized
                ]
            )
        )

        continuity_score = (
            self._avg_score(
                [
                    100.0
                    - s
                    .continuity_risk_score
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

        escalation_score = (
            self._avg_score(
                [
                    s
                    .escalation_pressure_score
                    for s in normalized
                ]
            )
        )

        strategic_risk_score = (
            self._avg_score(
                [
                    s
                    .strategic_risk_score
                    for s in normalized
                ]
            )
        )

        uncertainty_score = (
            self._avg_score(
                [
                    s
                    .uncertainty_score
                    for s in normalized
                ]
            )
        )

        governance_risk_score = (
            self
            ._governance_risk_score(
                escalation_score=(
                    escalation_score
                ),
                strategic_risk_score=(
                    strategic_risk_score
                ),
                uncertainty_score=(
                    uncertainty_score
                ),
            )
        )

        governance_state = (
            self._governance_state(
                governance_risk_score=(
                    governance_risk_score
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
                continuity_score=(
                    continuity_score
                ),
                survivability_score=(
                    survivability_score
                ),
            )
        )

        recommendation = (
            self._recommendation(
                governance_state=(
                    governance_state
                ),
                escalation_score=(
                    escalation_score
                ),
                sovereignty_score=(
                    sovereignty_score
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
                governance_state=(
                    governance_state
                ),
                recommendation=(
                    recommendation
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
                continuity_score=(
                    continuity_score
                ),
                survivability_score=(
                    survivability_score
                ),
                escalation_score=(
                    escalation_score
                ),
                governance_depth=(
                    governance_depth
                ),
            )
        )

        assessment = (
            SovereignOperationalGovernanceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                governance_state=(
                    governance_state
                ),
                recommendation=(
                    recommendation
                ),
                sovereignty_score=(
                    sovereignty_score
                ),
                continuity_score=(
                    continuity_score
                ),
                survivability_score=(
                    survivability_score
                ),
                escalation_score=(
                    escalation_score
                ),
                strategic_risk_score=(
                    strategic_risk_score
                ),
                uncertainty_score=(
                    uncertainty_score
                ),
                governance_risk_score=(
                    governance_risk_score
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                governance_confidence=(
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
                governance_depth=(
                    governance_depth
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
                governance_topology=(
                    topology
                ),
                recommended_controls=[
                    (
                        "sovereign_operational_review"
                    ),
                    (
                        "cross_tenant_boundary_validation"
                    ),
                    (
                        "mission_continuity_governance"
                    ),
                ],
                recommended_actions=[
                    {
                        "action": (
                            "review_governance_posture"
                        )
                    },
                    {
                        "action": (
                            "validate_tenant_isolation"
                        )
                    },
                ],
                rationale=(
                    self._build_rationale(
                        governance_state=(
                            governance_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                        governance_risk_score=(
                            governance_risk_score
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
    def _governance_state(
        *,
        governance_risk_score: float,
        sovereignty_score: float,
        continuity_score: float,
        survivability_score: float,
    ) -> str:

        if sovereignty_score <= 40:
            return (
                GOVERNANCE_STATE_SOVEREIGN_PROTECTION
            )

        if continuity_score <= 45:
            return (
                GOVERNANCE_STATE_CONTINUITY_LOCK
            )

        if governance_risk_score >= 75:
            return (
                GOVERNANCE_STATE_ESCALATED
            )

        if survivability_score <= 55:
            return (
                GOVERNANCE_STATE_RESTRICTED
            )

        if governance_risk_score >= 50:
            return (
                GOVERNANCE_STATE_REVIEW
            )

        return GOVERNANCE_STATE_STABLE

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        governance_state: str,
        escalation_score: float,
        sovereignty_score: float,
    ) -> str:

        if (
            governance_state
            == GOVERNANCE_STATE_ESCALATED
        ):
            return (
                RECOMMENDATION_ESCALATE_AUTHORITY
            )

        if (
            governance_state
            == GOVERNANCE_STATE_RESTRICTED
        ):
            return (
                RECOMMENDATION_RESTRICT_AUTONOMY
            )

        if (
            governance_state
            == GOVERNANCE_STATE_CONTINUITY_LOCK
        ):
            return (
                RECOMMENDATION_ENABLE_CONTINUITY_PROTECTION
            )

        if (
            governance_state
            == GOVERNANCE_STATE_SOVEREIGN_PROTECTION
        ):
            return (
                RECOMMENDATION_ENABLE_SOVEREIGN_PROTECTION
            )

        if escalation_score >= 65:
            return (
                RECOMMENDATION_ESCALATE_AUTHORITY
            )

        if sovereignty_score <= 60:
            return (
                RECOMMENDATION_GOVERNANCE_REVIEW
            )

        return RECOMMENDATION_MONITOR

    # ==========================================================
    # RISK
    # ==========================================================

    def _governance_risk_score(
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
            GovernanceSignal
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
                        "authority_level": (
                            directive
                            .authority_level
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
        governance_state: str,
        recommendation: str,
        sovereignty_score: float,
        continuity_score: float,
        survivability_score: float,
        escalation_score: float,
        governance_depth: int,
    ) -> List[
        GovernanceSimulationStep
    ]:

        steps = []

        for idx in range(
            max(1, governance_depth)
        ):

            steps.append(
                GovernanceSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        governance_state
                    ),
                    recommendation=(
                        recommendation
                    ),
                    sovereignty_score=(
                        sovereignty_score
                    ),
                    continuity_score=(
                        continuity_score
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    escalation_score=(
                        escalation_score
                    ),
                    governance_risk_score=(
                        self
                        ._governance_risk_score(
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
                        f"Governance projection "
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
            SovereignOperationalGovernanceAssessment
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
                f"⚠️ Governance memory write failed: {exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            GovernanceSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> GovernanceSignal:

        if isinstance(item, GovernanceSignal):
            return item

        return GovernanceSignal(
            governance_signal_id=str(
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
        SovereignOperationalGovernanceAssessment
    ):

        return (
            SovereignOperationalGovernanceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                governance_state=(
                    GOVERNANCE_STATE_STABLE
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                sovereignty_score=100.0,
                continuity_score=100.0,
                survivability_score=100.0,
                escalation_score=0.0,
                strategic_risk_score=0.0,
                uncertainty_score=0.0,
                governance_risk_score=0.0,
                explainability_score=100.0,
                governance_confidence=1.0,
                severity="INFO",
                confidence=1.0,
                governance_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                governance_topology={},
                recommended_controls=[],
                recommended_actions=[],
                rationale=(
                    "No governance signals submitted."
                ),
                metadata={},
            )
        )

    def _build_rationale(
        self,
        *,
        governance_state: str,
        recommendation: str,
        governance_risk_score: float,
    ) -> str:

        return (
            f"Sovereign operational "
            f"governance evaluation "
            f"completed. "
            f"Governance state "
            f"{governance_state}; "
            f"recommendation "
            f"{recommendation}; "
            f"risk score "
            f"{governance_risk_score:.2f}."
        )

    def _confidence(
        self,
        signals: Sequence[
            GovernanceSignal
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
            GovernanceSignal
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


def build_sovereign_autonomous_operational_governor(
    *,
    event_bus: Optional[Any] = None,
    operational_command_mesh: Optional[
        Any
    ] = None,
    autonomous_defense_director: Optional[
        Any
    ] = None,
    adversarial_reasoning_engine: Optional[
        Any
    ] = None,
    governance_guardrails_engine: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignAutonomousOperationalGovernor:

    return (
        SovereignAutonomousOperationalGovernor(
            event_bus=event_bus,
            operational_command_mesh=(
                operational_command_mesh
            ),
            autonomous_defense_director=(
                autonomous_defense_director
            ),
            adversarial_reasoning_engine=(
                adversarial_reasoning_engine
            ),
            governance_guardrails_engine=(
                governance_guardrails_engine
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