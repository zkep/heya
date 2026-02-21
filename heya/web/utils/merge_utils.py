from __future__ import annotations

from heya.core.pdf.pdf_merger import PdfMerger
from heya.core.temp.temp import create_output_path
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

    output_dir = create_output_path()

    result_path = merger.merge_pdfs_with_options(
        pdf_files=pdf_files,
        merge_title=merge_title,
        filename_prefix=filename_prefix,
        output_dir=output_dir,
    )

    return result_path, texts.merge_btn
