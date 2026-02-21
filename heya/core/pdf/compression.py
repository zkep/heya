from __future__ import annotations

from collections.abc import Callable

from heya.core.exceptions import CompressError
from heya.core.models import (
    COMPRESSION_QUALITY_MAX,
    COMPRESSION_QUALITY_MIN,
    PdfContent,
    is_valid_compression_quality,
)

__all__ = ["compress_pdf"]


def compress_pdf(
    content: PdfContent,
    quality: int,
    compress_fn: Callable[[PdfContent, int], PdfContent],
) -> PdfContent:
    if not is_valid_compression_quality(quality):
        raise CompressError(
            f"Invalid quality level: {quality}. "
            f"Must be {COMPRESSION_QUALITY_MIN}-{COMPRESSION_QUALITY_MAX}."
        )
    return compress_fn(content, quality)
