from __future__ import annotations

import os
from typing import Any

from heya.domain import ConvertResult
from heya.infrastructure import (
    MarkdownProcessor,
    PdfCompressor,
    PdfWriter,
    PlaywrightBrowser,
)
from heya.shared.config import get_config

from .converters import HtmlToPdfConverter, MarkdownToPdfConverter
from .ports import (
    BrowserPort,
    MarkdownPort,
    PdfCompressorPort,
    PdfWriterPort,
)
from .wechat_converter import WechatArticleConverter, WechatConvertResult

__all__ = [
    "BrowserPort",
    "MarkdownPort",
    "PdfWriterPort",
    "PdfCompressorPort",
    "HtmlToPdfConverter",
    "MarkdownToPdfConverter",
    "WechatArticleConverter",
    "WechatConvertResult",
    "create_html_converter",
    "create_markdown_converter",
    "create_wechat_converter",
    "convert",
    "convert_md",
    "convert_wechat",
    "convert_pdf_to_word",
]


def create_html_converter(
    timeout: float | None = None,
    compress: bool = False,
) -> HtmlToPdfConverter:
    config = get_config()
    browser = PlaywrightBrowser(
        timeout=timeout if timeout is not None else config.browser.timeout,
        launch_args=config.browser.launch_args,
        print_config=config.print,
    )
    compressor = PdfCompressor() if compress else None
    return HtmlToPdfConverter(
        browser, PdfWriter(), compressor, timeout or config.browser.timeout
    )


def create_markdown_converter(
    timeout: float | None = None,
    compress: bool = False,
) -> MarkdownToPdfConverter:
    html_converter = create_html_converter(timeout, compress)
    md_processor = MarkdownProcessor()
    return MarkdownToPdfConverter(md_processor, html_converter)


def create_wechat_converter(
    timeout: float | None = None,
    compress: bool = False,
) -> WechatArticleConverter:
    html_converter = create_html_converter(timeout, compress)
    return WechatArticleConverter(html_converter)


def convert(
    source: str,
    target: str,
    timeout: float = 3.0,
    compress: bool = False,
    quality: int = 0,
    print_options: dict[str, Any] | None = None,
) -> ConvertResult:
    converter = create_html_converter(timeout, compress)
    return converter.convert(
        source=source,
        target=target,
        compress=compress,
        quality=quality,
        print_options=print_options,
    )


def convert_md(
    source: str,
    target: str,
    timeout: float = 3.0,
    compress: bool = False,
    quality: int = 0,
) -> ConvertResult:
    converter = create_markdown_converter(timeout, compress)
    return converter.convert(
        source=source,
        target=target,
        compress=compress,
        quality=quality,
    )


def convert_wechat(
    url: str,
    output_dir: str,
    timeout: float = 3.0,
    compress: bool = False,
    quality: int = 0,
) -> WechatConvertResult:
    converter = create_wechat_converter(timeout, compress)
    return converter.convert(
        url=url,
        output_dir=output_dir,
        compress=compress,
        quality=quality,
    )


def convert_pdf_to_word(
    source: str,
    target: str,
) -> ConvertResult:
    try:
        from pdf2docx import Converter
    except ImportError:
        return ConvertResult(
            success=False,
            output_path=None,
            error_message="pdf2docx is required. Install with: pip install pdf2docx",
        )

    try:
        pdf_filename = os.path.basename(source)
        word_filename = os.path.splitext(pdf_filename)[0] + ".docx"
        word_path = os.path.join(os.path.dirname(target), word_filename)

        cv = Converter(source)
        cv.convert(word_path, start=0, end=None)
        cv.close()

        if os.path.exists(word_path):
            return ConvertResult(
                success=True,
                output_path=word_path,
                error_message=None,
            )
        return ConvertResult(
            success=False,
            output_path=None,
            error_message="Failed to convert PDF to Word",
        )
    except Exception as e:
        return ConvertResult(
            success=False,
            output_path=None,
            error_message=str(e),
        )
