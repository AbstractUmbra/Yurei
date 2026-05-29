import pathlib
from typing import Literal, TypedDict

from yurei.parser import PARSER, DictEntry, ES3Dictionary
from yurei.serializer import ES3Serializer

INPUTS_PATH = pathlib.Path(__file__).parent / "inputs"


def _strip(inp_: str) -> str:
    return inp_.replace("\n", "").replace(" ", "")


class KeyType(TypedDict):
    low: int
    high: int


class ValueType(TypedDict):
    guid: dict[Literal["value"], str]
    materialOption: int


class PlayerItemsInner(TypedDict):
    Items: ES3Dictionary[KeyType, ValueType]


class PlayerItemsType(TypedDict):
    __type: Literal["PlayerOutfit,Assembly-CSharp"]
    value: PlayerItemsInner


class TestSerializer:
    def test_serialize(self) -> None:
        player_item_input = INPUTS_PATH / "player_items.es3"
        text = player_item_input.read_text()

        parsed: dict[Literal["LocalPlayerOutfit"], PlayerItemsType] = PARSER.parse(text)  # pyright: ignore[reportAssignmentType, reportUnknownMemberType] # lark types

        primary_key = parsed["LocalPlayerOutfit"]["value"]

        items = primary_key["Items"]

        assert isinstance(items, ES3Dictionary)
        assert isinstance(items.entries[0], DictEntry)

        for entry in items.entries:
            assert entry.key.get("low") is not None
            assert entry.key.get("high") is not None

            assert entry.value.get("guid") is not None
            assert entry.value.get("materialOption") is not None

        serialized = ES3Serializer().dumps(parsed)
        assert serialized == _strip(text)
