"""
core/governance/governance_execution_guardrails.py

Governance Execution Guardrails

Final authoritative governance safety boundary before execution.

This module evaluates:
- governance posture
- blast radius
- autonomy mode
- tenant sovereignty policy
- continuity posture
- rollback readiness
- verification posture
- resilience posture
- connector posture
- execution freeze states

before execution is allowed to proceed.

IMPORTANT:
This module DOES NOT:
- execute connectors
- mutate external systems
- perform connector failover
- route execution directly

It ONLY:
- evaluates execution safety posture
- enforces governance constraints
- emits replayable governance lineage
- generates deterministic guardrail decisions
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

DEFAULT_GUARDRAILS_NAME = "governance_execution_guardrails"

GUARDRAIL_ALLOWED = "ALLOWED"
GUARDRAIL_BLOCKED = "BLOCKED"
GUARDRAIL_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
GUARDRAIL_REQUIRES_GOVERNANCE = "REQUIRES_GOVERNANCE"
GUARDRAIL_REQUIRES_LEGAL_REVIEW = "REQUIRES_LEGAL_REVIEW"
GUARDRAIL_REQUIRES_CONTINUITY_REVIEW = "REQUIRES_CONTINUITY_REVIEW"
GUARDRAIL_REQUIRES_VERIFICATION = "REQUIRES_VERIFICATION"
GUARDRAIL_REQUIRES_ROLLBACK = "REQUIRES_ROLLBACK"
GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE = (
    "REQUIRES_AUTONOMY_DOWNGRADE"
)
GUARDRAIL_FROZEN = "FROZEN"
GUARDRAIL_LOCKDOWN = "LOCKDOWN"

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
AUTONOMY_FULL_AUTONOMY = "FULL_AUTONOMY"
AUTONOMY_LOCKDOWN = "LOCKDOWN"

BLAST_RADIUS_LOW = "LOW"
BLAST_RADIUS_MEDIUM = "MEDIUM"
BLAST_RADIUS_HIGH = "HIGH"
BLAST_RADIUS_CRITICAL = "CRITICAL"

FREEZE_NONE = "NONE"
FREEZE_TENANT = "TENANT"
FREEZE_GLOBAL = "GLOBAL"
FREEZE_CONNECTOR = "CONNECTOR"
FREEZE_ROLLBACK_ONLY = "ROLLBACK_ONLY"


# ============================================================
# ENUMS
# ============================================================

class GuardrailActionType(str, Enum):
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    ENRICH = "ENRICH"
    ESCALATE = "ESCALATE"
    NOTIFY = "NOTIFY"
    CONTAIN = "CONTAIN"
    ISOLATE_ENDPOINT = "ISOLATE_ENDPOINT"
    REVOKE_SESSION = "REVOKE_SESSION"
    DISABLE_USER = "DISABLE_USER"
    QUARANTINE_EMAIL = "QUARANTINE_EMAIL"
    DELETE_EMAIL = "DELETE_EMAIL"
    PURGE_MAILBOX = "PURGE_MAILBOX"
    BLOCK_NETWORK_TRAFFIC = "BLOCK_NETWORK_TRAFFIC"
    UPDATE_POLICY = "UPDATE_POLICY"
    ROLLBACK = "ROLLBACK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class GovernanceGuardrailRequest:
    """
    Governance evaluation request.
    """

    guardrail_request_id: str
    source_engine: str
    action_type: str
    severity: str
    confidence: float

    blast_radius: str
    autonomy_mode: str
    tenant_policy: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    execution_package_id: Optional[str] = None
    connector_result_id: Optional[str] = None
    failover_plan_id: Optional[str] = None

    governance_approved: bool = False
    human_approved: bool = False
    legal_approved: bool = False

    rollback_available: bool = False
    verification_available: bool = False
    continuity_review_completed: bool = False

    resilience_degraded: bool = False
    connector_degraded: bool = False
    governance_stale: bool = False

    freeze_mode: str = FREEZE_NONE

    lineage_event_ids: List[str] = field(default_factory=list)
    evidence_event_ids: List[str] = field(default_factory=list)
    control_ids: List[str] = field(default_factory=list)

    payload: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class GovernanceGuardrailDecision:
    """
    Deterministic governance decision.
    """

    guardrail_decision_id: str
    guardrail_request_id: str
    status: str

    action_type: str
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    execution_package_id: Optional[str]
    connector_result_id: Optional[str]
    failover_plan_id: Optional[str]

    blast_radius: str
    current_autonomy_mode: str
    recommended_autonomy_mode: str

    governance_required: bool
    human_approval_required: bool
    legal_review_required: bool
    continuity_review_required: bool
    rollback_required: bool
    verification_required: bool

    execution_allowed: bool
    freeze_mode: str

    constraints: List[str]
    recommended_next_steps: List[Dict[str, Any]]
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass(frozen=True)
class GovernanceExecutionGuardrailsSnapshot:
    guardrails_name: str
    total_requests_seen: int
    total_decisions_created: int
    last_decision_id: Optional[str]
    last_status: Optional[str]
    last_updated_ms: int


class GovernanceExecutionGuardrails:
    """
    Final sovereign execution governance boundary.
    """

    def __init__(
        self,
        *,
        guardrails_name: str = DEFAULT_GUARDRAILS_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.guardrails_name = guardrails_name

        self.event_bus = event_bus
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._requests_seen = 0
        self._decisions: List[GovernanceGuardrailDecision] = []

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------

    def evaluate(
        self,
        request: GovernanceGuardrailRequest | Dict[str, Any],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> GovernanceGuardrailDecision:
        """
        Evaluate governance safety posture.
        """

        normalized = self._normalize_request(request)
        self._requests_seen += 1

        status = self._determine_status(normalized)

        recommended_autonomy = self._recommended_autonomy_mode(
            normalized,
            status,
        )

        decision = GovernanceGuardrailDecision(
            guardrail_decision_id=str(uuid.uuid4()),
            guardrail_request_id=normalized.guardrail_request_id,
            status=status,
            action_type=normalized.action_type,
            tenant_id=normalized.tenant_id,
            case_id=normalized.case_id,
            correlation_id=normalized.correlation_id,
            execution_package_id=normalized.execution_package_id,
            connector_result_id=normalized.connector_result_id,
            failover_plan_id=normalized.failover_plan_id,
            blast_radius=normalized.blast_radius,
            current_autonomy_mode=normalized.autonomy_mode,
            recommended_autonomy_mode=recommended_autonomy,
            governance_required=self._governance_required(
                normalized,
                status,
            ),
            human_approval_required=self._human_required(
                normalized,
                status,
            ),
            legal_review_required=self._legal_required(
                normalized,
                status,
            ),
            continuity_review_required=self._continuity_required(
                normalized,
                status,
            ),
            rollback_required=self._rollback_required(
                normalized,
                status,
            ),
            verification_required=self._verification_required(
                normalized,
                status,
            ),
            execution_allowed=self._execution_allowed(status),
            freeze_mode=normalized.freeze_mode,
            constraints=self._constraints(normalized, status),
            recommended_next_steps=self._recommended_next_steps(
                normalized,
                status,
                recommended_autonomy,
            ),
            rationale=self._build_rationale(
                normalized,
                status,
                recommended_autonomy,
            ),
            metadata={
                "tenant_policy": normalized.tenant_policy,
                "lineage_event_ids": list(
                    normalized.lineage_event_ids
                ),
                "evidence_event_ids": list(
                    normalized.evidence_event_ids
                ),
                "control_ids": list(normalized.control_ids),
            },
        )

        self._record_decision(decision, context=context)

        return decision

    def submit(
        self,
        request: GovernanceGuardrailRequest | Dict[str, Any],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> GovernanceGuardrailDecision:
        """
        Compatibility alias.
        """

        return self.evaluate(request, context=context)

    def create_request(
        self,
        *,
        source_engine: str,
        action_type: str,
        severity: str,
        confidence: float,
        blast_radius: str,
        autonomy_mode: str,
        tenant_policy: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        execution_package_id: Optional[str] = None,
        connector_result_id: Optional[str] = None,
        failover_plan_id: Optional[str] = None,
        governance_approved: bool = False,
        human_approved: bool = False,
        legal_approved: bool = False,
        rollback_available: bool = False,
        verification_available: bool = False,
        continuity_review_completed: bool = False,
        resilience_degraded: bool = False,
        connector_degraded: bool = False,
        governance_stale: bool = False,
        freeze_mode: str = FREEZE_NONE,
        lineage_event_ids: Optional[Sequence[str]] = None,
        evidence_event_ids: Optional[Sequence[str]] = None,
        control_ids: Optional[Sequence[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        constraints: Optional[Sequence[str]] = None,
    ) -> GovernanceGuardrailRequest:
        """
        Convenience constructor.
        """

        return GovernanceGuardrailRequest(
            guardrail_request_id=str(uuid.uuid4()),
            source_engine=source_engine or "unknown_engine",
            action_type=self._safe_action_type(action_type),
            severity=self._safe_severity(severity),
            confidence=self._clamp_confidence(confidence),
            blast_radius=self._safe_blast_radius(blast_radius),
            autonomy_mode=self._safe_autonomy_mode(
                autonomy_mode
            ),
            tenant_policy=str(tenant_policy or "STANDARD").upper(),
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            execution_package_id=execution_package_id,
            connector_result_id=connector_result_id,
            failover_plan_id=failover_plan_id,
            governance_approved=governance_approved,
            human_approved=human_approved,
            legal_approved=legal_approved,
            rollback_available=rollback_available,
            verification_available=verification_available,
            continuity_review_completed=(
                continuity_review_completed
            ),
            resilience_degraded=resilience_degraded,
            connector_degraded=connector_degraded,
            governance_stale=governance_stale,
            freeze_mode=self._safe_freeze_mode(freeze_mode),
            lineage_event_ids=list(lineage_event_ids or []),
            evidence_event_ids=list(evidence_event_ids or []),
            control_ids=[
                str(item or "").upper().strip()
                for item in list(control_ids or [])
            ],
            payload=dict(payload or {}),
            constraints=list(constraints or []),
        )

    def create_request_from_execution_package(
        self,
        package: Any,
        *,
        tenant_policy: str = "STANDARD",
    ) -> GovernanceGuardrailRequest:
        """
        Build request from sovereign execution package.
        """

        pkg = self._to_dict(package)

        governance = dict(pkg.get("governance_metadata", {}))
        rollback = dict(pkg.get("rollback_metadata", {}))
        verification = dict(
            pkg.get("verification_metadata", {})
        )

        return self.create_request(
            source_engine="sovereign_execution_router",
            action_type=str(pkg.get("action_type", "UNKNOWN")),
            severity=str(pkg.get("severity", "INFO")),
            confidence=float(pkg.get("confidence", 0.0)),
            blast_radius=str(
                pkg.get("blast_radius", BLAST_RADIUS_LOW)
            ),
            autonomy_mode=str(
                pkg.get(
                    "autonomy_mode",
                    AUTONOMY_SUPERVISED_AUTONOMY,
                )
            ),
            tenant_policy=tenant_policy,
            tenant_id=pkg.get("tenant_id"),
            case_id=pkg.get("case_id"),
            correlation_id=pkg.get("correlation_id"),
            execution_package_id=pkg.get("execution_package_id"),
            governance_approved=bool(
                governance.get("governance_required", False)
                is False
                or governance.get("governance_approval_id")
            ),
            human_approved=not bool(
                governance.get("human_approval_required", False)
            ),
            legal_approved=not bool(
                governance.get("legal_approval_required", False)
            ),
            rollback_available=bool(
                rollback.get("rollback_available", False)
            ),
            verification_available=bool(
                verification.get(
                    "verification_required",
                    True,
                )
            ),
            continuity_review_completed=not bool(
                verification.get(
                    "continuity_review_required",
                    False,
                )
            ),
            lineage_event_ids=list(
                pkg.get("lineage_metadata", {}).get(
                    "lineage_event_ids",
                    [],
                )
            ),
            evidence_event_ids=list(
                pkg.get("compliance_metadata", {}).get(
                    "evidence_event_ids",
                    [],
                )
            ),
            control_ids=list(
                pkg.get("compliance_metadata", {}).get(
                    "control_ids",
                    [],
                )
            ),
            payload={"execution_package": pkg},
        )

    def get_recent_decisions(
        self,
        *,
        limit: int = 25,
    ) -> List[GovernanceGuardrailDecision]:
        limit = max(1, int(limit))
        return list(reversed(self._decisions[-limit:]))

    def snapshot(self) -> GovernanceExecutionGuardrailsSnapshot:
        last = self._decisions[-1] if self._decisions else None

        return GovernanceExecutionGuardrailsSnapshot(
            guardrails_name=self.guardrails_name,
            total_requests_seen=self._requests_seen,
            total_decisions_created=len(self._decisions),
            last_decision_id=(
                last.guardrail_decision_id if last else None
            ),
            last_status=last.status if last else None,
            last_updated_ms=int(time.time() * 1000),
        )

    # --------------------------------------------------------
    # DECISIONING
    # --------------------------------------------------------

    def _determine_status(
        self,
        request: GovernanceGuardrailRequest,
    ) -> str:

        if request.freeze_mode == FREEZE_GLOBAL:
            return GUARDRAIL_FROZEN

        if request.freeze_mode == FREEZE_TENANT:
            return GUARDRAIL_FROZEN

        if request.autonomy_mode == AUTONOMY_LOCKDOWN:
            return GUARDRAIL_LOCKDOWN

        if request.freeze_mode == FREEZE_ROLLBACK_ONLY:
            if request.action_type != GuardrailActionType.ROLLBACK.value:
                return GUARDRAIL_BLOCKED

        if request.governance_stale:
            return GUARDRAIL_REQUIRES_GOVERNANCE

        if not request.verification_available:
            return GUARDRAIL_REQUIRES_VERIFICATION

        if not request.rollback_available:
            if request.action_type in {
                GuardrailActionType.DISABLE_USER.value,
                GuardrailActionType.PURGE_MAILBOX.value,
                GuardrailActionType.UPDATE_POLICY.value,
                GuardrailActionType.BLOCK_NETWORK_TRAFFIC.value,
            }:
                return GUARDRAIL_REQUIRES_ROLLBACK

        if not request.continuity_review_completed:
            return GUARDRAIL_REQUIRES_CONTINUITY_REVIEW

        if request.blast_radius == BLAST_RADIUS_CRITICAL:
            if not request.human_approved:
                return GUARDRAIL_REQUIRES_APPROVAL

        if request.blast_radius == BLAST_RADIUS_HIGH:
            if request.autonomy_mode == AUTONOMY_FULL_AUTONOMY:
                return GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE

        if request.action_type in {
            GuardrailActionType.PURGE_MAILBOX.value,
            GuardrailActionType.DELETE_EMAIL.value,
            GuardrailActionType.UPDATE_POLICY.value,
        }:
            if not request.governance_approved:
                return GUARDRAIL_REQUIRES_GOVERNANCE

        if request.action_type in {
            GuardrailActionType.DISABLE_USER.value,
            GuardrailActionType.BLOCK_NETWORK_TRAFFIC.value,
        }:
            if not request.human_approved:
                return GUARDRAIL_REQUIRES_APPROVAL

        if request.tenant_policy in {
            "STRICT",
            "LOCKED",
        }:
            if request.autonomy_mode == AUTONOMY_FULL_AUTONOMY:
                return GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE

        if request.tenant_policy == "LEGAL_REVIEW_REQUIRED":
            if not request.legal_approved:
                return GUARDRAIL_REQUIRES_LEGAL_REVIEW

        if request.resilience_degraded:
            if request.blast_radius in {
                BLAST_RADIUS_HIGH,
                BLAST_RADIUS_CRITICAL,
            }:
                return GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE

        return GUARDRAIL_ALLOWED

    def _recommended_autonomy_mode(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> str:

        if status in {
            GUARDRAIL_LOCKDOWN,
            GUARDRAIL_FROZEN,
        }:
            return AUTONOMY_LOCKDOWN

        if status == GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE:
            return self._reduce_autonomy(
                request.autonomy_mode
            )

        if request.blast_radius == BLAST_RADIUS_CRITICAL:
            return AUTONOMY_MANUAL

        if request.blast_radius == BLAST_RADIUS_HIGH:
            return AUTONOMY_ASSISTED

        return request.autonomy_mode

    def _execution_allowed(self, status: str) -> bool:
        return status == GUARDRAIL_ALLOWED

    def _governance_required(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> bool:
        return (
            status == GUARDRAIL_REQUIRES_GOVERNANCE
            or request.action_type
            in {
                GuardrailActionType.PURGE_MAILBOX.value,
                GuardrailActionType.DELETE_EMAIL.value,
                GuardrailActionType.UPDATE_POLICY.value,
            }
        )

    def _human_required(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> bool:
        return (
            status == GUARDRAIL_REQUIRES_APPROVAL
            or request.blast_radius
            == BLAST_RADIUS_CRITICAL
        )

    def _legal_required(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> bool:
        return (
            status == GUARDRAIL_REQUIRES_LEGAL_REVIEW
            or request.tenant_policy
            == "LEGAL_REVIEW_REQUIRED"
        )

    def _continuity_required(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> bool:
        return (
            status
            == GUARDRAIL_REQUIRES_CONTINUITY_REVIEW
        )

    def _rollback_required(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> bool:
        return (
            status == GUARDRAIL_REQUIRES_ROLLBACK
        )

    def _verification_required(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> bool:
        return (
            status == GUARDRAIL_REQUIRES_VERIFICATION
        )

    def _constraints(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
    ) -> List[str]:

        constraints = list(request.constraints)

        if status == GUARDRAIL_FROZEN:
            constraints.append("execution_frozen")

        if status == GUARDRAIL_LOCKDOWN:
            constraints.append("autonomy_lockdown")

        if status == GUARDRAIL_REQUIRES_APPROVAL:
            constraints.append("human_approval_required")

        if status == GUARDRAIL_REQUIRES_GOVERNANCE:
            constraints.append("governance_revalidation_required")

        if status == GUARDRAIL_REQUIRES_LEGAL_REVIEW:
            constraints.append("legal_review_required")

        if status == GUARDRAIL_REQUIRES_CONTINUITY_REVIEW:
            constraints.append("continuity_review_required")

        if status == GUARDRAIL_REQUIRES_ROLLBACK:
            constraints.append("rollback_required")

        if status == GUARDRAIL_REQUIRES_VERIFICATION:
            constraints.append("verification_required")

        if status == GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE:
            constraints.append("autonomy_downgrade_required")

        if request.connector_degraded:
            constraints.append("connector_degraded")

        if request.resilience_degraded:
            constraints.append("resilience_degraded")

        if request.governance_stale:
            constraints.append("governance_stale")

        return list(dict.fromkeys(constraints))

    def _recommended_next_steps(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:

        steps: List[Dict[str, Any]] = []

        if status == GUARDRAIL_ALLOWED:
            steps.append(
                {
                    "step": "allow_execution",
                    "reason": "Governance guardrails satisfied.",
                }
            )

        if status == GUARDRAIL_FROZEN:
            steps.append(
                {
                    "step": "maintain_execution_freeze",
                    "freeze_mode": request.freeze_mode,
                }
            )

        if status == GUARDRAIL_LOCKDOWN:
            steps.append(
                {
                    "step": "maintain_autonomy_lockdown",
                }
            )

        if status == GUARDRAIL_REQUIRES_APPROVAL:
            steps.append(
                {
                    "step": "request_human_approval",
                }
            )

        if status == GUARDRAIL_REQUIRES_GOVERNANCE:
            steps.append(
                {
                    "step": "perform_governance_review",
                }
            )

        if status == GUARDRAIL_REQUIRES_LEGAL_REVIEW:
            steps.append(
                {
                    "step": "perform_legal_review",
                }
            )

        if status == GUARDRAIL_REQUIRES_CONTINUITY_REVIEW:
            steps.append(
                {
                    "step": "perform_continuity_review",
                }
            )

        if status == GUARDRAIL_REQUIRES_ROLLBACK:
            steps.append(
                {
                    "step": "prepare_or_attach_rollback",
                }
            )

        if status == GUARDRAIL_REQUIRES_VERIFICATION:
            steps.append(
                {
                    "step": "attach_verification_requirements",
                }
            )

        if status == GUARDRAIL_REQUIRES_AUTONOMY_DOWNGRADE:
            steps.append(
                {
                    "step": "downgrade_autonomy",
                    "from": request.autonomy_mode,
                    "to": recommended_autonomy,
                }
            )

        steps.append(
            {
                "step": "record_governance_lineage",
                "reason": "Decision must be replayable.",
            }
        )

        steps.append(
            {
                "step": "record_compliance_evidence",
                "reason": "Decision contributes to audit evidence.",
            }
        )

        return steps

    def _build_rationale(
        self,
        request: GovernanceGuardrailRequest,
        status: str,
        recommended_autonomy: str,
    ) -> str:
        return (
            f"Governance guardrail evaluation for action "
            f"{request.action_type}. Blast radius "
            f"{request.blast_radius}; autonomy "
            f"{request.autonomy_mode}; tenant policy "
            f"{request.tenant_policy}. Status {status}; "
            f"recommended autonomy "
            f"{recommended_autonomy}."
        )

    # --------------------------------------------------------
    # RECORDING
    # --------------------------------------------------------

    def _record_decision(
        self,
        decision: GovernanceGuardrailDecision,
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
        decision: GovernanceGuardrailDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:

        memory = self.operational_memory_engine
        if memory is None:
            return

        payload = {
            "type": "GOVERNANCE_GUARDRAIL_DECISION",
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
            print(
                f"⚠️ Governance guardrail memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        decision: GovernanceGuardrailDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:

        lineage = self.lineage_engine
        if lineage is None:
            return

        payload = {
            "lineage_type": "GOVERNANCE",
            "lineage_status": "RECORDED",
            "source_engine": self.guardrails_name,
            "summary": decision.rationale,
            "severity": decision.blast_radius,
            "confidence": 1.0,
            "mission_priority": 0,
            "tenant_id": decision.tenant_id,
            "case_id": decision.case_id,
            "correlation_id": decision.correlation_id,
            "parent_event_ids": list(
                decision.metadata.get(
                    "lineage_event_ids",
                    [],
                )
            ),
            "constraints": list(decision.constraints),
            "verification_requirements": [
                "verification_required"
                if decision.verification_required
                else "verification_not_required"
            ],
            "context": {
                "type": "GOVERNANCE_GUARDRAIL_DECISION",
                "decision": asdict(decision),
                "context": context or {},
            },
            "metadata": {
                "guardrail_decision_id": (
                    decision.guardrail_decision_id
                ),
                "status": decision.status,
                "recommended_autonomy_mode": (
                    decision.recommended_autonomy_mode
                ),
                "freeze_mode": decision.freeze_mode,
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
            print(
                f"⚠️ Governance guardrail lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        decision: GovernanceGuardrailDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:

        evidence = self.fedramp_evidence_lineage_engine
        if evidence is None:
            return

        payload = {
            "evidence_type": "POLICY_EVALUATION",
            "evidence_status": "RECORDED",
            "source_engine": self.guardrails_name,
            "summary": decision.rationale,
            "severity": decision.blast_radius,
            "confidence": 1.0,
            "mission_priority": 0,
            "tenant_id": decision.tenant_id,
            "case_id": decision.case_id,
            "correlation_id": decision.correlation_id,
            "lineage_event_ids": list(
                decision.metadata.get(
                    "lineage_event_ids",
                    [],
                )
            ),
            "parent_evidence_event_ids": list(
                decision.metadata.get(
                    "evidence_event_ids",
                    [],
                )
            ),
            "related_control_ids": list(
                decision.metadata.get(
                    "control_ids",
                    [],
                )
            ),
            "constraints": list(decision.constraints),
            "evidence_payload": {
                "type": "GOVERNANCE_GUARDRAIL_DECISION",
                "decision": asdict(decision),
                "context": context or {},
            },
            "metadata": {
                "guardrail_decision_id": (
                    decision.guardrail_decision_id
                ),
                "status": decision.status,
                "freeze_mode": decision.freeze_mode,
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
            print(
                f"⚠️ Governance guardrail evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        decision: GovernanceGuardrailDecision,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": "GOVERNANCE_GUARDRAIL_DECISION",
            "guardrails_name": self.guardrails_name,
            "decision": asdict(decision),
            "context": context or {},
        }

        try:

            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "GOVERNANCE_GUARDRAIL_DECISION",
                    payload,
                )

            elif hasattr(self.event_bus, "publish"):
                self.event_bus.publish(
                    "GOVERNANCE_GUARDRAIL_DECISION",
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Governance guardrail event emit failed: {exc}"
            )

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    @staticmethod
    def _reduce_autonomy(current: str) -> str:

        current = str(
            current or AUTONOMY_SUPERVISED_AUTONOMY
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

        return order[max(0, idx - 1)]

    @staticmethod
    def _safe_action_type(value: Any) -> str:

        value = str(
            value or GuardrailActionType.UNKNOWN.value
        ).upper()

        valid = {item.value for item in GuardrailActionType}

        return (
            value
            if value in valid
            else GuardrailActionType.UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(value: Any) -> str:

        value = str(value or "INFO").upper()

        valid = {
            "INFO",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

        return value if value in valid else "INFO"

    @staticmethod
    def _safe_blast_radius(value: Any) -> str:

        value = str(value or BLAST_RADIUS_LOW).upper()

        valid = {
            BLAST_RADIUS_LOW,
            BLAST_RADIUS_MEDIUM,
            BLAST_RADIUS_HIGH,
            BLAST_RADIUS_CRITICAL,
        }

        return (
            value
            if value in valid
            else BLAST_RADIUS_LOW
        )

    @staticmethod
    def _safe_autonomy_mode(value: Any) -> str:

        value = str(
            value or AUTONOMY_SUPERVISED_AUTONOMY
        ).upper()

        valid = {
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
            AUTONOMY_LOCKDOWN,
        }

        return (
            value
            if value in valid
            else AUTONOMY_SUPERVISED_AUTONOMY
        )

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
    def _clamp_confidence(value: Any) -> float:

        try:
            score = float(value)

        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))

    @staticmethod
    def _to_dict(value: Any) -> Dict[str, Any]:

        if value is None:
            return {}

        if isinstance(value, dict):
            return dict(value)

        if hasattr(value, "__dataclass_fields__"):
            return asdict(value)

        if hasattr(value, "__dict__"):
            return dict(value.__dict__)

        return {"value": value}

    def _normalize_request(
        self,
        request: GovernanceGuardrailRequest | Dict[str, Any],
    ) -> GovernanceGuardrailRequest:

        if isinstance(request, GovernanceGuardrailRequest):
            return request

        return GovernanceGuardrailRequest(
            guardrail_request_id=str(
                request.get("guardrail_request_id")
                or uuid.uuid4()
            ),
            source_engine=str(
                request.get("source_engine")
                or "unknown_engine"
            ),
            action_type=self._safe_action_type(
                request.get("action_type")
            ),
            severity=self._safe_severity(
                request.get("severity")
            ),
            confidence=self._clamp_confidence(
                request.get("confidence", 0.0)
            ),
            blast_radius=self._safe_blast_radius(
                request.get("blast_radius")
            ),
            autonomy_mode=self._safe_autonomy_mode(
                request.get("autonomy_mode")
            ),
            tenant_policy=str(
                request.get("tenant_policy")
                or "STANDARD"
            ).upper(),
            tenant_id=request.get("tenant_id"),
            case_id=request.get("case_id"),
            correlation_id=request.get("correlation_id"),
            execution_package_id=request.get(
                "execution_package_id"
            ),
            connector_result_id=request.get(
                "connector_result_id"
            ),
            failover_plan_id=request.get(
                "failover_plan_id"
            ),
            governance_approved=bool(
                request.get("governance_approved", False)
            ),
            human_approved=bool(
                request.get("human_approved", False)
            ),
            legal_approved=bool(
                request.get("legal_approved", False)
            ),
            rollback_available=bool(
                request.get("rollback_available", False)
            ),
            verification_available=bool(
                request.get(
                    "verification_available",
                    False,
                )
            ),
            continuity_review_completed=bool(
                request.get(
                    "continuity_review_completed",
                    False,
                )
            ),
            resilience_degraded=bool(
                request.get("resilience_degraded", False)
            ),
            connector_degraded=bool(
                request.get("connector_degraded", False)
            ),
            governance_stale=bool(
                request.get("governance_stale", False)
            ),
            freeze_mode=self._safe_freeze_mode(
                request.get("freeze_mode")
            ),
            lineage_event_ids=list(
                request.get("lineage_event_ids", [])
                or []
            ),
            evidence_event_ids=list(
                request.get("evidence_event_ids", [])
                or []
            ),
            control_ids=[
                str(item or "").upper().strip()
                for item in list(
                    request.get("control_ids", [])
                    or []
                )
            ],
            payload=dict(
                request.get("payload", {})
                or {}
            ),
            constraints=list(
                request.get("constraints", [])
                or []
            ),
        )


# ============================================================
# FACTORY
# ============================================================

def build_governance_execution_guardrails(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> GovernanceExecutionGuardrails:
    """
    Factory for explicit dependency injection.
    """

    return GovernanceExecutionGuardrails(
        event_bus=event_bus,
        operational_memory_engine=(
            operational_memory_engine
        ),
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=(
            fedramp_evidence_lineage_engine
        ),
    )