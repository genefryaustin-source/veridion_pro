"""
core/runtime/strategic_resilience_engine.py

Strategic Resilience Engine

Sovereign runtime survivability cognition layer.

This engine protects the sovereign runtime when:
- governance degrades
- event bus fails
- cognition engines conflict
- workers stall
- execution queues congest
- verification fails
- blast radius rises
- telemetry confidence drops

IMPORTANT:
This engine DOES NOT:
- execute connectors
- mutate external systems
- directly restart workers
- directly isolate infrastructure
- directly change production autonomy settings

It ONLY:
- evaluates resilience posture
- recommends survivability actions
- produces deterministic resilience decisions
- records lineage/memory/event telemetry
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

DEFAULT_ENGINE_NAME = "strategic_resilience_engine"

HEALTH_HEALTHY = "HEALTHY"
HEALTH_DEGRADED = "DEGRADED"
HEALTH_UNSTABLE = "UNSTABLE"
HEALTH_CRITICAL = "CRITICAL"
HEALTH_UNKNOWN = "UNKNOWN"

RESILIENCE_NORMAL = "NORMAL"
RESILIENCE_DEGRADED_MODE = "DEGRADED_MODE"
RESILIENCE_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
RESILIENCE_ISOLATE_SUBSYSTEM = "ISOLATE_SUBSYSTEM"
RESILIENCE_FAILOVER_REQUIRED = "FAILOVER_REQUIRED"
RESILIENCE_BLOCK_EXECUTION = "BLOCK_EXECUTION"
RESILIENCE_CONTINUITY_REVIEW_REQUIRED = "CONTINUITY_REVIEW_REQUIRED"
RESILIENCE_RECOVERY_REQUIRED = "RECOVERY_REQUIRED"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class ResilienceSignalType(str, Enum):
    GOVERNANCE_DEGRADATION = "GOVERNANCE_DEGRADATION"
    EVENT_BUS_FAILURE = "EVENT_BUS_FAILURE"
    COGNITION_CONFLICT = "COGNITION_CONFLICT"
    WORKER_STALL = "WORKER_STALL"
    EXECUTION_CONGESTION = "EXECUTION_CONGESTION"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    HIGH_BLAST_RADIUS = "HIGH_BLAST_RADIUS"
    LOW_TELEMETRY_CONFIDENCE = "LOW_TELEMETRY_CONFIDENCE"
    CONTINUITY_RISK = "CONTINUITY_RISK"
    MEMORY_WRITE_FAILURE = "MEMORY_WRITE_FAILURE"
    LINEAGE_WRITE_FAILURE = "LINEAGE_WRITE_FAILURE"
    CONNECTOR_DEGRADATION = "CONNECTOR_DEGRADATION"
    UNKNOWN = "UNKNOWN"


class ResilienceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResilienceDomain(str, Enum):
    RUNTIME = "RUNTIME"
    GOVERNANCE = "GOVERNANCE"
    COGNITION = "COGNITION"
    EXECUTION = "EXECUTION"
    CONTINUITY = "CONTINUITY"
    MEMORY = "MEMORY"
    LINEAGE = "LINEAGE"
    CONNECTOR = "CONNECTOR"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class StrategicResilienceSignal:
    """
    Runtime health signal entering the resilience engine.
    """

    signal_id: str
    signal_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    affected_subsystem: Optional[str] = None
    current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class StrategicResilienceDecision:
    """
    Deterministic resilience decision.

    This is NOT an execution result.
    """

    decision_id: str
    decision: str
    runtime_health: str
    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]
    affected_subsystem: Optional[str]

    severity: str
    confidence: float
    current_autonomy_mode: str
    recommended_autonomy_mode: str

    recommended_actions: List[Dict[str, Any]]
    required_controls: List[str]
    rationale: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    suppressed_signal_ids: List[str] = field(default_factory=list)
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class StrategicResilienceSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str
    total_signals_seen: int
    total_decisions_created: int
    last_decision_id: Optional[str]
    last_decision: Optional[str]
    last_runtime_health: Optional[str]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class StrategicResilienceEngine:
    """
    Sovereign runtime survivability cognition engine.

    Design guarantees:
    - no connector execution
    - no direct runtime mutation
    - deterministic decisioning
    - explicit dependency injection
    - append-only local decision history
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine

        self._signals_seen = 0
        self._decisions: List[StrategicResilienceDecision] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        signals: Sequence[StrategicResilienceSignal | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategicResilienceDecision:
        """
        Evaluate resilience posture and return a deterministic decision.
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
            decision = self._normal_decision(
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_decision(decision, context=context)
            return decision

        selected = self._select_highest_risk_signal(normalized)
        suppressed = [
            item.signal_id
            for item in normalized
            if item.signal_id != selected.signal_id
        ]

        runtime_health = self._derive_runtime_health(selected)
        decision_value = self._determine_resilience_decision(
            selected,
            runtime_health,
        )
        recommended_autonomy = self._recommended_autonomy_mode(
            selected,
            decision_value,
        )

        decision = StrategicResilienceDecision(
            decision_id=str(uuid.uuid4()),
            decision=decision_value,
            runtime_health=runtime_health,
            selected_signal_id=selected.signal_id,
            selected_signal_type=selected.signal_type,
            affected_subsystem=selected.affected_subsystem,
            severity=selected.severity,
            confidence=selected.confidence,
            current_autonomy_mode=selected.current_autonomy_mode,
            recommended_autonomy_mode=recommended_autonomy,
            recommended_actions=self._recommended_actions(
                selected,
                decision_value,
                runtime_health,
                recommended_autonomy,
            ),
            required_controls=self._required_controls(
                selected,
                decision_value,
                runtime_health,
            ),
            rationale=self._build_rationale(
                selected,
                decision_value,
                runtime_health,
                recommended_autonomy,
                len(normalized),
            ),
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            suppressed_signal_ids=suppressed,
        )

        self._record_decision(decision, context=context)
        return decision

    def submit(
        self,
        signals: Sequence[StrategicResilienceSignal | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategicResilienceDecision:
        """
        Compatibility alias.
        """

        return self.evaluate(
            signals,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
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
        affected_subsystem: Optional[str] = None,
        current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY,
        payload: Optional[Dict[str, Any]] = None,
    ) -> StrategicResilienceSignal:
        """
        Convenience constructor for resilience signals.
        """

        return StrategicResilienceSignal(
            signal_id=str(uuid.uuid4()),
            signal_type=self._safe_signal_type(signal_type),
            domain=self._safe_domain(domain),
            source_engine=source_engine or "unknown_engine",
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            affected_subsystem=affected_subsystem,
            current_autonomy_mode=self._safe_autonomy_mode(
                current_autonomy_mode
            ),
            payload=payload or {},
        )

    def get_recent_decisions(
        self,
        *,
        limit: int = 25,
    ) -> List[StrategicResilienceDecision]:
        """
        Return recent decisions newest-first.
        """

        limit = max(1, int(limit))
        return list(reversed(self._decisions[-limit:]))

    def snapshot(self) -> StrategicResilienceSnapshot:
        """
        Return lightweight engine snapshot.
        """

        last = self._decisions[-1] if self._decisions else None

        return StrategicResilienceSnapshot(
            engine_name=self.engine_name,
            total_signals_seen=self._signals_seen,
            total_decisions_created=len(self._decisions),
            last_decision_id=last.decision_id if last else None,
            last_decision=last.decision if last else None,
            last_runtime_health=last.runtime_health if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # DECISIONING
    # --------------------------------------------------------

    def _select_highest_risk_signal(
        self,
        signals: Sequence[StrategicResilienceSignal],
    ) -> StrategicResilienceSignal:
        """
        Deterministic selection:
        1. severity
        2. signal-type risk
        3. low confidence risk
        4. oldest signal first for stable ordering
        """

        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(item.severity),
                self._signal_type_weight(item.signal_type),
                1.0 - item.confidence,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _derive_runtime_health(
        self,
        signal: StrategicResilienceSignal,
    ) -> str:
        """
        Derive runtime health from selected risk signal.
        """

        if signal.severity == ResilienceSeverity.CRITICAL.value:
            return HEALTH_CRITICAL

        if signal.severity == ResilienceSeverity.HIGH.value:
            return HEALTH_UNSTABLE

        if signal.severity == ResilienceSeverity.MEDIUM.value:
            return HEALTH_DEGRADED

        if signal.confidence < 0.35:
            return HEALTH_DEGRADED

        if signal.signal_type in {
            ResilienceSignalType.EVENT_BUS_FAILURE.value,
            ResilienceSignalType.GOVERNANCE_DEGRADATION.value,
            ResilienceSignalType.VERIFICATION_FAILURE.value,
        }:
            return HEALTH_UNSTABLE

        return HEALTH_HEALTHY

    def _determine_resilience_decision(
        self,
        signal: StrategicResilienceSignal,
        runtime_health: str,
    ) -> str:
        """
        Determine survivability decision.
        """

        if runtime_health == HEALTH_CRITICAL:
            if signal.signal_type in {
                ResilienceSignalType.EVENT_BUS_FAILURE.value,
                ResilienceSignalType.GOVERNANCE_DEGRADATION.value,
                ResilienceSignalType.VERIFICATION_FAILURE.value,
                ResilienceSignalType.HIGH_BLAST_RADIUS.value,
            }:
                return RESILIENCE_BLOCK_EXECUTION

            return RESILIENCE_RECOVERY_REQUIRED

        if signal.signal_type == ResilienceSignalType.EVENT_BUS_FAILURE.value:
            return RESILIENCE_FAILOVER_REQUIRED

        if signal.signal_type == ResilienceSignalType.GOVERNANCE_DEGRADATION.value:
            return RESILIENCE_REDUCE_AUTONOMY

        if signal.signal_type == ResilienceSignalType.COGNITION_CONFLICT.value:
            return RESILIENCE_REDUCE_AUTONOMY

        if signal.signal_type == ResilienceSignalType.WORKER_STALL.value:
            return RESILIENCE_RECOVERY_REQUIRED

        if signal.signal_type == ResilienceSignalType.EXECUTION_CONGESTION.value:
            return RESILIENCE_DEGRADED_MODE

        if signal.signal_type == ResilienceSignalType.VERIFICATION_FAILURE.value:
            return RESILIENCE_BLOCK_EXECUTION

        if signal.signal_type == ResilienceSignalType.HIGH_BLAST_RADIUS.value:
            return RESILIENCE_CONTINUITY_REVIEW_REQUIRED

        if signal.signal_type == ResilienceSignalType.LOW_TELEMETRY_CONFIDENCE.value:
            return RESILIENCE_REDUCE_AUTONOMY

        if signal.signal_type == ResilienceSignalType.CONTINUITY_RISK.value:
            return RESILIENCE_CONTINUITY_REVIEW_REQUIRED

        if signal.signal_type in {
            ResilienceSignalType.MEMORY_WRITE_FAILURE.value,
            ResilienceSignalType.LINEAGE_WRITE_FAILURE.value,
        }:
            return RESILIENCE_DEGRADED_MODE

        if signal.signal_type == ResilienceSignalType.CONNECTOR_DEGRADATION.value:
            return RESILIENCE_FAILOVER_REQUIRED

        if runtime_health in {HEALTH_DEGRADED, HEALTH_UNSTABLE}:
            return RESILIENCE_DEGRADED_MODE

        return RESILIENCE_NORMAL

    def _recommended_autonomy_mode(
        self,
        signal: StrategicResilienceSignal,
        decision: str,
    ) -> str:
        """
        Recommend safer autonomy posture.
        """

        current = self._safe_autonomy_mode(signal.current_autonomy_mode)

        if decision == RESILIENCE_BLOCK_EXECUTION:
            return AUTONOMY_LOCKDOWN

        if decision in {
            RESILIENCE_REDUCE_AUTONOMY,
            RESILIENCE_CONTINUITY_REVIEW_REQUIRED,
            RESILIENCE_RECOVERY_REQUIRED,
        }:
            return self._reduce_autonomy(current)

        if decision in {
            RESILIENCE_DEGRADED_MODE,
            RESILIENCE_FAILOVER_REQUIRED,
        }:
            if current == AUTONOMY_FULL_AUTONOMY:
                return AUTONOMY_SUPERVISED_AUTONOMY
            return current

        return current

    @staticmethod
    def _reduce_autonomy(current: str) -> str:
        """
        Step autonomy down one safety level.
        """

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

    # --------------------------------------------------------
    # ACTIONS / CONTROLS
    # --------------------------------------------------------

    def _recommended_actions(
        self,
        signal: StrategicResilienceSignal,
        decision: str,
        runtime_health: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        if decision == RESILIENCE_NORMAL:
            actions.append(
                {
                    "action": "continue_normal_operations",
                    "reason": "Runtime health is acceptable.",
                }
            )

        if decision == RESILIENCE_DEGRADED_MODE:
            actions.append(
                {
                    "action": "enter_degraded_mode",
                    "reason": "Runtime health requires reduced operating posture.",
                }
            )

        if decision == RESILIENCE_REDUCE_AUTONOMY:
            actions.append(
                {
                    "action": "recommend_autonomy_reduction",
                    "from": signal.current_autonomy_mode,
                    "to": recommended_autonomy,
                }
            )

        if decision == RESILIENCE_ISOLATE_SUBSYSTEM:
            actions.append(
                {
                    "action": "recommend_subsystem_isolation",
                    "subsystem": signal.affected_subsystem,
                }
            )

        if decision == RESILIENCE_FAILOVER_REQUIRED:
            actions.append(
                {
                    "action": "route_to_failover_path",
                    "subsystem": signal.affected_subsystem,
                }
            )

        if decision == RESILIENCE_BLOCK_EXECUTION:
            actions.append(
                {
                    "action": "block_execution_handoff",
                    "reason": "Runtime survivability risk is too high.",
                }
            )

        if decision == RESILIENCE_CONTINUITY_REVIEW_REQUIRED:
            actions.append(
                {
                    "action": "request_continuity_review",
                    "reason": "Mission continuity risk requires review.",
                }
            )

        if decision == RESILIENCE_RECOVERY_REQUIRED:
            actions.append(
                {
                    "action": "start_recovery_workflow",
                    "subsystem": signal.affected_subsystem,
                }
            )

        actions.append(
            {
                "action": "record_resilience_lineage",
                "reason": "Survivability decision must be replayable.",
            }
        )

        actions.append(
            {
                "action": "record_runtime_health",
                "runtime_health": runtime_health,
            }
        )

        return actions

    def _required_controls(
        self,
        signal: StrategicResilienceSignal,
        decision: str,
        runtime_health: str,
    ) -> List[str]:
        controls: List[str] = []

        if decision == RESILIENCE_BLOCK_EXECUTION:
            controls.append("execution_block")

        if decision in {
            RESILIENCE_REDUCE_AUTONOMY,
            RESILIENCE_DEGRADED_MODE,
        }:
            controls.append("autonomy_safety_review")

        if decision == RESILIENCE_FAILOVER_REQUIRED:
            controls.append("failover_validation")

        if decision == RESILIENCE_RECOVERY_REQUIRED:
            controls.append("recovery_validation")

        if decision == RESILIENCE_CONTINUITY_REVIEW_REQUIRED:
            controls.append("continuity_review")

        if runtime_health in {HEALTH_UNSTABLE, HEALTH_CRITICAL}:
            controls.append("operator_notification")

        if signal.signal_type == ResilienceSignalType.GOVERNANCE_DEGRADATION.value:
            controls.append("governance_revalidation")

        if signal.signal_type == ResilienceSignalType.VERIFICATION_FAILURE.value:
            controls.append("verification_recovery")

        controls.append("lineage_recording")
        controls.append("operational_memory_recording")

        return list(dict.fromkeys(controls))

    def _build_rationale(
        self,
        signal: StrategicResilienceSignal,
        decision: str,
        runtime_health: str,
        recommended_autonomy: str,
        signal_count: int,
    ) -> str:
        return (
            f"Selected resilience signal {signal.signal_type} from "
            f"{signal.source_engine} in domain {signal.domain}. "
            f"Severity {signal.severity}, confidence {signal.confidence:.2f}. "
            f"Runtime health derived as {runtime_health}. "
            f"Decision: {decision}. Current autonomy "
            f"{signal.current_autonomy_mode}; recommended autonomy "
            f"{recommended_autonomy}. Evaluated across {signal_count} signal(s)."
        )

    # --------------------------------------------------------
    # RECORDING
    # --------------------------------------------------------

    def _record_decision(
        self,
        decision: StrategicResilienceDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._decisions.append(decision)

        self._write_to_operational_memory(decision, context=context)
        self._write_to_lineage(decision, context=context)
        self._emit_event(decision, context=context)

    def _write_to_operational_memory(
        self,
        decision: StrategicResilienceDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "STRATEGIC_RESILIENCE_DECISION",
            "decision": self._decision_to_dict(decision),
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
            print(f"⚠️ Strategic resilience memory write failed: {exc}")

    def _write_to_lineage(
        self,
        decision: StrategicResilienceDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "CONTINUITY",
            "lineage_status": "RECORDED",
            "source_engine": self.engine_name,
            "summary": decision.rationale,
            "severity": decision.severity,
            "confidence": decision.confidence,
            "mission_priority": 0,
            "tenant_id": decision.tenant_id,
            "case_id": decision.case_id,
            "correlation_id": decision.correlation_id,
            "constraints": decision.required_controls,
            "context": {
                "type": "STRATEGIC_RESILIENCE_DECISION",
                "decision": self._decision_to_dict(decision),
                "context": context or {},
            },
            "metadata": {
                "runtime_health": decision.runtime_health,
                "resilience_decision": decision.decision,
                "recommended_autonomy_mode": (
                    decision.recommended_autonomy_mode
                ),
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
            print(f"⚠️ Strategic resilience lineage write failed: {exc}")

    def _emit_event(
        self,
        decision: StrategicResilienceDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "STRATEGIC_RESILIENCE_DECISION",
            "engine_name": self.engine_name,
            "decision": self._decision_to_dict(decision),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "STRATEGIC_RESILIENCE_DECISION",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "STRATEGIC_RESILIENCE_DECISION",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Strategic resilience event emit failed: {exc}")

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_signal(
        self,
        item: StrategicResilienceSignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> StrategicResilienceSignal:
        if isinstance(item, StrategicResilienceSignal):
            return item

        return StrategicResilienceSignal(
            signal_id=str(item.get("signal_id") or uuid.uuid4()),
            signal_type=self._safe_signal_type(item.get("signal_type")),
            domain=self._safe_domain(item.get("domain")),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_confidence(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=tenant_id or item.get("tenant_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            affected_subsystem=item.get("affected_subsystem"),
            current_autonomy_mode=self._safe_autonomy_mode(
                item.get("current_autonomy_mode")
            ),
            payload=dict(item.get("payload") or {}),
        )

    def _normal_decision(
        self,
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> StrategicResilienceDecision:
        return StrategicResilienceDecision(
            decision_id=str(uuid.uuid4()),
            decision=RESILIENCE_NORMAL,
            runtime_health=HEALTH_HEALTHY,
            selected_signal_id=None,
            selected_signal_type=None,
            affected_subsystem=None,
            severity=ResilienceSeverity.INFO.value,
            confidence=1.0,
            current_autonomy_mode=AUTONOMY_SUPERVISED_AUTONOMY,
            recommended_autonomy_mode=AUTONOMY_SUPERVISED_AUTONOMY,
            recommended_actions=[
                {
                    "action": "continue_normal_operations",
                    "reason": "No resilience signals were submitted.",
                }
            ],
            required_controls=[
                "operational_memory_recording",
                "lineage_recording",
            ],
            rationale="No resilience signals were submitted. Runtime assumed healthy.",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            suppressed_signal_ids=[],
        )

    # --------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------

    @staticmethod
    def _decision_to_dict(
        decision: StrategicResilienceDecision,
    ) -> Dict[str, Any]:
        return asdict(decision)

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_signal_type(value: Any) -> str:
        value = str(value or ResilienceSignalType.UNKNOWN.value).upper()
        valid = {item.value for item in ResilienceSignalType}
        return value if value in valid else ResilienceSignalType.UNKNOWN.value

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or ResilienceDomain.UNKNOWN.value).upper()
        valid = {item.value for item in ResilienceDomain}
        return value if value in valid else ResilienceDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or ResilienceSeverity.INFO.value).upper()
        valid = {item.value for item in ResilienceSeverity}
        return value if value in valid else ResilienceSeverity.INFO.value

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
    def _severity_weight(severity: str) -> int:
        return {
            ResilienceSeverity.INFO.value: 0,
            ResilienceSeverity.LOW.value: 1,
            ResilienceSeverity.MEDIUM.value: 2,
            ResilienceSeverity.HIGH.value: 3,
            ResilienceSeverity.CRITICAL.value: 4,
        }.get(str(severity).upper(), 0)

    @staticmethod
    def _signal_type_weight(signal_type: str) -> int:
        return {
            ResilienceSignalType.EVENT_BUS_FAILURE.value: 5,
            ResilienceSignalType.GOVERNANCE_DEGRADATION.value: 5,
            ResilienceSignalType.VERIFICATION_FAILURE.value: 5,
            ResilienceSignalType.HIGH_BLAST_RADIUS.value: 4,
            ResilienceSignalType.CONTINUITY_RISK.value: 4,
            ResilienceSignalType.COGNITION_CONFLICT.value: 4,
            ResilienceSignalType.WORKER_STALL.value: 3,
            ResilienceSignalType.EXECUTION_CONGESTION.value: 3,
            ResilienceSignalType.CONNECTOR_DEGRADATION.value: 3,
            ResilienceSignalType.LOW_TELEMETRY_CONFIDENCE.value: 2,
            ResilienceSignalType.MEMORY_WRITE_FAILURE.value: 2,
            ResilienceSignalType.LINEAGE_WRITE_FAILURE.value: 2,
            ResilienceSignalType.UNKNOWN.value: 1,
        }.get(str(signal_type).upper(), 1)


# ============================================================
# FACTORY
# ============================================================

def build_strategic_resilience_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
) -> StrategicResilienceEngine:
    """
    Factory for explicit dependency injection.
    """

    return StrategicResilienceEngine(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
    )