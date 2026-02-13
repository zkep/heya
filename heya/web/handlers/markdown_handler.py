from __future__ import annotations

from typing import Generator

import gradio as gr

from heya.web.constants import MAX_FILES_PER_BATCH
from heya.web.handlers.base_handler import BaseHandler, StreamProgressResponse
from heya.web.i18n import get_texts
from heya.web.service import ConversionError

__all__ = ["MarkdownHandler"]


class MarkdownHandler(BaseHandler):
    def convert(
        self,
        md_files: list[str] | str,
        timeout: float,
        quality: int,
        lang: str,
    ) -> str | list[str]:
        try:
            service = self._get_service(lang)
            if isinstance(md_files, str) or (
                isinstance(md_files, list) and len(md_files) == 1
            ):
                md_file = md_files[0] if isinstance(md_files, list) else md_files
                return service.convert_markdown(md_file, timeout, quality)
            else:
                results = []
                for md_file in md_files:
                    result = service.convert_markdown(md_file, timeout, quality)
                    results.append(result)
                return results
        except ConversionError as e:
            raise gr.Error(str(e)) from e

    def _validate_md_files(self, md_files: list[str] | str, lang: str) -> list[str]:
        if not md_files:
            raise gr.Error(get_texts(lang).error_no_md)

        if isinstance(md_files, str):
            md_files = [md_files]

        total = len(md_files)
        if total > MAX_FILES_PER_BATCH:
            raise gr.Error(
                get_texts(lang).error_convert.format(
                    f"Maximum {MAX_FILES_PER_BATCH} files allowed, got {total}"
                )
            )

        return md_files

    def convert_stream(
        self,
        md_files: list[str] | str,
        timeout: float,
        quality: int,
        lang: str,
    ) -> Generator[StreamProgressResponse, None, None]:
        md_files = self._validate_md_files(md_files, lang)

        try:
            service = self._get_service(lang)
            yield from service.convert_markdown_stream(
                md_files, timeout, quality, lang, self._get_stream_progress_update
            )
        except ConversionError as e:
            completed_files, button_update, progress_update = self._get_stream_error_response([], lang)
            yield completed_files, button_update, progress_update
            raise gr.Error(str(e)) from e
