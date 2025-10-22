from typing import TYPE_CHECKING

from textual.containers import Grid, Horizontal
from textual.widgets import Button, Select, SelectionList

if TYPE_CHECKING:
    from textual.app import ComposeResult


class UnlockGearGrid(Grid):
    def __init__(self, items: list[tuple[str, str]]) -> None:
        self._equipment_items = items
        super().__init__(id="unlock-gear-grid", classes="gear")

    def compose(self) -> ComposeResult:
        yield SelectionList[str](*self._equipment_items, name="Unlock gear tier", id="unlock-gear-selection")
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
