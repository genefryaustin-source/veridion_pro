"""
core/runtime/sovereign_live_runtime_state_engine.py

Sovereign Live Runtime State Engine

Continuous sovereign operational state awareness layer.

Maintains:
- live runtime posture
- live governance posture
- live survivability posture
- live sovereignty posture
- live continuity posture
- live resilience posture
- live operational pressure posture
- replayable live state lineage
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "sovereign_live_runtime_state_engine"
DEFAULT_STATE_HISTORY_LIMIT = 1000


LIVE_STATE_OPTIMAL = "OPTIMAL"
LIVE_STATE_STABLE = "STABLE"
LIVE_STATE_WATCH = "WATCH"
LIVE_STATE_PRESSURE = "PRESSURE"
LIVE_STATE_DEGRADED = "DEGRADED"
LIVE_STATE_CRITICAL = "CRITICAL"


class LiveStateSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class LiveRuntimeStateSignal:
    signal_id: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    runtime_score: float = 100.0
    governance_score: float = 100.0
    verification_score: float = 100.0
    adaptive_score: float = 100.0
    policy_score: float = 100.0
    survivability_score: float = 100.0
    continuity_score: float = 100.0
    resilience_score: float = 100.0
    sovereignty_score: float = 100.0

    governance_drift_score: float = 0.0
    escalation_pressure_score: float = 0.0
    sovereignty_pressure_score: float = 0.0
    survivability_pressure_score: float = 0.0
    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class LiveRuntimeStateTransition:
    transition_id: str
    previous_state: str
    current_state: str
    transition_reason: str
    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class SovereignLiveRuntimeStateAssessment:
    assessment_id: str

    live_state: str
    previous_state: Optional[str]

    runtime_score: float
    governance_score: float
    verification_score: float
    adaptive_score: float
    policy_score: float
    survivability_score: float
    continuity_score: float
    resilience_score: float
    sovereignty_score: float

    governance_drift_score: float
    escalation_pressure_score: float
    sovereignty_pressure_score: float
    survivability_pressure_score: float
    uncertainty_score: float

    operational_stability_score: float
    pressure_score: float
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

    transition: Optional[LiveRuntimeStateTransition]

    telemetry_fusion: Dict[str, Any]
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


class SovereignLiveRuntimeStateEngine:
    """
    Continuous sovereign operational state cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        telemetry_bus: Optional[Any] = None,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
        history_limit: int = DEFAULT_STATE_HISTORY_LIMIT,
    ) -> None:
        self.engine_name = engine_name
        self.telemetry_bus = telemetry_bus
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._history_limit = max(100, int(history_limit))
        self._assessments: List[SovereignLiveRuntimeStateAssessment] = []
        self._current_state: Optional[str] = None

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[LiveRuntimeStateSignal | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignLiveRuntimeStateAssessment:

        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        if not normalized:
            assessment = self._empty_assessment(
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_assessment(assessment, context=context)
            return assessment

        selected = self._select_primary_signal(normalized)

        runtime_score = self._avg_score([s.runtime_score for s in normalized])
        governance_score = self._avg_score([s.governance_score for s in normalized])
        verification_score = self._avg_score([s.verification_score for s in normalized])
        adaptive_score = self._avg_score([s.adaptive_score for s in normalized])
        policy_score = self._avg_score([s.policy_score for s in normalized])
        survivability_score = self._avg_score([s.survivability_score for s in normalized])
        continuity_score = self._avg_score([s.continuity_score for s in normalized])
        resilience_score = self._avg_score([s.resilience_score for s in normalized])
        sovereignty_score = self._avg_score([s.sovereignty_score for s in normalized])

        governance_drift = self._avg_score([s.governance_drift_score for s in normalized])
        escalation_pressure = self._avg_score([s.escalation_pressure_score for s in normalized])
        sovereignty_pressure = self._avg_score([s.sovereignty_pressure_score for s in normalized])
        survivability_pressure = self._avg_score([s.survivability_pressure_score for s in normalized])
        uncertainty = self._avg_score([s.uncertainty_score for s in normalized])

        operational_stability = self._operational_stability_score(
            runtime_score=runtime_score,
            governance_score=governance_score,
            verification_score=verification_score,
            adaptive_score=adaptive_score,
            policy_score=policy_score,
            survivability_score=survivability_score,
            continuity_score=continuity_score,
            resilience_score=resilience_score,
            sovereignty_score=sovereignty_score,
        )

        pressure_score = self._pressure_score(
            governance_drift_score=governance_drift,
            escalation_pressure_score=escalation_pressure,
            sovereignty_pressure_score=sovereignty_pressure,
            survivability_pressure_score=survivability_pressure,
            uncertainty_score=uncertainty,
        )

        systemic_risk_probability = self._systemic_risk_probability(
            pressure_score=pressure_score,
            operational_stability_score=operational_stability,
        )

        live_state = self._live_state(
            operational_stability_score=operational_stability,
            pressure_score=pressure_score,
            systemic_risk_probability=systemic_risk_probability,
        )

        previous_state = self._current_state

        transition = self._build_transition(
            previous_state=previous_state,
            current_state=live_state,
            pressure_score=pressure_score,
            operational_stability_score=operational_stability,
        )

        self._current_state = live_state

        assessment = SovereignLiveRuntimeStateAssessment(
            assessment_id=str(uuid.uuid4()),
            live_state=live_state,
            previous_state=previous_state,
            runtime_score=runtime_score,
            governance_score=governance_score,
            verification_score=verification_score,
            adaptive_score=adaptive_score,
            policy_score=policy_score,
            survivability_score=survivability_score,
            continuity_score=continuity_score,
            resilience_score=resilience_score,
            sovereignty_score=sovereignty_score,
            governance_drift_score=governance_drift,
            escalation_pressure_score=escalation_pressure,
            sovereignty_pressure_score=sovereignty_pressure,
            survivability_pressure_score=survivability_pressure,
            uncertainty_score=uncertainty,
            operational_stability_score=operational_stability,
            pressure_score=pressure_score,
            systemic_risk_probability=systemic_risk_probability,
            confidence=self._confidence(normalized),
            explainability_score=self._explainability_score(normalized),
            signal_count=len(normalized),
            engine_count=len({s.source_engine for s in normalized}),
            severity=selected.severity,
            tenant_id=tenant_id or selected.tenant_id,
            mission_id=mission_id or selected.mission_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            transition=transition,
            telemetry_fusion=self._telemetry_fusion(normalized),
            rationale=self._rationale(
                live_state=live_state,
                operational_stability_score=operational_stability,
                pressure_score=pressure_score,
                systemic_risk_probability=systemic_risk_probability,
            ),
            metadata={
                "source_engines": sorted({s.source_engine for s in normalized}),
            },
        )

        self._record_assessment(assessment, context=context)

        return assessment

    def evaluate_from_telemetry_bus(
        self,
        *,
        limit: int = 250,
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignLiveRuntimeStateAssessment:

        if self.telemetry_bus is None:
            return self.evaluate(
                [],
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
                context=context,
            )

        events = []

        try:
            if hasattr(self.telemetry_bus, "get_recent_events"):
                events = self.telemetry_bus.get_recent_events(limit=limit)
        except Exception as exc:
            print(f"⚠️ Live state telemetry read failed: {exc}")

        signals = [
            self._signal_from_telemetry_event(event)
            for event in events
        ]

        return self.evaluate(
            signals,
            tenant_id=tenant_id,
            mission_id=mission_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def get_current_state(self) -> Optional[str]:
        return self._current_state

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignLiveRuntimeStateAssessment]:
        return list(reversed(self._assessments[-max(1, int(limit)):]))

    # ==========================================================
    # SCORING
    # ==========================================================

    def _operational_stability_score(
        self,
        *,
        runtime_score: float,
        governance_score: float,
        verification_score: float,
        adaptive_score: float,
        policy_score: float,
        survivability_score: float,
        continuity_score: float,
        resilience_score: float,
        sovereignty_score: float,
    ) -> float:
        return self._avg_score(
            [
                runtime_score,
                governance_score,
                verification_score,
                adaptive_score,
                policy_score,
                survivability_score,
                continuity_score,
                resilience_score,
                sovereignty_score,
            ]
        )

    def _pressure_score(
        self,
        *,
        governance_drift_score: float,
        escalation_pressure_score: float,
        sovereignty_pressure_score: float,
        survivability_pressure_score: float,
        uncertainty_score: float,
    ) -> float:
        return self._avg_score(
            [
                governance_drift_score,
                escalation_pressure_score,
                sovereignty_pressure_score,
                survivability_pressure_score,
                uncertainty_score,
            ]
        )

    def _systemic_risk_probability(
        self,
        *,
        pressure_score: float,
        operational_stability_score: float,
    ) -> float:
        value = (
            pressure_score
            + (100.0 - operational_stability_score)
        ) / 200.0

        return self._clamp_probability(value)

    @staticmethod
    def _live_state(
        *,
        operational_stability_score: float,
        pressure_score: float,
        systemic_risk_probability: float,
    ) -> str:
        if systemic_risk_probability >= 0.75 or operational_stability_score < 35:
            return LIVE_STATE_CRITICAL

        if operational_stability_score < 55 or pressure_score >= 70:
            return LIVE_STATE_DEGRADED

        if operational_stability_score < 70 or pressure_score >= 55:
            return LIVE_STATE_PRESSURE

        if operational_stability_score < 82 or pressure_score >= 35:
            return LIVE_STATE_WATCH

        if operational_stability_score < 93:
            return LIVE_STATE_STABLE

        return LIVE_STATE_OPTIMAL

    def _build_transition(
        self,
        *,
        previous_state: Optional[str],
        current_state: str,
        pressure_score: float,
        operational_stability_score: float,
    ) -> Optional[LiveRuntimeStateTransition]:
        if previous_state is None or previous_state == current_state:
            return None

        return LiveRuntimeStateTransition(
            transition_id=str(uuid.uuid4()),
            previous_state=previous_state,
            current_state=current_state,
            transition_reason=(
                f"Live state changed from {previous_state} to {current_state}. "
                f"Pressure={pressure_score:.2f}; "
                f"stability={operational_stability_score:.2f}."
            ),
        )

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: SovereignLiveRuntimeStateAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._assessments.append(assessment)

        if len(self._assessments) > self._history_limit:
            self._assessments = self._assessments[-self._history_limit:]

        payload = {
            "type": "SOVEREIGN_LIVE_RUNTIME_STATE",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        self._write_memory(payload)
        self._write_lineage(payload)
        self._write_evidence(payload)
        self._emit_event(payload)

    def _write_memory(self, payload: Dict[str, Any]) -> None:
        try:
            if self.operational_memory_engine and hasattr(
                self.operational_memory_engine,
                "append_memory",
            ):
                self.operational_memory_engine.append_memory(payload)
        except Exception as exc:
            print(f"⚠️ Live runtime state memory write failed: {exc}")

    def _write_lineage(self, payload: Dict[str, Any]) -> None:
        try:
            if self.lineage_engine and hasattr(self.lineage_engine, "record_lineage"):
                self.lineage_engine.record_lineage(payload)
        except Exception as exc:
            print(f"⚠️ Live runtime state lineage write failed: {exc}")

    def _write_evidence(self, payload: Dict[str, Any]) -> None:
        try:
            if self.fedramp_evidence_lineage_engine and hasattr(
                self.fedramp_evidence_lineage_engine,
                "record_evidence",
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(payload)
        except Exception as exc:
            print(f"⚠️ Live runtime state evidence write failed: {exc}")

    def _emit_event(self, payload: Dict[str, Any]) -> None:
        try:
            if self.event_bus and hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_LIVE_RUNTIME_STATE",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Live runtime state event emit failed: {exc}")

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: LiveRuntimeStateSignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> LiveRuntimeStateSignal:

        if isinstance(item, LiveRuntimeStateSignal):
            return item

        return LiveRuntimeStateSignal(
            signal_id=str(item.get("signal_id") or uuid.uuid4()),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=tenant_id or item.get("tenant_id"),
            mission_id=mission_id or item.get("mission_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            runtime_score=self._clamp_score(item.get("runtime_score", 100.0)),
            governance_score=self._clamp_score(item.get("governance_score", 100.0)),
            verification_score=self._clamp_score(item.get("verification_score", 100.0)),
            adaptive_score=self._clamp_score(item.get("adaptive_score", 100.0)),
            policy_score=self._clamp_score(item.get("policy_score", 100.0)),
            survivability_score=self._clamp_score(item.get("survivability_score", 100.0)),
            continuity_score=self._clamp_score(item.get("continuity_score", 100.0)),
            resilience_score=self._clamp_score(item.get("resilience_score", 100.0)),
            sovereignty_score=self._clamp_score(item.get("sovereignty_score", 100.0)),
            governance_drift_score=self._clamp_score(item.get("governance_drift_score", 0.0)),
            escalation_pressure_score=self._clamp_score(item.get("escalation_pressure_score", 0.0)),
            sovereignty_pressure_score=self._clamp_score(item.get("sovereignty_pressure_score", 0.0)),
            survivability_pressure_score=self._clamp_score(item.get("survivability_pressure_score", 0.0)),
            uncertainty_score=self._clamp_score(item.get("uncertainty_score", 0.0)),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _signal_from_telemetry_event(self, event: Any) -> LiveRuntimeStateSignal:
        payload = event if isinstance(event, dict) else getattr(event, "__dict__", {})

        return LiveRuntimeStateSignal(
            signal_id=str(payload.get("event_id") or uuid.uuid4()),
            source_engine=str(payload.get("source_engine") or "telemetry_bus"),
            severity=self._safe_severity(payload.get("severity")),
            confidence=self._clamp_probability(payload.get("confidence", 1.0)),
            summary=str(payload.get("summary") or "Telemetry-derived live state signal."),
            tenant_id=payload.get("tenant_id"),
            mission_id=payload.get("mission_id"),
            case_id=payload.get("case_id"),
            correlation_id=payload.get("correlation_id"),
            runtime_score=self._clamp_score(payload.get("runtime_score", 100.0)),
            governance_score=self._clamp_score(payload.get("governance_score", 100.0)),
            survivability_score=self._clamp_score(payload.get("survivability_score", 100.0)),
            continuity_score=self._clamp_score(payload.get("continuity_score", 100.0)),
            resilience_score=self._clamp_score(payload.get("resilience_score", 100.0)),
            sovereignty_score=self._clamp_score(payload.get("sovereignty_score", 100.0)),
            governance_drift_score=self._clamp_score(payload.get("governance_drift_score", 0.0)),
            escalation_pressure_score=self._clamp_score(payload.get("escalation_pressure_score", 0.0)),
            uncertainty_score=self._clamp_score(payload.get("uncertainty_score", 0.0)),
            payload=dict(payload.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignLiveRuntimeStateAssessment:

        previous_state = self._current_state
        self._current_state = LIVE_STATE_OPTIMAL

        return SovereignLiveRuntimeStateAssessment(
            assessment_id=str(uuid.uuid4()),
            live_state=LIVE_STATE_OPTIMAL,
            previous_state=previous_state,
            runtime_score=100.0,
            governance_score=100.0,
            verification_score=100.0,
            adaptive_score=100.0,
            policy_score=100.0,
            survivability_score=100.0,
            continuity_score=100.0,
            resilience_score=100.0,
            sovereignty_score=100.0,
            governance_drift_score=0.0,
            escalation_pressure_score=0.0,
            sovereignty_pressure_score=0.0,
            survivability_pressure_score=0.0,
            uncertainty_score=0.0,
            operational_stability_score=100.0,
            pressure_score=0.0,
            systemic_risk_probability=0.0,
            confidence=1.0,
            explainability_score=100.0,
            signal_count=0,
            engine_count=0,
            severity=LiveStateSeverity.INFO.value,
            tenant_id=tenant_id,
            mission_id=mission_id,
            case_id=case_id,
            correlation_id=correlation_id,
            transition=None,
            telemetry_fusion={},
            rationale="No live runtime state signals submitted.",
            metadata={},
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _select_primary_signal(
        self,
        signals: Sequence[LiveRuntimeStateSignal],
    ) -> LiveRuntimeStateSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.governance_drift_score,
                item.escalation_pressure_score,
                item.sovereignty_pressure_score,
                item.survivability_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[LiveRuntimeStateSignal],
    ) -> Dict[str, Any]:
        return {
            "signal_count": len(signals),
            "source_engines": sorted({s.source_engine for s in signals}),
            "tenants": sorted({s.tenant_id for s in signals if s.tenant_id}),
            "missions": sorted({s.mission_id for s in signals if s.mission_id}),
        }

    def _confidence(self, signals: Sequence[LiveRuntimeStateSignal]) -> float:
        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean([s.confidence for s in signals])
        )

    def _explainability_score(
        self,
        signals: Sequence[LiveRuntimeStateSignal],
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

        return self._clamp_score((explained / (len(signals) * 3)) * 100.0)

    @staticmethod
    def _rationale(
        *,
        live_state: str,
        operational_stability_score: float,
        pressure_score: float,
        systemic_risk_probability: float,
    ) -> str:
        return (
            f"Sovereign live runtime state evaluated. "
            f"Live state {live_state}; operational stability "
            f"{operational_stability_score:.2f}; pressure "
            f"{pressure_score:.2f}; systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or LiveStateSeverity.INFO.value).upper()
        valid = {item.value for item in LiveStateSeverity}
        return value if value in valid else LiveStateSeverity.INFO.value

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _clamp_probability(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))

    def _avg_score(
        self,
        values: Sequence[float],
        *,
        default: float = 0.0,
    ) -> float:
        if not values:
            return default

        return self._clamp_score(statistics.mean(values))


def build_sovereign_live_runtime_state_engine(
    *,
    telemetry_bus: Optional[Any] = None,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignLiveRuntimeStateEngine:

    return SovereignLiveRuntimeStateEngine(
        telemetry_bus=telemetry_bus,
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )