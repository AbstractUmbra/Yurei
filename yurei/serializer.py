from __future__ import annotations

import json
from typing import Any

from .parser import DictEntry, ES3Dictionary

__all__ = ("ES3Serializer",)


class ES3Serializer:
    def dumps(self, obj: Any) -> str:
        return self._emit(obj)

    def _emit(self, obj: Any) -> str:  # noqa: PLR0911 # the joys of recursive factories
        if isinstance(obj, ES3Dictionary):
            return self._emit_es3_dictionary(obj)

        if isinstance(obj, DictEntry):
            return self._emit_dict_entry(obj)

        if isinstance(obj, dict):
            return self._emit_object(obj)  # pyright: ignore[reportUnknownArgumentType] # the joys of recursive factories

        if isinstance(obj, list):
            return self._emit_array(obj)  # pyright: ignore[reportUnknownArgumentType] # the joys of recursive factories

        if isinstance(obj, str):
            return json.dumps(obj)

        if isinstance(obj, bool):
            return "true" if obj else "false"

        if obj is None:
            return "null"

        return str(obj)

    def _emit_key(self, obj: str | int) -> str:
        if isinstance(obj, int):
            return str(obj)
        return json.dumps(obj)

    def _emit_object(self, obj: dict[Any, Any]) -> str:
        members: list[str] = []

        for key, value in obj.items():
            members.append(f"{self._emit_key(key)}:{self._emit(value)}")

        return "{" + ",".join(members) + "}"

    def _emit_array(self, arr: list[Any]) -> str:
        return "[" + ",".join(self._emit(item) for item in arr) + "]"

    def _emit_dict_entry(self, entry: DictEntry) -> str:
        return f"{self._emit(entry.key)}:{self._emit(entry.value)}"

    def _emit_es3_dictionary(
        self,
        d: ES3Dictionary,
    ) -> str:
        return "{" + ",".join(self._emit(entry) for entry in d.entries) + "}"
