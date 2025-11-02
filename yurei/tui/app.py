import pathlib
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.events import Focus
from textual.widgets import (
    DirectoryTree,
    Footer,
    Header,
    Input,
    RadioButton,
    RadioSet,
    TextArea,
)

from yurei.save import EQUIPMENT, Save

from .widgets.add_gear import AddGearGrid
from .widgets.file_browser import PathInputBrowser, SafeDirectoryTree
from .widgets.level import LevelGrid
from .widgets.money import MoneyGrid
from .widgets.unlock_gear import UnlockGearGrid
from .widgets.unlockables import AchievementManageGrid, UnlockablePane

if TYPE_CHECKING:
    from textual.binding import BindingType
    from textual.dom import DOMNode
    from textual.timer import Timer

    from yurei.unlockable import Achievement


class YureiApp(App[None]):
    _has_touched_editor: bool
    save_file: Save
    debounce_timer: Timer | None
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+q", "quit", "Exit the application, making no changes", show=True, priority=True),
        ("o", "open_file", "Browse for a save file"),
        ("O", "open_file(True)", "Open the default save file at known path"),
        Binding("ctrl+w", "save_file", "Save the current edits to the selected file", priority=True),
    ]
    CSS_PATH = "../../css/layout.tcss"
    TITLE = "Yurei"
    SUB_TITLE = "A Phasmophobia Save editor"

    def compose(self) -> ComposeResult:
        self.theme = "textual-dark"
        yield Header(name="Yurei", id="app-header", show_clock=True)
        with Container(id="app-grid"):
            yield PathInputBrowser("left-pane", path=".")
            with Horizontal(id="top-right"):
                yield Container(id="top-right-container")
            with Container(id="bottom-right"), VerticalScroll(id="data-pane"):
                ta = TextArea.code_editor(id="decrypted-output", language="json", read_only=False, show_line_numbers=True)
                ta.border_title = "Decoded save output"
                ta.border_subtitle = "Edit at your own risk!"
                yield ta
        yield Footer(show_command_palette=False)

    async def on_mount(self) -> None:
        self._has_touched_editor = False
        self.set_focus(self.query_one("#open-save-tree", SafeDirectoryTree))

    def action_exit_app(self) -> None:
        self.exit(None, 0, message="Closing without saving any changes.")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:  # noqa: ARG002 # not yet anyway
        if action == "save_file" and not getattr(self, "save_file", None):  # noqa: SIM103 # this may need more nesting
            return False
        return True

    @on(Focus, "#decrypted-output")
    async def on_text_editor_focus(self, _: Focus) -> None:
        if getattr(self, "_has_touched_editor", False):
            return

        self.notify(
            "Please only edit and save these changes at your own risk.", title="Warning!", severity="warning", timeout=3.0
        )
        self._has_touched_editor = True

    async def action_open_file(self, default: bool = False) -> None:  # noqa: FBT001, FBT002 # i dont think kwargs are supported
        pane = self.query_one("#left-pane", PathInputBrowser)
        if default:
            self.save_file = Save.from_default_path()
            text_area = self.query_one("#decrypted-output", TextArea)
            text_area.replace(insert=self.save_file.to_json_string(), start=(0, 0), end=text_area.document.end)

        # reload input
        input_ = pane.query_one("#path-input", Input)
        input_.value = ""
        input_.placeholder = "Path..."
        input_.refresh()

        # reload tree if exists
        try:
            tree = pane.query_one("#open-save-tree", SafeDirectoryTree)
        except NoMatches:
            pass
        else:
            await tree.reload()
            tree.focus()
            return

        await pane.remove()
        browser = PathInputBrowser("left-pane", path=".")
        await self.mount(browser)
        directory_tree = browser.query_one("#open-save-tree", SafeDirectoryTree)
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

        pane = self.query_one("#left-pane")

        await pane.remove_children()
        pane.border_title = "Options"
        radio_set = RadioSet(
            *[RadioButton(item[0], id=item[1]) for item in sorted(self.save_file.TUI_ALLOWED_OPERATIONS)], id="methods"
        )
        await pane.mount(radio_set)
        self.set_focus(radio_set)

    async def set_unlockable_pane(self) -> None:
        new_pane = UnlockablePane("left-pane", radio_set_id="unlockables")
        current_pane = self.query_one("#left-pane")
        await current_pane.remove()

        app_grid = self.query_one("#app-grid", Container)
        await app_grid.mount(new_pane, before=0)
        self.set_focus(new_pane.query_one("#unlockables", RadioSet))

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        await self.file_selected(event.path)

    @on(RadioSet.Changed, "#methods")
    async def on_methods_radio_changed(self, message: RadioSet.Changed) -> None:
        if not message.pressed.id:
            return None

        match message.pressed.id:
            case "edit-money":
                to_mount = MoneyGrid()
            case "alter-level":
                to_mount = LevelGrid()
            case "unlock-gear":
                items = [(item, item) for item in sorted(EQUIPMENT)]
                to_mount = UnlockGearGrid(items)
            case "add-gear":
                items = [(item, item) for item in sorted(EQUIPMENT)]
                to_mount = AddGearGrid(items)
            case "manage-unlockables":
                return await self.set_unlockable_pane()
            case _:
                return None

        top_right = self.query_one("#top-right", Horizontal)
        await top_right.remove_children()

        top_right.border_title = to_mount.border_title
        await top_right.mount(to_mount)
        self.set_focus(to_mount)
        return None

    @on(RadioSet.Changed, "#unlockables")
    async def on_unlockables_radioset_changed(self, message: RadioSet.Changed) -> None:
        button_id = message.pressed.id
        if not button_id:
            return

        data: Achievement = getattr(self.save_file.unlockable_manager, button_id)
        to_mount = AchievementManageGrid(data)

        top_right = self.query_one("#top-right", Horizontal)
        for child in list(top_right.children):
            await child.remove()

        top_right.border_title = to_mount.border_title
        await top_right.mount(to_mount)
        self.refresh(layout=True)
        self.set_focus(to_mount)

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
