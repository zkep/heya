from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from heya.app.core.component import Component, ComponentContext
from heya.app.i18n import get_texts

__all__ = ["TipsComponent"]


class TipsComponent(Component):
    name = "tips"

    def __init__(self) -> None:
        self._label: QLabel | None = None

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext, parent: QWidget | None = None) -> QWidget:
        texts = get_texts(ctx.lang)

        widget = QWidget(parent)
        layout = QVBoxLayout()

        tips_text = (
            f"{texts.tips_title}\n"
            f"- {texts.tips_html}\n"
            f"- {texts.tips_md}\n"
            f"- {texts.tips_wechat}\n"
            f"- {texts.tips_pdf_to_word}"
        )

        label = QLabel(tips_text)
        label.setWordWrap(True)
        label.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; border-radius: 5px; color: #333333; }")

        layout.addWidget(label)
        widget.setLayout(layout)

        self._label = label
        return widget

    def setup_handlers(self) -> None:
        pass

    def update_text(self, lang: str) -> None:
        texts = get_texts(lang)
        tips_text = (
            f"{texts.tips_title}\n"
            f"- {texts.tips_html}\n"
            f"- {texts.tips_md}\n"
            f"- {texts.tips_wechat}\n"
            f"- {texts.tips_pdf_to_word}"
        )
        if self._label:
            self._label.setText(tips_text)
