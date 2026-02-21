from __future__ import annotations

from heya.core.models import ConvertResult
from heya.core.exceptions import PdfToWordError

__all__ = ["convert_pdf_to_word"]


def convert_pdf_to_word(
    source: str,
    target: str,
) -> ConvertResult:
    try:
        from pdf2docx import Converter

        cv = Converter(source)
        cv.convert(target, start=0, end=None)
        cv.close()

        return ConvertResult(
            success=True,
            output_path=target,
            duration=0.0,
        )
    except Exception as e:
        raise PdfToWordError(f"Failed to convert PDF to Word: {e}") from e
