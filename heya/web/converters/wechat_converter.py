from __future__ import annotations

import os
from collections.abc import Callable, Generator
from typing import Any

import gradio as gr

from heya.application import convert_wechat, create_wechat_converter
from heya.application.wechat_converter import WechatConvertResult
from heya.infrastructure.wechat import WechatParser
from heya.shared.temp import create_output_path
from heya.web.converters.base import BaseWechatConverter

__all__ = ["WechatConverter"]


class WechatConverter(BaseWechatConverter):
    def __init__(
        self,
        convert_fn: Callable[..., WechatConvertResult] | None = None,
    ) -> None:
        super().__init__(convert_fn or convert_wechat)
        self._typed_convert_fn: Callable[..., WechatConvertResult] = (
            convert_fn if convert_fn is not None else convert_wechat
        )

    def convert(
        self,
        source: str,
        target: str,
        timeout: float = 3.0,
        quality: int = 0,
        **kwargs: Any,
    ) -> WechatConvertResult:
        return self._typed_convert_fn(
            url=source,
            output_dir=target,
            timeout=timeout,
            compress=True,
            quality=quality,
        )

    def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, dict[str, Any], dict[str, Any]], None, None]:
        if len(sources) != 1:
            raise RuntimeError("WeChat converter expects exactly one URL")

        url = sources[0]
        timeout = kwargs.get("timeout", 3.0)
        quality = kwargs.get("quality", 0)

        if not self.is_article_list(url):
            yield None, gr.update(interactive=False), gr.update(visible=False)
            result = self.convert(url, "", timeout, quality)
            pdf_files = self._extract_pdf_files(result)
            yield pdf_files, gr.update(interactive=True), gr.update(visible=False)
            return

        output_dir = create_output_path()
        os.makedirs(output_dir, exist_ok=True)

        converter = create_wechat_converter(timeout, compress=True)

        articles = WechatParser.parse_article_list(url)
        if not articles:
            raise RuntimeError("No articles found in the provided WeChat URL")

        total = len(articles)
        completed_files: list[str] = []
        yield None, gr.update(interactive=False), gr.update(visible=False)

        for idx, article in enumerate(articles):
            safe_title = converter._sanitize_filename(article.title)
            output_path = os.path.join(
                output_dir, f"{article.index:02d}_{safe_title}.pdf"
            )

            progress_update = (
                gr.update(interactive=False, value=f"{idx + 1}/{total} {article.title}")
                if progress_update_fn
                else gr.update(interactive=False)
            )
            yield (
                completed_files.copy(),
                progress_update,
                gr.update(visible=False),
            )

            convert_result = converter._html_converter.convert(
                source=article.url,
                target=output_path,
                compress=True,
                quality=quality,
            )
            if convert_result.success and convert_result.output_path:
                completed_files.append(convert_result.output_path)

        if not completed_files:
            raise RuntimeError("Failed to convert WeChat articles")

        show_merge_button = len(completed_files) > 1
        yield (
            completed_files.copy(),
            gr.update(interactive=True),
            gr.update(visible=show_merge_button),
        )

    def is_article_list(self, url: str) -> bool:
        return WechatParser.is_article_list(url)

    def _extract_pdf_files(self, result: WechatConvertResult) -> list[str]:
        pdf_files: list[str] = []
        for article in result.articles:
            output = article.get("output")
            if isinstance(output, str):
                pdf_files.append(output)
        return pdf_files
