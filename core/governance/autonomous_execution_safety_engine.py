"""
core/governance/autonomous_execution_safety_engine.py

Autonomous Execution Safety Engine

Runtime safety cognition layer for autonomous execution governance.

This engine evaluates:
- execution drift
- autonomy escalation pressure
- cascading retries
- failover accumulation
- connector degradation
- verification failures
- rollback pressure
- governance degradation
- continuity instability
- blast-radius accumulation

IMPORTANT:
This engine DOES NOT:
- execute connectors
- mutate external systems
- directly freeze tenants/connectors
- directly change autonomy mode
- perform rollback

It ONLY:
- evaluates runtime safety posture
- generates deterministic safety decisions
- recommends freeze/autonomy/rollback/governance actions
- records replayable safety lineage and compliance evidence
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

DEFAULT_ENGINE_NAME = "autonomous_execution_safety_engine"

SAFETY_NORMAL = "NORMAL"
SAFETY_ELEVATED = "ELEVATED"
SAFETY_DEGRADED = "DEGRADED"
SAFETY_CRITICAL = "CRITICAL"
SAFETY_LOCKDOWN_RECOMMENDED = "LOCKDOWN_RECOMMENDED"
SAFETY_FREEZE_RECOMMENDED = "FREEZE_RECOMMENDED"
SAFETY_ROLLBACK_ONLY_RECOMMENDED = "ROLLBACK_ONLY_RECOMMENDED"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"

FREEZE_NONE = "NONE"
FREEZE_TENANT = "TENANT"
FREEZE_GLOBAL = "GLOBAL"
FREEZE_CONNECTOR = "CONNECTOR"
FREEZE_ROLLBACK_ONLY = "ROLLBACK_ONLY"

BLAST_RADIUS_LOW = "LOW"
BLAST_RADIUS_MEDIUM = "MEDIUM"
BLAST_RADIUS_HIGH = "HIGH"
BLAST_RADIUS_CRITICAL = "CRITICAL"


# ============================================================
# ENUMS
# ============================================================

class SafetySignalType(str, Enum):
    EXECUTION_DRIFT = "EXECUTION_DRIFT"
    AUTONOMY_ESCALATION = "AUTONOMY_ESCALATION"
    EXECUTION_SATURATION = "EXECUTION_SATURATION"
    CASCADING_RETRIES = "CASCADING_RETRIES"
    CONNECTOR_DEGRADATION = "CONNECTOR_DEGRADATION"
    FAILOVER_ACCUMULATION = "FAILOVER_ACCUMULATION"
    VERIFICATION_FAILURE = "VERIFICATION_FAILURE"
    ROLLBACK_PRESSURE = "ROLLBACK_PRESSURE"
    GOVERNANCE_DEGRADATION = "GOVERNANCE_DEGRADATION"
    CONTINUITY_INSTABILITY = "CONTINUITY_INSTABILITY"
    BLAST_RADIUS_ACCUMULATION = "BLAST_RADIUS_ACCUMULATION"
    BLOCKED_ACTION_SPIKE = "BLOCKED_ACTION_SPIKE"
    TENANT_POLICY_PRESSURE = "TENANT_POLICY_PRESSURE"
    NETWORK_ANOMALY_PRESSURE = "NETWORK_ANOMALY_PRESSURE"
    UNKNOWN = "UNKNOWN"


class SafetySeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SafetyDomain(str, Enum):
    RUNTIME = "RUNTIME"
    EXECUTION = "EXECUTION"
    GOVERNANCE = "GOVERNANCE"
    CONNECTOR = "CONNECTOR"
    CONTINUITY = "CONTINUITY"
    VERIFICATION = "VERIFICATION"
    ROLLBACK = "ROLLBACK"
    NETWORK = "NETWORK"
    TENANT = "TENANT"
    UNKNOWN = "UNKNOWN"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class AutonomousExecutionSafetySignal:
    """
    Runtime safety signal entering the safety engine.
    """

    safety_signal_id: str
    signal_type: str
    domain: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    affected_connector: Optional[str] = None
    affected_subsystem: Optional[str] = None

    current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY
    current_freeze_mode: str = FREEZE_NONE
    blast_radius: str = BLAST_RADIUS_LOW

    event_count: int = 1
    retry_count: int = 0
    failover_count: int = 0
    verification_failure_count: int = 0
    blocked_action_count: int = 0
    rollback_recommendation_count: int = 0

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class AutonomousExecutionSafetyDecision:
    """
    Deterministic safety decision.

    This is NOT an execution command.
    """

    safety_decision_id: str
    status: str
    safety_score: float
    autonomy_pressure_score: float
    governance_pressure_score: float
    resilience_pressure_score: float
    execution_instability_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]
    domain: Optional[str]

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    current_autonomy_mode: str
    recommended_autonomy_mode: str
    current_freeze_mode: str
    recommended_freeze_mode: str

    blast_radius: str
    severity: str
    confidence: float

    recommended_actions: List[Dict[str, Any]]
    required_controls: List[str]
    constraints: List[str]
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class AutonomousExecutionSafetySnapshot:
    """
    Lightweight runtime diagnostics snapshot.
    """

    engine_name: str
    total_signals_seen: int
    total_decisions_created: int
    last_decision_id: Optional[str]
    last_status: Optional[str]
    last_safety_score: Optional[float]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class AutonomousExecutionSafetyEngine:
    """
    Autonomous runtime safety cognition engine.

    Design guarantees:
    - no connector execution
    - no external mutation
    - deterministic safety posture
    - explicit dependency injection
    - replayable safety lineage
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
        self._decisions: List[AutonomousExecutionSafetyDecision] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AutonomousExecutionSafetyDecision:
        """
        Evaluate safety posture from one or more runtime safety signals.
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

        selected = self._select_highest_pressure_signal(normalized)

        safety_score = self._safety_score(normalized)
        autonomy_pressure = self._autonomy_pressure_score(normalized)
        governance_pressure = self._governance_pressure_score(normalized)
        resilience_pressure = self._resilience_pressure_score(normalized)
        execution_instability = self._execution_instability_score(normalized)

        status = self._determine_status(
            selected=selected,
            safety_score=safety_score,
            autonomy_pressure=autonomy_pressure,
            governance_pressure=governance_pressure,
            resilience_pressure=resilience_pressure,
            execution_instability=execution_instability,
        )

        recommended_autonomy = self._recommended_autonomy_mode(
            selected,
            status,
        )

        recommended_freeze = self._recommended_freeze_mode(
            selected,
            status,
        )

        decision = AutonomousExecutionSafetyDecision(
            safety_decision_id=str(uuid.uuid4()),
            status=status,
            safety_score=safety_score,
            autonomy_pressure_score=autonomy_pressure,
            governance_pressure_score=governance_pressure,
            resilience_pressure_score=resilience_pressure,
            execution_instability_score=execution_instability,
            selected_signal_id=selected.safety_signal_id,
            selected_signal_type=selected.signal_type,
            domain=selected.domain,
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            current_autonomy_mode=selected.current_autonomy_mode,
            recommended_autonomy_mode=recommended_autonomy,
            current_freeze_mode=selected.current_freeze_mode,
            recommended_freeze_mode=recommended_freeze,
            blast_radius=selected.blast_radius,
            severity=selected.severity,
            confidence=selected.confidence,
            recommended_actions=self._recommended_actions(
                selected,
                status,
                recommended_autonomy,
                recommended_freeze,
            ),
            required_controls=self._required_controls(
                selected,
                status,
                recommended_autonomy,
                recommended_freeze,
            ),
            constraints=self._constraints(selected, status),
            rationale=self._build_rationale(
                selected=selected,
                status=status,
                safety_score=safety_score,
                autonomy_pressure=autonomy_pressure,
                governance_pressure=governance_pressure,
                resilience_pressure=resilience_pressure,
                execution_instability=execution_instability,
                signal_count=len(normalized),
                recommended_autonomy=recommended_autonomy,
                recommended_freeze=recommended_freeze,
            ),
            metadata={
                "evaluated_signal_ids": [
                    item.safety_signal_id for item in normalized
                ],
                "affected_connector": selected.affected_connector,
                "affected_subsystem": selected.affected_subsystem,
                "event_count": selected.event_count,
                "retry_count": selected.retry_count,
                "failover_count": selected.failover_count,
                "verification_failure_count": (
                    selected.verification_failure_count
                ),
                "blocked_action_count": selected.blocked_action_count,
                "rollback_recommendation_count": (
                    selected.rollback_recommendation_count
                ),
            },
        )

        self._record_decision(decision, context=context)
        return decision

    def submit(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AutonomousExecutionSafetyDecision:
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
        affected_connector: Optional[str] = None,
        affected_subsystem: Optional[str] = None,
        current_autonomy_mode: str = AUTONOMY_SUPERVISED_AUTONOMY,
        current_freeze_mode: str = FREEZE_NONE,
        blast_radius: str = BLAST_RADIUS_LOW,
        event_count: int = 1,
        retry_count: int = 0,
        failover_count: int = 0,
        verification_failure_count: int = 0,
        blocked_action_count: int = 0,
        rollback_recommendation_count: int = 0,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AutonomousExecutionSafetySignal:
        """
        Convenience constructor.
        """

        return AutonomousExecutionSafetySignal(
            safety_signal_id=str(uuid.uuid4()),
            signal_type=self._safe_signal_type(signal_type),
            domain=self._safe_domain(domain),
            source_engine=source_engine or "unknown_engine",
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            summary=summary or "",
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            affected_connector=affected_connector,
            affected_subsystem=affected_subsystem,
            current_autonomy_mode=self._safe_autonomy_mode(
                current_autonomy_mode
            ),
            current_freeze_mode=self._safe_freeze_mode(current_freeze_mode),
            blast_radius=self._safe_blast_radius(blast_radius),
            event_count=max(0, int(event_count)),
            retry_count=max(0, int(retry_count)),
            failover_count=max(0, int(failover_count)),
            verification_failure_count=max(
                0,
                int(verification_failure_count),
            ),
            blocked_action_count=max(0, int(blocked_action_count)),
            rollback_recommendation_count=max(
                0,
                int(rollback_recommendation_count),
            ),
            payload=payload or {},
        )

    def get_recent_decisions(
        self,
        *,
        limit: int = 25,
    ) -> List[AutonomousExecutionSafetyDecision]:
        limit = max(1, int(limit))
        return list(reversed(self._decisions[-limit:]))

    def snapshot(self) -> AutonomousExecutionSafetySnapshot:
        last = self._decisions[-1] if self._decisions else None

        return AutonomousExecutionSafetySnapshot(
            engine_name=self.engine_name,
            total_signals_seen=self._signals_seen,
            total_decisions_created=len(self._decisions),
            last_decision_id=last.safety_decision_id if last else None,
            last_status=last.status if last else None,
            last_safety_score=last.safety_score if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # SCORING
    # --------------------------------------------------------

    def _select_highest_pressure_signal(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal],
    ) -> AutonomousExecutionSafetySignal:
        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(item.severity),
                self._signal_type_weight(item.signal_type),
                item.retry_count,
                item.failover_count,
                item.verification_failure_count,
                item.blocked_action_count,
                item.rollback_recommendation_count,
                item.event_count,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _safety_score(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal],
    ) -> float:
        if not signals:
            return 0.0

        raw = 0.0

        for item in signals:
            raw += self._severity_weight(item.severity) * 10
            raw += self._signal_type_weight(item.signal_type) * 5
            raw += min(item.event_count, 25) * 1.5
            raw += min(item.retry_count, 10) * 4
            raw += min(item.failover_count, 10) * 5
            raw += min(item.verification_failure_count, 10) * 7
            raw += min(item.blocked_action_count, 10) * 5
            raw += min(item.rollback_recommendation_count, 10) * 6

            if item.blast_radius == BLAST_RADIUS_CRITICAL:
                raw += 25
            elif item.blast_radius == BLAST_RADIUS_HIGH:
                raw += 15

            if item.current_autonomy_mode == AUTONOMY_FULL_AUTONOMY:
                raw += 10

        return self._clamp_score(raw / max(1, len(signals)))

    def _autonomy_pressure_score(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal],
    ) -> float:
        raw = 0.0

        for item in signals:
            if item.current_autonomy_mode == AUTONOMY_FULL_AUTONOMY:
                raw += 30
            elif item.current_autonomy_mode == AUTONOMY_SUPERVISED_AUTONOMY:
                raw += 15
            elif item.current_autonomy_mode == AUTONOMY_ASSISTED:
                raw += 7

            if item.signal_type == SafetySignalType.AUTONOMY_ESCALATION.value:
                raw += 35

            if item.blast_radius in {
                BLAST_RADIUS_HIGH,
                BLAST_RADIUS_CRITICAL,
            }:
                raw += 15

        return self._clamp_score(raw / max(1, len(signals)))

    def _governance_pressure_score(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal],
    ) -> float:
        raw = 0.0

        for item in signals:
            if item.signal_type == SafetySignalType.GOVERNANCE_DEGRADATION.value:
                raw += 40

            if item.signal_type == SafetySignalType.BLOCKED_ACTION_SPIKE.value:
                raw += 25

            if item.signal_type == SafetySignalType.TENANT_POLICY_PRESSURE.value:
                raw += 25

            if item.blocked_action_count:
                raw += min(item.blocked_action_count, 10) * 6

        return self._clamp_score(raw / max(1, len(signals)))

    def _resilience_pressure_score(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal],
    ) -> float:
        raw = 0.0

        for item in signals:
            if item.signal_type in {
                SafetySignalType.CONNECTOR_DEGRADATION.value,
                SafetySignalType.FAILOVER_ACCUMULATION.value,
                SafetySignalType.CONTINUITY_INSTABILITY.value,
                SafetySignalType.NETWORK_ANOMALY_PRESSURE.value,
            }:
                raw += 30

            raw += min(item.failover_count, 10) * 6
            raw += min(item.rollback_recommendation_count, 10) * 5

        return self._clamp_score(raw / max(1, len(signals)))

    def _execution_instability_score(
        self,
        signals: Sequence[AutonomousExecutionSafetySignal],
    ) -> float:
        raw = 0.0

        for item in signals:
            if item.signal_type in {
                SafetySignalType.EXECUTION_DRIFT.value,
                SafetySignalType.EXECUTION_SATURATION.value,
                SafetySignalType.CASCADING_RETRIES.value,
                SafetySignalType.VERIFICATION_FAILURE.value,
            }:
                raw += 35

            raw += min(item.retry_count, 10) * 6
            raw += min(item.verification_failure_count, 10) * 8
            raw += min(item.event_count, 25) * 1.5

        return self._clamp_score(raw / max(1, len(signals)))

    # --------------------------------------------------------
    # DECISIONING
    # --------------------------------------------------------

    def _determine_status(
        self,
        *,
        selected: AutonomousExecutionSafetySignal,
        safety_score: float,
        autonomy_pressure: float,
        governance_pressure: float,
        resilience_pressure: float,
        execution_instability: float,
    ) -> str:
        if selected.current_freeze_mode != FREEZE_NONE:
            return SAFETY_FREEZE_RECOMMENDED

        if selected.current_autonomy_mode == AUTONOMY_LOCKDOWN:
            return SAFETY_LOCKDOWN_RECOMMENDED

        if safety_score >= 90:
            return SAFETY_LOCKDOWN_RECOMMENDED

        if (
            execution_instability >= 85
            or resilience_pressure >= 85
            or selected.blast_radius == BLAST_RADIUS_CRITICAL
        ):
            return SAFETY_FREEZE_RECOMMENDED

        if (
            governance_pressure >= 75
            or autonomy_pressure >= 75
            or selected.signal_type
            in {
                SafetySignalType.GOVERNANCE_DEGRADATION.value,
                SafetySignalType.AUTONOMY_ESCALATION.value,
            }
        ):
            return SAFETY_ROLLBACK_ONLY_RECOMMENDED

        if safety_score >= 70:
            return SAFETY_CRITICAL

        if safety_score >= 50:
            return SAFETY_DEGRADED

        if safety_score >= 30:
            return SAFETY_ELEVATED

        return SAFETY_NORMAL

    def _recommended_autonomy_mode(
        self,
        selected: AutonomousExecutionSafetySignal,
        status: str,
    ) -> str:
        if status == SAFETY_LOCKDOWN_RECOMMENDED:
            return AUTONOMY_LOCKDOWN

        if status in {
            SAFETY_FREEZE_RECOMMENDED,
            SAFETY_ROLLBACK_ONLY_RECOMMENDED,
            SAFETY_CRITICAL,
        }:
            return self._reduce_autonomy(selected.current_autonomy_mode)

        if status == SAFETY_DEGRADED:
            if selected.current_autonomy_mode == AUTONOMY_FULL_AUTONOMY:
                return AUTONOMY_SUPERVISED_AUTONOMY

        return selected.current_autonomy_mode

    def _recommended_freeze_mode(
        self,
        selected: AutonomousExecutionSafetySignal,
        status: str,
    ) -> str:
        if status == SAFETY_LOCKDOWN_RECOMMENDED:
            return FREEZE_GLOBAL

        if status == SAFETY_FREEZE_RECOMMENDED:
            if selected.tenant_id:
                return FREEZE_TENANT
            return FREEZE_GLOBAL

        if status == SAFETY_ROLLBACK_ONLY_RECOMMENDED:
            return FREEZE_ROLLBACK_ONLY

        if selected.signal_type == SafetySignalType.CONNECTOR_DEGRADATION.value:
            return FREEZE_CONNECTOR

        return selected.current_freeze_mode

    # --------------------------------------------------------
    # OUTPUT BUILDERS
    # --------------------------------------------------------

    def _recommended_actions(
        self,
        selected: AutonomousExecutionSafetySignal,
        status: str,
        recommended_autonomy: str,
        recommended_freeze: str,
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        if status == SAFETY_NORMAL:
            actions.append(
                {
                    "action": "continue_operations",
                    "reason": "Safety posture is normal.",
                }
            )

        if status == SAFETY_ELEVATED:
            actions.append(
                {
                    "action": "increase_monitoring",
                    "reason": "Safety pressure is elevated.",
                }
            )

        if status == SAFETY_DEGRADED:
            actions.append(
                {
                    "action": "enter_degraded_safety_posture",
                    "reason": "Runtime safety score indicates degradation.",
                }
            )

        if status == SAFETY_CRITICAL:
            actions.append(
                {
                    "action": "escalate_to_governance",
                    "reason": "Runtime safety pressure is critical.",
                }
            )

        if status == SAFETY_LOCKDOWN_RECOMMENDED:
            actions.append(
                {
                    "action": "recommend_autonomy_lockdown",
                    "reason": "Runtime safety score exceeds lockdown threshold.",
                }
            )

        if status == SAFETY_FREEZE_RECOMMENDED:
            actions.append(
                {
                    "action": "recommend_execution_freeze",
                    "freeze_mode": recommended_freeze,
                }
            )

        if status == SAFETY_ROLLBACK_ONLY_RECOMMENDED:
            actions.append(
                {
                    "action": "recommend_rollback_only_mode",
                    "reason": "Governance/autonomy pressure requires rollback-only posture.",
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

        if recommended_freeze != selected.current_freeze_mode:
            actions.append(
                {
                    "action": "recommend_freeze_mode_change",
                    "from": selected.current_freeze_mode,
                    "to": recommended_freeze,
                }
            )

        actions.append(
            {
                "action": "record_safety_lineage",
                "reason": "Safety decision must be replayable.",
            }
        )

        actions.append(
            {
                "action": "record_safety_compliance_evidence",
                "reason": "Safety decision contributes to audit evidence.",
            }
        )

        return actions

    def _required_controls(
        self,
        selected: AutonomousExecutionSafetySignal,
        status: str,
        recommended_autonomy: str,
        recommended_freeze: str,
    ) -> List[str]:
        controls: List[str] = []

        if status in {
            SAFETY_LOCKDOWN_RECOMMENDED,
            SAFETY_FREEZE_RECOMMENDED,
            SAFETY_ROLLBACK_ONLY_RECOMMENDED,
        }:
            controls.append("operator_notification")

        if recommended_autonomy != selected.current_autonomy_mode:
            controls.append("autonomy_governance_review")

        if recommended_freeze != selected.current_freeze_mode:
            controls.append("freeze_governance_review")

        if selected.verification_failure_count:
            controls.append("verification_recovery")

        if selected.failover_count:
            controls.append("failover_review")

        if selected.rollback_recommendation_count:
            controls.append("rollback_review")

        if selected.blast_radius in {
            BLAST_RADIUS_HIGH,
            BLAST_RADIUS_CRITICAL,
        }:
            controls.append("blast_radius_review")

        controls.append("lineage_recording")
        controls.append("evidence_recording")

        return list(dict.fromkeys(controls))

    def _constraints(
        self,
        selected: AutonomousExecutionSafetySignal,
        status: str,
    ) -> List[str]:
        constraints: List[str] = []

        if selected.signal_type != SafetySignalType.UNKNOWN.value:
            constraints.append(f"safety_signal_{selected.signal_type.lower()}")

        if status != SAFETY_NORMAL:
            constraints.append(f"safety_status_{status.lower()}")

        if selected.blast_radius in {
            BLAST_RADIUS_HIGH,
            BLAST_RADIUS_CRITICAL,
        }:
            constraints.append("high_blast_radius_pressure")

        if selected.retry_count:
            constraints.append("retry_pressure")

        if selected.failover_count:
            constraints.append("failover_pressure")

        if selected.verification_failure_count:
            constraints.append("verification_failure_pressure")

        if selected.blocked_action_count:
            constraints.append("blocked_action_pressure")

        if selected.rollback_recommendation_count:
            constraints.append("rollback_pressure")

        return list(dict.fromkeys(constraints))

    def _build_rationale(
        self,
        *,
        selected: AutonomousExecutionSafetySignal,
        status: str,
        safety_score: float,
        autonomy_pressure: float,
        governance_pressure: float,
        resilience_pressure: float,
        execution_instability: float,
        signal_count: int,
        recommended_autonomy: str,
        recommended_freeze: str,
    ) -> str:
        return (
            f"Autonomous execution safety evaluation selected signal "
            f"{selected.signal_type} from {selected.source_engine}. "
            f"Safety score {safety_score:.2f}; autonomy pressure "
            f"{autonomy_pressure:.2f}; governance pressure "
            f"{governance_pressure:.2f}; resilience pressure "
            f"{resilience_pressure:.2f}; execution instability "
            f"{execution_instability:.2f}. Status {status}. "
            f"Recommended autonomy {recommended_autonomy}; recommended "
            f"freeze mode {recommended_freeze}. Evaluated across "
            f"{signal_count} signal(s)."
        )

    # --------------------------------------------------------
    # RECORDING
    # --------------------------------------------------------

    def _record_decision(
        self,
        decision: AutonomousExecutionSafetyDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._decisions.append(decision)
        self._write_to_memory(decision, context=context)
        self._write_to_lineage(decision, context=context)
        self._write_to_evidence(decision, context=context)
        self._emit_event(decision, context=context)

    def _write_to_memory(
        self,
        decision: AutonomousExecutionSafetyDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "AUTONOMOUS_EXECUTION_SAFETY_DECISION",
            "decision": asdict(decision),
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
            print(f"⚠️ Autonomous safety memory write failed: {exc}")

    def _write_to_lineage(
        self,
        decision: AutonomousExecutionSafetyDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "GOVERNANCE",
            "lineage_status": "RECORDED",
            "source_engine": self.engine_name,
            "summary": decision.rationale,
            "severity": decision.severity,
            "confidence": decision.confidence,
            "mission_priority": 0,
            "tenant_id": decision.tenant_id,
            "case_id": decision.case_id,
            "correlation_id": decision.correlation_id,
            "constraints": list(decision.constraints),
            "verification_requirements": list(decision.required_controls),
            "context": {
                "type": "AUTONOMOUS_EXECUTION_SAFETY_DECISION",
                "decision": asdict(decision),
                "context": context or {},
            },
            "metadata": {
                "safety_decision_id": decision.safety_decision_id,
                "status": decision.status,
                "safety_score": decision.safety_score,
                "recommended_autonomy_mode": (
                    decision.recommended_autonomy_mode
                ),
                "recommended_freeze_mode": (
                    decision.recommended_freeze_mode
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
            print(f"⚠️ Autonomous safety lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        decision: AutonomousExecutionSafetyDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        evidence = self.fedramp_evidence_lineage_engine
        if evidence is None:
            return

        payload = {
            "evidence_type": "POLICY_EVALUATION",
            "evidence_status": "RECORDED",
            "source_engine": self.engine_name,
            "summary": decision.rationale,
            "severity": decision.severity,
            "confidence": decision.confidence,
            "mission_priority": 0,
            "tenant_id": decision.tenant_id,
            "case_id": decision.case_id,
            "correlation_id": decision.correlation_id,
            "constraints": list(decision.constraints),
            "evidence_payload": {
                "type": "AUTONOMOUS_EXECUTION_SAFETY_DECISION",
                "decision": asdict(decision),
                "context": context or {},
            },
            "metadata": {
                "safety_decision_id": decision.safety_decision_id,
                "status": decision.status,
                "safety_score": decision.safety_score,
                "recommended_autonomy_mode": (
                    decision.recommended_autonomy_mode
                ),
                "recommended_freeze_mode": (
                    decision.recommended_freeze_mode
                ),
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
            print(f"⚠️ Autonomous safety evidence write failed: {exc}")

    def _emit_event(
        self,
        decision: AutonomousExecutionSafetyDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "AUTONOMOUS_EXECUTION_SAFETY_DECISION",
            "engine_name": self.engine_name,
            "decision": asdict(decision),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "AUTONOMOUS_EXECUTION_SAFETY_DECISION",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "AUTONOMOUS_EXECUTION_SAFETY_DECISION",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Autonomous safety event emit failed: {exc}")

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize_signal(
        self,
        item: AutonomousExecutionSafetySignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> AutonomousExecutionSafetySignal:
        if isinstance(item, AutonomousExecutionSafetySignal):
            return item

        return AutonomousExecutionSafetySignal(
            safety_signal_id=str(
                item.get("safety_signal_id") or uuid.uuid4()
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
            affected_connector=item.get("affected_connector"),
            affected_subsystem=item.get("affected_subsystem"),
            current_autonomy_mode=self._safe_autonomy_mode(
                item.get("current_autonomy_mode")
            ),
            current_freeze_mode=self._safe_freeze_mode(
                item.get("current_freeze_mode")
            ),
            blast_radius=self._safe_blast_radius(item.get("blast_radius")),
            event_count=max(0, int(item.get("event_count", 1) or 0)),
            retry_count=max(0, int(item.get("retry_count", 0) or 0)),
            failover_count=max(0, int(item.get("failover_count", 0) or 0)),
            verification_failure_count=max(
                0,
                int(item.get("verification_failure_count", 0) or 0),
            ),
            blocked_action_count=max(
                0,
                int(item.get("blocked_action_count", 0) or 0),
            ),
            rollback_recommendation_count=max(
                0,
                int(item.get("rollback_recommendation_count", 0) or 0),
            ),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _normal_decision(
        self,
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> AutonomousExecutionSafetyDecision:
        return AutonomousExecutionSafetyDecision(
            safety_decision_id=str(uuid.uuid4()),
            status=SAFETY_NORMAL,
            safety_score=0.0,
            autonomy_pressure_score=0.0,
            governance_pressure_score=0.0,
            resilience_pressure_score=0.0,
            execution_instability_score=0.0,
            selected_signal_id=None,
            selected_signal_type=None,
            domain=None,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            current_autonomy_mode=AUTONOMY_SUPERVISED_AUTONOMY,
            recommended_autonomy_mode=AUTONOMY_SUPERVISED_AUTONOMY,
            current_freeze_mode=FREEZE_NONE,
            recommended_freeze_mode=FREEZE_NONE,
            blast_radius=BLAST_RADIUS_LOW,
            severity=SafetySeverity.INFO.value,
            confidence=1.0,
            recommended_actions=[
                {
                    "action": "continue_operations",
                    "reason": "No safety signals were submitted.",
                }
            ],
            required_controls=[
                "lineage_recording",
                "evidence_recording",
            ],
            constraints=[],
            rationale=(
                "No autonomous execution safety signals were submitted. "
                "Safety posture assumed normal."
            ),
            metadata={},
        )

    # --------------------------------------------------------
    # SAFETY HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _safe_signal_type(value: Any) -> str:
        value = str(value or SafetySignalType.UNKNOWN.value).upper()
        valid = {item.value for item in SafetySignalType}
        return value if value in valid else SafetySignalType.UNKNOWN.value

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or SafetyDomain.UNKNOWN.value).upper()
        valid = {item.value for item in SafetyDomain}
        return value if value in valid else SafetyDomain.UNKNOWN.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or SafetySeverity.INFO.value).upper()
        valid = {item.value for item in SafetySeverity}
        return value if value in valid else SafetySeverity.INFO.value

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
    def _safe_freeze_mode(value: Any) -> str:
        value = str(value or FREEZE_NONE).upper()
        valid = {
            FREEZE_NONE,
            FREEZE_TENANT,
            FREEZE_GLOBAL,
            FREEZE_CONNECTOR,
            FREEZE_ROLLBACK_ONLY,
        }
        return value if value in valid else FREEZE_NONE

    @staticmethod
    def _safe_blast_radius(value: Any) -> str:
        value = str(value or BLAST_RADIUS_LOW).upper()
        valid = {
            BLAST_RADIUS_LOW,
            BLAST_RADIUS_MEDIUM,
            BLAST_RADIUS_HIGH,
            BLAST_RADIUS_CRITICAL,
        }
        return value if value in valid else BLAST_RADIUS_LOW

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
            SafetySeverity.INFO.value: 0,
            SafetySeverity.LOW.value: 1,
            SafetySeverity.MEDIUM.value: 2,
            SafetySeverity.HIGH.value: 3,
            SafetySeverity.CRITICAL.value: 4,
        }.get(str(severity).upper(), 0)

    @staticmethod
    def _signal_type_weight(signal_type: str) -> int:
        return {
            SafetySignalType.EXECUTION_DRIFT.value: 3,
            SafetySignalType.AUTONOMY_ESCALATION.value: 5,
            SafetySignalType.EXECUTION_SATURATION.value: 4,
            SafetySignalType.CASCADING_RETRIES.value: 5,
            SafetySignalType.CONNECTOR_DEGRADATION.value: 3,
            SafetySignalType.FAILOVER_ACCUMULATION.value: 4,
            SafetySignalType.VERIFICATION_FAILURE.value: 5,
            SafetySignalType.ROLLBACK_PRESSURE.value: 4,
            SafetySignalType.GOVERNANCE_DEGRADATION.value: 5,
            SafetySignalType.CONTINUITY_INSTABILITY.value: 5,
            SafetySignalType.BLAST_RADIUS_ACCUMULATION.value: 5,
            SafetySignalType.BLOCKED_ACTION_SPIKE.value: 4,
            SafetySignalType.TENANT_POLICY_PRESSURE.value: 4,
            SafetySignalType.NETWORK_ANOMALY_PRESSURE.value: 4,
            SafetySignalType.UNKNOWN.value: 1,
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

def build_autonomous_execution_safety_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> AutonomousExecutionSafetyEngine:
    """
    Factory for explicit dependency injection.
    """

    return AutonomousExecutionSafetyEngine(
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )