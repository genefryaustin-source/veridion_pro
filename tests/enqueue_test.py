from core.storage.factory import build_storage
from core.pipeline.sqlite_queue import (
    SQLitePipelineQueue
)

storage = build_storage()

queue = SQLitePipelineQueue(
    storage.ledger
)

job_id = queue.enqueue(
    stage="INGEST",
    tenant_id="tenant_demo",
    mailbox="test@example.com",
    payload={
        "provider": "gmail",
        "message_id": "itar_test_002",
        "subject": "ITAR Technical Data",
        "body_text": """
        This email contains ITAR-controlled
        technical data and CUI export material.
        """,
    },
)

print(job_id)