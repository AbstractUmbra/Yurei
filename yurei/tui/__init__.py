from .app import YureiApp

__all__ = ("YureiApp",)


def entry() -> None:  # noqa: RUF067 # we use this as module level scripts
    yurei = YureiApp()
    yurei.run()


def web_entry() -> None:  # noqa: RUF067 # we use this as module level scripts
    from .web import run_server  # noqa: PLC0415 # required for extension access

    run_server()
