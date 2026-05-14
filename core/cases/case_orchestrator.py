# Veridion Pro — Centralized Case Orchestration Architecture


import json
import time
import traceback


from core.alerts.notifier import notify
from core.cases.correlation_engine import (CaseCorrelationEngine)

class CaseOrchestrator:

    def __init__(self, storage):
        self.storage = storage
        self.ledger = storage.ledger



    # -------------------------------------------------
    # MAIN DETECTION PIPELINE
    # -------------------------------------------------
    def process_detection(
        self,
        evidence_id,
        result,
        run_id=None,
        source="email",
    ):

        try:

            severity = (
                    result.get("severity") or "LOW"
            ).upper()

            hit_count = int(
                result.get("hit_count", 0)
            )

            category = (
                result.get("primary_category")
                or "UNCATEGORIZED"
            )

            has_detection = bool(
                result.get("has_detection")
            ) or int(result.get("hit_count", 0)) > 0

            severity = (
                    result.get("severity") or "LOW"
            ).upper()

            if severity == "NONE":
                return None

            if not has_detection:
                return None

            now = int(time.time() * 1000)
            print(
                f"🚀 ORCHESTRATOR: "
                f"evidence={evidence_id} "
                f"category={category} "
                f"severity={severity} "
                f"hits={hit_count}"
            )


            # ---------------------------------
            # PHASE 1 — ALERT INSERT / REUSE
            # ---------------------------------
            alert_id = None

            try:
                with self.ledger._connect() as con:

                    row = con.execute("""
                                SELECT id
                                FROM alerts
                                WHERE evidence_id = ?
                                AND severity = ?
                                ORDER BY created_at_ms DESC
                                LIMIT 1
                            """, (
                        evidence_id,
                        severity,
                    )).fetchone()

                    if row:
                        alert_id = row["id"]

                    else:
                        cur = con.execute("""
                                    INSERT OR IGNORE INTO alerts (
                                        evidence_id,
                                        severity,
                                        message,
                                        created_at_ms,
                                        source_name
                                    )
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                            evidence_id,
                            severity,
                            f"{category} detected ({hit_count} hits)",
                            now,
                            source,
                        ))

                        alert_id = cur.lastrowid

                        if not alert_id:
                            row = con.execute("""
                                        SELECT id
                                        FROM alerts
                                        WHERE evidence_id = ?
                                        AND severity = ?
                                        ORDER BY created_at_ms DESC
                                        LIMIT 1
                                    """, (
                                evidence_id,
                                severity,
                            )).fetchone()

                            alert_id = row["id"] if row else None

                    con.commit()

            except Exception:
                traceback.print_exc()
                return None

            if not alert_id:
                print(
                    "⚠️ ORCHESTRATOR: no alert_id created/reused"
                )
                return None
            # ---------------------------------
            # PRE-ENRICH CASE METADATA
            # REQUIRED FOR CORRELATION
            # ---------------------------------
            self.ledger.ensure_case_for_alert(

                alert_id=alert_id,

                evidence_id=evidence_id,

                job_id=run_id,

                category=category,

                source=source,

                sender=result.get("sender"),

                subject=result.get("subject"),

                attachment_sha=result.get(
                    "attachment_sha"
                ),
            )
            # ---------------------------------
            # 🔗 CASE CORRELATION ENGINE
            # ---------------------------------


            correlator = CaseCorrelationEngine(
                self.storage
            )

            existing_case = correlator.find_matching_case(
                category=category,
                sender=result.get("sender"),
                attachment_sha=result.get("attachment_sha"),
                subject=result.get("subject"),
                source=source,
            )

            # ---------------------------------
            # 📁 CASE CREATION / REUSE
            # ---------------------------------
            case_id = None

            try:
                correlation_reason = None
                if existing_case:

                    case_id = existing_case.get(
                        "case_id"
                    )

                    correlation_reason = (
                        existing_case.get("reason")
                    )

                    print(
                        "🔗 CORRELATED TO EXISTING CASE:",
                        case_id,
                        "|",
                        correlation_reason
                    )

                else:
                    print(
                        "🧩 ORCHESTRATOR CASE INPUT:",
                        {
                            "category": category,
                            "source": source,
                            "sender": result.get("sender"),
                            "subject": result.get("subject"),
                            "attachment_sha": result.get(
                                "attachment_sha"
                            ),
                        }
                    )
                    case_id = (
                        self.ledger.ensure_case_for_alert(
                            alert_id=alert_id,
                            evidence_id=evidence_id,
                            job_id=run_id,
                            category=category,
                            source=source,
                            sender=result.get("sender"),
                            subject=result.get("subject"),
                            attachment_sha=result.get("attachment_sha"),
                        )
                    )

            except Exception:
                traceback.print_exc()

            if not case_id:
                print(
                    "⚠️ ORCHESTRATOR: no case_id created/reused"
                )

                return None

            # ---------------------------------
            # IDEMPOTENCY CHECK
            # ---------------------------------
            try:

                with self.ledger._connect() as con:

                    existing = con.execute("""
                        SELECT 1
                        FROM case_timeline
                        WHERE case_id = ?
                        AND event_type = ?
                        AND json_extract(
                            details,
                            '$.evidence_id'
                        ) = ?
                        LIMIT 1
                    """, (
                        case_id,
                        "ALERT_CREATED",
                        evidence_id,
                    )).fetchone()

                    if existing:
                        print(
                            "♻️ REUSING EXISTING EVIDENCE:",
                            evidence_id
                        )

                        # ---------------------------------
                        # ENSURE CASE + METADATA ENRICHMENT
                        # EVEN FOR REUSED EVIDENCE
                        # ---------------------------------
                        self.ledger.ensure_case_for_alert(

                            alert_id=alert_id,

                            evidence_id=evidence_id,

                            job_id=run_id,

                            category=category,

                            source=source,

                            sender=result.get("sender"),

                            subject=result.get("subject"),

                            attachment_sha=result.get(
                                "attachment_sha"
                            ),
                        )

                        # DO NOT EXIT
                        # continue correlation/timeline flow



            except Exception:
                traceback.print_exc()

            # ---------------------------------
            # PHASE 3 — ASSIGNMENT
            # ---------------------------------
            assigned_to = None

            try:
                from core.cases.assignment_engine import (
                    auto_assign_case
                )

                assigned_to = auto_assign_case(
                    self.storage,
                    case_id=case_id,
                    severity=severity,
                )

            except Exception:
                traceback.print_exc()
            print(
                "🔗 FINAL CORRELATION REASON:",
                correlation_reason
            )
            # ---------------------------------
            # PHASE 4 — TIMELINE EVENT
            # IMPORTANT: separate short transaction
            # ---------------------------------
            try:
                print(
                    "🧪 TIMELINE CORRELATION DEBUG:",
                    {
                        "case_id": case_id,
                        "correlation_reason": correlation_reason,
                        "existing_case": existing_case,
                    }
                )
                with self.ledger._connect() as con:
                    con.execute("""
                                INSERT INTO case_timeline (
                                    case_id,
                                    event_type,
                                    created_at_ms,
                                    label,
                                    actor,
                                    details
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                        case_id,
                        "ALERT_CREATED",
                        now,
                        f"{severity} {category} detected",
                        "system",
                        json.dumps(
                            {

                                "alert_id": alert_id,

                                "evidence_id": evidence_id,

                                "severity": severity,

                                "category": category,

                                "source": source,

                                "hit_count": hit_count,

                                "correlation_reason": correlation_reason,

                            },
                            default=str
                        )
                    ))

                    con.commit()

            except Exception:
                traceback.print_exc()

            # -------------------------------------
            # PHASE 5 — NOTIFY OUTSIDE DB
            # -------------------------------------
            try:
                notify(
                    self.storage,
                    severity,
                    f"{category} detected (hits: {hit_count})",
                )

            except Exception:
                traceback.print_exc()

            return {
                "alert_id": alert_id,
                "case_id": case_id,
                "assigned_to": assigned_to,
            }

        except Exception:
            traceback.print_exc()
        return None

    # -------------------------------------------------
    # SLA BREACH PIPELINE
    # -------------------------------------------------
    def process_sla_breach(self, case_id, severity="HIGH"):

        try:

            notify(
                self.storage,
                severity,
                f"SLA breach detected for case {case_id}",
                case_id=case_id,
            )

        except Exception:
            traceback.print_exc()
