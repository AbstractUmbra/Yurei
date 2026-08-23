import pathlib
from dataclasses import dataclass
from typing import Any, Literal

from lark import Lark, Token, Transformer, v_args  # pyright: ignore[reportUnknownVariableType] # lark types aren't complete

type JSONValue = str | int | float | bool | list[JSONValue] | dict[str, JSONValue] | None
type ES3Value = str | int | float | bool | list[ES3Value] | dict[str, ES3Value] | ES3Dictionary | DictEntry | None
__all__ = ("PARSER", "ES3Transformer")


@dataclass
class DictEntry[KeyT = JSONValue, ValueT = JSONValue]:
    key: KeyT
    value: ValueT


@dataclass
class ES3Dictionary[KeyT = JSONValue, ValT = JSONValue]:
    entries: list[DictEntry[KeyT, ValT]]


class ES3Transformer(Transformer[ES3Value, Any]):
    @v_args(inline=True)
    def string(self, items: list[Token]) -> str:
        return str(items[1:-1]).replace('\\"', '"')

    # @v_args(inline=True)
    def number(self, items: list[Token]) -> float | int:
        n = items[0]

        if "." in n:
            return float(n)

        return int(n)

    def true(self, _: list[Any]) -> Literal[True]:
        return True

    def false(self, _: list[Any]) -> Literal[False]:
        return False

    def null(self, _: list[Any]) -> None:
        return None

    def member(self, items: list[Any]) -> tuple[Any, Any]:
        return (items[0], items[1])

    def numeric_key(self, token: list[Token]) -> int:
        return int(token[0].value)

    def string_key(self, token: list[Token]) -> str:
        return token[0].value[1:-1]

    def dict_entry(self, items: list[Any]) -> DictEntry:
        return DictEntry(key=items[0], value=items[1])

    def object(self, items: list[tuple[str, Any] | DictEntry]) -> dict[str, Any] | ES3Dictionary:
        # Detect ES3 dictionary style
        if not items:
            return {}

        if isinstance(items[0], DictEntry):
            return ES3Dictionary(entries=[x for x in items if isinstance(x, DictEntry)])

        return dict(items)  # pyright: ignore[reportReturnType, reportArgumentType, reportCallIssue] # standard JSON object

    def array(self, items: list[Any]) -> list[Any]:
        return list(items)


LARK_FILE = pathlib.Path(__file__).parent / "save.lark"
PARSER = Lark.open(str(LARK_FILE), parser="lalr", transformer=ES3Transformer(), propagate_positions=True)  # pyright: ignore[reportUnknownMemberType] # lark types aren't complete
