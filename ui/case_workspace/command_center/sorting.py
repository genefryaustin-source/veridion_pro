from __future__ import annotations

import time
from typing import Any, Dict, List

from ui.case_workspace.command_center.queue_state import QueueState


def operational_priority_score(case: Dict[str, Any]) -> int:
    """
    Composite command-center priority score.

    Higher score = more urgent.
    """

    score = 0

    severity = str(
        case.get("severity")
        or case.get("priority")
        or ""
    ).upper()

    severity_weights = {
        "CRITICAL": 100,
        "HIGH": 70,
        "MEDIUM": 40,
        "LOW": 10,
    }

    score += severity_weights.get(severity, 0)

    escalation_level = int(case.get("escalation_level") or 0)
    score += escalation_level * 30

    graph_risk = int(case.get("graph_risk_score") or 0)
    score += graph_risk

    cross_case_links = int(case.get("cross_case_links") or 0)
    score += cross_case_links * 8

    evidence_count = int(case.get("evidence_count") or 0)
    score += min(evidence_count * 2, 30)

    if _is_breached(case):
        score += 100

    elif _is_near_breach(case):
        score += 50

    if not (case.get("assigned_to") or case.get("owner")):
        score += 25

    return score


def apply_command_center_sorting(
    cases: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    sort_by = QueueState.get_sort_by()

    if sort_by == "Operational Priority":
        return sorted(
            cases,
            key=operational_priority_score,
            reverse=True,
        )

    if sort_by == "Graph Risk":
        return sorted(
            cases,
            key=lambda x: int(x.get("graph_risk_score") or 0),
            reverse=True,
        )

    if sort_by == "Criticality":
        return sorted(
            cases,
            key=lambda x: _severity_rank(x),
            reverse=True,
        )

    if sort_by == "Escalation Level":
        return sorted(
            cases,
            key=lambda x: int(x.get("escalation_level") or 0),
            reverse=True,
        )

    if sort_by == "Cross-Case Links":
        return sorted(
            cases,
            key=lambda x: int(x.get("cross_case_links") or 0),
            reverse=True,
        )

    if sort_by == "Evidence Volume":
        return sorted(
            cases,
            key=lambda x: int(x.get("evidence_count") or 0),
            reverse=True,
        )

    if sort_by == "Recent Activity":
        return sorted(
            cases,
            key=lambda x: int(x.get("updated_at_ms") or x.get("created_at_ms") or 0),
            reverse=True,
        )

    if sort_by == "Created Time":
        return sorted(
            cases,
            key=lambda x: int(x.get("created_at_ms") or 0),
            reverse=True,
        )

    if sort_by == "Updated Time":
        return sorted(
            cases,
            key=lambda x: int(x.get("updated_at_ms") or 0),
            reverse=True,
        )

    return sorted(
        cases,
        key=lambda x: int(
            x.get("sla_due_at_ms")
            or x.get("sla_deadline_ms")
            or 9999999999999
        ),
    )


def _severity_rank(case: Dict[str, Any]) -> int:
    severity = str(
        case.get("severity")
        or case.get("priority")
        or ""
    ).upper()

    return {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }.get(severity, 0)


def _is_breached(case: Dict[str, Any]) -> bool:
    if case.get("sla_breached") is True:
        return True

    due = case.get("sla_due_at_ms") or case.get("sla_deadline_ms")

    if not due:
        return False

    try:
        return int(due) < int(time.time() * 1000)
    except Exception:
        return False


def _is_near_breach(case: Dict[str, Any]) -> bool:
    due = case.get("sla_due_at_ms") or case.get("sla_deadline_ms")

    if not due:
        return False

    try:
        delta_min = (int(due) - int(time.time() * 1000)) / 60000
        return 0 <= delta_min <= 15
    except Exception:
        return False