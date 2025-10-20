"""
The MIT License (MIT)

Copyright (c) 2023-present AbstractUmbra

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import json
import os
import pathlib
import platform
from typing import Any

__all__ = (
    "MISSING",
    "from_json",
    "resolve_save_path",
    "to_json",
)

try:
    import orjson  # pyright: ignore[reportMissingImports] # may not exist
except ModuleNotFoundError:

    def to_json(obj: Any, /) -> str:
        """A quick method that dumps a Python type to JSON object."""
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=True, indent=2, sort_keys=True)

    from_json = json.loads
else:

    def to_json(obj: Any, /) -> str:
        """A quick method that dumps a Python type to JSON object."""
        return orjson.dumps(obj, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS).decode("utf-8")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]  # may not be installed

    from_json = orjson.loads  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType] # this is guarded in an if.


class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "..."


MISSING: Any = _MissingSentinel()


def resolve_save_path() -> pathlib.Path:
    if platform.system() != "Windows":
        raise NotImplementedError("Only Windows supports default locations.")

    user_profile = os.getenv("USERPROFILE")
    if not user_profile:
        raise RuntimeError("This shouldn't happen or your windows profile is messed up.")

    save_data_path = (pathlib.Path(user_profile) / "AppData" / "LocalLow" / "Kinetic Games" / "Phasmophobia").expanduser()

    return save_data_path / "SaveFile.txt"
