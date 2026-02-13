from __future__ import annotations

from typing import Any

import gradio as gr

from heya.web.handlers.error_handler import ErrorHandler, GradioUpdate
from heya.web.service import ConversionError, WebConvertService

__all__ = ["BaseHandler", "HandlerResponse", "StreamProgressResponse"]

HandlerResponse = tuple[
    str | list[str], GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate
]
StreamProgressResponse = tuple[list[str] | None, dict[str, Any], dict[str, Any]]


class BaseHandler:
    def __init__(
        self,
        error_handler: ErrorHandler | None = None,
        service: WebConvertService | None = None,
    ) -> None:
        self._error_handler = error_handler or ErrorHandler()
        self._service = service

    def _get_service(self, lang: str) -> WebConvertService:
        if self._service is None:
            return WebConvertService(lang=lang)
        self._service.set_language(lang)
        return self._service

    def _handle_conversion_error(
        self,
        e: Exception,
        lang: str,
    ) -> HandlerResponse:
        if isinstance(e, ConversionError):
            error_info = self._error_handler.handle_conversion_error(e, lang)
            error_box_update, error_url_update, report_btn_visible, cancel_btn_visible, error_buttons_visible = (
                self._error_handler.show_error_dialog(error_info, lang)
            )
            return (
                [],
                self._error_handler.reset_convert_button(lang),
                error_box_update,
                error_url_update,
                report_btn_visible,
                cancel_btn_visible,
                error_buttons_visible,
            )
        raise gr.Error(str(e)) from e

    def _get_success_response(
        self,
        result: str | list[str],
        lang: str,
    ) -> HandlerResponse:
        return (
            result,
            self._error_handler.reset_convert_button(lang),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    def _get_stream_progress_update(
        self,
        current: int,
        total: int,
        filename: str,
    ) -> GradioUpdate:
        return gr.update(interactive=False, value=f"{current}/{total} {filename}")

    def _get_stream_error_response(
        self,
        completed_files: list[str],
        lang: str,
    ) -> tuple[list[str], GradioUpdate, GradioUpdate]:
        return (
            completed_files.copy(),
            self._error_handler.reset_convert_button(lang),
            gr.update(visible=False),
        )

    def _get_stream_success_response(
        self,
        completed_files: list[str],
        lang: str,
        show_merge_button: bool = False,
    ) -> tuple[list[str], GradioUpdate, GradioUpdate]:
        return (
            completed_files.copy(),
            self._error_handler.reset_convert_button(lang),
            gr.update(visible=show_merge_button),
        )
