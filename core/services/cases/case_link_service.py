import time
import uuid
import json


def _now_ms():
    return int(time.time() * 1000)


class CaseLinkService:

    def __init__(self, ledger):
        self.ledger = ledger

    # =========================================================
    # CASE ↔ EVIDENCE
    # =========================================================

    def link_case_evidence(
        self,
        case_id,
        evidence_id,
    ):

        if not case_id or not evidence_id:
            return False

        with self.ledger._connect() as con:

            # -----------------------------------------
            # NEW TABLE
            # -----------------------------------------
            exists = con.execute(
                """
                SELECT id
                FROM case_evidence
                WHERE case_id = ?
                  AND evidence_id = ?
                """,
                (
                    case_id,
                    evidence_id,
                ),
            ).fetchone()

            if not exists:

                con.execute(
                    """
                    INSERT INTO case_evidence (
                        case_id,
                        evidence_id,
                        linked_at_ms
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        case_id,
                        evidence_id,
                        _now_ms(),
                    ),
                )

            # -----------------------------------------
            # LEGACY TABLE MIRROR
            # -----------------------------------------
            legacy_exists = con.execute(
                """
                SELECT 1
                FROM case_evidence_map
                WHERE case_id = ?
                  AND evidence_id = ?
                """,
                (
                    case_id,
                    evidence_id,
                ),
            ).fetchone()

            if not legacy_exists:

                con.execute(
                    """
                    INSERT INTO case_evidence_map (
                        case_id,
                        evidence_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        case_id,
                        evidence_id,
                    ),
                )

            # -----------------------------------------
            # AUDIT EVENT
            # -----------------------------------------
            self._create_case_event(
                con=con,
                case_id=case_id,
                event_type="EVIDENCE_LINKED",
                message=f"Evidence linked: {evidence_id}",
                severity="INFO",
                metadata={
                    "evidence_id": evidence_id,
                },
            )

        return True

    def get_case_evidence_ids(
        self,
        case_id,
    ):

        evidence_ids = set()

        with self.ledger._connect() as con:

            # -----------------------------------------
            # NEW TABLE
            # -----------------------------------------
            try:

                rows = con.execute(
                    """
                    SELECT evidence_id
                    FROM case_evidence
                    WHERE case_id = ?
                    """,
                    (case_id,),
                ).fetchall()

                for r in rows:
                    evidence_ids.add(
                        r["evidence_id"]
                    )

            except Exception:
                pass

            # -----------------------------------------
            # LEGACY TABLE
            # -----------------------------------------
            try:

                rows = con.execute(
                    """
                    SELECT evidence_id
                    FROM case_evidence_map
                    WHERE case_id = ?
                    """,
                    (case_id,),
                ).fetchall()

                for r in rows:
                    evidence_ids.add(
                        r["evidence_id"]
                    )

            except Exception:
                pass

        return list(evidence_ids)

    # =========================================================
    # CASE ↔ ALERT
    # =========================================================

    def link_case_alert(
        self,
        case_id,
        alert_id,
    ):

        if not case_id or not alert_id:
            return False

        with self.ledger._connect() as con:

            con.execute(
                """
                UPDATE alerts
                SET case_id = ?
                WHERE id = ?
                """,
                (
                    case_id,
                    alert_id,
                ),
            )

            self._create_case_event(
                con=con,
                case_id=case_id,
                event_type="ALERT_LINKED",
                message=f"Alert linked: {alert_id}",
                severity="INFO",
                metadata={
                    "alert_id": alert_id,
                },
            )

        return True

    def get_case_alerts(
        self,
        case_id,
    ):

        with self.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT *
                FROM alerts
                WHERE case_id = ?
                ORDER BY created_at_ms DESC
                """,
                (case_id,),
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    # =========================================================
    # CASE ↔ ENTITY
    # =========================================================

    def link_case_entity(
        self,
        case_id,
        entity_id,
        evidence_id=None,
    ):

        if not case_id or not entity_id:
            return False

        with self.ledger._connect() as con:

            exists = con.execute(
                """
                SELECT id
                FROM case_entities
                WHERE case_id = ?
                  AND entity_id = ?
                """,
                (
                    case_id,
                    entity_id,
                ),
            ).fetchone()

            if not exists:

                con.execute(
                    """
                    INSERT INTO case_entities (
                        case_id,
                        entity_id,
                        evidence_id,
                        created_at_ms
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        case_id,
                        entity_id,
                        evidence_id,
                        _now_ms(),
                    ),
                )

                self._create_case_event(
                    con=con,
                    case_id=case_id,
                    event_type="ENTITY_LINKED",
                    message=f"Entity linked: {entity_id}",
                    severity="INFO",
                    metadata={
                        "entity_id": entity_id,
                        "evidence_id": evidence_id,
                    },
                )

        return True

    def get_case_entities(
        self,
        case_id,
    ):

        with self.ledger._connect() as con:

            rows = con.execute(
                """
                SELECT
                    ce.case_id,
                    ce.evidence_id,

                    e.entity_id,
                    e.entity_type,
                    e.entity_value,
                    e.normalized_value,
                    e.confidence,
                    e.metadata_json,
                    e.created_at_ms

                FROM case_entities ce

                JOIN entities e
                    ON ce.entity_id = e.entity_id

                WHERE ce.case_id = ?

                ORDER BY e.entity_type,
                         e.entity_value
                """,
                (case_id,),
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    # =========================================================
    # CASE HYDRATION
    # =========================================================

    def hydrate_case_bundle(
        self,
        case_id,
    ):

        return {
            "case_id": case_id,
            "evidence_ids": self.get_case_evidence_ids(
                case_id
            ),
            "alerts": self.get_case_alerts(
                case_id
            ),
            "entities": self.get_case_entities(
                case_id
            ),
        }

    # =========================================================
    # INTERNAL EVENT LOGGER
    # =========================================================

    def _create_case_event(
        self,
        con,
        case_id,
        event_type,
        message,
        severity="INFO",
        metadata=None,
    ):

        metadata = metadata or {}

        # -----------------------------------------
        # case_events
        # -----------------------------------------
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

        # -----------------------------------------
        # case_audit_log
        # -----------------------------------------
        try:

            con.execute(
                """
                INSERT INTO case_audit_log (
                    case_id,
                    action,
                    performed_by,
                    details
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    case_id,
                    event_type,
                    "system",
                    message,
                ),
            )

        except Exception:
            pass