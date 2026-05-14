import time


class CaseCorrelationEngine:

    def __init__(self, storage):
        self.storage = storage
        self.ledger = storage.ledger

    def find_matching_case(
        self,
        category,
        sender=None,
        attachment_sha=None,
        subject=None,
        source="email",
        lookback_hours=24,
    ):

        now_ms = int(time.time() * 1000)

        lookback_ms = (
            lookback_hours
            * 60
            * 60
            * 1000
        )

        cutoff = now_ms - lookback_ms

        with self.ledger._connect() as con:

            rows = con.execute("""
                SELECT
                    case_id,
                    category,
                    source,
                    sender,
                    subject,
                    attachment_sha,
                    status,
                    created_at_ms
                FROM cases
                WHERE created_at_ms >= ?
                AND status NOT IN (
                    'CLOSED',
                    'FALSE_POSITIVE'
                )
                ORDER BY created_at_ms DESC
            """, (
                cutoff,
            )).fetchall()

        for row in rows:

            # --------------------------------
            # CATEGORY MATCH
            # --------------------------------
            if row["category"] != category:
                continue

            # --------------------------------
            # ATTACHMENT HASH MATCH
            # --------------------------------
            if (
                attachment_sha
                and row["attachment_sha"]
                and row["attachment_sha"]
                == attachment_sha
            ):
                return {
                    "case_id": row["case_id"],
                    "reason": "ATTACHMENT_SHA_MATCH",
                }

            # --------------------------------
            # SENDER MATCH
            # --------------------------------
            if (
                    sender
                    and row["sender"]
                    and row["sender"].lower()
                    == sender.lower()
            ):
                return {
                    "case_id": row["case_id"],
                    "reason": "SENDER_MATCH",
                }

            # --------------------------------
            # SUBJECT MATCH
            # --------------------------------
            if (
                    subject
                    and row["subject"]
                    and subject.lower()
                    in row["subject"].lower()
            ):
                return {
                    "case_id": row["case_id"],
                    "reason": "SUBJECT_MATCH",
                }

        return None