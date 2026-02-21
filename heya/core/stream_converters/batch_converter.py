from __future__ import annotations

from collections.abc import Callable, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from heya.core.models import ConvertResult
from heya.core.temp import create_output_path
from heya.core.stream_converters.base import BaseConverter

__all__ = ["BatchConverter"]


class BatchConverter(BaseConverter):
    def __init__(
        self,
        convert_fn: Callable[..., ConvertResult] | None = None,
        max_workers: int = 4,
    ) -> None:
        super().__init__(convert_fn)
        self._max_workers = max_workers

    async def convert(
        self,
        source: str,
        target: str,
        timeout: float = 3.0,
        quality: int = 0,
        **kwargs: Any,
    ) -> ConvertResult:
        if self._convert_fn is None:
            raise RuntimeError("Convert function not set")

        return await self._convert_fn(
            source=source,
            target=target,
            timeout=timeout,
            compress=True,
            quality=quality,
        )

    async def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], None] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        if not sources:
            raise RuntimeError("No sources provided")

        if self._convert_fn is None:
            raise RuntimeError("Convert function not set")

        convert_fn = self._convert_fn
        total = len(sources)
        completed_files: list[str] = []
        timeout = kwargs.get("timeout", 3.0)
        quality = kwargs.get("quality", 0)
        completed_count = 0

        def process_source(source: str) -> tuple[str, ConvertResult | None]:
            output_path = create_output_path()
            try:
                result = convert_fn(
                    source=source,
                    target=output_path,
                    timeout=timeout,
                    compress=True,
                    quality=quality,
                )
                return (source, result)
            except Exception:
                return (source, None)

        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_source = {
                executor.submit(process_source, source): source
                for source in sources
            }

            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    source, result = future.result()
                    completed_count += 1

                    if progress_update_fn:
                        progress_update_fn(completed_count, total, source)

                    if result and result.success and result.output_path:
                        completed_files.append(result.output_path)

                except Exception:
                    completed_count += 1
                    if progress_update_fn:
                        progress_update_fn(completed_count, total, f"Error: {source}")

        if not completed_files:
            raise RuntimeError("Failed to convert any files")

        show_merge_button = len(completed_files) > 1
        yield (completed_files.copy(), len(completed_files), total, "completed" if show_merge_button else None)
