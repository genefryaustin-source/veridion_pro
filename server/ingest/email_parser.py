# core/ingest/email_parser.py

import base64
import hashlib
import html
import re
from dataclasses import dataclass, asdict
from email import policy
from email.parser import BytesParser
from email.message import Message, EmailMessage
from email.header import decode_header
from typing import Any, Dict, List, Optional
from core.email.reply_parser import (strip_quoted_reply,)

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None


MAX_TEXT_CHARS = 500_000


@dataclass
class ParsedAttachment:
    filename: str
    content_type: str
    size_bytes: int
    sha256: str
    disposition: str
    content_id: Optional[str]
    payload: bytes


@dataclass
class ParsedEmail:
    message_id: Optional[str]
    subject: str
    sender: str
    to: List[str]
    cc: List[str]
    date: Optional[str]
    body_text: str
    body_html: str
    clean_text: str
    attachments: List[ParsedAttachment]
    headers: Dict[str, str]
    mime_structure: List[Dict[str, Any]]
    raw_sha256: Optional[str]

import re


def normalize_whitespace(
    text: str,
) -> str:

    if not text:
        return ""

    # collapse excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    # collapse repeated spaces/tabs
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()

def _decode_header_value(value: Any) -> str:
    if not value:
        return ""

    try:
        decoded = decode_header(str(value))
        parts = []

        for text, charset in decoded:
            if isinstance(text, bytes):
                parts.append(text.decode(charset or "utf-8", errors="replace"))
            else:
                parts.append(str(text))

        return "".join(parts).strip()
    except Exception:
        return str(value).strip()


def _split_addresses(value: Any) -> List[str]:
    if not value:
        return []

    value = _decode_header_value(value)
    return [v.strip() for v in value.split(",") if v.strip()]


def _decode_payload(part: Message) -> bytes:
    try:
        payload = part.get_payload(decode=True)
        if payload is not None:
            return payload
    except Exception:
        pass

    try:
        raw = part.get_payload()
        if isinstance(raw, str):
            return raw.encode(part.get_content_charset() or "utf-8", errors="replace")
    except Exception:
        pass

    return b""


def _decode_text_payload(part: Message) -> str:
    payload = _decode_payload(part)

    if not payload:
        return ""

    charset = part.get_content_charset() or "utf-8"

    for enc in [charset, "utf-8", "latin-1", "cp1252"]:
        try:
            return payload.decode(enc, errors="replace")
        except Exception:
            continue

    return payload.decode("utf-8", errors="replace")


