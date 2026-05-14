

# ---------------------------------------
# NORMAL IMPORTS
# ---------------------------------------
import json
import time

from typing import Dict, Any, List

# ✅ detection (NEW LOCATION)
from core.detection.analyzer import analyze_text



from core.evidence.analysis_service import persist_analysis

# ✅ gmail client (unchanged)
from server.ingest.gmail_client import (
    build_service_from_db,
    list_messages,
)




from server.ingest.gmail_ingest import build_gmail_query, fetch_attachments
import base64



from core.extractors.dispatcher import extract_content

from core.entities.entity_extractor import (
    extract_entities,
)

from core.entities.persist_entities import (
    persist_entities,
)

from core.correlation.entity_correlation import (
    correlate_entities,
)

from core.correlation.persist_correlations import (
    persist_correlations,
)
# ---------------------------
# Helpers
# ---------------------------
def extract_email_body(payload):
    def walk(parts):
        for part in parts:
            mime = part.get("mimeType", "")
            if mime == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            if "parts" in part:
                result = walk(part["parts"])
                if result:
                    return result
        return None

    root_data = payload.get("body", {}).get("data")
    if root_data:
        return base64.urlsafe_b64decode(root_data).decode("utf-8", errors="ignore")

    return walk(payload.get("parts", []))


def _headers_map(payload: Dict[str, Any]) -> Dict[str, str]:
    return {
        h.get("name", ""): h.get("value", "")
        for h in payload.get("headers", [])
        if isinstance(h, dict)
    }


def extract_parts(payload):
    parts = []
    if not payload:
        return parts

    if "parts" in payload:
        for p in payload["parts"]:
            parts.extend(extract_parts(p))
    else:
        parts.append(payload)

    return parts


