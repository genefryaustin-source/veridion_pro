"""
core/runtime/sovereign_ai_coordination_engine.py

Sovereign AI Coordination Engine

Coordinates multiple sovereign cognition engines into one governed,
mission-aware, deterministic coordination layer.

This engine does NOT own low-level execution.
It arbitrates, aligns, prioritizes, and records AI coordination decisions.

Primary responsibilities:
- Multi-engine cognition arbitration
- Mission-priority coordination
- Governance-aware AI alignment
- Sovereignty-aware execution coordination
- Cross-domain AI synchronization
- Audit-ready coordination records
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

SEVERITY_INFO = "INFO"
SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

COORDINATION_STATUS_ACCEPTED = "ACCEPTED"
COORDINATION_STATUS_REJECTED = "REJECTED"
COORDINATION_STATUS_DEFERRED = "DEFERRED"
COORDINATION_STATUS_REQUIRES_GOVERNANCE = "REQUIRES_GOVERNANCE"
COORDINATION_STATUS_REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"

DEFAULT_ENGINE_NAME = "sovereign_ai_coordination_engine"


class CoordinationMode(str, Enum):
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
    FULL_AUTONOMY = "FULL_AUTONOMY"
    LOCKDOWN = "LOCKDOWN"


class CoordinationDomain(str, Enum):
    RUNTIME = "RUNTIME"
    GOVERNANCE = "GOVERNANCE"
    CONTINUITY = "CONTINUITY"
    SECURITY = "SECURITY"
    MEMORY = "MEMORY"
    CASES = "CASES"
    COMPLIANCE = "COMPLIANCE"
    FEDRAMP = "FEDRAMP"
    CMMC = "CMMC"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


class CoordinationIntent(str, Enum):
    OBSERVE = "OBSERVE"
    RECOMMEND = "RECOMMEND"
    PRIORITIZE = "PRIORITIZE"
    ALIGN = "ALIGN"
    ESCALATE = "ESCALATE"
    CONTAIN = "CONTAIN"
    DEFER = "DEFER"
    BLOCK = "BLOCK"
    RECORD = "RECORD"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class SovereignAICoordinationSignal:
    """
    A proposed signal, recommendation, or intent from one cognition engine.
    """

    signal_id: str
    source_engine: str
    domain: str
    intent: str
    severity: str
    confidence: float
    mission_priority: int
    summary: str
    payload: Dict[str, Any] = field(default_factory=dict)
    requires_governance: bool = False
    requires_human_approval: bool = False
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class SovereignAICoordinationDecision:
    """
    Final coordination decision after arbitration.
    """

    decision_id: str
    status: str
    coordination_mode: str
    selected_signal_id: Optional[str]
    selected_source_engine: Optional[str]
    selected_domain: Optional[str]
    selected_intent: Optional[str]
    severity: str
    confidence: float
    mission_priority: int
    rationale: str
    recommended_actions: List[Dict[str, Any]]
    suppressed_signal_ids: List[str]
    governance_required: bool
    human_approval_required: bool
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class SovereignAICoordinationSnapshot:
    """
    Lightweight runtime state snapshot for UI panels and audit surfaces.
    """

    engine_name: str
    coordination_mode: str
    total_signals_seen: int
    total_decisions_made: int
    last_decision_id: Optional[str]
    last_status: Optional[str]
    last_severity: Optional[str]
    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class SovereignAICoordinationEngine:
    """
    Coordinates sovereign AI cognition across runtime, governance,
    continuity, memory, case, compliance, and future telemetry domains.

    This is intentionally deterministic:
    - No hidden shared global state
    - No direct Streamlit/session dependency
    - No connector execution
    - No mutation outside explicit engine-owned state
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        coordination_mode: str = CoordinationMode.SUPERVISED_AUTONOMY.value,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        governance_engine: Optional[Any] = None,
        mission_continuity_engine: Optional[Any] = None,
        runtime_cognition_orchestrator: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.coordination_mode = coordination_mode

        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.governance_engine = governance_engine
        self.mission_continuity_engine = mission_continuity_engine
        self.runtime_cognition_orchestrator = runtime_cognition_orchestrator

        self._signals_seen = 0
        self._decisions: List[SovereignAICoordinationDecision] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def coordinate(
        self,
        signals: Sequence[SovereignAICoordinationSignal | Dict[str, Any]],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignAICoordinationDecision:
        """
        Coordinate multiple cognition signals into one sovereign decision.
        """

        normalized = [
            self._normalize_signal(
                signal,
                tenant_id=tenant_id,
                case_id=case_id,
            )
            for signal in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:
            decision = self._empty_decision(
                tenant_id=tenant_id,
                case_id=case_id,
            )
            self._record_decision(decision, context=context)
            return decision

        selected = self._select_highest_priority_signal(normalized)

        suppressed = [
            signal.signal_id
            for signal in normalized
            if signal.signal_id != selected.signal_id
        ]

        status = self._determine_status(selected)
        rationale = self._build_rationale(selected, normalized, status)

        decision = SovereignAICoordinationDecision(
            decision_id=str(uuid.uuid4()),
            status=status,
            coordination_mode=self.coordination_mode,
            selected_signal_id=selected.signal_id,
            selected_source_engine=selected.source_engine,
            selected_domain=selected.domain,
            selected_intent=selected.intent,
            severity=selected.severity,
            confidence=selected.confidence,
            mission_priority=selected.mission_priority,
            rationale=rationale,
            recommended_actions=self._build_recommended_actions(selected, status),
            suppressed_signal_ids=suppressed,
            governance_required=selected.requires_governance,
            human_approval_required=selected.requires_human_approval,
            tenant_id=tenant_id or selected.tenant_id,
            case_id=case_id or selected.case_id,
        )

        self._record_decision(decision, context=context)
        return decision

    def ingest_signal(
        self,
        *,
        source_engine: str,
        domain: str,
        intent: str,
        severity: str,
        confidence: float,
        mission_priority: int,
        summary: str,
        payload: Optional[Dict[str, Any]] = None,
        requires_governance: bool = False,
        requires_human_approval: bool = False,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
    ) -> SovereignAICoordinationSignal:
        """
        Create a normalized coordination signal.
        """

        return SovereignAICoordinationSignal(
            signal_id=str(uuid.uuid4()),
            source_engine=source_engine,
            domain=self._safe_domain(domain),
            intent=self._safe_intent(intent),
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            mission_priority=max(0, int(mission_priority)),
            summary=summary or "",
            payload=payload or {},
            requires_governance=requires_governance,
            requires_human_approval=requires_human_approval,
            tenant_id=tenant_id,
            case_id=case_id,
        )

    def get_recent_decisions(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignAICoordinationDecision]:
        """
        Return most recent coordination decisions.
        """

        limit = max(1, int(limit))
        return list(reversed(self._decisions[-limit:]))

    def snapshot(self) -> SovereignAICoordinationSnapshot:
        """
        Return current engine status snapshot.
        """

        last = self._decisions[-1] if self._decisions else None

        return SovereignAICoordinationSnapshot(
            engine_name=self.engine_name,
            coordination_mode=self.coordination_mode,
            total_signals_seen=self._signals_seen,
            total_decisions_made=len(self._decisions),
            last_decision_id=last.decision_id if last else None,
            last_status=last.status if last else None,
            last_severity=last.severity if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # ARBITRATION
    # --------------------------------------------------------

    def _select_highest_priority_signal(
        self,
        signals: Sequence[SovereignAICoordinationSignal],
    ) -> SovereignAICoordinationSignal:
        """
        Deterministic ranking:
        1. severity weight
        2. mission priority
        3. governance/human approval sensitivity
        4. confidence
        5. oldest signal first for stable ordering
        """

        return sorted(
            signals,
            key=lambda s: (
                self._severity_weight(s.severity),
                s.mission_priority,
                1 if s.requires_governance else 0,
                1 if s.requires_human_approval else 0,
                s.confidence,
                -s.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _determine_status(
        self,
        signal: SovereignAICoordinationSignal,
    ) -> str:
        """
        Determine decision status based on coordination mode and governance needs.
        """

        mode = self.coordination_mode

        if mode == CoordinationMode.LOCKDOWN.value:
            return COORDINATION_STATUS_REJECTED

        if signal.requires_human_approval:
            return COORDINATION_STATUS_REQUIRES_HUMAN_APPROVAL

        if signal.requires_governance:
            return COORDINATION_STATUS_REQUIRES_GOVERNANCE

        if mode == CoordinationMode.MANUAL.value:
            return COORDINATION_STATUS_REQUIRES_HUMAN_APPROVAL

        if mode == CoordinationMode.ASSISTED.value:
            return COORDINATION_STATUS_DEFERRED

        return COORDINATION_STATUS_ACCEPTED

    # --------------------------------------------------------
    # RECORDING / EVENTS
    # --------------------------------------------------------

    def _record_decision(
        self,
        decision: SovereignAICoordinationDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Persist internally and optionally emit/write to external services.
        """

        self._decisions.append(decision)

        self._write_to_operational_memory(decision, context=context)
        self._emit_event(decision, context=context)

    def _write_to_operational_memory(
        self,
        decision: SovereignAICoordinationDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Append coordination decision to sovereign operational memory when available.
        """

        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "SOVEREIGN_AI_COORDINATION_DECISION",
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
            print(f"⚠️ Sovereign AI coordination memory write failed: {exc}")

    def _emit_event(
        self,
        decision: SovereignAICoordinationDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit event if an event bus is attached.
        """

        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGN_AI_COORDINATION_DECISION",
            "engine": self.engine_name,
            "decision": self._decision_to_dict(decision),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_AI_COORDINATION_DECISION",
                    payload,
                )
            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "SOVEREIGN_AI_COORDINATION_DECISION",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Sovereign AI coordination event emit failed: {exc}")

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def _empty_decision(
        self,
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
    ) -> SovereignAICoordinationDecision:
        return SovereignAICoordinationDecision(
            decision_id=str(uuid.uuid4()),
            status=COORDINATION_STATUS_DEFERRED,
            coordination_mode=self.coordination_mode,
            selected_signal_id=None,
            selected_source_engine=None,
            selected_domain=None,
            selected_intent=None,
            severity=SEVERITY_INFO,
            confidence=0.0,
            mission_priority=0,
            rationale="No coordination signals were provided.",
            recommended_actions=[],
            suppressed_signal_ids=[],
            governance_required=False,
            human_approval_required=False,
            tenant_id=tenant_id,
            case_id=case_id,
        )

    def _normalize_signal(
        self,
        signal: SovereignAICoordinationSignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
    ) -> SovereignAICoordinationSignal:
        if isinstance(signal, SovereignAICoordinationSignal):
            return signal

        return SovereignAICoordinationSignal(
            signal_id=str(signal.get("signal_id") or uuid.uuid4()),
            source_engine=str(signal.get("source_engine") or "unknown_engine"),
            domain=self._safe_domain(signal.get("domain")),
            intent=self._safe_intent(signal.get("intent")),
            severity=self._safe_severity(signal.get("severity")),
            confidence=self._clamp_confidence(signal.get("confidence", 0.0)),
            mission_priority=max(0, int(signal.get("mission_priority", 0) or 0)),
            summary=str(signal.get("summary") or ""),
            payload=dict(signal.get("payload") or {}),
            requires_governance=bool(signal.get("requires_governance", False)),
            requires_human_approval=bool(signal.get("requires_human_approval", False)),
            tenant_id=tenant_id or signal.get("tenant_id"),
            case_id=case_id or signal.get("case_id"),
        )

    def _build_rationale(
        self,
        selected: SovereignAICoordinationSignal,
        signals: Sequence[SovereignAICoordinationSignal],
        status: str,
    ) -> str:
        return (
            f"Selected signal from {selected.source_engine} in domain "
            f"{selected.domain} with severity {selected.severity}, "
            f"mission priority {selected.mission_priority}, confidence "
            f"{selected.confidence:.2f}. Coordination status: {status}. "
            f"Arbitrated across {len(signals)} signal(s)."
        )

    def _build_recommended_actions(
        self,
        selected: SovereignAICoordinationSignal,
        status: str,
    ) -> List[Dict[str, Any]]:
        if status == COORDINATION_STATUS_REJECTED:
            return [
                {
                    "action": "block_execution",
                    "reason": "Coordination mode is LOCKDOWN or signal was rejected.",
                }
            ]

        if status == COORDINATION_STATUS_REQUIRES_HUMAN_APPROVAL:
            return [
                {
                    "action": "request_human_approval",
                    "domain": selected.domain,
                    "intent": selected.intent,
                    "summary": selected.summary,
                }
            ]

        if status == COORDINATION_STATUS_REQUIRES_GOVERNANCE:
            return [
                {
                    "action": "route_to_governance",
                    "domain": selected.domain,
                    "intent": selected.intent,
                    "summary": selected.summary,
                }
            ]

        if status == COORDINATION_STATUS_DEFERRED:
            return [
                {
                    "action": "defer_for_review",
                    "domain": selected.domain,
                    "intent": selected.intent,
                    "summary": selected.summary,
                }
            ]

        return [
            {
                "action": "accept_coordination_signal",
                "domain": selected.domain,
                "intent": selected.intent,
                "summary": selected.summary,
            }
        ]

    @staticmethod
    def _safe_domain(value: Any) -> str:
        value = str(value or CoordinationDomain.UNKNOWN.value).upper()
        valid = {item.value for item in CoordinationDomain}
        return value if value in valid else CoordinationDomain.UNKNOWN.value

    @staticmethod
    def _safe_intent(value: Any) -> str:
        value = str(value or CoordinationIntent.OBSERVE.value).upper()
        valid = {item.value for item in CoordinationIntent}
        return value if value in valid else CoordinationIntent.OBSERVE.value

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or SEVERITY_INFO).upper()
        valid = {
            SEVERITY_INFO,
            SEVERITY_LOW,
            SEVERITY_MEDIUM,
            SEVERITY_HIGH,
            SEVERITY_CRITICAL,
        }
        return value if value in valid else SEVERITY_INFO

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
            SEVERITY_INFO: 0,
            SEVERITY_LOW: 1,
            SEVERITY_MEDIUM: 2,
            SEVERITY_HIGH: 3,
            SEVERITY_CRITICAL: 4,
        }.get(str(severity).upper(), 0)

    @staticmethod
    def _decision_to_dict(
        decision: SovereignAICoordinationDecision,
    ) -> Dict[str, Any]:
        return {
            "decision_id": decision.decision_id,
            "status": decision.status,
            "coordination_mode": decision.coordination_mode,
            "selected_signal_id": decision.selected_signal_id,
            "selected_source_engine": decision.selected_source_engine,
            "selected_domain": decision.selected_domain,
            "selected_intent": decision.selected_intent,
            "severity": decision.severity,
            "confidence": decision.confidence,
            "mission_priority": decision.mission_priority,
            "rationale": decision.rationale,
            "recommended_actions": decision.recommended_actions,
            "suppressed_signal_ids": decision.suppressed_signal_ids,
            "governance_required": decision.governance_required,
            "human_approval_required": decision.human_approval_required,
            "tenant_id": decision.tenant_id,
            "case_id": decision.case_id,
            "created_at_ms": decision.created_at_ms,
        }


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_ai_coordination_engine(
    *,
    coordination_mode: str = CoordinationMode.SUPERVISED_AUTONOMY.value,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    governance_engine: Optional[Any] = None,
    mission_continuity_engine: Optional[Any] = None,
    runtime_cognition_orchestrator: Optional[Any] = None,
) -> SovereignAICoordinationEngine:
    """
    Factory for explicit dependency injection.
    """

    return SovereignAICoordinationEngine(
        coordination_mode=coordination_mode,
        event_bus=event_bus,
        operational_memory_engine=operational_memory_engine,
        governance_engine=governance_engine,
        mission_continuity_engine=mission_continuity_engine,
        runtime_cognition_orchestrator=runtime_cognition_orchestrator,
    )