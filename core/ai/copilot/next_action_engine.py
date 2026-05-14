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


class NextActionEngine:
    """
    AI operational next-action engine.

    Produces ranked workflow recommendations using:
    - SLA pressure
    - graph risk
    - campaign intelligence
    - escalation state
    - analyst workload
    - linked investigations
    - entity relationships
    - export-control indicators
    - approvals
    - blast-radius score
    """

    def __init__(
        self,
        playbook_service: Any = None,
        recommendation_engine: Any = None,
    ):
        self.playbook_service = playbook_service
        self.recommendation_engine = recommendation_engine

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def recommend_next_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        reasoning = reasoning or {}

        actions: List[Dict[str, Any]] = []

        actions.extend(
            self._escalation_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._legal_review_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._endpoint_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._playbook_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._reassignment_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._merge_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._evidence_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions.extend(
            self._approval_actions(
                context=context,
                reasoning=reasoning,
            )
        )

        actions = self._dedupe_actions(actions)
        actions = self._rank_actions(actions)

        return {
            "case_id": context.get("case_id"),
            "recommended_actions": actions,
            "top_action": actions[0] if actions else None,
            "action_count": len(actions),
            "generated_at_ms": _now_ms(),
            "engine": "NextActionEngine",
        }

    # ------------------------------------------------------------------
    # Action Families
    # ------------------------------------------------------------------

    def _escalation_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        severity = _upper(context.get("severity"))
        sla = context.get("sla") or {}
        campaign = context.get("campaign") or {}
        escalation = context.get("escalation") or {}

        blast_radius = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        linked_cases = context.get("linked_cases") or []

        already_escalated = bool(
            escalation.get("is_escalated")
        )

        should_escalate = (
            severity == "CRITICAL"
            or sla.get("breached")
            or campaign.get("campaign_id")
            or blast_radius >= 75
            or len(linked_cases) >= 5
        )

        if should_escalate and not already_escalated:
            actions.append(
                self._make_action(
                    action="ESCALATE_CASE",
                    label="Escalate Investigation",
                    priority="CRITICAL" if severity == "CRITICAL" or sla.get("breached") else "HIGH",
                    confidence=94,
                    reason="Severity, SLA pressure, campaign linkage, blast radius, or cross-case pivots support escalation.",
                    category="ESCALATION",
                    requires_approval=False,
                )
            )

        if sla.get("breached"):
            actions.append(
                self._make_action(
                    action="INCREASE_SLA_PRIORITY",
                    label="Increase SLA Priority",
                    priority="HIGH",
                    confidence=90,
                    reason="SLA breach detected.",
                    category="SLA",
                )
            )

        return actions

    def _legal_review_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        export_reasoning = (
            reasoning.get("export_control_reasoning")
            or {}
        )

        legal_reasoning = (
            reasoning.get("legal_review_reasoning")
            or {}
        )

        entities = context.get("entities") or []

        export_terms = {
            "ITAR",
            "EAR",
            "EAR99",
            "USML",
            "EXPORT",
            "EXPORT_CONTROL",
            "CTI",
            "CONTROLLED",
            "DEFENSE",
        }

        export_detected = (
            export_reasoning.get("detected")
            or any(
                any(term in _upper(entity) for term in export_terms)
                for entity in entities
            )
        )

        if export_detected:
            actions.append(
                self._make_action(
                    action="REQUEST_LEGAL_REVIEW",
                    label="Request Legal Review",
                    priority="CRITICAL",
                    confidence=95,
                    reason="Export-control or controlled technical data indicators detected.",
                    category="LEGAL",
                    requires_approval=True,
                    approval_type="LEGAL_REVIEW",
                )
            )

            actions.append(
                self._make_action(
                    action="REQUEST_EXPORT_REVIEW",
                    label="Request Export-Control Review",
                    priority="CRITICAL",
                    confidence=96,
                    reason="ITAR/EAR/export-control indicators require export review.",
                    category="EXPORT_CONTROL",
                    requires_approval=True,
                    approval_type="EXPORT_CONTROL_REVIEW",
                )
            )

        elif legal_reasoning.get("recommended"):
            actions.append(
                self._make_action(
                    action="REQUEST_LEGAL_REVIEW",
                    label="Request Legal Review",
                    priority="HIGH",
                    confidence=_safe_int(
                        legal_reasoning.get("confidence"),
                        75,
                    ),
                    reason="Legal reasoning engine recommends review.",
                    category="LEGAL",
                    requires_approval=True,
                    approval_type="LEGAL_REVIEW",
                )
            )

        return actions

    def _endpoint_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        insider_reasoning = (
            reasoning.get("insider_risk_reasoning")
            or {}
        )

        campaign = context.get("campaign") or {}

        entities = context.get("entities") or []

        endpoint_terms = {
            "USB",
            "MASS_DOWNLOAD",
            "PERSONAL_EMAIL",
            "CREDENTIAL",
            "TOKEN",
            "PASSWORD",
            "API_KEY",
            "SECRET",
        }

        endpoint_signal = (
            insider_reasoning.get("suspected")
            or campaign.get("campaign_id")
            or any(
                any(term in _upper(entity) for term in endpoint_terms)
                for entity in entities
            )
        )

        if endpoint_signal:
            actions.append(
                self._make_action(
                    action="REQUEST_ENDPOINT_SCAN",
                    label="Launch Endpoint Scan",
                    priority="HIGH",
                    confidence=86,
                    reason="Insider-risk, credential, campaign, or endpoint-related indicators detected.",
                    category="ENDPOINT",
                )
            )

            actions.append(
                self._make_action(
                    action="INITIATE_CONTAINMENT_REVIEW",
                    label="Initiate Containment Review",
                    priority="HIGH",
                    confidence=82,
                    reason="Potential user/device containment decision may be required.",
                    category="CONTAINMENT",
                    requires_approval=True,
                    approval_type="CONTAINMENT_APPROVAL",
                )
            )

        return actions

    def _playbook_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        playbooks = context.get("playbooks") or []

        for playbook in playbooks:
            playbook_name = (
                playbook.get("playbook_name")
                or playbook.get("name")
            )

            if not playbook_name:
                continue

            actions.append(
                self._make_action(
                    action="EXECUTE_PLAYBOOK",
                    label=f"Execute Playbook: {playbook.get('name') or playbook_name}",
                    priority=playbook.get("severity") or "HIGH",
                    confidence=88,
                    reason=f"Matched investigation playbook: {playbook.get('name') or playbook_name}.",
                    category="PLAYBOOK",
                    playbook=playbook_name,
                    requires_approval=False,
                )
            )

        recommendations = context.get("recommendations") or []

        for rec in recommendations:
            playbook = rec.get("playbook")

            if not playbook:
                continue

            playbook_name = (
                playbook.get("playbook_name")
                or playbook.get("name")
            )

            if playbook_name:
                actions.append(
                    self._make_action(
                        action="EXECUTE_PLAYBOOK",
                        label=f"Execute Playbook: {playbook.get('name') or playbook_name}",
                        priority=rec.get("priority") or "HIGH",
                        confidence=84,
                        reason=rec.get("reason") or "Recommendation includes playbook.",
                        category="PLAYBOOK",
                        playbook=playbook_name,
                    )
                )

        return actions

    def _reassignment_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        owner = context.get("owner")
        severity = _upper(context.get("severity"))
        sla = context.get("sla") or {}

        if not owner:
            actions.append(
                self._make_action(
                    action="ASSIGN_ANALYST",
                    label="Assign Analyst",
                    priority="HIGH" if severity in {"CRITICAL", "HIGH"} else "MEDIUM",
                    confidence=92,
                    reason="Case is currently unassigned.",
                    category="ROUTING",
                )
            )

        if severity == "CRITICAL" or sla.get("breached"):
            actions.append(
                self._make_action(
                    action="REASSIGN_TIER_3",
                    label="Reassign to Tier-3 Analyst",
                    priority="HIGH",
                    confidence=84,
                    reason="Critical severity or SLA pressure suggests senior analyst handling.",
                    category="ROUTING",
                )
            )

        workload = context.get("analyst_workload") or {}
        workload_items = workload.get("items") or []

        overloaded_owner = False

        for item in workload_items:
            analyst = (
                item.get("analyst")
                or item.get("owner")
                or item.get("username")
            )

            if str(analyst) == str(owner):
                workload_score = _safe_int(
                    item.get("workload_score")
                    or item.get("assigned_cases")
                    or item.get("case_count"),
                    0,
                )

                if workload_score >= 10:
                    overloaded_owner = True

        if owner and overloaded_owner:
            actions.append(
                self._make_action(
                    action="REBALANCE_ASSIGNMENT",
                    label="Rebalance Analyst Assignment",
                    priority="MEDIUM",
                    confidence=76,
                    reason="Assigned analyst appears overloaded.",
                    category="ROUTING",
                )
            )

        return actions

    def _merge_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        linked_cases = context.get("linked_cases") or []
        campaign = context.get("campaign") or {}

        strong_links = [
            c for c in linked_cases
            if _safe_int(c.get("score"), 0) >= 75
        ]

        if len(strong_links) >= 1:
            actions.append(
                self._make_action(
                    action="LINK_RELATED_CASES",
                    label="Link Related Investigations",
                    priority="HIGH",
                    confidence=88,
                    reason="Strong cross-case relationship detected.",
                    category="GRAPH",
                )
            )

        if len(strong_links) >= 2 or campaign.get("campaign_id"):
            actions.append(
                self._make_action(
                    action="MERGE_INVESTIGATIONS",
                    label="Merge Linked Investigations",
                    priority="HIGH",
                    confidence=82,
                    reason="Campaign clustering or multiple strong linked cases detected.",
                    category="GRAPH",
                    requires_approval=True,
                    approval_type="CASE_MERGE_APPROVAL",
                )
            )

        return actions

    def _evidence_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        evidence_count = _safe_int(
            context.get("evidence_count"),
            0,
        )

        blast_radius = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        severity = _upper(context.get("severity"))

        if evidence_count == 0:
            actions.append(
                self._make_action(
                    action="ATTACH_SUPPORTING_EVIDENCE",
                    label="Attach Supporting Evidence",
                    priority="MEDIUM",
                    confidence=80,
                    reason="No evidence is currently attached to this case.",
                    category="EVIDENCE",
                )
            )

        if blast_radius >= 70 or severity == "CRITICAL":
            actions.append(
                self._make_action(
                    action="PRESERVE_EVIDENCE",
                    label="Preserve Evidence",
                    priority="HIGH" if severity != "CRITICAL" else "CRITICAL",
                    confidence=90,
                    reason="High impact or critical investigation requires evidence preservation.",
                    category="EVIDENCE",
                )
            )

        if evidence_count >= 10:
            actions.append(
                self._make_action(
                    action="CLUSTER_EVIDENCE",
                    label="Cluster Related Evidence",
                    priority="MEDIUM",
                    confidence=75,
                    reason="Large evidence volume may benefit from clustering.",
                    category="EVIDENCE",
                )
            )

        return actions

    def _approval_actions(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        status = _upper(context.get("status"))
        approvals = context.get("approvals") or []

        pending_approvals = [
            a for a in approvals
            if _upper(a.get("status")) in {"PENDING", "OPEN", "REQUESTED"}
        ]

        if status == "RESOLVED" and not pending_approvals:
            actions.append(
                self._make_action(
                    action="REQUEST_CLOSURE_APPROVAL",
                    label="Request Closure Approval",
                    priority="MEDIUM",
                    confidence=86,
                    reason="Resolved case should receive closure approval before closing.",
                    category="APPROVAL",
                    requires_approval=True,
                    approval_type="CLOSURE_APPROVAL",
                )
            )

        if pending_approvals:
            actions.append(
                self._make_action(
                    action="REVIEW_PENDING_APPROVALS",
                    label="Review Pending Approvals",
                    priority="MEDIUM",
                    confidence=80,
                    reason=f"{len(pending_approvals)} pending approval request(s) found.",
                    category="APPROVAL",
                )
            )

        return actions

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_action(
        self,
        *,
        action: str,
        label: str,
        priority: str,
        confidence: int,
        reason: str,
        category: str,
        requires_approval: bool = False,
        approval_type: Optional[str] = None,
        playbook: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "action": action,
            "label": label,
            "priority": priority,
            "confidence": confidence,
            "reason": reason,
            "category": category,
            "requires_approval": requires_approval,
            "approval_type": approval_type,
            "playbook": playbook,
            "generated_at_ms": _now_ms(),
            "engine": "NextActionEngine",
        }

    def _dedupe_actions(
        self,
        actions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        seen = set()
        out = []

        for action in actions:
            key = (
                action.get("action"),
                action.get("approval_type"),
                action.get("playbook"),
            )

            if key in seen:
                continue

            seen.add(key)
            out.append(action)

        return out

    def _rank_actions(
        self,
        actions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        priority_rank = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        return sorted(
            actions,
            key=lambda a: (
                priority_rank.get(
                    _upper(a.get("priority")),
                    0,
                ),
                _safe_int(a.get("confidence"), 0),
            ),
            reverse=True,
        )
    