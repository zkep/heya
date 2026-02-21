from __future__ import annotations

import os
import click

from heya.core.pdf import convert_pdf_to_word

__all__ = ["pdf2word"]


@click.command()
@click.option("-i", "--input", "input_path", required=True, multiple=True, help="PDF file path (supports multiple inputs)")
@click.option("-o", "--output", "output_dir", help="Output directory path")
def pdf2word(
    input_path: tuple[str, ...],
    output_dir: str | None,
) -> None:
    try:
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        total = len(input_path)
        with click.progressbar(
            input_path,
            label=f"Converting {total} file(s)",
            length=total,
            show_pos=True,
            show_eta=True,
        ) as bar:
            for path in bar:
                if output_dir:
                    import uuid
                    output_filename = f"heya_{uuid.uuid4().hex[:8]}.docx"
                    target_path = os.path.join(output_dir, output_filename)
                else:
                    from heya.core.temp.temp import create_output_path
                    target_path = create_output_path()
                
                convert_pdf_to_word(path, target_path)
                click.echo(f"\n✓ Success! Output: {target_path}")
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        raise click.ClickException(str(e))
