from __future__ import annotations

from collections.abc import Callable

from heya.core.models import ConvertResult
from heya.core.browser.browser_pool import BrowserSessionPool
from heya.core.pdf.pdf_compressor import PdfCompressor
from heya.core.pdf.pypdf_writer import PdfWriter
from heya.core.converters.converters import HtmlToPdfConverter
from heya.core.config import load_config

__all__ = ["create_html_converter"]


def create_html_converter(
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

    converter = HtmlToPdfConverter(
        browser=browser_pool,
        pdf_writer=pdf_writer,
        pdf_compressor=pdf_compressor,
        timeout=timeout,
    )

    async def convert(
        source: str,
        target: str,
        timeout: float = 3.0,
        compress: bool = False,
        quality: int = 0,
        print_options: dict[str, object] | None = None,
    ) -> ConvertResult:
        return await converter.convert(
            source=source,
            target=target,
            compress=compress,
            quality=quality,
            print_options=print_options,
        )

    return convert
