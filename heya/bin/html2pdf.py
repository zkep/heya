from __future__ import annotations

import click


from heya.pdf import converter


@click.command()
@click.option(
    "-i",
    "--source",
    required=True,
    help="source is html url",
)
@click.option(
    "-o",
    "--target",
    required=True,
    help="target is pdf save dir",
)
@click.option(
    "-t",
    "--timeout",
    type=float,
    default=3.0,
    help="timeout",
)
@click.option(
    "-c",
    "--compress",
    type=bool,
    default=False,
    help="compress",
)
@click.option(
    "-p",
    "--power",
    type=int,
    default=0,
    help="power",
)
@click.option(
    "-d",
    "--install_driver",
    type=bool,
    default=True,
    help="install driver",
)
def html2pdf(
    source,
    target,
    timeout,
    compress,
    power,
    install_driver,
):
    """Convert html to pdf file"""
    converter.convert(source, target, timeout, compress, power, install_driver)
