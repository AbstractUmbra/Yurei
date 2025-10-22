from typing import TYPE_CHECKING

from textual import on
from textual.containers import Grid, VerticalScroll
from textual.css.query import NoMatches
from textual.validation import Integer
from textual.widgets import Button, Checkbox, Input, RadioButton, RadioSet, Static

from yurei.unlockable import LOOKUP

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from yurei.tui.app import YureiApp
    from yurei.unlockable import Achievement


class UnlockablePane(VerticalScroll):
    app: YureiApp

    def __init__(self, id_: str, /, *, radio_set_id: str) -> None:
        super().__init__(
            RadioSet(*[RadioButton(k, id=v) for k, v in LOOKUP.items()], id=radio_set_id),
            Button("Back", variant="default", name="back-button", id="unlockables-back-button", flat=True),
            id=id_,
        )
        self.border_title = "Unlockables"
        self.border_subtitle = "Achievements and Easter Eggs"

    @on(Button.Pressed, "#unlockables-back-button")
    async def revert_to_primary_screen(self) -> None:
        return await self.app.file_selected(self.app.save_file.save_path)


class AchievementManageGrid(Grid):
    app: YureiApp

    DEFAULT_CSS = """
    #achievement-manager-grid {
        grid-size: 1 4;          /* 1 column, 4 rows */
        grid-rows: auto auto auto 1fr; /* Last row stretches */
        height: 100%;
        width: 100%;
    }

    #achievement-manager-grid .grid-row {
        /* margin-bottom: 0;   /* or 1, 2, 3px etc. */
        margin-left: 1;
        padding-left: 1;
    }

    #achievement-manager-grid Checkbox {
        background: $surface;
    }

    #achievement-submit-button {
        dock: bottom;
        align-horizontal: left;
        margin-left: 1;
    }
    """

    def __init__(self, achievement: Achievement) -> None:
        self.achievement = achievement
        super().__init__(id="achievement-manager-grid", classes="unlockables")
        self.border_title = "Details"

    def compose(self) -> ComposeResult:
        yield Checkbox(
            "Completed?", value=self.achievement.completed, id="achievement-manager-completed", classes="grid-row"
        )
        yield Checkbox(
            "Recieved reward?", value=self.achievement.received, id="achievement-manager-received", classes="grid-row"
        )
        if not self.achievement.no_progression_count:
            yield Input(
                value=str(self.achievement.progression),
                placeholder="0-50",
                validate_on=["blur", "submitted"],
                validators=[Integer(0, 50, failure_description="The progression value must be between 0 and 50.")],
                type="integer",
                name="Progression value",
                tooltip="The amount of progress towards this unlockable",
                id="achievement-manager-progression",
                classes="grid-row",
            )
        else:
            yield Static(id="achievement-manager-progression-spacer", classes="grid-row")

        yield Button(
            label="Submit",
            id="achievement-submit-button",
            variant="primary",
            name="Submit Achievement",
            flat=True,
        )

    def process_progression_input(self, progression: Input) -> bool:
        result = progression.validate(progression.value)
        if not result or result.is_valid:
            self.achievement.progression = int(progression.value)
            return True
        self.notify(
            f"Unable to submit the value {progression.value!r}\n{', '.join(result.failure_descriptions)}",
            title="Error!",
            severity="error",
            timeout=3.0,
        )
        return False

    @on(Button.Pressed, "#achievement-submit-button")
    async def submit(self, _: Button.Pressed) -> None:
        completed = self.query_one("#achievement-manager-completed", Checkbox)
        received = self.query_one("#achievement-manager-received", Checkbox)
        try:
            progression = self.query_one("#achievement-manager-progression", Input)
        except NoMatches:
            progression = None

        if progression:
            self.process_progression_input(progression)
        if completed.value:
            self.achievement.completed = True
            self.achievement.progression = (
                True if self.achievement.no_progression_count else self.achievement.MAX_PROGRESSION_VALUE
            )
        if received.value:
            self.achievement.received = True

        setattr(self.app.save_file.unlockable_manager, self.achievement.attribute_name, self.achievement)
        self.app.notify(f"Submitted achievement info for {self.achievement.pretty_name}", title="Success!", timeout=3.0)
