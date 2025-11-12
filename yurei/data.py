from math import floor
from typing import TYPE_CHECKING, Self, TypedDict

from .utils import from_json

if TYPE_CHECKING:
    import pathlib


class Scale(TypedDict):
    to_next: int
    cumulative: int


__all__ = ("XPLevel",)


class XPLevel:
    __slots__ = ("data",)

    def __init__(self, data: dict[str, Scale]) -> None:
        self.data = {int(k): v for k, v in data.items()}

    @classmethod
    def from_file(cls, file: pathlib.Path, /) -> Self:
        data = file.read_text(encoding="utf-8")
        return cls(from_json(data))

    def _get_cum(self, level: int) -> int:
        if 101 <= level <= 999:
            return 283432 + 4971 * (level - 100)
        if level >= 999:
            return floor(4468929 + 100 * ((level - 100) ** 1.73))
        return 100 * ((level - 1) ** 1.73)

    def __getitem__(self, key: str | int) -> Scale:
        key = int(key)

        if key > 9999:
            raise ValueError("Levels above 9,999 are not possible.")

        if 9999 > key >= 999:
            return {"to_next": 4971, "cumulative": self._get_cum(key)}
        return self.data[key]

    def __getattribute__(self, name: str) -> Scale:
        return self.__getitem__(name)
