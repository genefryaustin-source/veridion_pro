from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.services.cases.sla_dashboard_service import SLADashboardService


class CommandCenterService:
    """
    Aggregation service for the SOC Command Center.

    This keeps the UI from calling many services directly.

    Future targets:
    - REST APIs
    - websocket broadcasting
    - MSSP dashboards
    - GovCloud operations
    - mobile command center views
    """

    def __init__(
        self,
        ledger: Any,
        assignment_service: Any = None,
        escalation_service: Any = None,
        approval_service: Any = None,
        routing_service: Any = None,
        graph_service: Any = None,
        activity_service: Any = None,
    ):
        self.ledger = ledger
        self.assignment_service = assignment_service
        self.escalation_service = escalation_service
        self.approval_service = approval_service
        self.routing_service = routing_service
        self.graph_service = graph_service
        self.activity_service = activity_service

        self.sla_service = SLADashboardService(ledger)

    def get_command_center_snapshot(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        cases = self.get_cases(tenant_id=tenant_id)

        return {
            "cases": cases,
            "sla_summary": self.sla_service.get_dashboard_summary(tenant_id=tenant_id),
            "operational_pressure": self.sla_service.get_operational_pressure_score(tenant_id=tenant_id),
            "analyst_workload": self.sla_service.get_analyst_workload(tenant_id=tenant_id),
            "activity": self.get_recent_activity(tenant_id=tenant_id, limit=limit),
            "approvals": self.get_pending_approvals(tenant_id=tenant_id),
            "generated_by": "CommandCenterService",
        }

    def get_cases(
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
                        return method(tenant_id=tenant_id)
                    return method()
                except TypeError:
                    try:
                        return method(tenant_id)
                    except Exception:
                        pass
                except Exception:
                    pass

        return []

    def get_recent_activity(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if self.activity_service is not None:
            for method_name in [
                "get_recent_activity",
                "list_recent_activity",
            ]:
                method = getattr(self.activity_service, method_name, None)
                if callable(method):
                    try:
                        return method(tenant_id=tenant_id, limit=limit)
                    except TypeError:
                        return method(limit)

        events = []

        for method_name in [
            "get_recent_case_events",
            "list_recent_case_events",
            "fetch_recent_case_events",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    if tenant_id:
                        result = method(tenant_id=tenant_id, limit=limit)
                    else:
                        result = method(limit=limit)
                    if result:
                        events.extend(result)
                    break
                except TypeError:
                    try:
                        result = method(limit)
                        if result:
                            events.extend(result)
                        break
                    except Exception:
                        pass
                except Exception:
                    pass

        return events[:limit]

    def get_pending_approvals(
        self,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if self.approval_service is not None:
            for method_name in [
                "get_pending_approvals",
                "list_pending_approvals",
            ]:
                method = getattr(self.approval_service, method_name, None)
                if callable(method):
                    try:
                        return method(tenant_id=tenant_id)
                    except TypeError:
                        return method()

        for method_name in [
            "get_pending_approvals",
            "list_pending_approvals",
        ]:
            method = getattr(self.ledger, method_name, None)
            if callable(method):
                try:
                    if tenant_id:
                        return method(tenant_id=tenant_id)
                    return method()
                except TypeError:
                    try:
                        return method()
                    except Exception:
                        pass
                except Exception:
                    pass

        return []