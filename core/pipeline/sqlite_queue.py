import json
import time
import uuid
from typing import Any, Dict, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _new_id() -> str:
    return uuid.uuid4().hex


class SQLitePipelineQueue:
    """
    SQLite-backed pipeline queue.

    This is the local/dev queue backend. Later, this can be replaced with
    SQS/Kafka/Redis without changing the workers if workers only call this API.
    """

    def __init__(self, ledger):
        self.ledger = ledger

    def _connect(self):
        if hasattr(self.ledger, "_connect"):
            return self.ledger._connect()

        if hasattr(self.ledger, "connect"):
            return self.ledger.connect()

        raise RuntimeError("Ledger does not expose _connect() or connect().")

    # -----------------------------------
    # ENQUEUE
    # -----------------------------------
    def enqueue(
        self,
        stage: str,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        mailbox: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        alert_id: Optional[int] = None,
        parent_job_id: Optional[str] = None,
        max_attempts: int = 5,
    ) -> str:

        job_id = _new_id()
        now = _now_ms()

        payload_json = json.dumps(payload or {}, default=str)

        with self._connect() as con:
            con.execute(
                """
                INSERT INTO pipeline_jobs (
                    job_id,
                    stage,
                    status,
                    tenant_id,
                    mailbox,
                    case_id,
                    evidence_id,
                    alert_id,
                    parent_job_id,
                    payload_json,
                    attempts,
                    max_attempts,
                    worker_id,
                    lease_expires_ms,
                    last_error,
                    created_at_ms,
                    updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    stage,
                    "PENDING",
                    tenant_id,
                    mailbox,
                    case_id,
                    evidence_id,
                    alert_id,
                    parent_job_id,
                    payload_json,
                    0,
                    max_attempts,
                    None,
                    None,
                    None,
                    now,
                    now,
                ),
            )

            self._record_event(
                con=con,
                job_id=job_id,
                stage=stage,
                status="PENDING",
                message="Job enqueued",
            )

            con.commit()

        return job_id

    # -----------------------------------
    # CLAIM NEXT JOB
    # -----------------------------------
    def claim_next(
        self,
        stage: str,
        worker_id: str,
        lease_seconds: int = 300,
    ) -> Optional[Dict[str, Any]]:

        now = _now_ms()
        lease_expires_ms = now + lease_seconds * 1000

        with self._connect() as con:
            row = con.execute(
                """
                SELECT *
                FROM pipeline_jobs
                WHERE stage = ?
                  AND (
                        status = 'PENDING'
                        OR (
                            status = 'PROCESSING'
                            AND lease_expires_ms IS NOT NULL
                            AND lease_expires_ms < ?
                        )
                  )
                ORDER BY created_at_ms ASC
                LIMIT 1
                """,
                (
                    stage,
                    now,
                ),
            ).fetchone()

            if not row:
                return None

            job = dict(row)
            job_id = job["job_id"]

            updated = con.execute(
                """
                UPDATE pipeline_jobs
                SET
                    status = 'PROCESSING',
                    worker_id = ?,
                    lease_expires_ms = ?,
                    attempts = attempts + 1,
                    updated_at_ms = ?
                WHERE job_id = ?
                  AND (
                        status = 'PENDING'
                        OR (
                            status = 'PROCESSING'
                            AND lease_expires_ms IS NOT NULL
                            AND lease_expires_ms < ?
                        )
                  )
                """,
                (
                    worker_id,
                    lease_expires_ms,
                    now,
                    job_id,
                    now,
                ),
            )

            if updated.rowcount != 1:
                con.commit()
                return None

            self._record_event(
                con=con,
                job_id=job_id,
                stage=stage,
                status="PROCESSING",
                message=f"Job claimed by {worker_id}",
            )

            con.commit()

            refreshed = con.execute(
                """
                SELECT *
                FROM pipeline_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            ).fetchone()

            return self._hydrate_job(dict(refreshed))

    # -----------------------------------
    # COMPLETE JOB
    # -----------------------------------
    def complete(
        self,
        job_id: str,
        message: str = "Job completed",
    ) -> None:

        now = _now_ms()

        with self._connect() as con:
            row = con.execute(
                """
                SELECT stage
                FROM pipeline_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            ).fetchone()

            if not row:
                return

            stage = row["stage"]

            con.execute(
                """
                UPDATE pipeline_jobs
                SET
                    status = 'COMPLETED',
                    worker_id = NULL,
                    lease_expires_ms = NULL,
                    last_error = NULL,
                    updated_at_ms = ?
                WHERE job_id = ?
                """,
                (
                    now,
                    job_id,
                ),
            )

            self._record_event(
                con=con,
                job_id=job_id,
                stage=stage,
                status="COMPLETED",
                message=message,
            )

            con.commit()

    # -----------------------------------
    # FAIL JOB
    # -----------------------------------
    def fail(
        self,
        job_id: str,
        error: str,
        retry: bool = True,
    ) -> None:

        now = _now_ms()

        with self._connect() as con:
            row = con.execute(
                """
                SELECT stage, attempts, max_attempts
                FROM pipeline_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            ).fetchone()

            if not row:
                return

            stage = row["stage"]
            attempts = int(row["attempts"] or 0)
            max_attempts = int(row["max_attempts"] or 5)

            should_retry = retry and attempts < max_attempts

            next_status = "PENDING" if should_retry else "FAILED"

            con.execute(
                """
                UPDATE pipeline_jobs
                SET
                    status = ?,
                    worker_id = NULL,
                    lease_expires_ms = NULL,
                    last_error = ?,
                    updated_at_ms = ?
                WHERE job_id = ?
                """,
                (
                    next_status,
                    str(error)[:4000],
                    now,
                    job_id,
                ),
            )

            self._record_event(
                con=con,
                job_id=job_id,
                stage=stage,
                status=next_status,
                message=str(error)[:4000],
            )

            con.commit()

    # -----------------------------------
    # HEARTBEAT / EXTEND LEASE
    # -----------------------------------
    def extend_lease(
        self,
        job_id: str,
        worker_id: str,
        lease_seconds: int = 300,
    ) -> bool:

        now = _now_ms()
        lease_expires_ms = now + lease_seconds * 1000

        with self._connect() as con:
            result = con.execute(
                """
                UPDATE pipeline_jobs
                SET
                    lease_expires_ms = ?,
                    updated_at_ms = ?
                WHERE job_id = ?
                  AND worker_id = ?
                  AND status = 'PROCESSING'
                """,
                (
                    lease_expires_ms,
                    now,
                    job_id,
                    worker_id,
                ),
            )

            con.commit()

            return result.rowcount == 1

    # -----------------------------------
    # RECOVER STALE JOBS
    # -----------------------------------
    def recover_stale_jobs(
        self,
        max_age_ms: Optional[int] = None,
    ) -> int:

        now = _now_ms()

        with self._connect() as con:
            rows = con.execute(
                """
                SELECT job_id, stage
                FROM pipeline_jobs
                WHERE status = 'PROCESSING'
                  AND lease_expires_ms IS NOT NULL
                  AND lease_expires_ms < ?
                """,
                (now,),
            ).fetchall()

            recovered = 0

            for row in rows:
                job_id = row["job_id"]
                stage = row["stage"]

                con.execute(
                    """
                    UPDATE pipeline_jobs
                    SET
                        status = 'PENDING',
                        worker_id = NULL,
                        lease_expires_ms = NULL,
                        updated_at_ms = ?
                    WHERE job_id = ?
                    """,
                    (
                        now,
                        job_id,
                    ),
                )

                self._record_event(
                    con=con,
                    job_id=job_id,
                    stage=stage,
                    status="PENDING",
                    message="Recovered stale processing job",
                )

                recovered += 1

            con.commit()

        return recovered

    # -----------------------------------
    # READ JOB
    # -----------------------------------
    def get_job(
        self,
        job_id: str,
    ) -> Optional[Dict[str, Any]]:

        with self._connect() as con:
            row = con.execute(
                """
                SELECT *
                FROM pipeline_jobs
                WHERE job_id = ?
                """,
                (job_id,),
            ).fetchone()

            if not row:
                return None

            return self._hydrate_job(dict(row))

    # -----------------------------------
    # LIST JOBS
    # -----------------------------------
    def list_jobs(
        self,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ):

        query = """
            SELECT *
            FROM pipeline_jobs
            WHERE 1 = 1
        """

        params = []

        if stage:
            query += " AND stage = ?"
            params.append(stage)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += """
            ORDER BY created_at_ms DESC
            LIMIT ?
        """

        params.append(limit)

        with self._connect() as con:
            rows = con.execute(
                query,
                tuple(params),
            ).fetchall()

            return [
                self._hydrate_job(dict(r))
                for r in rows
            ]

    # -----------------------------------
    # EVENTS
    # -----------------------------------
    def get_events(
        self,
        job_id: str,
    ):

        with self._connect() as con:
            rows = con.execute(
                """
                SELECT *
                FROM pipeline_events
                WHERE job_id = ?
                ORDER BY created_at_ms ASC
                """,
                (job_id,),
            ).fetchall()

            return [
                dict(r)
                for r in rows
            ]

    # -----------------------------------
    # INTERNAL HELPERS
    # -----------------------------------
    def _record_event(
        self,
        con,
        job_id: str,
        stage: str,
        status: str,
        message: str,
    ) -> None:

        con.execute(
            """
            INSERT INTO pipeline_events (
                event_id,
                job_id,
                stage,
                status,
                message,
                created_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                _new_id(),
                job_id,
                stage,
                status,
                message,
                _now_ms(),
            ),
        )

    def _hydrate_job(
        self,
        job: Dict[str, Any],
    ) -> Dict[str, Any]:

        payload_raw = job.get("payload_json")

        try:
            job["payload"] = json.loads(payload_raw or "{}")
        except Exception:
            job["payload"] = {}

        return job