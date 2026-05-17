"""
core/runtime/autonomy_governor_v2.py

Autonomy Governor V2.

Purpose:
- adaptive sovereign governance intelligence
- risk-aware autonomy modulation
- runtime fabric governance scoring
- sovereign risk modeling
- adaptive throttling / freeze recommendations
- governance policy recommendations

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned state only
- explicit injected dependencies
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"

GOVERNANCE_LOW = "LOW"
GOVERNANCE_MEDIUM = "MEDIUM"
GOVERNANCE_HIGH = "HIGH"
GOVERNANCE_CRITICAL = "CRITICAL"

ACTION_NONE = "NONE"
ACTION_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
ACTION_PAUSE_AUTONOMY = "PAUSE_AUTONOMY"
ACTION_TRIGGER_BACKPRESSURE = "TRIGGER_BACKPRESSURE"
ACTION_TRIGGER_RECOVERY = "TRIGGER_RECOVERY"
ACTION_REQUIRE_APPROVALS = "REQUIRE_APPROVALS"
ACTION_FREEZE_SOVEREIGN_DOMAIN = "FREEZE_SOVEREIGN_DOMAIN"
ACTION_QUARANTINE_CLUSTER = "QUARANTINE_CLUSTER"
ACTION_LOCKDOWN = "LOCKDOWN"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class AutonomyGovernanceAssessment:
    assessment_id: str
    tenant_id: str
    autonomy_mode: str
    recommended_mode: str
    risk_level: str
    risk_score: float
    allowed: bool
    reason: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AutonomyGovernanceAction:
    action_id: str
    action_type: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    reason: str = ""
    status: str = "PENDING"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    completed_at_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomyGovernorV2:
    def __init__(
        self,
        *,
        registry: Any = None,
        policy_manager: Any = None,
        health_manager: Any = None,
        supervisor: Any = None,
        recovery_manager: Any = None,
        backpressure_controller: Any = None,
        federation_manager: Any = None,
        cluster_manager: Any = None,
        domain_manager: Any = None,
        sovereign_controller: Any = None,
        federated_router: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        default_mode: str = AUTONOMY_SUPERVISED,
    ) -> None:
        self.storage = storage
        self.registry = registry or getattr(storage, "runtime_service_registry", None)
        self.policy_manager = policy_manager or getattr(storage, "runtime_policy_manager", None)
        self.health_manager = health_manager or getattr(storage, "runtime_health_manager", None)
        self.supervisor = supervisor or getattr(storage, "autonomous_runtime_supervisor", None)
        self.recovery_manager = recovery_manager or getattr(storage, "runtime_recovery_manager", None)
        self.backpressure_controller = (
            backpressure_controller
            or getattr(storage, "backpressure_controller", None)
        )
        self.federation_manager = federation_manager or getattr(storage, "runtime_federation_manager", None)
        self.cluster_manager = cluster_manager or getattr(storage, "distributed_runtime_cluster_manager", None)
        self.domain_manager = domain_manager or getattr(storage, "execution_domain_manager", None)
        self.sovereign_controller = sovereign_controller or getattr(storage, "sovereign_execution_controller", None)
        self.federated_router = federated_router or getattr(storage, "federated_execution_router", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.default_mode = default_mode
        self._tenant_modes: Dict[str, str] = {DEFAULT_TENANT: default_mode}
        self._assessments: List[AutonomyGovernanceAssessment] = []
        self._actions: List[AutonomyGovernanceAction] = []

    # ========================================================
    # MODE MANAGEMENT
    # ========================================================

    def set_autonomy_mode(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        mode: str,
        reason: str = "manual_update",
    ) -> Dict[str, Any]:
        self._tenant_modes[tenant_id] = mode

        self._emit(
            "AUTONOMY_GOVERNOR_MODE_CHANGED",
            {
                "tenant_id": tenant_id,
                "mode": mode,
                "reason": reason,
            },
        )

        return {
            "ok": True,
            "tenant_id": tenant_id,
            "mode": mode,
            "reason": reason,
        }

    def get_autonomy_mode(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> str:
        return self._tenant_modes.get(
            tenant_id,
            self.default_mode,
        )

    # ========================================================
    # MAIN ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        requested_mode: Optional[str] = None,
        workload: Optional[Dict[str, Any]] = None,
    ) -> AutonomyGovernanceAssessment:
        workload = workload or {}

        current_mode = requested_mode or self.get_autonomy_mode(
            tenant_id=tenant_id
        )

        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            workload=workload,
        )

        findings = self._derive_findings(
            telemetry=telemetry,
            workload=workload,
        )

        risk_score = self._score_risk(
            findings=findings,
            telemetry=telemetry,
            workload=workload,
        )

        risk_level = self._risk_level(risk_score)

        recommended_mode = self._recommended_mode(
            current_mode=current_mode,
            risk_level=risk_level,
            risk_score=risk_score,
            findings=findings,
        )

        actions = self._recommended_actions(
            tenant_id=tenant_id,
            risk_level=risk_level,
            risk_score=risk_score,
            findings=findings,
            telemetry=telemetry,
        )

        allowed = recommended_mode not in {
            AUTONOMY_LOCKDOWN,
        }

        reason = (
            "Autonomy operating within acceptable sovereign governance bounds."
            if risk_level in {GOVERNANCE_LOW, GOVERNANCE_MEDIUM}
            else "Autonomy reduction recommended due to elevated sovereign/runtime risk."
        )

        assessment = AutonomyGovernanceAssessment(
            assessment_id=f"AUTO-GOV-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            autonomy_mode=current_mode,
            recommended_mode=recommended_mode,
            risk_level=risk_level,
            risk_score=risk_score,
            allowed=allowed,
            reason=reason,
            findings=findings,
            recommended_actions=actions,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._emit(
            "AUTONOMY_GOVERNANCE_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # ENFORCEMENT
    # ========================================================

    def enforce(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        assessment = self.assess(
            tenant_id=tenant_id,
            workload=workload or {},
        )

        executed: List[Dict[str, Any]] = []

        for rec in assessment.recommended_actions:
            action = AutonomyGovernanceAction(
                action_id=f"AUTO-ACTION-{uuid.uuid4().hex[:12].upper()}",
                action_type=rec.get("action", ACTION_NONE),
                tenant_id=tenant_id,
                target=rec.get("target"),
                reason=rec.get("reason", ""),
                metadata=rec,
            )

            if dry_run:
                action.status = "DRY_RUN"
            else:
                action.status = "RUNNING"
                self._execute_action(action)
                action.completed_at_ms = _now_ms()

            self._actions.append(action)
            self._actions = self._actions[-500:]
            executed.append(action.to_dict())

        if not dry_run and assessment.recommended_mode != assessment.autonomy_mode:
            self.set_autonomy_mode(
                tenant_id=tenant_id,
                mode=assessment.recommended_mode,
                reason="autonomy_governor_v2_enforcement",
            )

        result = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "actions": executed,
        }

        self._emit(
            "AUTONOMY_GOVERNANCE_ENFORCED",
            result,
        )

        return result

    def _execute_action(
        self,
        action: AutonomyGovernanceAction,
    ) -> None:
        try:
            if action.action_type == ACTION_TRIGGER_BACKPRESSURE:
                self._trigger_backpressure(action)

            elif action.action_type == ACTION_TRIGGER_RECOVERY:
                self._trigger_recovery(action)

            elif action.action_type == ACTION_FREEZE_SOVEREIGN_DOMAIN:
                self._freeze_domain(action)

            elif action.action_type == ACTION_QUARANTINE_CLUSTER:
                self._quarantine_cluster(action)

            elif action.action_type in {
                ACTION_REDUCE_AUTONOMY,
                ACTION_PAUSE_AUTONOMY,
                ACTION_REQUIRE_APPROVALS,
                ACTION_LOCKDOWN,
            }:
                action.status = "COMPLETED"

            else:
                action.status = "SKIPPED"

        except Exception as exc:
            action.status = "FAILED"
            action.metadata["error"] = str(exc)

    # ========================================================
    # TELEMETRY
    # ========================================================

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "workload": workload,
            "collected_at_ms": _now_ms(),
        }

        try:
            if self.health_manager is not None:
                snapshot = self.health_manager.evaluate()
                telemetry["runtime_health"] = (
                    snapshot.to_dict()
                    if hasattr(snapshot, "to_dict")
                    else {}
                )
        except Exception as exc:
            telemetry["runtime_health_error"] = str(exc)

        try:
            if self.policy_manager is not None:
                telemetry["policy_status"] = self.policy_manager.policy_status()
        except Exception as exc:
            telemetry["policy_error"] = str(exc)

        try:
            if self.supervisor is not None:
                telemetry["supervisor_status"] = self.supervisor.status_snapshot()
        except Exception as exc:
            telemetry["supervisor_error"] = str(exc)

        try:
            if self.federation_manager is not None:
                telemetry["federation_health"] = self.federation_manager.federation_health()
        except Exception as exc:
            telemetry["federation_error"] = str(exc)

        try:
            if self.cluster_manager is not None:
                telemetry["cluster_health"] = self.cluster_manager.cluster_health()
        except Exception as exc:
            telemetry["cluster_error"] = str(exc)

        try:
            if self.domain_manager is not None:
                telemetry["domain_health"] = self.domain_manager.domain_health()
        except Exception as exc:
            telemetry["domain_error"] = str(exc)

        try:
            if self.sovereign_controller is not None:
                telemetry["sovereignty_status"] = self.sovereign_controller.sovereignty_status()
        except Exception as exc:
            telemetry["sovereignty_error"] = str(exc)

        try:
            if self.federated_router is not None:
                telemetry["routing_status"] = self.federated_router.routing_status()
        except Exception as exc:
            telemetry["routing_error"] = str(exc)

        return telemetry

    # ========================================================
    # FINDINGS / RISK
    # ========================================================

    def _derive_findings(
        self,
        *,
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []

        runtime_health = telemetry.get("runtime_health", {})
        if runtime_health:
            risk = runtime_health.get("risk")
            score = float(runtime_health.get("score", 100.0) or 100.0)

            if risk in {"HIGH", "CRITICAL"} or score < 65:
                findings.append({
                    "type": "RUNTIME_HEALTH_RISK",
                    "severity": risk or "HIGH",
                    "score": score,
                    "details": runtime_health,
                })

        policy_status = telemetry.get("policy_status", {})
        if policy_status:
            violations = int(policy_status.get("violation_count", 0) or 0)
            if violations > 0:
                findings.append({
                    "type": "POLICY_VIOLATIONS",
                    "severity": "HIGH",
                    "violations": violations,
                })

        federation_health = telemetry.get("federation_health", {})
        if federation_health:
            risk = federation_health.get("risk")
            if risk in {"HIGH", "CRITICAL"}:
                findings.append({
                    "type": "FEDERATION_RISK",
                    "severity": risk,
                    "details": federation_health,
                })

        cluster_health = telemetry.get("cluster_health", {})
        if cluster_health:
            risk = cluster_health.get("risk")
            if risk in {"HIGH", "CRITICAL"}:
                findings.append({
                    "type": "CLUSTER_RISK",
                    "severity": risk,
                    "details": cluster_health,
                })

        domain_health = telemetry.get("domain_health", {})
        if domain_health:
            risk = domain_health.get("risk")
            if risk in {"HIGH", "CRITICAL"}:
                findings.append({
                    "type": "DOMAIN_RISK",
                    "severity": risk,
                    "details": domain_health,
                })

        sovereignty = telemetry.get("sovereignty_status", {})
        if sovereignty:
            blocked = int(sovereignty.get("blocked", 0) or 0)
            approvals = int(sovereignty.get("requires_approval", 0) or 0)

            if blocked > 0:
                findings.append({
                    "type": "SOVEREIGN_BLOCKS",
                    "severity": "HIGH",
                    "blocked": blocked,
                })

            if approvals > 5:
                findings.append({
                    "type": "SOVEREIGN_APPROVAL_PRESSURE",
                    "severity": "MEDIUM",
                    "requires_approval": approvals,
                })

        routing = telemetry.get("routing_status", {})
        if routing:
            blocked = int(routing.get("blocked", 0) or 0)

            if blocked > 0:
                findings.append({
                    "type": "ROUTING_BLOCKS",
                    "severity": "HIGH",
                    "blocked": blocked,
                })

        categories = {
            str(c).upper()
            for c in workload.get("categories", [])
        }

        if categories.intersection({"CLASSIFIED", "EXPORT_CONTROLLED", "EXPORT_CONTROL", "ITAR"}):
            findings.append({
                "type": "HIGH_SENSITIVITY_WORKLOAD",
                "severity": "HIGH",
                "categories": sorted(categories),
            })

        return findings

    def _score_risk(
        self,
        *,
        findings: List[Dict[str, Any]],
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> float:
        score = 0.0

        weights = {
            "RUNTIME_HEALTH_RISK": 25.0,
            "POLICY_VIOLATIONS": 20.0,
            "FEDERATION_RISK": 20.0,
            "CLUSTER_RISK": 20.0,
            "DOMAIN_RISK": 25.0,
            "SOVEREIGN_BLOCKS": 25.0,
            "SOVEREIGN_APPROVAL_PRESSURE": 10.0,
            "ROUTING_BLOCKS": 20.0,
            "HIGH_SENSITIVITY_WORKLOAD": 15.0,
        }

        severity_boost = {
            "LOW": 0.0,
            "MEDIUM": 5.0,
            "HIGH": 10.0,
            "CRITICAL": 20.0,
        }

        for finding in findings:
            ftype = finding.get("type")
            severity = str(finding.get("severity", "LOW")).upper()

            score += weights.get(ftype, 5.0)
            score += severity_boost.get(severity, 0.0)

        runtime_health = telemetry.get("runtime_health", {})
        if runtime_health:
            health_score = float(runtime_health.get("score", 100.0) or 100.0)
            score += max(0.0, 100.0 - health_score) * 0.25

        return max(0.0, min(score, 100.0))

    def _risk_level(self, score: float) -> str:
        if score >= 80:
            return GOVERNANCE_CRITICAL
        if score >= 55:
            return GOVERNANCE_HIGH
        if score >= 25:
            return GOVERNANCE_MEDIUM
        return GOVERNANCE_LOW

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def _recommended_mode(
        self,
        *,
        current_mode: str,
        risk_level: str,
        risk_score: float,
        findings: List[Dict[str, Any]],
    ) -> str:
        finding_types = {f.get("type") for f in findings}

        if risk_level == GOVERNANCE_CRITICAL:
            return AUTONOMY_LOCKDOWN

        if risk_level == GOVERNANCE_HIGH:
            if "HIGH_SENSITIVITY_WORKLOAD" in finding_types:
                return AUTONOMY_MANUAL
            return AUTONOMY_ASSISTED

        if risk_level == GOVERNANCE_MEDIUM:
            if current_mode == AUTONOMY_FULL:
                return AUTONOMY_SUPERVISED
            return current_mode

        return current_mode

    def _recommended_actions(
        self,
        *,
        tenant_id: str,
        risk_level: str,
        risk_score: float,
        findings: List[Dict[str, Any]],
        telemetry: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []

        finding_types = {f.get("type") for f in findings}

        if risk_level == GOVERNANCE_CRITICAL:
            actions.append({
                "action": ACTION_LOCKDOWN,
                "reason": "Critical governance risk detected.",
            })
            actions.append({
                "action": ACTION_PAUSE_AUTONOMY,
                "reason": "Pause autonomy under critical governance risk.",
            })

        if finding_types.intersection({
            "RUNTIME_HEALTH_RISK",
            "FEDERATION_RISK",
            "CLUSTER_RISK",
        }):
            actions.append({
                "action": ACTION_TRIGGER_BACKPRESSURE,
                "reason": "Runtime/fabric instability detected.",
            })
            actions.append({
                "action": ACTION_TRIGGER_RECOVERY,
                "reason": "Runtime/fabric recovery recommended.",
            })

        if finding_types.intersection({
            "SOVEREIGN_BLOCKS",
            "DOMAIN_RISK",
            "HIGH_SENSITIVITY_WORKLOAD",
        }):
            actions.append({
                "action": ACTION_REQUIRE_APPROVALS,
                "reason": "Sovereign or high-sensitivity workload pressure detected.",
            })

        if "DOMAIN_RISK" in finding_types:
            actions.append({
                "action": ACTION_FREEZE_SOVEREIGN_DOMAIN,
                "reason": "Domain risk detected; freeze may be required.",
            })

        if "CLUSTER_RISK" in finding_types:
            actions.append({
                "action": ACTION_QUARANTINE_CLUSTER,
                "reason": "Cluster risk detected; quarantine may be required.",
            })

        if risk_level == GOVERNANCE_HIGH:
            actions.append({
                "action": ACTION_REDUCE_AUTONOMY,
                "reason": "High governance risk; reduce autonomy.",
            })

        return actions

    # ========================================================
    # ACTION EXECUTION
    # ========================================================

    def _trigger_backpressure(self, action: AutonomyGovernanceAction) -> None:
        if self.backpressure_controller is None:
            action.status = "SKIPPED"
            action.metadata["reason"] = "backpressure_controller_unavailable"
            return

        decision = self.backpressure_controller.evaluate(
            tenant_id=action.tenant_id,
            context={
                "source": "autonomy_governor_v2",
                "reason": action.reason,
            },
        )

        if getattr(decision, "freeze_tenant", False):
            self.backpressure_controller.enforce_freeze_if_needed(decision)

        action.status = "COMPLETED"
        action.metadata["backpressure_decision"] = (
            decision.to_dict()
            if hasattr(decision, "to_dict")
            else {}
        )

    def _trigger_recovery(self, action: AutonomyGovernanceAction) -> None:
        if self.recovery_manager is None:
            action.status = "SKIPPED"
            action.metadata["reason"] = "recovery_manager_unavailable"
            return

        result = self.recovery_manager.auto_recover(
            tenant_id=action.tenant_id,
            actor="autonomy_governor_v2",
            force=False,
        )

        action.status = "COMPLETED" if result.ok else "FAILED"
        action.metadata["recovery_result"] = (
            result.to_dict()
            if hasattr(result, "to_dict")
            else {}
        )

    def _freeze_domain(self, action: AutonomyGovernanceAction) -> None:
        if self.domain_manager is None:
            action.status = "SKIPPED"
            action.metadata["reason"] = "domain_manager_unavailable"
            return

        target = action.target

        if not target:
            domains = self.domain_manager.list_domains()
            risky = [
                d for d in domains
                if d.get("status") in {"DEGRADED", "QUARANTINED"}
            ]
            target = risky[0].get("domain_id") if risky else None

        if not target:
            action.status = "SKIPPED"
            action.metadata["reason"] = "no_domain_target"
            return

        ok = self.domain_manager.freeze_domain(
            target,
            reason=action.reason,
        )

        action.status = "COMPLETED" if ok else "FAILED"
        action.target = target

    def _quarantine_cluster(self, action: AutonomyGovernanceAction) -> None:
        if self.cluster_manager is None:
            action.status = "SKIPPED"
            action.metadata["reason"] = "cluster_manager_unavailable"
            return

        target = action.target

        if not target:
            clusters = self.cluster_manager.list_clusters()
            risky = [
                c for c in clusters
                if c.get("status") in {"DEGRADED", "OFFLINE"}
                or c.get("risk_level") in {"HIGH", "CRITICAL"}
            ]
            target = risky[0].get("cluster_id") if risky else None

        if not target:
            action.status = "SKIPPED"
            action.metadata["reason"] = "no_cluster_target"
            return

        ok = self.cluster_manager.quarantine_cluster(
            target,
            reason=action.reason,
        )

        action.status = "COMPLETED" if ok else "FAILED"
        action.target = target

    # ========================================================
    # READS
    # ========================================================

    def list_assessments(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        assessments = sorted(
            self._assessments,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )

        return [
            a.to_dict()
            for a in assessments[:limit]
        ]

    def list_actions(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        actions = sorted(
            self._actions,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )

        return [
            a.to_dict()
            for a in actions[:limit]
        ]

    def governor_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "default_mode": self.default_mode,
            "tenant_mode": self.get_autonomy_mode(tenant_id=tenant_id),
            "assessment_count": len(self._assessments),
            "action_count": len(self._actions),
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
                source="autonomy_governor_v2",
                severity=payload.get("risk_level") or "INFO",
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


_DEFAULT_AUTONOMY_GOVERNOR_V2: Optional[
    AutonomyGovernorV2
] = None


def get_autonomy_governor_v2(
    *,
    registry: Any = None,
    policy_manager: Any = None,
    health_manager: Any = None,
    supervisor: Any = None,
    recovery_manager: Any = None,
    backpressure_controller: Any = None,
    federation_manager: Any = None,
    cluster_manager: Any = None,
    domain_manager: Any = None,
    sovereign_controller: Any = None,
    federated_router: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    default_mode: str = AUTONOMY_SUPERVISED,
    reset: bool = False,
) -> AutonomyGovernorV2:
    global _DEFAULT_AUTONOMY_GOVERNOR_V2

    if reset or _DEFAULT_AUTONOMY_GOVERNOR_V2 is None:
        _DEFAULT_AUTONOMY_GOVERNOR_V2 = AutonomyGovernorV2(
            registry=registry,
            policy_manager=policy_manager,
            health_manager=health_manager,
            supervisor=supervisor,
            recovery_manager=recovery_manager,
            backpressure_controller=backpressure_controller,
            federation_manager=federation_manager,
            cluster_manager=cluster_manager,
            domain_manager=domain_manager,
            sovereign_controller=sovereign_controller,
            federated_router=federated_router,
            storage=storage,
            event_bus=event_bus,
            default_mode=default_mode,
        )

    return _DEFAULT_AUTONOMY_GOVERNOR_V2