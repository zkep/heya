from __future__ import annotations

import os
import shutil
import socket
import subprocess
import tempfile

import click
import yaml

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
def md2pdf(
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

            port = get_available_port()
            proc = subprocess.Popen(
                ["mkdocs", "serve", "-a", f"localhost:{port}"],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )

            converter.convert(
                f"http://localhost:{port}",
                target,
                timeout,
                compress,
                power,
                install_driver,
            )

            proc.kill()


def get_available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
