"""
core/runtime/runtime_telemetry_fusion_engine.py

Runtime Telemetry Fusion Engine

Unified sovereign telemetry cognition layer.

This subsystem fuses:
- runtime cognition telemetry
- execution verification telemetry
- autonomy pressure telemetry
- governance telemetry
- infrastructure telemetry
- resilience telemetry
- connector telemetry
- failover telemetry
- survivability telemetry
- future network telemetry
- future endpoint telemetry

IMPORTANT:
This subsystem DOES NOT:
- execute infrastructure actions
- directly mutate runtime state
- directly freeze autonomy
- directly quarantine tenants/connectors

It ONLY:
- fuses telemetry
- correlates operational conditions
- detects runtime anomalies
- evaluates telemetry trust posture
- builds unified runtime awareness
- emits replayable telemetry lineage/evidence
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

DEFAULT_ENGINE_NAME = "runtime_telemetry_fusion_engine"

RUNTIME_STATE_STABLE = "STABLE"
RUNTIME_STATE_ELEVATED = "ELEVATED"
RUNTIME_STATE_DEGRADED = "DEGRADED"
RUNTIME_STATE_UNSTABLE = "UNSTABLE"
RUNTIME_STATE_CRITICAL = "CRITICAL"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_STABILIZATION_REVIEW = (
    "STABILIZATION_REVIEW"
)
RECOMMENDATION_GOVERNANCE_REVIEW = (
    "GOVERNANCE_REVIEW"
)
RECOMMENDATION_AUTONOMY_DOWNGRADE = (
    "AUTONOMY_DOWNGRADE"
)
RECOMMENDATION_FREEZE_ESCALATION = (
    "FREEZE_ESCALATION"
)
RECOMMENDATION_INFRASTRUCTURE_REVIEW = (
    "INFRASTRUCTURE_REVIEW"
)
RECOMMENDATION_TENANT_ISOLATION = (
    "TENANT_ISOLATION"
)
RECOMMENDATION_CONNECTOR_QUARANTINE = (
    "CONNECTOR_QUARANTINE"
)

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = (
    "SUPERVISED_AUTONOMY"
)
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class TelemetrySignalType(str, Enum):
    EXECUTION_TELEMETRY = (
        "EXECUTION_TELEMETRY"
    )
    GOVERNANCE_TELEMETRY = (
        "GOVERNANCE_TELEMETRY"
    )
    VERIFICATION_TELEMETRY = (
        "VERIFICATION_TELEMETRY"
    )
    CONNECTOR_TELEMETRY = (
        "CONNECTOR_TELEMETRY"
    )
    FAILOVER_TELEMETRY = (
        "FAILOVER_TELEMETRY"
    )
    RESILIENCE_TELEMETRY = (
        "RESILIENCE_TELEMETRY"
    )
    AUTONOMY_TELEMETRY = (
        "AUTONOMY_TELEMETRY"
    )
    NETWORK_TELEMETRY = (
        "NETWORK_TELEMETRY"
    )
    ENDPOINT_TELEMETRY = (
        "ENDPOINT_TELEMETRY"
    )
    INFRASTRUCTURE_TELEMETRY = (
        "INFRASTRUCTURE_TELEMETRY"
    )
    UNKNOWN = "UNKNOWN"


class TelemetryDomain(str, Enum):
    EXECUTION = "EXECUTION"
    GOVERNANCE = "GOVERNANCE"
    VERIFICATION = "VERIFICATION"
    CONNECTOR = "CONNECTOR"
    FAILOVER = "FAILOVER"
    RESILIENCE = "RESILIENCE"
    NETWORK = "NETWORK"
    ENDPOINT = "ENDPOINT"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class TelemetrySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class RuntimeTelemetrySignal:
    """
    Unified telemetry signal entering fusion layer.
    """

    telemetry_signal_id: str
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

    execution_pressure: float = 0.0
    governance_pressure: float = 0.0
    verification_pressure: float = 0.0
    infrastructure_pressure: float = 0.0
    survivability_pressure: float = 0.0

    anomaly_score: float = 0.0
    instability_score: float = 0.0
    telemetry_integrity_score: float = 100.0
    telemetry_reliability_score: float = 100.0

    retry_count: int = 0
    failover_count: int = 0
    rollback_count: int = 0
    contradiction_count: int = 0
    escalation_count: int = 0

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
class RuntimeTelemetryFusionAssessment:
    """
    Deterministic telemetry fusion assessment.
    """

    assessment_id: str

    runtime_state: str
    recommendation: str

    telemetry_integrity_score: float
    telemetry_reliability_score: float
    telemetry_survivability_score: float
    telemetry_confidence_score: float

    operational_stability_score: float
    operational_instability_score: float
    anomaly_pressure_score: float
    governance_saturation_score: float
    systemic_runtime_pressure_score: float

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
class RuntimeTelemetryFusionSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int
    total_assessments_created: int

    last_assessment_id: Optional[str]
    last_runtime_state: Optional[str]
    last_systemic_runtime_pressure_score: (
        Optional[float]
    )

    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class RuntimeTelemetryFusionEngine:
    """
    Unified sovereign telemetry cognition layer.
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
            RuntimeTelemetryFusionAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
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
    ) -> RuntimeTelemetryFusionAssessment:
        """
        Evaluate unified runtime telemetry posture.
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

        telemetry_integrity = (
            self._telemetry_integrity_score(
                normalized
            )
        )

        telemetry_reliability = (
            self._telemetry_reliability_score(
                normalized
            )
        )

        telemetry_survivability = (
            self._telemetry_survivability_score(
                normalized
            )
        )

        telemetry_confidence = (
            self._telemetry_confidence_score(
                normalized
            )
        )

        operational_stability = (
            self._operational_stability_score(
                normalized
            )
        )

        operational_instability = (
            self._operational_instability_score(
                normalized
            )
        )

        anomaly_pressure = (
            self._anomaly_pressure_score(
                normalized
            )
        )

        governance_saturation = (
            self._governance_saturation_score(
                normalized
            )
        )

        systemic_runtime_pressure = (
            self._systemic_runtime_pressure_score(
                normalized
            )
        )

        runtime_state = (
            self._determine_runtime_state(
                telemetry_integrity=(
                    telemetry_integrity
                ),
                operational_instability=(
                    operational_instability
                ),
                anomaly_pressure=(
                    anomaly_pressure
                ),
                governance_saturation=(
                    governance_saturation
                ),
                systemic_runtime_pressure=(
                    systemic_runtime_pressure
                ),
            )
        )

        recommendation = (
            self._determine_recommendation(
                selected=selected,
                runtime_state=runtime_state,
                systemic_runtime_pressure=(
                    systemic_runtime_pressure
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
            RuntimeTelemetryFusionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                runtime_state=runtime_state,
                recommendation=recommendation,
                telemetry_integrity_score=(
                    telemetry_integrity
                ),
                telemetry_reliability_score=(
                    telemetry_reliability
                ),
                telemetry_survivability_score=(
                    telemetry_survivability
                ),
                telemetry_confidence_score=(
                    telemetry_confidence
                ),
                operational_stability_score=(
                    operational_stability
                ),
                operational_instability_score=(
                    operational_instability
                ),
                anomaly_pressure_score=(
                    anomaly_pressure
                ),
                governance_saturation_score=(
                    governance_saturation
                ),
                systemic_runtime_pressure_score=(
                    systemic_runtime_pressure
                ),
                selected_signal_id=(
                    selected
                    .telemetry_signal_id
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
                        runtime_state,
                        recommendation,
                        recommended_autonomy,
                    )
                ),
                required_controls=(
                    self._required_controls(
                        runtime_state,
                        recommendation,
                    )
                ),
                constraints=self._constraints(
                    selected,
                    runtime_state,
                    recommendation,
                ),
                rationale=self._build_rationale(
                    selected=selected,
                    runtime_state=runtime_state,
                    recommendation=recommendation,
                    telemetry_integrity=(
                        telemetry_integrity
                    ),
                    telemetry_reliability=(
                        telemetry_reliability
                    ),
                    telemetry_survivability=(
                        telemetry_survivability
                    ),
                    telemetry_confidence=(
                        telemetry_confidence
                    ),
                    operational_stability=(
                        operational_stability
                    ),
                    operational_instability=(
                        operational_instability
                    ),
                    anomaly_pressure=(
                        anomaly_pressure
                    ),
                    governance_saturation=(
                        governance_saturation
                    ),
                    systemic_runtime_pressure=(
                        systemic_runtime_pressure
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
                        .telemetry_signal_id
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
            RuntimeTelemetrySignal
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
    ) -> RuntimeTelemetryFusionAssessment:
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
        execution_pressure: float = 0.0,
        governance_pressure: float = 0.0,
        verification_pressure: float = 0.0,
        infrastructure_pressure: float = 0.0,
        survivability_pressure: float = 0.0,
        anomaly_score: float = 0.0,
        instability_score: float = 0.0,
        telemetry_integrity_score: float = (
            100.0
        ),
        telemetry_reliability_score: float = (
            100.0
        ),
        retry_count: int = 0,
        failover_count: int = 0,
        rollback_count: int = 0,
        contradiction_count: int = 0,
        escalation_count: int = 0,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        payload: Optional[
            Dict[str, Any]
        ] = None,
    ) -> RuntimeTelemetrySignal:
        """
        Convenience constructor.
        """

        return RuntimeTelemetrySignal(
            telemetry_signal_id=str(
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
            execution_pressure=(
                self._clamp_score(
                    execution_pressure
                )
            ),
            governance_pressure=(
                self._clamp_score(
                    governance_pressure
                )
            ),
            verification_pressure=(
                self._clamp_score(
                    verification_pressure
                )
            ),
            infrastructure_pressure=(
                self._clamp_score(
                    infrastructure_pressure
                )
            ),
            survivability_pressure=(
                self._clamp_score(
                    survivability_pressure
                )
            ),
            anomaly_score=(
                self._clamp_score(
                    anomaly_score
                )
            ),
            instability_score=(
                self._clamp_score(
                    instability_score
                )
            ),
            telemetry_integrity_score=(
                self._clamp_score(
                    telemetry_integrity_score
                )
            ),
            telemetry_reliability_score=(
                self._clamp_score(
                    telemetry_reliability_score
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
            contradiction_count=max(
                0,
                int(contradiction_count),
            ),
            escalation_count=max(
                0,
                int(escalation_count),
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
    ) -> RuntimeTelemetryFusionSnapshot:

        last = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            RuntimeTelemetryFusionSnapshot(
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
                last_runtime_state=(
                    last.runtime_state
                    if last
                    else None
                ),
                last_systemic_runtime_pressure_score=(
                    last
                    .systemic_runtime_pressure_score
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

    def _telemetry_integrity_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        total = sum(
            item.telemetry_integrity_score
            for item in signals
        )

        total -= (
            sum(
                item.contradiction_count
                for item in signals
            )
            * 3
        )

        return self._clamp_score(
            total / len(signals)
        )

    def _telemetry_reliability_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        total = sum(
            item.telemetry_reliability_score
            for item in signals
        )

        total -= (
            sum(
                item.failover_count
                for item in signals
            )
            * 2
        )

        total -= (
            sum(
                item.retry_count
                for item in signals
            )
            * 1.5
        )

        return self._clamp_score(
            total / len(signals)
        )

    def _telemetry_survivability_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        score = 100.0

        score -= (
            sum(
                item.rollback_count
                for item in signals
            )
            * 2
        )

        score -= (
            sum(
                item.failover_count
                for item in signals
            )
            * 1.5
        )

        return self._clamp_score(score)

    def _telemetry_confidence_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        total = sum(
            item.confidence * 100
            for item in signals
        )

        return self._clamp_score(
            total / len(signals)
        )

    def _operational_stability_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        score = 100.0

        score -= (
            sum(
                item.instability_score
                for item in signals
            )
            / max(1, len(signals))
        )

        score -= (
            sum(
                item.anomaly_score
                for item in signals
            )
            / max(1, len(signals))
        )

        return self._clamp_score(score)

    def _operational_instability_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
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
            * 0.5
        )

        total += (
            sum(
                item.failover_count
                for item in signals
            )
            * 1.5
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _anomaly_pressure_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        total = sum(
            item.anomaly_score
            for item in signals
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

    def _governance_saturation_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        total = (
            sum(
                item.governance_pressure
                for item in signals
            )
            + (
                sum(
                    item.escalation_count
                    for item in signals
                )
                * 3
            )
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _systemic_runtime_pressure_score(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.execution_pressure
            )

            total += (
                item.governance_pressure
            )

            total += (
                item.verification_pressure
            )

            total += (
                item.infrastructure_pressure
            )

            total += (
                item.survivability_pressure
            )

        return self._clamp_score(
            total / (max(1, len(signals)) * 5)
        )

    # ========================================================
    # DECISIONING
    # ========================================================

    def _determine_runtime_state(
        self,
        *,
        telemetry_integrity: float,
        operational_instability: float,
        anomaly_pressure: float,
        governance_saturation: float,
        systemic_runtime_pressure: float,
    ) -> str:

        if (
            telemetry_integrity <= 20
            or systemic_runtime_pressure
            >= 85
        ):
            return RUNTIME_STATE_CRITICAL

        if (
            operational_instability >= 70
            or anomaly_pressure >= 70
        ):
            return RUNTIME_STATE_UNSTABLE

        if (
            governance_saturation >= 60
            or systemic_runtime_pressure
            >= 60
        ):
            return RUNTIME_STATE_DEGRADED

        if (
            systemic_runtime_pressure
            >= 30
        ):
            return RUNTIME_STATE_ELEVATED

        return RUNTIME_STATE_STABLE

    def _determine_recommendation(
        self,
        *,
        selected: RuntimeTelemetrySignal,
        runtime_state: str,
        systemic_runtime_pressure: float,
    ) -> str:

        if (
            runtime_state
            == RUNTIME_STATE_CRITICAL
        ):
            return (
                RECOMMENDATION_FREEZE_ESCALATION
            )

        if (
            runtime_state
            == RUNTIME_STATE_UNSTABLE
        ):
            return (
                RECOMMENDATION_STABILIZATION_REVIEW
            )

        if (
            runtime_state
            == RUNTIME_STATE_DEGRADED
        ):
            return (
                RECOMMENDATION_GOVERNANCE_REVIEW
            )

        if (
            selected.domain
            == TelemetryDomain
            .INFRASTRUCTURE.value
        ):
            return (
                RECOMMENDATION_INFRASTRUCTURE_REVIEW
            )

        if (
            selected.domain
            == TelemetryDomain
            .CONNECTOR.value
        ):
            return (
                RECOMMENDATION_CONNECTOR_QUARANTINE
            )

        if systemic_runtime_pressure >= 55:
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
            RECOMMENDATION_FREEZE_ESCALATION,
            RECOMMENDATION_GOVERNANCE_REVIEW,
        }:
            return AUTONOMY_MANUAL

        if recommendation in {
            RECOMMENDATION_AUTONOMY_DOWNGRADE,
            RECOMMENDATION_STABILIZATION_REVIEW,
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
        selected: RuntimeTelemetrySignal,
        runtime_state: str,
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
            == RECOMMENDATION_FREEZE_ESCALATION
        ):
            actions.append(
                {
                    "action": (
                        "recommend_runtime_freeze"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_GOVERNANCE_REVIEW
        ):
            actions.append(
                {
                    "action": (
                        "escalate_governance_review"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_CONNECTOR_QUARANTINE
        ):
            actions.append(
                {
                    "action": (
                        "recommend_connector_quarantine"
                    ),
                    "connector_name": (
                        selected.connector_name
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_INFRASTRUCTURE_REVIEW
        ):
            actions.append(
                {
                    "action": (
                        "request_infrastructure_review"
                    ),
                }
            )

        actions.append(
            {
                "action": (
                    "record_telemetry_lineage"
                ),
            }
        )

        actions.append(
            {
                "action": (
                    "record_telemetry_evidence"
                ),
            }
        )

        return actions

    def _required_controls(
        self,
        runtime_state: str,
        recommendation: str,
    ) -> List[str]:

        controls: List[str] = []

        if (
            runtime_state
            != RUNTIME_STATE_STABLE
        ):
            controls.append(
                "runtime_review"
            )

        if recommendation in {
            RECOMMENDATION_GOVERNANCE_REVIEW,
            RECOMMENDATION_FREEZE_ESCALATION,
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
        selected: RuntimeTelemetrySignal,
        runtime_state: str,
        recommendation: str,
    ) -> List[str]:

        constraints: List[
            str
        ] = []

        constraints.append(
            f"runtime_state_{runtime_state.lower()}"
        )

        if (
            recommendation
            != RECOMMENDATION_NONE
        ):
            constraints.append(
                f"telemetry_recommendation_{recommendation.lower()}"
            )

        if (
            selected.retry_count > 25
        ):
            constraints.append(
                "retry_amplification_detected"
            )

        if (
            selected.failover_count > 10
        ):
            constraints.append(
                "failover_instability_detected"
            )

        if (
            selected.contradiction_count
            > 10
        ):
            constraints.append(
                "telemetry_contradiction_detected"
            )

        return list(
            dict.fromkeys(constraints)
        )

    def _build_rationale(
        self,
        *,
        selected: RuntimeTelemetrySignal,
        runtime_state: str,
        recommendation: str,
        telemetry_integrity: float,
        telemetry_reliability: float,
        telemetry_survivability: float,
        telemetry_confidence: float,
        operational_stability: float,
        operational_instability: float,
        anomaly_pressure: float,
        governance_saturation: float,
        systemic_runtime_pressure: float,
        signal_count: int,
        recommended_autonomy: str,
    ) -> str:

        return (
            f"Runtime telemetry fusion assessment. "
            f"Selected signal "
            f"{selected.signal_type} from "
            f"{selected.source_engine}. "
            f"Telemetry integrity "
            f"{telemetry_integrity:.2f}; "
            f"telemetry reliability "
            f"{telemetry_reliability:.2f}; "
            f"telemetry survivability "
            f"{telemetry_survivability:.2f}; "
            f"telemetry confidence "
            f"{telemetry_confidence:.2f}; "
            f"operational stability "
            f"{operational_stability:.2f}; "
            f"operational instability "
            f"{operational_instability:.2f}; "
            f"anomaly pressure "
            f"{anomaly_pressure:.2f}; "
            f"governance saturation "
            f"{governance_saturation:.2f}; "
            f"systemic runtime pressure "
            f"{systemic_runtime_pressure:.2f}. "
            f"Runtime state "
            f"{runtime_state}; "
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
            RuntimeTelemetryFusionAssessment
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
            RuntimeTelemetryFusionAssessment
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
                "RUNTIME_TELEMETRY_FUSION_ASSESSMENT"
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
                f"⚠️ Telemetry memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            RuntimeTelemetryFusionAssessment
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
                "TELEMETRY"
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
                    "RUNTIME_TELEMETRY_FUSION_ASSESSMENT"
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
                f"⚠️ Telemetry lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            RuntimeTelemetryFusionAssessment
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
                "RUNTIME_TELEMETRY"
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
                    "RUNTIME_TELEMETRY_FUSION_ASSESSMENT"
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
                f"⚠️ Telemetry evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            RuntimeTelemetryFusionAssessment
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
                "RUNTIME_TELEMETRY_FUSION_ASSESSMENT"
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
                        "RUNTIME_TELEMETRY_FUSION_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Telemetry event emit failed: {exc}"
            )

    # ========================================================
    # HELPERS
    # ========================================================

    def _select_highest_risk_signal(
        self,
        signals: Sequence[
            RuntimeTelemetrySignal
        ],
    ) -> RuntimeTelemetrySignal:

        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(
                    item.severity
                ),
                item.anomaly_score,
                item.instability_score,
                item.execution_pressure,
                item.governance_pressure,
                item.verification_pressure,
                item.infrastructure_pressure,
                item.survivability_pressure,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            RuntimeTelemetrySignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> RuntimeTelemetrySignal:

        if isinstance(
            item,
            RuntimeTelemetrySignal,
        ):
            return item

        return RuntimeTelemetrySignal(
            telemetry_signal_id=str(
                item.get(
                    "telemetry_signal_id"
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
            execution_pressure=(
                self._clamp_score(
                    item.get(
                        "execution_pressure",
                        0.0,
                    )
                )
            ),
            governance_pressure=(
                self._clamp_score(
                    item.get(
                        "governance_pressure",
                        0.0,
                    )
                )
            ),
            verification_pressure=(
                self._clamp_score(
                    item.get(
                        "verification_pressure",
                        0.0,
                    )
                )
            ),
            infrastructure_pressure=(
                self._clamp_score(
                    item.get(
                        "infrastructure_pressure",
                        0.0,
                    )
                )
            ),
            survivability_pressure=(
                self._clamp_score(
                    item.get(
                        "survivability_pressure",
                        0.0,
                    )
                )
            ),
            anomaly_score=(
                self._clamp_score(
                    item.get(
                        "anomaly_score",
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
            telemetry_integrity_score=(
                self._clamp_score(
                    item.get(
                        "telemetry_integrity_score",
                        100.0,
                    )
                )
            ),
            telemetry_reliability_score=(
                self._clamp_score(
                    item.get(
                        "telemetry_reliability_score",
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
    ) -> RuntimeTelemetryFusionAssessment:

        return (
            RuntimeTelemetryFusionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                runtime_state=(
                    RUNTIME_STATE_STABLE
                ),
                recommendation=(
                    RECOMMENDATION_NONE
                ),
                telemetry_integrity_score=100.0,
                telemetry_reliability_score=100.0,
                telemetry_survivability_score=100.0,
                telemetry_confidence_score=100.0,
                operational_stability_score=100.0,
                operational_instability_score=0.0,
                anomaly_pressure_score=0.0,
                governance_saturation_score=0.0,
                systemic_runtime_pressure_score=0.0,
                selected_signal_id=None,
                selected_signal_type=None,
                domain=(
                    TelemetryDomain
                    .UNKNOWN.value
                ),
                severity=(
                    TelemetrySeverity
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
                    "No telemetry signals were submitted."
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
            or TelemetrySignalType
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                TelemetrySignalType
            )
        }

        return (
            value
            if value in valid
            else (
                TelemetrySignalType
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or TelemetryDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                TelemetryDomain
            )
        }

        return (
            value
            if value in valid
            else (
                TelemetryDomain
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or TelemetrySeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in (
                TelemetrySeverity
            )
        }

        return (
            value
            if value in valid
            else (
                TelemetrySeverity
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
            TelemetrySeverity
            .INFO.value: 0,
            TelemetrySeverity
            .LOW.value: 1,
            TelemetrySeverity
            .MEDIUM.value: 2,
            TelemetrySeverity
            .HIGH.value: 3,
            TelemetrySeverity
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

def build_runtime_telemetry_fusion_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> RuntimeTelemetryFusionEngine:
    """
    Factory for explicit dependency injection.
    """

    return RuntimeTelemetryFusionEngine(
        event_bus=event_bus,
        operational_memory_engine=(
            operational_memory_engine
        ),
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=(
            fedramp_evidence_lineage_engine
        ),
    )