from __future__ import annotations

import asyncio
import os
import click

from heya.core.helpers import convert
from heya.core.pdf import PdfMerger

__all__ = ["html2pdf"]


@click.command()
@click.option("-i", "--input", "input_path", required=True, multiple=True, help="URL or HTML file path (supports multiple inputs)")
@click.option("-o", "--output", "output_dir", help="Output directory path")
@click.option("-t", "--timeout", default=30.0, show_default=True, help="Timeout in seconds")
@click.option("-q", "--quality", type=click.Choice(["0", "1", "2"]), default="0", show_default=True, help="Compression quality: 0=high, 1=medium, 2=low")
@click.option("-m", "--merge", "merge_pdf", is_flag=True, help="Merge all PDFs into one file in order")
def html2pdf(
    input_path: tuple[str, ...],
    output_dir: str | None,
    timeout: float,
    quality: str,
    merge_pdf: bool,
) -> None:
    try:
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        total = len(input_path)
        temp_pdf_files = []
        
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
                    output_filename = f"heya_{uuid.uuid4().hex[:8]}.pdf"
                    target_path = os.path.join(output_dir, output_filename)
                else:
                    from heya.core.temp.temp import create_output_path
                    target_path = create_output_path()
                
                asyncio.run(convert(
                    source=path,
                    target=target_path,
                    timeout=timeout,
                    quality=int(quality),
                ))
                temp_pdf_files.append(target_path)
                if not merge_pdf:
                    click.echo(f"\n✓ Success! Output: {target_path}")
        
        if merge_pdf and len(temp_pdf_files) > 1:
            click.echo(f"\nMerging {len(temp_pdf_files)} PDFs...")
            merger = PdfMerger()
            if output_dir:
                import uuid
                merged_filename = f"heya_merged_{uuid.uuid4().hex[:8]}.pdf"
                merged_path = os.path.join(output_dir, merged_filename)
            else:
                from heya.core.temp.temp import create_output_path
                merged_path = create_output_path()
            
            merged_path = merger.merge_pdfs_simple(temp_pdf_files, merged_path)
            click.echo(f"✓ Merged PDF saved to: {merged_path}")
            
            for temp_file in temp_pdf_files:
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        raise click.ClickException(str(e))
