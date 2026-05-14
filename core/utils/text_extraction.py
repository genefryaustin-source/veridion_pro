import io
import logging
from typing import Optional

from core.extractors import extract_content
def extract_text_from_bytes(
    data: bytes,
    filename: str | None = None,
) -> str:

    extracted = extract_content(
        data=data,
        filename=filename or "unknown.bin",
    )

    return extracted.text or ""