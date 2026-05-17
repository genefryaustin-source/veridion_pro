"""
core/runtime/sovereign_operational_reasoning_engine.py

Sovereign Operational Reasoning Engine.

Purpose:
- strategic sovereign operational reasoning
- mission-aware runtime cognition
- operational intent reasoning
- strategic tradeoff modeling
- survivability and continuity reasoning
- sovereignty-preserving strategy recommendations

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned reasoning memory only
- recommendations before destructive action
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


REASONING_STABLE = "STABLE"
REASONING_WATCH = "WATCH"
REASONING_CONSTRAINED = "CONSTRAINED"
REASONING_DEGRADED = "DEGRADED"
REASONING_CRITICAL = "CRITICAL"

PRIORITY_LOW = "LOW"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_HIGH = "HIGH"
PRIORITY_CRITICAL = "CRITICAL"

STRATEGY_OBSERVE = "OBSERVE"
STRATEGY_PRESERVE_CONTINUITY = "PRESERVE_CONTINUITY"
STRATEGY_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
STRATEGY_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
STRATEGY_RESTRICT_RELAYS = "RESTRICT_RELAYS"
STRATEGY_RESTRICT_FEDERATION = "RESTRICT_FEDERATION"
STRATEGY_TRIGGER_EXECUTION_COGNITION = "TRIGGER_EXECUTION_COGNITION"
STRATEGY_TRIGGER_PREDICTIVE_ASSESSMENT = "TRIGGER_PREDICTIVE_ASSESSMENT"
STRATEGY_TRIGGER_POLICY_REVIEW = "TRIGGER_POLICY_REVIEW"
STRATEGY_TRIGGER_MESH_OPTIMIZATION = "TRIGGER_MESH_OPTIMIZATION"
STRATEGY_TRIGGER_RECOVERY = "TRIGGER_RECOVERY"
STRATEGY_ESCALATE_GOVERNANCE = "ESCALATE_GOVERNANCE"
STRATEGY_PROTECT_SOVEREIGN_PATHS = "PROTECT_SOVEREIGN_PATHS"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class OperationalIntent:
    intent_id: str
    tenant_id: str = DEFAULT_TENANT
    objective: str = "maintain_sovereign_runtime_operations"
    mission_priority: str = PRIORITY_MEDIUM
    continuity_required: bool = True
    sovereignty_required: bool = True
    governance_required: bool = True
    high_sensitivity: bool = False
    categories: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OperationalReasoningSignal:
    signal_id: str
    signal_type: str
    severity: str
    source: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OperationalStrategy:
    strategy_id: str
    strategy_type: str
    priority: str
    reason: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    requires_approval: bool = True
    expected_benefit: str = ""
    tradeoffs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OperationalReasoningAssessment:
    assessment_id: str
    tenant_id: str
    reasoning_state: str
    mission_priority: str
    strategic_score: float
    confidence: float
    mission_survivability: float
    continuity_viability: float
    sovereignty_integrity: float
    summary: str
    intent: Dict[str, Any] = field(default_factory=dict)
    signals: List[OperationalReasoningSignal] = field(default_factory=list)
    strategies: List[OperationalStrategy] = field(default_factory=list)
    tradeoff_model: Dict[str, Any] = field(default_factory=dict)
    mission_model: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["signals"] = [
            s.to_dict() if hasattr(s, "to_dict") else s
            for s in self.signals
        ]
        data["strategies"] = [
            s.to_dict() if hasattr(s, "to_dict") else s
            for s in self.strategies
        ]
        return data


class SovereignOperationalReasoningEngine:
    def __init__(
        self,
        *,
        execution_cognition_engine: Any = None,
        predictive_engine: Any = None,
        learning_engine: Any = None,
        sovereignty_decision_engine: Any = None,
        adaptive_policy_engine: Any = None,
        mesh_optimizer: Any = None,
        execution_relay: Any = None,
        autonomy_governor: Any = None,
        recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.execution_cognition_engine = (
            execution_cognition_engine
            or getattr(storage, "autonomous_execution_cognition_engine", None)
        )
        self.predictive_engine = (
            predictive_engine
            or getattr(storage, "predictive_runtime_stability_engine", None)
        )
        self.learning_engine = (
            learning_engine
            or getattr(storage, "runtime_fabric_learning_engine", None)
        )
        self.sovereignty_decision_engine = (
            sovereignty_decision_engine
            or getattr(storage, "sovereignty_decision_engine", None)
        )
        self.adaptive_policy_engine = (
            adaptive_policy_engine
            or getattr(storage, "adaptive_sovereign_policy_engine", None)
        )
        self.mesh_optimizer = (
            mesh_optimizer
            or getattr(storage, "sovereign_mesh_optimizer", None)
        )
        self.execution_relay = (
            execution_relay
            or getattr(storage, "cross_runtime_execution_relay", None)
        )
        self.autonomy_governor = (
            autonomy_governor
            or getattr(storage, "autonomy_governor_v2", None)
        )
        self.recovery_manager = (
            recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._assessments: List[OperationalReasoningAssessment] = []
        self._signals: List[OperationalReasoningSignal] = []
        self._strategies: List[OperationalStrategy] = []

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        objective: str = "maintain_sovereign_runtime_operations",
        workload: Optional[Dict[str, Any]] = None,
    ) -> OperationalReasoningAssessment:
        workload = dict(workload or {})

        intent = self._build_intent(
            tenant_id=tenant_id,
            objective=objective,
            workload=workload,
        )

        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            intent=intent,
            workload=workload,
        )

        signals = self._derive_signals(
            tenant_id=tenant_id,
            intent=intent,
            telemetry=telemetry,
        )

        tradeoff_model = self._build_tradeoff_model(
            intent=intent,
            signals=signals,
            telemetry=telemetry,
        )

        mission_model = self._build_mission_model(
            intent=intent,
            signals=signals,
            telemetry=telemetry,
            tradeoff_model=tradeoff_model,
        )

        strategic_score = self._strategic_score(
            signals=signals,
            tradeoff_model=tradeoff_model,
            mission_model=mission_model,
        )

        reasoning_state = self._reasoning_state(strategic_score)

        confidence = self._confidence(
            signals=signals,
            telemetry=telemetry,
        )

        mission_survivability = float(
            mission_model.get("mission_survivability", 100.0)
        )

        continuity_viability = float(
            mission_model.get("continuity_viability", 100.0)
        )

        sovereignty_integrity = float(
            mission_model.get("sovereignty_integrity", 100.0)
        )

        strategies = self._strategies_for(
            tenant_id=tenant_id,
            intent=intent,
            reasoning_state=reasoning_state,
            strategic_score=strategic_score,
            signals=signals,
            tradeoff_model=tradeoff_model,
            mission_model=mission_model,
        )

        summary = self._summary(
            reasoning_state=reasoning_state,
            strategic_score=strategic_score,
            confidence=confidence,
            mission_survivability=mission_survivability,
            continuity_viability=continuity_viability,
            sovereignty_integrity=sovereignty_integrity,
            strategy_count=len(strategies),
        )

        assessment = OperationalReasoningAssessment(
            assessment_id=f"SOV-OPS-REASON-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            reasoning_state=reasoning_state,
            mission_priority=intent.mission_priority,
            strategic_score=strategic_score,
            confidence=confidence,
            mission_survivability=mission_survivability,
            continuity_viability=continuity_viability,
            sovereignty_integrity=sovereignty_integrity,
            summary=summary,
            intent=intent.to_dict(),
            signals=signals,
            strategies=strategies,
            tradeoff_model=tradeoff_model,
            mission_model=mission_model,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._signals.extend(signals)
        self._signals = self._signals[-1500:]

        self._strategies.extend(strategies)
        self._strategies = self._strategies[-1500:]

        self._emit(
            "SOVEREIGN_OPERATIONAL_REASONING_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    def enforce(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        objective: str = "maintain_sovereign_runtime_operations",
        workload: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        assessment = self.assess(
            tenant_id=tenant_id,
            objective=objective,
            workload=workload or {},
        )

        actions = []

        for strategy in assessment.strategies:
            if dry_run:
                actions.append({
                    "strategy_id": strategy.strategy_id,
                    "strategy": strategy.strategy_type,
                    "status": "DRY_RUN",
                    "reason": strategy.reason,
                })
            else:
                actions.append(self._execute_strategy(strategy))

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "actions": actions,
        }

        self._emit(
            "SOVEREIGN_OPERATIONAL_REASONING_ENFORCED",
            payload,
        )

        return payload

    def _build_intent(
        self,
        *,
        tenant_id: str,
        objective: str,
        workload: Dict[str, Any],
    ) -> OperationalIntent:
        categories = [
            str(c).upper()
            for c in workload.get("categories", [])
        ]

        high_sensitivity = bool(
            set(categories).intersection(
                {
                    "CUI",
                    "ITAR",
                    "EXPORT_CONTROLLED",
                    "CLASSIFIED",
                    "FEDRAMP_HIGH",
                    "MISSION_CRITICAL",
                }
            )
        )

        mission_priority = workload.get("mission_priority") or (
            PRIORITY_HIGH if high_sensitivity else PRIORITY_MEDIUM
        )

        return OperationalIntent(
            intent_id=f"OPS-INTENT-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            objective=objective,
            mission_priority=mission_priority,
            continuity_required=bool(workload.get("continuity_required", True)),
            sovereignty_required=bool(workload.get("sovereignty_required", True)),
            governance_required=bool(workload.get("governance_required", True)),
            high_sensitivity=high_sensitivity,
            categories=categories,
            constraints={
                "requires_govcloud": bool(workload.get("requires_govcloud", False)),
                "requires_high_trust": bool(workload.get("requires_high_trust", False)),
                "requires_approval": bool(workload.get("requires_approval", high_sensitivity)),
            },
        )

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
        intent: OperationalIntent,
        workload: Dict[str, Any],
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "intent": intent.to_dict(),
            "workload": workload,
            "collected_at_ms": _now_ms(),
        }

        def capture(key: str, fn) -> None:
            try:
                telemetry[key] = fn()
            except Exception as exc:
                telemetry[f"{key}_error"] = str(exc)

        if self.execution_cognition_engine is not None:
            capture(
                "execution_cognition_status",
                lambda: self.execution_cognition_engine.cognition_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "execution_cognition_assessment",
                lambda: self.execution_cognition_engine.assess(
                    tenant_id=tenant_id,
                    workload=workload,
                ).to_dict(),
            )

        if self.predictive_engine is not None:
            capture(
                "predictive_status",
                lambda: self.predictive_engine.predictive_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.learning_engine is not None:
            capture(
                "learning_status",
                lambda: self.learning_engine.learning_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.sovereignty_decision_engine is not None:
            capture(
                "sovereignty_decision_status",
                lambda: self.sovereignty_decision_engine.decision_engine_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.adaptive_policy_engine is not None:
            capture(
                "policy_status",
                lambda: self.adaptive_policy_engine.policy_engine_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.mesh_optimizer is not None:
            capture(
                "mesh_status",
                lambda: self.mesh_optimizer.optimizer_status(),
            )

        if self.execution_relay is not None:
            capture(
                "relay_status",
                lambda: self.execution_relay.relay_status(),
            )

        if self.autonomy_governor is not None:
            capture(
                "governor_status",
                lambda: self.autonomy_governor.governor_status(
                    tenant_id=tenant_id,
                ),
            )

        return telemetry

    def _derive_signals(
        self,
        *,
        tenant_id: str,
        intent: OperationalIntent,
        telemetry: Dict[str, Any],
    ) -> List[OperationalReasoningSignal]:
        signals: List[OperationalReasoningSignal] = []

        exec_assessment = telemetry.get("execution_cognition_assessment", {}) or {}

        if exec_assessment:
            state = str(exec_assessment.get("cognition_state") or "").upper()
            risk = str(exec_assessment.get("risk_level") or "").upper()

            if state in {"WATCH", "DEGRADED", "UNSTABLE", "CRITICAL"}:
                signals.append(
                    self._signal(
                        "EXECUTION_COGNITION_PRESSURE",
                        risk or PRIORITY_MEDIUM,
                        "autonomous_execution_cognition_engine",
                        f"Execution cognition reports state={state}.",
                        tenant_id,
                        confidence=float(exec_assessment.get("confidence", 0.6) or 0.6),
                        metadata=exec_assessment,
                    )
                )

            if float(exec_assessment.get("continuity_score", 100.0) or 100.0) < 70:
                signals.append(
                    self._signal(
                        "MISSION_CONTINUITY_PRESSURE",
                        PRIORITY_HIGH,
                        "autonomous_execution_cognition_engine",
                        "Execution continuity score is degraded.",
                        tenant_id,
                        confidence=0.75,
                        metadata=exec_assessment,
                    )
                )

            if float(exec_assessment.get("survivability_score", 100.0) or 100.0) < 70:
                signals.append(
                    self._signal(
                        "MISSION_SURVIVABILITY_PRESSURE",
                        PRIORITY_HIGH,
                        "autonomous_execution_cognition_engine",
                        "Mission survivability score is degraded.",
                        tenant_id,
                        confidence=0.75,
                        metadata=exec_assessment,
                    )
                )

        predictive = (
            telemetry.get("predictive_status", {})
            .get("latest_assessment")
            or {}
        )

        if str(predictive.get("predictive_state") or "").upper() in {
            "WATCH",
            "DEGRADING",
            "UNSTABLE",
            "CRITICAL",
        }:
            signals.append(
                self._signal(
                    "PREDICTIVE_RUNTIME_PRESSURE",
                    PRIORITY_HIGH,
                    "predictive_runtime_stability_engine",
                    "Predictive runtime state indicates future instability.",
                    tenant_id,
                    confidence=float(predictive.get("confidence", 0.6) or 0.6),
                    metadata=predictive,
                )
            )

        policy = (
            telemetry.get("policy_status", {})
            .get("latest_assessment")
            or {}
        )

        if str(policy.get("risk_level") or "").upper() in {"HIGH", "CRITICAL"}:
            signals.append(
                self._signal(
                    "POLICY_GOVERNANCE_PRESSURE",
                    str(policy.get("risk_level")).upper(),
                    "adaptive_sovereign_policy_engine",
                    "Adaptive policy engine reports elevated policy risk.",
                    tenant_id,
                    confidence=0.7,
                    metadata=policy,
                )
            )

        relay = telemetry.get("relay_status", {}) or {}
        if int(relay.get("failed", 0) or 0) > 0 or int(relay.get("blocked", 0) or 0) > 0:
            signals.append(
                self._signal(
                    "RELAY_CONTINUITY_PRESSURE",
                    PRIORITY_HIGH,
                    "cross_runtime_execution_relay",
                    "Relay continuity pressure detected.",
                    tenant_id,
                    confidence=0.72,
                    metadata=relay,
                )
            )

        if intent.high_sensitivity:
            signals.append(
                self._signal(
                    "SOVEREIGN_MISSION_CONTEXT",
                    PRIORITY_HIGH,
                    "operational_intent",
                    "High-sensitivity sovereign mission context detected.",
                    tenant_id,
                    confidence=0.85,
                    metadata=intent.to_dict(),
                )
            )

        return signals

    def _signal(
        self,
        signal_type: str,
        severity: str,
        source: str,
        message: str,
        tenant_id: str,
        *,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OperationalReasoningSignal:
        return OperationalReasoningSignal(
            signal_id=f"OPS-SIGNAL-{uuid.uuid4().hex[:12].upper()}",
            signal_type=signal_type,
            severity=severity,
            source=source,
            message=message,
            tenant_id=tenant_id,
            confidence=round(max(0.0, min(confidence, 1.0)), 3),
            metadata=metadata or {},
        )

    def _build_tradeoff_model(
        self,
        *,
        intent: OperationalIntent,
        signals: List[OperationalReasoningSignal],
        telemetry: Dict[str, Any],
    ) -> Dict[str, Any]:
        signal_types = {s.signal_type for s in signals}

        tradeoffs = []

        if intent.continuity_required and "RELAY_CONTINUITY_PRESSURE" in signal_types:
            tradeoffs.append({
                "tradeoff": "continuity_vs_relay_restriction",
                "tension": "HIGH",
                "preferred_bias": "preserve_continuity_with_governed_restriction",
            })

        if intent.sovereignty_required and "MISSION_CONTINUITY_PRESSURE" in signal_types:
            tradeoffs.append({
                "tradeoff": "sovereignty_vs_operational_continuity",
                "tension": "HIGH",
                "preferred_bias": "preserve_sovereignty_first",
            })

        if intent.governance_required and "POLICY_GOVERNANCE_PRESSURE" in signal_types:
            tradeoffs.append({
                "tradeoff": "autonomy_vs_governance",
                "tension": "HIGH",
                "preferred_bias": "reduce_autonomy_and_escalate_governance",
            })

        if "PREDICTIVE_RUNTIME_PRESSURE" in signal_types:
            tradeoffs.append({
                "tradeoff": "proactive_restriction_vs_throughput",
                "tension": "MEDIUM",
                "preferred_bias": "proactive_stabilization",
            })

        return {
            "tradeoff_count": len(tradeoffs),
            "tradeoffs": tradeoffs,
            "created_at_ms": _now_ms(),
        }

    def _build_mission_model(
        self,
        *,
        intent: OperationalIntent,
        signals: List[OperationalReasoningSignal],
        telemetry: Dict[str, Any],
        tradeoff_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        mission_survivability = 100.0
        continuity_viability = 100.0
        sovereignty_integrity = 100.0

        for signal in signals:
            sev = str(signal.severity or "").upper()

            penalty = {
                PRIORITY_LOW: 2.0,
                PRIORITY_MEDIUM: 6.0,
                PRIORITY_HIGH: 14.0,
                PRIORITY_CRITICAL: 25.0,
            }.get(sev, 6.0)

            if "CONTINUITY" in signal.signal_type:
                continuity_viability -= penalty

            if "SOVEREIGN" in signal.signal_type or "POLICY" in signal.signal_type:
                sovereignty_integrity -= penalty

            mission_survivability -= penalty * 0.6

        if intent.high_sensitivity:
            sovereignty_integrity -= 5.0

        if int(tradeoff_model.get("tradeoff_count", 0) or 0) > 0:
            mission_survivability -= 5.0 * int(tradeoff_model.get("tradeoff_count", 0))

        return {
            "mission_survivability": round(max(0.0, min(mission_survivability, 100.0)), 2),
            "continuity_viability": round(max(0.0, min(continuity_viability, 100.0)), 2),
            "sovereignty_integrity": round(max(0.0, min(sovereignty_integrity, 100.0)), 2),
            "mission_priority": intent.mission_priority,
            "objective": intent.objective,
        }

    def _strategic_score(
        self,
        *,
        signals: List[OperationalReasoningSignal],
        tradeoff_model: Dict[str, Any],
        mission_model: Dict[str, Any],
    ) -> float:
        pressure = 0.0

        weights = {
            PRIORITY_LOW: 5.0,
            PRIORITY_MEDIUM: 15.0,
            PRIORITY_HIGH: 30.0,
            PRIORITY_CRITICAL: 50.0,
        }

        for signal in signals:
            pressure += weights.get(str(signal.severity).upper(), 10.0) * float(
                signal.confidence or 0.5
            )

        pressure += int(tradeoff_model.get("tradeoff_count", 0) or 0) * 8.0

        pressure += max(0.0, 100.0 - float(mission_model.get("mission_survivability", 100.0))) * 0.25
        pressure += max(0.0, 100.0 - float(mission_model.get("continuity_viability", 100.0))) * 0.25
        pressure += max(0.0, 100.0 - float(mission_model.get("sovereignty_integrity", 100.0))) * 0.25

        return round(max(0.0, min(pressure, 100.0)), 2)

    def _reasoning_state(self, score: float) -> str:
        if score >= 80:
            return REASONING_CRITICAL
        if score >= 60:
            return REASONING_DEGRADED
        if score >= 40:
            return REASONING_CONSTRAINED
        if score >= 20:
            return REASONING_WATCH
        return REASONING_STABLE

    def _confidence(
        self,
        *,
        signals: List[OperationalReasoningSignal],
        telemetry: Dict[str, Any],
    ) -> float:
        if not signals:
            return 0.55

        avg_signal = sum(s.confidence for s in signals) / max(len(signals), 1)
        telemetry_quality = min(
            len([k for k in telemetry.keys() if not k.endswith("_error")]) * 0.025,
            0.25,
        )
        error_penalty = min(
            len([k for k in telemetry.keys() if k.endswith("_error")]) * 0.04,
            0.25,
        )

        return round(max(0.05, min(avg_signal + telemetry_quality - error_penalty, 0.98)), 3)

    def _strategies_for(
        self,
        *,
        tenant_id: str,
        intent: OperationalIntent,
        reasoning_state: str,
        strategic_score: float,
        signals: List[OperationalReasoningSignal],
        tradeoff_model: Dict[str, Any],
        mission_model: Dict[str, Any],
    ) -> List[OperationalStrategy]:
        strategies: List[OperationalStrategy] = []
        seen = set()
        signal_types = {s.signal_type for s in signals}

        def add(
            strategy_type: str,
            priority: str,
            reason: str,
            *,
            expected_benefit: str,
            tradeoffs: Optional[List[str]] = None,
            requires_approval: bool = True,
        ) -> None:
            key = (strategy_type, reason)
            if key in seen:
                return
            seen.add(key)
            strategies.append(
                OperationalStrategy(
                    strategy_id=f"OPS-STRATEGY-{uuid.uuid4().hex[:12].upper()}",
                    strategy_type=strategy_type,
                    priority=priority,
                    reason=reason,
                    tenant_id=tenant_id,
                    requires_approval=requires_approval,
                    expected_benefit=expected_benefit,
                    tradeoffs=tradeoffs or [],
                    metadata={
                        "reasoning_state": reasoning_state,
                        "strategic_score": strategic_score,
                        "mission_priority": intent.mission_priority,
                    },
                )
            )

        if not signals:
            add(
                STRATEGY_OBSERVE,
                PRIORITY_LOW,
                "No strategic operational pressure detected.",
                expected_benefit="Maintain current operational posture.",
                requires_approval=False,
            )
            return strategies

        if "MISSION_CONTINUITY_PRESSURE" in signal_types or "RELAY_CONTINUITY_PRESSURE" in signal_types:
            add(
                STRATEGY_PRESERVE_CONTINUITY,
                PRIORITY_HIGH,
                "Preserve sovereign mission continuity under degraded relay or execution conditions.",
                expected_benefit="Maintain operational survivability.",
                tradeoffs=["may reduce throughput", "may increase governance approvals"],
            )

        if "SOVEREIGN_MISSION_CONTEXT" in signal_types:
            add(
                STRATEGY_PROTECT_SOVEREIGN_PATHS,
                PRIORITY_HIGH,
                "Protect sovereign execution paths for high-sensitivity mission context.",
                expected_benefit="Preserve sovereign integrity.",
                tradeoffs=["may restrict federation", "may require approvals"],
            )
            add(
                STRATEGY_REQUIRE_APPROVAL,
                PRIORITY_HIGH,
                "Require governance approval for high-sensitivity sovereign mission actions.",
                expected_benefit="Maintain compliance and audit defensibility.",
            )

        if "POLICY_GOVERNANCE_PRESSURE" in signal_types:
            add(
                STRATEGY_TRIGGER_POLICY_REVIEW,
                PRIORITY_HIGH,
                "Trigger adaptive sovereign policy review under elevated governance pressure.",
                expected_benefit="Reduce policy drift and governance overload.",
                requires_approval=False,
            )
            add(
                STRATEGY_REDUCE_AUTONOMY,
                PRIORITY_HIGH,
                "Reduce autonomy under elevated governance pressure.",
                expected_benefit="Increase human control over sensitive operations.",
            )

        if "PREDICTIVE_RUNTIME_PRESSURE" in signal_types:
            add(
                STRATEGY_TRIGGER_PREDICTIVE_ASSESSMENT,
                PRIORITY_MEDIUM,
                "Refresh predictive assessment under future-state instability pressure.",
                expected_benefit="Improve early-warning accuracy.",
                requires_approval=False,
            )
            add(
                STRATEGY_TRIGGER_MESH_OPTIMIZATION,
                PRIORITY_MEDIUM,
                "Trigger mesh optimization before predicted instability materializes.",
                expected_benefit="Reduce future topology pressure.",
                requires_approval=False,
            )

        if reasoning_state in {REASONING_DEGRADED, REASONING_CRITICAL}:
            add(
                STRATEGY_ESCALATE_GOVERNANCE,
                PRIORITY_HIGH if reasoning_state == REASONING_DEGRADED else PRIORITY_CRITICAL,
                "Escalate governance due to degraded strategic operational reasoning state.",
                expected_benefit="Ensure command-level oversight.",
            )

        if float(mission_model.get("mission_survivability", 100.0)) < 60:
            add(
                STRATEGY_TRIGGER_RECOVERY,
                PRIORITY_HIGH,
                "Trigger runtime recovery because mission survivability is degraded.",
                expected_benefit="Recover mission-capable runtime pathways.",
                requires_approval=False,
            )

        return strategies

    def _execute_strategy(
        self,
        strategy: OperationalStrategy,
    ) -> Dict[str, Any]:
        try:
            if strategy.strategy_type == STRATEGY_TRIGGER_EXECUTION_COGNITION:
                return self._trigger_execution_cognition(strategy)

            if strategy.strategy_type == STRATEGY_TRIGGER_PREDICTIVE_ASSESSMENT:
                return self._trigger_predictive(strategy)

            if strategy.strategy_type == STRATEGY_TRIGGER_POLICY_REVIEW:
                return self._trigger_policy(strategy)

            if strategy.strategy_type == STRATEGY_TRIGGER_MESH_OPTIMIZATION:
                return self._trigger_mesh(strategy)

            if strategy.strategy_type == STRATEGY_TRIGGER_RECOVERY:
                return self._trigger_recovery(strategy)

            if strategy.strategy_type == STRATEGY_REDUCE_AUTONOMY:
                return self._reduce_autonomy(strategy)

            return {
                "strategy_id": strategy.strategy_id,
                "strategy": strategy.strategy_type,
                "status": "RECOMMENDED",
                "manual_or_policy_update_required": True,
                "reason": strategy.reason,
            }

        except Exception as exc:
            return {
                "strategy_id": strategy.strategy_id,
                "strategy": strategy.strategy_type,
                "status": "FAILED",
                "error": str(exc),
            }

    def _trigger_execution_cognition(self, strategy: OperationalStrategy) -> Dict[str, Any]:
        if self.execution_cognition_engine is None:
            return {"status": "SKIPPED", "reason": "execution_cognition_engine_unavailable"}

        assessment = self.execution_cognition_engine.assess(
            tenant_id=strategy.tenant_id,
            workload={"action": "SOVEREIGN_OPERATIONAL_REASONING_TRIGGER"},
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_predictive(self, strategy: OperationalStrategy) -> Dict[str, Any]:
        if self.predictive_engine is None:
            return {"status": "SKIPPED", "reason": "predictive_engine_unavailable"}

        assessment = self.predictive_engine.assess(
            tenant_id=strategy.tenant_id,
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_policy(self, strategy: OperationalStrategy) -> Dict[str, Any]:
        if self.adaptive_policy_engine is None:
            return {"status": "SKIPPED", "reason": "adaptive_policy_engine_unavailable"}

        assessment = self.adaptive_policy_engine.assess(
            tenant_id=strategy.tenant_id,
            workload={"action": "SOVEREIGN_OPERATIONAL_POLICY_REVIEW"},
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_mesh(self, strategy: OperationalStrategy) -> Dict[str, Any]:
        if self.mesh_optimizer is None:
            return {"status": "SKIPPED", "reason": "mesh_optimizer_unavailable"}

        result = self.mesh_optimizer.enforce(
            tenant_id=strategy.tenant_id,
            dry_run=True,
        )

        return {"status": "EXECUTED", "result": result}

    def _trigger_recovery(self, strategy: OperationalStrategy) -> Dict[str, Any]:
        if self.recovery_manager is None:
            return {"status": "SKIPPED", "reason": "recovery_manager_unavailable"}

        result = self.recovery_manager.auto_recover(
            tenant_id=strategy.tenant_id,
            actor="sovereign_operational_reasoning_engine",
            force=False,
        )

        return {
            "status": "EXECUTED",
            "result": result.to_dict() if hasattr(result, "to_dict") else {},
        }

    def _reduce_autonomy(self, strategy: OperationalStrategy) -> Dict[str, Any]:
        if self.autonomy_governor is None:
            return {"status": "SKIPPED", "reason": "autonomy_governor_unavailable"}

        result = self.autonomy_governor.set_autonomy_mode(
            tenant_id=strategy.tenant_id,
            mode="ASSISTED",
            reason=strategy.reason,
        )

        return {"status": "EXECUTED", "result": result}

    def list_assessments(self, *, limit: int = 100) -> List[Dict[str, Any]]:
        rows = sorted(self._assessments, key=lambda a: a.created_at_ms, reverse=True)
        return [r.to_dict() for r in rows[:limit]]

    def list_signals(self, *, limit: int = 100) -> List[Dict[str, Any]]:
        rows = sorted(self._signals, key=lambda s: s.created_at_ms, reverse=True)
        return [r.to_dict() for r in rows[:limit]]

    def list_strategies(self, *, limit: int = 100) -> List[Dict[str, Any]]:
        rows = sorted(self._strategies, key=lambda s: s.created_at_ms, reverse=True)
        return [r.to_dict() for r in rows[:limit]]

    def reasoning_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "tenant_id": tenant_id,
            "assessment_count": len(self._assessments),
            "signal_count": len(self._signals),
            "strategy_count": len(self._strategies),
            "latest_assessment": latest,
        }

    def _summary(
        self,
        *,
        reasoning_state: str,
        strategic_score: float,
        confidence: float,
        mission_survivability: float,
        continuity_viability: float,
        sovereignty_integrity: float,
        strategy_count: int,
    ) -> str:
        return (
            f"Strategic reasoning state={reasoning_state}, "
            f"score={strategic_score}, confidence={confidence}. "
            f"Mission survivability={mission_survivability}, "
            f"continuity={continuity_viability}, "
            f"sovereignty={sovereignty_integrity}. "
            f"Strategies={strategy_count}."
        )

    def _emit(self, event_type: str, payload: Dict[str, Any]) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                source="sovereign_operational_reasoning_engine",
                severity=payload.get("reasoning_state") or "INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(event_type=event_type, payload=payload)
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_SOVEREIGN_OPERATIONAL_REASONING_ENGINE: Optional[
    SovereignOperationalReasoningEngine
] = None


def get_sovereign_operational_reasoning_engine(
    *,
    execution_cognition_engine: Any = None,
    predictive_engine: Any = None,
    learning_engine: Any = None,
    sovereignty_decision_engine: Any = None,
    adaptive_policy_engine: Any = None,
    mesh_optimizer: Any = None,
    execution_relay: Any = None,
    autonomy_governor: Any = None,
    recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> SovereignOperationalReasoningEngine:
    global _DEFAULT_SOVEREIGN_OPERATIONAL_REASONING_ENGINE

    if reset or _DEFAULT_SOVEREIGN_OPERATIONAL_REASONING_ENGINE is None:
        _DEFAULT_SOVEREIGN_OPERATIONAL_REASONING_ENGINE = (
            SovereignOperationalReasoningEngine(
                execution_cognition_engine=execution_cognition_engine,
                predictive_engine=predictive_engine,
                learning_engine=learning_engine,
                sovereignty_decision_engine=sovereignty_decision_engine,
                adaptive_policy_engine=adaptive_policy_engine,
                mesh_optimizer=mesh_optimizer,
                execution_relay=execution_relay,
                autonomy_governor=autonomy_governor,
                recovery_manager=recovery_manager,
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_SOVEREIGN_OPERATIONAL_REASONING_ENGINE