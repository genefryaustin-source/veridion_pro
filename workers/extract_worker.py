import json
import time
import traceback

from core.storage.factory import build_storage
from core.pipeline.sqlite_queue import SQLitePipelineQueue


POLL_INTERVAL_SECONDS = 5
WORKER_ID = "extract_worker_1"


def _now_ms():
    return int(time.time() * 1000)


def process_extract_job(storage, queue, job):
    ledger = storage.ledger

    payload = job.get("payload") or {}

    print("\n========================")
    print("EXTRACT JOB CLAIMED")
    print("========================")

    print(json.dumps(job, indent=2, default=str))

    evidence_id = job.get("evidence_id")

    if not evidence_id:
        raise RuntimeError(
            "EXTRACT job missing evidence_id"
        )

    with ledger._connect() as con:

        # -----------------------------------
        # LOAD EVIDENCE
        # -----------------------------------
        evidence = con.execute(
            """
            SELECT *
            FROM evidence_records
            WHERE evidence_id = ?
            """,
            (evidence_id,),
        ).fetchone()

        if not evidence:
            raise RuntimeError(
                f"Evidence not found: {evidence_id}"
            )

        evidence = dict(evidence)

        metadata = {}

        try:
            metadata = json.loads(
                evidence.get("metadata_json") or "{}"
            )

            print("\nMETADATA:")
            print(json.dumps(metadata, indent=2))
        except Exception:
            metadata = {}

        content_type = (
            evidence.get("content_type")
            or ""
        ).lower()

        storage_uri = evidence.get("storage_uri")

        print("\nEVIDENCE LOADED")
        print("CONTENT TYPE:", content_type)
        print("STORAGE URI:", storage_uri)

        # -----------------------------------
        # SIMULATED CONTENT LOAD
        # -----------------------------------
        #
        # Later:
        # - load bytes from vault/S3/disk
        # - stream large artifacts
        # - support PDFs/DOCX/XLSX/etc
        #
        # For now:
        #
        # use metadata body_text
        #
        # -----------------------------------
        extracted_text = metadata.get(
            "body_text"
        ) or ""

        extraction_status = "SUCCESS"

        # -----------------------------------
        # DETERMINE OCR REQUIREMENT
        # -----------------------------------
        needs_ocr = False

        if content_type.startswith("image/"):
            needs_ocr = True

        elif (
            content_type == "application/pdf"
            and len(extracted_text.strip()) < 20
        ):
            needs_ocr = True

        elif not extracted_text.strip():
            needs_ocr = True

        print("\nOCR REQUIRED:", needs_ocr)

        # -----------------------------------
        # PERSIST EXTRACTION ARTIFACT
        # -----------------------------------
        extraction_metadata = {
            "worker_id": WORKER_ID,
            "extraction_status": extraction_status,
            "extracted_length": len(extracted_text),
            "ocr_required": needs_ocr,
        }

        # -----------------------------------
        # PERSIST EXTRACTION ARTIFACT
        # -----------------------------------
        con.execute(
            """
            INSERT INTO evidence_events (
                evidence_id,
                run_id,
                event_type,
                created_at_ms,
                data_json
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                None,
                "TEXT_EXTRACTED",
                _now_ms(),
                json.dumps(
                    {
                        "text": extracted_text[:5000],
                        "metadata": {
                            "worker_id": WORKER_ID,
                            "extraction_status": extraction_status,
                            "ocr_required": needs_ocr,
                            "content_type": content_type,
                            "storage_uri": storage_uri,
                            "text_length": len(extracted_text),
                        }
                    }
                ),
            ),
        )

        # -----------------------------------
        # COMMIT EXTRACTION EVENT
        # -----------------------------------
        con.commit()

    # -----------------------------------
    # OCR PATH
    # -----------------------------------
    if needs_ocr:

        ocr_job_id = queue.enqueue(
            stage="OCR",
            tenant_id=job.get("tenant_id"),
            mailbox=job.get("mailbox"),
            evidence_id=evidence_id,
            parent_job_id=job.get("job_id"),
            payload={
                "evidence_id": evidence_id,
                "content_type": content_type,
            },
        )

        print("\nENQUEUED OCR JOB:")
        print(ocr_job_id)

    # -----------------------------------
    # DETECT PATH
    # -----------------------------------
    else:

        detect_job_id = queue.enqueue(
            stage="DETECT",
            tenant_id=job.get("tenant_id"),
            mailbox=job.get("mailbox"),
            evidence_id=evidence_id,
            parent_job_id=job.get("job_id"),
            payload={
                "evidence_id": evidence_id,
                "content_type": content_type,
            },
        )

        print("\nENQUEUED DETECT JOB:")
        print(detect_job_id)

    # -----------------------------------
    # COMPLETE EXTRACT
    # -----------------------------------
    queue.complete(
        job["job_id"],
        message="EXTRACT COMPLETED"
    )

    print("\nEXTRACT COMPLETED")


def main():

    print("\n========================")
    print("EXTRACT WORKER STARTED")
    print("========================")

    storage = build_storage()

    queue = SQLitePipelineQueue(
        storage.ledger
    )

    while True:

        try:

            recovered = queue.recover_stale_jobs()

            if recovered:

                print(
                    f"\nRECOVERED STALE JOBS: "
                    f"{recovered}"
                )

            job = queue.claim_next(
                stage="EXTRACT",
                worker_id=WORKER_ID,
                lease_seconds=300,
            )

            if not job:

                time.sleep(
                    POLL_INTERVAL_SECONDS
                )

                continue

            process_extract_job(
                storage=storage,
                queue=queue,
                job=job,
            )

        except Exception as e:

            print("\nEXTRACT WORKER ERROR")
            print(str(e))

            traceback.print_exc()

            time.sleep(5)


if __name__ == "__main__":
    main()