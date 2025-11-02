from typing import TYPE_CHECKING, ClassVar

from textual.binding import Binding
from textual.widgets import TextArea

if TYPE_CHECKING:
    from yurei.tui.app import YureiApp

__all__ = ("CodeEditor",)


class CodeEditor(TextArea):
    app: YureiApp
    BINDINGS: ClassVar[list[Binding]] = [Binding("ctrl+s", "save", "Save your text-area edits", show=True)]

    def action_save(self) -> None:
        self.app.save_file.from_json_string(self.text)
        self.app.save_file.write()
        self.app.notify("Successfully saved the editor contents!", title="Success!", severity="information", timeout=3.0)
        self.app.refresh_code_container()
