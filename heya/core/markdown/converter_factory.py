from __future__ import annotations

from collections.abc import Callable

from heya.core.models import ConvertResult
from heya.core.browser.browser_pool import BrowserSessionPool
from heya.core.pdf.pdf_compressor import PdfCompressor
from heya.core.pdf.pypdf_writer import PdfWriter
from heya.core.converters.converters import HtmlToPdfConverter, MarkdownToPdfConverter
from heya.core.markdown.markdown_processor import MarkdownProcessor
from heya.core.config import load_config

__all__ = ["create_markdown_converter"]


def create_markdown_converter(
    timeout: float = 3.0,
    compress: bool = False,
) -> Callable[..., ConvertResult]:
    config = load_config()
    browser_pool = BrowserSessionPool(
        timeout=config.browser.timeout,
        launch_args=config.browser.launch_args,
        print_config=config.print,
    )
    pdf_writer = PdfWriter()
    pdf_compressor = PdfCompressor()

    html_converter = HtmlToPdfConverter(
        browser=browser_pool,
        pdf_writer=pdf_writer,
        pdf_compressor=pdf_compressor,
        timeout=timeout,
    )

    markdown_processor = MarkdownProcessor(config.markdown)

    converter = MarkdownToPdfConverter(
        markdown_processor=markdown_processor,
        html_converter=html_converter,
    )

    async def convert(
        source: str,
        target: str,
        timeout: float = 3.0,
        compress: bool = False,
        quality: int = 0,
    ) -> ConvertResult:
        return await converter.convert(
            source=source,
            target=target,
            compress=compress,
            quality=quality,
        )

    return convert
