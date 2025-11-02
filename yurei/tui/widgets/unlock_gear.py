from typing import TYPE_CHECKING, Literal, cast

from textual import on
from textual.containers import Grid, Horizontal
from textual.widgets import Button, Select, SelectionList

from yurei.enums import Equipment
from yurei.utils import human_join

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from yurei.tui.app import YureiApp


class UnlockGearGrid(Grid):
    app: YureiApp

    def __init__(self, items: list[tuple[str, str]]) -> None:
        self._equipment_items = items
        super().__init__(id="unlock-gear-grid", classes="gear")
        self.border_title = "Unlock gear and alter tiers"

    def compose(self) -> ComposeResult:
        list_ = SelectionList[str](*self._equipment_items, name="Unlock gear tier", id="unlock-gear-selection")
        yield list_
        yield (
            Horizontal(
                Select[int](
                    [("One", 1), ("Two", 2), ("Three", 3)],
                    id="unlock-gear-tier",
                    prompt="Tier",
                    allow_blank=False,
                ),
                Button(
                    label="Submit",
                    id="unlock-submit-button",
                    variant="primary",
                    name="Unlock Submit",
                    flat=True,
                ),
                classes="input-row",
            )
        )
        self.app.set_focus(list_)

    @on(Button.Pressed)
    async def on_submit(self, _: Button.Pressed) -> None:
        select = cast("SelectionList[str]", self.query_one("#unlock-gear-selection", SelectionList))
        tier = cast("Select[Literal[1,2,3]]", self.query_one("#unlock-gear-tier", Select))
        if not tier.selection:
            self.notify(
                "An equipment tier must be selected before trying to submit gear unlocks!",
                title="Error",
                severity="error",
                timeout=3.0,
            )
            return
        for value in select.selected:
            self.app.save_file.unlock_equipment(item=Equipment(value), tier=tier.selection)

        self.app.refresh_code_container()
        self.notify(f"Unlocked {human_join(select.selected)} at tier {tier.selection}.")
