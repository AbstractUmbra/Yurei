import datetime
import logging
import pathlib
from typing import TYPE_CHECKING, Any, Final, Literal, Self, cast

from .crypt import decrypt, encrypt
from .data import XPLevel
from .enums import Equipment
from .types_.save import Save as SaveType
from .unlockable import UnlockableManager
from .utils import MISSING, from_json, get_save_password, resolve_save_path, to_json

if TYPE_CHECKING:
    from types import TracebackType

    from .unlockable import CURRENT_UNLOCKABLES, Achievement

__all__ = ("Save",)

TEMP_FILE = pathlib.Path(__file__).parent.parent / ("./_previously_decrypted_file.json")
LOGGER = logging.getLogger(__name__)
EQUIPMENT: set[str] = {e.value for e in Equipment}
EQUIPMENT_TIER_LOOKUP: dict[int, str] = {1: "One", 2: "Two", 3: "Three"}
CURRENT_SAVE_KEY = get_save_password(password_file=(pathlib.Path(__file__).parent.parent / "resources" / "save_password"))
LEVEL_SCALES_FILE = pathlib.Path(__file__).parent.parent / "resources" / "levelscaling.json"


class Save:
    TUI_ALLOWED_OPERATIONS: Final[set[tuple[str, str]]] = {
        ("Unlock Gear", "unlock-gear"),
        ("Add Gear", "add-gear"),
        ("Edit Money", "edit-money"),
        ("Alter Prestige/Level", "alter-level"),
        ("Manage Unlockables", "manage-unlockables"),
    }

    __slots__ = ("_create_backup", "_data", "_written", "save_path", "unlockable_manager", "xp_manager")

    def __init__(self, *, data: SaveType, path: pathlib.Path, create_backup: bool = True) -> None:
        self._data: SaveType = data
        self.unlockable_manager = UnlockableManager(self)
        self.xp_manager = XPLevel.from_file(LEVEL_SCALES_FILE)
        self.save_path = path
        self._create_backup = create_backup
        self._written: bool = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if not self._written and not exc_type:
            self.write()

    def __contains__(self, key: str) -> bool:
        return self._has_value(key)

    def __getitem__(self, key: str) -> Any:
        return self.get_value(key)

    def _reload(self) -> None:
        self.unlockable_manager = UnlockableManager(self)
        self._written = False

    @classmethod
    def from_path(cls, path: pathlib.Path, *, create_backup: bool = True) -> Self:
        data = path.read_bytes()

        return cls(
            data=decrypt(data=data, password=CURRENT_SAVE_KEY, return_type=SaveType), path=path, create_backup=create_backup
        )

    @classmethod
    def from_default_path(cls, *, create_backup: bool = True) -> Self:
        path = resolve_save_path()

        return cls(
            data=decrypt(path=path, password=CURRENT_SAVE_KEY, return_type=SaveType), path=path, create_backup=create_backup
        )

    def create_backup(self) -> pathlib.Path:
        now = datetime.datetime.now(datetime.UTC)
        now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = self.save_path.with_stem(self.save_path.name + f"-{now_str}").with_suffix(".bak")
        if backup_path.exists():
            backup_path.unlink(missing_ok=True)

        LOGGER.info("Creating backup at %r", str(backup_path))
        return self.save_path.copy(backup_path)

    def _has_value(self, key: str) -> bool:
        return key in self._data

    def get_value[T: Any = Any](self, key: str, _: type[T] = MISSING, *, default: T = MISSING) -> T:
        if default is not MISSING:
            return cast("T", self._data.get(key, {}).get("value", default))
        return cast("T", self._data[key]["value"])

    @property
    def level(self) -> int:
        if self.prestige >= 1:
            return self._data["NewLevel"]["value"]
        return self._data["Level"]["value"]

    @level.setter
    def level(self, value: int) -> None:
        LOGGER.info("Setting level to %s", value)
        self._data["Experience"]["value"] = 0

        if self.prestige >= 1:
            self._data["NewLevel"]["value"] = value
        else:
            self._data["Level"]["value"] = 100
            self._data["NewLevel"]["value"] = value

    @property
    def prestige(self) -> int:
        return self._data.get("Prestige", {}).get("value", 0)

    @prestige.setter
    def prestige(self, value: int) -> None:
        LOGGER.info("Setting prestige to %s", value)
        if value == 0:
            self._data.pop("Prestige", 0)
            self._data.pop("PrestigeIndex", 0)
        else:
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

    def has_unlockable_(self, name: str) -> bool:
        keys = [f"{name}{progress}" for progress in ["Completed", "Progression", "Received"]]

        return any(key in self._data for key in keys)

    def manage_unlockable(self, unlockable: CURRENT_UNLOCKABLES) -> Achievement:
        return getattr(self.unlockable_manager, unlockable)

    def to_json_string(self) -> str:
        return to_json(self._data)

    def from_json_string(self, input_: str, /) -> None:
        self._data = from_json(input_)

    def _merge_unlockables(self) -> None:
        for attr in self.unlockable_manager.__slots__:
            if attr.startswith("_") or attr not in self.unlockable_manager:
                continue

            unlockable = self.unlockable_manager.get_handler(attr)  # pyright: ignore[reportArgumentType] # our slots are the literal
            unlockable_data = unlockable.to_data()
            LOGGER.info("UNLOCKABLE: Merging %r", str(unlockable_data))
            self._data.update(unlockable_data)  # pyright: ignore[reportArgumentType, reportCallIssue] # our keys match but we can't narrow, alas

    def write(self) -> pathlib.Path:
        from . import CURRENT_SAVE_KEY  # noqa: PLC0415 # cyclic circumvention

        # merge unlockables
        self._merge_unlockables()

        decrypted = to_json(self._data).encode()
        with TEMP_FILE.open("wb") as fp:
            fp.write(decrypted)

        encrypted = encrypt(data=decrypted, password=CURRENT_SAVE_KEY)

        self.create_backup()

        with self.save_path.open("wb") as fp:
            fp.write(encrypted)

        self._written = True
        LOGGER.info("Written to %s", self.save_path.absolute())
        return self.save_path
