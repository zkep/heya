from __future__ import annotations

import click
from heya.bin.html2pdf import html2pdf
from heya import __version__
from heya.bin.md2pdf import md2pdf


@click.group(invoke_without_command=True)
@click.option(
    "--version",
    is_flag=True,
)
@click.pass_context
def heya(ctx, version):
    if version:
        click.echo(__version__)
        ctx.exit()
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


heya.add_command(html2pdf)
heya.add_command(md2pdf)


def main() -> int:
    return heya(auto_envvar_prefix="HEYA")
