# core/ingest/gmail_ingest.py

from __future__ import annotations

from typing import List, Dict, Any, Optional
import base64

from server.ingest.gmail_auth import get_gmail_service
from core.classify.rules import CUI_KEYWORDS


from server.ingest.email_parser import parse_raw_email
# ---------------------------------------------------------
# QUERY BUILDER (CONTRACT-STABLE)
# ---------------------------------------------------------

def build_gmail_query(
    lookback_hours: int,
    attachments_only: bool = True,
    monitored_mailbox: Optional[str] = None,
    include_keywords: bool = True,   # 🔥 NEW (safe default)
    **kwargs,
) -> str:
    """
    Build a Gmail search query.

    Enhancements:
    - Uses CUI_KEYWORDS to dynamically inject detection terms
    - Supports attachments + keywords hybrid filtering
    - Backward compatible (no breaking changes)
    """

     # adjust path if needed

    # ---------------------------------------
    # 🔥 SAFE LOOKBACK HANDLING
    # ---------------------------------------
    if isinstance(lookback_hours, dict):
        lookback_hours = lookback_hours.get("value") or lookback_hours.get("hours") or 24

    try:
        lookback_hours = int(lookback_hours)
    except Exception:
        print("⚠️ Invalid lookback_hours, defaulting to 24:", lookback_hours)
        lookback_hours = 24

    # ---------------------------------------
    # 🔥 RELAXED TIME FILTER (SAFE DEFAULT)
    # ---------------------------------------
    if lookback_hours and lookback_hours > 0:
        q_parts = [f"newer_than:{lookback_hours}h"]
    else:
        q_parts = ["in:inbox"]  # fallback

    # ---------------------------------------
    # 🔥 BUILD KEYWORD BLOCK FROM RULES
    # ---------------------------------------

    keyword_terms = []
    MAX_TERMS = 20
    keyword_terms = keyword_terms[:MAX_TERMS]
    if include_keywords:
        for category, words in CUI_KEYWORDS.items():
            for w in words:
                w = w.lower().strip()

                if " " in w:
                    keyword_terms.append(f'"{w}"')
                else:
                    keyword_terms.append(w)

    keyword_query = " OR ".join(keyword_terms) if keyword_terms else ""

    # ---------------------------------------
    # 🔥 COMBINE ATTACHMENTS + KEYWORDS
    # ---------------------------------------
    if attachments_only and keyword_query:
        q_parts.append(f"(has:attachment OR {keyword_query})")

    elif attachments_only:
        q_parts.append("has:attachment")

    elif keyword_query:
        q_parts.append(f"({keyword_query})")

    # ---------------------------------------
    # FUTURE: mailbox targeting (safe placeholder)
    # ---------------------------------------
    # if monitored_mailbox:
    #     q_parts.append(f"to:{monitored_mailbox}")

    query = " ".join(q_parts)

    print("🔥 BUILT GMAIL QUERY:", query)

    return query


# ---------------------------------------------------------
# ATTACHMENT FETCHER (CONTRACT-STABLE)
# ---------------------------------------------------------

def fetch_attachments(
    service,
    query: str,
    max_messages: int = 100,
    monitored_mailbox: Optional[str] = None,
    **kwargs,
) -> List[Dict[str, Any]]:





    resp = (
        service.users()
        .messages()
        .list(
            userId="me",
            q=query,
            maxResults=int(max_messages),
        )
        .execute()
    )

    messages = resp.get("messages", []) or []

    results: List[Dict[str, Any]] = []

    print("📬 TOTAL GMAIL MESSAGES:", len(messages))

    for m in messages:

        msg_id = m.get("id")

        if not msg_id:
            continue

        try:

            # ---------------------------------------------------
            # 🔥 FETCH RAW RFC822 MIME
            # ---------------------------------------------------
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format="raw",
                )
                .execute()
            )

            raw_data = msg.get("raw")

            if not raw_data:

                print(
                    "⚠️ MESSAGE MISSING RAW MIME:",
                    msg_id
                )

                continue

            # ---------------------------------------------------
            # 🔥 RAW MIME BYTES
            # ---------------------------------------------------
            raw_bytes = base64.urlsafe_b64decode(
                raw_data.encode("utf-8")
            )

            # ---------------------------------------------------
            # 🔥 UNIVERSAL MIME PARSER
            # ---------------------------------------------------
            parsed = parse_raw_email(
                raw_bytes,
                provider="gmail"
            )

            # ---------------------------------------------------
            # 🔥 MIME DEBUG LOGGING
            # ---------------------------------------------------
            try:

                print(
                    "📧 CLEAN TEXT LENGTH:",
                    len(parsed.clean_text or "")
                )

                print(
                    "📧 BODY_TEXT LENGTH:",
                    len(parsed.body_text or "")
                )

                print(
                    "📧 BODY_HTML LENGTH:",
                    len(parsed.body_html or "")
                )

                print(
                    "📎 ATTACHMENTS:",
                    len(parsed.attachments or [])
                )

                print("📎 MIME STRUCTURE:")

                for part in parsed.mime_structure:

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

            except Exception as e:

                print(
                    "⚠️ MIME DEBUG LOGGING ERROR:",
                    e
                )

            # ---------------------------------------------------
            # 🔥 NORMALIZE ATTACHMENTS
            # ---------------------------------------------------
            attachments: List[Dict[str, Any]] = []

            for att in parsed.attachments:

                try:

                    attachments.append(
                        {
                            "filename": att.filename,
                            "bytes": att.payload,
                            "content_type": (
                                att.content_type
                                or "application/octet-stream"
                            ),
                            "sha256": att.sha256,
                            "size_bytes": att.size_bytes,
                        }
                    )

                except Exception as e:

                    print(
                        "⚠️ ATTACHMENT NORMALIZATION FAILED:",
                        e
                    )

            # ---------------------------------------------------
            # 🔥 NORMALIZED MESSAGE OBJECT
            # ---------------------------------------------------
            results.append(
                {
                    "message_id": msg_id,

                    "provider": "gmail",

                    "subject": parsed.subject,

                    "sender": parsed.sender,

                    "to": parsed.to,

                    "cc": parsed.cc,

                    "date": parsed.date,

                    "clean_text": parsed.clean_text,

                    "body_text": parsed.body_text,

                    "body_html": parsed.body_html,

                    "mime_structure": parsed.mime_structure,

                    "attachments": attachments,
                }
            )

        except Exception as e:

            print(
                f"❌ FAILED PROCESSING MESSAGE {msg_id}:",
                e
            )

    return results
# ---------------------------------------------------------
# PIPELINE ENTRYPOINT (REQUIRED)
# ---------------------------------------------------------

def fetch_emails(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Pipeline-compatible wrapper.
    Converts config → query → attachments → normalized email objects.
    """

    query = build_gmail_query(
        lookback_hours=int(config.get("lookback_hours", 24)),
        attachments_only=bool(config.get("attachments_only", True)),
        monitored_mailbox=config.get("mailbox"),
    )

    raw = fetch_attachments(
        query=query,
        max_messages=int(config.get("max_messages", 100)),
        monitored_mailbox=config.get("mailbox"),
    )

    # Normalize to pipeline format
    emails = []

    for r in raw:
        emails.append({
            "id": r.get("message_id"),
            "body": f"{len(r.get('attachments', []))} attachments",
            "attachments": r.get("attachments", []),
        })

    return emails







