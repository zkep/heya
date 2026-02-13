from __future__ import annotations

from typing import Any

import gradio as gr

from heya.web.core.component import ComponentContext
from heya.web.i18n import get_texts

__all__ = ["TipsComponent"]


class TipsComponent:
    name = "tips"

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext) -> gr.Markdown:
        texts = get_texts(ctx.lang)
        return gr.Markdown(
            f"{texts.tips_title}\n- {texts.tips_html}\n- {texts.tips_md}\n- {texts.tips_compress}",
        )

    def register_handlers(self, app: Any) -> None:
        pass