def _html_to_text(raw_html: str) -> str:
    if not raw_html:
        return ""

    raw_html = html.unescape(raw_html)

    if BeautifulSoup:
        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup(["script", "style", "noscript", "meta", "head"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
    else:
        text = re.sub(r"<(script|style).*?</\1>", " ", raw_html, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)

    return _clean_text(text)


def _strip_quoted_replies(text: str) -> str:
    if not text:
        return ""

    patterns = [
        r"\nOn .+ wrote:\n",
        r"\nFrom:\s.+\nSent:\s.+\nTo:\s.+\nSubject:\s.+",
        r"\n-{2,}\s*Original Message\s*-{2,}",
        r"\n_{5,}",
    ]

    cut = len(text)

    for pattern in patterns:
        m = re.search(pattern, text, flags=re.I | re.S)
        if m:
            cut = min(cut, m.start())

    return text[:cut].strip()


def _clean_text(text: str) -> str:
    if not text:
        return ""

    text = html.unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = _strip_quoted_replies(text)
    return text.strip()[:MAX_TEXT_CHARS]


def _part_filename(part: Message) -> str:
    filename = part.get_filename()
    return _decode_header_value(filename) if filename else ""


def _is_attachment(part: Message) -> bool:
    disposition = (part.get_content_disposition() or "").lower()
    filename = _part_filename(part)

    if disposition == "attachment":
        return True

    if filename:
        return True

    return False


def _walk_parts(msg: Message, path: str = "0") -> List[Dict[str, Any]]:
    structure = []

    content_type = msg.get_content_type()
    disposition = msg.get_content_disposition()
    filename = _part_filename(msg)

    structure.append({
        "path": path,
        "content_type": content_type,
        "disposition": disposition,
        "filename": filename,
        "is_multipart": msg.is_multipart(),
    })

    if msg.is_multipart():
        for idx, child in enumerate(msg.get_payload() or []):
            structure.extend(_walk_parts(child, f"{path}.{idx}"))

    return structure


def parse_raw_email(raw_email_bytes: bytes, provider: str = "unknown") -> ParsedEmail:
    raw_sha256 = hashlib.sha256(raw_email_bytes).hexdigest() if raw_email_bytes else None

    msg = BytesParser(policy=policy.default).parsebytes(raw_email_bytes)

    return parse_email_message(msg, raw_sha256=raw_sha256, provider=provider)


def parse_email_message(
    msg: Message,
    raw_sha256: Optional[str] = None,
    provider: str = "unknown",
) -> ParsedEmail:

    headers = {}
    for k, v in msg.items():
        headers[str(k)] = _decode_header_value(v)

    subject = _decode_header_value(msg.get("Subject"))
    sender = _decode_header_value(msg.get("From"))
    to = _split_addresses(msg.get("To"))
    cc = _split_addresses(msg.get("Cc"))
    date = _decode_header_value(msg.get("Date"))
    message_id = _decode_header_value(msg.get("Message-ID"))

    plain_parts: List[str] = []
    html_parts: List[str] = []
    attachments: List[ParsedAttachment] = []

    all_parts = list(msg.walk()) if msg.is_multipart() else [msg]

    for part in all_parts:
        if part.is_multipart():
            continue

        content_type = (part.get_content_type() or "").lower()
        disposition = (part.get_content_disposition() or "").lower()
        filename = _part_filename(part)
        content_id = part.get("Content-ID")

        if _is_attachment(part):
            payload = _decode_payload(part)
            sha = hashlib.sha256(payload).hexdigest() if payload else ""

            attachments.append(
                ParsedAttachment(
                    filename=filename or f"attachment_{len(attachments) + 1}",
                    content_type=content_type,
                    size_bytes=len(payload),
                    sha256=sha,
                    disposition=disposition or "attachment",
                    content_id=_decode_header_value(content_id) if content_id else None,
                    payload=payload,
                )
            )
            continue

        if content_type == "text/plain":
            plain_parts.append(_decode_text_payload(part))

        elif content_type == "text/html":
            html_parts.append(_decode_text_payload(part))

    body_text = _clean_text("\n\n".join([p for p in plain_parts if p.strip()]))
    body_html = "\n\n".join([p for p in html_parts if p.strip()])

    if body_text:
        clean_text = body_text
    elif body_html:
        clean_text = _html_to_text(body_html)
    else:
        clean_text = ""

    # Metadata fallback so analyzer is not blind.
    if not clean_text:
        fallback_parts = [
            f"Subject: {subject}" if subject else "",
            f"From: {sender}" if sender else "",
            f"To: {', '.join(to)}" if to else "",
        ]
        clean_text = _clean_text("\n".join([p for p in fallback_parts if p]))
    clean_text = normalize_whitespace(
        clean_text
    )
    # ---------------------------------------
    # 🔥 QUOTED REPLY STRIPPING
    # ---------------------------------------

    clean_text = strip_quoted_reply(
        clean_text
    )
    return ParsedEmail(
        message_id=message_id,
        subject=subject,
        sender=sender,
        to=to,
        cc=cc,
        date=date,
        body_text=body_text,
        body_html=body_html,
        clean_text=clean_text,
        attachments=attachments,
        headers=headers,
        mime_structure=_walk_parts(msg),
        raw_sha256=raw_sha256,
    )


def parsed_email_to_dict(parsed: ParsedEmail, include_payloads: bool = False) -> Dict[str, Any]:
    data = asdict(parsed)

    if not include_payloads:
        for att in data["attachments"]:
            att.pop("payload", None)
    else:
        for att in data["attachments"]:
            payload = att.get("payload")
            if isinstance(payload, bytes):
                att["payload_b64"] = base64.b64encode(payload).decode("ascii")
                att.pop("payload", None)

    return data