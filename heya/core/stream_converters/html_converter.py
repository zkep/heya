from __future__ import annotations

import os
from collections.abc import Callable, Generator
from typing import Any

from heya.core.helpers import convert
from heya.core.models import ConvertResult
from heya.core.cache import get_conversion_cache
from heya.core.temp import create_output_path
from heya.core.stream_converters.base import BaseConverter

__all__ = ["HtmlConverter"]


class HtmlConverter(BaseConverter):
    def __init__(
        self,
        convert_fn: Callable[..., ConvertResult] | None = None,
        use_cache: bool = True,
    ) -> None:
        super().__init__(convert_fn or convert)
        self._use_cache = use_cache
        self._cache = get_conversion_cache() if use_cache else None

    async def convert(
        self,
        source: str,
        target: str,
        timeout: float = 3.0,
        quality: int = 0,
        **kwargs: Any,
    ) -> ConvertResult:
        cache_key = {"timeout": timeout, "quality": quality}

        if self._use_cache and self._cache:
            cached_content = self._cache.get(source, cache_key)
            if cached_content is not None:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as f:
                    f.write(cached_content)
                return ConvertResult(success=True, output_path=target, duration=0.0)

        if self._convert_fn is None:
            raise RuntimeError("Convert function not set")

        result = await self._convert_fn(
            source=source,
            target=target,
            timeout=timeout,
            compress=True,
            quality=quality,
        )

        if self._use_cache and self._cache and result.success and result.output_path:
            try:
                with open(result.output_path, "rb") as f:
                    content = f.read()
                self._cache.put(source, content, cache_key)
            except Exception:
                pass

        return result

    async def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], None] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        total = len(sources)
        completed_files: list[str] = []
        timeout = kwargs.get("timeout",3.0)
        quality = kwargs.get("quality", 0)

        for idx, url in enumerate(sources):
            output_path = create_output_path()

            if progress_update_fn:
                progress_update_fn(idx + 1, total, url)

            if self._convert_fn is None:
                raise RuntimeError("Convert function not set")

            result = await self._convert_fn(
                source=url,
                target=output_path,
                compress=True,
                quality=quality,
            )
            if result.success and result.output_path:
                completed_files.append(result.output_path)

        if not completed_files:
            raise RuntimeError("Failed to convert HTML files")

        show_merge_button = len(completed_files) > 1
        yield (completed_files.copy(), len(completed_files), total, "completed" if show_merge_button else None)
