"""
core/runtime/sovereign_autonomy_pressure_engine.py

Sovereign Autonomy Pressure Engine

Systemic runtime autonomy pressure cognition layer.

This subsystem evaluates:
- execution pressure
- governance pressure
- verification pressure
- infrastructure pressure
- survivability pressure
- escalation pressure
- retry amplification
- rollback frequency
- freeze escalation frequency
- connector instability
- tenant instability
- runaway autonomy conditions

IMPORTANT:
This subsystem DOES NOT:
- execute connectors
- directly freeze infrastructure
- directly downgrade autonomy
- directly mutate tenant state
- directly trigger rollback

It ONLY:
- evaluates systemic autonomy pressure
- correlates runtime instability
- recommends stabilization actions
- emits replayable pressure lineage/evidence
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

DEFAULT_ENGINE_NAME = "sovereign_autonomy_pressure_engine"

PRESSURE_NORMAL = "NORMAL"
PRESSURE_ELEVATED = "ELEVATED"
PRESSURE_HIGH = "HIGH"
PRESSURE_CRITICAL = "CRITICAL"
PRESSURE_RUNAWAY = "RUNAWAY"
PRESSURE_STABILIZATION_REQUIRED = "STABILIZATION_REQUIRED"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_AUTONOMY_DOWNGRADE = "AUTONOMY_DOWNGRADE"
RECOMMENDATION_FREEZE_ESCALATION = "FREEZE_ESCALATION"
RECOMMENDATION_ROLLBACK_ONLY = "ROLLBACK_ONLY"
RECOMMENDATION_GOVERNANCE_INTERVENTION = "GOVERNANCE_INTERVENTION"
RECOMMENDATION_CONNECTOR_QUARANTINE = "CONNECTOR_QUARANTINE"
RECOMMENDATION_TENANT_ISOLATION = "TENANT_ISOLATION"
RECOMMENDATION_MANUAL_REVIEW = "MANUAL_REVIEW"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class AutonomyPressureSignalType(str, Enum):
    EXECUTION_SURGE = "EXECUTION_SURGE"
    EXECUTION_CONCURRENCY = "EXECUTION_CONCURRENCY"
    RETRY_AMPLIFICATION = "RETRY_AMPLIFICATION"
    GOVERNANCE_ESCALATION = "GOVERNANCE_ESCALATION"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    FAILOVER_STORM = "FAILOVER_STORM"
    ROLLBACK_FREQUENCY = "ROLLBACK_FREQUENCY"
    CONNECTOR_DEGRADATION = "CONNECTOR_DEGRADATION"
    CONTRADICTION_PRESSURE = "CONTRADICTION_PRESSURE"
    AUTONOMY_DOWNGRADE = "AUTONOMY_DOWNGRADE"
    FREEZE_ESCALATION = "FREEZE_ESCALATION"
    TENANT_INSTABILITY = "TENANT_INSTABILITY"
    NETWORK_PRESSURE = "NETWORK_PRESSURE"
    INFRASTRUCTURE_PRESSURE = "INFRASTRUCTURE_PRESSURE"
    UNKNOWN = "UNKNOWN"


class PressureDomain(str, Enum):
    EXECUTION = "EXECUTION"
    GOVERNANCE = "GOVERNANCE"
    VERIFICATION = "VERIFICATION"
    CONNECTOR = "CONNECTOR"
    TENANT = "TENANT"
    NETWORK = "NETWORK"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class PressureSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class SovereignAutonomyPressureSignal:
    """
    Runtime autonomy pressure signal.
    """

    pressure_signal_id: str
    signal_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    connector_name: Optional[str] = None

    execution_count: int = 0
    concurrent_execution_count: int = 0
    retry_count: int = 0
    governance_escalation_count: int = 0
    verification_failure_count: int = 0
    failover_count: int = 0
    rollback_count: int = 0
    freeze_count: int = 0
    contradiction_count: int = 0
    autonomy_downgrade_count: int = 0

    current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignAutonomyPressureAssessment:
    """
    Deterministic systemic pressure assessment.
    """

    assessment_id: str
    pressure_status: str
    recommendation: str

    autonomy_pressure_score: float
    governance_pressure_score: float
    verification_pressure_score: float
    infrastructure_pressure_score: float
    survivability_pressure_score: float
    escalation_pressure_score: float
    systemic_pressure_score: float

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

    recommended_actions: List[Dict[str, Any]]
    required_controls: List[str]
    constraints: List[str]
    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignAutonomyPressureSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str
    total_signals_seen: int
    total_assessments_created: int
    last_assessment_id: Optional[str]
    last_pressure_status: Optional[str]
    last_systemic_pressure_score: Optional[float]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class SovereignAutonomyPressureEngine:
    """
    Systemic runtime autonomy pressure cognition layer.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            SovereignAutonomyPressureAssessment
        ] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignAutonomyPressureAssessment:
        """
        Evaluate systemic autonomy pressure.
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

            assessment = self._empty_assessment(
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
                current_autonomy_mode=current_autonomy_mode,
            )

            self._record_assessment(
                assessment,
                context=context,
            )

            return assessment

        selected = self._select_highest_risk_signal(
            normalized
        )

        autonomy_pressure = (
            self._autonomy_pressure_score(
                normalized
            )
        )

        governance_pressure = (
            self._governance_pressure_score(
                normalized
            )
        )

        verification_pressure = (
            self._verification_pressure_score(
                normalized
            )
        )

        infrastructure_pressure = (
            self._infrastructure_pressure_score(
                normalized
            )
        )

        survivability_pressure = (
            self._survivability_pressure_score(
                normalized
            )
        )

        escalation_pressure = (
            self._escalation_pressure_score(
                normalized
            )
        )

        systemic_pressure = (
            self._systemic_pressure_score(
                autonomy_pressure,
                governance_pressure,
                verification_pressure,
                infrastructure_pressure,
                survivability_pressure,
                escalation_pressure,
            )
        )

        pressure_status = (
            self._determine_pressure_status(
                selected=selected,
                systemic_pressure=systemic_pressure,
            )
        )

        recommendation = (
            self._determine_recommendation(
                selected=selected,
                pressure_status=pressure_status,
                systemic_pressure=systemic_pressure,
            )
        )

        recommended_autonomy = (
            self._recommended_autonomy_mode(
                current_autonomy_mode,
                recommendation,
                systemic_pressure,
            )
        )

        assessment = (
            SovereignAutonomyPressureAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                pressure_status=pressure_status,
                recommendation=recommendation,
                autonomy_pressure_score=(
                    autonomy_pressure
                ),
                governance_pressure_score=(
                    governance_pressure
                ),
                verification_pressure_score=(
                    verification_pressure
                ),
                infrastructure_pressure_score=(
                    infrastructure_pressure
                ),
                survivability_pressure_score=(
                    survivability_pressure
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                systemic_pressure_score=(
                    systemic_pressure
                ),
                selected_signal_id=(
                    selected.pressure_signal_id
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
                        pressure_status,
                        recommendation,
                        recommended_autonomy,
                    )
                ),
                required_controls=(
                    self._required_controls(
                        selected,
                        pressure_status,
                        recommendation,
                    )
                ),
                constraints=self._constraints(
                    selected,
                    pressure_status,
                    recommendation,
                ),
                rationale=self._build_rationale(
                    selected=selected,
                    pressure_status=pressure_status,
                    recommendation=recommendation,
                    autonomy_pressure=autonomy_pressure,
                    governance_pressure=governance_pressure,
                    verification_pressure=verification_pressure,
                    infrastructure_pressure=infrastructure_pressure,
                    survivability_pressure=survivability_pressure,
                    escalation_pressure=escalation_pressure,
                    systemic_pressure=systemic_pressure,
                    signal_count=len(normalized),
                    recommended_autonomy=recommended_autonomy,
                ),
                metadata={
                    "evaluated_signal_ids": [
                        item.pressure_signal_id
                        for item in normalized
                    ],
                    "connector_names": sorted(
                        {
                            item.connector_name
                            for item in normalized
                            if item.connector_name
                        }
                    ),
                    "aggregate_counts": (
                        self._aggregate_counts(
                            normalized
                        )
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
            SovereignAutonomyPressureSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignAutonomyPressureAssessment:
        """
        Compatibility alias.
        """

        return self.evaluate(
            signals,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            current_autonomy_mode=current_autonomy_mode,
            context=context,
        )

    def create_signal(
        self,
        *,
        signal_type: str,
        domain: str,
        source_engine: str,
        severity: str,
        confidence: float,
        summary: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        connector_name: Optional[str] = None,
        execution_count: int = 0,
        concurrent_execution_count: int = 0,
        retry_count: int = 0,
        governance_escalation_count: int = 0,
        verification_failure_count: int = 0,
        failover_count: int = 0,
        rollback_count: int = 0,
        freeze_count: int = 0,
        contradiction_count: int = 0,
        autonomy_downgrade_count: int = 0,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        payload: Optional[Dict[str, Any]] = None,
    ) -> SovereignAutonomyPressureSignal:
        """
        Convenience constructor.
        """

        return SovereignAutonomyPressureSignal(
            pressure_signal_id=str(
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
            severity=self._safe_severity(
                severity
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
            execution_count=max(
                0,
                int(execution_count),
            ),
            concurrent_execution_count=max(
                0,
                int(
                    concurrent_execution_count
                ),
            ),
            retry_count=max(
                0,
                int(retry_count),
            ),
            governance_escalation_count=max(
                0,
                int(
                    governance_escalation_count
                ),
            ),
            verification_failure_count=max(
                0,
                int(
                    verification_failure_count
                ),
            ),
            failover_count=max(
                0,
                int(failover_count),
            ),
            rollback_count=max(
                0,
                int(rollback_count),
            ),
            freeze_count=max(
                0,
                int(freeze_count),
            ),
            contradiction_count=max(
                0,
                int(
                    contradiction_count
                ),
            ),
            autonomy_downgrade_count=max(
                0,
                int(
                    autonomy_downgrade_count
                ),
            ),
            current_autonomy_mode=(
                self._safe_autonomy_mode(
                    current_autonomy_mode
                )
            ),
            payload=payload or {},
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[
        SovereignAutonomyPressureAssessment
    ]:

        limit = max(1, int(limit))

        return list(
            reversed(self._assessments[-limit:])
        )

    def snapshot(
        self,
    ) -> SovereignAutonomyPressureSnapshot:

        last = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            SovereignAutonomyPressureSnapshot(
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
                last_pressure_status=(
                    last.pressure_status
                    if last
                    else None
                ),
                last_systemic_pressure_score=(
                    last.systemic_pressure_score
                    if last
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # --------------------------------------------------------
    # SCORING
    # --------------------------------------------------------

    def _autonomy_pressure_score(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.execution_count
                * 0.5
            )

            total += (
                item.concurrent_execution_count
                * 1.5
            )

            total += (
                item.retry_count
                * 2
            )

            total += (
                item.autonomy_downgrade_count
                * 3
            )

            if (
                item.current_autonomy_mode
                == AUTONOMY_FULL_AUTONOMY
            ):
                total += 15

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _governance_pressure_score(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.governance_escalation_count
                * 4
            )

            total += (
                item.freeze_count
                * 5
            )

            total += (
                item.rollback_count
                * 3
            )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _verification_pressure_score(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.verification_failure_count
                * 5
            )

            total += (
                item.contradiction_count
                * 6
            )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _infrastructure_pressure_score(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.failover_count
                * 4
            )

            total += (
                item.retry_count
                * 2
            )

            if (
                item.signal_type
                == AutonomyPressureSignalType
                .CONNECTOR_DEGRADATION.value
            ):
                total += 20

            if (
                item.signal_type
                == AutonomyPressureSignalType
                .NETWORK_PRESSURE.value
            ):
                total += 25

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _survivability_pressure_score(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.rollback_count
                * 4
            )

            total += (
                item.freeze_count
                * 5
            )

            total += (
                item.failover_count
                * 3
            )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _escalation_pressure_score(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.governance_escalation_count
                * 5
            )

            total += (
                item.freeze_count
                * 4
            )

            total += (
                item.autonomy_downgrade_count
                * 3
            )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _systemic_pressure_score(
        self,
        autonomy_pressure: float,
        governance_pressure: float,
        verification_pressure: float,
        infrastructure_pressure: float,
        survivability_pressure: float,
        escalation_pressure: float,
    ) -> float:

        total = (
            autonomy_pressure
            + governance_pressure
            + verification_pressure
            + infrastructure_pressure
            + survivability_pressure
            + escalation_pressure
        )

        return self._clamp_score(
            total / 6
        )

    # --------------------------------------------------------
    # DECISIONING
    # --------------------------------------------------------

    def _determine_pressure_status(
        self,
        *,
        selected: SovereignAutonomyPressureSignal,
        systemic_pressure: float,
    ) -> str:

        if systemic_pressure >= 90:
            return PRESSURE_RUNAWAY

        if systemic_pressure >= 75:
            return (
                PRESSURE_STABILIZATION_REQUIRED
            )

        if systemic_pressure >= 60:
            return PRESSURE_CRITICAL

        if systemic_pressure >= 40:
            return PRESSURE_HIGH

        if systemic_pressure >= 20:
            return PRESSURE_ELEVATED

        return PRESSURE_NORMAL

    def _determine_recommendation(
        self,
        *,
        selected: SovereignAutonomyPressureSignal,
        pressure_status: str,
        systemic_pressure: float,
    ) -> str:

        if (
            pressure_status
            == PRESSURE_RUNAWAY
        ):
            return (
                RECOMMENDATION_FREEZE_ESCALATION
            )

        if (
            pressure_status
            == PRESSURE_STABILIZATION_REQUIRED
        ):
            return (
                RECOMMENDATION_GOVERNANCE_INTERVENTION
            )

        if (
            selected.signal_type
            == AutonomyPressureSignalType
            .TENANT_INSTABILITY.value
        ):
            return (
                RECOMMENDATION_TENANT_ISOLATION
            )

        if (
            selected.signal_type
            == AutonomyPressureSignalType
            .CONNECTOR_DEGRADATION.value
        ):
            return (
                RECOMMENDATION_CONNECTOR_QUARANTINE
            )

        if systemic_pressure >= 55:
            return (
                RECOMMENDATION_AUTONOMY_DOWNGRADE
            )

        if systemic_pressure >= 45:
            return (
                RECOMMENDATION_MANUAL_REVIEW
            )

        return RECOMMENDATION_NONE

    def _recommended_autonomy_mode(
        self,
        current_autonomy_mode: str,
        recommendation: str,
        systemic_pressure: float,
    ) -> str:

        if recommendation in {
            RECOMMENDATION_FREEZE_ESCALATION,
            RECOMMENDATION_GOVERNANCE_INTERVENTION,
        }:
            return AUTONOMY_MANUAL

        if recommendation in {
            RECOMMENDATION_AUTONOMY_DOWNGRADE,
            RECOMMENDATION_MANUAL_REVIEW,
        }:
            return self._reduce_autonomy(
                current_autonomy_mode
            )

        return current_autonomy_mode

    # --------------------------------------------------------
    # OUTPUT BUILDERS
    # --------------------------------------------------------

    def _recommended_actions(
        self,
        selected: SovereignAutonomyPressureSignal,
        pressure_status: str,
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
            == RECOMMENDATION_ROLLBACK_ONLY
        ):
            actions.append(
                {
                    "action": (
                        "recommend_rollback_only_mode"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_GOVERNANCE_INTERVENTION
        ):
            actions.append(
                {
                    "action": (
                        "escalate_to_governance"
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

        if (
            recommendation
            == RECOMMENDATION_MANUAL_REVIEW
        ):
            actions.append(
                {
                    "action": (
                        "request_manual_review"
                    ),
                }
            )

        actions.append(
            {
                "action": (
                    "record_pressure_lineage"
                ),
            }
        )

        actions.append(
            {
                "action": (
                    "record_pressure_evidence"
                ),
            }
        )

        return actions

    def _required_controls(
        self,
        selected: SovereignAutonomyPressureSignal,
        pressure_status: str,
        recommendation: str,
    ) -> List[str]:

        controls: List[str] = []

        if (
            pressure_status
            != PRESSURE_NORMAL
        ):
            controls.append(
                "runtime_pressure_review"
            )

        if (
            recommendation
            == RECOMMENDATION_GOVERNANCE_INTERVENTION
        ):
            controls.append(
                "governance_review"
            )

        if (
            recommendation
            == RECOMMENDATION_FREEZE_ESCALATION
        ):
            controls.append(
                "freeze_review"
            )

        if (
            recommendation
            == RECOMMENDATION_TENANT_ISOLATION
        ):
            controls.append(
                "tenant_review"
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
        selected: SovereignAutonomyPressureSignal,
        pressure_status: str,
        recommendation: str,
    ) -> List[str]:

        constraints: List[
            str
        ] = []

        constraints.append(
            f"pressure_status_{pressure_status.lower()}"
        )

        if (
            recommendation
            != RECOMMENDATION_NONE
        ):
            constraints.append(
                f"pressure_recommendation_{recommendation.lower()}"
            )

        if (
            selected.execution_count
            > 100
        ):
            constraints.append(
                "high_execution_volume"
            )

        if (
            selected.concurrent_execution_count
            > 50
        ):
            constraints.append(
                "high_execution_concurrency"
            )

        if (
            selected.retry_count
            > 25
        ):
            constraints.append(
                "retry_amplification_detected"
            )

        return list(
            dict.fromkeys(constraints)
        )

    def _build_rationale(
        self,
        *,
        selected: SovereignAutonomyPressureSignal,
        pressure_status: str,
        recommendation: str,
        autonomy_pressure: float,
        governance_pressure: float,
        verification_pressure: float,
        infrastructure_pressure: float,
        survivability_pressure: float,
        escalation_pressure: float,
        systemic_pressure: float,
        signal_count: int,
        recommended_autonomy: str,
    ) -> str:

        return (
            f"Sovereign autonomy pressure assessment. "
            f"Selected signal "
            f"{selected.signal_type} from "
            f"{selected.source_engine}. "
            f"Autonomy pressure "
            f"{autonomy_pressure:.2f}; "
            f"governance pressure "
            f"{governance_pressure:.2f}; "
            f"verification pressure "
            f"{verification_pressure:.2f}; "
            f"infrastructure pressure "
            f"{infrastructure_pressure:.2f}; "
            f"survivability pressure "
            f"{survivability_pressure:.2f}; "
            f"escalation pressure "
            f"{escalation_pressure:.2f}; "
            f"systemic pressure "
            f"{systemic_pressure:.2f}. "
            f"Status {pressure_status}; "
            f"recommendation {recommendation}; "
            f"recommended autonomy "
            f"{recommended_autonomy}. "
            f"Evaluated across "
            f"{signal_count} signal(s)."
        )

    # --------------------------------------------------------
    # RECORDING
    # --------------------------------------------------------

    def _record_assessment(
        self,
        assessment: SovereignAutonomyPressureAssessment,
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
        assessment: SovereignAutonomyPressureAssessment,
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
                "SOVEREIGN_AUTONOMY_PRESSURE_ASSESSMENT"
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

            elif hasattr(
                memory,
                "write",
            ):
                memory.write(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Pressure memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: SovereignAutonomyPressureAssessment,
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
                "RUNTIME"
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
            "mission_priority": 0,
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
            "verification_requirements": list(
                assessment.required_controls
            ),
            "context": {
                "type": (
                    "SOVEREIGN_AUTONOMY_PRESSURE_ASSESSMENT"
                ),
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
            "metadata": {
                "assessment_id": (
                    assessment.assessment_id
                ),
                "pressure_status": (
                    assessment.pressure_status
                ),
                "recommendation": (
                    assessment.recommendation
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

            elif hasattr(
                lineage,
                "append_lineage",
            ):
                lineage.append_lineage(
                    payload
                )

            elif hasattr(
                lineage,
                "record",
            ):
                lineage.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Pressure lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: SovereignAutonomyPressureAssessment,
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
                "POLICY_EVALUATION"
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
            "mission_priority": 0,
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
            "evidence_payload": {
                "type": (
                    "SOVEREIGN_AUTONOMY_PRESSURE_ASSESSMENT"
                ),
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
            "metadata": {
                "assessment_id": (
                    assessment.assessment_id
                ),
                "pressure_status": (
                    assessment.pressure_status
                ),
                "recommendation": (
                    assessment.recommendation
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

            elif hasattr(
                evidence,
                "append_evidence",
            ):
                evidence.append_evidence(
                    payload
                )

            elif hasattr(
                evidence,
                "record",
            ):
                evidence.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Pressure evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: SovereignAutonomyPressureAssessment,
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "SOVEREIGN_AUTONOMY_PRESSURE_ASSESSMENT"
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
                        "SOVEREIGN_AUTONOMY_PRESSURE_ASSESSMENT"
                    ),
                    payload,
                )

            elif hasattr(
                self.event_bus,
                "publish",
            ):
                self.event_bus.publish(
                    (
                        "SOVEREIGN_AUTONOMY_PRESSURE_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Pressure event emit failed: {exc}"
            )

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def _select_highest_risk_signal(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> SovereignAutonomyPressureSignal:

        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(
                    item.severity
                ),
                self._signal_type_weight(
                    item.signal_type
                ),
                item.concurrent_execution_count,
                item.retry_count,
                item.governance_escalation_count,
                item.verification_failure_count,
                item.failover_count,
                item.freeze_count,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _aggregate_counts(
        self,
        signals: Sequence[
            SovereignAutonomyPressureSignal
        ],
    ) -> Dict[str, int]:

        return {
            "execution_count": sum(
                item.execution_count
                for item in signals
            ),
            "concurrent_execution_count": sum(
                item.concurrent_execution_count
                for item in signals
            ),
            "retry_count": sum(
                item.retry_count
                for item in signals
            ),
            "governance_escalation_count": sum(
                item.governance_escalation_count
                for item in signals
            ),
            "verification_failure_count": sum(
                item.verification_failure_count
                for item in signals
            ),
            "failover_count": sum(
                item.failover_count
                for item in signals
            ),
            "rollback_count": sum(
                item.rollback_count
                for item in signals
            ),
            "freeze_count": sum(
                item.freeze_count
                for item in signals
            ),
        }

    def _normalize_signal(
        self,
        item: (
            SovereignAutonomyPressureSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignAutonomyPressureSignal:

        if isinstance(
            item,
            SovereignAutonomyPressureSignal,
        ):
            return item

        return SovereignAutonomyPressureSignal(
            pressure_signal_id=str(
                item.get(
                    "pressure_signal_id"
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
            execution_count=max(
                0,
                int(
                    item.get(
                        "execution_count",
                        0,
                    )
                    or 0
                ),
            ),
            concurrent_execution_count=max(
                0,
                int(
                    item.get(
                        "concurrent_execution_count",
                        0,
                    )
                    or 0
                ),
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
            governance_escalation_count=max(
                0,
                int(
                    item.get(
                        "governance_escalation_count",
                        0,
                    )
                    or 0
                ),
            ),
            verification_failure_count=max(
                0,
                int(
                    item.get(
                        "verification_failure_count",
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
            freeze_count=max(
                0,
                int(
                    item.get(
                        "freeze_count",
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
            autonomy_downgrade_count=max(
                0,
                int(
                    item.get(
                        "autonomy_downgrade_count",
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
    ) -> SovereignAutonomyPressureAssessment:

        return (
            SovereignAutonomyPressureAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                pressure_status=(
                    PRESSURE_NORMAL
                ),
                recommendation=(
                    RECOMMENDATION_NONE
                ),
                autonomy_pressure_score=0.0,
                governance_pressure_score=0.0,
                verification_pressure_score=0.0,
                infrastructure_pressure_score=0.0,
                survivability_pressure_score=0.0,
                escalation_pressure_score=0.0,
                systemic_pressure_score=0.0,
                selected_signal_id=None,
                selected_signal_type=None,
                domain=(
                    PressureDomain
                    .UNKNOWN.value
                ),
                severity=(
                    PressureSeverity
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
                    "No runtime pressure signals were submitted."
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
            or AutonomyPressureSignalType
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                AutonomyPressureSignalType
            )
        }

        return (
            value
            if value in valid
            else (
                AutonomyPressureSignalType
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or PressureDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in PressureDomain
        }

        return (
            value
            if value in valid
            else PressureDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or PressureSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in PressureSeverity
        }

        return (
            value
            if value in valid
            else PressureSeverity
            .INFO.value
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
            PressureSeverity
            .INFO.value: 0,
            PressureSeverity
            .LOW.value: 1,
            PressureSeverity
            .MEDIUM.value: 2,
            PressureSeverity
            .HIGH.value: 3,
            PressureSeverity
            .CRITICAL.value: 4,
        }.get(
            str(severity).upper(),
            0,
        )

    @staticmethod
    def _signal_type_weight(
        signal_type: str,
    ) -> int:

        return {
            AutonomyPressureSignalType
            .EXECUTION_SURGE.value: 3,

            AutonomyPressureSignalType
            .EXECUTION_CONCURRENCY.value: 4,

            AutonomyPressureSignalType
            .RETRY_AMPLIFICATION.value: 5,

            AutonomyPressureSignalType
            .GOVERNANCE_ESCALATION.value: 4,

            AutonomyPressureSignalType
            .VERIFICATION_FAILURE.value: 5,

            AutonomyPressureSignalType
            .FAILOVER_STORM.value: 5,

            AutonomyPressureSignalType
            .ROLLBACK_FREQUENCY.value: 4,

            AutonomyPressureSignalType
            .CONNECTOR_DEGRADATION.value: 4,

            AutonomyPressureSignalType
            .CONTRADICTION_PRESSURE.value: 5,

            AutonomyPressureSignalType
            .AUTONOMY_DOWNGRADE.value: 3,

            AutonomyPressureSignalType
            .FREEZE_ESCALATION.value: 5,

            AutonomyPressureSignalType
            .TENANT_INSTABILITY.value: 5,

            AutonomyPressureSignalType
            .NETWORK_PRESSURE.value: 4,

            AutonomyPressureSignalType
            .INFRASTRUCTURE_PRESSURE.value: 4,

            AutonomyPressureSignalType
            .UNKNOWN.value: 1,
        }.get(
            str(signal_type).upper(),
            1,
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

def build_sovereign_autonomy_pressure_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignAutonomyPressureEngine:
    """
    Factory for explicit dependency injection.
    """

    return SovereignAutonomyPressureEngine(
        event_bus=event_bus,
        operational_memory_engine=(
            operational_memory_engine
        ),
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=(
            fedramp_evidence_lineage_engine
        ),
    )