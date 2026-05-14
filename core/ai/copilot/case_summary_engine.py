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


class CaseSummaryEngine:
    """
    AI operational narrative engine.

    Generates:
    - executive summaries
    - analyst summaries
    - escalation summaries
    - legal summaries
    - export-control summaries
    - shift handoff summaries
    """

    def __init__(self, llm_service: Any = None):
        self.llm_service = llm_service

    def generate_summaries(
        self,
        *,
        context: Dict[str, Any],
        reasoning: Optional[Dict[str, Any]] = None,
        next_actions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        reasoning = reasoning or {}
        next_actions = next_actions or {}

        return {
            "case_id": context.get("case_id"),
            "executive_summary": self.executive_summary(context, reasoning, next_actions),
            "analyst_summary": self.analyst_summary(context, reasoning, next_actions),
            "escalation_summary": self.escalation_summary(context, reasoning, next_actions),
            "legal_summary": self.legal_summary(context, reasoning, next_actions),
            "export_control_summary": self.export_control_summary(context, reasoning, next_actions),
            "shift_handoff_summary": self.shift_handoff_summary(context, reasoning, next_actions),
            "generated_at_ms": _now_ms(),
            "engine": "CaseSummaryEngine",
        }

    # ------------------------------------------------------------------
    # Summary Types
    # ------------------------------------------------------------------

    def executive_summary(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
        next_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        title = context.get("title") or f"Case {context.get('case_id')}"
        severity = context.get("severity") or "UNKNOWN"
        status = context.get("status") or "UNKNOWN"
        priority = _safe_int(context.get("operational_priority_score"), 0)

        key_points = []

        if context.get("sla", {}).get("breached"):
            key_points.append("SLA is breached.")

        if context.get("campaign", {}).get("campaign_id"):
            key_points.append("Campaign linkage has been detected.")

        if _safe_int(context.get("blast_radius_score"), 0) >= 70:
            key_points.append("Blast radius is elevated.")

        if reasoning.get("legal_review_reasoning", {}).get("recommended"):
            key_points.append("Legal review is recommended.")

        top_action = (next_actions.get("top_action") or {}).get("label")

        if top_action:
            key_points.append(f"Top recommended action: {top_action}.")

        return {
            "title": title,
            "summary": (
                f"{title} is a {severity} severity investigation currently in "
                f"{status} status with an operational priority score of {priority}."
            ),
            "key_points": key_points,
            "audience": "executive",
        }

    def analyst_summary(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
        next_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        linked_cases = context.get("linked_cases") or []
        entities = context.get("entities") or []
        evidence_count = _safe_int(context.get("evidence_count"), 0)

        actions = next_actions.get("recommended_actions") or []

        return {
            "summary": (
                f"Case {context.get('case_id')} has {evidence_count} evidence item(s), "
                f"{len(entities)} resolved entity/entities, and {len(linked_cases)} linked case(s)."
            ),
            "risk_drivers": self._collect_risk_drivers(context, reasoning),
            "recommended_actions": actions[:5],
            "audience": "analyst",
        }

    def escalation_summary(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
        next_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        escalation = reasoning.get("escalation_reasoning") or {}
        operational = reasoning.get("operational_priority_reasoning") or {}

        return {
            "recommended": bool(escalation.get("recommended")),
            "summary": (
                "Escalation is recommended."
                if escalation.get("recommended")
                else "Escalation is not currently required based on available signals."
            ),
            "reasons": escalation.get("reasons", []),
            "priority_level": operational.get("priority_level"),
            "priority_score": operational.get("priority_score"),
            "audience": "manager",
        }

    def legal_summary(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
        next_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        legal = reasoning.get("legal_review_reasoning") or {}

        legal_actions = [
            a for a in next_actions.get("recommended_actions", [])
            if a.get("category") in {"LEGAL", "EXPORT_CONTROL", "APPROVAL"}
        ]

        return {
            "legal_review_recommended": bool(legal.get("recommended")),
            "summary": (
                "Legal review is recommended due to regulatory, export-control, "
                "campaign, or severity indicators."
                if legal.get("recommended")
                else "No mandatory legal-review trigger was identified from current context."
            ),
            "reasons": legal.get("reasons", []),
            "legal_actions": legal_actions,
            "audience": "legal",
        }

    def export_control_summary(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
        next_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        export = reasoning.get("export_control_reasoning") or {}

        return {
            "detected": bool(export.get("detected")),
            "summary": (
                "Export-control indicators were detected and should be reviewed "
                "before closure, disclosure, or disposition."
                if export.get("detected")
                else "No export-control indicators were identified from current context."
            ),
            "matched_entities": export.get("matched_entities", []),
            "recommendations": export.get("recommendations", []),
            "audience": "export_control",
        }

    def shift_handoff_summary(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
        next_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        top_actions = next_actions.get("recommended_actions", [])[:3]

        live_events = context.get("live_events") or []

        recent_events = [
            {
                "event_type": e.get("event_type"),
                "timestamp_ms": e.get("timestamp_ms"),
                "actor": e.get("actor"),
            }
            for e in live_events[:5]
        ]

        return {
            "summary": (
                f"Case {context.get('case_id')} remains {context.get('status')} "
                f"with severity {context.get('severity')}."
            ),
            "next_actions": top_actions,
            "recent_events": recent_events,
            "handoff_notes": self._build_handoff_notes(context, reasoning),
            "audience": "shift_handoff",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _collect_risk_drivers(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[str]:
        drivers = []

        why = reasoning.get("why_case_matters") or {}
        drivers.extend(why.get("reasons", []))

        operational = reasoning.get("operational_priority_reasoning") or {}
        drivers.extend(operational.get("reasons", []))

        export = reasoning.get("export_control_reasoning") or {}
        if export.get("detected"):
            drivers.append("Export-control indicators detected.")

        campaign = reasoning.get("campaign_reasoning") or {}
        drivers.extend(campaign.get("reasons", []))

        return list(dict.fromkeys(drivers))

    def _build_handoff_notes(
        self,
        context: Dict[str, Any],
        reasoning: Dict[str, Any],
    ) -> List[str]:
        notes = []

        if context.get("sla", {}).get("breached"):
            notes.append("SLA is breached; prioritize immediate review.")

        if context.get("approvals"):
            notes.append("Approval workflow exists; check pending approval state.")

        if context.get("campaign", {}).get("campaign_id"):
            notes.append("Review linked campaign context before taking closure action.")

        if reasoning.get("legal_review_reasoning", {}).get("recommended"):
            notes.append("Legal review recommended before disposition.")

        if not notes:
            notes.append("Continue standard triage and evidence review.")

        return notes