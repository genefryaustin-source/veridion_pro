import time


def _now_ms():
    return int(time.time() * 1000)


SLA_MINUTES = {
    "CRITICAL": 15,
    "HIGH": 60,
    "MEDIUM": 240,
    "LOW": 1440,
    "INFO": 1440,
}


class SLAService:

    def __init__(self, ledger):
        self.ledger = ledger

    def calculate_case_sla(
        self,
        case,
        graph_risk=None,
    ):
        graph_risk = graph_risk or {}

        severity = (
            graph_risk.get("case_risk", {}).get("severity")
            or case.get("severity")
            or case.get("priority")
            or "LOW"
        ).upper()

        created_at_ms = (
            case.get("created_at_ms")
            or case.get("created_at")
            or _now_ms()
        )

        try:
            created_at_ms = int(created_at_ms)
        except Exception:
            created_at_ms = _now_ms()

        sla_minutes = SLA_MINUTES.get(
            severity,
            SLA_MINUTES["LOW"],
        )

        deadline_ms = created_at_ms + (
            sla_minutes * 60 * 1000
        )

        now = _now_ms()

        breached = now > deadline_ms

        remaining_ms = max(
            0,
            deadline_ms - now,
        )

        overdue_ms = max(
            0,
            now - deadline_ms,
        )

        return {
            "severity": severity,
            "sla_minutes": sla_minutes,
            "deadline_ms": deadline_ms,
            "breached": breached,
            "remaining_ms": remaining_ms,
            "overdue_ms": overdue_ms,
            "remaining_minutes": round(
                remaining_ms / 60000,
                1,
            ),
            "overdue_minutes": round(
                overdue_ms / 60000,
                1,
            ),
        }

    def get_breached_cases(self):
        breached = []

        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT *
                FROM cases
                WHERE COALESCE(status, 'NEW') NOT IN ('RESOLVED', 'CLOSED')
                """
            ).fetchall()

            for r in rows:
                case = dict(r)
                sla = self.calculate_case_sla(case)

                if sla["breached"]:
                    case["sla"] = sla
                    breached.append(case)

        return breached

    def get_escalation_candidates(self):
        candidates = []

        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT *
                FROM cases
                WHERE COALESCE(status, 'NEW') NOT IN ('ESCALATED', 'RESOLVED', 'CLOSED')
                """
            ).fetchall()

            for r in rows:
                case = dict(r)
                sla = self.calculate_case_sla(case)

                if sla["breached"] or sla["remaining_minutes"] <= 5:
                    case["sla"] = sla
                    candidates.append(case)

        return candidates