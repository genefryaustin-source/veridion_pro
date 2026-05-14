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


class InvestigationReasoner:
    """
    AI operational reasoning engine.

    Responsibilities:
    - escalation reasoning
    - threat reasoning
    - export-control reasoning
    - insider-risk reasoning
    - campaign reasoning
    - operational priority reasoning
    - blast-radius reasoning
    - legal review reasoning

    Produces:
    - human-readable analyst reasoning
    - operational justifications
    - escalation rationale
    - AI investigation narratives
    """

    def __init__(
        self,
        operational_context_builder: Any = None,
    ):
        self.context_builder = operational_context_builder

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def analyze_case(
        self,
        *,
        context: Optional[Dict[str, Any]] = None,
        case_id: Optional[Any] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build full AI reasoning package for a case.
        """

        if context is None:
            if self.context_builder is None:
                raise ValueError(
                    "context or operational_context_builder required"
                )

            context = self.context_builder.build_case_context(
                case_id=case_id,
                tenant_id=tenant_id,
            )

        escalation = self.build_escalation_reasoning(context)
        threat = self.build_threat_reasoning(context)
        export_control = self.build_export_control_reasoning(context)
        insider = self.build_insider_risk_reasoning(context)
        campaign = self.build_campaign_reasoning(context)
        blast = self.build_blast_radius_reasoning(context)
        operational = self.build_operational_priority_reasoning(context)
        legal = self.build_legal_review_reasoning(context)

        why_case_matters = self.build_why_case_matters(context)

        summary = self._build_summary(
            context=context,
            escalation=escalation,
            threat=threat,
            export_control=export_control,
            insider=insider,
            campaign=campaign,
            blast=blast,
            operational=operational,
            legal=legal,
        )

        return {
            "case_id": context.get("case_id"),
            "severity": context.get("severity"),
            "status": context.get("status"),

            "why_case_matters": why_case_matters,

            "escalation_reasoning": escalation,
            "threat_reasoning": threat,
            "export_control_reasoning": export_control,
            "insider_risk_reasoning": insider,
            "campaign_reasoning": campaign,
            "blast_radius_reasoning": blast,
            "operational_priority_reasoning": operational,
            "legal_review_reasoning": legal,

            "summary": summary,

            "generated_at_ms": _now_ms(),
            "engine": "InvestigationReasoner",
        }

    # ------------------------------------------------------------------
    # Why Case Matters
    # ------------------------------------------------------------------

    def build_why_case_matters(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        reasons = []

        severity = _upper(context.get("severity"))
        status = _upper(context.get("status"))

        if severity == "CRITICAL":
            reasons.append(
                "Case classified as CRITICAL severity."
            )

        if status == "ESCALATED":
            reasons.append(
                "Investigation is currently escalated."
            )

        sla = context.get("sla", {}) or {}

        if sla.get("breached"):
            reasons.append(
                "SLA breach indicates operational urgency."
            )

        campaign = context.get("campaign") or {}

        if campaign.get("campaign_id"):
            reasons.append(
                "Campaign indicators suggest coordinated activity."
            )

        linked_cases = context.get("linked_cases") or []

        if len(linked_cases) >= 3:
            reasons.append(
                f"{len(linked_cases)} linked investigations detected."
            )

        blast_radius = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        if blast_radius >= 70:
            reasons.append(
                "High blast-radius score indicates broad operational impact."
            )

        entities = context.get("entities") or []

        export_terms = [
            "ITAR",
            "EAR",
            "EAR99",
            "EXPORT",
            "USML",
        ]

        if any(
            any(term in _upper(entity) for term in export_terms)
            for entity in entities
        ):
            reasons.append(
                "Export-control indicators detected in entity graph."
            )

        return {
            "reasons": reasons,
            "importance_score": min(
                100,
                len(reasons) * 15
                + _safe_int(
                    context.get("operational_priority_score"),
                    0,
                ) // 2,
            ),
        }

    # ------------------------------------------------------------------
    # Escalation
    # ------------------------------------------------------------------

    def build_escalation_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        rationale = []

        escalation = context.get("escalation") or {}
        severity = _upper(context.get("severity"))

        if escalation.get("is_escalated"):
            rationale.append(
                "Case already escalated within operational workflow."
            )

        if severity == "CRITICAL":
            rationale.append(
                "CRITICAL severity warrants elevated handling."
            )

        sla = context.get("sla") or {}

        if sla.get("breached"):
            rationale.append(
                "SLA breach increases escalation urgency."
            )

        linked_cases = context.get("linked_cases") or []

        if len(linked_cases) >= 5:
            rationale.append(
                "Cross-case linkage volume suggests coordinated activity."
            )

        blast_radius = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        if blast_radius >= 80:
            rationale.append(
                "High blast-radius score supports escalation."
            )

        return {
            "recommended": len(rationale) > 0,
            "confidence": min(100, 50 + len(rationale) * 10),
            "reasons": rationale,
        }

    # ------------------------------------------------------------------
    # Threat
    # ------------------------------------------------------------------

    def build_threat_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        indicators = []

        graph_risk = (
            context.get("graph_risk", {})
            .get("case_risk", {})
        )

        score = _safe_int(
            graph_risk.get("score"),
            0,
        )

        if score >= 80:
            indicators.append(
                "Graph risk score exceeds critical threshold."
            )

        campaign = context.get("campaign") or {}

        if campaign.get("campaign_id"):
            indicators.append(
                "Campaign correlation detected."
            )

        entities = context.get("entities") or []

        suspicious_terms = [
            "CREDENTIAL",
            "EXPORT",
            "ITAR",
            "CLASSIFIED",
            "CONTROLLED",
            "FINANCIAL",
        ]

        for entity in entities:
            if any(
                term in _upper(entity)
                for term in suspicious_terms
            ):
                indicators.append(
                    f"Sensitive entity indicator detected: {entity}"
                )

        return {
            "risk_score": min(
                100,
                40 + len(indicators) * 12,
            ),
            "threat_indicators": indicators,
        }

    # ------------------------------------------------------------------
    # Export Control
    # ------------------------------------------------------------------

    def build_export_control_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        indicators = []

        entities = context.get("entities") or []

        export_terms = [
            "ITAR",
            "EAR",
            "EAR99",
            "USML",
            "EXPORT",
            "DEFENSE",
            "CONTROLLED TECHNICAL INFORMATION",
        ]

        for entity in entities:
            if any(
                term in _upper(entity)
                for term in export_terms
            ):
                indicators.append(entity)

        recommendations = []

        if indicators:
            recommendations.extend([
                "Recommend legal review.",
                "Recommend export-control escalation.",
                "Recommend evidence preservation.",
            ])

        return {
            "detected": len(indicators) > 0,
            "confidence": min(100, len(indicators) * 18),
            "matched_entities": indicators,
            "recommendations": recommendations,
        }

    # ------------------------------------------------------------------
    # Insider Risk
    # ------------------------------------------------------------------

    def build_insider_risk_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        indicators = []

        linked_cases = context.get("linked_cases") or []

        if len(linked_cases) >= 4:
            indicators.append(
                "Repeated cross-case linkage pattern detected."
            )

        campaign = context.get("campaign") or {}

        if campaign.get("campaign_id"):
            indicators.append(
                "Campaign activity may indicate coordinated insider behavior."
            )

        approvals = context.get("approvals") or []

        if len(approvals) >= 3:
            indicators.append(
                "Repeated approval workflow involvement detected."
            )

        return {
            "suspected": len(indicators) >= 2,
            "confidence": min(100, len(indicators) * 20),
            "indicators": indicators,
        }

    # ------------------------------------------------------------------
    # Campaign
    # ------------------------------------------------------------------

    def build_campaign_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        campaign = context.get("campaign") or {}

        rationale = []

        if campaign.get("campaign_id"):
            rationale.append(
                "Campaign identifier assigned."
            )

        linked_cases = context.get("linked_cases") or []

        if len(linked_cases) >= 3:
            rationale.append(
                "Multiple linked investigations detected."
            )

        graph_risk = (
            context.get("graph_risk", {})
            .get("case_risk", {})
        )

        if _safe_int(
            graph_risk.get("cross_case_pivots"),
            0,
        ) >= 5:
            rationale.append(
                "High cross-case pivot count detected."
            )

        return {
            "campaign_detected": len(rationale) > 0,
            "campaign_id": campaign.get("campaign_id"),
            "confidence": min(100, len(rationale) * 22),
            "reasons": rationale,
        }

    # ------------------------------------------------------------------
    # Blast Radius
    # ------------------------------------------------------------------

    def build_blast_radius_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        score = _safe_int(
            context.get("blast_radius_score"),
            0,
        )

        reasons = []

        linked_cases = context.get("linked_cases") or []

        if len(linked_cases) >= 5:
            reasons.append(
                "High linked-case count increases operational spread."
            )

        entities = context.get("entities") or []

        if len(entities) >= 10:
            reasons.append(
                "Large entity footprint detected."
            )

        if score >= 75:
            reasons.append(
                "Blast radius score exceeds high-risk threshold."
            )

        return {
            "blast_radius_score": score,
            "high_impact": score >= 75,
            "reasons": reasons,
        }

    # ------------------------------------------------------------------
    # Operational Priority
    # ------------------------------------------------------------------

    def build_operational_priority_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        score = _safe_int(
            context.get("operational_priority_score"),
            0,
        )

        reasons = []

        if score >= 180:
            reasons.append(
                "Operational priority exceeds critical threshold."
            )

        if context.get("sla", {}).get("breached"):
            reasons.append(
                "SLA breach contributes to operational urgency."
            )

        if _upper(context.get("severity")) == "CRITICAL":
            reasons.append(
                "CRITICAL severity impacts operational priority."
            )

        if context.get("campaign", {}).get("campaign_id"):
            reasons.append(
                "Campaign detection elevates operational priority."
            )

        return {
            "priority_score": score,
            "priority_level": self._priority_level(score),
            "reasons": reasons,
        }

    # ------------------------------------------------------------------
    # Legal Review
    # ------------------------------------------------------------------

    def build_legal_review_reasoning(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:

        export_reasoning = self.build_export_control_reasoning(
            context
        )

        rationale = []

        if export_reasoning.get("detected"):
            rationale.append(
                "Export-control indicators require legal assessment."
            )

        if _upper(context.get("severity")) == "CRITICAL":
            rationale.append(
                "CRITICAL investigation severity may require legal oversight."
            )

        if context.get("campaign", {}).get("campaign_id"):
            rationale.append(
                "Coordinated campaign activity may increase legal exposure."
            )

        return {
            "recommended": len(rationale) > 0,
            "reasons": rationale,
            "confidence": min(100, len(rationale) * 20),
        }

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def _build_summary(
        self,
        *,
        context: Dict[str, Any],
        escalation: Dict[str, Any],
        threat: Dict[str, Any],
        export_control: Dict[str, Any],
        insider: Dict[str, Any],
        campaign: Dict[str, Any],
        blast: Dict[str, Any],
        operational: Dict[str, Any],
        legal: Dict[str, Any],
    ) -> Dict[str, Any]:

        highlights = []

        if escalation.get("recommended"):
            highlights.append(
                "Escalation recommended."
            )

        if export_control.get("detected"):
            highlights.append(
                "Export-control indicators detected."
            )

        if campaign.get("campaign_detected"):
            highlights.append(
                "Campaign linkage suspected."
            )

        if blast.get("high_impact"):
            highlights.append(
                "High blast-radius risk identified."
            )

        if legal.get("recommended"):
            highlights.append(
                "Legal review recommended."
            )

        return {
            "headline":
                f"{context.get('severity')} "
                f"{context.get('status')} "
                f"investigation",

            "highlights": highlights,

            "priority_level":
                operational.get("priority_level"),

            "priority_score":
                operational.get("priority_score"),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _priority_level(
        self,
        score: int,
    ) -> str:

        if score >= 220:
            return "CRITICAL"

        if score >= 150:
            return "HIGH"

        if score >= 80:
            return "MEDIUM"

        return "LOW"