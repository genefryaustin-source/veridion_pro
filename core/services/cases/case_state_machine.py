import time
import json


def _now_ms():
    return int(time.time() * 1000)


CASE_STATUSES = [
    "NEW",
    "TRIAGE",
    "INVESTIGATING",
    "ESCALATED",
    "CONTAINED",
    "RESOLVED",
    "CLOSED",
]


ALLOWED_TRANSITIONS = {
    "NEW": ["TRIAGE", "INVESTIGATING", "ESCALATED", "CLOSED"],
    "TRIAGE": ["INVESTIGATING", "ESCALATED", "CLOSED"],
    "INVESTIGATING": ["ESCALATED", "CONTAINED", "RESOLVED", "CLOSED"],
    "ESCALATED": ["INVESTIGATING", "CONTAINED", "RESOLVED", "CLOSED"],
    "CONTAINED": ["RESOLVED", "ESCALATED", "CLOSED"],
    "RESOLVED": ["CLOSED", "INVESTIGATING"],
    "CLOSED": [],
}


class CaseStateMachine:

    def __init__(self, ledger):
        self.ledger = ledger

    def can_transition(self, current_status, new_status):
        current_status = (current_status or "NEW").upper()
        new_status = (new_status or "").upper()

        return new_status in ALLOWED_TRANSITIONS.get(
            current_status,
            [],
        )

    def transition_case(
        self,
        case_id,
        new_status,
        actor="system",
        reason=None,
        force=False,
    ):
        new_status = (new_status or "").upper()

        if new_status not in CASE_STATUSES:
            return {
                "ok": False,
                "error": f"Invalid status: {new_status}",
            }

        with self.ledger._connect() as con:
            row = con.execute(
                """
                SELECT *
                FROM cases
                WHERE case_id = ?
                   OR id = ?
                LIMIT 1
                """,
                (case_id, case_id),
            ).fetchone()

            if not row:
                return {
                    "ok": False,
                    "error": "Case not found",
                }

            case = dict(row)
            current_status = (
                case.get("status")
                or "NEW"
            ).upper()

            if (
                not force
                and not self.can_transition(
                    current_status,
                    new_status,
                )
            ):
                return {
                    "ok": False,
                    "error": f"Transition not allowed: {current_status} → {new_status}",
                }

            con.execute(
                """
                UPDATE cases
                SET status = ?
                WHERE case_id = ?
                   OR id = ?
                """,
                (new_status, case_id, case_id),
            )

            self._log_event(
                con=con,
                case_id=case_id,
                event_type="STATUS_CHANGED",
                actor=actor,
                message=f"Case status changed from {current_status} to {new_status}",
                metadata={
                    "from": current_status,
                    "to": new_status,
                    "reason": reason,
                },
            )

            con.commit()

        return {
            "ok": True,
            "from": current_status,
            "to": new_status,
        }

    def _log_event(
        self,
        con,
        case_id,
        event_type,
        actor,
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
                    f"evt_{_now_ms()}_{case_id}",
                    case_id,
                    event_type,
                    "INFO",
                    message,
                    _now_ms(),
                    json.dumps({
                        "actor": actor,
                        **metadata,
                    }),
                ),
            )
        except Exception:
            pass