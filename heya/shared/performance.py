from __future__ import annotations

import contextlib
import functools
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable

from heya.shared.logging import get_logger

__all__ = ["PerformanceMonitor", "PerformanceStats", "monitor_performance", "get_performance_monitor"]

logger = get_logger(__name__)


@dataclass
class PerformanceStats:
    operation: str
    count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    errors: int = 0
    last_error: str | None = None

    @property
    def avg_time(self) -> float:
        return self.total_time / self.count if self.count > 0 else 0.0

    def record(self, duration: float, success: bool = True, error: str | None = None) -> None:
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        if not success:
            self.errors += 1
            self.last_error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "count": self.count,
            "total_time": f"{self.total_time:.3f}s",
            "avg_time": f"{self.avg_time:.3f}s",
            "min_time": f"{self.min_time:.3f}s",
            "max_time": f"{self.max_time:.3f}s",
            "errors": self.errors,
            "error_rate": f"{(self.errors / self.count * 100):.2f}%" if self.count > 0 else "0%",
            "last_error": self.last_error,
        }


class PerformanceMonitor:
    def __init__(self) -> None:
        self._stats: dict[str, PerformanceStats] = {}
        self._lock = threading.RLock()
        self._enabled = True

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def record_operation(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        if not self._enabled:
            return

        with self._lock:
            if operation not in self._stats:
                self._stats[operation] = PerformanceStats(operation=operation)
            self._stats[operation].record(duration, success, error)

    def get_stats(self, operation: str | None = None) -> dict[str, Any]:
        with self._lock:
            if operation:
                if operation in self._stats:
                    return self._stats[operation].to_dict()
                return {}
            return {op: stats.to_dict() for op, stats in self._stats.items()}

    def reset(self, operation: str | None = None) -> None:
        with self._lock:
            if operation:
                self._stats.pop(operation, None)
            else:
                self._stats.clear()

    def get_summary(self) -> str:
        with self._lock:
            if not self._stats:
                return "No performance data available"

            lines = ["Performance Summary:", "=" * 50]
            for operation, stats in sorted(self._stats.items()):
                lines.append(f"\n{operation}:")
                lines.append(f"  Calls: {stats.count}")
                lines.append(f"  Total: {stats.total_time:.3f}s")
                lines.append(f"  Avg: {stats.avg_time:.3f}s")
                lines.append(f"  Min: {stats.min_time:.3f}s")
                lines.append(f"  Max: {stats.max_time:.3f}s")
                if stats.errors > 0:
                    lines.append(f"  Errors: {stats.errors} ({(stats.errors / stats.count * 100):.1f}%)")
                    if stats.last_error:
                        lines.append(f"  Last Error: {stats.last_error}")
            return "\n".join(lines)


_performance_monitor: PerformanceMonitor | None = None
_monitor_lock = threading.Lock()


def get_performance_monitor() -> PerformanceMonitor:
    global _performance_monitor
    if _performance_monitor is None:
        with _monitor_lock:
            if _performance_monitor is None:
                _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def monitor_performance(operation: str) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            monitor = get_performance_monitor()
            if not monitor.is_enabled():
                return func(*args, **kwargs)

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_operation(operation, duration, success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_operation(operation, duration, success=False, error=str(e))
                raise

        return wrapper

    return decorator


@contextlib.contextmanager
def measure_performance(operation: str) -> Any:
    monitor = get_performance_monitor()
    if not monitor.is_enabled():
        yield
        return

    start_time = time.time()
    try:
        yield
        duration = time.time() - start_time
        monitor.record_operation(operation, duration, success=True)
    except Exception as e:
        duration = time.time() - start_time
        monitor.record_operation(operation, duration, success=False, error=str(e))
        raise
