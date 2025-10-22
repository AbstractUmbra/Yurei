import pathlib
from typing import TYPE_CHECKING

from textual.containers import VerticalScroll
from textual.validation import Function, Length
from textual.widgets import DirectoryTree, Input

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = ("PathInput", "PathInputBrowser", "SafeDirectoryTree")


def is_real_path(input_: str) -> bool:
    return pathlib.Path(input_).expanduser().resolve().exists()


class SafeDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[pathlib.Path]) -> Iterable[pathlib.Path]:
        return [p for p in paths if not p.name.startswith(".")]


class PathInput(Input):
    def __init__(self) -> None:
        super().__init__(
            placeholder="Path...",
            id="path-input",
            validators=[
                Function(is_real_path, failure_description="The provided path does not exist or is not readable/writable."),
                Length(minimum=0, failure_description="Length of the path must be at least 1 character, if provided"),
            ],
            validate_on=["submitted", "blur"],
        )


class PathInputBrowser(VerticalScroll):
    def __init__(self, id_: str, /, *, path: pathlib.Path | str = ".") -> None:
        super().__init__(
            PathInput(), SafeDirectoryTree(path, id="open-save-tree"), id=id_, can_focus=True, can_focus_children=True
        )
