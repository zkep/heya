from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

import click

F = TypeVar("F", bound=Callable)

__all__ = ["pdf_options"]


def pdf_options(fn: F) -> F:
    decorators = [
        click.option(
            "-i",
            "--source",
            required=True,
            type=str,
            help="Source file path or URL",
        ),
        click.option(
            "-o",
            "--target",
            required=True,
            type=str,
            help="Target PDF file path",
        ),
        click.option(
            "-t",
            "--timeout",
            type=float,
            default=3.0,
            help="Timeout in seconds (default: 3.0)",
        ),
        click.option(
            "-c",
            "--compress",
            is_flag=True,
            default=False,
            help="Enable PDF compression",
        ),
        click.option(
            "-q",
            "--quality",
            type=int,
            default=0,
            help="Compression quality: 0=high, 1=medium, 2=low",
        ),
    ]
    for d in reversed(decorators):
        fn = d(fn)
    return fn
