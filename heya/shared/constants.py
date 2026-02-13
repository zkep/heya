from __future__ import annotations

__all__ = [
    "BrowserConstants",
    "TempFileConstants",
    "ScrollConstants",
    "PoolConstants",
]


class BrowserConstants:
    DEFAULT_TIMEOUT: float = 3.0
    TIMEOUT_MULTIPLIER: int = 1000
    DEFAULT_LAUNCH_ARGS: list[str] = ["--no-sandbox", "--disable-dev-shm-usage"]


class PoolConstants:
    DEFAULT_MAX_SIZE: int = 3
    DEFAULT_MAX_IDLE_TIME: float = 300.0
    DEFAULT_CLEANUP_INTERVAL: float = 60.0
    MAX_WAIT_TIME: float = 30.0
    POLL_INTERVAL: float = 0.1


class TempFileConstants:
    DEFAULT_MAX_TOTAL_SIZE: int = 1024 * 1024 * 1024
    DEFAULT_MAX_FILE_AGE: float = 3600.0
    DEFAULT_CLEANUP_INTERVAL: float = 300.0
    SIZE_CLEANUP_THRESHOLD: float = 0.8
    OUTPUT_DIR_NAME: str = "heya_output"
    TEMP_PREFIX: str = "heya"


class ScrollConstants:
    SCROLL_DISTANCE: int = 100
    SCROLL_INTERVAL: int = 100
