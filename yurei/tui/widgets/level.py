from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.validation import Integer
from textual.widgets import Input, Label

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from ..app import YureiApp  # noqa: TID252


class LevelGrid(Grid):
    app: YureiApp

    def __init__(self) -> None:
        super().__init__(id="level-prestige-grid", classes="two-col")
        self.border_title = "Alter your level/prestige"

    def compose(self) -> ComposeResult:
        yield Label("Prestige:", id="prestige-label")
        yield Input(
            placeholder=str(self.app.save_file.prestige),
            type="integer",
            validate_on=["blur", "submitted"],
            validators=[
                Integer(0, 100, "Level must be a minimum of 0 and maximum of 100"),
            ],
            id="level-prestige-input",
        )
        yield (Label("Level:", id="level-label"))
        yield Input(
            placeholder=str(self.app.save_file.level),
            type="integer",
            validate_on=["submitted", "blur"],
            validators=[
                Integer(0, 100, failure_description="Prestige cannot be lower than 0 or higher than 100."),
            ],
            id="level-level-input",
        )
