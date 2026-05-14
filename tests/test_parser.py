import pathlib
from typing import Literal, TypedDict

from yurei.parser import PARSER

INPUTS_PATH = pathlib.Path(__file__).parent / "inputs"


class IntKeysExpected(TypedDict):
    __type: str
    values: dict[int, str]


class PlayedMapsExpected(TypedDict):
    __type: Literal[
        "System.Collections.Generic.Dictionary`2[[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral, "
        "PublicKeyToken=b77a5c561934e089],[System.Int32, mscorlib, Version=4.0.0.0, Culture=neutral,"
        "PublicKeyToken=b77a5c561934e089]],mscorlib"
    ]
    value: dict[int, int]


class TestParser:
    def test_int_keys(self) -> None:
        """A falsified simple version of the problem."""
        int_keys_input = INPUTS_PATH / "int_keys.es3"
        text = int_keys_input.read_text()

        parsed: IntKeysExpected = PARSER.parse(text)  # pyright: ignore[reportAssignmentType, reportUnknownMemberType] # lark types

        assert parsed["values"].get(1)
        assert parsed["__type"] == "dict[int, str]"

    def test_played_maps(self) -> None:
        """Pulled a literal example from a test save file."""
        played_maps_input = INPUTS_PATH / "playedMaps.es3"
        text = played_maps_input.read_text()

        parsed: dict[Literal["playedMaps"], PlayedMapsExpected] = PARSER.parse(text)  # pyright: ignore[reportAssignmentType, reportUnknownMemberType] # lark types

        assert parsed["playedMaps"]["value"].get(0)
        assert parsed["playedMaps"]["value"].get(12) == 6
