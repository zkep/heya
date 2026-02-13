from __future__ import annotations

import os
import time
from collections.abc import Callable

from heya.application.ports import (
    BrowserPort,
    MarkdownPort,
    PdfCompressorPort,
    PdfWriterPort,
)
from heya.domain import ConvertError, ConvertResult, PdfContent, compress_pdf
from heya.shared.logging import format_error_with_issue, get_logger
from heya.shared.temp import TempFileManager

logger = get_logger(__name__)


class HtmlToPdfConverter:
    """HTML to PDF converter.

    Converts HTML content from URLs or files to PDF format using a browser
    for rendering and optional compression.
    """

    def __init__(
        self,
        browser: BrowserPort,
        pdf_writer: PdfWriterPort,
        pdf_compressor: PdfCompressorPort | None = None,
        timeout: float = 3.0,
    ) -> None:
        """Initialize converter with dependencies.

        Args:
            browser: Browser implementation for rendering
            pdf_writer: PDF writer implementation
            pdf_compressor: Optional PDF compressor
            timeout: Browser timeout in seconds
        """
        self._browser = browser
        self._pdf_writer = pdf_writer
        self._pdf_compressor = pdf_compressor
        self._timeout = timeout

    def convert(
        self,
        source: str,
        target: str,
        compress: bool = False,
        quality: int = 0,
        print_options: dict[str, object] | None = None,
    ) -> ConvertResult:
        """Convert HTML source to PDF.

        Args:
            source: URL or file path to HTML content
            target: Output PDF file path
            compress: Whether to compress the PDF
            quality: Compression quality level (0-2)
            print_options: Additional browser print options

        Returns:
            ConvertResult with success status and output path

        Raises:
            ConvertError: If conversion fails
        """
        start_time = time.time()

        try:
            pdf_content = self._browser.render_to_pdf(source, print_options)

            if compress:
                if self._pdf_compressor is None:
                    raise ConvertError(
                        "Compression requested but no compressor provided"
                    )
                compress_fn: Callable[[PdfContent, int], PdfContent] = (
                    self._pdf_compressor.compress
                )
                pdf_content = compress_pdf(pdf_content, quality, compress_fn)

            self._pdf_writer.write(pdf_content, target)

            duration = time.time() - start_time
            return ConvertResult(
                success=True,
                output_path=target,
                duration=duration,
            )

        except Exception as e:
            raise ConvertError(format_error_with_issue(e)) from e


class MarkdownToPdfConverter:
    """Markdown to PDF converter.

    Converts Markdown files to PDF by first converting to HTML
    and then using the HTML to PDF converter.
    """

    def __init__(
        self,
        markdown_processor: MarkdownPort,
        html_converter: HtmlToPdfConverter,
    ) -> None:
        """Initialize converter with dependencies.

        Args:
            markdown_processor: Markdown to HTML processor
            html_converter: HTML to PDF converter
        """
        self._markdown_processor = markdown_processor
        self._html_converter = html_converter

    def convert(
        self,
        source: str,
        target: str,
        compress: bool = False,
        quality: int = 0,
    ) -> ConvertResult:
        with TempFileManager() as temp_manager:
            html_content = self._markdown_processor.convert_to_html(source)
            temp_html_path = temp_manager.create_temp_file(html_content, "output.html")
            html_url = f"file://{os.path.abspath(temp_html_path)}"
            return self._html_converter.convert(
                source=html_url,
                target=target,
                compress=compress,
                quality=quality,
            )
