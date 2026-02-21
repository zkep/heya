from __future__ import annotations

import os
from collections.abc import Callable, Generator
from typing import TYPE_CHECKING, Any

from heya.core.helpers import convert_wechat
from heya.core.wechat import create_wechat_converter, WechatConvertResult, WechatArticleConverter, WechatParser
from heya.core.temp import create_output_path
from heya.core.stream_converters.base import BaseWechatConverter

if TYPE_CHECKING:
    from heya.core.converters.converters import HtmlToPdfConverter

__all__ = ["WechatConverter"]


class WechatConverter(BaseWechatConverter):
    def __init__(
        self,
        convert_fn: Callable[..., WechatConvertResult] | None = None,
        html_converter: "HtmlToPdfConverter | None" = None,
    ) -> None:
        super().__init__(convert_fn)
        self._typed_convert_fn = convert_fn if convert_fn is not None else convert_wechat
        self._html_converter = html_converter

    async def convert(
        self,
        source: str,
        target: str,
        timeout: float = 3.0,
        quality: int = 0,
        **kwargs: Any,
    ) -> WechatConvertResult:
        return await self._typed_convert_fn(
            url=source,
            output_dir=target,
            timeout=timeout,
            compress=True,
            quality=quality,
        )

    async def convert_stream(
        self,
        sources: list[str],
        progress_update_fn: Callable[[int, int, str], None] | None = None,
        **kwargs: Any,
    ) -> Generator[tuple[list[str] | None, int, int, str | None], None, None]:
        if len(sources) != 1:
            raise RuntimeError("WeChat converter expects exactly one URL")

        url = sources[0]
        timeout = kwargs.get("timeout", 3.0)
        quality = kwargs.get("quality", 0)

        if not self.is_article_list(url):
            yield None, 0, 1, None
            output_dir = create_output_path()
            os.makedirs(output_dir, exist_ok=True)
            result = await self.convert(url, output_dir, timeout, quality)
            pdf_files = self._extract_pdf_files(result)
            yield pdf_files, len(pdf_files), 1, None
            return

        output_dir = create_output_path()
        os.makedirs(output_dir, exist_ok=True)

        if self._html_converter is not None:
            converter = self._html_converter
        else:
            converter = create_wechat_converter(timeout, compress=True)._html_converter

        articles = await WechatParser.parse_article_list(url)
        if not articles:
            raise RuntimeError("No articles found in provided WeChat URL")

        total = len(articles)
        completed_files: list[str] = []
        yield None, 0, total, None

        for idx, article in enumerate(articles):
            safe_title = WechatArticleConverter._sanitize_filename(article.title)
            output_path = os.path.join(
                output_dir, f"{article.index:02d}_{safe_title}.pdf"
            )

            if progress_update_fn:
                progress_update_fn(idx + 1, total, article.title)

            convert_result = await converter.convert(
                source=article.url,
                target=output_path,
                compress=True,
                quality=quality,
            )
            if convert_result.success and convert_result.output_path:
                completed_files.append(convert_result.output_path)
                yield (completed_files.copy(), idx + 1, total, None)

        if not completed_files:
            raise RuntimeError("Failed to convert WeChat articles")

        show_merge_button = len(completed_files) > 1
        yield (completed_files.copy(), len(completed_files), total, "completed" if show_merge_button else None)

    def is_article_list(self, url: str) -> bool:
        return WechatParser.is_article_list(url)

    def _extract_pdf_files(self, result: WechatConvertResult) -> list[str]:
        pdf_files: list[str] = []
        for article in result.articles:
            output = article.get("output")
            if isinstance(output, str):
                pdf_files.append(output)
        return pdf_files
