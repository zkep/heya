from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QObject, Signal

from heya.core.logging.logging import ErrorInfo, get_error_info
from heya.app.i18n import get_texts

__all__ = ["ErrorHandler"]


class ErrorHandler(QObject):
    error_occurred = Signal(str, str)
    error_cleared = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def handle_conversion_error(self, e: Exception, lang: str) -> ErrorInfo:
        return get_error_info(e)

    def show_error_dialog(
        self,
        error_info: ErrorInfo,
        lang: str,
        on_report: Callable[[str], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> tuple[str, str, Callable[[], None], Callable[[], None]]:
        texts = get_texts(lang)

        error_message = self._format_error_message(error_info, texts.error_title or "Error")

        def report_callback() -> None:
            if on_report:
                on_report(error_info.issue_url)

        def cancel_callback() -> None:
            if on_cancel:
                on_cancel()

        return error_message, error_info.issue_url, report_callback, cancel_callback

    def _format_error_message(self, error_info: ErrorInfo, error_title: str) -> str:
        return (
            f"⚠️ {error_title}\n\n"
            f"Type: {error_info.error_type}\n"
            f"Message: {error_info.error_message}\n"
            f"Platform: {error_info.platform} | Python {error_info.python_version.split()[0]}"
        )

    def open_issue_url(self, issue_url: str) -> None:
        import webbrowser

        webbrowser.open(issue_url)
