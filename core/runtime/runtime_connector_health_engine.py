"""
core/runtime/runtime_connector_health_engine.py

Runtime Connector Health Engine

Infrastructure health cognition layer for connector execution.

This engine evaluates:
- connector uptime
- degraded execution
- timeout frequency
- latency spikes
- auth failures
- throttling
- API instability
- retry amplification
- verification instability
- failover frequency
- connector trust posture

IMPORTANT:
This engine DOES NOT:
- execute connectors
- mutate connector configuration
- directly quarantine connectors
- directly alter routing tables
- call external APIs

It ONLY:
- evaluates connector health posture
- scores trust / reliability / survivability
- recommends quarantine, deprioritization, failover, or autonomy reduction
- records replayable connector health lineage and evidence
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

DEFAULT_ENGINE_NAME = "runtime_connector_health_engine"

HEALTH_HEALTHY = "HEALTHY"
HEALTH_WATCH = "WATCH"
HEALTH_DEGRADED = "DEGRADED"
HEALTH_UNSTABLE = "UNSTABLE"
HEALTH_QUARANTINE_RECOMMENDED = "QUARANTINE_RECOMMENDED"
HEALTH_UNAVAILABLE = "UNAVAILABLE"
HEALTH_UNKNOWN = "UNKNOWN"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_DEPRIORITIZE = "DEPRIORITIZE"
RECOMMENDATION_FAILOVER_PREFERRED = "FAILOVER_PREFERRED"
RECOMMENDATION_QUARANTINE = "QUARANTINE"
RECOMMENDATION_FREEZE_CONNECTOR = "FREEZE_CONNECTOR"
RECOMMENDATION_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class ConnectorHealthSignalType(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    TIMEOUT = "TIMEOUT"
    LATENCY_SPIKE = "LATENCY_SPIKE"
    AUTH_FAILURE = "AUTH_FAILURE"
    THROTTLING = "THROTTLING"
    API_INSTABILITY = "API_INSTABILITY"
    RETRY_AMPLIFICATION = "RETRY_AMPLIFICATION"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    FAILOVER_USED = "FAILOVER_USED"
    PARTIAL_EXECUTION = "PARTIAL_EXECUTION"
    CONNECTOR_DEGRADED = "CONNECTOR_DEGRADED"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    NETWORK_ANOMALY = "NETWORK_ANOMALY"
    UNKNOWN = "UNKNOWN"


class ConnectorDomain(str, Enum):
    IDENTITY = "IDENTITY"
    EMAIL = "EMAIL"
    ENDPOINT = "ENDPOINT"
    CLOUD = "CLOUD"
    NETWORK = "NETWORK"
    LOCAL_AGENT = "LOCAL_AGENT"
    GENERIC = "GENERIC"
    UNKNOWN = "UNKNOWN"


class ConnectorSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class RuntimeConnectorHealthSignal:
    """
    Connector health signal.
    """

    health_signal_id: str
    connector_name: str
    signal_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    latency_ms: Optional[int] = None
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    retry_count: int = 0
    failover_count: int = 0
    verification_failure_count: int = 0
    throttling_count: int = 0
    auth_failure_count: int = 0
    partial_execution_count: int = 0

    current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY

    payload: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class RuntimeConnectorHealthAssessment:
    """
    Deterministic connector health assessment.
    """

    assessment_id: str
    connector_name: str
    health_status: str
    recommendation: str

    health_score: float
    trust_score: float
    survivability_score: float
    execution_reliability_score: float
    verification_reliability_score: float
    connector_pressure_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]
    domain: str
    severity: str
    confidence: float

    current_autonomy_mode: str
    recommended_autonomy_mode: str

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    recommended_actions: List[Dict[str, Any]]
    required_controls: List[str]
    constraints: List[str]
    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class RuntimeConnectorHealthSnapshot:
    """
    Runtime diagnostics snapshot.
    """

    engine_name: str
    total_signals_seen: int
    total_assessments_created: int
    tracked_connectors: List[str]
    last_assessment_id: Optional[str]
    last_connector_name: Optional[str]
    last_health_status: Optional[str]
    last_health_score: Optional[float]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class RuntimeConnectorHealthEngine:
    """
    Connector infrastructure health cognition engine.

    Design guarantees:
    - no connector execution
    - no direct runtime mutation
    - deterministic scoring
    - explicit dependency injection
    - replayable health lineage
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
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._signals_seen = 0
        self._assessments: List[RuntimeConnectorHealthAssessment] = []
        self._latest_by_connector: Dict[str, RuntimeConnectorHealthAssessment] = {}

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal | Dict[str, Any]],
        *,
        connector_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> RuntimeConnectorHealthAssessment:
        """
        Evaluate connector health from one or more health signals.
        """

        normalized = [
            self._normalize_signal(
                item,
                connector_name=connector_name,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:
            assessment = self._unknown_assessment(
                connector_name=connector_name or "UNKNOWN",
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_assessment(assessment, context=context)
            return assessment

        selected = self._select_highest_risk_signal(normalized)
        connector = connector_name or selected.connector_name

        health_score = self._health_score(normalized)
        trust_score = self._trust_score(normalized)
        survivability_score = self._survivability_score(normalized)
        execution_reliability = self._execution_reliability_score(normalized)
        verification_reliability = self._verification_reliability_score(normalized)
        pressure_score = self._connector_pressure_score(normalized)

        health_status = self._determine_health_status(
            health_score=health_score,
            trust_score=trust_score,
            survivability_score=survivability_score,
            execution_reliability=execution_reliability,
            verification_reliability=verification_reliability,
            pressure_score=pressure_score,
            selected=selected,
        )

        recommendation = self._determine_recommendation(
            selected=selected,
            health_status=health_status,
            pressure_score=pressure_score,
        )

        recommended_autonomy = self._recommended_autonomy_mode(
            selected,
            health_status,
            recommendation,
        )

        assessment = RuntimeConnectorHealthAssessment(
            assessment_id=str(uuid.uuid4()),
            connector_name=connector,
            health_status=health_status,
            recommendation=recommendation,
            health_score=health_score,
            trust_score=trust_score,
            survivability_score=survivability_score,
            execution_reliability_score=execution_reliability,
            verification_reliability_score=verification_reliability,
            connector_pressure_score=pressure_score,
            selected_signal_id=selected.health_signal_id,
            selected_signal_type=selected.signal_type,
            domain=selected.domain,
            severity=selected.severity,
            confidence=selected.confidence,
            current_autonomy_mode=selected.current_autonomy_mode,
            recommended_autonomy_mode=recommended_autonomy,
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            recommended_actions=self._recommended_actions(
                selected,
                health_status,
                recommendation,
                recommended_autonomy,
            ),
            required_controls=self._required_controls(
                selected,
                health_status,
                recommendation,
                recommended_autonomy,
            ),
            constraints=self._constraints(selected, health_status, recommendation),
            rationale=self._build_rationale(
                connector=connector,
                selected=selected,
                health_status=health_status,
                recommendation=recommendation,
                health_score=health_score,
                trust_score=trust_score,
                survivability_score=survivability_score,
                execution_reliability=execution_reliability,
                verification_reliability=verification_reliability,
                pressure_score=pressure_score,
                recommended_autonomy=recommended_autonomy,
                signal_count=len(normalized),
            ),
            metadata={
                "evaluated_signal_ids": [
                    item.health_signal_id for item in normalized
                ],
                "aggregate_counts": self._aggregate_counts(normalized),
                "latency_stats": self._latency_stats(normalized),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal | Dict[str, Any]],
        *,
        connector_name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> RuntimeConnectorHealthAssessment:
        """
        Compatibility alias.
        """

        return self.evaluate(
            signals,
            connector_name=connector_name,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def create_signal(
        self,
        *,
        connector_name: str,
        signal_type: str,
        domain: str,
        source_engine: str,
        severity: str,
        confidence: float,
        summary: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        latency_ms: Optional[int] = None,
        success_count: int = 0,
        failure_count: int = 0,
        timeout_count: int = 0,
        retry_count: int = 0,
        failover_count: int = 0,
        verification_failure_count: int = 0,
        throttling_count: int = 0,
        auth_failure_count: int = 0,
        partial_execution_count: int = 0,
        current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY,
        payload: Optional[Dict[str, Any]] = None,
    ) -> RuntimeConnectorHealthSignal:
        """
        Convenience constructor.
        """

        return RuntimeConnectorHealthSignal(
            health_signal_id=str(uuid.uuid4()),
            connector_name=self._safe_connector_name(connector_name),
            signal_type=self._safe_signal_type(signal_type),
            domain=self._safe_domain(domain),
            source_engine=source_engine or "unknown_engine",
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            latency_ms=latency_ms if latency_ms is None else max(0, int(latency_ms)),
            success_count=max(0, int(success_count)),
            failure_count=max(0, int(failure_count)),
            timeout_count=max(0, int(timeout_count)),
            retry_count=max(0, int(retry_count)),
            failover_count=max(0, int(failover_count)),
            verification_failure_count=max(0, int(verification_failure_count)),
            throttling_count=max(0, int(throttling_count)),
            auth_failure_count=max(0, int(auth_failure_count)),
            partial_execution_count=max(0, int(partial_execution_count)),
            current_autonomy_mode=self._safe_autonomy_mode(current_autonomy_mode),
            payload=payload or {},
        )

    def get_latest_assessment(
        self,
        connector_name: str,
    ) -> Optional[RuntimeConnectorHealthAssessment]:
        """
        Return latest assessment for connector.
        """

        return self._latest_by_connector.get(
            self._safe_connector_name(connector_name)
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[RuntimeConnectorHealthAssessment]:
        """
        Return recent assessments newest-first.
        """

        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    def snapshot(self) -> RuntimeConnectorHealthSnapshot:
        """
        Return lightweight diagnostics snapshot.
        """

        last = self._assessments[-1] if self._assessments else None

        return RuntimeConnectorHealthSnapshot(
            engine_name=self.engine_name,
            total_signals_seen=self._signals_seen,
            total_assessments_created=len(self._assessments),
            tracked_connectors=sorted(self._latest_by_connector.keys()),
            last_assessment_id=last.assessment_id if last else None,
            last_connector_name=last.connector_name if last else None,
            last_health_status=last.health_status if last else None,
            last_health_score=last.health_score if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # SCORING
    # --------------------------------------------------------

    def _select_highest_risk_signal(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> RuntimeConnectorHealthSignal:
        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(item.severity),
                self._signal_type_weight(item.signal_type),
                item.failure_count,
                item.timeout_count,
                item.retry_count,
                item.failover_count,
                item.verification_failure_count,
                item.throttling_count,
                item.auth_failure_count,
                item.partial_execution_count,
                item.latency_ms or 0,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _health_score(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> float:
        """
        Higher is better.
        """

        if not signals:
            return 0.0

        raw = 100.0

        penalty = 0.0
        for item in signals:
            penalty += min(item.failure_count, 20) * 2.5
            penalty += min(item.timeout_count, 20) * 3.0
            penalty += min(item.auth_failure_count, 10) * 5.0
            penalty += min(item.throttling_count, 20) * 2.0
            penalty += min(item.retry_count, 20) * 1.5
            penalty += min(item.failover_count, 20) * 2.0
            penalty += min(item.verification_failure_count, 20) * 3.5
            penalty += min(item.partial_execution_count, 10) * 5.0

            if item.signal_type in {
                ConnectorHealthSignalType.CONNECTOR_UNAVAILABLE.value,
                ConnectorHealthSignalType.AUTH_FAILURE.value,
            }:
                penalty += 25

            elif item.signal_type in {
                ConnectorHealthSignalType.TIMEOUT.value,
                ConnectorHealthSignalType.API_INSTABILITY.value,
                ConnectorHealthSignalType.CONNECTOR_DEGRADED.value,
            }:
                penalty += 15

            if item.latency_ms is not None:
                if item.latency_ms > 10_000:
                    penalty += 20
                elif item.latency_ms > 5_000:
                    penalty += 10
                elif item.latency_ms > 2_000:
                    penalty += 5

        return self._clamp_score(raw - (penalty / max(1, len(signals))))

    def _trust_score(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> float:
        """
        Higher is better. Penalizes failures that undermine trust.
        """

        if not signals:
            return 0.0

        total_success = sum(item.success_count for item in signals)
        total_failure = sum(item.failure_count for item in signals)
        total_verification_failures = sum(
            item.verification_failure_count for item in signals
        )
        total_partial = sum(item.partial_execution_count for item in signals)

        total = total_success + total_failure + total_verification_failures + total_partial

        if total <= 0:
            base = 80.0
        else:
            base = 100.0 * (total_success / max(1, total))

        penalty = 0.0
        penalty += min(total_verification_failures, 20) * 3.0
        penalty += min(total_partial, 10) * 5.0

        for item in signals:
            if item.signal_type == ConnectorHealthSignalType.AUTH_FAILURE.value:
                penalty += 15
            if item.signal_type == ConnectorHealthSignalType.PARTIAL_EXECUTION.value:
                penalty += 20

        return self._clamp_score(base - penalty)

    def _survivability_score(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> float:
        """
        Higher is better. Measures whether connector remains usable under stress.
        """

        if not signals:
            return 0.0

        raw = 100.0

        pressure = 0.0
        for item in signals:
            pressure += min(item.failover_count, 20) * 3.0
            pressure += min(item.retry_count, 20) * 2.0
            pressure += min(item.timeout_count, 20) * 2.5
            pressure += min(item.throttling_count, 20) * 2.0

            if item.signal_type in {
                ConnectorHealthSignalType.FAILOVER_USED.value,
                ConnectorHealthSignalType.RETRY_AMPLIFICATION.value,
                ConnectorHealthSignalType.NETWORK_ANOMALY.value,
            }:
                pressure += 15

        return self._clamp_score(raw - (pressure / max(1, len(signals))))

    def _execution_reliability_score(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> float:
        """
        Higher is better.
        """

        total_success = sum(item.success_count for item in signals)
        total_failure = sum(item.failure_count for item in signals)
        total_timeout = sum(item.timeout_count for item in signals)
        total_partial = sum(item.partial_execution_count for item in signals)

        total = total_success + total_failure + total_timeout + total_partial

        if total <= 0:
            return 80.0

        score = 100.0 * (total_success / max(1, total))
        score -= min(total_partial, 10) * 4.0

        return self._clamp_score(score)

    def _verification_reliability_score(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> float:
        """
        Higher is better.
        """

        total_success = sum(item.success_count for item in signals)
        total_verification_failures = sum(
            item.verification_failure_count for item in signals
        )

        total = total_success + total_verification_failures

        if total <= 0:
            return 80.0

        score = 100.0 * (total_success / max(1, total))
        score -= min(total_verification_failures, 20) * 2.5

        return self._clamp_score(score)

    def _connector_pressure_score(
        self,
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> float:
        """
        Higher means more pressure / instability.
        """

        if not signals:
            return 0.0

        raw = 0.0

        for item in signals:
            raw += self._severity_weight(item.severity) * 8
            raw += self._signal_type_weight(item.signal_type) * 4
            raw += min(item.failure_count, 20) * 2
            raw += min(item.timeout_count, 20) * 3
            raw += min(item.retry_count, 20) * 2
            raw += min(item.failover_count, 20) * 3
            raw += min(item.verification_failure_count, 20) * 4
            raw += min(item.throttling_count, 20) * 2
            raw += min(item.auth_failure_count, 10) * 5
            raw += min(item.partial_execution_count, 10) * 5

            if item.latency_ms is not None:
                if item.latency_ms > 10_000:
                    raw += 20
                elif item.latency_ms > 5_000:
                    raw += 10
                elif item.latency_ms > 2_000:
                    raw += 5

        return self._clamp_score(raw / max(1, len(signals)))

    # --------------------------------------------------------
    # DECISIONING
    # --------------------------------------------------------

    def _determine_health_status(
        self,
        *,
        health_score: float,
        trust_score: float,
        survivability_score: float,
        execution_reliability: float,
        verification_reliability: float,
        pressure_score: float,
        selected: RuntimeConnectorHealthSignal,
    ) -> str:
        if selected.signal_type == ConnectorHealthSignalType.CONNECTOR_UNAVAILABLE.value:
            return HEALTH_UNAVAILABLE

        if (
            health_score <= 20
            or trust_score <= 20
            or execution_reliability <= 20
            or pressure_score >= 90
        ):
            return HEALTH_QUARANTINE_RECOMMENDED

        if (
            health_score <= 35
            or trust_score <= 35
            or survivability_score <= 35
            or verification_reliability <= 35
            or pressure_score >= 75
        ):
            return HEALTH_UNSTABLE

        if (
            health_score <= 55
            or trust_score <= 55
            or execution_reliability <= 55
            or pressure_score >= 55
        ):
            return HEALTH_DEGRADED

        if (
            health_score <= 75
            or trust_score <= 75
            or survivability_score <= 75
            or pressure_score >= 35
        ):
            return HEALTH_WATCH

        return HEALTH_HEALTHY

    def _determine_recommendation(
        self,
        *,
        selected: RuntimeConnectorHealthSignal,
        health_status: str,
        pressure_score: float,
    ) -> str:
        if health_status in {
            HEALTH_UNAVAILABLE,
            HEALTH_QUARANTINE_RECOMMENDED,
        }:
            return RECOMMENDATION_QUARANTINE

        if health_status == HEALTH_UNSTABLE:
            return RECOMMENDATION_FREEZE_CONNECTOR

        if health_status == HEALTH_DEGRADED:
            return RECOMMENDATION_FAILOVER_PREFERRED

        if health_status == HEALTH_WATCH:
            return RECOMMENDATION_DEPRIORITIZE

        if selected.signal_type in {
            ConnectorHealthSignalType.AUTH_FAILURE.value,
            ConnectorHealthSignalType.PARTIAL_EXECUTION.value,
        }:
            return RECOMMENDATION_REDUCE_AUTONOMY

        if pressure_score >= 50:
            return RECOMMENDATION_MONITOR

        return RECOMMENDATION_NONE

    def _recommended_autonomy_mode(
        self,
        selected: RuntimeConnectorHealthSignal,
        health_status: str,
        recommendation: str,
    ) -> str:
        if recommendation in {
            RECOMMENDATION_QUARANTINE,
            RECOMMENDATION_FREEZE_CONNECTOR,
        }:
            return self._reduce_autonomy(selected.current_autonomy_mode)

        if health_status in {HEALTH_UNSTABLE, HEALTH_DEGRADED}:
            if selected.current_autonomy_mode == AUTONOMY_FULL_AUTONOMY:
                return AUTONOMY_SUPERVISED_AUTONOMY

        if recommendation == RECOMMENDATION_REDUCE_AUTONOMY:
            return self._reduce_autonomy(selected.current_autonomy_mode)

        return selected.current_autonomy_mode

    # --------------------------------------------------------
    # OUTPUT BUILDERS
    # --------------------------------------------------------

    def _recommended_actions(
        self,
        selected: RuntimeConnectorHealthSignal,
        health_status: str,
        recommendation: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        if recommendation == RECOMMENDATION_NONE:
            actions.append(
                {
                    "action": "continue_connector_routing",
                    "reason": "Connector health is acceptable.",
                }
            )

        if recommendation == RECOMMENDATION_MONITOR:
            actions.append(
                {
                    "action": "increase_connector_monitoring",
                    "connector": selected.connector_name,
                }
            )

        if recommendation == RECOMMENDATION_DEPRIORITIZE:
            actions.append(
                {
                    "action": "deprioritize_connector_routing",
                    "connector": selected.connector_name,
                }
            )

        if recommendation == RECOMMENDATION_FAILOVER_PREFERRED:
            actions.append(
                {
                    "action": "prefer_failover_connector",
                    "connector": selected.connector_name,
                }
            )

        if recommendation == RECOMMENDATION_QUARANTINE:
            actions.append(
                {
                    "action": "recommend_connector_quarantine",
                    "connector": selected.connector_name,
                }
            )

        if recommendation == RECOMMENDATION_FREEZE_CONNECTOR:
            actions.append(
                {
                    "action": "recommend_connector_freeze",
                    "connector": selected.connector_name,
                }
            )

        if recommended_autonomy != selected.current_autonomy_mode:
            actions.append(
                {
                    "action": "recommend_autonomy_change",
                    "from": selected.current_autonomy_mode,
                    "to": recommended_autonomy,
                }
            )

        actions.append(
            {
                "action": "record_connector_health_lineage",
                "reason": "Connector health assessment must be replayable.",
            }
        )

        actions.append(
            {
                "action": "record_connector_health_evidence",
                "reason": "Connector health assessment contributes to audit evidence.",
            }
        )

        return actions

    def _required_controls(
        self,
        selected: RuntimeConnectorHealthSignal,
        health_status: str,
        recommendation: str,
        recommended_autonomy: str,
    ) -> List[str]:
        controls: List[str] = []

        if health_status in {
            HEALTH_DEGRADED,
            HEALTH_UNSTABLE,
            HEALTH_QUARANTINE_RECOMMENDED,
            HEALTH_UNAVAILABLE,
        }:
            controls.append("operator_notification")

        if recommendation in {
            RECOMMENDATION_QUARANTINE,
            RECOMMENDATION_FREEZE_CONNECTOR,
        }:
            controls.append("connector_governance_review")

        if recommendation in {
            RECOMMENDATION_FAILOVER_PREFERRED,
            RECOMMENDATION_DEPRIORITIZE,
        }:
            controls.append("routing_policy_review")

        if recommended_autonomy != selected.current_autonomy_mode:
            controls.append("autonomy_governance_review")

        if selected.auth_failure_count:
            controls.append("credential_review")

        if selected.verification_failure_count:
            controls.append("verification_recovery")

        if selected.partial_execution_count:
            controls.append("partial_execution_review")

        controls.append("lineage_recording")
        controls.append("evidence_recording")

        return list(dict.fromkeys(controls))

    def _constraints(
        self,
        selected: RuntimeConnectorHealthSignal,
        health_status: str,
        recommendation: str,
    ) -> List[str]:
        constraints: List[str] = []

        if selected.signal_type != ConnectorHealthSignalType.UNKNOWN.value:
            constraints.append(
                f"connector_signal_{selected.signal_type.lower()}"
            )

        if health_status != HEALTH_HEALTHY:
            constraints.append(f"connector_health_{health_status.lower()}")

        if recommendation != RECOMMENDATION_NONE:
            constraints.append(f"connector_recommendation_{recommendation.lower()}")

        if selected.auth_failure_count:
            constraints.append("auth_failure_pressure")

        if selected.throttling_count:
            constraints.append("throttling_pressure")

        if selected.timeout_count:
            constraints.append("timeout_pressure")

        if selected.failover_count:
            constraints.append("failover_pressure")

        if selected.verification_failure_count:
            constraints.append("verification_failure_pressure")

        if selected.partial_execution_count:
            constraints.append("partial_execution_pressure")

        return list(dict.fromkeys(constraints))

    def _build_rationale(
        self,
        *,
        connector: str,
        selected: RuntimeConnectorHealthSignal,
        health_status: str,
        recommendation: str,
        health_score: float,
        trust_score: float,
        survivability_score: float,
        execution_reliability: float,
        verification_reliability: float,
        pressure_score: float,
        recommended_autonomy: str,
        signal_count: int,
    ) -> str:
        return (
            f"Connector health assessment for {connector}. Selected signal "
            f"{selected.signal_type} from {selected.source_engine}. Health "
            f"{health_score:.2f}; trust {trust_score:.2f}; survivability "
            f"{survivability_score:.2f}; execution reliability "
            f"{execution_reliability:.2f}; verification reliability "
            f"{verification_reliability:.2f}; connector pressure "
            f"{pressure_score:.2f}. Status {health_status}; recommendation "
            f"{recommendation}; recommended autonomy {recommended_autonomy}. "
            f"Evaluated across {signal_count} signal(s)."
        )

    # --------------------------------------------------------
    # RECORDING
    # --------------------------------------------------------

    def _record_assessment(
        self,
        assessment: RuntimeConnectorHealthAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._assessments.append(assessment)
        self._latest_by_connector[assessment.connector_name] = assessment

        self._write_to_memory(assessment, context=context)
        self._write_to_lineage(assessment, context=context)
        self._write_to_evidence(assessment, context=context)
        self._emit_event(assessment, context=context)

    def _write_to_memory(
        self,
        assessment: RuntimeConnectorHealthAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "RUNTIME_CONNECTOR_HEALTH_ASSESSMENT",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(memory, "append_memory"):
                memory.append_memory(payload)
            elif hasattr(memory, "record"):
                memory.record(payload)
            elif hasattr(memory, "write"):
                memory.write(payload)
        except Exception as exc:
            print(f"⚠️ Connector health memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: RuntimeConnectorHealthAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "EXECUTION",
            "lineage_status": "RECORDED",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "mission_priority": 0,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "constraints": list(assessment.constraints),
            "verification_requirements": list(assessment.required_controls),
            "context": {
                "type": "RUNTIME_CONNECTOR_HEALTH_ASSESSMENT",
                "assessment": asdict(assessment),
                "context": context or {},
            },
            "metadata": {
                "assessment_id": assessment.assessment_id,
                "connector_name": assessment.connector_name,
                "health_status": assessment.health_status,
                "recommendation": assessment.recommendation,
            },
        }

        try:
            if hasattr(lineage, "record_lineage"):
                lineage.record_lineage(payload)
            elif hasattr(lineage, "append_lineage"):
                lineage.append_lineage(payload)
            elif hasattr(lineage, "record"):
                lineage.record(payload)
        except Exception as exc:
            print(f"⚠️ Connector health lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: RuntimeConnectorHealthAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        evidence = self.fedramp_evidence_lineage_engine
        if evidence is None:
            return

        payload = {
            "evidence_type": "VERIFICATION_RESULT",
            "evidence_status": "RECORDED",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "mission_priority": 0,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "constraints": list(assessment.constraints),
            "evidence_payload": {
                "type": "RUNTIME_CONNECTOR_HEALTH_ASSESSMENT",
                "assessment": asdict(assessment),
                "context": context or {},
            },
            "metadata": {
                "assessment_id": assessment.assessment_id,
                "connector_name": assessment.connector_name,
                "health_status": assessment.health_status,
                "recommendation": assessment.recommendation,
            },
        }

        try:
            if hasattr(evidence, "record_evidence"):
                evidence.record_evidence(payload)
            elif hasattr(evidence, "append_evidence"):
                evidence.append_evidence(payload)
            elif hasattr(evidence, "record"):
                evidence.record(payload)
        except Exception as exc:
            print(f"⚠️ Connector health evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: RuntimeConnectorHealthAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "RUNTIME_CONNECTOR_HEALTH_ASSESSMENT",
            "engine_name": self.engine_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "RUNTIME_CONNECTOR_HEALTH_ASSESSMENT",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "RUNTIME_CONNECTOR_HEALTH_ASSESSMENT",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Connector health event emit failed: {exc}")

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_signal(
        self,
        item: RuntimeConnectorHealthSignal | Dict[str, Any],
        *,
        connector_name: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> RuntimeConnectorHealthSignal:
        if isinstance(item, RuntimeConnectorHealthSignal):
            return item

        return RuntimeConnectorHealthSignal(
            health_signal_id=str(item.get("health_signal_id") or uuid.uuid4()),
            connector_name=self._safe_connector_name(
                connector_name or item.get("connector_name")
            ),
            signal_type=self._safe_signal_type(item.get("signal_type")),
            domain=self._safe_domain(item.get("domain")),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_confidence(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=tenant_id or item.get("tenant_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            latency_ms=(
                None
                if item.get("latency_ms") is None
                else max(0, int(item.get("latency_ms") or 0))
            ),
            success_count=max(0, int(item.get("success_count", 0) or 0)),
            failure_count=max(0, int(item.get("failure_count", 0) or 0)),
            timeout_count=max(0, int(item.get("timeout_count", 0) or 0)),
            retry_count=max(0, int(item.get("retry_count", 0) or 0)),
            failover_count=max(0, int(item.get("failover_count", 0) or 0)),
            verification_failure_count=max(
                0,
                int(item.get("verification_failure_count", 0) or 0),
            ),
            throttling_count=max(0, int(item.get("throttling_count", 0) or 0)),
            auth_failure_count=max(
                0,
                int(item.get("auth_failure_count", 0) or 0),
            ),
            partial_execution_count=max(
                0,
                int(item.get("partial_execution_count", 0) or 0),
            ),
            current_autonomy_mode=self._safe_autonomy_mode(
                item.get("current_autonomy_mode")
            ),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _unknown_assessment(
        self,
        *,
        connector_name: str,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> RuntimeConnectorHealthAssessment:
        return RuntimeConnectorHealthAssessment(
            assessment_id=str(uuid.uuid4()),
            connector_name=self._safe_connector_name(connector_name),
            health_status=HEALTH_UNKNOWN,
            recommendation=RECOMMENDATION_MONITOR,
            health_score=0.0,
            trust_score=0.0,
            survivability_score=0.0,
            execution_reliability_score=0.0,
            verification_reliability_score=0.0,
            connector_pressure_score=0.0,
            selected_signal_id=None,
            selected_signal_type=None,
            domain=ConnectorDomain.UNKNOWN.value,
            severity=ConnectorSeverity.INFO.value,
            confidence=0.0,
            current_autonomy_mode=AUTONOMY_SUPERVISED_AUTONOMY,
            recommended_autonomy_mode=AUTONOMY_SUPERVISED_AUTONOMY,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            recommended_actions=[
                {
                    "action": "collect_connector_health_signals",
                    "reason": "No connector health signals were submitted.",
                }
            ],
            required_controls=[
                "lineage_recording",
                "evidence_recording",
            ],
            constraints=["connector_health_unknown"],
            rationale=(
                "No connector health signals were submitted. "
                "Connector health is unknown."
            ),
            metadata={},
        )

    # --------------------------------------------------------
    # AGGREGATES
    # --------------------------------------------------------

    @staticmethod
    def _aggregate_counts(
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> Dict[str, int]:
        return {
            "success_count": sum(item.success_count for item in signals),
            "failure_count": sum(item.failure_count for item in signals),
            "timeout_count": sum(item.timeout_count for item in signals),
            "retry_count": sum(item.retry_count for item in signals),
            "failover_count": sum(item.failover_count for item in signals),
            "verification_failure_count": sum(
                item.verification_failure_count for item in signals
            ),
            "throttling_count": sum(item.throttling_count for item in signals),
            "auth_failure_count": sum(item.auth_failure_count for item in signals),
            "partial_execution_count": sum(
                item.partial_execution_count for item in signals
            ),
        }

    @staticmethod
    def _latency_stats(
        signals: Sequence[RuntimeConnectorHealthSignal],
    ) -> Dict[str, Optional[float]]:
        values = [
            float(item.latency_ms)
            for item in signals
            if item.latency_ms is not None
        ]

        if not values:
            return {
                "min_latency_ms": None,
                "max_latency_ms": None,
                "avg_latency_ms": None,
            }

        return {
            "min_latency_ms": min(values),
            "max_latency_ms": max(values),
            "avg_latency_ms": sum(values) / len(values),
        }

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_connector_name(value: Any) -> str:
        return str(value or "UNKNOWN").upper().strip()

    @staticmethod
    def _safe_signal_type(value: Any) -> str:
        value = str(value or ConnectorHealthSignalType.UNKNOWN.value).upper()
        valid = {item.value for item in ConnectorHealthSignalType}
        return value if value in valid else ConnectorHealthSignalType.UNKNOWN.value

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or ConnectorDomain.UNKNOWN.value).upper()
        valid = {item.value for item in ConnectorDomain}
        return value if value in valid else ConnectorDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or ConnectorSeverity.INFO.value).upper()
        valid = {item.value for item in ConnectorSeverity}
        return value if value in valid else ConnectorSeverity.INFO.value

    @staticmethod
    def _safe_autonomy_mode(value: Any) -> str:
        value = str(value or AUTONOMY_SUPERVISED_AUTONOMY).upper()
        valid = {
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
            AUTONOMY_LOCKDOWN,
        }
        return value if value in valid else AUTONOMY_SUPERVISED_AUTONOMY

    @staticmethod
    def _clamp_confidence(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(1.0, score))

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0
        return max(0.0, min(100.0, score))

    @staticmethod
    def _severity_weight(severity: str) -> int:
        return {
            ConnectorSeverity.INFO.value: 0,
            ConnectorSeverity.LOW.value: 1,
            ConnectorSeverity.MEDIUM.value: 2,
            ConnectorSeverity.HIGH.value: 3,
            ConnectorSeverity.CRITICAL.value: 4,
        }.get(str(severity).upper(), 0)

    @staticmethod
    def _signal_type_weight(signal_type: str) -> int:
        return {
            ConnectorHealthSignalType.SUCCESS.value: 0,
            ConnectorHealthSignalType.FAILURE.value: 3,
            ConnectorHealthSignalType.TIMEOUT.value: 4,
            ConnectorHealthSignalType.LATENCY_SPIKE.value: 2,
            ConnectorHealthSignalType.AUTH_FAILURE.value: 5,
            ConnectorHealthSignalType.THROTTLING.value: 3,
            ConnectorHealthSignalType.API_INSTABILITY.value: 4,
            ConnectorHealthSignalType.RETRY_AMPLIFICATION.value: 4,
            ConnectorHealthSignalType.VERIFICATION_FAILURE.value: 5,
            ConnectorHealthSignalType.FAILOVER_USED.value: 3,
            ConnectorHealthSignalType.PARTIAL_EXECUTION.value: 5,
            ConnectorHealthSignalType.CONNECTOR_DEGRADED.value: 4,
            ConnectorHealthSignalType.CONNECTOR_UNAVAILABLE.value: 5,
            ConnectorHealthSignalType.NETWORK_ANOMALY.value: 4,
            ConnectorHealthSignalType.UNKNOWN.value: 1,
        }.get(str(signal_type).upper(), 1)

    @staticmethod
    def _reduce_autonomy(current: str) -> str:
        current = str(current or AUTONOMY_SUPERVISED_AUTONOMY).upper()

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
        return order[max(0, idx - 1)]


# ============================================================
# FACTORY
# ============================================================

def build_runtime_connector_health_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> RuntimeConnectorHealthEngine:
    """
    Factory for explicit dependency injection.
    """

    return RuntimeConnectorHealthEngine(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )