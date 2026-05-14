import hashlib
import json
import time
import traceback

from core.storage.factory import build_storage
from core.pipeline.sqlite_queue import SQLitePipelineQueue


POLL_INTERVAL_SECONDS = 5
WORKER_ID = "ingest_worker_1"


def _now_ms():
    return int(time.time() * 1000)


def _stable_id(*parts):
    raw = "|".join(str(p or "") for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def process_ingest_job(storage, queue, job):
    ledger = storage.ledger
    payload = job.get("payload") or {}

    print("\n========================")
    print("INGEST JOB CLAIMED")
    print("========================")
    print(json.dumps(job, indent=2, default=str))

    tenant_id = job.get("tenant_id") or "tenant_demo"
    provider = payload.get("provider") or "unknown"
    mailbox = job.get("mailbox") or payload.get("mailbox") or "unknown"
    message_id = payload.get("message_id") or _stable_id(tenant_id, mailbox, _now_ms())

    now_ms = _now_ms()
    run_id = job.get("job_id")

    subject = payload.get("subject") or "Simulated Subject"
    sender = payload.get("sender") or "sender@example.com"
    body_text = payload.get("body_text") or f"Simulated email body for message {message_id}"
    email_bytes = body_text.encode("utf-8", errors="ignore")

    sha256 = hashlib.sha256(email_bytes).hexdigest()
    evidence_id = _stable_id(tenant_id, mailbox, message_id, "email")

    print("\nPROVIDER:", provider)
    print("MAILBOX:", mailbox)
    print("MESSAGE ID:", message_id)
    print("EVIDENCE ID:", evidence_id)

    with ledger._connect() as con:
        # -----------------------------------
        # RUN RECORD
        # -----------------------------------
        con.execute(
            """
            INSERT OR IGNORE INTO runs (
                run_id,
                provider,
                mailbox,
                started_at_ms,
                messages_scanned,
                attachments_scanned,
                cui_flagged
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                provider,
                mailbox,
                now_ms,
                1,
                0,
                0,
            ),
        )

        # -----------------------------------
        # EMAIL RECORD
        # -----------------------------------
        con.execute(
            """
            INSERT OR IGNORE INTO emails (
                message_id,
                mailbox,
                subject,
                sender,
                received_at,
                snippet,
                body_text,
                body_html,
                raw_headers,
                has_attachments,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                mailbox,
                subject,
                sender,
                str(now_ms),
                body_text[:250],
                body_text,
                None,
                None,
                0,
                str(now_ms),
            ),
        )

        # -----------------------------------
        # EMAIL AS EVIDENCE
        # -----------------------------------
        con.execute(
            """
            INSERT OR IGNORE INTO evidence_records (
                evidence_id,
                sha256,
                size_bytes,
                content_type,
                storage_uri,
                suggested_name,
                created_at_ms,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                sha256,
                len(email_bytes),
                "message/rfc822",
                f"memory://email/{message_id}",
                f"{message_id}.eml",
                now_ms,
                json.dumps(
                    {
                        "tenant_id": tenant_id,
                        "provider": provider,
                        "mailbox": mailbox,
                        "message_id": message_id,
                        "artifact_type": "email",
                        "body_text": body_text,
                    }
                ),
            ),
        )

        # -----------------------------------
        # CUSTODY EVENT
        # -----------------------------------
        con.execute(
            """
            INSERT INTO custody_events (
                run_id,
                evidence_id,
                event_type,
                actor,
                timestamp_ms,
                details_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                evidence_id,
                "INGESTED",
                WORKER_ID,
                now_ms,
                json.dumps(
                    {
                        "message_id": message_id,
                        "provider": provider,
                        "mailbox": mailbox,
                    }
                ),
            ),
        )

        con.commit()

    # -----------------------------------
    # ENQUEUE EXTRACT FOR EMAIL EVIDENCE
    # -----------------------------------
    extract_job_id = queue.enqueue(
        stage="EXTRACT",
        tenant_id=tenant_id,
        mailbox=mailbox,
        evidence_id=evidence_id,
        parent_job_id=job.get("job_id"),
        payload={
            "provider": provider,
            "message_id": message_id,
            "evidence_id": evidence_id,
            "artifact_type": "email",
        },
    )

    print("\nENQUEUED EXTRACT JOB:")
    print(extract_job_id)

    queue.complete(
        job["job_id"],
        message="INGEST COMPLETED"
    )

    print("\nINGEST COMPLETED")


def main():
    print("\n========================")
    print("INGEST WORKER STARTED")
    print("========================")

    storage = build_storage()
    queue = SQLitePipelineQueue(storage.ledger)

    while True:
        try:
            recovered = queue.recover_stale_jobs()

            if recovered:
                print(f"\nRECOVERED STALE JOBS: {recovered}")

            job = queue.claim_next(
                stage="INGEST",
                worker_id=WORKER_ID,
                lease_seconds=300,
            )

            if not job:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            process_ingest_job(
                storage=storage,
                queue=queue,
                job=job,
            )

        except Exception as e:
            print("\nINGEST WORKER ERROR")
            print(str(e))
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    main()