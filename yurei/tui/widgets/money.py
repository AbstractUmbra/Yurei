from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.validation import Integer
from textual.widgets import Input, Label

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from ..app import YureiApp  # noqa: TID252


class MoneyGrid(Grid):
    app: YureiApp

    def __init__(self) -> None:
        super().__init__(id="money-scroll", classes="two-col")

    def compose(self) -> ComposeResult:
        yield Label("Money:", id="money-label")
        yield Input(
            placeholder=f"{self.app.save_file.money}",
            type="integer",
            validate_on=["submitted", "blur"],
            validators=[Integer(0, 249999, "must be between 0 and 249,999")],
            id="money-value",
        )
