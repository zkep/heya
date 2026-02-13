from __future__ import annotations

from .pdf_compressor import PdfCompressor, compress
from .pdf_merger import PdfMerger, PdfMergeItem
from .pypdf_writer import PdfWriter

__all__ = ["PdfWriter", "PdfCompressor", "compress", "PdfMerger", "PdfMergeItem"]
