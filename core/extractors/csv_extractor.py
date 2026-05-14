import csv
from io import StringIO
from typing import Any, Dict

from core.extractors.base import BaseExtractor
from core.extractors.models import ExtractedContent


class CsvExtractor(BaseExtractor):
    supported_extensions = [".csv"]
    supported_mime_types = ["text/csv", "application/csv"]

    def extract(
        self,
        data: bytes,
        filename: str,
        content_type: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> ExtractedContent:

        warnings = []
        tables = []
        text = ""

        try:
            decoded = data.decode("utf-8", errors="replace")
            reader = csv.reader(StringIO(decoded))
            rows = list(reader)

            tables.append({"rows": rows})
            text = "\n".join([" | ".join(row) for row in rows])

        except Exception as e:
            warnings.append(str(e))

        return ExtractedContent(
            text=text.strip(),
            filename=filename,
            content_type=content_type or "text/csv",
            extension=".csv",
            extraction_method="csv",
            confidence="HIGH" if text.strip() else "LOW",
            metadata=metadata or {},
            tables=tables,
            warnings=warnings,
        )