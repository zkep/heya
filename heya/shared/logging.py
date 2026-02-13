from __future__ import annotations

import logging
import sys
import traceback
import urllib.parse
from dataclasses import dataclass
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

ISSUES_URL = "https://github.com/zkep/heya/issues/new"


@dataclass
class ErrorInfo:
    error_message: str
    error_type: str
    issue_url: str
    stack_trace: str
    python_version: str
    platform: str


class PerformanceLogHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self._operation_times: dict[str, list[float]] = {}

    def emit(self, record: logging.LogRecord) -> None:
        operation = getattr(record, "operation", None)
        duration = getattr(record, "duration", None)
        if operation is not None and duration is not None:
            self._operation_times.setdefault(operation, []).append(duration)

    def get_stats(self) -> dict[str, dict[str, float]]:
        stats = {}
        for operation, times in self._operation_times.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "total": sum(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                }
        return stats

    def clear(self) -> None:
        self._operation_times.clear()


def _build_error_info(error: str | Exception) -> tuple[str, str, str]:
    error_msg = str(error)
    error_type = type(error).__name__ if isinstance(error, Exception) else "Error"
    stack_trace = traceback.format_exc()
    return error_msg, error_type, stack_trace


def _build_issue_url(error_msg: str, error_type: str, stack_trace: str) -> str:
    title = f"[{error_type}] {error_msg[:100]}"
    body = f"""## Error Description
{error_msg}

## Stack Trace
```
{stack_trace}
```

## Environment
- Python Version: {sys.version}
- Operating System: {sys.platform}"""

    encoded_title = urllib.parse.quote(title)
    encoded_body = urllib.parse.quote(body)
    return f"{ISSUES_URL}?title={encoded_title}&body={encoded_body}"


def format_error_with_issue(error: str | Exception) -> str:
    error_info = get_error_info(error)
    return f"{error_info.error_message}\n\nPlease report this issue at: {error_info.issue_url}"


def get_error_info(error: str | Exception) -> ErrorInfo:
    error_msg, error_type, stack_trace = _build_error_info(error)
    issue_url = _build_issue_url(error_msg, error_type, stack_trace)

    return ErrorInfo(
        error_message=error_msg,
        error_type=error_type,
        issue_url=issue_url,
        stack_trace=stack_trace,
        python_version=sys.version,
        platform=sys.platform,
    )


_logger_cache: dict[str, logging.Logger] = {}


def get_logger(name: str, level: LogLevel = "INFO") -> logging.Logger:
    if name in _logger_cache:
        logger = _logger_cache[name]
    else:
        logger = logging.getLogger(name)
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(DEFAULT_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        _logger_cache[name] = logger

    logger.setLevel(level)
    return logger


def setup_root_logger(level: LogLevel = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format=DEFAULT_FORMAT,
        stream=sys.stderr,
    )


logger = get_logger("heya")
