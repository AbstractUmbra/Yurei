import os

try:
    from textual_serve.server import Server
except ModuleNotFoundError:
    raise RuntimeError("The `web` extra is required to use the web extension.") from None

PORT = int(os.getenv("YUREI_PORT", "8000"))
HOST = os.getenv("YUREI_BIND_ADDRESS", "localhost")

__all__ = ("run_server",)


def run_server() -> None:
    server = Server("yurei", host=HOST, port=PORT)
    server.serve()
