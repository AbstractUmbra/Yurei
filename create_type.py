import json
import pathlib
import re
import subprocess  # noqa: S404 # this is used as preflight on trusted input
import sys
from typing import Any

from yurei import CURRENT_SAVE_KEY
from yurei.crypt import decrypt

GENERIC_PATTERN: re.Pattern[str] = re.compile(r"\[(?P<generic>[a-zA-Z0-9\.]+),")
TEMPLATE: str = r"""
from typing import TypedDict

from .inner_types import Bool, ColourValue, DifficultyValue, Float, Int, String, SpecialPlayedMaps

__all__ = ("Save",)

Save = TypedDict(
    "Save",
    {keyvalmap}
)

"""

LOOKUP = {
    "Color": "ColourValue",
    "string": "String",
    "float": "Float",
    "bool": "Bool",
    "System.String": "String",
    "System.Int32": "Int",
    "Difficulty,Assembly-CSharp": "DifficultyValue",
}

# usually because of dumb json issues with cs
SPECIAL_CASES = {"playedMaps": "SpecialPlayedMaps"}


def _extract_generic(inp: str) -> tuple[str, ...]:
    matches = list(GENERIC_PATTERN.finditer(inp))
    if not matches:
        raise ValueError("Our pattern is bad or the type is wrong.")

    return tuple(match.group("generic") for match in matches)


def _resolve_type(inp: str) -> str:
    if "System.Collections.Generic.Dictionary" in inp:
        key, val = _extract_generic(inp)
        key, val = LOOKUP[key], LOOKUP[val]
        return f"dict[{key}, {val}]"

    if "System.Collections.Generic.List" in inp:
        resolved, *_ = _extract_generic(inp)
        resolved = LOOKUP[resolved]
        return f"list[{resolved}]"

    return LOOKUP.get(inp, "Int")


def create_json() -> dict[str, Any]:
    file = pathlib.Path("test_files/SaveFile.txt")
    data = decrypt(path=file, password=CURRENT_SAVE_KEY, strip_type_key=False)

    # data is json

    with pathlib.Path("decrypted").open("w", encoding="utf-8") as fp:
        json.dump(data, fp)

    return dict(sorted(data.items()))


def parse_json(input_: dict[str, Any]) -> str:
    ret: dict[str, Any] = {}
    for k, v in input_.items():
        type_ = v["__type"]
        if k in SPECIAL_CASES:
            ret[k] = SPECIAL_CASES[k]
            continue
        ret[k] = _resolve_type(type_)

    return "{" + "\n".join([f'"{k}": {v},' for k, v in ret.items()]) + "}"


def main() -> None:
    json = create_json()
    type_ = TEMPLATE.format_map({"keyvalmap": parse_json(json)})
    with pathlib.Path("yurei/types_/save.py").open("w", encoding="utf-8") as fp:
        fp.write(type_)

    sys.exit(subprocess.Popen("ruff format yurei/types_/save.py", shell=True).returncode)  # noqa: S602, S607 # this is used as preflight on trusted input


if __name__ == "__main__":
    main()
