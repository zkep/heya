from __future__ import annotations

import hashlib
import heapq
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from heya.shared.logging import get_logger

__all__ = ["CacheEntry", "ConversionCache", "get_conversion_cache"]

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    content: bytes
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    size: int = field(init=False)

    def __post_init__(self) -> None:
        self.size = len(self.content)

    def touch(self) -> None:
        self.access_count += 1
        self.last_accessed = time.time()

    @property
    def age(self) -> float:
        return time.time() - self.created_at

    @property
    def idle_time(self) -> float:
        return time.time() - self.last_accessed

    @property
    def score(self) -> float:
        access_weight = 0.4
        age_weight = 0.3
        idle_weight = 0.3
        return (
            self.access_count * access_weight
            - self.age * age_weight
            - self.idle_time * idle_weight
        )


class ConversionCache:
    def __init__(
        self,
        max_size: int = 128,
        max_age: float = 3600.0,
        max_idle_time: float = 1800.0,
        max_memory_mb: int = 512,
    ) -> None:
        self._max_size = max_size
        self._max_age = max_age
        self._max_idle_time = max_idle_time
        self._max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: dict[str, CacheEntry] = {}
        self._lru: OrderedDict[str, None] = OrderedDict()
        self._score_heap: list[tuple[float, str]] = []
        self._heap_dirty = False
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._total_memory = 0

    def _generate_key(self, source: str, options: dict[str, Any] | None = None) -> str:
        key_data = source.encode("utf-8")
        if options:
            import json

            key_data += json.dumps(options, sort_keys=True).encode("utf-8")
        return hashlib.sha256(key_data).hexdigest()

    def _update_lru(self, key: str) -> None:
        if key in self._lru:
            self._lru.move_to_end(key)
        else:
            self._lru[key] = None

    def _evict_lru(self) -> str | None:
        if not self._lru:
            return None
        key, _ = self._lru.popitem(last=False)
        return key

    def _evict_by_score(self) -> str | None:
        if not self._cache:
            return None
        
        if self._heap_dirty:
            self._rebuild_heap()
        
        while self._score_heap:
            score, key = self._score_heap[0]
            if key in self._cache and abs(self._cache[key].score - score) < 0.0001:
                heapq.heappop(self._score_heap)
                return key
            heapq.heappop(self._score_heap)
        
        return None

    def _rebuild_heap(self) -> None:
        self._score_heap = [(entry.score, key) for key, entry in self._cache.items()]
        heapq.heapify(self._score_heap)
        self._heap_dirty = False
        logger.debug(f"Rebuilt score heap with {len(self._score_heap)} entries")

    def _check_memory_limit(self) -> bool:
        return self._total_memory >= self._max_memory_bytes

    def _evict_for_memory(self) -> int:
        evicted = 0
        while self._check_memory_limit() and self._cache:
            key = self._evict_lru()
            if key:
                entry = self._cache.pop(key, None)
                if entry:
                    self._total_memory -= entry.size
                    evicted += 1
                    logger.debug(f"Evicted cache entry for memory: {key[:16]}...")
        return evicted

    def get(self, source: str, options: dict[str, Any] | None = None) -> bytes | None:
        key = self._generate_key(source, options)

        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                logger.debug(f"Cache miss for key: {key[:16]}...")
                return None

            if entry.age > self._max_age or entry.idle_time > self._max_idle_time:
                del self._cache[key]
                self._lru.pop(key, None)
                self._total_memory -= entry.size
                self._heap_dirty = True
                self._misses += 1
                logger.debug(f"Cache entry expired for key: {key[:16]}...")
                return None

            entry.touch()
            self._update_lru(key)
            self._heap_dirty = True
            self._hits += 1
            logger.debug(
                f"Cache hit for key: {key[:16]}... (access count: {entry.access_count})"
            )
            return entry.content

    def put(
        self, source: str, content: bytes, options: dict[str, Any] | None = None
    ) -> None:
        key = self._generate_key(source, options)
        content_size = len(content)

        with self._lock:
            if key in self._cache:
                old_entry = self._cache[key]
                self._total_memory -= old_entry.size
                self._lru.pop(key, None)
                self._heap_dirty = True

            while len(self._cache) >= self._max_size or self._check_memory_limit():
                evicted_key = self._evict_lru()
                if evicted_key:
                    entry = self._cache.pop(evicted_key, None)
                    if entry:
                        self._total_memory -= entry.size
                        self._heap_dirty = True
                        logger.debug(f"Evicted cache entry: {evicted_key[:16]}...")
                else:
                    break

            if content_size > self._max_memory_bytes:
                logger.warning(
                    f"Content too large for cache ({content_size} bytes > {self._max_memory_bytes} bytes)"
                )
                return

            self._cache[key] = CacheEntry(content=content)
            self._update_lru(key)
            heapq.heappush(self._score_heap, (self._cache[key].score, key))
            self._total_memory += content_size
            logger.debug(
                f"Cache entry added for key: {key[:16]}... (size: {len(self._cache)}, memory: {self._total_memory / 1024 / 1024:.2f} MB)"
            )

    def _evict_oldest(self) -> None:
        key = self._evict_lru()
        if key:
            entry = self._cache.pop(key, None)
            if entry:
                self._total_memory -= entry.size
                logger.debug(f"Evicted oldest cache entry: {key[:16]}...")

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._lru.clear()
            self._total_memory = 0
            self._hits = 0
            self._misses = 0
            logger.debug("Cache cleared")

    def cleanup_expired(self) -> int:
        with self._lock:
            expired_keys = [
                key
                for key, entry in self._cache.items()
                if entry.age > self._max_age or entry.idle_time > self._max_idle_time
            ]
            for key in expired_keys:
                entry = self._cache.pop(key)
                self._lru.pop(key, None)
                self._total_memory -= entry.size
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (
                (self._hits / total_requests * 100) if total_requests > 0 else 0.0
            )

            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
                "max_age": self._max_age,
                "max_idle_time": self._max_idle_time,
                "memory_usage_mb": f"{self._total_memory / 1024 / 1024:.2f}",
                "max_memory_mb": self._max_memory_bytes / 1024 / 1024,
            }


_conversion_cache: ConversionCache | None = None
_cache_lock = threading.Lock()


def get_conversion_cache() -> ConversionCache:
    global _conversion_cache
    if _conversion_cache is None:
        with _cache_lock:
            if _conversion_cache is None:
                _conversion_cache = ConversionCache()
    return _conversion_cache
