import json
import re
import time
import traceback

from core.storage.factory import build_storage
from core.pipeline.sqlite_queue import SQLitePipelineQueue
from core.ai.orchestration.detection_response_router import (
    route_detection,
)

from core.cases.case_manager import (
    ensure_case_for_alert,
)

POLL_INTERVAL_SECONDS = 5
WORKER_ID = "detect_worker_1"


def _now_ms():
    return int(time.time() * 1000)


DETECTION_RULES = [
    {
        "category": "CUI",
        "severity": "HIGH",
        "pattern": r"\bCUI\b|controlled unclassified information",
    },
    {
        "category": "EXPORT_CONTROL",
        "severity": "CRITICAL",
        "pattern": r"\bITAR\b|\bEAR\b|export[- ]controlled|EXPORT_CONTROL|defense article|technical data",
    },
    {
        "category": "PII_SSN",
        "severity": "HIGH",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
    },
    {
        "category": "PHI",
        "severity": "HIGH",
        "pattern": r"\bpatient\b|\bmedical record\b|\bdiagnosis\b|\bHIPAA\b",
    },
    {
        "category": "CREDENTIAL",
        "severity": "CRITICAL",
        "pattern": r"\bpassword\b|\bapi key\b|\bsecret key\b|\btoken\b|\bprivate key\b",
    },
    {
        "category": "EMAIL",
        "severity": "LOW",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    },
]


SEVERITY_RANK = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def _highest_severity(hits):
    if not hits:
        return "LOW"

    return max(
        (h.get("severity", "LOW") for h in hits),
        key=lambda s: SEVERITY_RANK.get(s, 0),
    )


def _load_latest_extracted_text(con, evidence_id):
    row = con.execute(
        """
        SELECT data_json
        FROM evidence_events
        WHERE evidence_id = ?
          AND event_type = 'TEXT_EXTRACTED'
        ORDER BY created_at_ms DESC
        LIMIT 1
        """,
        (evidence_id,),
    ).fetchone()

    if not row:
        return ""

    try:
        data = json.loads(row["data_json"] or "{}")
        return data.get("text") or ""
    except Exception:
        return ""


