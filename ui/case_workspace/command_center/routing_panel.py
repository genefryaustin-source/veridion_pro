from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from core.services.cases.sla_dashboard_service import SLADashboardService
from ui.case_workspace.command_center.queue_state import QueueState


ROUTING_STRATEGIES = [
    "Balanced",
    "Least Loaded",
    "Severity-Based",
    "Tenant-Based",
    "Skill-Based",
    "Escalation-Aware",
]


def render_routing_panel(
    *,
    ledger: Any,
    assignment_service: Any = None,
    routing_service: Any = None,
    current_user: str = "system",
    tenant_id: Optional[str] = None,
):
    """
    SOC Dispatcher / Routing Panel.

    Handles:
    - analyst workload visibility
    - auto-routing
    - unassigned queue distribution
    - breached queue routing
    - critical case routing
    - future AI orchestration strategy selection
    """

    QueueState.initialize()

    sla_service = SLADashboardService(ledger)

    st.subheader("SOC Routing / Analyst Dispatch")

    strategy = st.selectbox(
        "Routing Strategy",
        ROUTING_STRATEGIES,
        index=ROUTING_STRATEGIES.index(
            QueueState.get("routing_strategy", "Balanced")
            if QueueState.get("routing_strategy", "Balanced") in ROUTING_STRATEGIES
            else "Balanced"
        ),
        key="routing_strategy_select",
    )

    QueueState.set("routing_strategy", strategy)

    st.caption(
        "Routing strategy is stored now and can later drive AI-based investigation orchestration."
    )

    st.divider()

    render_workload_table(
        sla_service=sla_service,
        tenant_id=tenant_id,
    )

    st.divider()

    render_auto_routing_controls(
        ledger=ledger,
        assignment_service=assignment_service,
        routing_service=routing_service,
        current_user=current_user,
        tenant_id=tenant_id,
        strategy=strategy,
    )


def render_workload_table(
    *,
    sla_service: SLADashboardService,
    tenant_id: Optional[str] = None,
):
    workloads = sla_service.get_analyst_workload(
        tenant_id=tenant_id,
    )

    st.markdown("### Analyst Workload")

    if not workloads:
        st.info("No analyst workload data available.")
        return

    df = pd.DataFrame(workloads)

    expected_cols = [
        "analyst",
        "assigned_cases",
        "critical_cases",
        "breached_cases",
        "escalated_cases",
        "workload_score",
    ]

    show_cols = [
        c for c in expected_cols
        if c in df.columns
    ]

    st.dataframe(
        df[show_cols],
        use_container_width=True,
        hide_index=True,
    )


def render_auto_routing_controls(
    *,
    ledger: Any,
    assignment_service: Any = None,
    routing_service: Any = None,
    current_user: str = "system",
    tenant_id: Optional[str] = None,
    strategy: str = "Balanced",
):
    st.markdown("### Auto-Routing Controls")

    cols = st.columns(4)

    with cols[0]:
        if st.button("Auto Assign Critical", use_container_width=True):
            result = _route_cases(
                ledger=ledger,
                assignment_service=assignment_service,
                routing_service=routing_service,
                mode="critical",
                strategy=strategy,
                actor=current_user,
                tenant_id=tenant_id,
            )
            _show_result(result)

    with cols[1]:
        if st.button("Balance Queue", use_container_width=True):
            result = _route_cases(
                ledger=ledger,
                assignment_service=assignment_service,
                routing_service=routing_service,
                mode="balance",
                strategy=strategy,
                actor=current_user,
                tenant_id=tenant_id,
            )
            _show_result(result)

    with cols[2]:
        if st.button("Route Unassigned", use_container_width=True):
            result = _route_cases(
                ledger=ledger,
                assignment_service=assignment_service,
                routing_service=routing_service,
                mode="unassigned",
                strategy=strategy,
                actor=current_user,
                tenant_id=tenant_id,
            )
            _show_result(result)

    with cols[3]:
        if st.button("Route Breached", use_container_width=True):
            result = _route_cases(
                ledger=ledger,
                assignment_service=assignment_service,
                routing_service=routing_service,
                mode="breached",
                strategy=strategy,
                actor=current_user,
                tenant_id=tenant_id,
            )
            _show_result(result)


