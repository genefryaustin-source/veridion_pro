"""
core/runtime/infrastructure_resilience_correlation_engine.py

Infrastructure Resilience Correlation Engine

Systemic infrastructure survivability and resilience cognition layer.

This subsystem correlates:
- infrastructure instability
- connector degradation
- retry amplification
- failover storms
- rollback amplification
- governance saturation
- verification instability
- telemetry degradation
- survivability degradation
- recovery behavior
- cascading operational failures

IMPORTANT:
This subsystem DOES NOT:
- directly mutate runtime infrastructure
- directly execute recovery actions
- directly quarantine connectors
- directly downgrade autonomy
- directly freeze execution

It ONLY:
- correlates resilience conditions
- evaluates survivability posture
- models infrastructure degradation
- models recovery behavior
- predicts resilience collapse patterns
- emits replayable resilience lineage/evidence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_ENGINE_NAME = (
    "infrastructure_resilience_correlation_engine"
)

RESILIENCE_STATE_STABLE = "STABLE"
RESILIENCE_STATE_ELEVATED = "ELEVATED"
RESILIENCE_STATE_DEGRADED = "DEGRADED"
RESILIENCE_STATE_UNSTABLE = "UNSTABLE"
RESILIENCE_STATE_COLLAPSE_RISK = (
    "COLLAPSE_RISK"
)

RECOVERY_STATE_HEALTHY = "HEALTHY"
RECOVERY_STATE_RECOVERING = "RECOVERING"
RECOVERY_STATE_DEGRADED = "DEGRADED"
RECOVERY_STATE_FAILED = "FAILED"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_RESILIENCE_REVIEW = (
    "RESILIENCE_REVIEW"
)
RECOMMENDATION_RECOVERY_ESCALATION = (
    "RECOVERY_ESCALATION"
)
RECOMMENDATION_FAILOVER_REVIEW = (
    "FAILOVER_REVIEW"
)
RECOMMENDATION_STABILIZATION_REQUIRED = (
    "STABILIZATION_REQUIRED"
)
RECOMMENDATION_INFRASTRUCTURE_ISOLATION = (
    "INFRASTRUCTURE_ISOLATION"
)
RECOMMENDATION_TENANT_ISOLATION = (
    "TENANT_ISOLATION"
)
RECOMMENDATION_AUTONOMY_DOWNGRADE = (
    "AUTONOMY_DOWNGRADE"
)

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = (
    "SUPERVISED_AUTONOMY"
)
AUTONOMY_FULL_AUTONOMY = (
    "FULL_AUTONOMY"
)
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class ResilienceSignalType(str, Enum):
    CONNECTOR_DEGRADATION = (
        "CONNECTOR_DEGRADATION"
    )
    FAILOVER_STORM = "FAILOVER_STORM"
    RETRY_AMPLIFICATION = (
        "RETRY_AMPLIFICATION"
    )
    EXECUTION_INSTABILITY = (
        "EXECUTION_INSTABILITY"
    )
    GOVERNANCE_SATURATION = (
        "GOVERNANCE_SATURATION"
    )
    VERIFICATION_INSTABILITY = (
        "VERIFICATION_INSTABILITY"
    )
    ROLLBACK_AMPLIFICATION = (
        "ROLLBACK_AMPLIFICATION"
    )
    TELEMETRY_DEGRADATION = (
        "TELEMETRY_DEGRADATION"
    )
    SURVIVABILITY_DEGRADATION = (
        "SURVIVABILITY_DEGRADATION"
    )
    RECOVERY_FAILURE = (
        "RECOVERY_FAILURE"
    )
    TENANT_INSTABILITY = (
        "TENANT_INSTABILITY"
    )
    NETWORK_INSTABILITY = (
        "NETWORK_INSTABILITY"
    )
    INFRASTRUCTURE_COLLAPSE_RISK = (
        "INFRASTRUCTURE_COLLAPSE_RISK"
    )
    UNKNOWN = "UNKNOWN"


class ResilienceDomain(str, Enum):
    CONNECTOR = "CONNECTOR"
    FAILOVER = "FAILOVER"
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    VERIFICATION = "VERIFICATION"
    TELEMETRY = "TELEMETRY"
    NETWORK = "NETWORK"
    TENANT = "TENANT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class ResilienceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class InfrastructureResilienceSignal:
    """
    Infrastructure resilience telemetry signal.
    """

    resilience_signal_id: str

    signal_type: str
    domain: str

    source_engine: str
    source_system: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    connector_name: Optional[str] = None

    resilience_pressure_score: float = 0.0
    survivability_score: float = 100.0
    degradation_score: float = 0.0
    instability_score: float = 0.0
    recovery_score: float = 100.0

    retry_count: int = 0
    failover_count: int = 0
    rollback_count: int = 0
    escalation_count: int = 0
    contradiction_count: int = 0

    current_autonomy_mode: str = (
        AUTONOMY_SUPERVISED_AUTONOMY
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
class InfrastructureResilienceAssessment:
    """
    Deterministic infrastructure resilience assessment.
    """

    assessment_id: str

    resilience_state: str
    recovery_state: str
    recommendation: str

    resilience_pressure_score: float
    survivability_score: float
    degradation_score: float
    instability_score: float
    recovery_score: float

    failover_pressure_score: float
    rollback_pressure_score: float
    governance_pressure_score: float
    telemetry_degradation_score: float

    systemic_collapse_risk_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    domain: str
    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    current_autonomy_mode: str
    recommended_autonomy_mode: str

    recommended_actions: List[
        Dict[str, Any]
    ]

    required_controls: List[str]
    constraints: List[str]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class InfrastructureResilienceSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int
    total_assessments_created: int

    last_assessment_id: Optional[str]
    last_resilience_state: Optional[str]
    last_collapse_risk_score: (
        Optional[float]
    )

    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class InfrastructureResilienceCorrelationEngine:
    """
    Sovereign infrastructure resilience cognition layer.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: (
            Optional[Any]
        ) = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            InfrastructureResilienceAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> InfrastructureResilienceAssessment:
        """
        Evaluate infrastructure resilience posture.
        """

        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:

            assessment = (
                self._empty_assessment(
                    tenant_id=tenant_id,
                    case_id=case_id,
                    correlation_id=correlation_id,
                    current_autonomy_mode=(
                        current_autonomy_mode
                    ),
                )
            )

            self._record_assessment(
                assessment,
                context=context,
            )

            return assessment

        selected = (
            self._select_highest_risk_signal(
                normalized
            )
        )

        resilience_pressure = (
            self._resilience_pressure_score(
                normalized
            )
        )

        survivability_score = (
            self._survivability_score(
                normalized
            )
        )

        degradation_score = (
            self._degradation_score(
                normalized
            )
        )

        instability_score = (
            self._instability_score(
                normalized
            )
        )

        recovery_score = (
            self._recovery_score(
                normalized
            )
        )

        failover_pressure = (
            self._failover_pressure_score(
                normalized
            )
        )

        rollback_pressure = (
            self._rollback_pressure_score(
                normalized
            )
        )

        governance_pressure = (
            self._governance_pressure_score(
                normalized
            )
        )

        telemetry_degradation = (
            self
            ._telemetry_degradation_score(
                normalized
            )
        )

        systemic_collapse_risk = (
            self
            ._systemic_collapse_risk_score(
                normalized
            )
        )

        resilience_state = (
            self._determine_resilience_state(
                resilience_pressure=(
                    resilience_pressure
                ),
                degradation_score=(
                    degradation_score
                ),
                instability_score=(
                    instability_score
                ),
                systemic_collapse_risk=(
                    systemic_collapse_risk
                ),
            )
        )

        recovery_state = (
            self._determine_recovery_state(
                recovery_score
            )
        )

        recommendation = (
            self._determine_recommendation(
                selected=selected,
                resilience_state=(
                    resilience_state
                ),
                recovery_state=(
                    recovery_state
                ),
                systemic_collapse_risk=(
                    systemic_collapse_risk
                ),
            )
        )

        recommended_autonomy = (
            self._recommended_autonomy_mode(
                current_autonomy_mode,
                recommendation,
            )
        )

        assessment = (
            InfrastructureResilienceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                resilience_state=(
                    resilience_state
                ),
                recovery_state=(
                    recovery_state
                ),
                recommendation=(
                    recommendation
                ),
                resilience_pressure_score=(
                    resilience_pressure
                ),
                survivability_score=(
                    survivability_score
                ),
                degradation_score=(
                    degradation_score
                ),
                instability_score=(
                    instability_score
                ),
                recovery_score=(
                    recovery_score
                ),
                failover_pressure_score=(
                    failover_pressure
                ),
                rollback_pressure_score=(
                    rollback_pressure
                ),
                governance_pressure_score=(
                    governance_pressure
                ),
                telemetry_degradation_score=(
                    telemetry_degradation
                ),
                systemic_collapse_risk_score=(
                    systemic_collapse_risk
                ),
                selected_signal_id=(
                    selected
                    .resilience_signal_id
                ),
                selected_signal_type=(
                    selected.signal_type
                ),
                domain=selected.domain,
                severity=selected.severity,
                confidence=selected.confidence,
                tenant_id=(
                    tenant_id
                    or selected.tenant_id
                ),
                case_id=(
                    case_id
                    or selected.case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected.correlation_id
                ),
                current_autonomy_mode=(
                    current_autonomy_mode
                ),
                recommended_autonomy_mode=(
                    recommended_autonomy
                ),
                recommended_actions=(
                    self._recommended_actions(
                        selected,
                        resilience_state,
                        recommendation,
                        recommended_autonomy,
                    )
                ),
                required_controls=(
                    self._required_controls(
                        resilience_state,
                        recommendation,
                    )
                ),
                constraints=self._constraints(
                    selected,
                    resilience_state,
                    recommendation,
                ),
                rationale=self._build_rationale(
                    selected=selected,
                    resilience_state=(
                        resilience_state
                    ),
                    recovery_state=(
                        recovery_state
                    ),
                    recommendation=(
                        recommendation
                    ),
                    resilience_pressure=(
                        resilience_pressure
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    degradation_score=(
                        degradation_score
                    ),
                    instability_score=(
                        instability_score
                    ),
                    recovery_score=(
                        recovery_score
                    ),
                    failover_pressure=(
                        failover_pressure
                    ),
                    rollback_pressure=(
                        rollback_pressure
                    ),
                    governance_pressure=(
                        governance_pressure
                    ),
                    telemetry_degradation=(
                        telemetry_degradation
                    ),
                    systemic_collapse_risk=(
                        systemic_collapse_risk
                    ),
                    signal_count=len(
                        normalized
                    ),
                    recommended_autonomy=(
                        recommended_autonomy
                    ),
                ),
                metadata={
                    "evaluated_signal_ids": [
                        item
                        .resilience_signal_id
                        for item in normalized
                    ],
                    "source_engines": sorted(
                        {
                            item.source_engine
                            for item in normalized
                        }
                    ),
                    "source_systems": sorted(
                        {
                            item.source_system
                            for item in normalized
                        }
                    ),
                },
            )
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        return assessment

    def submit(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> InfrastructureResilienceAssessment:
        """
        Compatibility alias.
        """

        return self.evaluate(
            signals,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            current_autonomy_mode=(
                current_autonomy_mode
            ),
            context=context,
        )

    def create_signal(
        self,
        *,
        signal_type: str,
        domain: str,
        source_engine: str,
        source_system: str,
        severity: str,
        confidence: float,
        summary: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        connector_name: Optional[str] = None,
        resilience_pressure_score: (
            float
        ) = 0.0,
        survivability_score: float = (
            100.0
        ),
        degradation_score: float = 0.0,
        instability_score: float = 0.0,
        recovery_score: float = 100.0,
        retry_count: int = 0,
        failover_count: int = 0,
        rollback_count: int = 0,
        escalation_count: int = 0,
        contradiction_count: int = 0,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        payload: Optional[
            Dict[str, Any]
        ] = None,
    ) -> InfrastructureResilienceSignal:
        """
        Convenience constructor.
        """

        return InfrastructureResilienceSignal(
            resilience_signal_id=str(
                uuid.uuid4()
            ),
            signal_type=(
                self._safe_signal_type(
                    signal_type
                )
            ),
            domain=self._safe_domain(
                domain
            ),
            source_engine=(
                source_engine
                or "unknown_engine"
            ),
            source_system=(
                source_system
                or "unknown_system"
            ),
            severity=(
                self._safe_severity(
                    severity
                )
            ),
            confidence=(
                self._clamp_confidence(
                    confidence
                )
            ),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            connector_name=connector_name,
            resilience_pressure_score=(
                self._clamp_score(
                    resilience_pressure_score
                )
            ),
            survivability_score=(
                self._clamp_score(
                    survivability_score
                )
            ),
            degradation_score=(
                self._clamp_score(
                    degradation_score
                )
            ),
            instability_score=(
                self._clamp_score(
                    instability_score
                )
            ),
            recovery_score=(
                self._clamp_score(
                    recovery_score
                )
            ),
            retry_count=max(
                0,
                int(retry_count),
            ),
            failover_count=max(
                0,
                int(failover_count),
            ),
            rollback_count=max(
                0,
                int(rollback_count),
            ),
            escalation_count=max(
                0,
                int(escalation_count),
            ),
            contradiction_count=max(
                0,
                int(contradiction_count),
            ),
            current_autonomy_mode=(
                self._safe_autonomy_mode(
                    current_autonomy_mode
                )
            ),
            payload=payload or {},
        )

    def snapshot(
        self,
    ) -> InfrastructureResilienceSnapshot:

        last = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            InfrastructureResilienceSnapshot(
                engine_name=self.engine_name,
                total_signals_seen=(
                    self._signals_seen
                ),
                total_assessments_created=len(
                    self._assessments
                ),
                last_assessment_id=(
                    last.assessment_id
                    if last
                    else None
                ),
                last_resilience_state=(
                    last.resilience_state
                    if last
                    else None
                ),
                last_collapse_risk_score=(
                    last
                    .systemic_collapse_risk_score
                    if last
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # ========================================================
    # SCORING
    # ========================================================

    def _resilience_pressure_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = sum(
            item.resilience_pressure_score
            for item in signals
        )

        total += (
            sum(
                item.failover_count
                for item in signals
            )
            * 1.5
        )

        total += (
            sum(
                item.retry_count
                for item in signals
            )
            * 1.0
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _survivability_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        total = sum(
            item.survivability_score
            for item in signals
        )

        total -= (
            sum(
                item.rollback_count
                for item in signals
            )
            * 1.5
        )

        return self._clamp_score(
            total / len(signals)
        )

    def _degradation_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = sum(
            item.degradation_score
            for item in signals
        )

        total += (
            sum(
                item.failover_count
                for item in signals
            )
            * 2
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _instability_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = sum(
            item.instability_score
            for item in signals
        )

        total += (
            sum(
                item.retry_count
                for item in signals
            )
            * 1.5
        )

        total += (
            sum(
                item.contradiction_count
                for item in signals
            )
            * 2
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _recovery_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        total = sum(
            item.recovery_score
            for item in signals
        )

        total -= (
            sum(
                item.rollback_count
                for item in signals
            )
            * 1.0
        )

        return self._clamp_score(
            total / len(signals)
        )

    def _failover_pressure_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = (
            sum(
                item.failover_count
                for item in signals
            )
            * 4
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _rollback_pressure_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = (
            sum(
                item.rollback_count
                for item in signals
            )
            * 4
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _governance_pressure_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = (
            sum(
                item.escalation_count
                for item in signals
            )
            * 4
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _telemetry_degradation_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = (
            sum(
                item.contradiction_count
                for item in signals
            )
            * 5
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _systemic_collapse_risk_score(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.resilience_pressure_score
            )

            total += (
                item.degradation_score
            )

            total += (
                item.instability_score
            )

            total += (
                100.0
                - item.survivability_score
            )

        return self._clamp_score(
            total / (max(1, len(signals)) * 4)
        )

    # ========================================================
    # DECISIONING
    # ========================================================

    def _determine_resilience_state(
        self,
        *,
        resilience_pressure: float,
        degradation_score: float,
        instability_score: float,
        systemic_collapse_risk: float,
    ) -> str:

        if systemic_collapse_risk >= 85:
            return (
                RESILIENCE_STATE_COLLAPSE_RISK
            )

        if (
            instability_score >= 70
            or degradation_score >= 70
        ):
            return (
                RESILIENCE_STATE_UNSTABLE
            )

        if (
            resilience_pressure >= 60
        ):
            return (
                RESILIENCE_STATE_DEGRADED
            )

        if (
            resilience_pressure >= 30
        ):
            return (
                RESILIENCE_STATE_ELEVATED
            )

        return RESILIENCE_STATE_STABLE

    def _determine_recovery_state(
        self,
        recovery_score: float,
    ) -> str:

        if recovery_score >= 85:
            return RECOVERY_STATE_HEALTHY

        if recovery_score >= 60:
            return (
                RECOVERY_STATE_RECOVERING
            )

        if recovery_score >= 30:
            return (
                RECOVERY_STATE_DEGRADED
            )

        return RECOVERY_STATE_FAILED

    def _determine_recommendation(
        self,
        *,
        selected: (
            InfrastructureResilienceSignal
        ),
        resilience_state: str,
        recovery_state: str,
        systemic_collapse_risk: float,
    ) -> str:

        if (
            resilience_state
            == RESILIENCE_STATE_COLLAPSE_RISK
        ):
            return (
                RECOMMENDATION_STABILIZATION_REQUIRED
            )

        if (
            recovery_state
            == RECOVERY_STATE_FAILED
        ):
            return (
                RECOMMENDATION_RECOVERY_ESCALATION
            )

        if (
            selected.signal_type
            == ResilienceSignalType
            .FAILOVER_STORM.value
        ):
            return (
                RECOMMENDATION_FAILOVER_REVIEW
            )

        if (
            selected.signal_type
            == ResilienceSignalType
            .TENANT_INSTABILITY.value
        ):
            return (
                RECOMMENDATION_TENANT_ISOLATION
            )

        if (
            selected.signal_type
            == ResilienceSignalType
            .INFRASTRUCTURE_COLLAPSE_RISK.value
        ):
            return (
                RECOMMENDATION_INFRASTRUCTURE_ISOLATION
            )

        if systemic_collapse_risk >= 60:
            return (
                RECOMMENDATION_AUTONOMY_DOWNGRADE
            )

        return RECOMMENDATION_NONE

    def _recommended_autonomy_mode(
        self,
        current_autonomy_mode: str,
        recommendation: str,
    ) -> str:

        if recommendation in {
            RECOMMENDATION_STABILIZATION_REQUIRED,
            RECOMMENDATION_RECOVERY_ESCALATION,
        }:
            return AUTONOMY_MANUAL

        if recommendation in {
            RECOMMENDATION_AUTONOMY_DOWNGRADE,
            RECOMMENDATION_FAILOVER_REVIEW,
        }:
            return self._reduce_autonomy(
                current_autonomy_mode
            )

        return current_autonomy_mode

    # ========================================================
    # OUTPUT BUILDERS
    # ========================================================

    def _recommended_actions(
        self,
        selected: (
            InfrastructureResilienceSignal
        ),
        resilience_state: str,
        recommendation: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:

        actions: List[
            Dict[str, Any]
        ] = []

        if (
            recommendation
            == RECOMMENDATION_AUTONOMY_DOWNGRADE
        ):
            actions.append(
                {
                    "action": (
                        "recommend_autonomy_change"
                    ),
                    "to": (
                        recommended_autonomy
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_STABILIZATION_REQUIRED
        ):
            actions.append(
                {
                    "action": (
                        "recommend_runtime_stabilization"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_RECOVERY_ESCALATION
        ):
            actions.append(
                {
                    "action": (
                        "escalate_recovery_review"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_INFRASTRUCTURE_ISOLATION
        ):
            actions.append(
                {
                    "action": (
                        "recommend_infrastructure_isolation"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_TENANT_ISOLATION
        ):
            actions.append(
                {
                    "action": (
                        "recommend_tenant_isolation"
                    ),
                    "tenant_id": (
                        selected.tenant_id
                    ),
                }
            )

        actions.append(
            {
                "action": (
                    "record_resilience_lineage"
                ),
            }
        )

        actions.append(
            {
                "action": (
                    "record_resilience_evidence"
                ),
            }
        )

        return actions

    def _required_controls(
        self,
        resilience_state: str,
        recommendation: str,
    ) -> List[str]:

        controls: List[str] = []

        if (
            resilience_state
            != RESILIENCE_STATE_STABLE
        ):
            controls.append(
                "resilience_review"
            )

        if recommendation in {
            RECOMMENDATION_RECOVERY_ESCALATION,
            RECOMMENDATION_STABILIZATION_REQUIRED,
        }:
            controls.append(
                "governance_review"
            )

        controls.append(
            "lineage_recording"
        )

        controls.append(
            "evidence_recording"
        )

        return list(
            dict.fromkeys(controls)
        )

    def _constraints(
        self,
        selected: (
            InfrastructureResilienceSignal
        ),
        resilience_state: str,
        recommendation: str,
    ) -> List[str]:

        constraints: List[
            str
        ] = []

        constraints.append(
            f"resilience_state_{resilience_state.lower()}"
        )

        if (
            recommendation
            != RECOMMENDATION_NONE
        ):
            constraints.append(
                f"resilience_recommendation_{recommendation.lower()}"
            )

        if (
            selected.failover_count > 10
        ):
            constraints.append(
                "failover_storm_detected"
            )

        if (
            selected.retry_count > 25
        ):
            constraints.append(
                "retry_amplification_detected"
            )

        if (
            selected.rollback_count > 10
        ):
            constraints.append(
                "rollback_amplification_detected"
            )

        return list(
            dict.fromkeys(constraints)
        )

    def _build_rationale(
        self,
        *,
        selected: (
            InfrastructureResilienceSignal
        ),
        resilience_state: str,
        recovery_state: str,
        recommendation: str,
        resilience_pressure: float,
        survivability_score: float,
        degradation_score: float,
        instability_score: float,
        recovery_score: float,
        failover_pressure: float,
        rollback_pressure: float,
        governance_pressure: float,
        telemetry_degradation: float,
        systemic_collapse_risk: float,
        signal_count: int,
        recommended_autonomy: str,
    ) -> str:

        return (
            f"Infrastructure resilience assessment. "
            f"Selected signal "
            f"{selected.signal_type} from "
            f"{selected.source_engine}. "
            f"Resilience pressure "
            f"{resilience_pressure:.2f}; "
            f"survivability "
            f"{survivability_score:.2f}; "
            f"degradation "
            f"{degradation_score:.2f}; "
            f"instability "
            f"{instability_score:.2f}; "
            f"recovery "
            f"{recovery_score:.2f}; "
            f"failover pressure "
            f"{failover_pressure:.2f}; "
            f"rollback pressure "
            f"{rollback_pressure:.2f}; "
            f"governance pressure "
            f"{governance_pressure:.2f}; "
            f"telemetry degradation "
            f"{telemetry_degradation:.2f}; "
            f"collapse risk "
            f"{systemic_collapse_risk:.2f}. "
            f"Resilience state "
            f"{resilience_state}; "
            f"recovery state "
            f"{recovery_state}; "
            f"recommendation "
            f"{recommendation}; "
            f"recommended autonomy "
            f"{recommended_autonomy}. "
            f"Evaluated across "
            f"{signal_count} signal(s)."
        )

    # ========================================================
    # RECORDING
    # ========================================================

    def _record_assessment(
        self,
        assessment: (
            InfrastructureResilienceAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        self._write_to_memory(
            assessment,
            context=context,
        )

        self._write_to_lineage(
            assessment,
            context=context,
        )

        self._write_to_evidence(
            assessment,
            context=context,
        )

        self._emit_event(
            assessment,
            context=context,
        )

    def _write_to_memory(
        self,
        assessment: (
            InfrastructureResilienceAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        memory = (
            self.operational_memory_engine
        )

        if memory is None:
            return

        payload = {
            "type": (
                "INFRASTRUCTURE_RESILIENCE_ASSESSMENT"
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                memory,
                "append_memory",
            ):
                memory.append_memory(
                    payload
                )

            elif hasattr(
                memory,
                "record",
            ):
                memory.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Resilience memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            InfrastructureResilienceAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        lineage = self.lineage_engine

        if lineage is None:
            return

        payload = {
            "lineage_type": (
                "RESILIENCE"
            ),
            "lineage_status": (
                "RECORDED"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "tenant_id": (
                assessment.tenant_id
            ),
            "case_id": (
                assessment.case_id
            ),
            "correlation_id": (
                assessment.correlation_id
            ),
            "constraints": list(
                assessment.constraints
            ),
            "context": {
                "type": (
                    "INFRASTRUCTURE_RESILIENCE_ASSESSMENT"
                ),
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                lineage,
                "record_lineage",
            ):
                lineage.record_lineage(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Resilience lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            InfrastructureResilienceAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        evidence = (
            self
            .fedramp_evidence_lineage_engine
        )

        if evidence is None:
            return

        payload = {
            "evidence_type": (
                "INFRASTRUCTURE_RESILIENCE"
            ),
            "evidence_status": (
                "RECORDED"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "tenant_id": (
                assessment.tenant_id
            ),
            "case_id": (
                assessment.case_id
            ),
            "correlation_id": (
                assessment.correlation_id
            ),
            "evidence_payload": {
                "type": (
                    "INFRASTRUCTURE_RESILIENCE_ASSESSMENT"
                ),
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                evidence,
                "record_evidence",
            ):
                evidence.record_evidence(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Resilience evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            InfrastructureResilienceAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "INFRASTRUCTURE_RESILIENCE_ASSESSMENT"
            ),
            "engine_name": (
                self.engine_name
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                self.event_bus,
                "emit",
            ):
                self.event_bus.emit(
                    (
                        "INFRASTRUCTURE_RESILIENCE_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Resilience event emit failed: {exc}"
            )

    # ========================================================
    # HELPERS
    # ========================================================

    def _select_highest_risk_signal(
        self,
        signals: Sequence[
            InfrastructureResilienceSignal
        ],
    ) -> InfrastructureResilienceSignal:

        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(
                    item.severity
                ),
                item.resilience_pressure_score,
                item.degradation_score,
                item.instability_score,
                item.failover_count,
                item.rollback_count,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            InfrastructureResilienceSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> InfrastructureResilienceSignal:

        if isinstance(
            item,
            InfrastructureResilienceSignal,
        ):
            return item

        return InfrastructureResilienceSignal(
            resilience_signal_id=str(
                item.get(
                    "resilience_signal_id"
                )
                or uuid.uuid4()
            ),
            signal_type=(
                self._safe_signal_type(
                    item.get(
                        "signal_type"
                    )
                )
            ),
            domain=self._safe_domain(
                item.get("domain")
            ),
            source_engine=str(
                item.get(
                    "source_engine"
                )
                or "unknown_engine"
            ),
            source_system=str(
                item.get(
                    "source_system"
                )
                or "unknown_system"
            ),
            severity=(
                self._safe_severity(
                    item.get(
                        "severity"
                    )
                )
            ),
            confidence=(
                self._clamp_confidence(
                    item.get(
                        "confidence",
                        0.0,
                    )
                )
            ),
            summary=str(
                item.get("summary")
                or ""
            ),
            tenant_id=(
                tenant_id
                or item.get(
                    "tenant_id"
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
            connector_name=item.get(
                "connector_name"
            ),
            resilience_pressure_score=(
                self._clamp_score(
                    item.get(
                        "resilience_pressure_score",
                        0.0,
                    )
                )
            ),
            survivability_score=(
                self._clamp_score(
                    item.get(
                        "survivability_score",
                        100.0,
                    )
                )
            ),
            degradation_score=(
                self._clamp_score(
                    item.get(
                        "degradation_score",
                        0.0,
                    )
                )
            ),
            instability_score=(
                self._clamp_score(
                    item.get(
                        "instability_score",
                        0.0,
                    )
                )
            ),
            recovery_score=(
                self._clamp_score(
                    item.get(
                        "recovery_score",
                        100.0,
                    )
                )
            ),
            retry_count=max(
                0,
                int(
                    item.get(
                        "retry_count",
                        0,
                    )
                    or 0
                ),
            ),
            failover_count=max(
                0,
                int(
                    item.get(
                        "failover_count",
                        0,
                    )
                    or 0
                ),
            ),
            rollback_count=max(
                0,
                int(
                    item.get(
                        "rollback_count",
                        0,
                    )
                    or 0
                ),
            ),
            escalation_count=max(
                0,
                int(
                    item.get(
                        "escalation_count",
                        0,
                    )
                    or 0
                ),
            ),
            contradiction_count=max(
                0,
                int(
                    item.get(
                        "contradiction_count",
                        0,
                    )
                    or 0
                ),
            ),
            current_autonomy_mode=(
                self._safe_autonomy_mode(
                    item.get(
                        "current_autonomy_mode"
                    )
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
        case_id: Optional[str],
        correlation_id: Optional[str],
        current_autonomy_mode: str,
    ) -> InfrastructureResilienceAssessment:

        return (
            InfrastructureResilienceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                resilience_state=(
                    RESILIENCE_STATE_STABLE
                ),
                recovery_state=(
                    RECOVERY_STATE_HEALTHY
                ),
                recommendation=(
                    RECOMMENDATION_NONE
                ),
                resilience_pressure_score=0.0,
                survivability_score=100.0,
                degradation_score=0.0,
                instability_score=0.0,
                recovery_score=100.0,
                failover_pressure_score=0.0,
                rollback_pressure_score=0.0,
                governance_pressure_score=0.0,
                telemetry_degradation_score=0.0,
                systemic_collapse_risk_score=0.0,
                selected_signal_id=None,
                selected_signal_type=None,
                domain=(
                    ResilienceDomain
                    .UNKNOWN.value
                ),
                severity=(
                    ResilienceSeverity
                    .INFO.value
                ),
                confidence=1.0,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
                current_autonomy_mode=(
                    current_autonomy_mode
                ),
                recommended_autonomy_mode=(
                    current_autonomy_mode
                ),
                recommended_actions=[
                    {
                        "action": (
                            "continue_runtime_operations"
                        ),
                    }
                ],
                required_controls=[
                    "lineage_recording",
                    "evidence_recording",
                ],
                constraints=[],
                rationale=(
                    "No resilience signals were submitted."
                ),
                metadata={},
            )
        )

    @staticmethod
    def _safe_signal_type(
        value: Any,
    ) -> str:

        value = str(
            value
            or ResilienceSignalType
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                ResilienceSignalType
            )
        }

        return (
            value
            if value in valid
            else (
                ResilienceSignalType
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or ResilienceDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                ResilienceDomain
            )
        }

        return (
            value
            if value in valid
            else (
                ResilienceDomain
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or ResilienceSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in (
                ResilienceSeverity
            )
        }

        return (
            value
            if value in valid
            else (
                ResilienceSeverity
                .INFO.value
            )
        )

    @staticmethod
    def _safe_autonomy_mode(
        value: Any,
    ) -> str:

        value = str(
            value
            or AUTONOMY_SUPERVISED_AUTONOMY
        ).upper()

        valid = {
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
            AUTONOMY_LOCKDOWN,
        }

        return (
            value
            if value in valid
            else AUTONOMY_SUPERVISED_AUTONOMY
        )

    @staticmethod
    def _clamp_confidence(
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
    def _severity_weight(
        severity: str,
    ) -> int:

        return {
            ResilienceSeverity
            .INFO.value: 0,
            ResilienceSeverity
            .LOW.value: 1,
            ResilienceSeverity
            .MEDIUM.value: 2,
            ResilienceSeverity
            .HIGH.value: 3,
            ResilienceSeverity
            .CRITICAL.value: 4,
        }.get(
            str(severity).upper(),
            0,
        )

    @staticmethod
    def _reduce_autonomy(
        current: str,
    ) -> str:

        current = str(
            current
            or AUTONOMY_SUPERVISED_AUTONOMY
        ).upper()

        order = [
            AUTONOMY_LOCKDOWN,
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
        ]

        if current not in order:
            return AUTONOMY_ASSISTED

        idx = order.index(current)

        return order[
            max(0, idx - 1)
        ]


# ============================================================
# FACTORY
# ============================================================

def build_infrastructure_resilience_correlation_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> InfrastructureResilienceCorrelationEngine:
    """
    Factory for explicit dependency injection.
    """

    return (
        InfrastructureResilienceCorrelationEngine(
            event_bus=event_bus,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )