from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from .colour import Colour
    from .difficulty import Difficulty

__all__ = ("Bool", "ColourValue", "DifficultyValue", "Float", "Int", "String")


class String(TypedDict):
    __type: Literal["string"]
    value: str


class Int(TypedDict):
    __type: Literal["int"]
    value: int


class Float(TypedDict):
    __type: Literal["float"]
    value: float


class Bool(TypedDict):
    __type: Literal["bool"]
    value: bool


class ColourValue(TypedDict):
    __type: Literal["Color"]
    value: Colour


class DifficultyValue(TypedDict):
    __type: Literal["Difficulty,Assembly-CSharp"]
    value: Difficulty


class SpecialPlayedMaps(TypedDict):
    __type: str
    value: dict[str, int]
