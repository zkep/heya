from __future__ import annotations

from typing import Protocol, runtime_checkable

from heya.domain.models import PdfContent


@runtime_checkable
class BrowserPort(Protocol):
    def render_to_pdf(
        self,
        url: str,
        print_options: dict[str, object] | None = None,
    ) -> PdfContent: ...


@runtime_checkable
class PdfWriterPort(Protocol):
    def write(self, content: PdfContent, target: str) -> None: ...


@runtime_checkable
class PdfCompressorPort(Protocol):
    def compress(self, content: PdfContent, quality: int = 0) -> PdfContent: ...


@runtime_checkable
class MarkdownPort(Protocol):
    def convert_to_html(self, md_file: str) -> str: ...
