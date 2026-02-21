from __future__ import annotations

from typing import Any

import gradio as gr

from heya.web.core.component import ComponentContext
from heya.web.i18n import get_texts

__all__ = ["PdfToWordComponent"]


class PdfToWordComponent:
    name = "pdf_to_word_converter"

    def __init__(self) -> None:
        self._input: gr.File | None = None
        self._output: gr.File | None = None
        self._convert_btn: gr.Button | None = None

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(self, ctx: ComponentContext) -> tuple[gr.File, gr.Button, gr.File]:
        texts = get_texts(ctx.lang)
        with gr.Row():
            pdf_input = gr.File(
                label=texts.pdf_file_label,
                file_types=[".pdf"],
                file_count="single",
            )
        with gr.Row():
            convert_btn = gr.Button(
                texts.convert_word_btn,
                variant="primary",
                size="lg",
            )
        output = gr.File(
            label=f"📥 {texts.word_output_label}",
            visible=True,
            interactive=False,
        )
        self._input = pdf_input
        self._output = output
        self._convert_btn = convert_btn
        return pdf_input, convert_btn, output

    def register_handlers(self, app: Any) -> None:
        pass

    def setup_handler(
        self,
        lang_state: gr.State,
        error_box: gr.HTML,
        error_url: gr.Textbox,
        report_btn: gr.Button,
        cancel_btn: gr.Button,
        error_buttons_row: gr.Row,
    ) -> None:
        from heya.web.services.handler import convert_pdf_to_word_with_error_handling

        assert self._convert_btn is not None
        assert self._input is not None
        assert self._output is not None

        self._convert_btn.click(
            convert_pdf_to_word_with_error_handling,
            inputs=[self._input, lang_state],
            outputs=[
                self._output,
                self._convert_btn,
                error_box,
                error_url,
                report_btn,
                cancel_btn,
                error_buttons_row,
            ],
            show_progress="full",
        )
