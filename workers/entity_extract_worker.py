import json
import re
import time
import traceback
import uuid

from core.storage.factory import build_storage
from core.pipeline.sqlite_queue import SQLitePipelineQueue


POLL_INTERVAL_SECONDS = 5
WORKER_ID = "entity_extract_worker_1"


def _now_ms():
    return int(time.time() * 1000)


ENTITY_PATTERNS = [
    {
        "type": "EMAIL",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    },
    {
        "type": "IP_ADDRESS",
        "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    },
    {
        "type": "DOMAIN",
        "pattern": r"\b[a-zA-Z0-9.-]+\.(com|gov|mil|edu|net|org)\b",
    },
    {
        "type": "ITAR_REFERENCE",
        "pattern": r"\bITAR\b|\bEAR\b|\bUSML\b",
    },
    {
        "type": "CREDENTIAL_TERM",
        "pattern": r"\bpassword\b|\btoken\b|\bapi key\b|\bsecret\b",
    },

    {
        "type": "CUI_MARKING",
        "pattern": r"\bCUI\b",
    },
    {
        "type": "TECHNICAL_DATA",
        "pattern": r"\btechnical data\b",
    },
    {
        "type": "FILE_NAME",
        "pattern": r"\b[\w,\s-]+\.(pdf|docx|xlsx|pptx|zip)\b",
    },
    {
        "type": "GOVERNMENT_PROGRAM",
        "pattern": r"\bITAR\b|\bEAR\b|\bUSML\b|\bDFARS\b",
    }
]


def _load_latest_event(con, evidence_id, event_type):

    row = con.execute(
        """
        SELECT data_json
        FROM evidence_events
        WHERE evidence_id = ?
          AND event_type = ?
        ORDER BY created_at_ms DESC
        LIMIT 1
        """,
        (
            evidence_id,
            event_type,
        ),
    ).fetchone()

    if not row:
        return {}

    try:
        return json.loads(
            row["data_json"] or "{}"
        )
    except Exception:
        return {}


def _extract_entities(text):

    entities = []

    for rule in ENTITY_PATTERNS:

        entity_type = rule["type"]
        pattern = rule["pattern"]

        for match in re.finditer(
            pattern,
            text or "",
            re.IGNORECASE,
        ):

            value = match.group(0).strip()

            entities.append(
                {
                    "entity_type": entity_type,
                    "entity_value": value,
                    "normalized_value": value.lower(),
                    "confidence": 1.0,
                }
            )

    return entities


def process_entity_extract_job(
    storage,
    queue,
    job,
):
    ledger = storage.ledger

    payload = job.get("payload") or {}

    evidence_id = (
        job.get("evidence_id")
        or payload.get("evidence_id")
    )

    print("\n========================")
    print("ENTITY_EXTRACT JOB CLAIMED")
    print("========================")
    print(json.dumps(job, indent=2, default=str))

    if not evidence_id:
        raise RuntimeError(
            "ENTITY_EXTRACT job missing evidence_id"
        )

    with ledger._connect() as con:

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

        text_event = _load_latest_event(
            con,
            evidence_id,
            "TEXT_EXTRACTED",
        )

        detection_event = _load_latest_event(
            con,
            evidence_id,
            "DETECTION_RESULT",
        )

        extracted_text = (
            text_event.get("text")
            or ""
        )

        print("\nEXTRACTED TEXT LENGTH:")
        print(len(extracted_text))

        entities = _extract_entities(
            extracted_text
        )

        print("\nENTITIES DETECTED:")
        print(len(entities))

        entity_ids = []

        for entity in entities:

            entity_id = uuid.uuid4().hex

            con.execute(
                """
                INSERT INTO entities (
                    entity_id,
                    evidence_id,
                    entity_type,
                    entity_value,
                    normalized_value,
                    confidence,
                    metadata_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity_id,
                    evidence_id,
                    entity["entity_type"],
                    entity["entity_value"],
                    entity["normalized_value"],
                    entity["confidence"],
                    json.dumps(
                        {
                            "worker_id": WORKER_ID,
                            "detection_categories": detection_event.get(
                                "categories",
                                [],
                            ),
                        }
                    ),
                    _now_ms(),
                ),
            )

            entity_ids.append(
                (
                    entity_id,
                    entity,
                )
            )

            print(
                f"ENTITY: "
                f"{entity['entity_type']} "
                f"=> "
                f"{entity['entity_value']}"
            )
        # -----------------------------------
        # LOAD RELATED CASE
        # -----------------------------------
        case_id = None

        alert_id = payload.get("alert_id")

        if alert_id:

            alert_row = con.execute(
                """
                SELECT case_id
                FROM alerts
                WHERE id = ?
                """,
                (alert_id,),
            ).fetchone()

            if alert_row:
                case_id = alert_row["case_id"]

        print("\nRELATED CASE:")
        print(case_id)

        # -----------------------------------
        # LINK ENTITY TO CASE
        # -----------------------------------
        if case_id:
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

            print(
                f"CASE ENTITY LINK: "
                f"{case_id} "
                f"<-> "
                f"{entity['entity_value']}"
            )
        # -----------------------------------
        # BUILD SIMPLE CO-OCCURRENCE EDGES
        # -----------------------------------
        for i in range(len(entity_ids)):

            for j in range(i + 1, len(entity_ids)):

                source_id, source_entity = entity_ids[i]
                target_id, target_entity = entity_ids[j]

                edge_id = uuid.uuid4().hex

                con.execute(
                    """
                    INSERT INTO relationship_edges (
                        edge_id,
                        source_entity_id,
                        target_entity_id,
                        relationship_type,
                        evidence_id,
                        metadata_json,
                        created_at_ms
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        edge_id,
                        source_id,
                        target_id,
                        "CO_OCCURRENCE",
                        evidence_id,
                        json.dumps(
                            {
                                "worker_id": WORKER_ID,
                            }
                        ),
                        _now_ms(),
                    ),
                )

        # -----------------------------------
        # PERSIST ENTITY EXTRACTION EVENT
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
                "ENTITY_EXTRACTION_RESULT",
                _now_ms(),
                json.dumps(
                    {
                        "entity_count": len(entities),
                        "relationship_count": max(
                            0,
                            len(entity_ids) - 1,
                        ),
                    }
                ),
            ),
        )

        con.commit()

    queue.complete(
        job["job_id"],
        message="ENTITY EXTRACTION COMPLETED",
    )

    print("\nENTITY EXTRACTION COMPLETED")


def main():

    print("\n========================")
    print("ENTITY EXTRACT WORKER STARTED")
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
                stage="ENTITY_EXTRACT",
                worker_id=WORKER_ID,
                lease_seconds=300,
            )

            if not job:

                time.sleep(
                    POLL_INTERVAL_SECONDS
                )

                continue

            process_entity_extract_job(
                storage=storage,
                queue=queue,
                job=job,
            )

        except Exception as e:

            print("\nENTITY EXTRACT WORKER ERROR")
            print(str(e))

            traceback.print_exc()

            time.sleep(5)


if __name__ == "__main__":
    main()