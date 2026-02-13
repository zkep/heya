from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

from heya.application import HtmlToPdfConverter
from heya.infrastructure.wechat import WechatParser
from heya.shared.logging import get_logger

__all__ = ["WechatArticleConverter", "WechatConvertResult"]

logger = get_logger(__name__)


@dataclass
class WechatConvertResult:
    success: bool
    articles: list[dict[str, Any]]
    total_duration: float
    output_dir: str


class WechatArticleConverter:
    def __init__(
        self,
        html_converter: HtmlToPdfConverter,
    ) -> None:
        self._html_converter = html_converter

    def convert(
        self,
        url: str,
        output_dir: str,
        compress: bool = False,
        quality: int = 0,
    ) -> WechatConvertResult:
        if not WechatParser.is_wechat_url(url):
            raise ValueError(f"Invalid WeChat URL: {url}")

        if WechatParser.is_article_list(url):
            return self._convert_article_list(url, output_dir, compress, quality)
        else:
            return self._convert_single_article(url, output_dir, compress, quality)

    def convert_stream(
        self,
        url: str,
        output_dir: str,
        compress: bool = False,
        quality: int = 0,
        progress_callback: Callable[[int, int, dict[str, Any]], None] | None = None,
    ) -> WechatConvertResult:
        if not WechatParser.is_wechat_url(url):
            raise ValueError(f"Invalid WeChat URL: {url}")

        if WechatParser.is_article_list(url):
            return self._convert_article_list_stream(
                url, output_dir, compress, quality, progress_callback
            )
        else:
            return self._convert_single_article(url, output_dir, compress, quality)

    def _convert_single_article(
        self,
        url: str,
        output_dir: str,
        compress: bool,
        quality: int,
    ) -> WechatConvertResult:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "article.pdf")

        result = self._html_converter.convert(
            source=url,
            target=output_path,
            compress=compress,
            quality=quality,
        )

        return WechatConvertResult(
            success=result.success,
            articles=[
                {
                    "title": "Single Article",
                    "url": url,
                    "output": result.output_path,
                    "duration": result.duration,
                }
            ],
            total_duration=result.duration,
            output_dir=output_dir,
        )

    def _convert_article_list(
        self,
        url: str,
        output_dir: str,
        compress: bool,
        quality: int,
    ) -> WechatConvertResult:
        return self._convert_article_list_stream(
            url, output_dir, compress, quality, None
        )

    def _convert_article_list_stream(
        self,
        url: str,
        output_dir: str,
        compress: bool,
        quality: int,
        progress_callback: Callable[[int, int, dict[str, Any]], None] | None,
    ) -> WechatConvertResult:
        articles = WechatParser.parse_article_list(url)

        if not articles:
            return WechatConvertResult(
                success=False,
                articles=[],
                total_duration=0.0,
                output_dir=output_dir,
            )

        os.makedirs(output_dir, exist_ok=True)
        results: list[dict[str, Any]] = []
        total_duration = 0.0
        total_count = len(articles)

        for idx, article in enumerate(articles):
            safe_title = self._sanitize_filename(article.title)
            output_path = os.path.join(
                output_dir, f"{article.index:02d}_{safe_title}.pdf"
            )

            try:
                result = self._html_converter.convert(
                    source=article.url,
                    target=output_path,
                    compress=compress,
                    quality=quality,
                )

                article_result = {
                    "title": article.title,
                    "url": article.url,
                    "output": result.output_path,
                    "duration": result.duration,
                }
                results.append(article_result)
                total_duration += result.duration

                if progress_callback:
                    progress_callback(idx + 1, total_count, article_result)
            except Exception as e:
                article_result = {
                    "title": article.title,
                    "url": article.url,
                    "output": None,
                    "duration": 0.0,
                    "error": str(e),
                }
                results.append(article_result)

                if progress_callback:
                    progress_callback(idx + 1, total_count, article_result)

        success = all(r.get("output") for r in results)
        return WechatConvertResult(
            success=success,
            articles=results,
            total_duration=total_duration,
            output_dir=output_dir,
        )

    @staticmethod
    def _sanitize_filename(title: str) -> str:
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, "_")
        return title[:100]
