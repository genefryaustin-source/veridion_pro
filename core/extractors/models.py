from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExtractedContent:
    text: str = ""
    filename: str = ""
    content_type: str = ""
    extension: str = ""
    extraction_method: str = ""
    confidence: str = "LOW"
    metadata: Dict[str, Any] = field(default_factory=dict)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    ocr_text: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    child_artifacts: List[Dict[str, Any]] = field(default_factory=list)