from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import gradio as gr

if TYPE_CHECKING:
    GradioUpdate = dict
else:
    GradioUpdate = dict

from heya.shared import ErrorInfo
from heya.web.constants import (
    FILENAME_PREFIX_MARKDOWN,
    MERGE_TITLE_MARKDOWN,
)
from heya.web.handlers import HtmlHandler, MarkdownHandler, WechatHandler
from heya.web.handlers import ErrorHandler
from heya.web.handlers.base_handler import HandlerResponse, StreamProgressResponse
from heya.web.i18n import get_texts
from heya.web.merge_utils import merge_pdfs
from heya.web.service import WebConvertService

__all__ = [
    "convert_html_to_pdf_with_error_handling",
    "convert_md_to_pdf",
    "convert_md_to_pdf_stream",
    "convert_wechat_to_pdf",
    "convert_wechat_to_pdf_stream",
    "merge_md_pdfs",
    "merge_wechat_pdfs",
    "convert_pdf_to_word_with_error_handling",
    "show_error_dialog",
    "open_issue_url",
    "hide_error_dialog",
]

_error_handler = ErrorHandler()
_html_handler = HtmlHandler(_error_handler)
_markdown_handler = MarkdownHandler(_error_handler)
_wechat_handler = WechatHandler(_error_handler)


def convert_html_to_pdf_with_error_handling(
    url: str,
    timeout: float,
    quality: int,
    lang: str,
) -> HandlerResponse:
    return _html_handler.convert_with_error_handling(url, timeout, quality, lang)


def convert_md_to_pdf(
    md_files: list[str] | str,
    timeout: float,
    quality: int,
    lang: str,
) -> str | list[str]:
    return _markdown_handler.convert(md_files, timeout, quality, lang)


def convert_md_to_pdf_stream(
    md_files: list[str] | str,
    timeout: float,
    quality: int,
    lang: str,
) -> Generator[StreamProgressResponse, None, None]:
    yield from _markdown_handler.convert_stream(md_files, timeout, quality, lang)


def convert_wechat_to_pdf(
    url: str,
    timeout: float,
    quality: int,
    lang: str,
) -> list[str]:
    return _wechat_handler.convert(url, timeout, quality, lang)


def convert_wechat_to_pdf_stream(
    url: str,
    timeout: float,
    quality: int,
    lang: str,
) -> Generator[StreamProgressResponse, None, None]:
    yield from _wechat_handler.convert_stream(url, timeout, quality, lang)


def merge_md_pdfs(
    pdf_files: list[str] | None,
    md_files: list[str] | None,
    lang: str,
) -> tuple[dict, dict]:
    try:
        result_path, button_text = merge_pdfs(
            pdf_files=pdf_files,
            merge_title=MERGE_TITLE_MARKDOWN,
            filename_prefix=FILENAME_PREFIX_MARKDOWN,
            lang=lang,
        )
        return gr.update(value=result_path, visible=True), gr.update(
            interactive=True, value=button_text
        )
    except ImportError as e:
        raise gr.Error(get_texts(lang).error_ghostscript) from e
    except Exception as e:
        raise gr.Error(str(e)) from e


def convert_pdf_to_word_with_error_handling(
    pdf_file: str,
    lang: str,
) -> tuple[str | None, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate]:
    try:
        service = WebConvertService(lang=lang)
        result = service.convert_pdf_to_word(pdf_file)
        return (
            result,
            _error_handler.reset_word_button(lang),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )
    except Exception as e:
        error_info = _error_handler.handle_conversion_error(e, lang)
        error_box_update, error_url_update, report_btn_visible, cancel_btn_visible, error_buttons_visible = (
            _error_handler.show_error_dialog(error_info, lang)
        )
        return (
            None,
            _error_handler.reset_word_button(lang),
            error_box_update,
            error_url_update,
            report_btn_visible,
            cancel_btn_visible,
            error_buttons_visible,
        )


def merge_wechat_pdfs(
    pdf_files: list[str] | None,
    url: str,
    lang: str,
) -> tuple[dict, dict]:
    return _wechat_handler.merge_pdfs(pdf_files, url, lang)


def show_error_dialog(
    error_info: ErrorInfo, lang: str
) -> tuple[GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate]:
    return _error_handler.show_error_dialog(error_info, lang)


def open_issue_url(issue_url: str) -> str:
    return _error_handler.open_issue_url(issue_url)


def hide_error_dialog() -> tuple[GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate]:
    return _error_handler.hide_error_dialog()
