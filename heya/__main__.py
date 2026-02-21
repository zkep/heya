from __future__ import annotations

import click

from heya import __version__
from heya.cmd.commands import html2pdf, md2pdf, pdf2word
from heya.cmd.commands.wechat2pdf import wechat2pdf


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
        click.echo("  heya html2pdf -i <url/file> -o <output_dir/>")
        click.echo("  heya md2pdf -i <file.md> -o <output_dir/>")
        click.echo("  heya wechat2pdf -i <url> -o <output_dir/>")
        click.echo("  heya pdf2word -i <file.pdf> -o <output_dir/>")
        click.echo("  heya web              # Start web interface")
        click.echo("  heya app              # Start desktop application")
        click.echo("\nOptions:")
        click.echo("  --version             Show version")
        click.echo("  --help                Show this help message")
        ctx.exit()


cli.add_command(html2pdf)
cli.add_command(md2pdf)
cli.add_command(wechat2pdf)
cli.add_command(pdf2word)


@click.command()
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode",
)
def app(debug: bool) -> None:
    """Start the desktop application."""
    import sys
    import os

    if not os.isatty(sys.stdout.fileno()) and not debug:
        click.echo(
            "Warning: Desktop app may not display in sandboxed environments.\n"
            "Please run this command in a local terminal instead:\n"
            "  heya app\n"
            "Or run with --debug to see more info.",
            err=True,
        )

    if debug:
        print("Starting heya app...", file=sys.stderr)

    try:
        from heya.app import create_app
        from PySide6.QtWidgets import QApplication

        if debug:
            print("Creating QApplication...", file=sys.stderr)

        qt_app = QApplication(sys.argv)
        qt_app.setStyle("Fusion")

        if debug:
            print("Creating main window...", file=sys.stderr)

        main_window = create_app(qt_app)

        if debug:
            print(f"Main window created: {main_window}", file=sys.stderr)
            print(f"Window visible: {main_window.isVisible()}", file=sys.stderr)

        sys.exit(qt_app.exec())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


cli.add_command(app)


@click.command()
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Host to bind the server to",
)
@click.option(
    "--port",
    type=int,
    default=7860,
    help="Port to bind the server to",
)
@click.option(
    "--share",
    is_flag=True,
    help="Create a public share link",
)
def web(host: str, port: int, share: bool) -> None:
    """Start the Web UI server."""
    from heya.web import run_server

    click.echo(f"Starting Heya Web server on http://{host}:{port}")
    run_server(host=host, port=port, share=share)

cli.add_command(web)


def main() -> None:
    cli(auto_envvar_prefix="HEYA")


if __name__ == "__main__":
    main()
