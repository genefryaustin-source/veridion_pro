import json
import time

from core.storage.factory import build_storage
from core.pipeline.sqlite_queue import (
    SQLitePipelineQueue
)


def main():

    print("\n========================")
    print("PIPELINE QUEUE TEST")
    print("========================\n")

    storage = build_storage()

    queue = SQLitePipelineQueue(
        storage.ledger
    )

    # -----------------------------------
    # ENQUEUE
    # -----------------------------------
    print("1. ENQUEUE JOB")

    job_id = queue.enqueue(
        stage="INGEST",
        tenant_id="tenant_demo",
        mailbox="test@example.com",
        payload={
            "provider": "gmail",
            "message_id": "abc123",
        },
    )

    print("JOB ID:", job_id)

    # -----------------------------------
    # READ BACK
    # -----------------------------------
    print("\n2. READ JOB")

    job = queue.get_job(job_id)

    print(
        json.dumps(
            job,
            indent=2,
            default=str
        )
    )

    # -----------------------------------
    # CLAIM
    # -----------------------------------
    print("\n3. CLAIM JOB")

    claimed = queue.claim_next(
        stage="INGEST",
        worker_id="worker_1",
        lease_seconds=60,
    )

    print(
        json.dumps(
            claimed,
            indent=2,
            default=str
        )
    )

    if not claimed:

        raise RuntimeError(
            "FAILED TO CLAIM JOB"
        )

    # -----------------------------------
    # EVENTS
    # -----------------------------------
    print("\n4. EVENTS AFTER CLAIM")

    events = queue.get_events(job_id)

    for e in events:

        print(
            f"[{e['status']}] "
            f"{e['message']}"
        )

    # -----------------------------------
    # EXTEND LEASE
    # -----------------------------------
    print("\n5. EXTEND LEASE")

    ok = queue.extend_lease(
        job_id=job_id,
        worker_id="worker_1",
        lease_seconds=120,
    )

    print("LEASE EXTENDED:", ok)

    # -----------------------------------
    # COMPLETE
    # -----------------------------------
    print("\n6. COMPLETE JOB")

    queue.complete(
        job_id,
        message="INGEST COMPLETED"
    )

    completed = queue.get_job(
        job_id
    )

    print(
        json.dumps(
            completed,
            indent=2,
            default=str
        )
    )

    # -----------------------------------
    # FINAL EVENTS
    # -----------------------------------
    print("\n7. FINAL EVENTS")

    events = queue.get_events(job_id)

    for e in events:

        print(
            f"[{e['status']}] "
            f"{e['message']}"
        )

    print("\n========================")
    print("PIPELINE TEST COMPLETE")
    print("========================\n")


if __name__ == "__main__":
    main()