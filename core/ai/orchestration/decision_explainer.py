from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _upper(value: Any) -> str:
    return str(value or "").upper().strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


class DecisionExplainer:
    """
    Explainable AI operations layer.

    Explains:
    - why escalation occurred
    - why approval is required
    - why autonomous containment is allowed
    - why campaign linkage is suspected
    - why policy blocked execution
    - why rollback is required
    """

    def __init__(
        self,
        *,
        policy_engine: Any = None,
        orchestration_memory: Any = None,
        ledger: Any = None,
    ):
        self.policy_engine = policy_engine
        self.orchestration_memory = orchestration_memory
        self.ledger = ledger

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def explain_decision(
        self,
        *,
        decision: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        action: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        action = action or {}

        explanation_type = self._detect_explanation_type(
            decision=decision,
            context=context,
            action=action,
        )

        sections = []

        if explanation_type == "APPROVAL_REQUIRED":
            sections = self.explain_approval_required(
                decision=decision,
                context=context,
                action=action,
            )["sections"]

        elif explanation_type == "AUTONOMOUS_ALLOWED":
            sections = self.explain_autonomous_allowed(
                decision=decision,
                context=context,
                action=action,
            )["sections"]

        elif explanation_type == "ESCALATION":
            sections = self.explain_escalation(
                decision=decision,
                context=context,
                action=action,
            )["sections"]

        elif explanation_type == "CAMPAIGN_LINKAGE":
            sections = self.explain_campaign_linkage(
                decision=decision,
                context=context,
            )["sections"]

        else:
            sections = self._generic_explanation(
                decision=decision,
                context=context,
                action=action,
            )

        return {
            "explanation_type": explanation_type,
            "headline": self._headline(explanation_type, decision, action),
            "sections": sections,
            "summary": self._summary_from_sections(sections),
            "generated_at_ms": _now_ms(),
            "engine": "DecisionExplainer",
        }

    # ------------------------------------------------------------------
    # Specific Explanations
    # ------------------------------------------------------------------

    def explain_escalation(
        self,
        *,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        action: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        reasons = []

        severity = _upper(context.get("severity"))
        sla = context.get("sla") or {}
        blast_radius = _safe_int(context.get("blast_radius_score"), 0)
        entities = context.get("entities") or []
        workload = context.get("analyst_workload") or {}
        campaign = context.get("campaign") or {}

        if severity == "CRITICAL":
            reasons.append("Case severity is CRITICAL.")

        if sla.get("breached"):
            reasons.append("SLA is breached or overdue.")

        if blast_radius >= 75:
            reasons.append("Blast-radius score exceeds high-risk threshold.")

        if self._contains_export_control(entities, context):
            reasons.append("Export-control / CUI / ITAR indicators are present.")

        if campaign.get("campaign_id"):
            reasons.append("Case appears linked to a broader campaign.")

        if self._analyst_workload_saturated(workload):
            reasons.append("Assigned analyst or queue workload appears saturated.")

        sections = [
            {
                "title": "Why escalation occurred",
                "items": reasons or ["No explicit escalation driver was identified."],
            },
            {
                "title": "Operational impact",
                "items": [
                    "Escalation increases visibility and prioritization.",
                    "Manager or senior analyst review may be required.",
                    "Realtime activity feeds and command center views should update.",
                ],
            },
        ]

        return {
            "headline": "Escalation rationale generated.",
            "sections": sections,
        }

    def explain_approval_required(
        self,
        *,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        action_code = _upper(
            action.get("action")
            or decision.get("action")
        )

        reasons = []

        if decision.get("approval_required"):
            reasons.append("Policy requires human approval before execution.")

        if decision.get("legal_required"):
            reasons.append("Legal or export-control review is required.")

        if decision.get("destructive") or action_code in {
            "WIPE_DEVICE",
            "PURGE_MESSAGE",
            "DISABLE_USER",
            "DELETE_EVIDENCE",
            "MERGE_INVESTIGATIONS",
        }:
            reasons.append("Action is destructive or operationally high-impact.")

        if decision.get("export_control"):
            reasons.append("Export-control/CUI/DFARS indicators are present.")

        if decision.get("risk_score", 0) >= 65:
            reasons.append("Risk score exceeds approval threshold.")

        if action.get("requires_approval"):
            reasons.append("Recommendation explicitly requested approval.")

        required = (
            decision.get("required_approvals")
            or decision.get("policy", {}).get("required_approvals")
            or []
        )

        if not required:
            required = [decision.get("approval_type") or "SOC_LEAD"]

        sections = [
            {
                "title": "Why approval is required",
                "items": reasons or ["Approval required by default governance policy."],
            },
            {
                "title": "Required approval path",
                "items": [str(x) for x in required],
            },
            {
                "title": "Execution status",
                "items": [
                    "Execution should remain paused until an approval grant is issued.",
                    "Approval lineage should be linked to the execution record.",
                ],
            },
        ]

        return {
            "headline": f"Approval required for {action_code}.",
            "sections": sections,
        }

    def explain_autonomous_allowed(
        self,
        *,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        reasons = []

        action_code = _upper(
            action.get("action")
            or decision.get("action")
        )

        if decision.get("allowed") or decision.get("auto_execute"):
            reasons.append("Policy permits autonomous execution.")

        if decision.get("confidence", 0) >= 85:
            reasons.append(f"AI confidence is high ({decision.get('confidence')}).")

        if action_code == "ISOLATE_ENDPOINT" and decision.get("malware_detected"):
            reasons.append("Critical malware containment policy permits endpoint isolation.")

        if not decision.get("approval_required"):
            reasons.append("No approval gate was triggered.")

        if not decision.get("legal_required"):
            reasons.append("No legal-review gate was triggered.")

        targets = decision.get("targets") or {}

        if targets:
            reasons.append("Target count is within blast-radius limits.")

        sections = [
            {
                "title": "Why autonomous execution is allowed",
                "items": reasons or ["Autonomous allowance was derived from policy evaluation."],
            },
            {
                "title": "Safety controls still active",
                "items": [
                    "Execution audit should record a unified execution ID.",
                    "Rollback metadata should be available for reversible actions.",
                    "Realtime operation events should be published.",
                ],
            },
        ]

        return {
            "headline": f"Autonomous execution allowed for {action_code}.",
            "sections": sections,
        }

    def explain_campaign_linkage(
        self,
        *,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        campaign = context.get("campaign") or {}
        linked_cases = context.get("linked_cases") or []
        entities = context.get("entities") or []
        evidence = context.get("evidence") or []

        reasons = []

        if campaign.get("campaign_id"):
            reasons.append(f"Campaign ID assigned: {campaign.get('campaign_id')}.")

        if len(linked_cases) > 0:
            reasons.append(f"{len(linked_cases)} linked case(s) detected.")

        if len(entities) >= 5:
            reasons.append("Multiple overlapping entities exist across the case graph.")

        if self._has_shared_hash_signal(evidence):
            reasons.append("Shared attachment or evidence hash indicators are present.")

        if campaign.get("confidence"):
            reasons.append(f"Campaign confidence: {campaign.get('confidence')}.")

        sections = [
            {
                "title": "Why campaign linkage is suspected",
                "items": reasons or ["No strong campaign linkage indicators were detected."],
            },
            {
                "title": "Recommended analyst validation",
                "items": [
                    "Review shared entities.",
                    "Review attachment hashes.",
                    "Review sender and recipient overlap.",
                    "Review timeline clustering.",
                ],
            },
        ]

        return {
            "headline": "Campaign linkage explanation generated.",
            "sections": sections,
        }

    def explain_policy_block(
        self,
        *,
        decision: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        action: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        action = action or {}

        reasons = list(decision.get("reasoning") or [])

        if not reasons:
            reasons.append("Policy engine blocked execution based on governance defaults.")

        sections = [
            {
                "title": "Why execution was blocked",
                "items": reasons,
            },
            {
                "title": "How to proceed",
                "items": [
                    "Request the required approval.",
                    "Reduce blast radius.",
                    "Use dry-run mode first.",
                    "Attach legal/export review if CUI/ITAR/DFARS indicators are present.",
                ],
            },
        ]

        return {
            "headline": "Execution blocked by policy.",
            "sections": sections,
        }

    def explain_rollback_required(
        self,
        *,
        action: Dict[str, Any],
        decision: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        action_code = _upper(action.get("action"))
        reasons = []

        if action_code in {
            "DISABLE_USER",
            "SUSPEND_USER",
            "ISOLATE_ENDPOINT",
            "REMOTE_LOCK",
            "QUARANTINE_MAILBOX",
        }:
            reasons.append("Action changes operational access or containment state.")

        if action.get("destructive"):
            reasons.append("Action is destructive or disruptive.")

        if not action.get("rollback_action"):
            reasons.append("No rollback action metadata is attached yet.")

        sections = [
            {
                "title": "Why rollback planning is required",
                "items": reasons or ["Rollback planning required by safety guardrails."],
            },
            {
                "title": "Expected rollback metadata",
                "items": [
                    "Original action.",
                    "Reverse action.",
                    "Target identifier.",
                    "Adapter name.",
                    "Execution ID.",
                    "Approval lineage.",
                ],
            },
        ]

        return {
            "headline": f"Rollback plan required for {action_code}.",
            "sections": sections,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _detect_explanation_type(
        self,
        *,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> str:
        if decision.get("approval_required") or decision.get("legal_required"):
            return "APPROVAL_REQUIRED"

        if decision.get("allowed") or decision.get("auto_execute"):
            return "AUTONOMOUS_ALLOWED"

        if decision.get("must_escalate") or _upper(context.get("status")) == "ESCALATED":
            return "ESCALATION"

        if context.get("campaign", {}).get("campaign_id"):
            return "CAMPAIGN_LINKAGE"

        if decision.get("allowed") is False:
            return "POLICY_BLOCK"

        return "GENERAL"

    def _generic_explanation(
        self,
        *,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        action: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        reasons = list(decision.get("reasoning") or [])

        return [
            {
                "title": "Decision summary",
                "items": reasons or ["Decision was evaluated using available policy and context."],
            },
            {
                "title": "Operational context",
                "items": [
                    f"Severity: {context.get('severity', 'UNKNOWN')}",
                    f"Status: {context.get('status', 'UNKNOWN')}",
                    f"Action: {action.get('action') or decision.get('action')}",
                    f"Risk score: {decision.get('risk_score', 'N/A')}",
                ],
            },
        ]

    def _headline(
        self,
        explanation_type: str,
        decision: Dict[str, Any],
        action: Dict[str, Any],
    ) -> str:
        action_code = action.get("action") or decision.get("action") or "action"

        mapping = {
            "APPROVAL_REQUIRED": f"Approval required before {action_code}.",
            "AUTONOMOUS_ALLOWED": f"Autonomous execution allowed for {action_code}.",
            "ESCALATION": "Escalation rationale generated.",
            "CAMPAIGN_LINKAGE": "Campaign linkage explanation generated.",
            "POLICY_BLOCK": f"Policy blocked {action_code}.",
            "GENERAL": f"Decision explanation generated for {action_code}.",
        }

        return mapping.get(explanation_type, "Decision explanation generated.")

    def _summary_from_sections(
        self,
        sections: List[Dict[str, Any]],
    ) -> str:
        parts = []

        for section in sections:
            items = section.get("items") or []
            if items:
                parts.append(str(items[0]))

        return " ".join(parts[:3])

    def _contains_export_control(
        self,
        entities: List[Any],
        context: Dict[str, Any],
    ) -> bool:
        blob = " ".join([
            str(entities),
            str(context),
        ]).upper()

        terms = [
            "ITAR",
            "EAR",
            "EAR99",
            "DFARS",
            "CUI",
            "CTI",
            "EXPORT_CONTROL",
            "USML",
        ]

        return any(term in blob for term in terms)

    def _analyst_workload_saturated(
        self,
        workload: Dict[str, Any],
    ) -> bool:
        items = workload.get("items") or []

        for item in items:
            score = _safe_int(
                item.get("workload_score")
                or item.get("assigned_cases")
                or item.get("case_count"),
                0,
            )

            if score >= 10:
                return True

        return False

    def _has_shared_hash_signal(
        self,
        evidence: List[Dict[str, Any]],
    ) -> bool:
        hashes = []

        for item in evidence:
            value = (
                item.get("sha256")
                or item.get("hash")
                or item.get("content_hash")
            )

            if value:
                hashes.append(value)

        return len(hashes) != len(set(hashes)) if hashes else False