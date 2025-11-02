from typing import TYPE_CHECKING, cast

from textual import on
from textual.containers import Grid, Horizontal
from textual.validation import Integer
from textual.widgets import Button, Input, SelectionList

from yurei.enums import Equipment

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from yurei.tui.app import YureiApp


class AddGearGrid(Grid):
    app: YureiApp

    def __init__(self, items: list[tuple[str, str]]) -> None:
        self._equipment_items = items
        super().__init__(id="add-gear-grid", classes="gear")
        self.border_title = "Add gear amounts"

    def compose(self) -> ComposeResult:
        list_ = SelectionList[str](*self._equipment_items, name="Set gear amount", id="add-gear-selection")
        yield list_
        yield Horizontal(
            Input(
                placeholder="Amount?",
                id="add-gear-input",
                type="integer",
                validate_on=["blur", "submitted"],
                validators=[Integer(0, 50, failure_description="Gear amount must be between 0 and 50.")],
            ),
            Button(label="Submit", id="add-submit-button", variant="primary", name="Add Submit", flat=True),
            classes="input-row",
        )
        self.app.set_focus(list_)

    @on(Button.Pressed)
    async def on_submit(self, _: Button.Pressed) -> None:
        select = cast("SelectionList[str]", self.query_one("#add-gear-selection", SelectionList))
        amount = self.query_one("#add-gear-input", Input)
        for value in select.selected:
            self.app.save_file.add_equipment(item=Equipment(value), amount=int(amount.value))
        self.app.refresh_code_container()
        self.notify(f"Added {amount.value}x of {', '.join(select.selected)}")
