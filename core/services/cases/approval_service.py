import json
import time
import uuid


def _now_ms():
    return int(time.time() * 1000)


class ApprovalService:
    def __init__(self, ledger):
        self.ledger = ledger

    def create_approval_request(
        self,
        case_id,
        approval_type,
        requested_by="system",
        approver=None,
        reason=None,
        metadata=None,
    ):
        approval_id = uuid.uuid4().hex
        metadata = metadata or {}

        with self.ledger._connect() as con:
            con.execute(
                """
                INSERT INTO case_approvals (
                    approval_id,
                    case_id,
                    approval_type,
                    status,
                    requested_by,
                    approver,
                    reason,
                    metadata_json,
                    created_at_ms,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval_id,
                    case_id,
                    approval_type,
                    "PENDING",
                    requested_by,
                    approver,
                    reason,
                    json.dumps(metadata),
                    _now_ms(),
                    _now_ms(),
                ),
            )

            self._log_case_event(
                con,
                case_id,
                "APPROVAL_REQUESTED",
                f"{approval_type} approval requested",
                {
                    "approval_id": approval_id,
                    "approval_type": approval_type,
                    "requested_by": requested_by,
                    "approver": approver,
                    "reason": reason,
                },
            )

            con.commit()

        return approval_id

    def approve(
        self,
        approval_id,
        approved_by="system",
        notes=None,
    ):
        return self._resolve_approval(
            approval_id=approval_id,
            status="APPROVED",
            actor=approved_by,
            notes=notes,
        )

    def reject(
        self,
        approval_id,
        rejected_by="system",
        notes=None,
    ):
        return self._resolve_approval(
            approval_id=approval_id,
            status="REJECTED",
            actor=rejected_by,
            notes=notes,
        )

    def cancel(
        self,
        approval_id,
        cancelled_by="system",
        notes=None,
    ):
        return self._resolve_approval(
            approval_id=approval_id,
            status="CANCELLED",
            actor=cancelled_by,
            notes=notes,
        )

    def get_pending_approvals(self, approver=None):
        with self.ledger._connect() as con:
            if approver:
                rows = con.execute(
                    """
                    SELECT *
                    FROM case_approvals
                    WHERE status = 'PENDING'
                      AND approver = ?
                    ORDER BY created_at_ms ASC
                    """,
                    (approver,),
                ).fetchall()
            else:
                rows = con.execute(
                    """
                    SELECT *
                    FROM case_approvals
                    WHERE status = 'PENDING'
                    ORDER BY created_at_ms ASC
                    """
                ).fetchall()

            return [dict(r) for r in rows]

    def get_case_approvals(self, case_id):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT *
                FROM case_approvals
                WHERE case_id = ?
                ORDER BY created_at_ms DESC
                """,
                (case_id,),
            ).fetchall()

            return [dict(r) for r in rows]

    def requires_closure_approval(self, case_id):
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
                return False

            case = dict(row)
            status = (case.get("status") or "").upper()
            severity = (
                case.get("severity")
                or case.get("priority")
                or ""
            ).upper()

            return status == "RESOLVED" or severity in ["HIGH", "CRITICAL"]

    def requires_export_control_review(self, case_id):
        with self.ledger._connect() as con:
            rows = con.execute(
                """
                SELECT e.entity_type, e.entity_value
                FROM case_entities ce
                JOIN entities e
                    ON ce.entity_id = e.entity_id
                WHERE ce.case_id = ?
                """,
                (case_id,),
            ).fetchall()

            for r in rows:
                entity_type = (r["entity_type"] or "").upper()
                entity_value = (r["entity_value"] or "").upper()

                if entity_type in [
                    "ITAR_REFERENCE",
                    "EXPORT_CONTROL_TERM",
                    "CUI_MARKING",
                    "GOVERNMENT_PROGRAM",
                ]:
                    return True

                if any(term in entity_value for term in ["ITAR", "EAR", "USML", "EXPORT"]):
                    return True

        return False

    def ensure_required_approvals(self, case_id, requested_by="system"):
        created = []

        if self.requires_closure_approval(case_id):
            if not self._has_pending_or_approved(case_id, "CLOSURE_APPROVAL"):
                created.append(
                    self.create_approval_request(
                        case_id=case_id,
                        approval_type="CLOSURE_APPROVAL",
                        requested_by=requested_by,
                        approver="manager",
                        reason="Case closure requires manager approval.",
                    )
                )

        if self.requires_export_control_review(case_id):
            if not self._has_pending_or_approved(case_id, "EXPORT_CONTROL_REVIEW"):
                created.append(
                    self.create_approval_request(
                        case_id=case_id,
                        approval_type="EXPORT_CONTROL_REVIEW",
                        requested_by=requested_by,
                        approver="legal_export_control",
                        reason="Export-control indicators require legal/compliance review.",
                    )
                )

        return created

    def _resolve_approval(self, approval_id, status, actor, notes=None):
        with self.ledger._connect() as con:
            row = con.execute(
                """
                SELECT *
                FROM case_approvals
                WHERE approval_id = ?
                """,
                (approval_id,),
            ).fetchone()

            if not row:
                return False

            approval = dict(row)
            case_id = approval["case_id"]

            con.execute(
                """
                UPDATE case_approvals
                SET
                    status = ?,
                    resolved_by = ?,
                    resolved_at_ms = ?,
                    resolution_notes = ?,
                    updated_at_ms = ?
                WHERE approval_id = ?
                """,
                (
                    status,
                    actor,
                    _now_ms(),
                    notes,
                    _now_ms(),
                    approval_id,
                ),
            )

            self._log_case_event(
                con,
                case_id,
                f"APPROVAL_{status}",
                f"{approval.get('approval_type')} approval {status.lower()}",
                {
                    "approval_id": approval_id,
                    "approval_type": approval.get("approval_type"),
                    "actor": actor,
                    "notes": notes,
                },
            )

            con.commit()

        return True

    def _has_pending_or_approved(self, case_id, approval_type):
        with self.ledger._connect() as con:
            row = con.execute(
                """
                SELECT approval_id
                FROM case_approvals
                WHERE case_id = ?
                  AND approval_type = ?
                  AND status IN ('PENDING', 'APPROVED')
                LIMIT 1
                """,
                (case_id, approval_type),
            ).fetchone()

            return row is not None

    def _log_case_event(self, con, case_id, event_type, message, metadata=None):
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
                    "INFO",
                    message,
                    _now_ms(),
                    json.dumps(metadata),
                ),
            )
        except Exception:
            pass