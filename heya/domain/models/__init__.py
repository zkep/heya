from __future__ import annotations

from .convert_result import ConvertResult
from .pdf_content import PdfContent
from .quality import (
    COMPRESSION_QUALITY_MAX,
    COMPRESSION_QUALITY_MIN,
    is_valid_compression_quality,
)

__all__ = [
    "PdfContent",
    "ConvertResult",
    "COMPRESSION_QUALITY_MIN",
    "COMPRESSION_QUALITY_MAX",
    "is_valid_compression_quality",
]
