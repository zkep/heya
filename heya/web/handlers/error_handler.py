from __future__ import annotations


import gradio as gr

from heya.shared import ErrorInfo, get_error_info
from heya.web.i18n import get_texts

__all__ = ["ErrorHandler", "GradioUpdate"]

GradioUpdate = dict[str, object]

_ERROR_BOX_BACKGROUND = "#fee2e2"
_ERROR_BOX_BORDER = "#fecaca"
_ERROR_TITLE_COLOR = "#991b1b"
_ERROR_TEXT_COLOR = "#7f1d1d"
_ERROR_BOX_PADDING = "16px"
_ERROR_BOX_BORDER_RADIUS = "8px"
_ERROR_BOX_MARGIN = "16px 0"


class ErrorHandler:
    def handle_conversion_error(self, e: Exception, lang: str) -> ErrorInfo:
        return get_error_info(e)

    def reset_convert_button(self, lang: str) -> GradioUpdate:
        return gr.update(interactive=True, value=get_texts(lang).convert_btn)

    def reset_word_button(self, lang: str) -> GradioUpdate:
        return gr.update(interactive=True, value=get_texts(lang).convert_word_btn)

    def show_error_dialog(
        self, error_info: ErrorInfo, lang: str
    ) -> tuple[GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate]:
        texts = get_texts(lang)

        error_html = self._format_error_html(error_info, texts.error_title or "Error")

        return (
            gr.update(value=error_html, visible=True),
            gr.update(value=error_info.issue_url, visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
        )

    def _format_error_html(self, error_info: ErrorInfo, error_title: str) -> str:
        return f"""
        <div style="padding: {_ERROR_BOX_PADDING}; background-color: {_ERROR_BOX_BACKGROUND}; border: 1px solid {_ERROR_BOX_BORDER}; border-radius: {_ERROR_BOX_BORDER_RADIUS}; margin: {_ERROR_BOX_MARGIN};">
            <h3 style="color: {_ERROR_TITLE_COLOR}; margin-top: 0;">⚠️ {error_title}</h3>
            <p style="color: {_ERROR_TEXT_COLOR}; margin-bottom: 8px;"><strong>Type:</strong> {error_info.error_type}</p>
            <p style="color: {_ERROR_TEXT_COLOR}; margin-bottom: 8px;"><strong>Message:</strong> {error_info.error_message}</p>
            <p style="color: {_ERROR_TEXT_COLOR}; margin-bottom: 0;"><strong>Platform:</strong> {error_info.platform} | Python {error_info.python_version.split()[0]}</p>
        </div>
        """

    def open_issue_url(self, issue_url: str) -> str:
        return f"window.open('{issue_url}', '_blank');"

    def hide_error_dialog(self) -> tuple[GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate, GradioUpdate]:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )
