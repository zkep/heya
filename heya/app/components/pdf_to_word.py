from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import QThread, Signal

from heya.app.core.component import Component, ComponentContext
from heya.app.i18n import get_texts
from heya.app.services.service import AppConvertService
from heya.app.handlers.error_handler import ErrorHandler

__all__ = ["PdfToWordComponent"]


class PdfToWordConversionThread(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, service: AppConvertService, pdf_file: str) -> None:
        super().__init__()
        self._service = service
        self._pdf_file = pdf_file

    def run(self) -> None:
        try:
            result = self._service.convert_pdf_to_word(self._pdf_file)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class PdfToWordComponent(Component):
    name = "pdf_to_word_converter"

    def __init__(self) -> None:
        self._pdf_file_path: str | None = None
        self._convert_btn: QPushButton | None = None
        self._output_label: QLabel | None = None
        self._progress_bar: QProgressBar | None = None
        self._service = AppConvertService()
        self._error_handler = ErrorHandler()
        self._current_lang = "zh"
        self._thread: PdfToWordConversionThread | None = None

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext, parent: QWidget | None = None) -> QWidget:
        self._current_lang = ctx.lang
        texts = get_texts(ctx.lang)

        widget = QWidget(parent)
        layout = QVBoxLayout()

        upload_layout = QHBoxLayout()
        upload_btn = QPushButton(f"📁 {texts.pdf_file_label}")
        upload_btn.setMinimumHeight(40)
        upload_btn.clicked.connect(self._on_upload_pdf)

        file_label = QLabel("No file selected")
        file_label.setWordWrap(True)
        file_label.setStyleSheet("QLabel { padding: 10px; background-color: #f5f5f5; border-radius: 5px; color: #333333; }")

        upload_layout.addWidget(upload_btn)
        upload_layout.addWidget(file_label)

        btn_layout = QHBoxLayout()
        convert_btn = QPushButton(texts.convert_word_btn)
        convert_btn.setMinimumHeight(40)
        convert_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        convert_btn.setEnabled(False)

        btn_layout.addWidget(convert_btn)

        progress_bar = QProgressBar()
        progress_bar.setVisible(False)

        output_label = QLabel(f"📥 {texts.word_output_label}")
        output_label.setStyleSheet("QLabel { padding: 10px; background-color: #e8f5e9; border-radius: 5px; color: #1b5e20; }")
        output_label.setVisible(False)

        layout.addLayout(upload_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(progress_bar)
        layout.addWidget(output_label)
        layout.addStretch()

        widget.setLayout(layout)

        self._convert_btn = convert_btn
        self._output_label = output_label
        self._progress_bar = progress_bar
        self._file_label = file_label

        return widget

    def setup_handlers(self) -> None:
        if self._convert_btn:
            self._convert_btn.clicked.connect(self._on_convert)

    def _on_upload_pdf(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )

        if file_path:
            self._pdf_file_path = file_path
            if self._file_label:
                self._file_label.setText(file_path)
            if self._convert_btn:
                self._convert_btn.setEnabled(True)

    def _on_convert(self) -> None:
        if not self._pdf_file_path or not self._convert_btn:
            return

        self._convert_btn.setEnabled(False)
        if self._progress_bar:
            self._progress_bar.setVisible(True)
            self._progress_bar.setRange(0, 0)

        thread = PdfToWordConversionThread(self._service, self._pdf_file_path)
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
            self._output_label.setText(f"📥 {get_texts(self._current_lang).word_output_label}: {result_path}")
            self._output_label.setVisible(True)
        self._thread = None

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
        if self._convert_btn:
            self._convert_btn.setText(texts.convert_word_btn)
        if self._output_label:
            self._output_label.setText(f"📥 {texts.word_output_label}")
