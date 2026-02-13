from __future__ import annotations

import os
from typing import TYPE_CHECKING, cast

import gradio as gr

from heya.web.components.converter import (
    HtmlConverterComponent,
    MarkdownConverterComponent,
)
from heya.web.components.pdf_to_word import PdfToWordComponent
from heya.web.components.tips import TipsComponent
from heya.web.components.wechat import WechatConverterComponent
from heya.web.core.component import ComponentContext
from heya.web.core.registry import ComponentRegistry
from heya.web.handler import hide_error_dialog, open_issue_url
from heya.web.i18n import LANGUAGE_OPTIONS, get_texts, UITexts

if TYPE_CHECKING:
    pass

_CSS_FILE_PATH = os.path.join(os.path.dirname(__file__), "styles.css")


def _load_css() -> str:
    with open(_CSS_FILE_PATH, encoding="utf-8") as f:
        return f.read()


def _create_quality_choices(texts: UITexts) -> list[tuple[str, int]]:
    return [
        (texts.quality_high, 0),
        (texts.quality_medium, 1),
        (texts.quality_low, 2),
    ]


def _create_settings_update(texts: UITexts) -> dict:
    return gr.update(label=f"⚙️ {texts.settings_label}")


def _create_quality_update(texts: UITexts) -> dict:
    return gr.update(
        label=texts.compression_level,
        info=texts.compression_info,
        choices=_create_quality_choices(texts),
    )


def _create_timeout_update(texts: UITexts) -> dict:
    return gr.update(label=texts.timeout_label)


