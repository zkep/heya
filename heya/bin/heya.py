import click
import click.exceptions

from heya.bin.base import HeyaOption
from heya.bin.html2pdf import html2pdf
from heya import VERSION_BANNER


@click.group(invoke_without_command=True)
@click.option(
    "--version",
    cls=HeyaOption,
    is_flag=True,
    help_group="Global Options",
)
@click.pass_context
def heya(ctx, version):
    if version:
        click.echo(VERSION_BANNER)
        ctx.exit()
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


heya.add_command(html2pdf)


def main() -> int:
    return heya(auto_envvar_prefix="HEYA")