from .app import YureiApp

__all__ = ("YureiApp",)


def entry() -> None:
    yurei = YureiApp()
    yurei.run()


def web_entry() -> None:
    from .web import run_server  # noqa: PLC0415 # required for extension access

    run_server()
