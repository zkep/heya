from __future__ import annotations

from collections.abc import Callable, Generator
from typing import Any

import gradio as gr

from heya.application import convert
from heya.domain import ConvertResult
from heya.shared.cache import get_conversion_cache
from heya.shared.temp import create_output_path
from heya.web.converters.base import BaseConverter

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

    def convert(
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
                import os

                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as f:
                    f.write(cached_content)
                return ConvertResult(success=True, output_path=target, duration=0.0)

        if self._convert_fn is None:
            raise RuntimeError("Convert function not set")

        result = self._convert_fn(
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

    def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
        total = len(sources)
        completed_files: list[str] = []
        timeout = kwargs.get("timeout", 3.0)
        quality = kwargs.get("quality", 0)

        for idx, url in enumerate(sources):
            output_path = create_output_path()

            progress_update = (
                gr.update(interactive=False, value=f"{idx + 1}/{total} {url}")
                if progress_update_fn
                else gr.update(interactive=False)
            )
            yield (
                completed_files.copy(),
                progress_update,
                gr.update(visible=False),
            )

            if self._convert_fn is None:
                raise RuntimeError("Convert function not set")

            result = self._convert_fn(
                source=url,
                target=output_path,
                timeout=timeout,
                compress=True,
                quality=quality,
            )
            if result.success and result.output_path:
                completed_files.append(result.output_path)

        if not completed_files:
            raise RuntimeError("Failed to convert HTML files")

        show_merge_button = len(completed_files) > 1
        yield (
            completed_files.copy(),
            gr.update(interactive=True),
            gr.update(visible=show_merge_button),
        )
