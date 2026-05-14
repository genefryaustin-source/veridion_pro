import io
import zipfile

from core.extractors.base import (
    BaseExtractor,
    ExtractedContent,
)




class ZipExtractor(BaseExtractor):

    supported_extensions = {
        ".zip",
    }

    supported_content_types = {
        "application/zip",
        "application/x-zip-compressed",
    }

    def extract(
        self,
        data: bytes,
        filename: str,
        content_type: str,
        metadata=None,
    ) -> ExtractedContent:

        metadata = metadata or {}

        combined_text = []

        warnings = []

        extracted_children = []
        from core.extractors.dispatcher import (
            extract_content,
        )
        try:

            with zipfile.ZipFile(
                io.BytesIO(data)
            ) as z:

                names = z.namelist()

                print(
                    "📦 ZIP CONTENTS:",
                    names
                )

                for child_name in names:

                    try:

                        # ---------------------------------------
                        # 🔥 SKIP DIRECTORIES
                        # ---------------------------------------

                        if child_name.endswith("/"):
                            continue

                        child_bytes = z.read(
                            child_name
                        )

                        print(
                            "📦 ZIP CHILD:",
                            child_name,
                            len(child_bytes),
                        )

                        # ---------------------------------------
                        # 🔥 RECURSIVE DISPATCH
                        # ---------------------------------------

                        child_result = extract_content(
                            data=child_bytes,
                            filename=child_name,
                            content_type="",
                            metadata={
                                **metadata,
                                "parent_archive": filename,
                            }
                        )

                        extracted_children.append(
                            {
                                "filename": child_name,
                                "method": child_result.extraction_method,
                                "confidence": child_result.confidence,
                            }
                        )

                        if child_result.text.strip():

                            combined_text.append(
                                f"\n\n===== FILE: {child_name} =====\n\n"
                            )

                            combined_text.append(
                                child_result.text
                            )

                    except Exception as e:

                        print(
                            "❌ ZIP CHILD FAILED:",
                            child_name,
                            e,
                        )

                        warnings.append(
                            f"{child_name}: {e}"
                        )

        except Exception as e:

            print(
                "❌ ZIP EXTRACTION FAILED:",
                e
            )

            warnings.append(str(e))

        final_text = "\n".join(
            combined_text
        )

        confidence = (
            "HIGH"
            if final_text.strip()
            else "LOW"
        )

        return ExtractedContent(
            text=final_text,
            filename=filename,
            content_type=content_type,
            extension=".zip",
            extraction_method="zip_recursive",
            confidence=confidence,
            metadata={
                **metadata,
                "children": extracted_children,
            },
            warnings=warnings,
        )