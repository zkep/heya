from __future__ import annotations

import asyncio
import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QCursor

from heya.app.core.component import Component, ComponentContext
from heya.app.i18n import get_texts
from heya.app.components.settings_panel import SettingsPanel
from heya.app.services.service import AppConvertService
from heya.app.handlers.error_handler import ErrorHandler

__all__ = ["HtmlConverterComponent"]


class ConversionThread(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, service: AppConvertService, url: str, timeout: float, quality: int) -> None:
        super().__init__()
        self._service = service
        self._url = url
        self._timeout = timeout
        self._quality = quality

    def run(self) -> None:
        try:
            result = asyncio.run(self._service.convert_html(self._url, self._timeout, self._quality))
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class HtmlConverterComponent(Component):
    name = "html_converter"

    def __init__(self) -> None:
        self._settings_panel = SettingsPanel()
        self._url_input: QLineEdit | None = None
        self._convert_btn: QPushButton | None = None
        self._output_label: QLabel | None = None
        self._progress_bar: QProgressBar | None = None
        self._service = AppConvertService()
        self._error_handler = ErrorHandler()
        self._current_lang = "zh"
        self._thread: ConversionThread | None = None
        self._current_pdf_path: str | None = None

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext, parent: QWidget | None = None) -> QWidget:
        self._current_lang = ctx.lang
        texts = get_texts(ctx.lang)

        widget = QWidget(parent)
        layout = QVBoxLayout()

        url_layout = QHBoxLayout()
        url_label = QLabel(texts.url_label)
        url_label.setMinimumWidth(80)
        url_input = QLineEdit()
        url_input.setPlaceholderText(texts.url_placeholder)

        url_layout.addWidget(url_label)
        url_layout.addWidget(url_input)

        settings_widget = self._settings_panel.render(ctx, widget)

        btn_layout = QHBoxLayout()
        convert_btn = QPushButton(texts.convert_btn)
        convert_btn.setMinimumHeight(40)
        convert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        btn_layout.addWidget(convert_btn)

        progress_bar = QProgressBar()
        progress_bar.setVisible(False)

        output_label = QLabel(f"📥 {texts.pdf_file_label}")
        output_label.setStyleSheet("QLabel { padding: 10px; background-color: #e8f5e9; border-radius: 5px; color: #1b5e20; }")
        output_label.setVisible(False)

        layout.addLayout(url_layout)
        layout.addWidget(settings_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(progress_bar)
        layout.addWidget(output_label)
        layout.addStretch()

        widget.setLayout(layout)

        self._url_input = url_input
        self._convert_btn = convert_btn
        self._output_label = output_label
        self._progress_bar = progress_bar

        return widget

    def setup_handlers(self) -> None:
        if self._convert_btn:
            self._convert_btn.clicked.connect(self._on_convert)

    def _on_convert(self) -> None:
        if not self._url_input or not self._convert_btn:
            return

        url = self._url_input.text().strip()
        if not url:
            QMessageBox.warning(None, "Error", get_texts(self._current_lang).error_no_url)
            return

        timeout = self._settings_panel.timeout
        quality = self._settings_panel.quality

        self._convert_btn.setEnabled(False)
        if self._progress_bar:
            self._progress_bar.setVisible(True)
            self._progress_bar.setRange(0, 0)

        thread = ConversionThread(self._service, url, timeout, quality)
        thread.finished.connect(self._on_conversion_finished)
        thread.error.connect(self._on_conversion_error)
        self._thread = thread
        thread.start()

    def _on_conversion_finished(self, result_path: str) -> None:
        if self._convert_btn:
            self._convert_btn.setEnabled(True)
        if self._progress_bar:
            self._progress_bar.setVisible(False)
        if self._output_label:
            self._current_pdf_path = result_path
            filename = os.path.basename(result_path)
            self._output_label.setText(f"📥 {get_texts(self._current_lang).pdf_file_label}: {filename}")
            self._output_label.setCursor(QCursor(Qt.PointingHandCursor))
            self._output_label.mousePressEvent = self._on_output_clicked
            self._output_label.setStyleSheet(
                "QLabel { padding: 10px; background-color: #e8f5e9; border-radius: 5px; color: #1b5e20; }"
                "QLabel:hover { background-color: #c8e6c9; text-decoration: underline; }"
            )
            self._output_label.setVisible(True)
        self._thread = None

    def _on_output_clicked(self, event) -> None:
        if self._current_pdf_path and os.path.exists(self._current_pdf_path):
            from PySide6.QtWidgets import QFileDialog
            save_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save PDF",
                os.path.basename(self._current_pdf_path),
                "PDF Files (*.pdf)"
            )
            if save_path:
                import shutil
                shutil.copy2(self._current_pdf_path, save_path)
                QMessageBox.information(None, "Success", f"PDF saved to: {save_path}")

    def _on_conversion_error(self, error_msg: str) -> None:
        if self._convert_btn:
            self._convert_btn.setEnabled(True)
        if self._progress_bar:
            self._progress_bar.setVisible(False)
        QMessageBox.critical(None, "Error", error_msg)
        self._thread = None

    def update_language(self, lang: str) -> None:
        self._current_lang = lang
        texts = get_texts(lang)
        if self._url_input:
            self._url_input.setPlaceholderText(texts.url_placeholder)
        if self._convert_btn:
            self._convert_btn.setText(texts.convert_btn)
        if self._output_label:
            self._output_label.setText(f"📥 {texts.pdf_file_label}")
