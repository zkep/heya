from __future__ import annotations

from heya.web.services.service import WebConvertService, ConversionError
from heya.web.services.handler import (
    convert_html_to_pdf_with_error_handling,
    convert_md_to_pdf,
    convert_md_to_pdf_stream,
    convert_wechat_to_pdf,
    convert_wechat_to_pdf_stream,
    merge_md_pdfs,
    merge_wechat_pdfs,
    convert_pdf_to_word_with_error_handling,
    show_error_dialog,
    open_issue_url,
    hide_error_dialog,
)

__all__ = [
    "WebConvertService",
    "ConversionError",
    "convert_html_to_pdf_with_error_handling",
    "convert_md_to_pdf",
    "convert_md_to_pdf_stream",
    "convert_wechat_to_pdf",
    "convert_wechat_to_pdf_stream",
    "merge_md_pdfs",
    "merge_wechat_pdfs",
    "convert_pdf_to_word_with_error_handling",
    "show_error_dialog",
    "open_issue_url",
    "hide_error_dialog",
]