def _route_cases(
    *,
    ledger: Any,
    assignment_service: Any = None,
    routing_service: Any = None,
    mode: str,
    strategy: str,
    actor: str,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Defensive adapter.

    Preferred:
        routing_service.route_cases(...)

    Fallback:
        assignment_service.auto_assign_case(...)

    Last resort:
        no-op result.
    """

    if routing_service is not None:
        for method_name in [
            "route_cases",
            "balance_workloads",
            "auto_route_cases",
        ]:
            method = getattr(routing_service, method_name, None)
            if callable(method):
                try:
                    return method(
                        mode=mode,
                        strategy=strategy,
                        actor=actor,
                        tenant_id=tenant_id,
                    )
                except TypeError:
                    return method(mode, strategy)

    if assignment_service is not None:
        method = getattr(assignment_service, "auto_assign_case", None)
        if callable(method):
            cases = _load_cases_for_mode(
                ledger=ledger,
                mode=mode,
                tenant_id=tenant_id,
            )

            succeeded = 0
            failed = 0
            details = []

            for case in cases:
                case_id = case.get("case_id") or case.get("id")
                try:
                    method(
                        case_id=case_id,
                        strategy=strategy,
                        assigned_by=actor,
                        tenant_id=tenant_id,
                    )
                    succeeded += 1
                    details.append({
                        "case_id": case_id,
                        "status": "success",
                    })
                except TypeError:
                    try:
                        method(case_id)
                        succeeded += 1
                        details.append({
                            "case_id": case_id,
                            "status": "success",
                        })
                    except Exception as exc:
                        failed += 1
                        details.append({
                            "case_id": case_id,
                            "status": "failed",
                            "error": str(exc),
                        })
                except Exception as exc:
                    failed += 1
                    details.append({
                        "case_id": case_id,
                        "status": "failed",
                        "error": str(exc),
                    })

            return {
                "mode": mode,
                "strategy": strategy,
                "succeeded": succeeded,
                "failed": failed,
                "details": details,
            }

    return {
        "mode": mode,
        "strategy": strategy,
        "succeeded": 0,
        "failed": 0,
        "details": [],
        "message": "No routing_service or assignment_service auto-routing method available.",
    }


def _load_cases_for_mode(
    *,
    ledger: Any,
    mode: str,
    tenant_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    cases = []

    for method_name in [
        "get_cases",
        "list_cases",
        "fetch_cases",
        "get_all_cases",
    ]:
        method = getattr(ledger, method_name, None)
        if callable(method):
            try:
                if tenant_id:
                    cases = method(tenant_id=tenant_id)
                else:
                    cases = method()
                break
            except TypeError:
                try:
                    cases = method(tenant_id)
                    break
                except Exception:
                    pass
            except Exception:
                pass

    if not cases:
        return []

    if mode == "critical":
        return [
            c for c in cases
            if str(c.get("severity") or c.get("priority") or "").upper() == "CRITICAL"
        ]

    if mode == "unassigned":
        return [
            c for c in cases
            if not (c.get("assigned_to") or c.get("owner"))
        ]

    if mode == "breached":
        import time
        now_ms = int(time.time() * 1000)
        return [
            c for c in cases
            if c.get("sla_breached") is True
            or int(c.get("sla_due_at_ms") or c.get("sla_deadline_ms") or 9999999999999) < now_ms
        ]

    return cases


def _show_result(result: Dict[str, Any]):
    if result.get("failed", 0):
        st.warning(
            f"Routing completed with {result.get('succeeded', 0)} succeeded and {result.get('failed', 0)} failed."
        )
    else:
        st.success(
            f"Routing completed: {result.get('succeeded', 0)} cases processed."
        )

    with st.expander("Routing Result", expanded=False):
        st.json(result)