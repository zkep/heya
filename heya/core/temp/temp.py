from __future__ import annotations

import os
import shutil
import tempfile
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from heya.core.temp.constants import TempFileConstants

__all__ = [
    "TempFileManager",
    "OutputFileManager",
    "create_output_path",
    "TempFileTracker",
]


@dataclass
class TempFileInfo:
    path: str
    created_at: float = field(default_factory=time.time)
    size: int = 0
    ref_count: int = 1
    _size_valid: bool = field(default=True, init=False, compare=False)
    _mtime: float = field(default_factory=lambda: 0.0, init=False, compare=False)
    
    def invalidate_size(self) -> None:
        self._size_valid = False
    
    def recalc_size(self) -> int:
        if os.path.isfile(self.path):
            self.size = os.path.getsize(self.path)
        elif os.path.isdir(self.path):
            self.size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(self.path)
                for filename in filenames
            )
        self._size_valid = True
        self._mtime = os.path.getmtime(self.path) if os.path.exists(self.path) else 0.0
        return self.size
    
    def get_size(self) -> int:
        if not self._size_valid or (os.path.exists(self.path) and abs(os.path.getmtime(self.path) - self._mtime) > 1.0):
            return self.recalc_size()
        return self.size


class TempFileTracker:
    _instance: "TempFileTracker | None" = None
    _lock = threading.Lock()
    _initialized: bool = False
    _files: dict[str, TempFileInfo] = {}
    _max_total_size: int = TempFileConstants.DEFAULT_MAX_TOTAL_SIZE
    _max_file_age: float = TempFileConstants.DEFAULT_MAX_FILE_AGE
    _cleanup_interval: float = TempFileConstants.DEFAULT_CLEANUP_INTERVAL
    _last_cleanup: float = 0.0
    _cleanup_thread: threading.Thread | None = None
    _running: bool = False

    def __new__(cls) -> "TempFileTracker":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._files = {}
        self._max_total_size = TempFileConstants.DEFAULT_MAX_TOTAL_SIZE
        self._max_file_age = TempFileConstants.DEFAULT_MAX_FILE_AGE
        self._cleanup_interval = TempFileConstants.DEFAULT_CLEANUP_INTERVAL
        self._last_cleanup = time.time()
        self._cleanup_thread = None
        self._running = False

    def track(self, path: str) -> None:
        with self._lock:
            if path not in self._files:
                info = TempFileInfo(path=path)
                info.recalc_size()
                self._files[path] = info
                self._check_size_limit()
            else:
                self._files[path].ref_count += 1

    def release(self, path: str) -> None:
        with self._lock:
            if path in self._files:
                self._files[path].ref_count -= 1
                if self._files[path].ref_count <= 0:
                    del self._files[path]

    def start_background_cleanup(self, interval: float = 300.0) -> None:
        if self._running:
            return
        self._running = True
        self._cleanup_interval = interval
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def stop_background_cleanup(self) -> None:
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
            self._cleanup_thread = None

    def _cleanup_loop(self) -> None:
        while self._running:
            time.sleep(self._cleanup_interval)
            self.cleanup_expired()

    def cleanup_expired(self) -> int:
        with self._lock:
            now = time.time()
            expired_paths = [
                path
                for path, info in self._files.items()
                if now - info.created_at > self._max_file_age
            ]
            for path in expired_paths:
                self._safe_remove(path)
                del self._files[path]
            return len(expired_paths)

    def cleanup_all(self) -> int:
        with self._lock:
            count = len(self._files)
            for path in list(self._files.keys()):
                self._safe_remove(path)
            self._files.clear()
            return count

    def _check_size_limit(self) -> None:
        total_size = sum(info.get_size() for info in self._files.values())
        if total_size > self._max_total_size:
            sorted_files = sorted(
                self._files.items(),
                key=lambda x: x[1].created_at,
            )
            removed_size = 0
            target_size = (
                total_size
                - self._max_total_size * TempFileConstants.SIZE_CLEANUP_THRESHOLD
            )
            for path, info in sorted_files:
                if removed_size >= target_size:
                    break
                self._safe_remove(path)
                removed_size += info.get_size()
                del self._files[path]

    def _safe_remove(self, path: str) -> None:
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
        except Exception:
            pass

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total_files": len(self._files),
                "total_size": sum(info.get_size() for info in self._files.values()),
                "total_size_mb": sum(info.get_size() for info in self._files.values())
                / (1024 * 1024),
                "max_size_mb": self._max_total_size / (1024 * 1024),
            }


_tracker = TempFileTracker()


class TempFileManager:
    def __init__(self, prefix: str = "heya") -> None:
        self.prefix = prefix
        self._temp_dir: str | None = None
        self._tracked_files: list[str] = []

    def __enter__(self) -> "TempFileManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: type[BaseException] | None,
    ) -> None:
        self.cleanup()

    def create_temp_dir(self) -> str:
        if self._temp_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix=self.prefix)
            _tracker.track(self._temp_dir)
            self._tracked_files.append(self._temp_dir)
        return self._temp_dir

    def create_temp_file(
        self, content: str, filename: str, encoding: str = "utf-8"
    ) -> str:
        temp_dir = self.create_temp_dir()
        temp_file = os.path.join(temp_dir, filename)
        with open(temp_file, "w", encoding=encoding) as f:
            f.write(content)
        _tracker.track(temp_file)
        self._tracked_files.append(temp_file)
        return temp_file

    def cleanup(self) -> None:
        for path in reversed(self._tracked_files):
            _tracker.release(path)
        self._tracked_files.clear()
        if self._temp_dir and os.path.exists(self._temp_dir):
            _tracker.release(self._temp_dir)
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass
        self._temp_dir = None

    @property
    def temp_dir(self) -> str | None:
        return self._temp_dir


class OutputFileManager:
    def __init__(self, output_dir: str | None = None) -> None:
        if output_dir is None:
            output_dir = os.path.join(
                tempfile.gettempdir(), TempFileConstants.OUTPUT_DIR_NAME
            )
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def create_output_path(self, prefix: str = "heya", extension: str = "pdf") -> str:
        output_filename = f"{prefix}_{uuid.uuid4().hex[:8]}.{extension}"
        return os.path.join(self.output_dir, output_filename)


_output_manager = OutputFileManager()


def create_output_path(prefix: str = "heya", extension: str = "pdf") -> str:
    return _output_manager.create_output_path(prefix, extension)


def start_background_cleanup(interval: float = 300.0) -> None:
    _tracker.start_background_cleanup(interval)


def stop_background_cleanup() -> None:
    _tracker.stop_background_cleanup()


def get_temp_file_stats() -> dict[str, Any]:
    return _tracker.get_stats()
