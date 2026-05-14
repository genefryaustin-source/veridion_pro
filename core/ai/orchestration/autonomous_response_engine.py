from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from core.runtime.tenant_policy_engine import (
    evaluate_tenant_action,
)

from core.runtime.governance_approval_engine import (
    get_governance_approval_engine,
)
from core.runtime.blast_radius_analyzer import (
    analyze_blast_radius,
    DECISION_ALLOW,
    DECISION_REQUIRE_APPROVAL,
    DECISION_REQUIRE_DUAL_APPROVAL,
    DECISION_REQUIRE_EXECUTIVE_APPROVAL,
    DECISION_BLOCK,
)

def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class AutonomousResponseEngine:
    """
    Semi-autonomous SOC orchestration engine.

    Responsibilities:
    - evaluate AI recommendations
    - auto-execute safe actions
    - gate risky actions behind approvals
    - launch playbooks
    - auto-escalate
    - auto-route
    - preserve evidence
    - publish realtime operational events

    This does NOT bypass governance.
    All high-risk actions are routed through:
        RiskDecisionEngine + TenantPolicyEngine + GovernanceApprovalEngine
    """

    def __init__(
        self,
        *,
        ledger: Any,
        copilot_service: Any = None,
        playbook_orchestrator: Any = None,
        approval_executor: Any = None,
        risk_decision_engine: Any = None,
        event_bus: Any = None,
        live_updates: Any = None,
    ):
        self.ledger = ledger
        self.copilot_service = copilot_service
        self.playbook_orchestrator = playbook_orchestrator
        self.approval_executor = approval_executor
        self.risk_decision_engine = risk_decision_engine
        self.event_bus = event_bus
        self.live_updates = live_updates

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def respond_to_case(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
        actor: str = "autonomous_response_engine",
        dry_run: bool = True,
        max_actions: int = 5,
    ) -> Dict[str, Any]:
        """
        Main autonomous response entrypoint.

        Default dry_run=True for safety.
        """

        response_id = self._new_response_id()

        self._record_event(
            case_id=case_id,
            event_type="AI_AUTONOMOUS_RESPONSE_STARTED",
            actor=actor,
            details={
                "response_id": response_id,
                "tenant_id": tenant_id,
                "dry_run": dry_run,
                "max_actions": max_actions,
            },
        )

        analysis = self._analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        context = analysis.get("context") or {}
        context.setdefault("case_id", case_id)
        context.setdefault("tenant_id", tenant_id)

        next_actions = analysis.get("next_actions") or {}

        actions = (
            next_actions.get("recommended_actions")
            or []
        )[:max_actions]

        results = []

        for action in actions:
            result = self.process_action(
                case_id=case_id,
                tenant_id=tenant_id,
                context=context,
                action=action,
                actor=actor,
                dry_run=dry_run,
                response_id=response_id,
            )

            results.append(result)

            if result.get("status") in {
                "approval_required",
                "failed",
                "blocked",
            }:
                break

        status = self._final_status(results)

        self._record_event(
            case_id=case_id,
            event_type="AI_AUTONOMOUS_RESPONSE_COMPLETED",
            actor=actor,
            details={
                "response_id": response_id,
                "status": status,
                "results": results,
                "dry_run": dry_run,
            },
        )

        self._publish_realtime(
            event_type="AI_AUTONOMOUS_RESPONSE_COMPLETED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload={
                "response_id": response_id,
                "status": status,
                "dry_run": dry_run,
                "result_count": len(results),
            },
        )

        return {
            "response_id": response_id,
            "case_id": case_id,
            "tenant_id": tenant_id,
            "status": status,
            "dry_run": dry_run,
            "analysis": analysis,
            "results": results,
            "generated_at_ms": _now_ms(),
            "engine": "AutonomousResponseEngine",
        }

    def process_action(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
        context: Dict[str, Any],
        action: Dict[str, Any],
        actor: str,
        dry_run: bool,
        response_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        response_id = response_id or self._new_response_id()

        context = context or {}
        context.setdefault("case_id", case_id)
        context.setdefault("tenant_id", tenant_id)

        action_code = _upper(
            action.get("action")
            or action.get("code")
            or action.get("label")
        )

        decision = self._evaluate_risk(
            context=context,
            action=action,
        )

        self._record_event(
            case_id=case_id,
            event_type="AI_ACTION_DECISIONED",
            actor=actor,
            details={
                "response_id": response_id,
                "action": action,
                "decision": decision,
                "dry_run": dry_run,
            },
        )

        if dry_run:
            return {
                "response_id": response_id,
                "case_id": case_id,
                "action": action_code,
                "status": "dry_run",
                "decision": decision,
                "timestamp_ms": _now_ms(),
            }

        if decision.get("blocked"):
            self._record_event(
                case_id=case_id,
                event_type="AI_ACTION_BLOCKED",
                actor=actor,
                details={
                    "response_id": response_id,
                    "action": action,
                    "decision": decision,
                },
            )

            self._publish_realtime(
                event_type="AI_ACTION_BLOCKED",
                case_id=case_id,
                tenant_id=tenant_id,
                actor=actor,
                payload={
                    "response_id": response_id,
                    "action": action_code,
                    "decision": decision,
                },
            )

            return {
                "response_id": response_id,
                "case_id": case_id,
                "action": action_code,
                "status": "blocked",
                "decision": decision,
                "timestamp_ms": _now_ms(),
            }

        if (
            decision.get("requires_approval")
            or decision.get("requires_legal")
            or decision.get("requires_dual_approval")
        ):
            return self._gate_action(
                case_id=case_id,
                tenant_id=tenant_id,
                context=context,
                action=action,
                actor=actor,
                decision=decision,
                response_id=response_id,
            )

        if decision.get("auto_execute") or decision.get("safe_to_automate"):
            return self._execute_action(
                case_id=case_id,
                tenant_id=tenant_id,
                action=action,
                actor=actor,
                decision=decision,
            )

        return self._record_recommendation_only(
            case_id=case_id,
            tenant_id=tenant_id,
            action=action,
            actor=actor,
            decision=decision,
        )

    # ------------------------------------------------------------------
    # Batch / Queue APIs
    # ------------------------------------------------------------------

    def respond_to_queue(
        self,
        *,
        tenant_id: Optional[str] = None,
        actor: str = "autonomous_response_engine",
        dry_run: bool = True,
        limit: int = 25,
        max_actions_per_case: int = 3,
    ) -> Dict[str, Any]:
        cases = self._load_cases(
            tenant_id=tenant_id,
            limit=limit,
        )

        results = []

        for case in cases:
            case_id = case.get("case_id") or case.get("id")

            if not case_id:
                continue

            result = self.respond_to_case(
                case_id=case_id,
                tenant_id=tenant_id or case.get("tenant_id"),
                actor=actor,
                dry_run=dry_run,
                max_actions=max_actions_per_case,
            )

            results.append(result)

        return {
            "tenant_id": tenant_id,
            "case_count": len(results),
            "results": results,
            "dry_run": dry_run,
            "generated_at_ms": _now_ms(),
        }

    def respond_to_event(
        self,
        *,
        event: Dict[str, Any],
        actor: str = "autonomous_response_engine",
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        case_id = event.get("case_id")
        tenant_id = event.get("tenant_id")

        if not case_id:
            return {
                "status": "ignored",
                "reason": "event has no case_id",
                "event": event,
                "timestamp_ms": _now_ms(),
            }

        event_type = _upper(event.get("event_type"))

        trigger_events = {
            "CASE_ESCALATED",
            "SLA_BREACHED",
            "CAMPAIGN_DETECTED",
            "GRAPH_UPDATED",
            "APPROVAL_REQUESTED",
            "PLAYBOOK_EXECUTED",
        }

        if event_type not in trigger_events:
            return {
                "status": "ignored",
                "reason": f"{event_type} is not an autonomous response trigger",
                "event_type": event_type,
                "timestamp_ms": _now_ms(),
            }

        return self.respond_to_case(
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            dry_run=dry_run,
            max_actions=3,
        )

    # ------------------------------------------------------------------
    # Action Execution / Gating
    # ------------------------------------------------------------------

    def _gate_action(
            self,
            *,
            case_id: Any,
            tenant_id: Optional[str],
            context: Dict[str, Any],
            action: Dict[str, Any],
            actor: str,
            decision: Dict[str, Any],
            response_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        from core.runtime.blast_radius_analyzer import (
            analyze_blast_radius,
            DECISION_ALLOW,
            DECISION_REQUIRE_APPROVAL,
            DECISION_REQUIRE_DUAL_APPROVAL,
            DECISION_REQUIRE_EXECUTIVE_APPROVAL,
            DECISION_BLOCK,
        )

        action_code = _upper(
            action.get("action")
            or action.get("code")
            or action.get("label")
        )

        response_id = (
                response_id
                or self._new_response_id()
        )

        effective_tenant_id = (
                tenant_id
                or context.get("tenant_id")
                or action.get("tenant_id")
                or "default"
        )

        execution_id = (
                action.get("execution_id")
                or action.get("job_id")
                or response_id
        )

        # =========================================================
        # BLAST RADIUS ANALYSIS
        # =========================================================

        blast_result = analyze_blast_radius(
            self.storage,
            tenant_id=effective_tenant_id,
            action=action_code,
            payload=action,
            actor=actor,
            context={
                **context,
                "case_id": case_id,
                "execution_id": execution_id,
                "response_id": response_id,
                "autonomous": True,
            },
        )

        # ---------------------------------------------------------
        # REALTIME TELEMETRY
        # ---------------------------------------------------------

        self._publish_realtime(
            event_type="BLAST_RADIUS_EVALUATED",
            case_id=case_id,
            tenant_id=effective_tenant_id,
            actor=actor,
            payload={
                "response_id": response_id,
                "execution_id": execution_id,
                "action": action_code,
                "risk_score": blast_result.risk_score,
                "risk_level": blast_result.risk_level,
                "decision": blast_result.decision,
                "autonomy_blocked": (
                    blast_result.autonomy_blocked
                ),
            },
        )

        self._record_event(
            case_id=case_id,
            event_type="BLAST_RADIUS_ANALYZED",
            actor=actor,
            details=blast_result.to_dict(),
        )

        # =========================================================
        # AUTONOMY BLOCK
        # =========================================================

        if blast_result.decision == DECISION_BLOCK:
            self._record_event(
                case_id=case_id,
                event_type="AUTONOMY_BLOCKED",
                actor=actor,
                details={
                    "response_id": response_id,
                    "execution_id": execution_id,
                    "action": action_code,
                    "reason": (
                        "Blast radius "
                        "analysis blocked "
                        "autonomous execution."
                    ),
                    "blast_radius": (
                        blast_result.to_dict()
                    ),
                },
            )

            self._publish_realtime(
                event_type="AUTONOMY_BLOCKED",
                case_id=case_id,
                tenant_id=effective_tenant_id,
                actor=actor,
                payload={
                    "response_id": response_id,
                    "execution_id": execution_id,
                    "action": action_code,
                    "blast_radius": (
                        blast_result.to_dict()
                    ),
                },
            )

            return {
                "response_id": response_id,
                "execution_id": execution_id,
                "status": "blocked",
                "blocked": True,
                "approval_required": False,
                "case_id": case_id,
                "tenant_id": effective_tenant_id,
                "action": action_code,
                "reason": (
                    "Blast radius analysis "
                    "blocked execution."
                ),
                "blast_radius": (
                    blast_result.to_dict()
                ),
                "timestamp_ms": _now_ms(),
            }

        # =========================================================
        # APPLY BLAST RADIUS GOVERNANCE
        # =========================================================

        if blast_result.requires_legal:
            decision["requires_legal"] = True

        if blast_result.requires_dual_approval:
            decision["requires_dual_approval"] = True

        decision["risk_level"] = (
            blast_result.risk_level
        )

        decision["risk_score"] = (
            blast_result.risk_score
        )

        decision["blast_radius"] = (
            blast_result.to_dict()
        )

        # =========================================================
        # EXECUTIVE APPROVAL ESCALATION
        # =========================================================

        if (
                blast_result.decision
                == DECISION_REQUIRE_EXECUTIVE_APPROVAL
        ):
            decision[
                "requires_executive_approval"
            ] = True

            decision[
                "requires_dual_approval"
            ] = True

            decision[
                "governance_status"
            ] = "EXECUTIVE_APPROVAL_REQUIRED"

        # =========================================================
        # EXISTING APPROVAL EXECUTOR FLOW
        # =========================================================

        if self.approval_executor is not None:
            result = (
                self.approval_executor
                .execute_or_gate(
                    case_id=case_id,
                    action=action,
                    executor_callback=lambda approved_action:
                    self._execute_action_callback(
                        case_id=case_id,
                        tenant_id=effective_tenant_id,
                        action=approved_action,
                        actor=actor,
                    ),
                    actor=actor,
                    tenant_id=effective_tenant_id,
                    dry_run=False,
                )
            )

            return {
                "status": result.get(
                    "status"
                ),
                "case_id": case_id,
                "action": action_code,
                "decision": decision,
                "blast_radius": (
                    blast_result.to_dict()
                ),
                "approval_result": result,
                "timestamp_ms": _now_ms(),
            }

        # =========================================================
        # GOVERNANCE APPROVAL ENGINE
        # =========================================================

        approval_engine = (
            get_governance_approval_engine(
                self.ledger,
                event_bus=self.event_bus,
            )
        )

        reason = (
                decision.get("policy_reason")
                or self._first_reason(
            decision
        )
                or "Governance approval required."
        )

        # ---------------------------------------------------------
        # APPROVAL TYPE
        # ---------------------------------------------------------

        approval_type = "STANDARD"

        if (
                blast_result.decision
                == DECISION_REQUIRE_DUAL_APPROVAL
        ):
            approval_type = "DUAL"

        if (
                blast_result.decision
                == DECISION_REQUIRE_EXECUTIVE_APPROVAL
        ):
            approval_type = "EXECUTIVE"

        approval_request = (
            approval_engine
            .create_approval_request(
                tenant_id=effective_tenant_id,
                action=action_code or "UNKNOWN",
                requested_by=actor,
                execution_id=execution_id,
                job_id=action.get(
                    "job_id"
                ),
                case_id=case_id,
                alert_id=(
                        context.get("alert_id")
                        or action.get(
                    "alert_id"
                )
                ),
                evidence_id=(
                        context.get("evidence_id")
                        or action.get(
                    "evidence_id"
                )
                ),
                severity=(
                    blast_result.risk_level
                ),
                risk_score=int(
                    blast_result.risk_score
                ),
                requires_legal=bool(
                    decision.get(
                        "requires_legal"
                    )
                ),
                requires_dual_approval=bool(
                    decision.get(
                        "requires_dual_approval"
                    )
                ),
                reason=reason,
                payload={
                    "response_id":
                        response_id,
                    "context":
                        context,
                    "action":
                        action,
                    "decision":
                        decision,
                    "blast_radius":
                        blast_result.to_dict(),
                },
                metadata={
                    "approval_type":
                        approval_type,
                    "governance_status":
                        decision.get(
                            "governance_status"
                        ),
                    "policy_decision":
                        decision.get(
                            "policy_decision"
                        ),
                    "policy_reason":
                        decision.get(
                            "policy_reason"
                        ),
                    "blast_radius":
                        blast_result.to_dict(),
                    "source":
                        (
                            "autonomous_response_engine"
                        ),
                },
            )
        )

        # =========================================================
        # AUDIT + TELEMETRY
        # =========================================================

        self._record_event(
            case_id=case_id,
            event_type="AI_ACTION_REQUIRES_APPROVAL",
            actor=actor,
            details={
                "response_id":
                    response_id,
                "approval_id":
                    approval_request.approval_id,
                "approval_type":
                    approval_type,
                "action":
                    action,
                "decision":
                    decision,
                "blast_radius":
                    blast_result.to_dict(),
                "requires_legal":
                    bool(
                        decision.get(
                            "requires_legal"
                        )
                    ),
                "requires_dual_approval":
                    bool(
                        decision.get(
                            "requires_dual_approval"
                        )
                    ),
            },
        )

        self._publish_realtime(
            event_type="AI_ACTION_REQUIRES_APPROVAL",
            case_id=case_id,
            tenant_id=effective_tenant_id,
            actor=actor,
            payload={
                "response_id":
                    response_id,
                "approval_id":
                    approval_request.approval_id,
                "approval_type":
                    approval_type,
                "action":
                    action_code,
                "decision":
                    decision,
                "blast_radius":
                    blast_result.to_dict(),
                "requires_legal":
                    bool(
                        decision.get(
                            "requires_legal"
                        )
                    ),
                "requires_dual_approval":
                    bool(
                        decision.get(
                            "requires_dual_approval"
                        )
                    ),
            },
        )

        return {
            "response_id": response_id,
            "execution_id": execution_id,
            "status": "approval_required",
            "approval_required": True,
            "approval_id": (
                approval_request.approval_id
            ),
            "approval_type": approval_type,
            "requires_legal": bool(
                decision.get(
                    "requires_legal"
                )
            ),
            "requires_dual_approval": bool(
                decision.get(
                    "requires_dual_approval"
                )
            ),
            "case_id": case_id,
            "tenant_id": effective_tenant_id,
            "action": action_code,
            "decision": decision,
            "blast_radius": (
                blast_result.to_dict()
            ),
            "timestamp_ms": _now_ms(),
        }

    def _execute_action(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
        action: Dict[str, Any],
        actor: str,
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        if self.playbook_orchestrator is not None:
            result = self.playbook_orchestrator.execute_recommendation(
                case_id=case_id,
                recommendation=action,
                actor=actor,
                tenant_id=tenant_id,
                dry_run=False,
            )

            return {
                "status": result.get("status"),
                "case_id": case_id,
                "action": _upper(action.get("action") or action.get("label")),
                "decision": decision,
                "execution": result,
                "timestamp_ms": _now_ms(),
            }

        return self._execute_action_callback(
            case_id=case_id,
            tenant_id=tenant_id,
            action=action,
            actor=actor,
        )

    def _execute_action_callback(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
        action: Dict[str, Any],
        actor: str,
    ) -> Dict[str, Any]:
        action_code = _upper(
            action.get("action")
            or action.get("label")
        )

        self._record_event(
            case_id=case_id,
            event_type="AI_ACTION_RECORDED",
            actor=actor,
            details={
                "action": action,
                "note": "No playbook_orchestrator configured; action recorded only.",
            },
        )

        self._publish_realtime(
            event_type="AI_ACTION_RECORDED",
            case_id=case_id,
            tenant_id=tenant_id,
            actor=actor,
            payload={
                "action": action_code,
                "recorded_only": True,
            },
        )

        return {
            "status": "recorded_only",
            "action": action_code,
            "timestamp_ms": _now_ms(),
        }

    def _record_recommendation_only(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
        action: Dict[str, Any],
        actor: str,
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._record_event(
            case_id=case_id,
            event_type="AI_RECOMMENDATION_RECORDED",
            actor=actor,
            details={
                "action": action,
                "decision": decision,
            },
        )

        return {
            "status": "recommendation_recorded",
            "case_id": case_id,
            "action": _upper(action.get("action") or action.get("label")),
            "decision": decision,
            "timestamp_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Analysis / Risk
    # ------------------------------------------------------------------

    def _analyze_case(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.copilot_service is None:
            return {
                "case_id": case_id,
                "tenant_id": tenant_id,
                "context": {
                    "case_id": case_id,
                    "tenant_id": tenant_id,
                    "severity": "UNKNOWN",
                    "status": "UNKNOWN",
                    "operational_priority_score": 0,
                },
                "next_actions": {
                    "recommended_actions": [],
                },
            }

        return self.copilot_service.analyze_case(
            case_id=case_id,
            tenant_id=tenant_id,
        )

    def _evaluate_risk(
        self,
        *,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        action_code = _upper(
            action.get("action")
            or action.get("label")
            or action.get("code")
        )

        if self.risk_decision_engine is not None:
            base_decision = self.risk_decision_engine.evaluate_decision(
                context=context,
                action=action,
            )
        else:
            base_decision = {
                "action": action_code,
                "risk_level": "MEDIUM",
                "risk_score": 50,
                "auto_execute": False,
                "safe_to_automate": False,
                "requires_approval": bool(action.get("requires_approval")),
                "requires_legal": False,
                "reasoning": [
                    (
                        "RiskDecisionEngine not configured; "
                        "defaulting to recommendation-only behavior."
                    )
                ],
            }

        tenant_id = (
            context.get("tenant_id")
            or action.get("tenant_id")
            or "default"
        )

        severity = (
            context.get("severity")
            or base_decision.get("risk_level")
            or "MEDIUM"
        )

        risk_score = int(
            base_decision.get("risk_score")
            or context.get("risk_score")
            or 50
        )

        confidence = float(
            base_decision.get("confidence")
            or context.get("confidence_score")
            or 0.50
        )

        categories = (
            context.get("categories")
            or action.get("categories")
            or []
        )

        policy_decision = evaluate_tenant_action(
            self.ledger,
            tenant_id=tenant_id,
            action=action_code,
            risk_score=risk_score,
            severity=severity,
            confidence=confidence,
            categories=categories,
            payload={
                "context": context,
                "action": action,
            },
            actor="autonomous_response_engine",
        )

        if policy_decision.blocked:
            return {
                **base_decision,
                "blocked": True,
                "auto_execute": False,
                "safe_to_automate": False,
                "requires_approval": False,
                "requires_legal": False,
                "requires_dual_approval": False,
                "policy_decision": policy_decision.decision,
                "policy_reason": policy_decision.reason,
                "governance_status": "BLOCKED",
            }

        if (
            policy_decision.requires_legal
            or policy_decision.requires_dual_approval
        ):
            return {
                **base_decision,
                "blocked": False,
                "auto_execute": False,
                "safe_to_automate": False,
                "requires_approval": True,
                "requires_legal": bool(policy_decision.requires_legal),
                "requires_dual_approval": bool(policy_decision.requires_dual_approval),
                "policy_decision": policy_decision.decision,
                "policy_reason": policy_decision.reason,
                "governance_status": "LEGAL_REVIEW_REQUIRED",
            }

        if policy_decision.requires_approval:
            return {
                **base_decision,
                "blocked": False,
                "auto_execute": False,
                "safe_to_automate": False,
                "requires_approval": True,
                "requires_legal": False,
                "requires_dual_approval": False,
                "policy_decision": policy_decision.decision,
                "policy_reason": policy_decision.reason,
                "governance_status": "APPROVAL_REQUIRED",
            }

        if policy_decision.allowed:
            return {
                **base_decision,
                "blocked": False,
                "auto_execute": True,
                "safe_to_automate": True,
                "requires_approval": False,
                "requires_legal": False,
                "requires_dual_approval": False,
                "policy_decision": policy_decision.decision,
                "policy_reason": policy_decision.reason,
                "governance_status": "AUTO_APPROVED",
            }

        return {
            **base_decision,
            "blocked": False,
            "auto_execute": False,
            "safe_to_automate": False,
            "requires_approval": True,
            "requires_legal": False,
            "requires_dual_approval": False,
            "policy_decision": "SAFE_DEFAULT",
            "policy_reason": "Fallback governance approval required.",
            "governance_status": "SAFE_DEFAULT",
        }

    # ------------------------------------------------------------------
    # Case Loading
    # ------------------------------------------------------------------

    def _load_cases(
        self,
        *,
        tenant_id: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        for method_name in [
            "get_cases",
            "list_cases",
            "fetch_cases",
            "get_all_cases",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    if tenant_id:
                        result = method(tenant_id=tenant_id)
                    else:
                        result = method()

                    return [
                        dict(r)
                        for r in result
                    ][:limit]

                except TypeError:
                    try:
                        result = method(tenant_id)
                        return [
                            dict(r)
                            for r in result
                        ][:limit]
                    except Exception:
                        pass

                except Exception:
                    pass

        try:
            with self.ledger._connect() as con:
                if tenant_id:
                    rows = con.execute(
                        """
                        SELECT *
                        FROM cases
                        WHERE tenant_id = ?
                        ORDER BY created_at_ms DESC
                        LIMIT ?
                        """,
                        (tenant_id, limit),
                    ).fetchall()
                else:
                    rows = con.execute(
                        """
                        SELECT *
                        FROM cases
                        ORDER BY created_at_ms DESC
                        LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()

                return [
                    dict(r)
                    for r in rows
                ]

        except Exception:
            return []

    # ------------------------------------------------------------------
    # Events / Realtime
    # ------------------------------------------------------------------

    def _record_event(
        self,
        *,
        case_id: Any,
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        for method_name in [
            "add_case_event",
            "create_case_event",
            "record_case_event",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    method(
                        case_id=case_id,
                        event_type=event_type,
                        actor=actor,
                        details=details,
                    )
                    return
                except TypeError:
                    try:
                        method(
                            case_id,
                            event_type,
                            actor,
                            details,
                        )
                        return
                    except Exception:
                        pass
                except Exception:
                    pass

    def _publish_realtime(
        self,
        *,
        event_type: str,
        case_id: Any,
        tenant_id: Optional[str],
        actor: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    case_id=case_id,
                    tenant_id=tenant_id,
                    actor=actor,
                    source="autonomous_response_engine",
                )
            except TypeError:
                try:
                    self.event_bus.publish(
                        event_type=event_type,
                        tenant_id=tenant_id or "default",
                        source="autonomous_response_engine",
                        payload={
                            "case_id": case_id,
                            "actor": actor,
                            **(payload or {}),
                        },
                    )
                except Exception:
                    pass
            except Exception:
                pass

        if self.live_updates is not None:
            try:
                self.live_updates.broadcast_case_update(
                    case_id=case_id,
                    tenant_id=tenant_id,
                    event_type=event_type,
                    payload=payload,
                    actor=actor,
                )
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _final_status(
        self,
        results: List[Dict[str, Any]],
    ) -> str:
        if not results:
            return "no_actions"

        if any(r.get("status") == "failed" for r in results):
            return "failed"

        if any(r.get("status") == "blocked" for r in results):
            return "blocked"

        if any(r.get("status") == "approval_required" for r in results):
            return "paused_for_approval"

        if any(r.get("status") == "dry_run" for r in results):
            return "dry_run"

        if all(r.get("status") in {"completed", "recorded_only", "executed"} for r in results):
            return "completed"

        return "partial"

    def _first_reason(self, decision: Dict[str, Any]) -> str:
        reasoning = decision.get("reasoning")

        if isinstance(reasoning, list) and reasoning:
            return str(reasoning[0])

        if isinstance(reasoning, str):
            return reasoning

        return ""

    def _new_response_id(self) -> str:
        return f"RESP-{uuid.uuid4().hex[:12].upper()}"