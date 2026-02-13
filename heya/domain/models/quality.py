from __future__ import annotations

__all__ = [
    "COMPRESSION_QUALITY_MIN",
    "COMPRESSION_QUALITY_MAX",
    "is_valid_compression_quality",
]

COMPRESSION_QUALITY_MIN = 0
COMPRESSION_QUALITY_MAX = 2


def is_valid_compression_quality(value: int) -> bool:
    return COMPRESSION_QUALITY_MIN <= value <= COMPRESSION_QUALITY_MAX
