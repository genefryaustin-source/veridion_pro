from abc import ABC, abstractmethod
from typing import Any, Dict

from core.extractors.models import ExtractedContent


class BaseExtractor(ABC):
    supported_extensions = []
    supported_mime_types = []

    def can_handle(self, filename: str, content_type: str = "") -> bool:
        name = (filename or "").lower()
        ctype = (content_type or "").lower()

        return (
            any(name.endswith(ext) for ext in self.supported_extensions)
            or ctype in self.supported_mime_types
        )

    @abstractmethod
    def extract(
        self,
        data: bytes,
        filename: str,
        content_type: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> ExtractedContent:
        raise NotImplementedError