from typing import TYPE_CHECKING, Literal, Self, final

if TYPE_CHECKING:
    from .save import Save
    from .types_.inner_types import Int

__all__ = ("Achievement", "UnlockableManager")

type CURRENT_UNLOCKABLES = Literal[
    "farmhouse_fieldwork",
    "lighthouse_ferrymen",
    "lighthouse_keeper",
    "ranger_challenge",
    "sunny_meadows_survival",
    "nells_diner",
    "moneybags",
    "ghost_in_the_machine",
    "tanglewood",
    "alan_wake",
]
type CURRENT_UNLOCKABLES_DATA_KEY = Literal[
    "FarmhouseFieldwork",
    "lighthouseFerrymen",
    "dinerGhostInTheMachine",
    "lighthouseKeeper",
    "rangerChallenge",
    "sunnyMeadowsSurvival",
    "NellsDiner",
    "Moneybags",
    "Tanglewood",
    "AWNurseryRhymePuzzle",
]
LOOKUP: dict[str, CURRENT_UNLOCKABLES] = {
    "Farmhouse Fieldwork": "farmhouse_fieldwork",
    "Lighthouse Ferrymen": "lighthouse_ferrymen",
    "Lighthouse Keeper": "lighthouse_keeper",
    "Ranger Challenge": "ranger_challenge",
    "Sunny Meadows Survival": "sunny_meadows_survival",
    "Nell's Diner": "nells_diner",
    "Moneybags": "moneybags",
    "Tanglewood": "tanglewood",
    "Alan Wake Nursery Rhyme": "alan_wake",
}
REVERSE_LOOKUP: dict[CURRENT_UNLOCKABLES, str] = {v: k for k, v in LOOKUP.items()}
DATA_KEY_TO_PRETTY_LOOKUP: dict[CURRENT_UNLOCKABLES_DATA_KEY, str] = {
    "FarmhouseFieldwork": "Farmhouse Fieldwork",
    "lighthouseFerrymen": "Lighthouse Ferrymen",
    "lighthouseKeeper": "Lighthouse Keeper",
    "rangerChallenge": "Ranger Challenge",
    "sunnyMeadowsSurvival": "Sunny Meadows Survival",
    "dinerGhostInTheMachine": "Ghost in the Machine",
    "NellsDiner": "Nell's Diner",
    "Moneybags": "Moneybags",
    "Tanglewood": "Tanglewood",
    "AWNurseryRhymePuzzle": "Alan Wake Nursery Rhyme Puzzle",
}
DATA_KEY_TO_ATTRIBUTE_LOOKUP: dict[CURRENT_UNLOCKABLES_DATA_KEY, CURRENT_UNLOCKABLES] = {
    "FarmhouseFieldwork": "farmhouse_fieldwork",
    "lighthouseFerrymen": "lighthouse_ferrymen",
    "lighthouseKeeper": "lighthouse_keeper",
    "rangerChallenge": "ranger_challenge",
    "sunnyMeadowsSurvival": "sunny_meadows_survival",
    "NellsDiner": "nells_diner",
    "dinerGhostInTheMachine": "ghost_in_the_machine",
    "Moneybags": "moneybags",
    "Tanglewood": "tanglewood",
    "AWNurseryRhymePuzzle": "alan_wake",
}


class Achievement:
    __slots__ = ("_completed", "_progression", "_received", "max_progression_value", "name", "no_progression_count")

    def __init__(
        self,
        name: CURRENT_UNLOCKABLES_DATA_KEY,
        /,
        *,
        completed: int | bool,
        progression: int,
        received: int | bool,
        no_progression_count: bool = False,
        max_progression_value: int = 50,
    ) -> None:
        self.name: CURRENT_UNLOCKABLES_DATA_KEY = name
        self._completed = int(completed)
        self._received = int(received)
        self._progression = progression
        self.no_progression_count = no_progression_count
        self.max_progression_value = max_progression_value

    def __repr__(self) -> str:
        return (
            f"<Achievement {self.pretty_name} completed={self.completed} "
            f"received={self.received} progression={self.progression}>"
        )

    @classmethod
    def from_alan_wake(cls, progress: int) -> Self:
        completed = progress == 3
        return cls(
            "AWNurseryRhymePuzzle", completed=completed, progression=progress, received=False, max_progression_value=3
        )

    @property
    def _alan_wake(self) -> bool:
        return self.name == "AWNurseryRhymePuzzle"

    @property
    def pretty_name(self) -> str:
        return DATA_KEY_TO_PRETTY_LOOKUP[self.name]

    @property
    def attribute_name(self) -> CURRENT_UNLOCKABLES:
        return DATA_KEY_TO_ATTRIBUTE_LOOKUP[self.name]

    @property
    def completed(self) -> bool:
        if self._alan_wake:
            return self._progression == 3
        return bool(self._completed)

    @completed.setter
    def completed(self, value: bool | int) -> None:
        if self._alan_wake:
            self._progression = 3
        self._completed = int(value)

    @property
    def received(self) -> bool:
        return bool(self._received)

    @received.setter
    def received(self, value: bool | int) -> None:
        self._received = int(value)

    @property
    def progression(self) -> bool | int:
        if self._alan_wake:
            return self._progression
        return bool(self._progression) if self.no_progression_count else self._progression

    @progression.setter
    def progression(self, value: bool | int) -> None:
        if self.no_progression_count:
            self._progression = int(bool(value))
        else:
            self._progression = int(value)

    def to_data(self) -> dict[str, Int]:
        if self.name == "AWNurseryRhymePuzzle":
            return {f"{self.name}Progress": {"__type": "int", "value": int(self.progression)}}

        return {
            f"{self.name}Completed": {"__type": "int", "value": self._completed},
            f"{self.name}Received": {"__type": "int", "value": self._received},
            f"{self.name}Progression": {"__type": "int", "value": int(self.progression)},
        }


