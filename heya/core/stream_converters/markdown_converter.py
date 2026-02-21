from __future__ import annotations

import os
from collections.abc import Callable, Generator
from typing import Any

from heya.core.helpers import convert_md
from heya.core.markdown import create_markdown_converter
from heya.core.models import ConvertResult
from heya.core.temp import create_output_path
from heya.core.stream_converters.base import BaseConverter

__all__ = ["MarkdownConverter"]


class MarkdownConverter(BaseConverter):
    def __init__(
        self,
        convert_fn: Callable[..., ConvertResult] | None = None,
    ) -> None:
        super().__init__(convert_fn or convert_md)

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
            raise RuntimeError("No Markdown files provided")

        total = len(sources)
        completed_files: list[str] = []
        converter = create_markdown_converter(kwargs.get("timeout", 3.0), compress=True)
        quality = kwargs.get("quality", 0)

        for idx, md_file in enumerate(sources):
            filename = os.path.basename(md_file)
            safe_title = os.path.splitext(filename)[0]
            output_dir = create_output_path()
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{safe_title}.pdf")

            if progress_update_fn:
                progress_update_fn(idx + 1, total, filename)

            result = await converter(
                source=md_file,
                target=output_path,
                compress=True,
                quality=quality,
            )
            if result.success and result.output_path:
                completed_files.append(result.output_path)
                yield (completed_files.copy(), idx + 1, total, None)

        if not completed_files:
            raise RuntimeError("Failed to convert Markdown files")

        show_merge_button = len(completed_files) > 1
        yield (completed_files.copy(), len(completed_files), total, "completed" if show_merge_button else None)
