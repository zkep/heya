from __future__ import annotations

from typing import Any

import gradio as gr

from heya.web.core.component import ComponentContext
from heya.web.services.handler import (
    convert_html_to_pdf_with_error_handling,
    convert_md_to_pdf_stream,
)
from heya.web.i18n import get_texts
from heya.web.components.settings_panel import SettingsPanel

__all__ = ["HtmlConverterComponent", "MarkdownConverterComponent"]


class HtmlConverterComponent:
    name = "html_converter"

    def __init__(self) -> None:
        self._settings_panel: SettingsPanel = SettingsPanel()
        self._input: gr.Textbox | None = None
        self._output: gr.File | None = None
        self._timeout: gr.Slider | None = None
        self._quality: gr.Radio | None = None
        self._convert_btn: gr.Button | None = None
        self._settings_accordion: gr.Accordion | None = None

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(
        self, ctx: ComponentContext
    ) -> tuple[gr.Textbox, gr.File, gr.Button, gr.Accordion, gr.Slider, gr.Radio]:
        texts = get_texts(ctx.lang)
        url_input = gr.Textbox(
            label=texts.url_label,
            placeholder=texts.url_placeholder,
            lines=1,
        )
        settings_accordion, timeout, quality_radio = self._settings_panel.render(ctx)
        with gr.Row():
            convert_btn = gr.Button(
                texts.convert_btn,
                variant="primary",
                size="lg",
            )
        output = gr.File(
            label=f"📥 {texts.pdf_file_label}",
            visible=True,
        )
        self._input = url_input
        self._output = output
        self._timeout = timeout
        self._quality = quality_radio
        self._convert_btn = convert_btn
        self._settings_accordion = settings_accordion
        return (
            url_input,
            output,
            convert_btn,
            settings_accordion,
            timeout,
            quality_radio,
        )

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
        assert self._convert_btn is not None
        assert self._input is not None
        assert self._output is not None
        assert self._timeout is not None
        assert self._quality is not None

        self._convert_btn.click(
            convert_html_to_pdf_with_error_handling,
            inputs=[self._input, self._timeout, self._quality, lang_state],
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


class MarkdownConverterComponent:
    name = "markdown_converter"

    def __init__(self) -> None:
        self._settings_panel: SettingsPanel = SettingsPanel()
        self._input: gr.File | None = None
        self._output: gr.File | None = None
        self._merge_btn: gr.Button | None = None
        self._merged_output: gr.File | None = None
        self._timeout: gr.Slider | None = None
        self._quality: gr.Radio | None = None
        self._convert_btn: gr.Button | None = None
        self._settings_accordion: gr.Accordion | None = None

    def get_i18n_keys(self) -> dict[str, dict[str, str]]:
        return {}

    def render(
        self, ctx: ComponentContext
    ) -> tuple[
        gr.File,
        gr.File,
        gr.Button,
        gr.File,
        gr.Button,
        gr.Accordion,
        gr.Slider,
        gr.Radio,
    ]:
        texts = get_texts(ctx.lang)
        with gr.Row():
            md_input = gr.File(
                label=texts.md_file_label,
                file_types=[".md"],
                file_count="multiple",
            )
        settings_accordion, timeout, quality_radio = self._settings_panel.render(ctx)
        with gr.Row():
            convert_btn = gr.Button(
                texts.convert_btn,
                variant="primary",
                size="lg",
            )
        output = gr.File(
            label=f"📥 {texts.pdf_file_label}",
            file_count="multiple",
            visible=True,
            interactive=False,
        )
        with gr.Row():
            merge_btn = gr.Button(
                value=texts.merge_btn,
                variant="primary",
                visible=False,
            )
        merged_output = gr.File(
            label=f"📥 {texts.merged_pdf_label}",
            visible=False,
        )
        self._input = md_input
        self._output = output
        self._merge_btn = merge_btn
        self._merged_output = merged_output
        self._timeout = timeout
        self._quality = quality_radio
        self._convert_btn = convert_btn
        self._settings_accordion = settings_accordion
        return (
            md_input,
            output,
            convert_btn,
            merged_output,
            merge_btn,
            settings_accordion,
            timeout,
            quality_radio,
        )

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
        from heya.web.services.handler import merge_md_pdfs

        assert self._convert_btn is not None
        assert self._input is not None
        assert self._output is not None
        assert self._timeout is not None
        assert self._quality is not None
        assert self._merge_btn is not None
        assert self._merged_output is not None

        self._convert_btn.click(
            convert_md_to_pdf_stream,
            inputs=[self._input, self._timeout, self._quality, lang_state],
            outputs=[self._output, self._convert_btn, self._merge_btn],
            show_progress="full",
        )

        self._merge_btn.click(
            merge_md_pdfs,
            inputs=[self._output, self._input, lang_state],
            outputs=[self._merged_output, self._merge_btn],
            show_progress="full",
        )
