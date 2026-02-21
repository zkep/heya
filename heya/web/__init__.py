from __future__ import annotations



def create_app():
    from .app import create_app as _create_app

    return _create_app()


def run_server(host: str = "127.0.0.1", port: int = 7860, share: bool = False):
    from .app import run_server as _run_server

    _run_server(host, port, share)



__all__ = ["create_app", "run_server"]
