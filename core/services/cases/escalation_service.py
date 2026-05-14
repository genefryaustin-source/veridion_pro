import json
import time
import uuid

from core.services.cases.assignment_service import (
    AssignmentService
)

from core.services.cases.sla_service import (
    SLAService
)

from core.services.cases.case_state_machine import (
    CaseStateMachine
)

from core.services.cases.approval_service import (
    ApprovalService
)

from core.services.graph.graph_risk_service import (
    GraphRiskService
)


def _now_ms():
    return int(time.time() * 1000)


DEFAULT_ESCALATION_OWNER = "soc_manager"


class EscalationService:

    def __init__(self, ledger):

        self.ledger = ledger

        self.assignment_service = (
            AssignmentService(ledger)
        )

        self.sla_service = (
            SLAService(ledger)
        )

        self.state_machine = (
            CaseStateMachine(ledger)
        )

        self.approval_service = (
            ApprovalService(ledger)
        )

        self.graph_risk_service = (
            GraphRiskService(ledger)
        )

    # =====================================================
    # MAIN ORCHESTRATION
    # =====================================================
    def evaluate_case(
        self,
        case_id,
    ):
        case = self._load_case(case_id)

        if not case:
            return {
                "ok": False,
                "error": "Case not found",
            }

        graph_risk = (
            self.graph_risk_service
            .analyze_case_graph(case_id)
        )

        case_risk = (
            graph_risk.get(
                "case_risk",
                {}
            )
        )

        severity = (
            case_risk.get(
                "severity",
                "LOW",
            )
        ).upper()

        sla = (
            self.sla_service
            .calculate_case_sla(
                case=case,
                graph_risk=graph_risk,
            )
        )

        actions = []

        # -------------------------------------------------
        # SLA BREACH
        # -------------------------------------------------
        if sla["breached"]:

            result = self.auto_escalate_case(
                case_id=case_id,
                reason="SLA_BREACH",
                severity=severity,
            )

            if result["ok"]:
                actions.append(
                    "AUTO_ESCALATED_SLA"
                )

        # -------------------------------------------------
        # CRITICAL INVESTIGATION
        # -------------------------------------------------
        if severity == "CRITICAL":

            result = self.ensure_critical_escalation(
                case_id=case_id,
            )

            if result["ok"]:
                actions.append(
                    "CRITICAL_ESCALATION"
                )

        # -------------------------------------------------
        # EXPORT CONTROL
        # -------------------------------------------------
        if (
            self.approval_service
            .requires_export_control_review(
                case_id
            )
        ):

            self.approval_service.ensure_required_approvals(
                case_id=case_id,
                requested_by="escalation_engine",
            )

            actions.append(
                "EXPORT_CONTROL_REVIEW"
            )

        return {
            "ok": True,
            "case_id": case_id,
            "severity": severity,
            "sla": sla,
            "actions": actions,
        }

    # =====================================================
    # AUTO ESCALATION
    # =====================================================
    def auto_escalate_case(
        self,
        case_id,
        reason="AUTO_ESCALATION",
        severity=None,
    ):
        case = self._load_case(case_id)

        if not case:
            return {
                "ok": False,
                "error": "Case not found",
            }

        status = (
            case.get("status")
            or "NEW"
        ).upper()

        if status == "ESCALATED":
            return {
                "ok": True,
                "already_escalated": True,
            }

        # -------------------------------------------------
        # CHANGE STATE
        # -------------------------------------------------
        transition = (
            self.state_machine
            .transition_case(
                case_id=case_id,
                new_status="ESCALATED",
                actor="escalation_engine",
                reason=reason,
                force=True,
            )
        )

        # -------------------------------------------------
        # ASSIGN ESCALATION OWNER
        # -------------------------------------------------
        self.assignment_service.set_escalation_owner(
            case_id=case_id,
            owner_id=DEFAULT_ESCALATION_OWNER,
            assigned_by="escalation_engine",
            reason=reason,
        )

        # -------------------------------------------------
        # UPDATE CASE OWNER
        # -------------------------------------------------
        self.assignment_service.reassign_case(
            case_id=case_id,
            new_analyst_id=DEFAULT_ESCALATION_OWNER,
            reassigned_by="escalation_engine",
            reason=reason,
        )

        # -------------------------------------------------
        # LOG EVENT
        # -------------------------------------------------
        with self.ledger._connect() as con:

            self._log_case_event(
                con=con,
                case_id=case_id,
                event_type="CASE_ESCALATED",
                severity=severity or "HIGH",
                message=f"Case auto-escalated ({reason})",
                metadata={
                    "reason": reason,
                    "severity": severity,
                    "owner": DEFAULT_ESCALATION_OWNER,
                },
            )

            con.commit()

        return {
            "ok": True,
            "transition": transition,
        }

    # =====================================================
    # CRITICAL ESCALATION
    # =====================================================
    def ensure_critical_escalation(
        self,
        case_id,
    ):
        case = self._load_case(case_id)

        if not case:
            return {
                "ok": False,
                "error": "Case not found",
            }

        graph_risk = (
            self.graph_risk_service
            .analyze_case_graph(case_id)
        )

        case_risk = (
            graph_risk.get(
                "case_risk",
                {}
            )
        )

        severity = (
            case_risk.get(
                "severity",
                "LOW",
            )
        ).upper()

        if severity != "CRITICAL":
            return {
                "ok": False,
                "reason": "Not critical",
            }

        return self.auto_escalate_case(
            case_id=case_id,
            reason="CRITICAL_INVESTIGATION",
            severity=severity,
        )

    # =====================================================
    # BULK EVALUATION
    # =====================================================
    def evaluate_all_cases(self):

        results = []

        with self.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT *
                FROM cases
                WHERE COALESCE(status, 'NEW')
                    NOT IN ('CLOSED')
                """
            ).fetchall()

            for r in rows:

                case = dict(r)

                case_id = (
                    case.get("case_id")
                    or case.get("id")
                )

                try:

                    result = (
                        self.evaluate_case(
                            case_id
                        )
                    )

                    results.append(result)

                except Exception as ex:

                    results.append({
                        "ok": False,
                        "case_id": case_id,
                        "error": str(ex),
                    })

        return results

    # =====================================================
    # ESCALATION QUEUES
    # =====================================================
    def get_escalated_cases(self):

        with self.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT *
                FROM cases
                WHERE UPPER(
                    COALESCE(status, '')
                ) = 'ESCALATED'
                ORDER BY created_at_ms DESC
                """
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    def get_critical_cases(self):

        critical = []

        with self.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT *
                FROM cases
                WHERE COALESCE(status, 'NEW')
                    NOT IN ('CLOSED')
                """
            ).fetchall()

            for r in rows:

                case = dict(r)

                case_id = (
                    case.get("case_id")
                    or case.get("id")
                )

                graph_risk = (
                    self.graph_risk_service
                    .analyze_case_graph(
                        case_id
                    )
                )

                severity = (
                    graph_risk.get(
                        "case_risk",
                        {}
                    ).get(
                        "severity",
                        "LOW",
                    )
                ).upper()

                if severity == "CRITICAL":

                    case["graph_risk"] = (
                        graph_risk
                    )

                    critical.append(case)

        return critical

    # =====================================================
    # LIVE ACTIVITY FEED
    # =====================================================
    def get_recent_escalation_activity(
        self,
        limit=50,
    ):
        with self.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT *
                FROM case_events
                WHERE event_type IN (
                    'CASE_ESCALATED',
                    'APPROVAL_REQUESTED',
                    'APPROVAL_APPROVED',
                    'APPROVAL_REJECTED',
                    'STATUS_CHANGED'
                )
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    # =====================================================
    # HELPERS
    # =====================================================
    def _load_case(
        self,
        case_id,
    ):
        with self.ledger._connect() as con:

            row = con.execute(
                """
                SELECT *
                FROM cases
                WHERE case_id = ?
                   OR id = ?
                LIMIT 1
                """,
                (
                    case_id,
                    case_id,
                ),
            ).fetchone()

            if not row:
                return None

            return dict(row)

    def _log_case_event(
        self,
        con,
        case_id,
        event_type,
        severity,
        message,
        metadata=None,
    ):
        metadata = metadata or {}

        try:

            con.execute(
                """
                INSERT INTO case_events (
                    event_id,
                    case_id,
                    event_type,
                    severity,
                    message,
                    created_at_ms,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid.uuid4().hex,
                    case_id,
                    event_type,
                    severity,
                    message,
                    _now_ms(),
                    json.dumps(metadata),
                ),
            )

        except Exception:
            pass