def create_app() -> gr.Blocks:
    texts = get_texts("zh")

    registry = ComponentRegistry()
    html_converter = HtmlConverterComponent()
    md_converter = MarkdownConverterComponent()
    wechat_converter = WechatConverterComponent()
    pdf_to_word_converter = PdfToWordComponent()
    tips = TipsComponent()

    registry.register(html_converter)
    registry.register(md_converter)
    registry.register(wechat_converter)
    registry.register(pdf_to_word_converter)
    registry.register(tips)

    with gr.Blocks(
        title=texts.title,
        delete_cache=(60, 3600),
    ) as demo:
        lang_state = gr.State(value="zh")
        ctx = ComponentContext(lang="zh")

        with gr.Row():
            with gr.Column(scale=4):
                title_md = gr.Markdown(f"# 📄 {texts.title}")
                subtitle_md = gr.Markdown(texts.subtitle)
            with gr.Column(scale=1, min_width=150):
                with gr.Row():
                    gr.HTML(
                        value='<a href="https://github.com/zkep/heya" target="_blank" style="text-decoration: none; display: flex; align-items: center; justify-content: center; width: 48px; height: 48px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>',
                        elem_classes=["github-link"],
                    )
                    lang_dropdown = gr.Dropdown(
                        choices=LANGUAGE_OPTIONS,
                        value="zh",
                        interactive=True,
                        elem_classes=["lang-dropdown"],
                        show_label=False,
                        min_width=50,
                    )

        tips_md = tips.render(ctx)

        error_box = gr.HTML(visible=False)
        error_url = gr.Textbox(visible=False)
        with gr.Row(visible=False) as error_buttons_row:
            report_btn = gr.Button(texts.error_report_btn, variant="primary")
            cancel_btn = gr.Button(texts.error_cancel_btn)

        with gr.Tabs():
            with gr.TabItem(texts.wechat_tab, interactive=True) as wechat_tab:
                (
                    wechat_url_input,
                    wechat_output,
                    wechat_convert_btn,
                    wechat_merged_output,
                    wechat_merge_btn,
                    wechat_settings,
                    wechat_timeout,
                    wechat_quality,
                ) = wechat_converter.render(ctx)
                wechat_converter.setup_handler(
                    lang_state, error_box, error_url, report_btn, cancel_btn, error_buttons_row
                )

            with gr.TabItem(texts.html_tab, interactive=True) as html_tab:
                (
                    url_input,
                    html_output,
                    html_convert_btn,
                    html_settings,
                    html_timeout,
                    html_quality,
                ) = html_converter.render(ctx)
                html_converter.setup_handler(
                    lang_state, error_box, error_url, report_btn, cancel_btn, error_buttons_row
                )

            with gr.TabItem(texts.md_tab, interactive=True) as md_tab:
                (
                    md_input,
                    md_output,
                    md_convert_btn,
                    md_merged_output,
                    md_merge_btn,
                    md_settings,
                    md_timeout,
                    md_quality,
                ) = md_converter.render(ctx)
                md_converter.setup_handler(
                    lang_state, error_box, error_url, report_btn, cancel_btn, error_buttons_row
                )

            with gr.TabItem(texts.pdf_to_word_tab, interactive=True) as pdf_to_word_tab:
                pdf_input, pdf_to_word_convert_btn, pdf_to_word_output = (
                    pdf_to_word_converter.render(ctx)
                )
                pdf_to_word_converter.setup_handler(
                    lang_state, error_box, error_url, report_btn, cancel_btn, error_buttons_row
                )

        def update_language(lang: str):
            texts = get_texts(lang)
            return [
                gr.update(value=lang),
                gr.update(value=f"# 📄 {texts.title}"),
                gr.update(value=texts.subtitle),
                gr.update(label=texts.url_label, placeholder=texts.url_placeholder),
                gr.update(label=texts.md_file_label),
                gr.update(
                    label=texts.wechat_url_label,
                    placeholder=texts.wechat_url_placeholder,
                ),
                gr.update(value=texts.merge_btn),
                gr.update(label=texts.merged_pdf_label),
                gr.update(
                    value=f"{texts.tips_title}\n- {texts.tips_html}\n- {texts.tips_md}\n- {texts.tips_wechat}\n- {texts.tips_pdf_to_word}\n"
                ),
                gr.update(label=texts.wechat_tab, interactive=True),
                gr.update(label=texts.html_tab, interactive=True),
                gr.update(label=texts.md_tab, interactive=True),
                gr.update(label=texts.pdf_to_word_tab, interactive=True),
                gr.update(value=texts.convert_btn),
                _create_settings_update(texts),
                gr.update(value=texts.convert_btn),
                _create_settings_update(texts),
                gr.update(value=texts.convert_btn),
                _create_settings_update(texts),
                gr.update(value=texts.merge_btn),
                gr.update(label=texts.merged_pdf_label),
                gr.update(label=f"📥 {texts.pdf_file_label}"),
                gr.update(label=f"📥 {texts.pdf_file_label}"),
                gr.update(label=f"📥 {texts.wechat_output_label}"),
                gr.update(label=f"📥 {texts.word_output_label}"),
                gr.update(value=texts.convert_word_btn),
                gr.update(label=f"📥 {texts.pdf_file_label}"),
                _create_timeout_update(texts),
                _create_quality_update(texts),
                _create_timeout_update(texts),
                _create_quality_update(texts),
                _create_timeout_update(texts),
                _create_quality_update(texts),
                gr.update(value=texts.error_report_btn),
                gr.update(value=texts.error_cancel_btn),
            ]

        lang_dropdown.change(
            update_language,
            inputs=lang_dropdown,
            outputs=[
                lang_state,
                title_md,
                subtitle_md,
                url_input,
                md_input,
                wechat_url_input,
                wechat_merge_btn,
                wechat_merged_output,
                tips_md,
                wechat_tab,
                html_tab,
                md_tab,
                pdf_to_word_tab,
                wechat_convert_btn,
                wechat_settings,
                html_convert_btn,
                html_settings,
                md_convert_btn,
                md_settings,
                md_merge_btn,
                md_merged_output,
                html_output,
                md_output,
                wechat_output,
                pdf_input,
                pdf_to_word_convert_btn,
                pdf_to_word_output,
                wechat_timeout,
                wechat_quality,
                html_timeout,
                html_quality,
                md_timeout,
                md_quality,
                report_btn,
                cancel_btn,
            ],
        )

        cancel_btn.click(
            hide_error_dialog,
            outputs=[error_box, error_url, report_btn, cancel_btn, error_buttons_row],
        )

        report_btn.click(
            open_issue_url,
            inputs=[error_url],
            outputs=[],
            js="(url) => { window.open(url, '_blank'); }",
        )

    return cast(gr.Blocks, demo)


def run_server(host: str = "127.0.0.1", port: int = 7860, share: bool = False):
    demo = create_app()
    demo.launch(server_name=host, server_port=port, share=share, css=_load_css())
