import pathlib
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.validation import Function, Integer, Length
from textual.widgets import DirectoryTree, Footer, Header, Input, Label, RadioButton, RadioSet, TextArea

from yurei.save import Save

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from textual.binding import BindingType
    from textual.dom import DOMNode
    from textual.timer import Timer


def is_real_path(input_: str) -> bool:
    return pathlib.Path(input_).expanduser().resolve().exists()


class SafeDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
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


class YureiApp(App[None]):
    save_file: Save
    debounce_timer: Timer | None
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+q", "quit", "Exit the application, making no changes", show=True, priority=True),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("o", "open_file", "Browse for a save file"),
        ("O", "open_file(True)", "Open the default save file at known path"),
        Binding("ctrl+w", "save_file", "Save the current edits to the selected file", priority=True),
    ]
    CSS_PATH = "../../css/layout.tcss"

    def compose(self) -> ComposeResult:
        self.debounce_timer = None
        yield Header(id="app-header", show_clock=True)
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane", can_focus=True, can_focus_children=True):
                yield PathInput()
                yield SafeDirectoryTree(".", id="open-save-tree")
            with Container(id="top-right"):
                yield Container(id="top-right-container")
            with Container(id="bottom-right"), VerticalScroll(id="data-pane"):
                yield TextArea.code_editor(id="decrypted-output", language="json", read_only=True, show_line_numbers=True)
        yield Footer(show_command_palette=False)

    async def on_mount(self) -> None:
        self.set_focus(self.query_one("#open-save-tree", SafeDirectoryTree))

    def action_exit_app(self) -> None:
        self.exit(None, 0, message="Closing without saving any changes.")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:  # noqa: ARG002 # not yet anyway
        if action == "save_file" and not getattr(self, "save_file", None):  # noqa: SIM103 # this may need more nesting
            return False
        return True

    async def action_open_file(self, default: bool = False) -> None:  # noqa: FBT001, FBT002 # i dont think kwargs are supported
        pane = self.query_one("#left-pane", VerticalScroll)
        if default:
            self.save_file = Save.from_default_path()
            text_area = self.query_one("#decrypted-output", TextArea)
            text_area.replace(insert=self.save_file.to_json_string(), start=(0, 0), end=text_area.document.end)

        # reload input
        input_ = pane.query_one("#path-input", Input)
        if pane:
            input_.value = ""
            input_.placeholder = "Path..."
            input_.refresh()
        # reload tree if exists
        tree = pane.query_one("#open-save-tree", SafeDirectoryTree)
        if tree:
            await tree.reload()
            tree.focus()
            return

        input_ = Input(placeholder="Path...", id="path-input")
        directory_tree = SafeDirectoryTree(".", id="open-save-tree")
        await pane.mount(input_, directory_tree)
        directory_tree.focus()

    async def action_save_file(self) -> None:
        if not getattr(self, "save_file", None):
            self.notify("There is no save file being actively edited!", severity="warning", timeout=3.0)
            return

        backup_path = self.save_file.create_backup()
        self.notify(
            f"Created a backup of the original save file at\n[i]{backup_path}[/i]", severity="information", timeout=3.0
        )

        self.save_file.write()
        self.notify("The selected file has been written to!", severity="information", timeout=3.0)

    def refresh_code_container(self) -> None:
        text_area = self.query_one("#decrypted-output", TextArea)
        text_area.replace(insert=self.save_file.to_json_string(), start=(0, 0), end=text_area.document.end)
        text_area.refresh()

    async def file_selected(self, file: pathlib.Path, /) -> None:
        self.save_file = Save.from_path(file)
        self.refresh_code_container()

        pane = self.query_one("#left-pane", VerticalScroll)

        await pane.remove_children()
        radio_set = RadioSet(
            *[RadioButton(item[0], id=item[1]) for item in sorted(self.save_file.ALLOWED_OPERATIONS)], id="methods"
        )
        await pane.mount(radio_set)
        self.set_focus(radio_set)

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        await self.file_selected(event.path)

    async def on_radio_set_changed(self, message: RadioSet.Changed) -> None:
        if message.radio_set.id == "methods":
            match message.pressed.id:
                case "edit-money":
                    container = Container(
                        VerticalScroll(
                            Label("Money:", id="money-label"),
                            Input(
                                placeholder=f"{self.save_file.money}",
                                type="integer",
                                validate_on=["submitted", "blur"],
                                validators=[Length(minimum=0), Integer(0, 249999, "must be between 0 and 249,999")],
                                id="money-value",
                            ),
                            id="money-scroll",
                        ),
                        id="money-editor",
                    )
                case _:
                    return

            top_right = self.query_one("#top-right", Container)
            await top_right.remove_children("#top-right-container")

            await top_right.mount(container)
            self.set_focus(container)

    def _handle_money_value(self, event: Input.Submitted | Input.Blurred) -> None:
        if event.validation_result and not event.validation_result.is_valid:
            self.notify(
                message="\n".join(event.validation_result.failure_descriptions),
                title="Edit money",
                severity="error",
                timeout=3.0,
            )
            return
        if event.input.id == "money-value":
            self.notify(
                f"Edited your money value to {event.value}!", title="Edit money", severity="information", timeout=3.0
            )
            self.save_file.money = int(event.value)

    async def _handle_path_input(self, event: Input.Submitted | Input.Blurred, *, parent: DOMNode | None = None) -> None:
        if event.validation_result and not event.validation_result.is_valid:
            self.notify(
                message="\n".join(event.validation_result.failure_descriptions),
                title="Path input",
                severity="error",
                timeout=3.0,
            )
            return

        if not parent:
            return

        tree = parent.query_one("#open-save-tree", SafeDirectoryTree)
        new_path = pathlib.Path(event.value).expanduser().resolve()
        if new_path.is_dir():
            tree.path = new_path
            await tree.reload()
            return

        await self.file_selected(new_path)

    @on(Input.Submitted)
    @on(Input.Blurred)
    async def update_input(self, event: Input.Submitted | Input.Blurred) -> None:
        parent = event.input.parent

        match event.input.id:
            case "path-input":
                await self._handle_path_input(event, parent=parent)
                return
            case "money-value":
                self._handle_money_value(event)
                return
            case _:
                pass

        self.refresh_code_container()
