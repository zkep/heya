from __future__ import annotations

__all__ = ["PoolConstants"]


class PoolConstants:
    DEFAULT_MAX_SIZE: int = 3
    DEFAULT_MAX_IDLE_TIME: float = 300.0
    DEFAULT_CLEANUP_INTERVAL: float = 60.0
    MAX_WAIT_TIME: float = 30.0
    POLL_INTERVAL: float = 0.1
