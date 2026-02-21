from __future__ import annotations

__all__ = ["TempFileConstants"]


class TempFileConstants:
    DEFAULT_MAX_TOTAL_SIZE: int = 1024 * 1024 * 1024
    DEFAULT_MAX_FILE_AGE: float = 3600.0
    DEFAULT_CLEANUP_INTERVAL: float = 300.0
    SIZE_CLEANUP_THRESHOLD: float = 0.8
    OUTPUT_DIR_NAME: str = "heya_output"
    TEMP_PREFIX: str = "heya"
