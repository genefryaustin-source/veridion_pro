from typing import Any, Dict

from core.extractors.models import ExtractedContent
from core.extractors.text_extractor import TextExtractor
from core.extractors.docx_extractor import DocxExtractor
from core.extractors.pdf_extractor import PdfExtractor
from core.extractors.csv_extractor import CsvExtractor
from core.extractors.image_extractor import (ImageExtractor,)
from core.extractors.zip_extractor import (ZipExtractor,)
from core.extractors.excel_extractor import (ExcelExtractor,)

EXTRACTORS = [
    PdfExtractor(),
    DocxExtractor(),
    CsvExtractor(),
    TextExtractor(),
    ImageExtractor(),
    ZipExtractor(),
    ExcelExtractor(),
]


def extract_content(
    data: bytes,
    filename: str,
    content_type: str = "",
    metadata: Dict[str, Any] | None = None,
) -> ExtractedContent:

    metadata = metadata or {}

    print(
        "📦 DISPATCH REQUEST:",
        {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": len(data) if data else 0,
        }
    )

    # ---------------------------------------
    # 🔥 TRY REGISTERED EXTRACTORS
    # ---------------------------------------

    for extractor in EXTRACTORS:

        if extractor.can_handle(
            filename,
            content_type,
        ):

            print(
                "✅ USING EXTRACTOR:",
                extractor.__class__.__name__
            )

            return extractor.extract(
                data=data,
                filename=filename,
                content_type=content_type,
                metadata=metadata,
            )

    # ---------------------------------------
    # ⚠️ FINAL FALLBACK
    # ---------------------------------------

    print(
        "⚠️ NO EXTRACTOR FOUND:",
        {
            "filename": filename,
            "content_type": content_type,
        }
    )

    return ExtractedContent(
        text="",
        filename=filename,
        content_type=content_type or "application/octet-stream",
        extension=(
            "." + filename.split(".")[-1].lower()
            if "." in filename
            else ""
        ),
        extraction_method="unsupported",
        confidence="NONE",
        metadata=metadata,
        warnings=[
            (
                "No extractor registered "
                f"for filename={filename}, "
                f"content_type={content_type}"
            )
        ],
    )