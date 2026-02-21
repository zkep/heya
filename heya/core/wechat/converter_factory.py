from __future__ import annotations

from heya.core.browser.browser_pool import BrowserSessionPool
from heya.core.pdf.pdf_compressor import PdfCompressor
from heya.core.pdf.pypdf_writer import PdfWriter
from heya.core.converters.converters import HtmlToPdfConverter
from heya.core.wechat.wechat_converter import WechatArticleConverter
from heya.core.config import load_config

__all__ = ["create_wechat_converter"]


def create_wechat_converter(
    timeout: float = 3.0,
    compress: bool = False,
) -> WechatArticleConverter:
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

    converter = WechatArticleConverter(html_converter=html_converter)

    return converter
