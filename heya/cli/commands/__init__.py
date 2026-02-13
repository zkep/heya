from __future__ import annotations

import click

from heya.application import convert, convert_md, convert_pdf_to_word
from heya.cli.utils import create_pdf_command

html2pdf = create_pdf_command(
    name="html2pdf",
    help_text="Convert HTML URL or file to PDF.\n\nExamples:\n  heya html2pdf -i https://example.com -o output.pdf\n  heya html2pdf -i file:///path/to/page.html -o output.pdf -c",
    converter=convert,
)

md2pdf = create_pdf_command(
    name="md2pdf",
    help_text="Convert Markdown file to PDF.\n\nExamples:\n  heya md2pdf -i README.md -o output.pdf\n  heya md2pdf -i doc.md -o output.pdf -c -q 1",
    converter=convert_md,
)


@click.command(
    name="pdf2word",
    help="Convert PDF to Word document.\n\nExamples:\n  heya pdf2word -i document.pdf -o output.docx",
)
@click.option(
    "-i",
    "--source",
    required=True,
    type=str,
    help="Source PDF file path",
)
@click.option(
    "-o",
    "--target",
    required=True,
    type=str,
    help="Target Word file path",
)
def pdf2word(source: str, target: str) -> None:
    from heya.cli.utils import handle_cli_errors, print_result

    with handle_cli_errors():
        result = convert_pdf_to_word(
            source=source,
            target=target,
        )
        print_result(result)


__all__ = ["html2pdf", "md2pdf", "pdf2word"]
