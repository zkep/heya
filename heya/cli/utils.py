from __future__ import annotations

import sys
from collections.abc import Callable
from contextlib import contextmanager
from typing import Generator

import click

from heya.cli.options import pdf_options
from heya.domain import ConvertResult

__all__ = [
    "handle_cli_errors",
    "print_success",
    "print_error",
    "print_result",
    "create_pdf_command",
]


@contextmanager
def handle_cli_errors() -> Generator[None, None, None]:
    try:
        yield
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


def print_success(message: str) -> None:
    click.echo(f"✓ {message}")


def print_error(message: str) -> None:
    click.echo(f"✗ {message}", err=True)


def print_result(result: ConvertResult) -> None:
    if result.success:
        print_success(f"PDF created: {result.output_path}")
        click.echo(f"  Duration: {result.duration:.2f}s")
        if result.error_message:
            click.echo(f"  Notes: {result.error_message}")


def create_pdf_command(
    name: str,
    help_text: str,
    converter: Callable[..., ConvertResult],
) -> click.Command:
    @click.command(name=name, help=help_text)
    @pdf_options
    def command(
        source: str,
        target: str,
        timeout: float,
        compress: bool,
        quality: int,
    ) -> None:
        with handle_cli_errors():
            result = converter(
                source=source,
                target=target,
                timeout=timeout,
                compress=compress,
                quality=quality,
            )
            print_result(result)

    return command
