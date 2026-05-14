from typing import Any, Dict

from core.extractors.base import BaseExtractor
from core.extractors.models import ExtractedContent


class TextExtractor(BaseExtractor):
    supported_extensions = [".txt", ".log", ".md", ".py", ".js", ".ts", ".html", ".css"]
    supported_mime_types = ["text/plain", "text/html", "text/markdown"]

    def extract(
        self,
        data: bytes,
        filename: str,
        content_type: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> ExtractedContent:

        text = ""

        for enc in ("utf-8", "utf-16", "latin-1", "cp1252"):
            try:
                text = data.decode(enc, errors="replace")
                break
            except Exception:
                continue

        return ExtractedContent(
            text=text.strip(),
            filename=filename,
            content_type=content_type or "text/plain",
            extension="." + filename.split(".")[-1].lower() if "." in filename else "",
            extraction_method="text_decode",
            confidence="HIGH" if text.strip() else "LOW",
            metadata=metadata or {},
        )