def _run_detection(text):
    hits = []

    for rule in DETECTION_RULES:
        for match in re.finditer(rule["pattern"], text or "", re.IGNORECASE):
            hits.append(
                {
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    return hits


def process_detect_job(storage, queue, job):
    ledger = storage.ledger
    payload = job.get("payload") or {}

    evidence_id = job.get("evidence_id") or payload.get("evidence_id")

    print("\n========================")
    print("DETECT JOB CLAIMED")
    print("========================")
    print(json.dumps(job, indent=2, default=str))

    if not evidence_id:
        raise RuntimeError("DETECT job missing evidence_id")

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
            raise RuntimeError(f"Evidence not found: {evidence_id}")

        evidence = dict(evidence)

        extracted_text = _load_latest_extracted_text(
            con,
            evidence_id,
        )

        print("\nEVIDENCE ID:", evidence_id)
        print("EXTRACTED TEXT LENGTH:", len(extracted_text))

        hits = _run_detection(extracted_text)
        severity = _highest_severity(hits)

        categories = sorted(set(h["category"] for h in hits))

        detection_result = {
            "worker_id": WORKER_ID,
            "evidence_id": evidence_id,
            "hit_count": len(hits),
            "severity": severity,
            "categories": categories,
            "hits": hits[:100],
        }

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
                "DETECTION_RESULT",
                _now_ms(),
                json.dumps(detection_result),
            ),
        )
        

        alert_id = None

        if hits:
            message = (
                f"{severity} detection on evidence {evidence_id}: "
                f"{', '.join(categories)}"
            )

            cur = con.execute(
                """
                INSERT INTO alerts (
                    evidence_id,
                    severity,
                    message,
                    created_at_ms,
                    resolved
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    severity,
                    message,
                    _now_ms(),
                    0,
                ),
            )

            alert_id = cur.lastrowid
            case_id = None

            try:

                case_id = ensure_case_for_alert(
                    storage=storage,
                    alert_id=alert_id,
                )

                print("\nCASE LINKED:", case_id)

            except Exception as case_exc:

                print("\nCASE CREATION FAILED")
                print(str(case_exc))
            print("\nALERT CREATED:", alert_id)
            print(message)
        else:
            print("\nNO DETECTION HITS")

        con.commit()

        # ------------------------------------------------------------------
        # AUTONOMOUS RESPONSE ROUTING
        # ------------------------------------------------------------------

        try:

            route_result = route_detection(
                storage,
                detection_result,

                tenant_id=job.get("tenant_id") or "default",
                actor=WORKER_ID,

                case_id=case_id,
                evidence_id=evidence_id,
                alert_id=alert_id,
                run_id=job.get("run_id"),

                autonomy_mode="ASSISTED",
                simulation_mode=True,
            )

            print("\nAUTONOMOUS RESPONSE ROUTED")
            print("ROUTE ID:", route_result.route_id)
            print("ROUTE OK:", route_result.ok)

            for response in route_result.response_results:
                print(
                    f"  ACTION={response.action} "
                    f"STATUS={response.status} "
                    f"OK={response.ok}"
                )

            # ----------------------------------------------------------
            # OPTIONAL CASE EVENT
            # ----------------------------------------------------------

            try:

                if (
                        case_id
                        and hasattr(ledger, "add_case_event")
                ):
                    ledger.add_case_event(
                        case_id=case_id,
                        event_type="AUTONOMOUS_RESPONSE_ROUTED",
                        actor=WORKER_ID,
                        details_json={
                            "route_id": route_result.route_id,
                            "ok": route_result.ok,
                            "response_count": len(
                                route_result.response_results
                            ),
                            "severity": severity,
                            "categories": categories,
                        },
                        created_at_ms=_now_ms(),
                    )

            except Exception as case_event_exc:

                print(
                    "\nCASE EVENT INSERT FAILED:",
                    str(case_event_exc),
                )

        except Exception as route_exc:

            print("\nAUTONOMOUS ROUTING FAILED")
            print(str(route_exc))
            traceback.print_exc()

            # ----------------------------------------------------------
            # FORENSIC EVENT
            # ----------------------------------------------------------

            try:

                if hasattr(ledger, "record_custody_event"):
                    ledger.record_custody_event(
                        run_id=job.get("run_id"),
                        evidence_id=evidence_id,
                        event_type="AUTONOMOUS_RESPONSE_ROUTING_FAILED",
                        actor=WORKER_ID,
                        timestamp_ms=_now_ms(),
                        details_json={
                            "error": str(route_exc),
                            "alert_id": alert_id,
                            "case_id": case_id,
                        },
                    )

            except Exception:
                pass

    entity_job_id = queue.enqueue(
        stage="ENTITY_EXTRACT",
        tenant_id=job.get("tenant_id"),
        mailbox=job.get("mailbox"),
        evidence_id=evidence_id,
        alert_id=alert_id,
        parent_job_id=job.get("job_id"),
        payload={
            "evidence_id": evidence_id,
            "alert_id": alert_id,
            "detection_categories": categories,
            "severity": severity,
        },
    )

    print("\nENQUEUED ENTITY_EXTRACT JOB:")
    print(entity_job_id)

    queue.complete(
        job["job_id"],
        message="DETECT COMPLETED",
    )

    print("\nDETECT COMPLETED")


def main():
    print("\n========================")
    print("DETECT WORKER STARTED")
    print("========================")

    storage = build_storage()
    queue = SQLitePipelineQueue(storage.ledger)

    while True:
        try:
            recovered = queue.recover_stale_jobs()

            if recovered:
                print(f"\nRECOVERED STALE JOBS: {recovered}")

            job = queue.claim_next(
                stage="DETECT",
                worker_id=WORKER_ID,
                lease_seconds=300,
            )

            if not job:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            process_detect_job(
                storage=storage,
                queue=queue,
                job=job,
            )

        except Exception as e:
            print("\nDETECT WORKER ERROR")
            print(str(e))
            traceback.print_exc()
            time.sleep(5)


if __name__ == "__main__":
    main()