from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


class RiskDecisionEngine:
    """
    Operational AI risk evaluation engine.

    Determines:
    - should AI auto-execute?
    - require approval?
    - require legal review?
    - require escalation?
    - safe to automate?
    - high operational risk?
    - regulated workflow?

    This is the governance brain for AI orchestration.
    """

    HIGH_RISK_ACTIONS = {
        "CLOSE_CASE",
        "MERGE_INVESTIGATIONS",
        "DISABLE_ACCOUNT",
        "ISOLATE_ENDPOINT",
        "DELETE_EVIDENCE",
        "EXPORT_EVIDENCE",
        "REVOKE_CREDENTIALS",
        "CONTAIN_USER",
        "INITIATE_CONTAINMENT_REVIEW",
    }

    LEGAL_ACTIONS = {
        "REQUEST_LEGAL_REVIEW",
        "REQUEST_EXPORT_REVIEW",
        "EXPORT_EVIDENCE",
        "EVIDENCE_DISPOSITION",
    }

    SAFE_AUTOMATION_ACTIONS = {
        "ESCALATE_CASE",
        "ASSIGN_ANALYST",
        "REASSIGN_TIER_3",
        "PRESERVE_EVIDENCE",
        "LINK_RELATED_CASES",
        "CLUSTER_EVIDENCE",
        "REQUEST_ENDPOINT_SCAN",
        "INCREASE_SLA_PRIORITY",
    }

    EXPORT_CONTROL_TERMS = {
        "ITAR",
        "EAR",
        "EAR99",
        "USML",
        "EXPORT_CONTROL",
        "CONTROLLED_TECHNICAL_INFORMATION",
        "CTI",
    }

    def __init__(
        self,
        *,
        approval_executor: Any = None,
    ):
        self.approval_executor = approval_executor

    # ------------------------------------------------------------------
    # Main Decision API
    # ------------------------------------------------------------------

    def evaluate_decision(
        self,
        *,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:

        action_code = self._action_code(action)

        severity = _upper(
            context.get("severity")
        )

        operational_priority = _safe_int(
            context.get("operational_priority_score"),
            0,
        )

        blast_radius = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        linked_cases = (
            context.get("linked_cases")
            or []
        )

        entities = (
            context.get("entities")
            or []
        )

        sla = context.get("sla") or {}

        campaign = (
            context.get("campaign")
            or {}
        )

        approvals = (
            context.get("approvals")
            or []
        )

        # --------------------------------------------------------------
        # Decision Signals
        # --------------------------------------------------------------

        export_control_detected = (
            self.detect_export_control(
                entities=entities,
                context=context,
            )
        )

        regulated_workflow = (
            export_control_detected
            or action_code in self.LEGAL_ACTIONS
        )

        high_operational_risk = (
            severity == "CRITICAL"
            or operational_priority >= 150
            or blast_radius >= 80
            or len(linked_cases) >= 5
            or sla.get("breached")
            or bool(campaign.get("campaign_id"))
        )

        requires_approval = (
            self.requires_approval(
                action=action,
                context=context,
            )
        )

        requires_legal = (
            regulated_workflow
            or action_code in self.LEGAL_ACTIONS
        )

        safe_to_automate = (
            action_code in self.SAFE_AUTOMATION_ACTIONS
            and not requires_approval
            and not requires_legal
            and not high_operational_risk
        )

        auto_execute = (
            safe_to_automate
            and not approvals
        )

        escalation_required = (
            severity == "CRITICAL"
            or sla.get("breached")
            or blast_radius >= 85
        )

        risk_level = self.classify_risk_level(
            high_operational_risk=high_operational_risk,
            requires_legal=requires_legal,
            requires_approval=requires_approval,
            severity=severity,
            blast_radius=blast_radius,
        )

        reasoning = self._build_reasoning(
            action_code=action_code,
            severity=severity,
            blast_radius=blast_radius,
            linked_cases=linked_cases,
            sla=sla,
            campaign=campaign,
            regulated_workflow=regulated_workflow,
            high_operational_risk=high_operational_risk,
            requires_approval=requires_approval,
            requires_legal=requires_legal,
            safe_to_automate=safe_to_automate,
            escalation_required=escalation_required,
        )

        return {
            "action": action_code,

            "risk_level":
                risk_level,

            "auto_execute":
                auto_execute,

            "safe_to_automate":
                safe_to_automate,

            "requires_approval":
                requires_approval,

            "requires_legal":
                requires_legal,

            "regulated_workflow":
                regulated_workflow,

            "high_operational_risk":
                high_operational_risk,

            "escalation_required":
                escalation_required,

            "approval_type":
                self.required_approval_type(
                    action=action,
                    context=context,
                ) if requires_approval else None,

            "reasoning":
                reasoning,

            "generated_at_ms":
                _now_ms(),

            "engine":
                "RiskDecisionEngine",
        }

    # ------------------------------------------------------------------
    # Risk Classification
    # ------------------------------------------------------------------

    def classify_risk_level(
        self,
        *,
        high_operational_risk: bool,
        requires_legal: bool,
        requires_approval: bool,
        severity: str,
        blast_radius: int,
    ) -> str:

        if (
            requires_legal
            or blast_radius >= 90
            or severity == "CRITICAL"
        ):
            return "CRITICAL"

        if (
            high_operational_risk
            or requires_approval
            or blast_radius >= 70
        ):
            return "HIGH"

        if blast_radius >= 40:
            return "MEDIUM"

        return "LOW"

    # ------------------------------------------------------------------
    # Approval Logic
    # ------------------------------------------------------------------

    def requires_approval(
        self,
        *,
        action: Dict[str, Any],
        context: Dict[str, Any],
    ) -> bool:

        action_code = self._action_code(action)

        if bool(action.get("requires_approval")):
            return True

        if action_code in self.HIGH_RISK_ACTIONS:
            return True

        if action_code in self.LEGAL_ACTIONS:
            return True

        if self.detect_export_control(
            entities=context.get("entities") or [],
            context=context,
        ):
            if action_code not in self.SAFE_AUTOMATION_ACTIONS:
                return True

        return False

    def required_approval_type(
        self,
        *,
        action: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:

        explicit = action.get("approval_type")

        if explicit:
            return explicit

        action_code = self._action_code(action)

        if "LEGAL" in action_code:
            return "LEGAL_REVIEW"

        if "EXPORT" in action_code:
            return "EXPORT_CONTROL_REVIEW"

        if "CONTAIN" in action_code:
            return "CONTAINMENT_APPROVAL"

        if "MERGE" in action_code:
            return "CASE_MERGE_APPROVAL"

        if "CLOSE" in action_code:
            return "CLOSURE_APPROVAL"

        if (
            self.detect_export_control(
                entities=context.get("entities") or [],
                context=context,
            )
        ):
            return "EXPORT_CONTROL_REVIEW"

        return "AI_ACTION_APPROVAL"

    # ------------------------------------------------------------------
    # Export-Control Detection
    # ------------------------------------------------------------------

    def detect_export_control(
        self,
        *,
        entities: List[Any],
        context: Dict[str, Any],
    ) -> bool:

        for entity in entities:

            entity_upper = _upper(entity)

            for term in self.EXPORT_CONTROL_TERMS:

                if term in entity_upper:
                    return True

        export_reasoning = (
            context.get("reasoning", {})
            .get("export_control_reasoning", {})
        )

        if export_reasoning.get("detected"):
            return True

        return False

    # ------------------------------------------------------------------
    # Reasoning
    # ------------------------------------------------------------------

    def _build_reasoning(
        self,
        *,
        action_code: str,
        severity: str,
        blast_radius: int,
        linked_cases: List[Any],
        sla: Dict[str, Any],
        campaign: Dict[str, Any],
        regulated_workflow: bool,
        high_operational_risk: bool,
        requires_approval: bool,
        requires_legal: bool,
        safe_to_automate: bool,
        escalation_required: bool,
    ) -> List[str]:

        reasons = []

        if severity == "CRITICAL":
            reasons.append(
                "Critical severity investigation detected."
            )

        if sla.get("breached"):
            reasons.append(
                "SLA breach increases operational risk."
            )

        if blast_radius >= 80:
            reasons.append(
                "Blast radius exceeds high-risk threshold."
            )

        if len(linked_cases) >= 5:
            reasons.append(
                "Cross-case linkage indicates possible campaign activity."
            )

        if campaign.get("campaign_id"):
            reasons.append(
                "Campaign activity detected."
            )

        if regulated_workflow:
            reasons.append(
                "Regulated workflow requires additional governance."
            )

        if requires_legal:
            reasons.append(
                "Legal review required before execution."
            )

        if requires_approval:
            reasons.append(
                "Human approval required before execution."
            )

        if safe_to_automate:
            reasons.append(
                "Action classified as safe for automation."
            )

        if escalation_required:
            reasons.append(
                "Operational escalation is recommended."
            )

        if not reasons:
            reasons.append(
                "No elevated operational risk detected."
            )

        return reasons

    # ------------------------------------------------------------------
    # Operational Policies
    # ------------------------------------------------------------------

    def should_auto_execute(
        self,
        *,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> bool:

        decision = self.evaluate_decision(
            context=context,
            action=action,
        )

        return bool(
            decision.get("auto_execute")
        )

    def should_require_human_review(
        self,
        *,
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> bool:

        decision = self.evaluate_decision(
            context=context,
            action=action,
        )

        return bool(
            decision.get("requires_approval")
            or decision.get("requires_legal")
        )

    def should_escalate(
        self,
        *,
        context: Dict[str, Any],
    ) -> bool:

        severity = _upper(
            context.get("severity")
        )

        blast_radius = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        sla = context.get("sla") or {}

        return (
            severity == "CRITICAL"
            or blast_radius >= 85
            or sla.get("breached")
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _action_code(
        self,
        action: Dict[str, Any],
    ) -> str:

        return _upper(
            action.get("action")
            or action.get("code")
            or action.get("label")
        )