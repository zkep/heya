from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QComboBox,
    QPushButton,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from heya.app.core.component import ComponentContext
from heya.app.core.registry import ComponentRegistry
from heya.app.i18n import get_texts, LANGUAGE_OPTIONS
from heya.app.components.converter import HtmlConverterComponent
from heya.app.components.markdown_converter import MarkdownConverterComponent
from heya.app.components.wechat import WechatConverterComponent
from heya.app.components.pdf_to_word import PdfToWordComponent
from heya.app.components.tips import TipsComponent

__all__ = ["MainWindow"]


class ErrorDialog(QDialog):
    def __init__(self, error_message: str, issue_url: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        error_label = QLabel(error_message)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("QLabel { padding: 10px; background-color: #fee2e2; border: 1px solid #fecaca; border-radius: 5px; color: #b91c1c; }")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Help)
        buttons.accepted.connect(self.accept)
        buttons.helpRequested.connect(self._on_report)

        layout.addWidget(error_label)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self._issue_url = issue_url

    def _on_report(self) -> None:
        import webbrowser
        webbrowser.open(self._issue_url)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._current_lang = "zh"
        self._registry = ComponentRegistry()
        self._setup_components()
        self._setup_ui()

    def _setup_components(self) -> None:
        wechat_converter = WechatConverterComponent()
        html_converter = HtmlConverterComponent()
        md_converter = MarkdownConverterComponent()
        pdf_to_word_converter = PdfToWordComponent()
        tips = TipsComponent()

        self._registry.register(wechat_converter)
        self._registry.register(html_converter)
        self._registry.register(md_converter)
        self._registry.register(pdf_to_word_converter)
        self._registry.register(tips)

    def _setup_ui(self) -> None:
        texts = get_texts(self._current_lang)

        self.setWindowTitle(texts.title)
        self.setMinimumSize(900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_label = QLabel(f"📄 {texts.title}")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        subtitle_label = QLabel(texts.subtitle)
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        right_layout = QHBoxLayout()
        right_layout.addStretch()

        github_btn = QPushButton()
        github_btn.setText("GitHub")
        github_btn.setMaximumWidth(80)
        github_btn.clicked.connect(self._open_github)

        lang_combo = QComboBox()
        for label, lang_code in LANGUAGE_OPTIONS:
            lang_combo.addItem(label, lang_code)
        lang_combo.setCurrentIndex(0)
        lang_combo.currentIndexChanged.connect(self._on_language_changed)

        right_layout.addWidget(github_btn)
        right_layout.addWidget(lang_combo)

        header_layout.addLayout(title_layout, stretch=4)
        header_layout.addLayout(right_layout, stretch=1)

        ctx = ComponentContext(lang=self._current_lang)

        tips_component = self._registry.get("tips")
        tips_widget = tips_component.render(ctx, central_widget) if tips_component else None

        tab_widget = QTabWidget()

        html_component = self._registry.get("html_converter")
        if html_component:
            html_tab = html_component.render(ctx, tab_widget)
            html_component.setup_handlers()
            tab_widget.addTab(html_tab, texts.html_tab)

        md_component = self._registry.get("markdown_converter")
        if md_component:
            md_tab = md_component.render(ctx, tab_widget)
            md_component.setup_handlers()
            tab_widget.addTab(md_tab, texts.md_tab)

        wechat_component = self._registry.get("wechat_converter")
        if wechat_component:
            wechat_tab = wechat_component.render(ctx, tab_widget)
            wechat_component.setup_handlers()
            tab_widget.addTab(wechat_tab, texts.wechat_tab)

        pdf_to_word_component = self._registry.get("pdf_to_word_converter")
        if pdf_to_word_component:
            pdf_tab = pdf_to_word_component.render(ctx, tab_widget)
            pdf_to_word_component.setup_handlers()
            tab_widget.addTab(pdf_tab, texts.pdf_to_word_tab)

        main_layout.addLayout(header_layout)
        if tips_widget:
            main_layout.addWidget(tips_widget)
        main_layout.addWidget(tab_widget)

        central_widget.setLayout(main_layout)

        self._lang_combo = lang_combo
        self._tab_widget = tab_widget

    def _on_language_changed(self, index: int) -> None:
        lang_code = self._lang_combo.itemData(index)
        self._current_lang = lang_code
        texts = get_texts(lang_code)

        self.setWindowTitle(texts.title)

        self._update_ui_texts(texts)

    def _update_ui_texts(self, texts) -> None:
        html_component = self._registry.get("html_converter")
        if html_component and hasattr(html_component, "update_language"):
            html_component.update_language(self._current_lang)

        md_component = self._registry.get("markdown_converter")
        if md_component and hasattr(md_component, "update_language"):
            md_component.update_language(self._current_lang)

        wechat_component = self._registry.get("wechat_converter")
        if wechat_component and hasattr(wechat_component, "update_language"):
            wechat_component.update_language(self._current_lang)

        pdf_to_word_component = self._registry.get("pdf_to_word_converter")
        if pdf_to_word_component and hasattr(pdf_to_word_component, "update_language"):
            pdf_to_word_component.update_language(self._current_lang)

        tips_component = self._registry.get("tips")
        if tips_component and hasattr(tips_component, "update_text"):
            tips_component.update_text(self._current_lang)

        if self._tab_widget:
            self._tab_widget.setTabText(0, texts.html_tab)
            self._tab_widget.setTabText(1, texts.md_tab)
            self._tab_widget.setTabText(2, texts.wechat_tab)
            self._tab_widget.setTabText(3, texts.pdf_to_word_tab)

    def _open_github(self) -> None:
        import webbrowser
        webbrowser.open("https://github.com/zkep/heya")

    def show_error(self, error_message: str, issue_url: str) -> None:
        dialog = ErrorDialog(error_message, issue_url, self)
        dialog.exec()
