from typing import TYPE_CHECKING

from textual.containers import Grid, Horizontal
from textual.validation import Integer
from textual.widgets import Button, Input, SelectionList

if TYPE_CHECKING:
    from textual.app import ComposeResult


class AddGearGrid(Grid):
    def __init__(self, items: list[tuple[str, str]]) -> None:
        self._equipment_items = items
        super().__init__(id="add-gear-grid", classes="gear")
        self.border_title = "Add gear amounts"

    def compose(self) -> ComposeResult:
        yield SelectionList[str](*self._equipment_items, name="Set gear amount", id="add-gear-selection")
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
