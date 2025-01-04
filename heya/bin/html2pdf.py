import click

from heya.bin.base import HeyaCommand, HeyaOption
from heya.pdf import _html


@click.command(cls=HeyaCommand)
@click.option(
    "-i",
    "--source",
    cls=HeyaOption,
    required=True,
    help_group="Source Options",
    help="source is html url",
)
@click.option(
    "-o",
    "--target",
    cls=HeyaOption,
    required=True,
    help_group="Target Options",
    help="target is pdf save dir",
)
@click.option(
    "-t",
    "--timeout",
    cls=HeyaOption,
    type=float,
    default=3.0,
    help_group="Timeout Options",
    help="timeout",
)
@click.option(
    "-c",
    "--compress",
    cls=HeyaOption,
    type=bool,
    default=False,
    help_group="Compress Options",
    help="compress",
)
@click.option(
    "-p",
    "--power",
    cls=HeyaOption,
    type=int,
    default=0,
    help_group="Power Options",
    help="power",
)
@click.option(
    "-d",
    "--install_driver",
    cls=HeyaOption,
    type=bool,
    default=True,
    help_group="install driver Options",
    help="install driver",
)
@click.pass_context
def html2pdf(
    ctx,
    source,
    target,
    timeout,
    compress,
    power,
    install_driver,
):
    """Convert html to pdf file"""
    _html.convert(source, target, timeout, compress, power, install_driver)
