from __future__ import annotations

__all__ = ["BrowserConstants"]


class BrowserConstants:
    DEFAULT_TIMEOUT: float = 3.0
    TIMEOUT_MULTIPLIER: int = 1000
    DEFAULT_LAUNCH_ARGS: list[str] = ["--no-sandbox", "--disable-dev-shm-usage"]
