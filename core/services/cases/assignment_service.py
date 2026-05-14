import time
import json


def _now_ms():
    return int(time.time() * 1000)


class AssignmentService:

    def __init__(self, ledger):
        self.ledger = ledger

    def assign_case(
        self,
        case_id,
        analyst_id,
        assigned_by="system",
        role="PRIMARY_ANALYST",
    ):
        if not case_id or not analyst_id:
            return False

        with self.ledger._connect() as con:
            con.execute(
                """
                UPDATE cases
                SET owner = ?
                WHERE case_id = ?
                   OR id = ?
                """,
                (
                    analyst_id,
                    case_id,
                    case_id,
                ),
            )

            self._log_assignment(
                con=con,
                case_id=case_id,
                analyst_id=analyst_id,
                assigned_by=assigned_by,
                role=role,
                action="ASSIGNED",
            )

            con.commit()

        return True

    def reassign_case(
        self,
        case_id,
        new_analyst_id,
        reassigned_by="system",
        reason=None,
    ):
        if not case_id or not new_analyst_id:
            return False

        with self.ledger._connect() as con:
            old_owner = None

            row = con.execute(
                """
                SELECT owner
                FROM cases
                WHERE case_id = ?
                   OR id = ?
                LIMIT 1
                """,
                (case_id, case_id),
            ).fetchone()

            if row:
                old_owner = row["owner"]

            con.execute(
                """
                UPDATE cases
                SET owner = ?
                WHERE case_id = ?
                   OR id = ?
                """,
                (
                    new_analyst_id,
                    case_id,
                    case_id,
                ),
            )

            self._log_assignment(
                con=con,
                case_id=case_id,
                analyst_id=new_analyst_id,
                assigned_by=reassigned_by,
                role="PRIMARY_ANALYST",
                action="REASSIGNED",
                metadata={
                    "old_owner": old_owner,
                    "reason": reason,
                },
            )

            con.commit()

        return True

    def set_escalation_owner(
        self,
        case_id,
        owner_id,
        assigned_by="system",
        reason=None,
    ):
        with self.ledger._connect() as con:
            self._log_assignment(
                con=con,
                case_id=case_id,
                analyst_id=owner_id,
                assigned_by=assigned_by,
                role="ESCALATION_OWNER",
                action="ESCALATION_OWNER_SET",
                metadata={
                    "reason": reason,
                },
            )

            con.commit()

        return True

    def get_analyst_queue(
        self,
        analyst_id,
        include_closed=False,
    ):
        with self.ledger._connect() as con:
            query = """
                SELECT *
                FROM cases
                WHERE owner = ?
            """

            params = [analyst_id]

            if not include_closed:
                query += """
                    AND COALESCE(status, 'NEW') != 'CLOSED'
                """

            query += """
                ORDER BY created_at_ms DESC
            """

            rows = con.execute(
                query,
                tuple(params),
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    def get_unassigned_cases(self):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT *
                FROM cases
                WHERE owner IS NULL
                   OR owner = ''
                   OR owner = 'analyst_queue'
                ORDER BY created_at_ms DESC
                """
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    def get_workload_summary(self):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT
                    COALESCE(owner, 'UNASSIGNED') AS analyst,
                    COUNT(*) AS total
                FROM cases
                WHERE COALESCE(status, 'NEW') != 'CLOSED'
                GROUP BY COALESCE(owner, 'UNASSIGNED')
                ORDER BY total DESC
                """
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    def _log_assignment(
        self,
        con,
        case_id,
        analyst_id,
        assigned_by,
        role,
        action,
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
                    f"assign_{_now_ms()}_{case_id}",
                    case_id,
                    action,
                    "INFO",
                    f"{action}: {analyst_id}",
                    _now_ms(),
                    json.dumps({
                        "analyst_id": analyst_id,
                        "assigned_by": assigned_by,
                        "role": role,
                        **metadata,
                    }),
                ),
            )
        except Exception:
            pass