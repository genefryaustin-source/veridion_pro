"""
core/runtime/execution_verification_mesh.py

Execution Verification Mesh

Distributed autonomous execution verification cognition layer.

This subsystem coordinates:
- connector verification
- telemetry verification
- rollback verification
- cross-source verification correlation
- contradictory verification detection
- verification drift detection
- verification confidence scoring
- governance escalation recommendations

IMPORTANT:
This subsystem DOES NOT:
- execute connectors
- mutate external systems
- directly trigger rollback
- directly freeze infrastructure
- directly modify autonomy mode

It ONLY:
- evaluates verification posture
- correlates verification evidence
- scores verification integrity/confidence
- recommends escalation/retry/governance actions
- records replayable verification lineage/evidence
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

DEFAULT_ENGINE_NAME = "execution_verification_mesh"

VERIFICATION_VERIFIED = "VERIFIED"
VERIFICATION_PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
VERIFICATION_UNVERIFIED = "UNVERIFIED"
VERIFICATION_CONFLICTED = "CONFLICTED"
VERIFICATION_STALE = "STALE"
VERIFICATION_ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"
VERIFICATION_ESCALATION_REQUIRED = "ESCALATION_REQUIRED"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_RETRY_VERIFICATION = "RETRY_VERIFICATION"
RECOMMENDATION_SECONDARY_VERIFICATION = "SECONDARY_VERIFICATION"
RECOMMENDATION_GOVERNANCE_ESCALATION = "GOVERNANCE_ESCALATION"
RECOMMENDATION_ROLLBACK_ESCALATION = "ROLLBACK_ESCALATION"
RECOMMENDATION_CONNECTOR_DISTRUST = "CONNECTOR_DISTRUST"
RECOMMENDATION_AUTONOMY_DOWNGRADE = "AUTONOMY_DOWNGRADE"
RECOMMENDATION_FREEZE_ESCALATION = "FREEZE_ESCALATION"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class VerificationSignalType(str, Enum):
    CONNECTOR_CONFIRMATION = "CONNECTOR_CONFIRMATION"
    TELEMETRY_CONFIRMATION = "TELEMETRY_CONFIRMATION"
    SECONDARY_CONFIRMATION = "SECONDARY_CONFIRMATION"
    ROLLBACK_CONFIRMATION = "ROLLBACK_CONFIRMATION"
    CONTRADICTORY_CONFIRMATION = "CONTRADICTORY_CONFIRMATION"
    VERIFICATION_TIMEOUT = "VERIFICATION_TIMEOUT"
    VERIFICATION_DRIFT = "VERIFICATION_DRIFT"
    STALE_CONFIRMATION = "STALE_CONFIRMATION"
    NETWORK_CORRELATION = "NETWORK_CORRELATION"
    UNKNOWN = "UNKNOWN"


class VerificationDomain(str, Enum):
    EMAIL = "EMAIL"
    IDENTITY = "IDENTITY"
    ENDPOINT = "ENDPOINT"
    NETWORK = "NETWORK"
    CLOUD = "CLOUD"
    GOVERNANCE = "GOVERNANCE"
    ROLLBACK = "ROLLBACK"
    GENERIC = "GENERIC"
    UNKNOWN = "UNKNOWN"


class VerificationSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class ExecutionVerificationSignal:
    """
    Verification signal entering the mesh.
    """

    verification_signal_id: str
    execution_id: str
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
    action_type: Optional[str] = None

    verification_successful: bool = False
    contradictory: bool = False
    stale: bool = False
    rollback_related: bool = False

    latency_ms: Optional[int] = None

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class ExecutionVerificationAssessment:
    """
    Deterministic verification assessment.
    """

    assessment_id: str
    execution_id: str
    verification_status: str
    recommendation: str

    verification_confidence_score: float
    verification_integrity_score: float
    verification_survivability_score: float
    cross_source_consistency_score: float
    verification_pressure_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    domain: str
    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    connector_name: Optional[str]
    action_type: Optional[str]

    current_autonomy_mode: str
    recommended_autonomy_mode: str

    recommended_actions: List[Dict[str, Any]]
    required_controls: List[str]
    constraints: List[str]
    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class ExecutionVerificationMeshSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str
    total_signals_seen: int
    total_assessments_created: int
    tracked_execution_ids: List[str]
    last_assessment_id: Optional[str]
    last_execution_id: Optional[str]
    last_verification_status: Optional[str]
    last_confidence_score: Optional[float]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class ExecutionVerificationMesh:
    """
    Distributed execution verification cognition layer.
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
            ExecutionVerificationAssessment
        ] = []

        self._latest_by_execution: Dict[
            str,
            ExecutionVerificationAssessment,
        ] = {}

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        signals: Sequence[
            ExecutionVerificationSignal | Dict[str, Any]
        ],
        *,
        execution_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionVerificationAssessment:
        """
        Evaluate verification posture across one or more
        verification signals.
        """

        normalized = [
            self._normalize_signal(
                item,
                execution_id=execution_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:
            assessment = self._unknown_assessment(
                execution_id=execution_id or "UNKNOWN",
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

        verification_confidence = (
            self._verification_confidence_score(
                normalized
            )
        )

        verification_integrity = (
            self._verification_integrity_score(
                normalized
            )
        )

        verification_survivability = (
            self._verification_survivability_score(
                normalized
            )
        )

        cross_source_consistency = (
            self._cross_source_consistency_score(
                normalized
            )
        )

        verification_pressure = (
            self._verification_pressure_score(
                normalized
            )
        )

        verification_status = (
            self._determine_verification_status(
                selected=selected,
                verification_confidence=verification_confidence,
                verification_integrity=verification_integrity,
                verification_survivability=verification_survivability,
                cross_source_consistency=cross_source_consistency,
                verification_pressure=verification_pressure,
            )
        )

        recommendation = self._determine_recommendation(
            selected=selected,
            verification_status=verification_status,
            verification_pressure=verification_pressure,
        )

        recommended_autonomy = (
            self._recommended_autonomy_mode(
                current_autonomy_mode,
                verification_status,
                recommendation,
            )
        )

        assessment = ExecutionVerificationAssessment(
            assessment_id=str(uuid.uuid4()),
            execution_id=(
                execution_id
                or selected.execution_id
            ),
            verification_status=verification_status,
            recommendation=recommendation,
            verification_confidence_score=(
                verification_confidence
            ),
            verification_integrity_score=(
                verification_integrity
            ),
            verification_survivability_score=(
                verification_survivability
            ),
            cross_source_consistency_score=(
                cross_source_consistency
            ),
            verification_pressure_score=(
                verification_pressure
            ),
            selected_signal_id=(
                selected.verification_signal_id
            ),
            selected_signal_type=selected.signal_type,
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
            connector_name=selected.connector_name,
            action_type=selected.action_type,
            current_autonomy_mode=(
                current_autonomy_mode
            ),
            recommended_autonomy_mode=(
                recommended_autonomy
            ),
            recommended_actions=(
                self._recommended_actions(
                    selected,
                    verification_status,
                    recommendation,
                    recommended_autonomy,
                )
            ),
            required_controls=(
                self._required_controls(
                    selected,
                    verification_status,
                    recommendation,
                    recommended_autonomy,
                )
            ),
            constraints=self._constraints(
                selected,
                verification_status,
                recommendation,
            ),
            rationale=self._build_rationale(
                selected=selected,
                verification_status=verification_status,
                recommendation=recommendation,
                verification_confidence=verification_confidence,
                verification_integrity=verification_integrity,
                verification_survivability=verification_survivability,
                cross_source_consistency=cross_source_consistency,
                verification_pressure=verification_pressure,
                signal_count=len(normalized),
                recommended_autonomy=recommended_autonomy,
            ),
            metadata={
                "evaluated_signal_ids": [
                    item.verification_signal_id
                    for item in normalized
                ],
                "source_systems": sorted(
                    {
                        item.source_system
                        for item in normalized
                    }
                ),
                "contradiction_count": sum(
                    1
                    for item in normalized
                    if item.contradictory
                ),
                "stale_count": sum(
                    1
                    for item in normalized
                    if item.stale
                ),
                "rollback_related_count": sum(
                    1
                    for item in normalized
                    if item.rollback_related
                ),
            },
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        return assessment

    def submit(
        self,
        signals: Sequence[
            ExecutionVerificationSignal | Dict[str, Any]
        ],
        *,
        execution_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[Dict[str, Any]] = None,
    ) -> ExecutionVerificationAssessment:
        """
        Compatibility alias.
        """

        return self.evaluate(
            signals,
            execution_id=execution_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            current_autonomy_mode=current_autonomy_mode,
            context=context,
        )

    def create_signal(
        self,
        *,
        execution_id: str,
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
        action_type: Optional[str] = None,
        verification_successful: bool = False,
        contradictory: bool = False,
        stale: bool = False,
        rollback_related: bool = False,
        latency_ms: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> ExecutionVerificationSignal:
        """
        Convenience constructor.
        """

        return ExecutionVerificationSignal(
            verification_signal_id=str(
                uuid.uuid4()
            ),
            execution_id=str(
                execution_id or "UNKNOWN"
            ),
            signal_type=self._safe_signal_type(
                signal_type
            ),
            domain=self._safe_domain(domain),
            source_engine=(
                source_engine or "unknown_engine"
            ),
            source_system=(
                source_system or "unknown_system"
            ),
            severity=self._safe_severity(
                severity
            ),
            confidence=self._clamp_confidence(
                confidence
            ),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            connector_name=connector_name,
            action_type=action_type,
            verification_successful=(
                verification_successful
            ),
            contradictory=contradictory,
            stale=stale,
            rollback_related=rollback_related,
            latency_ms=(
                latency_ms
                if latency_ms is None
                else max(0, int(latency_ms))
            ),
            payload=payload or {},
        )

    def get_latest_assessment(
        self,
        execution_id: str,
    ) -> Optional[
        ExecutionVerificationAssessment
    ]:
        return self._latest_by_execution.get(
            str(execution_id or "UNKNOWN")
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[
        ExecutionVerificationAssessment
    ]:
        limit = max(1, int(limit))

        return list(
            reversed(self._assessments[-limit:])
        )

    def snapshot(
        self,
    ) -> ExecutionVerificationMeshSnapshot:

        last = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return ExecutionVerificationMeshSnapshot(
            engine_name=self.engine_name,
            total_signals_seen=self._signals_seen,
            total_assessments_created=len(
                self._assessments
            ),
            tracked_execution_ids=sorted(
                self._latest_by_execution.keys()
            ),
            last_assessment_id=(
                last.assessment_id
                if last
                else None
            ),
            last_execution_id=(
                last.execution_id
                if last
                else None
            ),
            last_verification_status=(
                last.verification_status
                if last
                else None
            ),
            last_confidence_score=(
                last.verification_confidence_score
                if last
                else None
            ),
            last_updated_ms=int(
                time.time() * 1000
            ),
        )

    # --------------------------------------------------------
    # SCORING
    # --------------------------------------------------------

    def _verification_confidence_score(
        self,
        signals: Sequence[
            ExecutionVerificationSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        total = 0.0

        for item in signals:

            if item.verification_successful:
                total += 20

            total += (
                self._severity_weight(
                    item.severity
                )
                * 2
            )

            total += (
                item.confidence * 25
            )

            if (
                item.signal_type
                == VerificationSignalType
                .SECONDARY_CONFIRMATION.value
            ):
                total += 15

            if (
                item.signal_type
                == VerificationSignalType
                .TELEMETRY_CONFIRMATION.value
            ):
                total += 20

            if item.rollback_related:
                total += 5

            if item.contradictory:
                total -= 30

            if item.stale:
                total -= 20

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _verification_integrity_score(
        self,
        signals: Sequence[
            ExecutionVerificationSignal
        ],
    ) -> float:

        score = 100.0

        contradictions = sum(
            1
            for item in signals
            if item.contradictory
        )

        stale = sum(
            1
            for item in signals
            if item.stale
        )

        score -= contradictions * 25
        score -= stale * 10

        return self._clamp_score(score)

    def _verification_survivability_score(
        self,
        signals: Sequence[
            ExecutionVerificationSignal
        ],
    ) -> float:

        score = 100.0

        for item in signals:

            if (
                item.signal_type
                == VerificationSignalType
                .VERIFICATION_TIMEOUT.value
            ):
                score -= 20

            if (
                item.signal_type
                == VerificationSignalType
                .VERIFICATION_DRIFT.value
            ):
                score -= 25

            if item.rollback_related:
                score -= 5

        return self._clamp_score(score)

    def _cross_source_consistency_score(
        self,
        signals: Sequence[
            ExecutionVerificationSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        systems = {
            item.source_system
            for item in signals
        }

        contradictions = sum(
            1
            for item in signals
            if item.contradictory
        )

        score = min(
            100.0,
            50 + (len(systems) * 10),
        )

        score -= contradictions * 25

        return self._clamp_score(score)

    def _verification_pressure_score(
        self,
        signals: Sequence[
            ExecutionVerificationSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                self._severity_weight(
                    item.severity
                )
                * 8
            )

            total += (
                self._signal_type_weight(
                    item.signal_type
                )
                * 6
            )

            if item.contradictory:
                total += 25

            if item.stale:
                total += 15

            if (
                item.signal_type
                == VerificationSignalType
                .VERIFICATION_TIMEOUT.value
            ):
                total += 20

            if (
                item.signal_type
                == VerificationSignalType
                .VERIFICATION_DRIFT.value
            ):
                total += 30

        return self._clamp_score(
            total / max(1, len(signals))
        )

    # --------------------------------------------------------
    # DECISIONING
    # --------------------------------------------------------

    def _determine_verification_status(
        self,
        *,
        selected: ExecutionVerificationSignal,
        verification_confidence: float,
        verification_integrity: float,
        verification_survivability: float,
        cross_source_consistency: float,
        verification_pressure: float,
    ) -> str:

        if selected.contradictory:
            return VERIFICATION_CONFLICTED

        if selected.stale:
            return VERIFICATION_STALE

        if (
            verification_pressure >= 85
            or verification_integrity <= 25
        ):
            return (
                VERIFICATION_ESCALATION_REQUIRED
            )

        if (
            verification_survivability <= 25
        ):
            return (
                VERIFICATION_ROLLBACK_REQUIRED
            )

        if (
            verification_confidence <= 35
            or cross_source_consistency <= 35
        ):
            return VERIFICATION_UNVERIFIED

        if (
            verification_confidence <= 65
        ):
            return (
                VERIFICATION_PARTIALLY_VERIFIED
            )

        return VERIFICATION_VERIFIED

    def _determine_recommendation(
        self,
        *,
        selected: ExecutionVerificationSignal,
        verification_status: str,
        verification_pressure: float,
    ) -> str:

        if (
            verification_status
            == VERIFICATION_CONFLICTED
        ):
            return (
                RECOMMENDATION_GOVERNANCE_ESCALATION
            )

        if (
            verification_status
            == VERIFICATION_STALE
        ):
            return (
                RECOMMENDATION_RETRY_VERIFICATION
            )

        if (
            verification_status
            == VERIFICATION_ROLLBACK_REQUIRED
        ):
            return (
                RECOMMENDATION_ROLLBACK_ESCALATION
            )

        if (
            verification_status
            == VERIFICATION_ESCALATION_REQUIRED
        ):
            return (
                RECOMMENDATION_FREEZE_ESCALATION
            )

        if (
            verification_status
            == VERIFICATION_UNVERIFIED
        ):
            return (
                RECOMMENDATION_SECONDARY_VERIFICATION
            )

        if (
            verification_pressure >= 60
        ):
            return (
                RECOMMENDATION_AUTONOMY_DOWNGRADE
            )

        if selected.contradictory:
            return (
                RECOMMENDATION_CONNECTOR_DISTRUST
            )

        return RECOMMENDATION_NONE

    def _recommended_autonomy_mode(
        self,
        current_autonomy_mode: str,
        verification_status: str,
        recommendation: str,
    ) -> str:

        if recommendation in {
            RECOMMENDATION_FREEZE_ESCALATION,
            RECOMMENDATION_ROLLBACK_ESCALATION,
        }:
            return AUTONOMY_MANUAL

        if recommendation in {
            RECOMMENDATION_GOVERNANCE_ESCALATION,
            RECOMMENDATION_AUTONOMY_DOWNGRADE,
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
        selected: ExecutionVerificationSignal,
        verification_status: str,
        recommendation: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:

        actions: List[
            Dict[str, Any]
        ] = []

        if (
            recommendation
            == RECOMMENDATION_RETRY_VERIFICATION
        ):
            actions.append(
                {
                    "action": (
                        "retry_verification"
                    ),
                    "execution_id": (
                        selected.execution_id
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_SECONDARY_VERIFICATION
        ):
            actions.append(
                {
                    "action": (
                        "request_secondary_verification"
                    ),
                    "execution_id": (
                        selected.execution_id
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_GOVERNANCE_ESCALATION
        ):
            actions.append(
                {
                    "action": (
                        "escalate_to_governance"
                    ),
                    "execution_id": (
                        selected.execution_id
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_ROLLBACK_ESCALATION
        ):
            actions.append(
                {
                    "action": (
                        "escalate_rollback_review"
                    ),
                    "execution_id": (
                        selected.execution_id
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
                        "recommend_execution_freeze"
                    ),
                    "execution_id": (
                        selected.execution_id
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_CONNECTOR_DISTRUST
        ):
            actions.append(
                {
                    "action": (
                        "reduce_connector_trust"
                    ),
                    "connector_name": (
                        selected.connector_name
                    ),
                }
            )

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

        actions.append(
            {
                "action": (
                    "record_verification_lineage"
                ),
            }
        )

        actions.append(
            {
                "action": (
                    "record_verification_evidence"
                ),
            }
        )

        return actions

    def _required_controls(
        self,
        selected: ExecutionVerificationSignal,
        verification_status: str,
        recommendation: str,
        recommended_autonomy: str,
    ) -> List[str]:

        controls: List[str] = []

        if (
            verification_status
            != VERIFICATION_VERIFIED
        ):
            controls.append(
                "verification_review"
            )

        if selected.contradictory:
            controls.append(
                "contradiction_review"
            )

        if selected.rollback_related:
            controls.append(
                "rollback_review"
            )

        if (
            recommendation
            == RECOMMENDATION_GOVERNANCE_ESCALATION
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
        selected: ExecutionVerificationSignal,
        verification_status: str,
        recommendation: str,
    ) -> List[str]:

        constraints: List[
            str
        ] = []

        constraints.append(
            f"verification_status_{verification_status.lower()}"
        )

        if (
            recommendation
            != RECOMMENDATION_NONE
        ):
            constraints.append(
                f"verification_recommendation_{recommendation.lower()}"
            )

        if selected.contradictory:
            constraints.append(
                "contradictory_verification_detected"
            )

        if selected.stale:
            constraints.append(
                "stale_verification_detected"
            )

        if selected.rollback_related:
            constraints.append(
                "rollback_related_verification"
            )

        return list(
            dict.fromkeys(constraints)
        )

    def _build_rationale(
        self,
        *,
        selected: ExecutionVerificationSignal,
        verification_status: str,
        recommendation: str,
        verification_confidence: float,
        verification_integrity: float,
        verification_survivability: float,
        cross_source_consistency: float,
        verification_pressure: float,
        signal_count: int,
        recommended_autonomy: str,
    ) -> str:

        return (
            f"Execution verification assessment for "
            f"{selected.execution_id}. "
            f"Selected signal "
            f"{selected.signal_type} from "
            f"{selected.source_system}. "
            f"Verification confidence "
            f"{verification_confidence:.2f}; "
            f"verification integrity "
            f"{verification_integrity:.2f}; "
            f"verification survivability "
            f"{verification_survivability:.2f}; "
            f"cross-source consistency "
            f"{cross_source_consistency:.2f}; "
            f"verification pressure "
            f"{verification_pressure:.2f}. "
            f"Status {verification_status}; "
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
        assessment: ExecutionVerificationAssessment,
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        self._latest_by_execution[
            assessment.execution_id
        ] = assessment

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
        assessment: ExecutionVerificationAssessment,
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
                "EXECUTION_VERIFICATION_ASSESSMENT"
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
                f"⚠️ Verification memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: ExecutionVerificationAssessment,
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
                "VERIFICATION"
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
                    "EXECUTION_VERIFICATION_ASSESSMENT"
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
                "execution_id": (
                    assessment.execution_id
                ),
                "verification_status": (
                    assessment.verification_status
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
                f"⚠️ Verification lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: ExecutionVerificationAssessment,
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
                "VERIFICATION_RESULT"
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
                    "EXECUTION_VERIFICATION_ASSESSMENT"
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
                "execution_id": (
                    assessment.execution_id
                ),
                "verification_status": (
                    assessment.verification_status
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
                f"⚠️ Verification evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: ExecutionVerificationAssessment,
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "EXECUTION_VERIFICATION_ASSESSMENT"
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
                        "EXECUTION_VERIFICATION_ASSESSMENT"
                    ),
                    payload,
                )

            elif hasattr(
                self.event_bus,
                "publish",
            ):
                self.event_bus.publish(
                    (
                        "EXECUTION_VERIFICATION_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Verification event emit failed: {exc}"
            )

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def _select_highest_risk_signal(
        self,
        signals: Sequence[
            ExecutionVerificationSignal
        ],
    ) -> ExecutionVerificationSignal:

        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(
                    item.severity
                ),
                self._signal_type_weight(
                    item.signal_type
                ),
                int(item.contradictory),
                int(item.stale),
                int(
                    item.rollback_related
                ),
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            ExecutionVerificationSignal
            | Dict[str, Any]
        ),
        *,
        execution_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> ExecutionVerificationSignal:

        if isinstance(
            item,
            ExecutionVerificationSignal,
        ):
            return item

        return ExecutionVerificationSignal(
            verification_signal_id=str(
                item.get(
                    "verification_signal_id"
                )
                or uuid.uuid4()
            ),
            execution_id=str(
                execution_id
                or item.get(
                    "execution_id"
                )
                or "UNKNOWN"
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
            action_type=item.get(
                "action_type"
            ),
            verification_successful=bool(
                item.get(
                    "verification_successful",
                    False,
                )
            ),
            contradictory=bool(
                item.get(
                    "contradictory",
                    False,
                )
            ),
            stale=bool(
                item.get(
                    "stale",
                    False,
                )
            ),
            rollback_related=bool(
                item.get(
                    "rollback_related",
                    False,
                )
            ),
            latency_ms=(
                None
                if item.get(
                    "latency_ms"
                )
                is None
                else max(
                    0,
                    int(
                        item.get(
                            "latency_ms"
                        )
                        or 0
                    ),
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

    def _unknown_assessment(
        self,
        *,
        execution_id: str,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
        current_autonomy_mode: str,
    ) -> ExecutionVerificationAssessment:

        return ExecutionVerificationAssessment(
            assessment_id=str(
                uuid.uuid4()
            ),
            execution_id=execution_id,
            verification_status=(
                VERIFICATION_UNVERIFIED
            ),
            recommendation=(
                RECOMMENDATION_SECONDARY_VERIFICATION
            ),
            verification_confidence_score=0.0,
            verification_integrity_score=0.0,
            verification_survivability_score=0.0,
            cross_source_consistency_score=0.0,
            verification_pressure_score=0.0,
            selected_signal_id=None,
            selected_signal_type=None,
            domain=(
                VerificationDomain
                .UNKNOWN.value
            ),
            severity=(
                VerificationSeverity
                .INFO.value
            ),
            confidence=0.0,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            connector_name=None,
            action_type=None,
            current_autonomy_mode=(
                current_autonomy_mode
            ),
            recommended_autonomy_mode=(
                current_autonomy_mode
            ),
            recommended_actions=[
                {
                    "action": (
                        "collect_verification_signals"
                    ),
                }
            ],
            required_controls=[
                "verification_review",
                "lineage_recording",
                "evidence_recording",
            ],
            constraints=[
                "verification_unknown"
            ],
            rationale=(
                "No verification signals were submitted."
            ),
            metadata={},
        )

    @staticmethod
    def _safe_signal_type(
        value: Any,
    ) -> str:

        value = str(
            value
            or VerificationSignalType
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in VerificationSignalType
        }

        return (
            value
            if value in valid
            else VerificationSignalType
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or VerificationDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in VerificationDomain
        }

        return (
            value
            if value in valid
            else VerificationDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or VerificationSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in VerificationSeverity
        }

        return (
            value
            if value in valid
            else VerificationSeverity
            .INFO.value
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
            VerificationSeverity
            .INFO.value: 0,
            VerificationSeverity
            .LOW.value: 1,
            VerificationSeverity
            .MEDIUM.value: 2,
            VerificationSeverity
            .HIGH.value: 3,
            VerificationSeverity
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
            VerificationSignalType
            .CONNECTOR_CONFIRMATION.value: 1,

            VerificationSignalType
            .TELEMETRY_CONFIRMATION.value: 2,

            VerificationSignalType
            .SECONDARY_CONFIRMATION.value: 2,

            VerificationSignalType
            .ROLLBACK_CONFIRMATION.value: 3,

            VerificationSignalType
            .CONTRADICTORY_CONFIRMATION.value: 5,

            VerificationSignalType
            .VERIFICATION_TIMEOUT.value: 4,

            VerificationSignalType
            .VERIFICATION_DRIFT.value: 5,

            VerificationSignalType
            .STALE_CONFIRMATION.value: 3,

            VerificationSignalType
            .NETWORK_CORRELATION.value: 2,

            VerificationSignalType
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

def build_execution_verification_mesh(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> ExecutionVerificationMesh:
    """
    Factory for explicit dependency injection.
    """

    return ExecutionVerificationMesh(
        event_bus=event_bus,
        operational_memory_engine=(
            operational_memory_engine
        ),
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=(
            fedramp_evidence_lineage_engine
        ),
    )