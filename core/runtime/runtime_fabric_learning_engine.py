"""
core/runtime/runtime_fabric_learning_engine.py

Runtime Fabric Learning Engine.

Purpose:
- sovereign runtime learning system
- operational memory for runtime fabric behavior
- decision/outcome quality scoring
- topology behavior modeling
- relay/routing/cluster/domain learning
- predictive signal generation foundation

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned learning memory only
- learning signals before enforcement
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


LEARNING_SIGNAL_LOW = "LOW"
LEARNING_SIGNAL_MEDIUM = "MEDIUM"
LEARNING_SIGNAL_HIGH = "HIGH"
LEARNING_SIGNAL_CRITICAL = "CRITICAL"

PATTERN_STABLE = "STABLE"
PATTERN_DEGRADING = "DEGRADING"
PATTERN_UNSTABLE = "UNSTABLE"
PATTERN_RECURRING = "RECURRING"
PATTERN_UNKNOWN = "UNKNOWN"

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL = "PARTIAL"
OUTCOME_FAILED = "FAILED"
OUTCOME_BLOCKED = "BLOCKED"
OUTCOME_UNKNOWN = "UNKNOWN"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class FabricLearningEvent:
    event_id: str
    event_type: str
    tenant_id: str = DEFAULT_TENANT
    source: str = "runtime_fabric_learning_engine"
    outcome: str = OUTCOME_UNKNOWN
    target: Optional[str] = None
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FabricLearningPattern:
    pattern_id: str
    pattern_type: str
    severity: str
    confidence: float
    message: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    event_count: int = 0
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FabricLearningAssessment:
    assessment_id: str
    tenant_id: str
    learning_state: str
    confidence: float
    stability_score: float
    patterns: List[FabricLearningPattern] = field(default_factory=list)
    learned_signals: List[Dict[str, Any]] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["patterns"] = [
            p.to_dict() if hasattr(p, "to_dict") else p
            for p in self.patterns
        ]
        return data


class RuntimeFabricLearningEngine:
    def __init__(
        self,
        *,
        sovereignty_decision_engine: Any = None,
        adaptive_policy_engine: Any = None,
        mesh_optimizer: Any = None,
        cluster_balancer: Any = None,
        execution_relay: Any = None,
        federated_router: Any = None,
        cluster_manager: Any = None,
        domain_manager: Any = None,
        recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
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
        self.cluster_balancer = (
            cluster_balancer
            or getattr(storage, "autonomous_cluster_balancer", None)
        )
        self.execution_relay = (
            execution_relay
            or getattr(storage, "cross_runtime_execution_relay", None)
        )
        self.federated_router = (
            federated_router
            or getattr(storage, "federated_execution_router", None)
        )
        self.cluster_manager = (
            cluster_manager
            or getattr(storage, "distributed_runtime_cluster_manager", None)
        )
        self.domain_manager = (
            domain_manager
            or getattr(storage, "execution_domain_manager", None)
        )
        self.recovery_manager = (
            recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._events: List[FabricLearningEvent] = []
        self._patterns: List[FabricLearningPattern] = []
        self._assessments: List[FabricLearningAssessment] = []
        self._target_scores: Dict[str, Dict[str, Any]] = {}

    # ========================================================
    # INGEST
    # ========================================================

    def record_event(
        self,
        *,
        event_type: str,
        tenant_id: str = DEFAULT_TENANT,
        source: str = "external",
        outcome: str = OUTCOME_UNKNOWN,
        target: Optional[str] = None,
        score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FabricLearningEvent:
        event = FabricLearningEvent(
            event_id=f"LEARN-EVENT-{uuid.uuid4().hex[:12].upper()}",
            event_type=event_type,
            tenant_id=tenant_id,
            source=source,
            outcome=outcome,
            target=target,
            score=float(score or 0.0),
            metadata=metadata or {},
        )

        self._events.append(event)
        self._events = self._events[-5000:]

        self._update_target_score(event)

        self._emit(
            "RUNTIME_FABRIC_LEARNING_EVENT_RECORDED",
            event.to_dict(),
        )

        return event

    def ingest_current_state(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
        )

        created = []

        created.extend(
            self._ingest_sovereignty_decisions(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        created.extend(
            self._ingest_policy_assessments(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        created.extend(
            self._ingest_mesh_assessments(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        created.extend(
            self._ingest_balancer_assessments(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        created.extend(
            self._ingest_relay_results(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        payload = {
            "ok": True,
            "tenant_id": tenant_id,
            "created_events": len(created),
            "event_ids": [
                e.event_id for e in created
            ],
        }

        self._emit(
            "RUNTIME_FABRIC_LEARNING_STATE_INGESTED",
            payload,
        )

        return payload

    # ========================================================
    # ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> FabricLearningAssessment:
        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
        )

        patterns = self._derive_patterns(
            tenant_id=tenant_id,
            telemetry=telemetry,
        )

        stability_score = self._stability_score(
            patterns=patterns,
            telemetry=telemetry,
        )

        learning_state = self._learning_state(
            stability_score=stability_score,
            patterns=patterns,
        )

        confidence = self._confidence(
            patterns=patterns,
            telemetry=telemetry,
        )

        learned_signals = self._learned_signals(
            patterns=patterns,
            stability_score=stability_score,
            confidence=confidence,
        )

        assessment = FabricLearningAssessment(
            assessment_id=f"FABRIC-LEARN-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            learning_state=learning_state,
            confidence=confidence,
            stability_score=stability_score,
            patterns=patterns,
            learned_signals=learned_signals,
            telemetry=telemetry,
        )

        self._patterns.extend(patterns)
        self._patterns = self._patterns[-1000:]

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._emit(
            "RUNTIME_FABRIC_LEARNING_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # TELEMETRY
    # ========================================================

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "collected_at_ms": _now_ms(),
            "event_count": len(self._events),
            "target_scores": self._target_scores,
        }

        def capture(key: str, fn) -> None:
            try:
                telemetry[key] = fn()
            except Exception as exc:
                telemetry[f"{key}_error"] = str(exc)

        if self.sovereignty_decision_engine is not None:
            capture(
                "sovereignty_decision_status",
                lambda: self.sovereignty_decision_engine.decision_engine_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "sovereignty_decisions",
                lambda: self.sovereignty_decision_engine.list_decisions(limit=100),
            )

        if self.adaptive_policy_engine is not None:
            capture(
                "policy_engine_status",
                lambda: self.adaptive_policy_engine.policy_engine_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "policy_assessments",
                lambda: self.adaptive_policy_engine.list_assessments(limit=100),
            )

        if self.mesh_optimizer is not None:
            capture(
                "mesh_optimizer_status",
                lambda: self.mesh_optimizer.optimizer_status(),
            )
            capture(
                "mesh_assessments",
                lambda: self.mesh_optimizer.list_assessments(limit=100),
            )

        if self.cluster_balancer is not None:
            capture(
                "balancer_status",
                lambda: self.cluster_balancer.balancer_status(),
            )
            capture(
                "balancer_assessments",
                lambda: self.cluster_balancer.list_assessments(limit=100),
            )

        if self.execution_relay is not None:
            capture(
                "relay_status",
                lambda: self.execution_relay.relay_status(),
            )
            capture(
                "relay_results",
                lambda: self.execution_relay.list_results(limit=100),
            )

        if self.federated_router is not None:
            capture(
                "routing_status",
                lambda: self.federated_router.routing_status(),
            )
            capture(
                "route_decisions",
                lambda: self.federated_router.list_decisions(limit=100),
            )

        if self.cluster_manager is not None:
            capture(
                "cluster_health",
                lambda: self.cluster_manager.cluster_health(),
            )
            capture(
                "clusters",
                lambda: self.cluster_manager.list_clusters(tenant_id=tenant_id),
            )

        if self.domain_manager is not None:
            capture(
                "domain_health",
                lambda: self.domain_manager.domain_health(),
            )
            capture(
                "domains",
                lambda: self.domain_manager.list_domains(tenant_id=tenant_id),
            )

        return telemetry

    # ========================================================
    # INGEST HELPERS
    # ========================================================

    def _ingest_sovereignty_decisions(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningEvent]:
        events = []

        for decision in telemetry.get("sovereignty_decisions", []) or []:
            dtype = decision.get("decision_type") or decision.get("decision")
            status = decision.get("status")
            risk = decision.get("risk_level")

            outcome = OUTCOME_SUCCESS
            if status in {"FAILED"}:
                outcome = OUTCOME_FAILED
            elif dtype in {"LOCKDOWN", "QUARANTINE_DOMAIN", "QUARANTINE_CLUSTER"}:
                outcome = OUTCOME_PARTIAL
            elif status in {"BLOCKED"}:
                outcome = OUTCOME_BLOCKED

            events.append(
                self.record_event(
                    event_type=f"SOVEREIGN_DECISION:{dtype}",
                    tenant_id=tenant_id,
                    source="sovereignty_decision_engine",
                    outcome=outcome,
                    target=decision.get("target"),
                    score=float(decision.get("confidence", 0.0) or 0.0) * 100,
                    metadata={
                        "risk_level": risk,
                        "decision": decision,
                    },
                )
            )

        return events

    def _ingest_policy_assessments(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningEvent]:
        events = []

        for assessment in telemetry.get("policy_assessments", []) or []:
            risk = assessment.get("risk_level")
            pressure = float(assessment.get("policy_pressure_score", 0.0) or 0.0)

            outcome = OUTCOME_SUCCESS
            if risk in {"HIGH", "CRITICAL"}:
                outcome = OUTCOME_PARTIAL

            events.append(
                self.record_event(
                    event_type="POLICY_ASSESSMENT",
                    tenant_id=tenant_id,
                    source="adaptive_sovereign_policy_engine",
                    outcome=outcome,
                    score=max(0.0, 100.0 - pressure),
                    metadata=assessment,
                )
            )

        return events

    def _ingest_mesh_assessments(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningEvent]:
        events = []

        for assessment in telemetry.get("mesh_assessments", []) or []:
            status = assessment.get("status")
            score = float(assessment.get("optimization_score", 0.0) or 0.0)

            outcome = OUTCOME_SUCCESS
            if status in {"DEGRADED"}:
                outcome = OUTCOME_PARTIAL
            elif status in {"CRITICAL"}:
                outcome = OUTCOME_FAILED

            events.append(
                self.record_event(
                    event_type="MESH_OPTIMIZATION_ASSESSMENT",
                    tenant_id=tenant_id,
                    source="sovereign_mesh_optimizer",
                    outcome=outcome,
                    score=score,
                    metadata=assessment,
                )
            )

        return events

    def _ingest_balancer_assessments(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningEvent]:
        events = []

        for assessment in telemetry.get("balancer_assessments", []) or []:
            status = assessment.get("status")
            score = 100.0 - float(assessment.get("risk_score", 0.0) or 0.0)

            outcome = OUTCOME_SUCCESS
            if status in {"PRESSURE", "DEGRADED"}:
                outcome = OUTCOME_PARTIAL
            elif status in {"CRITICAL"}:
                outcome = OUTCOME_FAILED

            events.append(
                self.record_event(
                    event_type="CLUSTER_BALANCE_ASSESSMENT",
                    tenant_id=tenant_id,
                    source="autonomous_cluster_balancer",
                    outcome=outcome,
                    score=score,
                    metadata=assessment,
                )
            )

        return events

    def _ingest_relay_results(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningEvent]:
        events = []

        for result in telemetry.get("relay_results", []) or []:
            ok = bool(result.get("ok"))
            status = result.get("status")

            outcome = OUTCOME_SUCCESS if ok else OUTCOME_FAILED
            if status == "BLOCKED":
                outcome = OUTCOME_BLOCKED

            events.append(
                self.record_event(
                    event_type="CROSS_RUNTIME_RELAY_RESULT",
                    tenant_id=tenant_id,
                    source="cross_runtime_execution_relay",
                    outcome=outcome,
                    target=result.get("target_runtime_id"),
                    score=100.0 if ok else 0.0,
                    metadata=result,
                )
            )

        return events

    # ========================================================
    # PATTERNS
    # ========================================================

    def _derive_patterns(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningPattern]:
        events = [
            e for e in self._events
            if e.tenant_id == tenant_id
        ]

        patterns: List[FabricLearningPattern] = []

        patterns.extend(
            self._failure_patterns(
                tenant_id=tenant_id,
                events=events,
            )
        )

        patterns.extend(
            self._target_instability_patterns(
                tenant_id=tenant_id,
                events=events,
            )
        )

        patterns.extend(
            self._pressure_patterns(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        return patterns

    def _failure_patterns(
        self,
        *,
        tenant_id: str,
        events: List[FabricLearningEvent],
    ) -> List[FabricLearningPattern]:
        failed = [
            e for e in events
            if e.outcome in {OUTCOME_FAILED, OUTCOME_BLOCKED}
        ]

        if len(failed) < 3:
            return []

        severity = LEARNING_SIGNAL_HIGH if len(failed) < 8 else LEARNING_SIGNAL_CRITICAL

        return [
            FabricLearningPattern(
                pattern_id=f"FABRIC-PATTERN-{uuid.uuid4().hex[:12].upper()}",
                pattern_type="RECURRING_FAILURE_PATTERN",
                severity=severity,
                confidence=min(0.95, 0.4 + len(failed) * 0.05),
                message="Recurring runtime fabric failures or blocks detected.",
                tenant_id=tenant_id,
                event_count=len(failed),
                evidence=[e.to_dict() for e in failed[-10:]],
                metadata={"failed_count": len(failed)},
            )
        ]

    def _target_instability_patterns(
        self,
        *,
        tenant_id: str,
        events: List[FabricLearningEvent],
    ) -> List[FabricLearningPattern]:
        grouped: Dict[str, List[FabricLearningEvent]] = {}

        for event in events:
            if not event.target:
                continue

            grouped.setdefault(event.target, []).append(event)

        patterns = []

        for target, items in grouped.items():
            bad = [
                e for e in items
                if e.outcome in {OUTCOME_FAILED, OUTCOME_BLOCKED}
            ]

            if len(bad) >= 2:
                patterns.append(
                    FabricLearningPattern(
                        pattern_id=f"FABRIC-PATTERN-{uuid.uuid4().hex[:12].upper()}",
                        pattern_type="TARGET_INSTABILITY_PATTERN",
                        severity=LEARNING_SIGNAL_HIGH,
                        confidence=min(0.9, 0.45 + len(bad) * 0.1),
                        message=f"Target {target} shows repeated instability.",
                        tenant_id=tenant_id,
                        target=target,
                        event_count=len(bad),
                        evidence=[e.to_dict() for e in bad[-10:]],
                        metadata={
                            "target": target,
                            "bad_count": len(bad),
                            "total_count": len(items),
                        },
                    )
                )

        return patterns

    def _pressure_patterns(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[FabricLearningPattern]:
        patterns = []

        for key, label in [
            ("cluster_health", "CLUSTER_PRESSURE_PATTERN"),
            ("domain_health", "DOMAIN_PRESSURE_PATTERN"),
            ("routing_status", "ROUTING_PRESSURE_PATTERN"),
            ("relay_status", "RELAY_PRESSURE_PATTERN"),
        ]:
            data = telemetry.get(key, {}) or {}

            risk = data.get("risk")
            blocked = int(data.get("blocked", 0) or 0)
            failed = int(data.get("failed", 0) or 0)

            if risk in {"HIGH", "CRITICAL"} or blocked > 0 or failed > 0:
                severity = (
                    LEARNING_SIGNAL_CRITICAL
                    if risk == "CRITICAL"
                    else LEARNING_SIGNAL_HIGH
                )

                patterns.append(
                    FabricLearningPattern(
                        pattern_id=f"FABRIC-PATTERN-{uuid.uuid4().hex[:12].upper()}",
                        pattern_type=label,
                        severity=severity,
                        confidence=0.75,
                        message=f"{label} detected from runtime telemetry.",
                        tenant_id=tenant_id,
                        event_count=blocked + failed,
                        evidence=[data],
                        metadata=data,
                    )
                )

        return patterns

    # ========================================================
    # SCORING
    # ========================================================

    def _stability_score(
        self,
        *,
        patterns: List[FabricLearningPattern],
        telemetry: Dict[str, Any],
    ) -> float:
        score = 100.0

        penalties = {
            "RECURRING_FAILURE_PATTERN": 25.0,
            "TARGET_INSTABILITY_PATTERN": 20.0,
            "CLUSTER_PRESSURE_PATTERN": 18.0,
            "DOMAIN_PRESSURE_PATTERN": 20.0,
            "ROUTING_PRESSURE_PATTERN": 16.0,
            "RELAY_PRESSURE_PATTERN": 16.0,
        }

        severity_penalty = {
            LEARNING_SIGNAL_LOW: 0.0,
            LEARNING_SIGNAL_MEDIUM: 5.0,
            LEARNING_SIGNAL_HIGH: 10.0,
            LEARNING_SIGNAL_CRITICAL: 20.0,
        }

        for pattern in patterns:
            score -= penalties.get(pattern.pattern_type, 5.0)
            score -= severity_penalty.get(pattern.severity, 0.0)

        return round(max(0.0, min(score, 100.0)), 2)

    def _learning_state(
        self,
        *,
        stability_score: float,
        patterns: List[FabricLearningPattern],
    ) -> str:
        if stability_score >= 85:
            return PATTERN_STABLE
        if stability_score >= 65:
            return PATTERN_DEGRADING
        if stability_score >= 35:
            return PATTERN_UNSTABLE
        return PATTERN_RECURRING

    def _confidence(
        self,
        *,
        patterns: List[FabricLearningPattern],
        telemetry: Dict[str, Any],
    ) -> float:
        event_component = min(len(self._events) * 0.01, 0.45)
        pattern_component = min(len(patterns) * 0.08, 0.35)
        telemetry_component = min(
            len([k for k in telemetry.keys() if not k.endswith("_error")]) * 0.02,
            0.20,
        )

        return round(
            max(
                0.05,
                min(0.98, 0.25 + event_component + pattern_component + telemetry_component),
            ),
            3,
        )

    def _learned_signals(
        self,
        *,
        patterns: List[FabricLearningPattern],
        stability_score: float,
        confidence: float,
    ) -> List[Dict[str, Any]]:
        signals = []

        for pattern in patterns:
            signals.append(
                {
                    "signal_type": f"LEARNED_{pattern.pattern_type}",
                    "severity": pattern.severity,
                    "confidence": pattern.confidence,
                    "message": pattern.message,
                    "target": pattern.target,
                    "event_count": pattern.event_count,
                }
            )

        if stability_score < 65:
            signals.append(
                {
                    "signal_type": "LEARNED_RUNTIME_FABRIC_DEGRADATION",
                    "severity": LEARNING_SIGNAL_HIGH,
                    "confidence": confidence,
                    "message": "Learning engine detects degraded runtime fabric behavior.",
                }
            )

        return signals

    # ========================================================
    # TARGET SCORING
    # ========================================================

    def _update_target_score(
        self,
        event: FabricLearningEvent,
    ) -> None:
        if not event.target:
            return

        record = self._target_scores.setdefault(
            event.target,
            {
                "target": event.target,
                "events": 0,
                "success": 0,
                "failed": 0,
                "blocked": 0,
                "avg_score": 100.0,
                "trust_score": 100.0,
                "updated_at_ms": _now_ms(),
            },
        )

        record["events"] += 1

        if event.outcome == OUTCOME_SUCCESS:
            record["success"] += 1
        elif event.outcome == OUTCOME_BLOCKED:
            record["blocked"] += 1
        elif event.outcome == OUTCOME_FAILED:
            record["failed"] += 1

        prev = float(record.get("avg_score", 100.0))
        count = int(record.get("events", 1))

        record["avg_score"] = round(
            ((prev * max(count - 1, 0)) + float(event.score or 0.0)) / max(count, 1),
            2,
        )

        penalty = (
            record["failed"] * 12.0
            + record["blocked"] * 8.0
        )

        record["trust_score"] = round(
            max(0.0, min(100.0, record["avg_score"] - penalty)),
            2,
        )

        record["updated_at_ms"] = _now_ms()

    # ========================================================
    # READS
    # ========================================================

    def list_events(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._events,
            key=lambda e: e.created_at_ms,
            reverse=True,
        )

        return [
            r.to_dict()
            for r in rows[:limit]
        ]

    def list_patterns(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._patterns,
            key=lambda p: p.created_at_ms,
            reverse=True,
        )

        return [
            r.to_dict()
            for r in rows[:limit]
        ]

    def list_assessments(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._assessments,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )

        return [
            r.to_dict()
            for r in rows[:limit]
        ]

    def target_scores(
        self,
    ) -> List[Dict[str, Any]]:
        return sorted(
            self._target_scores.values(),
            key=lambda r: r.get("trust_score", 0.0),
        )

    def learning_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "tenant_id": tenant_id,
            "event_count": len(self._events),
            "pattern_count": len(self._patterns),
            "assessment_count": len(self._assessments),
            "target_count": len(self._target_scores),
            "latest_assessment": latest,
        }

    # ========================================================
    # EVENTS
    # ========================================================

    def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                source="runtime_fabric_learning_engine",
                severity=payload.get("learning_state") or payload.get("outcome") or "INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_RUNTIME_FABRIC_LEARNING_ENGINE: Optional[
    RuntimeFabricLearningEngine
] = None


def get_runtime_fabric_learning_engine(
    *,
    sovereignty_decision_engine: Any = None,
    adaptive_policy_engine: Any = None,
    mesh_optimizer: Any = None,
    cluster_balancer: Any = None,
    execution_relay: Any = None,
    federated_router: Any = None,
    cluster_manager: Any = None,
    domain_manager: Any = None,
    recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> RuntimeFabricLearningEngine:
    global _DEFAULT_RUNTIME_FABRIC_LEARNING_ENGINE

    if reset or _DEFAULT_RUNTIME_FABRIC_LEARNING_ENGINE is None:
        _DEFAULT_RUNTIME_FABRIC_LEARNING_ENGINE = RuntimeFabricLearningEngine(
            sovereignty_decision_engine=sovereignty_decision_engine,
            adaptive_policy_engine=adaptive_policy_engine,
            mesh_optimizer=mesh_optimizer,
            cluster_balancer=cluster_balancer,
            execution_relay=execution_relay,
            federated_router=federated_router,
            cluster_manager=cluster_manager,
            domain_manager=domain_manager,
            recovery_manager=recovery_manager,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_RUNTIME_FABRIC_LEARNING_ENGINE