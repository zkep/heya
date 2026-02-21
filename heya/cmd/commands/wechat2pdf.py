from __future__ import annotations

import asyncio
import os
import click

from heya.core.helpers import convert_wechat
from heya.core.pdf import PdfMerger

__all__ = ["wechat2pdf"]


@click.command()
@click.option("-i", "--input", "input_url", required=True, multiple=True, help="WeChat article URL (supports multiple inputs)")
@click.option("-o", "--output", "output_dir", help="Output directory path")
@click.option("-t", "--timeout", default=30.0, show_default=True, help="Timeout in seconds")
@click.option("-q", "--quality", type=click.Choice(["0", "1", "2"]), default="0", show_default=True, help="Compression quality: 0=high, 1=medium, 2=low")
@click.option("-m", "--merge", "merge_pdf", is_flag=True, help="Merge all PDFs into one file in order")
def wechat2pdf(
    input_url: tuple[str, ...],
    output_dir: str | None,
    timeout: float,
    quality: str,
    merge_pdf: bool,
) -> None:
    try:
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        total = len(input_url)
        temp_pdf_files = []
        
        with click.progressbar(
            input_url,
            label=f"Converting {total} URL(s)",
            length=total,
            show_pos=True,
            show_eta=True,
        ) as bar:
            for url in bar:
                click.echo(f"\nConverting: {url}")
                
                if output_dir:
                    result = asyncio.run(convert_wechat(
                        url=url,
                        output_dir=output_dir,
                        timeout=timeout,
                        compress=True,
                        quality=int(quality),
                    ))
                else:
                    from heya.core.temp.temp import create_output_path
                    temp_output = create_output_path()
                    os.makedirs(temp_output, exist_ok=True)
                    result = asyncio.run(convert_wechat(
                        url=url,
                        output_dir=temp_output,
                        timeout=timeout,
                        compress=True,
                        quality=int(quality),
                    ))
                
                for article in result.articles:
                    output = article.get("output")
                    if output:
                        temp_pdf_files.append(output)
                        if not merge_pdf:
                            click.echo(f"✓ Success! Output: {output}")
        
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
