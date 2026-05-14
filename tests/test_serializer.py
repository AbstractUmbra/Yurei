import pathlib
from typing import Any

from yurei.parser import PARSER, DictEntry, ES3Dictionary
from yurei.serializer import ES3Serializer

INPUTS_PATH = pathlib.Path(__file__).parent / "inputs"


def _strip(inp_: str) -> str:
    return inp_.replace("\n", "").replace(" ", "")


class TestSerializer:
    def test_serialize(self) -> None:
        player_item_input = INPUTS_PATH / "player_items.es3"
        text = player_item_input.read_text()

        parsed: dict[Any, Any] = PARSER.parse(text)  # pyright: ignore[reportAssignmentType, reportUnknownMemberType] # lark types
        # we accept the loss of types here because Python's type system can't make a dict-type complex enough

        primary_key = parsed["LocalPlayerOutfit"]["value"]

        assert isinstance(primary_key["Items"], ES3Dictionary)
        assert isinstance(primary_key["Items"].entries[0], DictEntry)

        serialized = ES3Serializer().dumps(parsed)
        assert serialized == _strip(text)
