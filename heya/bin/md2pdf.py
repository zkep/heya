from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import click
import yaml

from heya.bin.base import HeyaCommand, HeyaOption
from heya.pdf import converter


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
def md2pdf(
    ctx,
    source,
    target,
    timeout,
    compress,
    power,
    install_driver,
):
    """Convert markdown to pdf file"""
    current_path = os.path.abspath(os.path.dirname(__file__))
    source = os.path.abspath(source)
    with open(os.path.join(current_path, "mkdocs.yml")) as f:
        data = yaml.safe_load(f)
        with tempfile.TemporaryDirectory() as tmpdir:
            mkdocs = os.path.join(tmpdir, "mkdocs.yml")
            with open(mkdocs, "w") as w:
                w.write(yaml.safe_dump(data))

            docs_dir = os.path.join(tmpdir, "docs")
            os.mkdir(docs_dir)
            shutil.copy(source, os.path.join(docs_dir, "index.md"))

            proc = subprocess.Popen(
                ["mkdocs", "serve"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            converter.convert(
                "http://127.0.0.1:8000/",
                target,
                timeout,
                compress,
                power,
                install_driver,
            )

            proc.kill()
