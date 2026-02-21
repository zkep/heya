from __future__ import annotations

from typing import Generator

import gradio as gr

from heya.web.config.constants import (
    FILENAME_PREFIX_WECHAT,
    MERGE_TITLE_WECHAT,
)
from heya.web.handlers.base_handler import BaseHandler, StreamProgressResponse
from heya.web.i18n import get_texts
from heya.web.utils.merge_utils import merge_pdfs
from heya.web.services.service import ConversionError

__all__ = ["WechatHandler"]


class WechatHandler(BaseHandler):
    def convert_with_error_handling(
        self,
        url: str,
        timeout: float,
        quality: int,
        lang: str,
    ):
        try:
            service = self._get_service(lang)
            result = service.convert_wechat(url, timeout, quality)
            return self._get_wechat_success_response(result, lang)
        except Exception as e:
            return self._handle_conversion_error(e, lang)

    def _get_wechat_success_response(
        self,
        result: list[str],
        lang: str,
    ) -> tuple:
        show_merge_button = len(result) > 1
        return (
            result,
            self._error_handler.reset_convert_button(lang),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=show_merge_button),
        )

    def convert(
        self,
        url: str,
        timeout: float,
        quality: int,
        lang: str,
    ) -> list[str]:
        try:
            service = self._get_service(lang)
            return service.convert_wechat(url, timeout, quality)
        except ConversionError as e:
            raise gr.Error(str(e)) from e

    async def convert_stream(
        self,
        url: str,
        timeout: float,
        quality: int,
        lang: str,
    ) -> Generator[StreamProgressResponse, None, None]:
        try:
            service = self._get_service(lang)
            async for result in service.convert_wechat_stream(
                url, timeout, quality, lang, self._get_stream_progress_update
            ):
                yield result
        except ConversionError as e:
            completed_files, button_update, progress_update = self._get_stream_error_response([], lang)
            yield completed_files, button_update, progress_update
            raise gr.Error(str(e)) from e

    def merge_pdfs(
        self,
        pdf_files: list[str] | None,
        url: str,
        lang: str,
    ) -> tuple[dict, dict]:
        try:
            result_path, button_text = merge_pdfs(
                pdf_files=pdf_files,
                merge_title=MERGE_TITLE_WECHAT,
                filename_prefix=FILENAME_PREFIX_WECHAT,
                lang=lang,
            )
            return gr.update(value=result_path, visible=True), gr.update(
                interactive=True, value=button_text
            )
        except ImportError as e:
            raise gr.Error(get_texts(lang).error_ghostscript) from e
        except Exception as e:
            raise gr.Error(str(e)) from e
