from __future__ import annotations

import asyncio
import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QCursor

from heya.app.core.component import Component, ComponentContext
from heya.app.i18n import get_texts
from heya.app.components.settings_panel import SettingsPanel
from heya.app.services.service import AppConvertService
from heya.app.handlers.error_handler import ErrorHandler

__all__ = ["MarkdownConverterComponent"]


class MarkdownConversionThread(QThread):
    finished = Signal(list)
    progress = Signal(int, int, str)
    error = Signal(str)

    def __init__(self, service: AppConvertService, md_files: list[str], timeout: float, quality: int) -> None:
        super().__init__()
        self._service = service
        self._md_files = md_files
        self._timeout = timeout
        self._quality = quality

    def run(self) -> None:
        try:
            completed_files = []
            for i, md_file in enumerate(self._md_files):
                self.progress.emit(i + 1, len(self._md_files), md_file)
                result = asyncio.run(self._service.convert_markdown(md_file, self._timeout, self._quality))
                completed_files.append(result)
            self.finished.emit(completed_files)
        except Exception as e:
            self.error.emit(str(e))


class MarkdownConverterComponent(Component):
    name = "markdown_converter"

    def __init__(self) -> None:
        self._settings_panel = SettingsPanel()
        self._file_list: QListWidget | None = None
        self._convert_btn: QPushButton | None = None
        self._merge_btn: QPushButton | None = None
        self._output_label: QLabel | None = None
        self._progress_bar: QProgressBar | None = None
        self._service = AppConvertService()
        self._error_handler = ErrorHandler()
        self._current_lang = "zh"
        self._selected_files: list[str] = []
        self._converted_files: list[str] = []
        self._thread: MarkdownConversionThread | None = None
        self._output_widgets: list[tuple[QLabel, str]] = []

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext, parent: QWidget | None = None) -> QWidget:
        self._current_lang = ctx.lang
        texts = get_texts(ctx.lang)

        widget = QWidget(parent)
        layout = QVBoxLayout()

        file_list = QListWidget()
        file_list.setSelectionMode(QListWidget.SingleSelection)

        upload_btn = QPushButton("📁 Upload Markdown Files")
        upload_btn.clicked.connect(self._on_upload_files)

        settings_widget = self._settings_panel.render(ctx, widget)

        btn_layout = QHBoxLayout()
        convert_btn = QPushButton(texts.convert_btn)
        convert_btn.setMinimumHeight(40)
        convert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        merge_btn = QPushButton(texts.merge_btn)
        merge_btn.setMinimumHeight(40)
        merge_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        merge_btn.setVisible(False)

        btn_layout.addWidget(convert_btn)
        btn_layout.addWidget(merge_btn)

        progress_bar = QProgressBar()
        progress_bar.setVisible(False)

        output_scroll = QScrollArea()
        output_scroll.setWidgetResizable(True)
        output_scroll.setVisible(False)
        output_container = QWidget()
        output_container_layout = QVBoxLayout()
        output_container_layout.setContentsMargins(0, 0, 0, 0)
        output_container.setLayout(output_container_layout)
        output_scroll.setWidget(output_container)

        self._output_scroll = output_scroll
        self._output_container = output_container
        self._output_container_layout = output_container_layout

        layout.addWidget(file_list)
        layout.addWidget(upload_btn)
        layout.addWidget(settings_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(progress_bar)
        layout.addWidget(output_scroll)
        layout.addStretch()

        widget.setLayout(layout)

        self._file_list = file_list
        self._convert_btn = convert_btn
        self._merge_btn = merge_btn
        self._output_label = QLabel()
        self._progress_bar = progress_bar

        return widget

    def setup_handlers(self) -> None:
        if self._convert_btn:
            self._convert_btn.clicked.connect(self._on_convert)
        if self._merge_btn:
            self._merge_btn.clicked.connect(self._on_merge)

    def _on_upload_files(self) -> None:
        if not self._file_list:
            return

        files, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Markdown Files",
            "",
            "Markdown Files (*.md);;All Files (*)"
        )

        if files:
            self._selected_files = files
            self._file_list.clear()
            for file_path in files:
                item = QListWidgetItem(file_path)
                self._file_list.addItem(item)

    def _on_convert(self) -> None:
        if not self._selected_files or not self._convert_btn:
            return

        timeout = self._settings_panel.timeout
        quality = self._settings_panel.quality

        self._convert_btn.setEnabled(False)
        if self._progress_bar:
            self._progress_bar.setVisible(True)
            self._progress_bar.setRange(0, len(self._selected_files))

        thread = MarkdownConversionThread(self._service, self._selected_files, timeout, quality)
        thread.progress.connect(self._on_conversion_progress)
        thread.finished.connect(self._on_conversion_finished)
        thread.error.connect(self._on_conversion_error)
        self._thread = thread
        thread.start()

    def _on_conversion_progress(self, current: int, total: int, filename: str) -> None:
        if self._progress_bar:
            self._progress_bar.setValue(current)

    def _on_conversion_finished(self, result_files: list[str]) -> None:
        self._converted_files = result_files
        if self._convert_btn:
            self._convert_btn.setEnabled(True)
        if self._progress_bar:
            self._progress_bar.setVisible(False)
        if self._merge_btn and len(result_files) > 1:
            self._merge_btn.setVisible(True)

        if hasattr(self, '_output_container_layout'):
            while self._output_container_layout.count():
                child = self._output_container_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self._output_widgets.clear()

            for pdf_path in result_files:
                pdf_label = QLabel(f"📄 {os.path.basename(pdf_path)}")
                pdf_label.setCursor(QCursor(Qt.PointingHandCursor))
                pdf_label.setStyleSheet(
                    "QLabel { padding: 10px; background-color: #e8f5e9; border-radius: 5px; color: #1b5e20; margin-bottom: 5px; }"
                    "QLabel:hover { background-color: #c8e6c9; text-decoration: underline; }"
                )

                def make_click_handler(path):
                    def handler(event):
                        self._save_pdf_file(path)
                    return handler

                pdf_label.mousePressEvent = make_click_handler(pdf_path)
                self._output_container_layout.addWidget(pdf_label)
                self._output_widgets.append((pdf_label, pdf_path))

            if hasattr(self, '_output_scroll'):
                self._output_scroll.setVisible(True)

        self._thread = None

    def _save_pdf_file(self, pdf_path: str) -> None:
        if os.path.exists(pdf_path):
            save_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save PDF",
                os.path.basename(pdf_path),
                "PDF Files (*.pdf)"
            )
            if save_path:
                import shutil
                shutil.copy2(pdf_path, save_path)
                QMessageBox.information(None, "Success", f"PDF saved to: {save_path}")

    def _on_conversion_error(self, error_msg: str) -> None:
        if self._convert_btn:
            self._convert_btn.setEnabled(True)
        if self._progress_bar:
            self._progress_bar.setVisible(False)
        QMessageBox.critical(None, "Error", error_msg)
        self._thread = None

    def _on_merge(self) -> None:
        QMessageBox.information(None, "Info", "Merge functionality - to be implemented")

    def update_language(self, lang: str) -> None:
        self._current_lang = lang
        texts = get_texts(lang)
        if self._convert_btn:
            self._convert_btn.setText(texts.convert_btn)
        if self._merge_btn:
            self._merge_btn.setText(texts.merge_btn)
        if self._output_label:
            self._output_label.setText(f"📥 {texts.pdf_file_label}")
