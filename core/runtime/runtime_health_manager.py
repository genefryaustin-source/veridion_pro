"""
core/runtime/runtime_health_manager.py

Runtime Health Manager.

Purpose:
- aggregate runtime health
- score service stability
- correlate failures
- detect systemic degradation
- recommend recovery actions
- feed Command Center / operations map
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


HEALTH_HEALTHY = "HEALTHY"
HEALTH_DEGRADED = "DEGRADED"
HEALTH_UNSTABLE = "UNSTABLE"
HEALTH_CRITICAL = "CRITICAL"
HEALTH_UNKNOWN = "UNKNOWN"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeHealthSignal:
    signal_id: str
    service_name: str
    signal_type: str
    severity: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeHealthSnapshot:
    snapshot_id: str
    health: str
    risk: str
    score: float
    service_scores: Dict[str, float] = field(default_factory=dict)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuntimeHealthManager:
    def __init__(
        self,
        *,
        registry: Any,
        lifecycle: Any = None,
        policy_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.registry = registry
        self.lifecycle = lifecycle
        self.policy_manager = policy_manager
        self.storage = storage
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._signals: List[RuntimeHealthSignal] = []
        self._snapshots: List[RuntimeHealthSnapshot] = []

    # ========================================================
    # SIGNALS
    # ========================================================

    def record_signal(
        self,
        *,
        service_name: str,
        signal_type: str,
        severity: str,
        message: str,
        tenant_id: str = DEFAULT_TENANT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeHealthSignal:
        signal = RuntimeHealthSignal(
            signal_id=f"RHS-{uuid.uuid4().hex[:12].upper()}",
            service_name=service_name,
            signal_type=signal_type,
            severity=severity,
            message=message,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )

        self._signals.append(signal)

        self._emit(
            "RUNTIME_HEALTH_SIGNAL",
            signal.to_dict(),
        )

        return signal

    # ========================================================
    # HEALTH EVALUATION
    # ========================================================

    def evaluate(self) -> RuntimeHealthSnapshot:
        service_scores: Dict[str, float] = {}
        findings: List[Dict[str, Any]] = []
        recommendations: List[Dict[str, Any]] = []

        services = self._safe_list_services()

        for record in services:
            service_name = getattr(record, "service_name", None) or "unknown"
            score = float(getattr(record, "health_score", 100.0) or 100.0)

            status = str(getattr(record, "status", "UNKNOWN") or "UNKNOWN").upper()
            error_count = int(getattr(record, "error_count", 0) or 0)
            warning_count = int(getattr(record, "warning_count", 0) or 0)

            if status in {"DEGRADED"}:
                score -= 15
                findings.append({
                    "type": "SERVICE_DEGRADED",
                    "service": service_name,
                    "status": status,
                })

            if status in {"UNAVAILABLE", "FAILED", "STOPPED"}:
                score -= 35
                findings.append({
                    "type": "SERVICE_UNAVAILABLE",
                    "service": service_name,
                    "status": status,
                })

            if status in {"QUARANTINED"}:
                score -= 50
                findings.append({
                    "type": "SERVICE_QUARANTINED",
                    "service": service_name,
                    "status": status,
                })

            if error_count > 0:
                score -= min(error_count * 5, 40)
                findings.append({
                    "type": "SERVICE_ERRORS",
                    "service": service_name,
                    "error_count": error_count,
                })

            if warning_count > 0:
                score -= min(warning_count * 1, 15)

            service_scores[service_name] = max(0.0, min(score, 100.0))

        # Queue health
        queue = getattr(self.storage, "execution_queue", None)
        if queue is not None and hasattr(queue, "stats"):
            try:
                stats = queue.stats()
                pending = int(stats.get("pending", 0) or 0)
                retry = int(stats.get("retry", 0) or 0)
                dead = int(stats.get("dead_letter", 0) or 0)

                if pending > 1000:
                    findings.append({
                        "type": "QUEUE_DEPTH_HIGH",
                        "pending": pending,
                    })
                    recommendations.append({
                        "action": "ENABLE_BACKPRESSURE",
                        "reason": "Queue pending depth is high.",
                    })

                if retry > 100:
                    findings.append({
                        "type": "RETRY_STORM",
                        "retry": retry,
                    })
                    recommendations.append({
                        "action": "THROTTLE_ROUTING",
                        "reason": "Retry storm detected.",
                    })

                if dead > 25:
                    findings.append({
                        "type": "DEAD_LETTER_SPIKE",
                        "dead_letter": dead,
                    })
                    recommendations.append({
                        "action": "REVIEW_DEAD_LETTERS",
                        "reason": "Dead-letter spike detected.",
                    })

            except Exception as exc:
                findings.append({
                    "type": "QUEUE_HEALTH_ERROR",
                    "error": str(exc),
                })

        # Worker health
        orchestrator = getattr(self.storage, "worker_orchestrator", None)
        if orchestrator is not None and hasattr(orchestrator, "worker_stats"):
            try:
                stats = orchestrator.worker_stats()
                total = int(stats.get("total_workers", 0) or 0)
                degraded = int(stats.get("degraded", 0) or 0)
                offline = int(stats.get("offline", 0) or 0)
                quarantined = int(stats.get("quarantined", 0) or 0)

                if total > 0:
                    unavailable_ratio = (degraded + offline + quarantined) / max(total, 1)

                    if unavailable_ratio >= 0.25:
                        findings.append({
                            "type": "WORKER_POOL_DEGRADED",
                            "unavailable_ratio": unavailable_ratio,
                            "degraded": degraded,
                            "offline": offline,
                            "quarantined": quarantined,
                        })
                        recommendations.append({
                            "action": "CHECK_WORKER_POOL",
                            "reason": "Worker pool degradation detected.",
                        })

                    if unavailable_ratio >= 0.50:
                        recommendations.append({
                            "action": "PAUSE_AUTONOMY",
                            "reason": "Worker pool is critically degraded.",
                        })

            except Exception as exc:
                findings.append({
                    "type": "WORKER_HEALTH_ERROR",
                    "error": str(exc),
                })

        # Policy health
        if self.policy_manager is not None and hasattr(self.policy_manager, "policy_status"):
            try:
                ps = self.policy_manager.policy_status()
                violations = int(ps.get("violation_count", 0) or 0)
                warnings = int(ps.get("warning_count", 0) or 0)

                if violations > 0:
                    findings.append({
                        "type": "RUNTIME_POLICY_VIOLATIONS",
                        "violations": violations,
                        "warnings": warnings,
                    })
                    recommendations.append({
                        "action": "AUDIT_RUNTIME_POLICY",
                        "reason": "Runtime policy violations detected.",
                    })

            except Exception as exc:
                findings.append({
                    "type": "POLICY_HEALTH_ERROR",
                    "error": str(exc),
                })

        # Overall score
        if service_scores:
            base_score = sum(service_scores.values()) / len(service_scores)
        else:
            base_score = 100.0

        penalty = 0.0
        for finding in findings:
            ftype = finding.get("type")
            if ftype in {"SERVICE_QUARANTINED", "WORKER_POOL_DEGRADED"}:
                penalty += 15
            elif ftype in {"RETRY_STORM", "DEAD_LETTER_SPIKE", "RUNTIME_POLICY_VIOLATIONS"}:
                penalty += 10
            elif ftype.endswith("_ERROR"):
                penalty += 8
            else:
                penalty += 3

        score = max(0.0, min(100.0, base_score - penalty))

        health = self._health_from_score(score)
        risk = self._risk_from_score(score)

        snapshot = RuntimeHealthSnapshot(
            snapshot_id=f"RHSNAP-{uuid.uuid4().hex[:12].upper()}",
            health=health,
            risk=risk,
            score=score,
            service_scores=service_scores,
            findings=findings,
            recommendations=recommendations,
        )

        self._snapshots.append(snapshot)

        self._emit(
            "RUNTIME_HEALTH_EVALUATED",
            snapshot.to_dict(),
        )

        return snapshot

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def recommended_actions(self) -> List[Dict[str, Any]]:
        snapshot = self.evaluate()
        return snapshot.recommendations

    def should_pause_autonomy(self) -> bool:
        snapshot = self.evaluate()
        return snapshot.risk in {RISK_HIGH, RISK_CRITICAL}

    def should_run_recovery(self) -> bool:
        snapshot = self.evaluate()
        return snapshot.health in {HEALTH_UNSTABLE, HEALTH_CRITICAL}

    # ========================================================
    # READS
    # ========================================================

    def list_signals(
        self,
        *,
        service_name: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        signals = list(self._signals)

        if service_name:
            signals = [
                s for s in signals
                if s.service_name == service_name
            ]

        if severity:
            signals = [
                s for s in signals
                if s.severity == severity
            ]

        signals = sorted(
            signals,
            key=lambda s: s.created_at_ms,
            reverse=True,
        )

        return [
            s.to_dict()
            for s in signals[:limit]
        ]

    def latest_snapshot(self) -> Optional[Dict[str, Any]]:
        if not self._snapshots:
            return None

        return self._snapshots[-1].to_dict()

    def list_snapshots(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        snapshots = sorted(
            self._snapshots,
            key=lambda s: s.created_at_ms,
            reverse=True,
        )

        return [
            s.to_dict()
            for s in snapshots[:limit]
        ]

    # ========================================================
    # INTERNAL
    # ========================================================

    def _safe_list_services(self) -> List[Any]:
        if self.registry is None:
            return []

        try:
            return self.registry.list_services()
        except Exception:
            return []

    def _health_from_score(self, score: float) -> str:
        if score >= 85:
            return HEALTH_HEALTHY
        if score >= 65:
            return HEALTH_DEGRADED
        if score >= 35:
            return HEALTH_UNSTABLE
        return HEALTH_CRITICAL

    def _risk_from_score(self, score: float) -> str:
        if score >= 85:
            return RISK_LOW
        if score >= 65:
            return RISK_MEDIUM
        if score >= 35:
            return RISK_HIGH
        return RISK_CRITICAL

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
                source="runtime_health_manager",
                severity=payload.get("risk") or payload.get("severity") or "INFO",
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


_DEFAULT_RUNTIME_HEALTH_MANAGER: Optional[
    RuntimeHealthManager
] = None


def get_runtime_health_manager(
    *,
    registry: Any,
    lifecycle: Any = None,
    policy_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> RuntimeHealthManager:
    global _DEFAULT_RUNTIME_HEALTH_MANAGER

    if reset or _DEFAULT_RUNTIME_HEALTH_MANAGER is None:
        _DEFAULT_RUNTIME_HEALTH_MANAGER = RuntimeHealthManager(
            registry=registry,
            lifecycle=lifecycle,
            policy_manager=policy_manager,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_RUNTIME_HEALTH_MANAGER