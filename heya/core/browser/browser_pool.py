from __future__ import annotations

import asyncio
import heapq
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from heya.core.browser.playwright_browser import BrowserSession
from heya.core.browser.pool_constants import PoolConstants
from heya.core.config import PrintConfig, load_config
from heya.core.logging import get_logger
from heya.core.performance import measure_performance

__all__ = ["BrowserSessionPool", "PooledSession"]

logger = get_logger(__name__)


@dataclass(order=True)
class PooledSession:
    session: BrowserSession = field(compare=False)
    in_use: bool = field(default=False, compare=False)
    last_used: float = field(default_factory=time.time)
    use_count: int = field(default=0, compare=False)
    health_score: int = field(default=100, compare=False)
    priority: int = field(default=0)
    deleted: bool = field(default=False, compare=False)

    def update_priority(self) -> None:
        self.priority = self.use_count * 10 + self.health_score

    def is_healthy(self) -> bool:
        return self.health_score > 0 and self.health_score <= 100


class BrowserSessionPool:
    def __init__(
        self,
        max_size: int = PoolConstants.DEFAULT_MAX_SIZE,
        max_idle_time: float = PoolConstants.DEFAULT_MAX_IDLE_TIME,
        timeout: float | None = None,
        launch_args: list[str] | None = None,
        print_config: PrintConfig | None = None,
        initial_size: int = 1,
    ) -> None:
        self._max_size = max_size
        self._max_idle_time = max_idle_time
        self._timeout = timeout if timeout is not None else load_config().browser.timeout
        self._launch_args = (
            launch_args if launch_args is not None else load_config().browser.launch_args
        )
        self._print_config = print_config or load_config().print

        self._pool: list[PooledSession] = []
        self._priority_queue: list[PooledSession] = []
        self._lock = asyncio.Lock()
        self._cleanup_interval = PoolConstants.DEFAULT_CLEANUP_INTERVAL
        self._last_cleanup = time.time()
        self._session_available = asyncio.Condition(self._lock)
        self._initial_size = initial_size
        self._is_warmed_up = False
        self._cleanup_count = 0
        self._rebuild_threshold = 100

    async def _ensure_warmed_up(self) -> None:
        if not self._is_warmed_up and self._initial_size > 0:
            await self._warm_up_pool(self._initial_size)

    async def _warm_up_pool(self, size: int) -> None:
        if self._is_warmed_up:
            return

        actual_size = min(size, self._max_size)
        for _ in range(actual_size):
            try:
                session = BrowserSession(
                    self._timeout, self._launch_args, self._print_config
                )
                await session.__aenter__()
                pooled_session = PooledSession(session=session, in_use=False)
                pooled_session.update_priority()
                self._pool.append(pooled_session)
                heapq.heappush(self._priority_queue, pooled_session)
                logger.debug(f"Pre-warmed browser session ({len(self._pool)}/{actual_size})")
            except Exception as e:
                logger.warning(f"Failed to pre-warm browser session: {e}")

        self._is_warmed_up = True
        logger.info(f"Browser pool pre-warmed with {len(self._pool)} sessions")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[BrowserSession]:
        with measure_performance("browser_pool_acquire"):
            pooled_session = await self._acquire_session()
            try:
                pooled_session.in_use = True
                pooled_session.use_count += 1
                pooled_session.last_used = time.time()
                pooled_session.update_priority()
                yield pooled_session.session
            finally:
                async with self._lock:
                    pooled_session.in_use = False
                    pooled_session.last_used = time.time()
                    await self._cleanup_idle_sessions()
                    self._session_available.notify_all()

    async def _acquire_session(self) -> PooledSession:
        await self._ensure_warmed_up()
        async with self._lock:
            await self._cleanup_idle_sessions()

            for pooled_session in self._pool:
                if not pooled_session.in_use and pooled_session.is_healthy():
                    logger.debug(
                        f"Reusing existing browser session (use count: {pooled_session.use_count}, health: {pooled_session.health_score})"
                    )
                    return pooled_session

            if len(self._pool) < self._max_size:
                logger.debug(
                    f"Creating new browser session (pool size: {len(self._pool) + 1}/{self._max_size})"
                )
                session = BrowserSession(
                    self._timeout, self._launch_args, self._print_config
                )
                await session.__aenter__()
                pooled_session = PooledSession(session=session, in_use=True)
                pooled_session.update_priority()
                self._pool.append(pooled_session)
                heapq.heappush(self._priority_queue, pooled_session)
                return pooled_session

            logger.warning(
                f"Browser session pool full ({self._max_size}), waiting for available session"
            )
            return await self._wait_for_available_session()

    async def _wait_for_available_session(self) -> PooledSession:
        deadline = time.time() + PoolConstants.MAX_WAIT_TIME

        while time.time() < deadline:
            for pooled_session in self._pool:
                if not pooled_session.in_use:
                    return pooled_session

            remaining = deadline - time.time()
            if remaining > 0:
                try:
                    await asyncio.wait_for(self._session_available.wait(), remaining)
                except asyncio.TimeoutError:
                    pass

        raise RuntimeError(
            f"Timeout waiting for available browser session after {PoolConstants.MAX_WAIT_TIME}s"
        )

    async def _cleanup_idle_sessions(self) -> None:
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        self._cleanup_count += 1
        sessions_to_remove: list[PooledSession] = []

        for pooled_session in self._pool:
            if (
                not pooled_session.in_use
                and (now - pooled_session.last_used) > self._max_idle_time
            ) or not pooled_session.is_healthy():
                sessions_to_remove.append(pooled_session)

        for pooled_session in sessions_to_remove:
            reason = (
                f"idle for {now - pooled_session.last_used:.1f}s"
                if not pooled_session.in_use
                else "unhealthy"
            )
            logger.debug(f"Closing browser session ({reason})")
            try:
                await pooled_session.session.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
            if pooled_session in self._pool:
                self._pool.remove(pooled_session)
            pooled_session.deleted = True

        if self._cleanup_count >= self._rebuild_threshold:
            self._rebuild_priority_queue()
            self._cleanup_count = 0

    def _rebuild_priority_queue(self) -> None:
        active_sessions = [s for s in self._pool if not s.deleted]
        self._priority_queue = active_sessions.copy()
        heapq.heapify(self._priority_queue)
        logger.debug(f"Rebuilt priority queue with {len(self._priority_queue)} sessions")

    async def close_all(self) -> None:
        async with self._lock:
            for pooled_session in self._pool:
                try:
                    await pooled_session.session.close()
                except Exception as e:
                    logger.warning(f"Error closing session: {e}")
            self._pool.clear()

    @property
    def pool_size(self) -> int:
        return len(self._pool)

    @property
    def active_sessions(self) -> int:
        return sum(1 for s in self._pool if s.in_use)

    @property
    def idle_sessions(self) -> int:
        return sum(1 for s in self._pool if not s.in_use)

    def get_stats(self) -> dict[str, Any]:
        total_uses = sum(s.use_count for s in self._pool)
        healthy_sessions = sum(1 for s in self._pool if s.is_healthy())
        return {
            "pool_size": len(self._pool),
            "active_sessions": self.active_sessions,
            "idle_sessions": self.idle_sessions,
            "healthy_sessions": healthy_sessions,
            "total_uses": total_uses,
            "max_size": self._max_size,
            "is_warmed_up": self._is_warmed_up,
        }


_global_pool: BrowserSessionPool | None = None
_pool_lock = asyncio.Lock()


async def get_global_pool() -> BrowserSessionPool:
    global _global_pool
    if _global_pool is None:
        async with _pool_lock:
            if _global_pool is None:
                _global_pool = BrowserSessionPool()
    return _global_pool


async def close_global_pool() -> None:
    global _global_pool
    async with _pool_lock:
        if _global_pool is not None:
            await _global_pool.close_all()
            _global_pool = None
