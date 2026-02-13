from __future__ import annotations

import os
from collections.abc import Callable, Generator
from typing import Any

import gradio as gr

from heya.application import convert_md, create_markdown_converter
from heya.domain import ConvertResult
from heya.shared.temp import create_output_path
from heya.web.converters.base import BaseConverter

__all__ = ["MarkdownConverter"]


class MarkdownConverter(BaseConverter):
    def __init__(
        self,
        convert_fn: Callable[..., ConvertResult] | None = None,
    ) -> None:
        super().__init__(convert_fn or convert_md)

    def convert(
        self,
        source: str,
        target: str,
        timeout: float = 3.0,
        quality: int = 0,
        **kwargs: Any,
    ) -> ConvertResult:
        if self._convert_fn is None:
            raise RuntimeError("Convert function not set")

        return self._convert_fn(
            source=source,
            target=target,
            timeout=timeout,
            compress=True,
            quality=quality,
        )

    def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
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

            progress_update = (
                gr.update(interactive=False, value=f"{idx + 1}/{total} {filename}")
                if progress_update_fn
                else gr.update(interactive=False)
            )
            yield (
                completed_files.copy(),
                progress_update,
                gr.update(visible=False),
            )

            result = converter.convert(
                source=md_file,
                target=output_path,
                compress=True,
                quality=quality,
            )
            if result.success and result.output_path:
                completed_files.append(result.output_path)

        if not completed_files:
            raise RuntimeError("Failed to convert Markdown files")

        show_merge_button = len(completed_files) > 1
        yield (
            completed_files.copy(),
            gr.update(interactive=True),
            gr.update(visible=show_merge_button),
        )
