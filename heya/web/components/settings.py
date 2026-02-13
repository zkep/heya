from __future__ import annotations

from typing import Any

import gradio as gr

from heya.web.core.component import ComponentContext
from heya.web.i18n import get_texts
from heya.web.components.settings_panel import SettingsPanel

__all__ = ["SettingsComponent"]


class SettingsComponent:
    name = "settings"

    def __init__(self) -> None:
        self._settings_panel = SettingsPanel(open_by_default=True)

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext) -> tuple[gr.Slider, gr.Radio, gr.Button]:
        texts = get_texts(ctx.lang)
        settings_accordion, timeout, quality_radio = self._settings_panel.render(ctx)
        with gr.Row():
            convert_btn = gr.Button(
                texts.convert_btn,
                variant="primary",
                size="lg",
            )
        self._timeout = timeout
        self._quality = quality_radio
        self._btn = convert_btn
        return timeout, quality_radio, convert_btn

    def register_handlers(self, app: Any) -> None:
        pass

    @property
    def timeout(self) -> gr.Slider:
        return self._timeout

    @property
    def quality(self) -> gr.Radio:
        return self._quality

    @property
    def convert_btn(self) -> gr.Button:
        return self._btn