# ---------------------------------------
# 🔥 INGEST SINGLE MESSAGE (FIXED)
# ---------------------------------------
def ingest_message(storage, service, mailbox, message, run_id):
    evidence_created = 0
    messages_failed = 0

    msg = message

    # ---------------------------------------------------
    # 🔥 CANONICAL NORMALIZED EMAIL
    # ---------------------------------------------------

    subject = msg.get("subject", "") or ""

    sender = msg.get("sender", "") or ""

    body_text = msg.get("clean_text", "") or ""

    attachments = msg.get("attachments", []) or []

    mime_structure = msg.get("mime_structure", []) or []

    print(
        "📧 CLEAN TEXT LENGTH:",
        len(body_text)
    )

    print(
        "📎 ATTACHMENTS:",
        len(attachments)
    )

    print(
        "📎 MIME STRUCTURE COUNT:",
        len(mime_structure)
    )

    for part in mime_structure:
        print(
            "   ",
            {
                "path": part.get("path"),
                "content_type": part.get("content_type"),
                "disposition": part.get("disposition"),
                "filename": part.get("filename"),
                "is_multipart": part.get("is_multipart"),
            }
        )






    # ---------------------------------------
    # EMAIL → EVIDENCE
    # ---------------------------------------
    email_bytes = body_text.encode("utf-8")

    email_record = storage.vault.put_bytes(
        data=email_bytes,
        suggested_name=(
            f"email_{msg.get('message_id')}.txt"
        )
    )

    email_evidence_id = email_record.evidence_id

    with storage.ledger._connect() as con:

        before = con.total_changes

        # ---------------------------------------
        # 📦 ENSURE EVIDENCE RECORD EXISTS
        # ---------------------------------------
        con.execute("""
            INSERT OR REPLACE INTO evidence_records (
                evidence_id,
                run_id,
                sha256,
                size_bytes,
                content_type,
                storage_uri,
                suggested_name,
                created_at_ms,
                metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_evidence_id,
            run_id,
            email_record.sha256,
            email_record.size_bytes,
            email_record.content_type,
            email_record.storage_uri,
            email_record.suggested_name,
            int(time.time() * 1000),
            json.dumps({
                "source": "email"
            })
        ))

        after = con.total_changes

        if after > before:
            evidence_created += 1

        # ---------------------------------------
        # 🔥 ALWAYS RECORD CUSTODY (IMMUTABLE DESIGN)
        # ---------------------------------------
        con.execute("""
            INSERT INTO custody_events (
                run_id,
                evidence_id,
                event_type,
                actor,
                timestamp_ms,
                details_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            email_evidence_id,
            "INGESTED",
            "mail_ingest",
            int(time.time() * 1000),
            json.dumps({
                "source": "email",
                "mailbox": mailbox,
                "message_id": msg.get("message_id"),
                "subject": subject,
            })
        ))

        # ---------------------------------------
        # 🧠 DETECTION (EMAIL — CLEAN SINGLE PATH)
        # ---------------------------------------
        try:

            result = analyze_text(
                body_text
            )

            # ---------------------------------------
            # 🔥 ENTITY EXTRACTION
            # ---------------------------------------

            entities = extract_entities(
                body_text
            )

            print(
                "🧬 EMAIL ENTITY EXTRACTION:",
                entities
            )

            # ---------------------------------------
            # 🔥 ENRICH ANALYSIS
            # ---------------------------------------

            result["entities"] = entities

            persist_entities(
                con,
                run_id,
                email_evidence_id,
                entities,
            )
            # ---------------------------------------
            # 🔗 ENTITY CORRELATION
            # ---------------------------------------

            entity_correlations = correlate_entities(
                con,
                email_evidence_id,
                entities,
            )
            persist_correlations(
                con,
                run_id,
                email_evidence_id,
                entity_correlations,
            )
            for c in entity_correlations:
                print(
                    "🔗 ENTITY MATCH:",
                    c["type"],
                    c["entity_value"],
                )
            print(
                "🔗 ENTITY CORRELATIONS:",
                entity_correlations
            )
            print(
                "🔥 ANALYSIS RESULT:",
                result
            )

            # ---------------------------------------
            # 🔥 PERSIST ANALYSIS
            # ---------------------------------------

            persist_analysis(
                con,
                run_id,
                email_evidence_id,
                result
            )

            print(
                "🧠 EMAIL ANALYSIS INSERTED:",
                email_evidence_id
            )

            # ---------------------------------------
            # 🚀 CENTRALIZED ORCHESTRATION (EMAIL)
            # ---------------------------------------
            try:

                # Commit persisted analysis FIRST
                # before orchestrator opens
                # its own DB transactions
                con.commit()

                if (
                        result
                        and result.get("has_detection")
                        and result.get("hit_count", 0) > 0
                ):
                    import core.cases.case_orchestrator as orch

                    # ---------------------------------------
                    # 🔗 ENRICH DETECTION CONTEXT
                    # ---------------------------------------
                    result["sender"] = (
                        locals().get("sender")
                    )

                    result["subject"] = (
                        locals().get("subject")
                    )

                    result["mailbox"] = (
                        locals().get("mailbox")
                    )

                    # Optional if available
                    result["thread_id"] = (
                        locals().get("thread_id")
                    )

                    result["received_at"] = (
                        locals().get("received_at")
                    )

                    # ---------------------------------------
                    # 🚀 ORCHESTRATOR
                    # ---------------------------------------
                    orchestrator = (
                        orch.CaseOrchestrator(
                            storage
                        )
                    )

                    orchestrator.process_detection(
                        evidence_id=email_evidence_id,
                        result=result,
                        run_id=run_id,
                        source="email",
                    )

            except Exception as e:

                print(
                    "⚠️ Email orchestration failed:",
                    e
                )

        except Exception as e:

            print(
                "⚠️ Email analysis failed:",
                e
            )

        # ---------------------------------------
        # 📎 ATTACHMENTS (CANONICAL MIME PARSER)
        # ---------------------------------------
        attachment_count = 0

        for att in attachments:
            filename = att.get("filename")

            data = att.get("bytes")

            content_type = att.get("content_type")

            attachment_sha = att.get("sha256")

            if not filename:
                continue

            # ---------------------------------------------------
            # 🔥 CANONICAL ATTACHMENT PAYLOAD
            # ---------------------------------------------------
            if not data:
                print(
                    "⚠️ Attachment payload empty:",
                    filename
                )

                continue

            attachment_count += 1

            print(
                "📎 PROCESSING ATTACHMENT:",
                filename,
                content_type,
                len(data)
            )
            # ---------------------------------------
            # 🔥 UNIVERSAL EXTRACTION DISPATCHER
            # ---------------------------------------

            extracted = extract_content(
                data=data,
                filename=filename,
                content_type=content_type,
                metadata={
                    "source": "email_attachment",
                    "mailbox": mailbox,
                    "message_id": msg.get("message_id"),
                    "run_id": run_id,
                    "parent_email_evidence_id": email_evidence_id,
                }
            )
            attachment_text = extracted.text or ""
            extracted.extraction_method
            extracted.confidence
            extracted.warnings
            # ---------------------------------------
            # 📦 STORE ATTACHMENT IN VAULT
            # ---------------------------------------
            attachment_record = storage.vault.put_bytes(
                data=data,
                suggested_name=filename
            )

            attachment_evidence_id = (
                attachment_record.evidence_id
            )

            attachment_sha = (
                    att.get("sha256")
                    or attachment_record.sha256
            )

            # ---------------------------------------
            # 🚫 ATTACHMENT DEDUP CHECK
            # ---------------------------------------
            existing = None

            if hasattr(storage.ledger, "lookup_evidence_by_sha256"):
                existing = storage.ledger.lookup_evidence_by_sha256(
                    attachment_sha
                )

            if (
                    existing
                    and existing.get("evidence_id") != attachment_evidence_id
            ):
                print(
                    f"⚠️ ATTACHMENT ALREADY EXISTS: {attachment_sha}"
                )

                with storage.ledger._connect() as con:
                    con.execute("""
                        INSERT INTO custody_events (
                            run_id,
                            evidence_id,
                            event_type,
                            actor,
                            timestamp_ms,
                            details_json
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        run_id,
                        existing["evidence_id"],
                        "DUPLICATE_SKIPPED",
                        "attachment_ingest",
                        int(time.time() * 1000),
                        json.dumps({
                            "reason": "sha256_exists",
                            "filename": filename,
                            "parent_email_evidence_id": email_evidence_id,
                            "sha256": attachment_sha,
                        })
                    ))

                    con.commit()

                continue

            # ---------------------------------------
            # 💾 RECORD ATTACHMENT EVIDENCE + CUSTODY
            # ---------------------------------------
            with storage.ledger._connect() as con:

                before = con.total_changes

                con.execute("""
                    INSERT OR IGNORE INTO evidence_records (
                        evidence_id,
                        run_id,
                        sha256,
                        size_bytes,
                        content_type,
                        storage_uri,
                        suggested_name,
                        created_at_ms,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    attachment_evidence_id,
                    run_id,
                    attachment_record.sha256,
                    attachment_record.size_bytes,
                    content_type,
                    attachment_record.storage_uri,
                    attachment_record.suggested_name,
                    int(time.time() * 1000),
                    json.dumps({
                        "parent_email_evidence_id": email_evidence_id,
                        "filename": filename,
                        "content_type": content_type,
                        "sha256": attachment_sha,
                    })
                ))

                after = con.total_changes

                if after > before:
                    evidence_created += 1

                con.execute("""
                    INSERT INTO custody_events (
                        run_id,
                        evidence_id,
                        event_type,
                        actor,
                        timestamp_ms,
                        details_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    attachment_evidence_id,
                    "INGESTED_ATTACHMENT",
                    "mail_ingest",
                    int(time.time() * 1000),
                    json.dumps({

                        "filename": filename,

                        "parent_email_evidence_id": email_evidence_id,

                        "content_type": content_type,

                        # ---------------------------------------
                        # 🔥 EXTRACTION TELEMETRY
                        # ---------------------------------------

                        "extraction_method": extracted.extraction_method,

                        "extraction_confidence": extracted.confidence,

                        "extraction_warnings": extracted.warnings,

                        "extracted_text_length": len(
                            extracted.text or ""
                        ),

                    })
                ))


                print(
                    "🧾 ATTACHMENT CUSTODY EVENT INSERTED:",
                    attachment_evidence_id
                )

                # ---------------------------------------
                # 🧠 DETECTION (ATTACHMENT)
                # ---------------------------------------
                analysis = None

                try:



                    # ---------------------------------------
                    # 🔥 CANONICAL EXTRACTED TEXT
                    # ---------------------------------------

                    attachment_text = (
                            extracted.text or ""
                    ).strip()

                    print(
                        "📄 EXTRACTION METHOD:",
                        extracted.extraction_method
                    )

                    print(
                        "📄 EXTRACTION CONFIDENCE:",
                        extracted.confidence
                    )

                    print(
                        "📄 EXTRACTED TEXT LENGTH:",
                        len(attachment_text)
                    )

                    if extracted.warnings:
                        print(
                            "⚠️ EXTRACTION WARNINGS:",
                            extracted.warnings
                        )

                    # ---------------------------------------
                    # 🔥 ANALYZE EXTRACTED CONTENT
                    # ---------------------------------------

                    if attachment_text:

                        normalized_text = attachment_text.lower()

                        analysis = analyze_text(
                            normalized_text
                        )

                        print(
                            "🔥 ATTACHMENT ANALYSIS RESULT:",
                            analysis
                        )
                        # ---------------------------------------
                        # 🔥 ENTITY EXTRACTION
                        # ---------------------------------------

                        entities = extract_entities(
                            normalized_text
                        )

                        print(
                            "🧬 ENTITY EXTRACTION:",
                            entities
                        )

                        # ---------------------------------------
                        # 🔥 ENRICH ANALYSIS WITH ENTITIES
                        # ---------------------------------------

                        analysis["entities"] = entities

                        # ---------------------------------------
                        # 🔥 PERSIST STRUCTURED ENTITIES
                        # ---------------------------------------

                        persist_entities(
                            con,
                            run_id,
                            attachment_evidence_id,
                            entities,
                        )
                        # ---------------------------------------
                        # 🔗 ENTITY CORRELATION
                        # ---------------------------------------

                        entity_correlations = correlate_entities(
                            con,
                            attachment_evidence_id,
                            entities,
                        )

                        print(
                            "🔗 ENTITY CORRELATIONS:",
                            entity_correlations
                        )
                        persist_correlations(
                            con,
                            run_id,
                            attachment_evidence_id,
                            entity_correlations,
                        )
                        for c in entity_correlations:
                            print(
                                "🔗 ENTITY MATCH:",
                                c["type"],
                                c["entity_value"],
                            )
                        # ---------------------------------------
                        # 🔥 PERSIST ANALYSIS
                        # ---------------------------------------

                        persist_analysis(
                            con,
                            run_id,
                            attachment_evidence_id,
                            analysis
                        )

                        print(
                            "🧠 ATTACHMENT ANALYSIS INSERTED:",
                            attachment_evidence_id
                        )

                    else:

                        print(
                            "⚠️ NO EXTRACTED TEXT:",
                            filename
                        )

                except Exception as e:

                    print(
                        "⚠️ ATTACHMENT detection failed:",
                        e
                    )

                con.commit()

                # ---------------------------------------
                # 🚀 CENTRALIZED ORCHESTRATION (ATTACHMENT)
                # ---------------------------------------
                if (
                        analysis
                        and analysis.get("has_detection")
                        and analysis.get("hit_count", 0) > 0
                ):
                    from core.cases.case_orchestrator import (
                        CaseOrchestrator
                    )

                    # ---------------------------------------
                    # 🔗 ENRICH ATTACHMENT DETECTION CONTEXT
                    # ---------------------------------------
                    analysis["sender"] = (
                        locals().get("sender")
                    )

                    analysis["subject"] = (
                        locals().get("subject")
                    )

                    analysis["mailbox"] = (
                        locals().get("mailbox")
                    )

                    analysis["thread_id"] = (
                        locals().get("thread_id")
                    )

                    analysis["received_at"] = (
                        locals().get("received_at")
                    )

                    analysis["attachment_sha"] = (
                        attachment_sha
                    )

                    analysis["attachment_name"] = (
                        filename
                    )

                    analysis["parent_email"] = (
                        locals().get("subject")
                    )

                    orchestrator = (
                        CaseOrchestrator(storage)
                    )

                    orchestrator.process_detection(
                        evidence_id=attachment_evidence_id,
                        result=analysis,
                        run_id=run_id,
                        source="attachment",
                    )

        # ---------------------------------------
        # 📎 FINAL ATTACHMENT SUMMARY
        # ---------------------------------------
        print(
            "📎 TOTAL ATTACHMENTS PROCESSED:",
            attachment_count
        )

        return {
            "messages_processed": 1,
            "messages_failed": messages_failed,
            "evidence_created": evidence_created
        }






def run_ingest(
    storage,
    provider,
    mailbox,
    lookback_hours,
    attachments_only,
    max_messages,
    payload,
    job_id,
    run_id=None,
):
    ledger = storage.ledger

    if not run_id:
        run_id = f"manual-{int(time.time() * 1000)}"

    print("🧾 RUN ID USED:", run_id)

    # ---------------------------------------
    # 🔥 BUILD SERVICE
    # ---------------------------------------
    service = build_service_from_db(storage, mailbox)

    print("🔥 SERVICE TYPE:", type(service))

    if service is None or service == ...:
        raise ValueError("🔥 Gmail service is invalid — check build_service_from_db")

    # ---------------------------------------
    # 🔥 BUILD QUERY (FIXED)
    # ---------------------------------------
    query = build_gmail_query(
        lookback_hours=lookback_hours,
        attachments_only=attachments_only,
        include_keywords=True
    )

    print("🔥 USING GMAIL QUERY:", query)

    # ---------------------------------------
    # 🔥 FETCH MESSAGES (FIXED)
    # ---------------------------------------
    fetch_limit = max(25, max_messages or 10)

    print("🔥 PASSING QUERY INTO list_messages:", query)
    print("🔥 CALLING list_messages FROM:", list_messages.__module__)

    # ---------------------------------------
    # 🔥 FETCH NORMALIZED MESSAGES
    # ---------------------------------------
    messages = fetch_attachments(
        service=service,
        query=query,
        max_messages=fetch_limit,
        monitored_mailbox=mailbox,
    )

    if not messages:
        print("⚠️ No results from filtered query — falling back to inbox")

        messages = fetch_attachments(
            service=service,
            query=query,
            max_messages=fetch_limit,
            monitored_mailbox=mailbox,
        )

    print(f"📬 NORMALIZED MESSAGES FETCHED: {len(messages)}")

    # ---------------------------------------
    # 🔥 PRIORITIZE NORMALIZED ATTACHMENTS
    # ---------------------------------------
    messages.sort(
        key=lambda x: len(x.get("attachments", [])),
        reverse=True,
    )

    if not max_messages:
        max_messages = 10

    messages = messages[:max_messages]

    print(f"📬 FINAL NORMALIZED MESSAGES USED: {len(messages)}")

    # ---------------------------------------
    # 🔥 PROCESS NORMALIZED MESSAGES
    # ---------------------------------------

    processed = 0
    failed = 0
    evidence_created = 0

    for m in messages:

        try:

            result = ingest_message(
                storage,
                service,
                mailbox,
                m,
                run_id
            )

            if isinstance(result, dict):
                processed += result.get(
                    "messages_processed",
                    0
                )

                failed += result.get(
                    "messages_failed",
                    0
                )

                evidence_created += result.get(
                    "evidence_created",
                    0
                )

        except Exception as e:

            print(
                f"❌ Failed processing normalized message: {e}"
            )

            failed += 1

    # ---------------------------------------
    # 🔥 FINAL JOB SUMMARY
    # ---------------------------------------

    print(
        f"📊 Job summary → processed={processed}, "
        f"failed={failed}, "
        f"evidence={evidence_created}"
    )

    return {
        "status": "COMPLETED",
        "messages_processed": processed,
        "messages_failed": failed,
        "evidence_created": evidence_created,
    }
