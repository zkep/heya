from __future__ import annotations

import os
import time

from heya.infrastructure.pdf import PdfMerger, PdfMergeItem
from heya.shared.temp import create_output_path
from heya.web.i18n import get_texts

__all__ = ["merge_pdfs"]


def merge_pdfs(
    pdf_files: list[str] | None,
    merge_title: str,
    filename_prefix: str,
    lang: str,
) -> tuple[str, str]:
    """Merge multiple PDF files into a single PDF with table of contents.

    Args:
        pdf_files: List of PDF file paths to merge
        merge_title: Title for the merged PDF
        filename_prefix: Prefix for the output filename
        lang: Language code for error messages

    Returns:
        Tuple of (merged_pdf_path, button_text)

    Raises:
        ValueError: If no valid PDF files to merge or merge fails
    """
    texts = get_texts(lang)

    if not pdf_files or len(pdf_files) == 0:
        raise ValueError(texts.error_no_files_to_merge)

    merger = PdfMerger()

    merge_items: list[PdfMergeItem] = []
    for idx, pdf_path in enumerate(pdf_files):
        if os.path.exists(pdf_path):
            filename = os.path.basename(pdf_path)
            title = os.path.splitext(filename)[0]
            merge_items.append(PdfMergeItem(title=title, file_path=pdf_path))

    if not merge_items:
        raise ValueError(texts.error_no_files_to_merge)

    output_dir = create_output_path()
    os.makedirs(output_dir, exist_ok=True)

    timestamp = int(time.time())
    merged_filename = f"{filename_prefix}_{timestamp}.pdf"
    merged_path = os.path.join(output_dir, merged_filename)

    result_path = merger.merge_pdfs_with_toc(
        items=merge_items,
        output_path=merged_path,
        title=merge_title,
    )

    return result_path, texts.merge_btn
