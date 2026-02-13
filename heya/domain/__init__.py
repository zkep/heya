from __future__ import annotations

from .exceptions import (
    CompressError,
    ConfigError,
    ConvertError,
    ErrorCode,
    HeyaError,
    MarkdownError,
    NetworkError,
    PdfToWordError,
    TimeoutError,
    ValidationError,
    WechatError,
)
from .models import (
    COMPRESSION_QUALITY_MAX,
    COMPRESSION_QUALITY_MIN,
    ConvertResult,
    PdfContent,
    is_valid_compression_quality,
)
from .services import compress_pdf

__all__ = [
    "PdfContent",
    "ConvertResult",
    "compress_pdf",
    "COMPRESSION_QUALITY_MIN",
    "COMPRESSION_QUALITY_MAX",
    "is_valid_compression_quality",
    "HeyaError",
    "ConvertError",
    "CompressError",
    "MarkdownError",
    "ConfigError",
    "ErrorCode",
    "WechatError",
    "PdfToWordError",
    "TimeoutError",
    "NetworkError",
    "ValidationError",
]
