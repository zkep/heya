from __future__ import annotations

import click

from heya import __version__
from heya.cli.commands import html2pdf, md2pdf, pdf2word
from heya.cli.commands.wechat import wechat2pdf
from heya.cli.commands.web import web

__all__ = ("main",)


@click.group(
    invoke_without_command=True,
    help="heya is a powerful tool for WeChat articles, HTML, Markdown PDF conversion",
)
@click.option("--version", is_flag=True, help="Show version information")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    if version:
        click.echo(f"heya v{__version__}")
        click.echo("WeChat articles, HTML, Markdown PDF converter")
        ctx.exit()
    elif ctx.invoked_subcommand is None:
        click.echo("📄 heya - WeChat articles, HTML, Markdown PDF converter")
        click.echo("\nUsage:")
        click.echo("  heya html2pdf -i <url/file> -o <output.pdf>")
        click.echo("  heya md2pdf -i <file.md> -o <output.pdf>")
        click.echo("  heya wechat2pdf -i <url> -o <output_dir/>")
        click.echo("  heya pdf2word -i <file.pdf> -o <output.docx>")
        click.echo("  heya web              # Start web interface")
        click.echo("\nOptions:")
        click.echo("  --version             Show version")
        click.echo("  --help                Show this help message")
        ctx.exit()


cli.add_command(html2pdf)
cli.add_command(md2pdf)
cli.add_command(wechat2pdf)
cli.add_command(pdf2word)
cli.add_command(web)


def main() -> None:
    cli(auto_envvar_prefix="HEYA")


if __name__ == "__main__":
    main()
