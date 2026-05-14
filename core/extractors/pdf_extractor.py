from io import BytesIO
from typing import Any, Dict

from pypdf import PdfReader

from core.extractors.base import BaseExtractor
from core.extractors.models import ExtractedContent
import io

from pdf2image import convert_from_bytes

from core.extractors.ocr.tesseract_engine import (
    run_ocr,
)

class PdfExtractor(BaseExtractor):
    supported_extensions = [".pdf"]
    supported_mime_types = ["application/pdf"]

    def extract(
        self,
        data: bytes,
        filename: str,
        content_type: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> ExtractedContent:

        warnings = []
        text_parts = []
        extraction_method = "pypdf"
        confidence = "HIGH"
        try:
            reader = PdfReader(BytesIO(data))

            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text.strip())

        except Exception as e:
            warnings.append(str(e))

        text = "\n\n".join(text_parts).strip()

        # ---------------------------------------
        # 🔥 OCR FALLBACK
        # ---------------------------------------

        ocr_used = False

        if len(text.strip()) < 50:

            print(
                "⚠️ LOW PDF TEXT — OCR FALLBACK:",
                filename
            )

            try:

                images = convert_from_bytes(
                    data,
                    dpi=300,
                    poppler_path=r"C:\poppler\Library\bin",
                )

                ocr_text_parts = []

                for idx, image in enumerate(images):

                    print(
                        f"🔍 OCR PAGE {idx + 1}/{len(images)}"
                    )

                    img_bytes = io.BytesIO()

                    image.save(
                        img_bytes,
                        format="PNG",
                    )

                    page_text = run_ocr(
                        img_bytes.getvalue()
                    )

                    if page_text.strip():
                        ocr_text_parts.append(
                            page_text
                        )

                ocr_text = "\n\n".join(
                    ocr_text_parts
                )

                if len(ocr_text.strip()) > len(text.strip()):
                    print(
                        "✅ OCR IMPROVED PDF EXTRACTION"
                    )

                    text = ocr_text

                    extraction_method = (
                        "pdf_ocr_fallback"
                    )

                    confidence = "MEDIUM"

                    ocr_used = True

                    warnings.append(
                        "OCR_USED"
                    )

                    warnings.append(
                        "SCANNED_PDF"
                    )

            except Exception as e:

                print(
                    "❌ PDF OCR FALLBACK FAILED:",
                    e
                )

        return ExtractedContent(
            text=text,
            filename=filename,
            content_type=content_type or "application/pdf",
            extension=".pdf",
            extraction_method=extraction_method,
            confidence=confidence,
            metadata=metadata or {},
            warnings=warnings,
        )