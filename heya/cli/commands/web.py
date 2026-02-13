from __future__ import annotations

import click


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
