from __future__ import annotations

import time
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from heya.core.converters.converters import HtmlToPdfConverter, MarkdownToPdfConverter
from heya.core.exceptions import ConvertError
from heya.core.models import ConvertResult, PdfContent


class MockBrowser:
    def __init__(self, pdf_data: bytes = b"test-pdf") -> None:
        self._pdf_data = pdf_data

    def acquire(self):
        return MockBrowserContext(self)


class MockBrowserContext:
    def __init__(self, browser: MockBrowser) -> None:
        self._browser = browser

    async def __aenter__(self) -> "MockBrowserContext":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def render(
        self,
        url: str,
        print_options: dict[str, object] | None = None,
    ) -> bytes:
        return self._browser._pdf_data


class MockBrowserWithError:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def acquire(self):
        return MockBrowserContextWithError(self)


class MockBrowserContextWithError:
    def __init__(self, browser: MockBrowserWithError) -> None:
        self._browser = browser

    async def __aenter__(self) -> "MockBrowserContextWithError":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def render(
        self,
        url: str,
        print_options: dict[str, object] | None = None,
    ) -> bytes:
        raise self._browser._error


class MockPdfWriter:
    def __init__(self) -> None:
        self.written_content: PdfContent | None = None

    def write(self, content: PdfContent, target: str) -> None:
        self.written_content = content


class MockPdfCompressor:
    def compress(self, content: PdfContent, quality: int = 0) -> PdfContent:
        return PdfContent(b"compressed-" + content.data)


class MockMarkdownService:
    def __init__(self, html_content: str = "<html>test</html>") -> None:
        self._html_content = html_content

    def convert_to_html(self, md_file: str) -> str:
        return self._html_content


class TestHtmlToPdfConverter:
    @pytest.mark.asyncio
    async def test_convert_success(self) -> None:
        browser = MockBrowser(b"test-pdf-content")
        pdf_writer = MockPdfWriter()
        converter = HtmlToPdfConverter(browser, pdf_writer)

        result = await converter.convert(
            source="https://example.com",
            target="/tmp/output.pdf",
        )

        assert result.success is True
        assert result.output_path == "/tmp/output.pdf"
        assert result.duration >= 0
        assert pdf_writer.written_content is not None
        assert pdf_writer.written_content.data == b"test-pdf-content"

    @pytest.mark.asyncio
    async def test_convert_with_compression(self) -> None:
        browser = MockBrowser(b"test-pdf-content")
        pdf_writer = MockPdfWriter()
        pdf_compressor = MockPdfCompressor()
        converter = HtmlToPdfConverter(browser, pdf_writer, pdf_compressor)

        result = await converter.convert(
            source="https://example.com",
            target="/tmp/output.pdf",
            compress=True,
            quality=0,
        )

        assert result.success is True
        assert pdf_writer.written_content is not None
        assert b"compressed-" in pdf_writer.written_content.data

    @pytest.mark.asyncio
    async def test_convert_failure(self) -> None:
        browser = MockBrowserWithError(Exception("Browser error"))
        pdf_writer = MockPdfWriter()
        converter = HtmlToPdfConverter(browser, pdf_writer)

        with pytest.raises(ConvertError, match="Browser error"):
            await converter.convert(
                source="https://example.com",
                target="/tmp/output.pdf",
            )


class TestMarkdownToPdfConverter:
    @pytest.mark.asyncio
    async def test_convert_success(self) -> None:
        browser = MockBrowser(b"test-pdf-content")
        pdf_writer = MockPdfWriter()
        html_converter = HtmlToPdfConverter(browser, pdf_writer)
        markdown_service = MockMarkdownService()
        converter = MarkdownToPdfConverter(markdown_service, html_converter)

        result = await converter.convert(
            source="test.md",
            target="/tmp/output.pdf",
        )

        assert result.success is True
        assert result.output_path == "/tmp/output.pdf"

    @pytest.mark.asyncio
    async def test_convert_with_compression(self) -> None:
        browser = MockBrowser(b"test-pdf-content")
        pdf_writer = MockPdfWriter()
        pdf_compressor = MockPdfCompressor()
        html_converter = HtmlToPdfConverter(browser, pdf_writer, pdf_compressor)
        markdown_service = MockMarkdownService()
        converter = MarkdownToPdfConverter(markdown_service, html_converter)

        result = await converter.convert(
            source="test.md",
            target="/tmp/output.pdf",
            compress=True,
            quality=0,
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_cleanup_called_on_error(self) -> None:
        browser = MockBrowserWithError(Exception("Browser error"))
        pdf_writer = MockPdfWriter()
        html_converter = HtmlToPdfConverter(browser, pdf_writer)
        markdown_service = MockMarkdownService()
        converter = MarkdownToPdfConverter(markdown_service, html_converter)

        with pytest.raises(ConvertError):
            await converter.convert(
                source="test.md",
                target="/tmp/output.pdf",
            )


class TestPdfContent:
    def test_pdf_content_creation(self) -> None:
        content = PdfContent(b"test-pdf-data")
        assert len(content) == 13
        assert content.size == 13
        assert content.size_kb == 13 / 1024
        assert content.size_mb == 13 / (1024 * 1024)

    def test_pdf_content_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            PdfContent("not-bytes")