@final
class UnlockableManager:
    __slots__ = (
        "_save",
        "alan_wake",
        "farmhouse_fieldwork",
        "ghost_in_the_machine",
        "lighthouse_ferrymen",
        "lighthouse_keeper",
        "moneybags",
        "nells_diner",
        "ranger_challenge",
        "sunny_meadows_survival",
        "tanglewood",
    )

    def __init__(self, save: Save, /) -> None:
        self._save = save
        self.farmhouse_fieldwork = Achievement(
            "FarmhouseFieldwork",
            completed=save.get_value("FarmhouseFieldworkCompleted", int, default=0),
            progression=save.get_value("FarmhouseFieldworkProgression", int, default=0),
            received=save.get_value("FarmhouseFieldworkReceived", int, default=0),
        )
        self.lighthouse_ferrymen = Achievement(
            "lighthouseFerrymen",
            completed=save.get_value("lighthouseFerrymenCompleted", int, default=0),
            progression=save.get_value("lighthouseFerrymenProgression", int, default=0),
            received=save.get_value("lighthouseFerrymenReceived", int, default=0),
            no_progression_count=True,
        )
        self.lighthouse_keeper = Achievement(
            "lighthouseKeeper",
            completed=save.get_value("lighthouseKeeperCompleted", int, default=0),
            progression=save.get_value("lighthouseKeeperProgression", int, default=0),
            received=save.get_value("lighthouseKeeperReceived", int, default=0),
        )
        self.ranger_challenge = Achievement(
            "rangerChallenge",
            completed=save.get_value("rangerChallengeCompleted", int, default=0),
            progression=save.get_value("rangerChallengeProgression", int, default=0),
            received=save.get_value("rangerChallengeReceived", int, default=0),
        )
        self.sunny_meadows_survival = Achievement(
            "sunnyMeadowsSurvival",
            completed=save.get_value("sunnyMeadowsSurvivalCompleted", int, default=0),
            progression=save.get_value("sunnyMeadowsSurvivalProgression", int, default=0),
            received=save.get_value("sunnyMeadowsSurvivalReceived", int, default=0),
        )
        self.nells_diner = Achievement(
            "NellsDiner",
            completed=save.get_value("NellsDinerCompleted", int, default=0),
            progression=save.get_value("NellsDinerProgression", int, default=0),
            received=save.get_value("NellsDinerReceived", int, default=0),
        )
        self.ghost_in_the_machine = Achievement(
            "dinerGhostInTheMachine",
            completed=save.get_value("dinerGhostInTheMachineCompleted", int, default=0),
            progression=save.get_value("dinerGhostInTheMachineProgression", int, default=0),
            received=save.get_value("dinerGhostInTheMachineReceived", int, default=0),
        )
        self.moneybags = Achievement(
            "Moneybags",
            completed=save.get_value("MoneybagsCompleted", int, default=0),
            progression=save.get_value("MoneybagsProgression", int, default=0),
            received=save.get_value("MoneybagsReceived", int, default=0),
        )
        self.tanglewood = Achievement(
            "Tanglewood",
            completed=save.get_value("TanglewoodCompleted", int, default=0),
            progression=save.get_value("TanglewoodProgression", int, default=0),
            received=save.get_value("TanglewoodReceived", int, default=0),
            max_progression_value=50,
        )
        self.alan_wake = Achievement.from_alan_wake(save.get_value("AWNurseryRhymePuzzleProgress", int, default=0))

    def __contains__(self, key: str, /) -> bool:
        return hasattr(self, key)

    def __bool__(self) -> bool:
        return any(hasattr(self, key) for key in self.__slots__ if not key.startswith("_"))

    def get_handler(self, key: CURRENT_UNLOCKABLES) -> Achievement:
        return getattr(self, key)
