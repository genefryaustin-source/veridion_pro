from core.extractors.base import (
    BaseExtractor,
    ExtractedContent,
)

from core.extractors.ocr.tesseract_engine import (
    run_ocr,
)


class ImageExtractor(BaseExtractor):

    supported_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
    }

    supported_content_types = {
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/bmp",
        "image/tiff",
    }

    def extract(
        self,
        data: bytes,
        filename: str,
        content_type: str,
        metadata=None,
    ) -> ExtractedContent:

        text = run_ocr(data)

        confidence = (
            "HIGH"
            if len(text.strip()) > 50
            else "LOW"
        )

        return ExtractedContent(
            text=text,
            filename=filename,
            content_type=content_type,
            extension=(
                "." + filename.split(".")[-1].lower()
                if "." in filename
                else ""
            ),
            extraction_method="tesseract_ocr",
            confidence=confidence,
            metadata=metadata or {},
            warnings=[],
        )