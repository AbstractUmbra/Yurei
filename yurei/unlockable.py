from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .save import Save
    from .types_.inner_types import Int

__all__ = ("Achievement", "UnlockableManager")

type CURRENT_UNLOCKABLES = Literal[
    "farmhouse_fieldwork", "lighthouse_ferrymen", "lighthouse_keeper", "ranger_challenge", "sunny_meadows_survival"
]
type CURRENT_UNLOCKABLES_DATA_KEY = Literal[
    "FarmhouseFieldwork", "lighthouseFerrymen", "lighthouseKeeper", "rangerChallenge", "sunnyMeadowsSurvival"
]
LOOKUP: dict[str, CURRENT_UNLOCKABLES] = {
    "Farmhouse Fieldwork": "farmhouse_fieldwork",
    "Lighthouse Ferrymen": "lighthouse_ferrymen",
    "Lighthouse Keeper": "lighthouse_keeper",
    "Ranger Challenge": "ranger_challenge",
    "Sunny Meadows Survival": "sunny_meadows_survival",
}
REVERSE_LOOKUP: dict[CURRENT_UNLOCKABLES, str] = {v: k for k, v in LOOKUP.items()}
DATA_KEY_TO_PRETTY_LOOKUP: dict[CURRENT_UNLOCKABLES_DATA_KEY, str] = {
    "FarmhouseFieldwork": "Farmhouse Fieldwork",
    "lighthouseFerrymen": "Lighthouse Ferrymen",
    "lighthouseKeeper": "Lighthouse Keeper",
    "rangerChallenge": "Ranger Challenge",
    "sunnyMeadowsSurvival": "Sunny Meadows Survival",
}
DATA_KEY_TO_ATTRIBUTE_LOOKUP: dict[CURRENT_UNLOCKABLES_DATA_KEY, CURRENT_UNLOCKABLES] = {
    "FarmhouseFieldwork": "farmhouse_fieldwork",
    "lighthouseFerrymen": "lighthouse_ferrymen",
    "lighthouseKeeper": "lighthouse_keeper",
    "rangerChallenge": "ranger_challenge",
    "sunnyMeadowsSurvival": "sunny_meadows_survival",
}


class Achievement:
    MAX_PROGRESSION_VALUE: int = 50
    __slots__ = ("_completed", "_progression", "_received", "name", "no_progression_count")

    def __init__(
        self,
        name: CURRENT_UNLOCKABLES_DATA_KEY,
        /,
        *,
        completed: int | bool,
        progression: int,
        received: int | bool,
        no_progression_count: bool = False,
        max_progression_value: int | None = None,
    ) -> None:
        self.name: CURRENT_UNLOCKABLES_DATA_KEY = name
        self._completed = int(completed)
        self._received = int(received)
        self._progression = progression
        self.no_progression_count = no_progression_count
        if max_progression_value:
            self.__class__.MAX_PROGRESSION_VALUE = max_progression_value

    @property
    def pretty_name(self) -> str:
        return DATA_KEY_TO_PRETTY_LOOKUP[self.name]

    @property
    def attribute_name(self) -> CURRENT_UNLOCKABLES:
        return DATA_KEY_TO_ATTRIBUTE_LOOKUP[self.name]

    @property
    def completed(self) -> bool:
        return bool(self._completed)

    @completed.setter
    def completed(self, value: bool | int) -> None:
        self._completed = int(value)

    @property
    def received(self) -> bool:
        return bool(self._received)

    @received.setter
    def received(self, value: bool | int) -> None:
        self._received = int(value)

    @property
    def progression(self) -> bool | int:
        return bool(self._progression) if self.no_progression_count else self._progression

    @progression.setter
    def progression(self, value: bool | int) -> None:
        if self.no_progression_count:
            self._progression = int(bool(value))
        else:
            self._progression = int(value)

    def to_data(self) -> dict[str, Int]:
        return {
            f"{self.name}Completed": {"__type": "int", "value": self._completed},
            f"{self.name}Received": {"__type": "int", "value": self._received},
            f"{self.name}Progression": {"__type": "int", "value": self.progression},
        }


class UnlockableManager:
    __slots__ = (
        "farmhouse_fieldwork",
        "lighthouse_ferrymen",
        "lighthouse_keeper",
        "ranger_challenge",
        "save",
        "sunny_meadows_survival",
    )

    def __init__(self, save: Save, /) -> None:
        self.save = save
        self.farmhouse_fieldwork = Achievement(
            "FarmhouseFieldwork",
            completed=save.get_value("FarmhouseFieldworkCompleted", int),
            progression=save.get_value("FarmhouseFieldworkProgression", int),
            received=save.get_value("FarmhouseFieldworkReceived", int),
        )
        self.lighthouse_ferrymen = Achievement(
            "lighthouseFerrymen",
            completed=save.get_value("lighthouseFerrymenCompleted", int),
            progression=save.get_value("lighthouseFerrymenProgression", int),
            received=save.get_value("lighthouseFerrymenReceived", int),
            no_progression_count=True,
        )
        self.lighthouse_keeper = Achievement(
            "lighthouseKeeper",
            completed=save.get_value("lighthouseKeeperCompleted", int),
            progression=save.get_value("lighthouseKeeperProgression", int),
            received=save.get_value("lighthouseKeeperReceived", int),
        )
        self.ranger_challenge = Achievement(
            "rangerChallenge",
            completed=save.get_value("rangerChallengeCompleted", int),
            progression=save.get_value("rangerChallengeProgression", int),
            received=save.get_value("rangerChallengeReceived", int),
        )
        self.sunny_meadows_survival = Achievement(
            "sunnyMeadowsSurvival",
            completed=save.get_value("sunnyMeadowsSurvivalCompleted", int),
            progression=save.get_value("sunnyMeadowsSurvivalProgression", int),
            received=save.get_value("sunnyMeadowsSurvivalReceived", int),
        )

    def get_handler(self, key: CURRENT_UNLOCKABLES) -> Achievement:
        return getattr(self, key)
