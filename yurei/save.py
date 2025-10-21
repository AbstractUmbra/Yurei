import logging
import pathlib
from typing import TYPE_CHECKING, ClassVar, Literal, Self

from .crypt import decrypt, encrypt
from .enums import Equipment
from .utils import resolve_save_path, to_json

if TYPE_CHECKING:
    from types import TracebackType

    from .types_.save import Save as SaveType

__all__ = ("Save",)

TEMP_FILE = pathlib.Path(__file__).parent.parent / ("./_previously_decrypted_file.json")
LOGGER = logging.getLogger(__name__)
EQUIPMENT: set[str] = {e.value for e in Equipment}
EQUIPMENT_TIER_LOOKUP: dict[int, str] = {1: "One", 2: "Two", 3: "Three"}


class Save:
    TUI_ALLOWED_OPERATIONS: ClassVar[set[tuple[str, str]]] = {
        ("Unlock Gear", "unlock-gear"),
        ("Add Gear", "add-gear"),
        ("Edit Money", "edit-money"),
        ("Alter Prestige/Level", "alter-level"),
    }

    def __init__(self, *, data: SaveType, path: pathlib.Path) -> None:
        self._data = data
        self.save_path = path
        self._written: bool = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if not self._written and not exc_type:
            self.write()

    @classmethod
    def from_path(cls, path: pathlib.Path) -> Self:
        data = path.read_bytes()
        from . import CURRENT_SAVE_KEY  # noqa: PLC0415 # cyclic circumvention

        return cls(data=decrypt(data=data, password=CURRENT_SAVE_KEY), path=path)

    @classmethod
    def from_default_path(cls) -> Self:
        path = resolve_save_path()
        from . import CURRENT_SAVE_KEY  # noqa: PLC0415 # cyclic circumvention

        return cls(data=decrypt(path=path, password=CURRENT_SAVE_KEY), path=path)

    def create_backup(self) -> pathlib.Path:
        backup_path = self.save_path.with_suffix(".txt.bak")
        if backup_path.exists():
            backup_path.unlink(missing_ok=True)

        return self.save_path.copy(backup_path)

    @property
    def level(self) -> int:
        if self.prestige > 0:
            return self._data["NewLevel"]["value"]
        return self._data["Level"]["value"]

    @level.setter
    def level(self, value: int) -> None:
        LOGGER.info("Setting level to %s", value)
        if self.prestige > 0:
            self._data["NewLevel"]["value"] = value
            self._data["Level"]["value"] = 100
        else:
            self._data["Level"]["value"] = value

    @property
    def prestige(self) -> int:
        return self._data["Prestige"]["value"]

    @prestige.setter
    def prestige(self, value: int) -> None:
        LOGGER.info("Setting prestige to %s", value)
        self._data["Prestige"]["value"] = value
        self._data["PrestigeIndex"]["value"] = value

    @property
    def money(self) -> int:
        return self._data["PlayersMoney"]["value"]

    @money.setter
    def money(self, value: int) -> None:
        LOGGER.info("Setting money to %s", value)
        self._data["PlayersMoney"]["value"] = value

    def _do_unlock(self, *, formatted_string: str, bulk: bool) -> None:
        LOGGER.info("%sUnlocking %r", "BULK: " if bulk else "", formatted_string)
        self._data[formatted_string]["value"] = True

    def unlock_equipment(self, *, item: Equipment | None = None, tier: Literal[1, 2, 3]) -> None:
        fmt = EQUIPMENT_TIER_LOOKUP[tier]
        tier_str = f"Tier{fmt}UnlockOwned"
        if item:
            to_unlock = f"{item.value}{tier_str}"
            self._do_unlock(formatted_string=to_unlock, bulk=False)
            return

        for equipment in EQUIPMENT:
            to_unlock = f"{equipment}{tier_str}"
            self._do_unlock(formatted_string=to_unlock, bulk=True)

    def _do_add_equipment(self, item: str, amount: int, *, bulk: bool) -> None:
        LOGGER.info("%sAdding %sx %r", "BULK: " if bulk else "", item, amount)
        self._data[item + "Inventory"]["value"] = amount

    def add_equipment(self, *, item: Equipment | None = None, amount: int) -> None:
        if item:
            self._do_add_equipment(item, amount, bulk=False)
            return
        for equipment in EQUIPMENT:
            self._do_add_equipment(equipment, amount, bulk=True)

    def to_json_string(self) -> str:
        return to_json(self._data)

    def write(self) -> pathlib.Path:
        from . import CURRENT_SAVE_KEY  # noqa: PLC0415 # cyclic circumvention

        decrypted = to_json(self._data).encode()
        with TEMP_FILE.open("wb") as fp:
            fp.write(decrypted)

        encrypted = encrypt(data=decrypted, password=CURRENT_SAVE_KEY)

        with self.save_path.open("wb") as fp:
            fp.write(encrypted)

        self._written = True
        LOGGER.info("Written to %s", self.save_path.absolute())
        return self.save_path
