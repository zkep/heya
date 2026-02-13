from __future__ import annotations


import click

from heya.application import convert_wechat
from heya.cli.utils import handle_cli_errors, print_error, print_success

__all__ = ["wechat2pdf"]


@click.command(
    name="wechat2pdf",
    help="Convert WeChat Official Account articles to PDF.\n\nSupports:\n  - Single article: Direct article URL\n  - Article list: Profile page with multiple articles\n\nExamples:\n  heya wechat2pdf -i https://mp.weixin.qq.com/s/xxx -o output/\n  heya wechat2pdf -i https://mp.weixin.qq.com/mp/profile_ext -o articles/ -c -q 1",
)
@click.option(
    "-i",
    "--url",
    required=True,
    type=str,
    help="WeChat article URL or profile URL",
)
@click.option(
    "-o",
    "--output",
    required=True,
    type=str,
    help="Output directory for PDF files",
)
@click.option(
    "-t",
    "--timeout",
    type=float,
    default=3.0,
    help="Timeout in seconds (default: 3.0)",
)
@click.option(
    "-c",
    "--compress",
    is_flag=True,
    default=False,
    help="Enable PDF compression",
)
@click.option(
    "-q",
    "--quality",
    type=int,
    default=0,
    help="Compression quality: 0=high, 1=medium, 2=low",
)
def wechat2pdf(
    url: str,
    output: str,
    timeout: float,
    compress: bool,
    quality: int,
) -> None:
    with handle_cli_errors():
        result = convert_wechat(
            url=url,
            output_dir=output,
            timeout=timeout,
            compress=compress,
            quality=quality,
        )

        if result.success:
            print_success(f"Conversion completed: {len(result.articles)} article(s)")
            click.echo(f"  Output directory: {result.output_dir}")
            click.echo(f"  Total duration: {result.total_duration:.2f}s")

            for article in result.articles:
                if article.get("output"):
                    print_success(f"  - {article['title']}")
                    click.echo(f"    File: {article['output']}")
                else:
                    print_error(f"  - {article['title']}")
                    click.echo(f"    Error: {article.get('error', 'Unknown')}")
        else:
            print_error("Conversion failed")
            if result.articles:
                click.echo(
                    f"  Partial success: {len([a for a in result.articles if a.get('output')])}/{len(result.articles)} articles"
                )
