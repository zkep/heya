from __future__ import annotations

from heya.core.interfaces import (
    BrowserPort,
    MarkdownPort,
    PdfCompressorPort,
    PdfWriterPort,
)
from heya.core.models import PdfContent
from heya.core.markdown.markdown_processor import MarkdownProcessor
from heya.core.pdf.pdf_compressor import PdfCompressor
from heya.core.pdf.pypdf_writer import PdfWriter
from heya.core.browser.playwright_browser import PlaywrightBrowser


class TestBrowserPort:
    def test_browser_service_implements_port(self) -> None:
        browser = PlaywrightBrowser()
        assert isinstance(browser, BrowserPort) is True
        assert hasattr(browser, "render_to_pdf")


class TestPdfWriterPort:
    def test_pdf_writer_implements_port(self) -> None:
        writer = PdfWriter()
        assert isinstance(writer, PdfWriterPort) is True
        assert hasattr(writer, "write")


class TestPdfCompressorPort:
    def test_pdf_compressor_implements_port(self) -> None:
        compressor = PdfCompressor()
        assert isinstance(compressor, PdfCompressorPort) is True
        assert hasattr(compressor, "compress")


class TestMarkdownPort:
    def test_markdown_service_implements_port(self) -> None:
        processor = MarkdownProcessor()
        assert isinstance(processor, MarkdownPort) is True
        assert hasattr(processor, "convert_to_html")
