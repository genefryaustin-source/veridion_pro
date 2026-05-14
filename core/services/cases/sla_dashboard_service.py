"""
SLA Dashboard Service

Operational metrics engine for the SOC Command Center.

Responsibilities:
- breached case detection
- near-breach detection
- SLA health metrics
- analyst workload metrics
- MTTA / MTTR calculations
- escalation velocity
- case aging analytics
- operational heatmaps
- queue pressure visibility

This service is intentionally defensive and compatible with
evolving ledger schemas.
"""

from __future__ import annotations

import statistics
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


# ---------------------------------------------------------------------
# SLA Dashboard Service
# ---------------------------------------------------------------------

class SLADashboardService:

    NEAR_BREACH_MINUTES = 15

    def __init__(self, ledger: Any):
        self.ledger = ledger

    # -----------------------------------------------------------------
    # Main Dashboard Summary
    # -----------------------------------------------------------------

    def get_dashboard_summary(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        cases = self._get_cases(tenant_id=tenant_id)

        breached = []
        near_breach = []
        critical = []
        unassigned = []
        escalated = []

        for case in cases:

            if self._is_breached(case):
                breached.append(case)

            elif self._is_near_breach(case):
                near_breach.append(case)

            if self._is_critical(case):
                critical.append(case)

            if self._is_unassigned(case):
                unassigned.append(case)

            if self._is_escalated(case):
                escalated.append(case)

        return {
            "total_cases": len(cases),
            "breached_count": len(breached),
            "near_breach_count": len(near_breach),
            "critical_count": len(critical),
            "unassigned_count": len(unassigned),
            "escalated_count": len(escalated),

            "breached_cases": breached,
            "near_breach_cases": near_breach,
            "critical_cases": critical,
            "unassigned_cases": unassigned,
            "escalated_cases": escalated,

            "sla_health_score": self._calculate_sla_health_score(
                total_cases=len(cases),
                breached_count=len(breached),
                critical_count=len(critical),
            ),

            "generated_at_ms": _now_ms(),
        }

    # -----------------------------------------------------------------
    # Breach Detection
    # -----------------------------------------------------------------

    def get_breached_cases(
        self,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        cases = self._get_cases(tenant_id=tenant_id)

        return [
            case
            for case in cases
            if self._is_breached(case)
        ]

    def get_near_breach_cases(
        self,
        tenant_id: Optional[str] = None,
        threshold_minutes: Optional[int] = None,
    ) -> List[Dict[str, Any]]:

        threshold_minutes = (
            threshold_minutes
            or self.NEAR_BREACH_MINUTES
        )

        cases = self._get_cases(tenant_id=tenant_id)

        results = []

        for case in cases:
            if self._is_breached(case):
                continue

            minutes_remaining = self._minutes_until_breach(case)

            if (
                minutes_remaining is not None
                and minutes_remaining <= threshold_minutes
            ):
                results.append(case)

        return results

    # -----------------------------------------------------------------
    # Analyst Metrics
    # -----------------------------------------------------------------

    def get_analyst_workload(
        self,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        cases = self._get_cases(tenant_id=tenant_id)

        workloads = defaultdict(lambda: {
            "assigned_cases": 0,
            "critical_cases": 0,
            "breached_cases": 0,
            "escalated_cases": 0,
        })

        for case in cases:

            analyst = (
                case.get("assigned_to")
                or case.get("owner")
                or "UNASSIGNED"
            )

            workloads[analyst]["assigned_cases"] += 1

            if self._is_critical(case):
                workloads[analyst]["critical_cases"] += 1

            if self._is_breached(case):
                workloads[analyst]["breached_cases"] += 1

            if self._is_escalated(case):
                workloads[analyst]["escalated_cases"] += 1

        results = []

        for analyst, data in workloads.items():

            workload_score = (
                data["assigned_cases"]
                + (data["critical_cases"] * 3)
                + (data["breached_cases"] * 5)
                + (data["escalated_cases"] * 2)
            )

            results.append({
                "analyst": analyst,
                "assigned_cases": data["assigned_cases"],
                "critical_cases": data["critical_cases"],
                "breached_cases": data["breached_cases"],
                "escalated_cases": data["escalated_cases"],
                "workload_score": workload_score,
            })

        results.sort(
            key=lambda x: x["workload_score"],
            reverse=True,
        )

        return results

    # -----------------------------------------------------------------
    # MTTA / MTTR
    # -----------------------------------------------------------------

    def get_mtta_metrics(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        cases = self._get_cases(tenant_id=tenant_id)

        durations = []

        for case in cases:

            created_ms = self._get_created_ms(case)
            assigned_ms = self._get_assignment_ms(case)

            if not created_ms or not assigned_ms:
                continue

            delta = assigned_ms - created_ms

            if delta > 0:
                durations.append(delta)

        return self._build_duration_metrics(
            durations=durations,
            label="MTTA",
        )

    def get_mttr_metrics(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        cases = self._get_cases(tenant_id=tenant_id)

        durations = []

        for case in cases:

            created_ms = self._get_created_ms(case)
            resolved_ms = self._get_resolved_ms(case)

            if not created_ms or not resolved_ms:
                continue

            delta = resolved_ms - created_ms

            if delta > 0:
                durations.append(delta)

        return self._build_duration_metrics(
            durations=durations,
            label="MTTR",
        )

    # -----------------------------------------------------------------
    # Escalation Metrics
    # -----------------------------------------------------------------

    def get_escalation_metrics(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        cases = self._get_cases(tenant_id=tenant_id)

        escalated = [
            c for c in cases
            if self._is_escalated(c)
        ]

        escalation_levels = Counter()

        for case in escalated:
            level = (
                case.get("escalation_level")
                or 1
            )

            escalation_levels[str(level)] += 1

        return {
            "total_escalated": len(escalated),
            "escalation_distribution": dict(escalation_levels),
            "escalation_rate": (
                round(len(escalated) / max(len(cases), 1), 4)
            ),
        }

    # -----------------------------------------------------------------
    # Aging Metrics
    # -----------------------------------------------------------------

    def get_case_age_metrics(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        cases = self._get_cases(tenant_id=tenant_id)

        ages_hours = []

        for case in cases:

            created_ms = self._get_created_ms(case)

            if not created_ms:
                continue

            age_hours = (_now_ms() - created_ms) / 3600000

            ages_hours.append(age_hours)

        if not ages_hours:
            return {
                "count": 0,
                "avg_hours": 0,
                "median_hours": 0,
                "max_hours": 0,
            }

        return {
            "count": len(ages_hours),
            "avg_hours": round(statistics.mean(ages_hours), 2),
            "median_hours": round(statistics.median(ages_hours), 2),
            "max_hours": round(max(ages_hours), 2),
        }

    # -----------------------------------------------------------------
    # Heatmap Metrics
    # -----------------------------------------------------------------

    def get_heatmap_metrics(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        cases = self._get_cases(tenant_id=tenant_id)

        severity_heatmap = Counter()
        status_heatmap = Counter()

        for case in cases:

            severity = (
                case.get("severity")
                or case.get("priority")
                or "UNKNOWN"
            )

            status = (
                case.get("status")
                or "UNKNOWN"
            )

            severity_heatmap[severity] += 1
            status_heatmap[status] += 1

        return {
            "severity_heatmap": dict(severity_heatmap),
            "status_heatmap": dict(status_heatmap),
        }

    # -----------------------------------------------------------------
    # Operational Pressure Score
    # -----------------------------------------------------------------

    def get_operational_pressure_score(
        self,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        summary = self.get_dashboard_summary(
            tenant_id=tenant_id
        )

        score = 0

        score += summary["breached_count"] * 10
        score += summary["near_breach_count"] * 5
        score += summary["critical_count"] * 4
        score += summary["unassigned_count"] * 3
        score += summary["escalated_count"] * 2

        if score >= 200:
            level = "CRITICAL"

        elif score >= 100:
            level = "HIGH"

        elif score >= 50:
            level = "MEDIUM"

        else:
            level = "LOW"

        return {
            "score": score,
            "level": level,
        }

    # -----------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------

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
                        return method(tenant_id=tenant_id)

                    return method()

                except TypeError:
                    try:
                        return method(tenant_id)
                    except Exception:
                        pass

        return []

    def _is_breached(self, case: Dict[str, Any]) -> bool:

        if case.get("sla_breached") is True:
            return True

        breach_at = (
            case.get("sla_due_at_ms")
            or case.get("sla_deadline_ms")
        )

        if breach_at and _now_ms() > _safe_int(breach_at):
            return True

        return False

    def _is_near_breach(self, case: Dict[str, Any]) -> bool:

        minutes_remaining = self._minutes_until_breach(case)

        if minutes_remaining is None:
            return False

        return (
            0 <= minutes_remaining <= self.NEAR_BREACH_MINUTES
        )

    def _minutes_until_breach(
        self,
        case: Dict[str, Any],
    ) -> Optional[float]:

        breach_at = (
            case.get("sla_due_at_ms")
            or case.get("sla_deadline_ms")
        )

        if not breach_at:
            return None

        delta_ms = _safe_int(breach_at) - _now_ms()

        return delta_ms / 60000

    def _is_critical(self, case: Dict[str, Any]) -> bool:

        severity = (
            str(case.get("severity") or "")
            .upper()
            .strip()
        )

        priority = (
            str(case.get("priority") or "")
            .upper()
            .strip()
        )

        return (
            severity == "CRITICAL"
            or priority == "CRITICAL"
        )

    def _is_unassigned(self, case: Dict[str, Any]) -> bool:

        assigned = (
            case.get("assigned_to")
            or case.get("owner")
        )

        return not assigned

    def _is_escalated(self, case: Dict[str, Any]) -> bool:

        if case.get("escalated") is True:
            return True

        status = (
            str(case.get("status") or "")
            .upper()
            .strip()
        )

        if status == "ESCALATED":
            return True

        escalation_level = _safe_int(
            case.get("escalation_level"),
            0,
        )

        return escalation_level > 0

    def _get_created_ms(
        self,
        case: Dict[str, Any],
    ) -> Optional[int]:

        for field in [
            "created_at_ms",
            "created_ms",
            "opened_at_ms",
        ]:
            value = case.get(field)

            if value:
                return _safe_int(value)

        return None

    def _get_assignment_ms(
        self,
        case: Dict[str, Any],
    ) -> Optional[int]:

        for field in [
            "assigned_at_ms",
            "assignment_ts_ms",
        ]:
            value = case.get(field)

            if value:
                return _safe_int(value)

        return None

    def _get_resolved_ms(
        self,
        case: Dict[str, Any],
    ) -> Optional[int]:

        for field in [
            "resolved_at_ms",
            "closed_at_ms",
        ]:
            value = case.get(field)

            if value:
                return _safe_int(value)

        return None

    def _calculate_sla_health_score(
        self,
        total_cases: int,
        breached_count: int,
        critical_count: int,
    ) -> float:

        if total_cases <= 0:
            return 100.0

        penalty = 0

        penalty += breached_count * 5
        penalty += critical_count * 2

        score = max(0, 100 - penalty)

        return round(score, 2)

    def _build_duration_metrics(
        self,
        durations: List[int],
        label: str,
    ) -> Dict[str, Any]:

        if not durations:
            return {
                "label": label,
                "count": 0,
                "avg_minutes": 0,
                "median_minutes": 0,
                "max_minutes": 0,
            }

        durations_min = [
            d / 60000
            for d in durations
        ]

        return {
            "label": label,
            "count": len(durations_min),
            "avg_minutes": round(statistics.mean(durations_min), 2),
            "median_minutes": round(statistics.median(durations_min), 2),
            "max_minutes": round(max(durations_min), 2),
        }