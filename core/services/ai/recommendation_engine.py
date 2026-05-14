from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_upper(value: Any) -> str:
    return str(value or "").upper().strip()


class RecommendationEngine:
    """
    Rules-first AI recommendation engine.

    Converts investigation intelligence into operational actions.

    Future-ready for:
    - Ollama local LLM summaries
    - playbook automation
    - analyst copilot prompts
    - SOAR-style remediation
    """

    def __init__(
        self,
        ledger: Any = None,
        playbook_service: Any = None,
        llm_service: Any = None,
    ):
        self.ledger = ledger
        self.playbook_service = playbook_service
        self.llm_service = llm_service

    def recommend_actions(
        self,
        *,
        case: Dict[str, Any],
        evidence: Optional[List[Dict[str, Any]]] = None,
        entities: Optional[List[str]] = None,
        linked_cases: Optional[List[Dict[str, Any]]] = None,
        campaign: Optional[Dict[str, Any]] = None,
        graph_risk_score: int = 0,
        blast_radius_score: int = 0,
        insider_indicators: Optional[List[Dict[str, Any]]] = None,
        export_control: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:

        evidence = evidence or []
        entities = entities or []
        linked_cases = linked_cases or []
        campaign = campaign or {}
        insider_indicators = insider_indicators or []
        export_control = export_control or {}

        recommendations: List[Dict[str, Any]] = []

        recommendations.extend(
            self._export_control_recommendations(
                export_control=export_control,
            )
        )

        recommendations.extend(
            self._insider_threat_recommendations(
                insider_indicators=insider_indicators,
            )
        )

        recommendations.extend(
            self._graph_recommendations(
                linked_cases=linked_cases,
                graph_risk_score=graph_risk_score,
                blast_radius_score=blast_radius_score,
                campaign=campaign,
            )
        )

        recommendations.extend(
            self._workflow_recommendations(
                case=case,
                evidence=evidence,
            )
        )

        recommendations.extend(
            self._evidence_recommendations(
                evidence=evidence,
                blast_radius_score=blast_radius_score,
            )
        )

        recommendations = self._dedupe_recommendations(recommendations)

        recommendations = self._rank_recommendations(recommendations)

        if self.playbook_service is not None:
            recommendations = self._attach_playbooks(
                recommendations=recommendations,
                case=case,
                entities=entities,
            )

        if not recommendations:
            recommendations.append(
                self._make_action(
                    action="Continue Triage",
                    priority="MEDIUM",
                    reason="No critical automated triggers detected",
                    category="TRIAGE",
                )
            )

        return recommendations

    def summarize_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        critical = [
            r for r in recommendations
            if _safe_upper(r.get("priority")) == "CRITICAL"
        ]

        high = [
            r for r in recommendations
            if _safe_upper(r.get("priority")) == "HIGH"
        ]

        return {
            "total": len(recommendations),
            "critical": len(critical),
            "high": len(high),
            "top_action": recommendations[0] if recommendations else None,
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Recommendation Families
    # ------------------------------------------------------------------

    def _export_control_recommendations(
        self,
        *,
        export_control: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        if not export_control.get("has_export_control_risk"):
            return []

        markers = export_control.get("markers") or []

        return [
            self._make_action(
                action="Request Export Review",
                priority="CRITICAL",
                reason=f"Export-control indicators detected: {', '.join(markers) or 'controlled data markers'}",
                category="EXPORT_CONTROL",
                requires_approval=True,
                approval_type="EXPORT_CONTROL_REVIEW",
            ),
            self._make_action(
                action="Escalate to Legal",
                priority="CRITICAL",
                reason="Controlled technical data or export-control indicators require legal review",
                category="LEGAL",
                requires_approval=True,
                approval_type="LEGAL_REVIEW",
            ),
            self._make_action(
                action="Initiate Evidence Preservation",
                priority="CRITICAL",
                reason="Preserve chain of custody before disposition or external disclosure",
                category="EVIDENCE",
            ),
        ]

    def _insider_threat_recommendations(
        self,
        *,
        insider_indicators: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        if not insider_indicators:
            return []

        actions = [
            self._make_action(
                action="Request Endpoint Scan",
                priority="HIGH",
                reason="Insider-threat indicators detected",
                category="ENDPOINT",
            ),
            self._make_action(
                action="Contain User",
                priority="HIGH",
                reason="Potential insider-risk behavior requires access review",
                category="CONTAINMENT",
                requires_approval=True,
                approval_type="CONTAINMENT_APPROVAL",
            ),
            self._make_action(
                action="Assign Tier-3 Analyst",
                priority="HIGH",
                reason="Insider-risk indicators should be reviewed by senior analyst",
                category="ROUTING",
            ),
        ]

        return actions

    def _graph_recommendations(
        self,
        *,
        linked_cases: List[Dict[str, Any]],
        graph_risk_score: int,
        blast_radius_score: int,
        campaign: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        actions = []

        if graph_risk_score >= 75:
            actions.append(
                self._make_action(
                    action="Assign Tier-3 Analyst",
                    priority="HIGH",
                    reason=f"High graph risk score: {graph_risk_score}",
                    category="ROUTING",
                )
            )

        if len(linked_cases) >= 2:
            actions.append(
                self._make_action(
                    action="Merge With Related Investigation",
                    priority="HIGH",
                    reason=f"{len(linked_cases)} linked investigations detected",
                    category="GRAPH",
                )
            )

        if campaign.get("campaign_id"):
            actions.append(
                self._make_action(
                    action="Open Campaign-Level Investigation",
                    priority="HIGH",
                    reason=f"Campaign pattern detected: {campaign.get('campaign_id')}",
                    category="CAMPAIGN",
                )
            )

        if blast_radius_score >= 70:
            actions.append(
                self._make_action(
                    action="Run Blast Radius Review",
                    priority="HIGH",
                    reason=f"High blast-radius score: {blast_radius_score}",
                    category="GRAPH",
                )
            )

        return actions

    def _workflow_recommendations(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        actions = []

        status = _safe_upper(case.get("status"))
        severity = _safe_upper(case.get("severity") or case.get("priority"))
        assigned = case.get("assigned_to") or case.get("owner")

        if not assigned:
            actions.append(
                self._make_action(
                    action="Assign Analyst",
                    priority="HIGH" if severity in ["CRITICAL", "HIGH"] else "MEDIUM",
                    reason="Case is currently unassigned",
                    category="ROUTING",
                )
            )

        if severity == "CRITICAL" and status in ["NEW", "TRIAGE"]:
            actions.append(
                self._make_action(
                    action="Escalate Case",
                    priority="CRITICAL",
                    reason="Critical investigation is still in early workflow state",
                    category="ESCALATION",
                )
            )

        if status == "RESOLVED":
            actions.append(
                self._make_action(
                    action="Request Closure Approval",
                    priority="MEDIUM",
                    reason="Resolved cases should be reviewed before closure",
                    category="APPROVAL",
                    requires_approval=True,
                    approval_type="CLOSURE_APPROVAL",
                )
            )

        if not evidence:
            actions.append(
                self._make_action(
                    action="Attach Supporting Evidence",
                    priority="MEDIUM",
                    reason="No case evidence found",
                    category="EVIDENCE",
                )
            )

        return actions

    def _evidence_recommendations(
        self,
        *,
        evidence: List[Dict[str, Any]],
        blast_radius_score: int,
    ) -> List[Dict[str, Any]]:

        actions = []

        if len(evidence) >= 10:
            actions.append(
                self._make_action(
                    action="Run Evidence Clustering",
                    priority="MEDIUM",
                    reason=f"{len(evidence)} evidence items attached",
                    category="EVIDENCE",
                )
            )

        if blast_radius_score >= 70:
            actions.append(
                self._make_action(
                    action="Initiate Evidence Preservation",
                    priority="HIGH",
                    reason="High blast radius requires preservation review",
                    category="EVIDENCE",
                )
            )

        return actions

    # ------------------------------------------------------------------
    # Playbook Attachment
    # ------------------------------------------------------------------

    def _attach_playbooks(
        self,
        *,
        recommendations: List[Dict[str, Any]],
        case: Dict[str, Any],
        entities: List[str],
    ) -> List[Dict[str, Any]]:

        for recommendation in recommendations:
            try:
                playbook = self.playbook_service.find_playbook_for_action(
                    action=recommendation.get("action"),
                    case=case,
                    entities=entities,
                )
                if playbook:
                    recommendation["playbook"] = playbook
            except Exception:
                pass

        return recommendations

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_action(
        self,
        *,
        action: str,
        priority: str,
        reason: str,
        category: str,
        requires_approval: bool = False,
        approval_type: Optional[str] = None,
    ) -> Dict[str, Any]:

        return {
            "action": action,
            "priority": priority,
            "reason": reason,
            "category": category,
            "requires_approval": requires_approval,
            "approval_type": approval_type,
            "generated_at_ms": _now_ms(),
            "engine": "RecommendationEngine",
        }

    def _dedupe_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        seen = set()
        output = []

        for rec in recommendations:
            key = (
                rec.get("action"),
                rec.get("category"),
                rec.get("approval_type"),
            )

            if key in seen:
                continue

            seen.add(key)
            output.append(rec)

        return output

    def _rank_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        rank = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }

        return sorted(
            recommendations,
            key=lambda r: rank.get(_safe_upper(r.get("priority")), 0),
            reverse=True,
        )