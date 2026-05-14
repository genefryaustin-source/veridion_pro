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


def _safe_upper(value: Any) -> str:
    return str(value or "").upper().strip()


class OperationalContextBuilder:
    """
    AI operational context aggregation layer.

    Builds the complete case context needed by:
    - investigation reasoner
    - next action engine
    - case summary engine
    - copilot service
    - analyst copilot UI

    Aggregates:
    - case state
    - SLA pressure
    - graph intelligence
    - campaign detection
    - entity pivots
    - analyst workload
    - escalation state
    - approvals
    - playbooks
    - recommendations
    - live events
    - operational priority
    """

    def __init__(
        self,
        ledger: Any,
        sla_service: Any = None,
        graph_service: Any = None,
        graph_risk_service: Any = None,
        case_intelligence_service: Any = None,
        campaign_service: Any = None,
        entity_resolution_service: Any = None,
        recommendation_engine: Any = None,
        playbook_service: Any = None,
        approval_service: Any = None,
        assignment_service: Any = None,
        escalation_service: Any = None,
        event_broadcaster: Any = None,
    ):
        self.ledger = ledger
        self.sla_service = sla_service
        self.graph_service = graph_service
        self.graph_risk_service = graph_risk_service
        self.case_intelligence_service = case_intelligence_service
        self.campaign_service = campaign_service
        self.entity_resolution_service = entity_resolution_service
        self.recommendation_engine = recommendation_engine
        self.playbook_service = playbook_service
        self.approval_service = approval_service
        self.assignment_service = assignment_service
        self.escalation_service = escalation_service
        self.event_broadcaster = event_broadcaster

    # ------------------------------------------------------------------
    # Main API
    # ------------------------------------------------------------------

    def build_case_context(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        case = self._get_case(case_id)
        evidence = self._get_case_evidence(case_id)

        graph_risk = self._get_graph_risk(
            case_id=case_id,
            case=case,
        )

        sla = self._get_sla(
            case=case,
            graph_risk=graph_risk,
        )

        graph = self._get_graph(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        entities = self._get_entities(
            case=case,
            evidence=evidence,
            graph=graph,
        )

        entity_summary = self._get_entity_summary(
            entities=entities,
        )

        linked_cases = self._get_linked_cases(
            case_id=case_id,
            entities=entities,
            evidence=evidence,
            tenant_id=tenant_id,
        )

        campaign = self._get_campaign(
            case=case,
            evidence=evidence,
            entities=entities,
            linked_cases=linked_cases,
            tenant_id=tenant_id,
        )

        case_intelligence = self._get_case_intelligence(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        recommendations = self._get_recommendations(
            case=case,
            evidence=evidence,
            entities=entities,
            linked_cases=linked_cases,
            campaign=campaign,
            graph_risk=graph_risk,
            case_intelligence=case_intelligence,
        )

        playbooks = self._get_playbooks(
            case=case,
            entities=entities,
            campaign=campaign,
            recommendations=recommendations,
        )

        approvals = self._get_approvals(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        analyst_workload = self._get_analyst_workload(
            tenant_id=tenant_id,
        )

        escalation = self._get_escalation_context(
            case=case,
            case_id=case_id,
        )

        live_events = self._get_live_events(
            case_id=case_id,
            tenant_id=tenant_id,
        )

        operational_priority_score = self._calculate_operational_priority_score(
            case=case,
            sla=sla,
            graph_risk=graph_risk,
            linked_cases=linked_cases,
            campaign=campaign,
            case_intelligence=case_intelligence,
            approvals=approvals,
            escalation=escalation,
        )

        severity = (
            case_intelligence.get("export_control", {}).get("recommended_severity")
            or case.get("severity")
            or case.get("priority")
            or graph_risk.get("case_risk", {}).get("severity")
            or "UNKNOWN"
        )

        context = {
            "case_id": case_id,
            "tenant_id": tenant_id or case.get("tenant_id"),
            "title": case.get("title") or f"Case {case_id}",
            "status": case.get("status") or "UNKNOWN",
            "severity": _safe_upper(severity),
            "owner": case.get("owner") or case.get("assigned_to"),
            "case": case,
            "evidence": evidence,
            "evidence_count": len(evidence),

            "sla": sla,
            "graph_risk": graph_risk,
            "graph": graph,

            "entities": entities,
            "entity_summary": entity_summary,
            "linked_cases": linked_cases,
            "cross_case_links": len(linked_cases),

            "campaign": campaign,
            "campaigns": [campaign] if campaign.get("campaign_id") else [],

            "case_intelligence": case_intelligence,
            "blast_radius_score": (
                case_intelligence.get("blast_radius_score")
                or 0
            ),

            "approvals": approvals,
            "analyst_workload": analyst_workload,
            "escalation": escalation,

            "playbooks": playbooks,
            "recommendations": recommendations,
            "live_events": live_events,

            "operational_priority_score": operational_priority_score,
            "generated_at_ms": _now_ms(),
            "builder": "OperationalContextBuilder",
        }

        return context

    def build_queue_context(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        cases = self._get_cases(tenant_id=tenant_id)

        enriched_cases = []

        for case in cases[:limit]:
            case_id = case.get("case_id") or case.get("id")

            if not case_id:
                continue

            try:
                enriched_cases.append(
                    self.build_case_context(
                        case_id=case_id,
                        tenant_id=tenant_id,
                    )
                )
            except Exception:
                enriched_cases.append({
                    "case_id": case_id,
                    "case": case,
                    "error": "context_build_failed",
                })

        return {
            "tenant_id": tenant_id,
            "case_count": len(enriched_cases),
            "cases": enriched_cases,
            "generated_at_ms": _now_ms(),
        }

    # ------------------------------------------------------------------
    # Case / Evidence
    # ------------------------------------------------------------------

    def _get_case(self, case_id: Any) -> Dict[str, Any]:
        for method_name in [
            "get_case",
            "get_case_by_id",
            "fetch_case",
            "read_case",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    result = method(case_id)
                    if result:
                        return dict(result)
                except Exception:
                    pass

        # SQLite fallback
        try:
            with self.ledger._connect() as con:
                row = con.execute(
                    "SELECT * FROM cases WHERE id = ? OR case_id = ? LIMIT 1",
                    (case_id, case_id),
                ).fetchone()

                if row:
                    return dict(row)
        except Exception:
            pass

        return {
            "case_id": case_id,
            "title": f"Case {case_id}",
            "status": "UNKNOWN",
        }

    def _get_case_evidence(self, case_id: Any) -> List[Dict[str, Any]]:
        for method_name in [
            "get_case_evidence",
            "list_case_evidence",
            "fetch_case_evidence",
        ]:
            method = getattr(self.ledger, method_name, None)

            if callable(method):
                try:
                    result = method(case_id)
                    if result:
                        return [dict(r) for r in result]
                except Exception:
                    pass

        try:
            with self.ledger._connect() as con:
                rows = con.execute(
                    """
                    SELECT er.*
                    FROM case_evidence ce
                    JOIN evidence_records er
                        ON er.evidence_id = ce.evidence_id
                        OR er.id = ce.evidence_id
                    WHERE ce.case_id = ?
                    """,
                    (case_id,),
                ).fetchall()

                return [dict(r) for r in rows]
        except Exception:
            return []

    def _get_cases(
        self,
        tenant_id: Optional[str] = None,
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
                        return [dict(r) for r in method(tenant_id=tenant_id)]
                    return [dict(r) for r in method()]
                except TypeError:
                    try:
                        return [dict(r) for r in method(tenant_id)]
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
                        """,
                        (tenant_id,),
                    ).fetchall()
                else:
                    rows = con.execute(
                        """
                        SELECT *
                        FROM cases
                        ORDER BY created_at_ms DESC
                        """
                    ).fetchall()

                return [dict(r) for r in rows]
        except Exception:
            return []

    # ------------------------------------------------------------------
    # SLA
    # ------------------------------------------------------------------

    def _get_sla(
        self,
        *,
        case: Dict[str, Any],
        graph_risk: Dict[str, Any],
    ) -> Dict[str, Any]:
        if self.sla_service is not None:
            for method_name in [
                "calculate_case_sla",
                "get_case_sla",
            ]:
                method = getattr(self.sla_service, method_name, None)

                if callable(method):
                    try:
                        return method(case=case, graph_risk=graph_risk)
                    except TypeError:
                        try:
                            return method(case, graph_risk)
                        except Exception:
                            pass
                    except Exception:
                        pass

        return {
            "breached": bool(case.get("sla_breached")),
            "remaining_minutes": case.get("sla_remaining_minutes"),
            "overdue_minutes": case.get("sla_overdue_minutes"),
            "due_at_ms": case.get("sla_due_at_ms") or case.get("sla_deadline_ms"),
        }

    # ------------------------------------------------------------------
    # Graph
    # ------------------------------------------------------------------

    def _get_graph_risk(
        self,
        *,
        case_id: Any,
        case: Dict[str, Any],
    ) -> Dict[str, Any]:
        if self.graph_risk_service is not None:
            method = getattr(self.graph_risk_service, "analyze_case_graph", None)
            if callable(method):
                try:
                    return method(case_id)
                except Exception:
                    pass

        return {
            "case_risk": {
                "score": _safe_int(case.get("graph_risk_score"), 0),
                "severity": case.get("severity") or case.get("priority") or "UNKNOWN",
                "reasons": [],
                "cross_case_pivots": _safe_int(case.get("cross_case_links"), 0),
                "relationship_count": _safe_int(case.get("relationship_count"), 0),
            }
        }

    def _get_graph(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.graph_service is not None:
            for method_name in [
                "build_case_graph",
                "summarize_graph",
            ]:
                method = getattr(self.graph_service, method_name, None)

                if callable(method):
                    try:
                        return method(case_id=case_id, tenant_id=tenant_id)
                    except TypeError:
                        try:
                            return method(case_id)
                        except Exception:
                            pass
                    except Exception:
                        pass

        return {}

    def _get_linked_cases(
        self,
        *,
        case_id: Any,
        entities: List[str],
        evidence: List[Dict[str, Any]],
        tenant_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        if self.graph_service is not None:
            method = getattr(self.graph_service, "find_linked_cases", None)
            if callable(method):
                try:
                    return method(
                        case_id=case_id,
                        entities=entities,
                        evidence=evidence,
                        tenant_id=tenant_id,
                    )
                except TypeError:
                    try:
                        return method(case_id)
                    except Exception:
                        pass
                except Exception:
                    pass

        return []

    # ------------------------------------------------------------------
    # Entities
    # ------------------------------------------------------------------

    def _get_entities(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        graph: Dict[str, Any],
    ) -> List[str]:
        raw = []

        for field in [
            "entities",
            "related_entities",
            "detected_entities",
            "tags",
            "categories",
            "flags",
        ]:
            value = case.get(field)
            if isinstance(value, list):
                raw.extend(value)

        for ev in evidence:
            for field in [
                "entities",
                "detected_entities",
                "tags",
                "categories",
                "flags",
            ]:
                value = ev.get(field)
                if isinstance(value, list):
                    raw.extend(value)

        for entity in graph.get("entities", []) or []:
            raw.append(entity)

        cleaned = []

        for item in raw:
            if item is None:
                continue

            if isinstance(item, dict):
                value = (
                    item.get("name")
                    or item.get("value")
                    or item.get("label")
                    or item.get("entity")
                )
            else:
                value = str(item)

            if value:
                cleaned.append(value)

        if self.entity_resolution_service is not None:
            for method_name in [
                "resolve_entities",
                "normalize_entities",
                "dedupe_entities",
            ]:
                method = getattr(self.entity_resolution_service, method_name, None)

                if callable(method):
                    try:
                        return method(cleaned)
                    except Exception:
                        pass

        return sorted(list(set(cleaned)))

    def _get_entity_summary(
        self,
        *,
        entities: List[str],
    ) -> Dict[str, Any]:
        if self.entity_resolution_service is not None:
            method = getattr(self.entity_resolution_service, "summarize_entities", None)
            if callable(method):
                try:
                    return method(entities)
                except Exception:
                    pass

        return {
            "total_entities": len(entities),
            "entities": entities,
        }

    # ------------------------------------------------------------------
    # Campaign
    # ------------------------------------------------------------------

    def _get_campaign(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        entities: List[str],
        linked_cases: List[Dict[str, Any]],
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.campaign_service is not None:
            for method_name in [
                "detect_campaign",
                "analyze_campaign",
                "find_campaign",
            ]:
                method = getattr(self.campaign_service, method_name, None)

                if callable(method):
                    try:
                        return method(
                            case=case,
                            evidence=evidence,
                            entities=entities,
                            linked_cases=linked_cases,
                            tenant_id=tenant_id,
                        )
                    except Exception:
                        pass

        return {
            "campaign_id": None,
            "confidence": 0,
            "linked_case_count": len(linked_cases),
        }

    # ------------------------------------------------------------------
    # Intelligence
    # ------------------------------------------------------------------

    def _get_case_intelligence(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.case_intelligence_service is not None:
            method = getattr(self.case_intelligence_service, "analyze_case", None)
            if callable(method):
                try:
                    return method(case_id=case_id, tenant_id=tenant_id)
                except TypeError:
                    try:
                        return method(case_id)
                    except Exception:
                        pass
                except Exception:
                    pass

        return {}

    # ------------------------------------------------------------------
    # Recommendations / Playbooks
    # ------------------------------------------------------------------

    def _get_recommendations(
        self,
        *,
        case: Dict[str, Any],
        evidence: List[Dict[str, Any]],
        entities: List[str],
        linked_cases: List[Dict[str, Any]],
        campaign: Dict[str, Any],
        graph_risk: Dict[str, Any],
        case_intelligence: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if case_intelligence.get("recommended_actions"):
            return case_intelligence.get("recommended_actions") or []

        if self.recommendation_engine is not None:
            method = getattr(self.recommendation_engine, "recommend_actions", None)
            if callable(method):
                try:
                    return method(
                        case=case,
                        evidence=evidence,
                        entities=entities,
                        linked_cases=linked_cases,
                        campaign=campaign,
                        graph_risk_score=_safe_int(
                            graph_risk.get("case_risk", {}).get("score"),
                            0,
                        ),
                        blast_radius_score=_safe_int(
                            case_intelligence.get("blast_radius_score"),
                            0,
                        ),
                        insider_indicators=case_intelligence.get("insider_threat_indicators", []),
                        export_control=case_intelligence.get("export_control", {}),
                    )
                except Exception:
                    pass

        return []

    def _get_playbooks(
        self,
        *,
        case: Dict[str, Any],
        entities: List[str],
        campaign: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if self.playbook_service is None:
            return []

        playbooks = []

        method = getattr(self.playbook_service, "find_playbook_for_case", None)
        if callable(method):
            try:
                pb = method(
                    case=case,
                    entities=entities,
                    campaign=campaign,
                )
                if pb:
                    playbooks.append(pb)
            except Exception:
                pass

        action_method = getattr(self.playbook_service, "find_playbook_for_action", None)
        if callable(action_method):
            for rec in recommendations:
                try:
                    pb = action_method(
                        action=rec.get("action"),
                        case=case,
                        entities=entities,
                    )
                    if pb:
                        playbooks.append(pb)
                except Exception:
                    pass

        seen = set()
        deduped = []

        for pb in playbooks:
            key = pb.get("playbook_name") or pb.get("name")
            if key in seen:
                continue
            seen.add(key)
            deduped.append(pb)

        return deduped

    # ------------------------------------------------------------------
    # Approvals / Workload / Escalation / Events
    # ------------------------------------------------------------------

    def _get_approvals(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        if self.approval_service is not None:
            for method_name in [
                "get_case_approvals",
                "list_case_approvals",
                "get_pending_approvals_for_case",
            ]:
                method = getattr(self.approval_service, method_name, None)

                if callable(method):
                    try:
                        return method(case_id=case_id, tenant_id=tenant_id)
                    except TypeError:
                        try:
                            return method(case_id)
                        except Exception:
                            pass
                    except Exception:
                        pass

        return []

    def _get_analyst_workload(
        self,
        *,
        tenant_id: Optional[str],
    ) -> Dict[str, Any]:
        if self.assignment_service is not None:
            for method_name in [
                "get_workload_summary",
                "get_analyst_workload",
            ]:
                method = getattr(self.assignment_service, method_name, None)

                if callable(method):
                    try:
                        result = method(tenant_id=tenant_id)
                    except TypeError:
                        try:
                            result = method()
                        except Exception:
                            result = None

                    if result is not None:
                        return {
                            "items": result,
                        }

        return {}

    def _get_escalation_context(
        self,
        *,
        case: Dict[str, Any],
        case_id: Any,
    ) -> Dict[str, Any]:
        if self.escalation_service is not None:
            for method_name in [
                "get_case_escalation",
                "get_escalation_status",
            ]:
                method = getattr(self.escalation_service, method_name, None)

                if callable(method):
                    try:
                        return method(case_id=case_id)
                    except TypeError:
                        try:
                            return method(case_id)
                        except Exception:
                            pass
                    except Exception:
                        pass

        return {
            "is_escalated": (
                _safe_upper(case.get("status")) == "ESCALATED"
                or _safe_int(case.get("escalation_level"), 0) > 0
            ),
            "escalation_level": _safe_int(case.get("escalation_level"), 0),
            "escalation_owner": case.get("escalation_owner"),
        }

    def _get_live_events(
        self,
        *,
        case_id: Any,
        tenant_id: Optional[str],
    ) -> List[Dict[str, Any]]:
        if self.event_broadcaster is not None:
            method = getattr(self.event_broadcaster, "get_recent_activity", None)
            if callable(method):
                try:
                    return method(
                        case_id=case_id,
                        tenant_id=tenant_id,
                        limit=50,
                    )
                except TypeError:
                    try:
                        return method(case_id=case_id, limit=50)
                    except Exception:
                        pass
                except Exception:
                    pass

        return []

    # ------------------------------------------------------------------
    # Priority
    # ------------------------------------------------------------------

    def _calculate_operational_priority_score(
        self,
        *,
        case: Dict[str, Any],
        sla: Dict[str, Any],
        graph_risk: Dict[str, Any],
        linked_cases: List[Dict[str, Any]],
        campaign: Dict[str, Any],
        case_intelligence: Dict[str, Any],
        approvals: List[Dict[str, Any]],
        escalation: Dict[str, Any],
    ) -> int:
        if case_intelligence.get("operational_priority_score") is not None:
            return _safe_int(case_intelligence.get("operational_priority_score"), 0)

        score = 0

        severity = _safe_upper(
            case.get("severity")
            or case.get("priority")
            or graph_risk.get("case_risk", {}).get("severity")
        )

        score += {
            "CRITICAL": 100,
            "HIGH": 70,
            "MEDIUM": 40,
            "LOW": 10,
        }.get(severity, 0)

        score += _safe_int(graph_risk.get("case_risk", {}).get("score"), 0)

        if sla.get("breached"):
            score += 100

        if campaign.get("campaign_id"):
            score += 60

        score += min(len(linked_cases) * 15, 60)
        score += min(len(approvals) * 10, 30)

        if escalation.get("is_escalated"):
            score += 50

        score += _safe_int(escalation.get("escalation_level"), 0) * 25

        return score