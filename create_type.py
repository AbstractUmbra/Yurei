import argparse
import pathlib
import re
import subprocess  # noqa: S404 # this is used as preflight on trusted input
import sys
from typing import Any

from yurei.crypt import decrypt
from yurei.types_ import Save as SaveType
from yurei.utils import get_save_password, to_json

GENERIC_PATTERN: re.Pattern[str] = re.compile(r"\[(?P<generic>[a-zA-Z0-9\.]+),")
TEMPLATE: str = r"""
from typing import TypedDict

from .inner_types import Bool, ColourValue, Dict, DifficultyValue, Float, Int, List, SpecialPlayedMaps, String

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
    "int": "Int",
    "System.String": "String",
    "System.Int32": "Int",
    "Difficulty,Assembly-CSharp": "DifficultyValue",
}
PYTHON_TYPE_LOOKUP = {
    "Color": "ColourValue",
    "string": "str",
    "float": "float",
    "bool": "bool",
    "int": "int",
    "System.String": "str",
    "System.Int32": "int",
    "Difficulty,Assembly-CSharp": "DifficultyValue",
}
# usually because of dumb json issues with cs
SPECIAL_CASES = {"playedMaps": "SpecialPlayedMaps", "RoleType": "Int", "currentSeasonalEvent": "Int"}
CURRENT_SAVE_KEY = get_save_password(password_file=(pathlib.Path(__file__).parent / "resources" / "save_password"))


class ProgramNamespace(argparse.Namespace):
    file: pathlib.Path


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=pathlib.Path, required=True, dest="file")

args = parser.parse_args(namespace=ProgramNamespace())

if not args.file.exists():
    msg_ = f"Provided file {args.file} could not be found."
    raise FileNotFoundError(msg_)


def _extract_generic(inp: str) -> tuple[str, ...]:
    matches = list(GENERIC_PATTERN.finditer(inp))
    if not matches:
        raise ValueError("Our pattern is bad or the type is wrong.")

    return tuple(match.group("generic") for match in matches)


def _resolve_type(inp: str) -> str:
    if "System.Collections.Generic.Dictionary" in inp:
        key, val = _extract_generic(inp)
        key, val = PYTHON_TYPE_LOOKUP[key], PYTHON_TYPE_LOOKUP[val]
        return f"Dict[{key}, {val}]"

    if "System.Collections.Generic.List" in inp:
        resolved, *_ = _extract_generic(inp)
        resolved = PYTHON_TYPE_LOOKUP[resolved]
        return f"List[{resolved}]"

    return LOOKUP[inp]


def create_json() -> dict[str, Any]:
    data = decrypt(path=args.file, password=CURRENT_SAVE_KEY, strip_type_key=False, return_type=SaveType)

    # data is json

    with pathlib.Path("decrypted.json").open("w", encoding="utf-8") as fp:
        fp.write(to_json(data))

    return dict(sorted(data.items()))


def parse_json(input_: dict[str, Any]) -> str:
    ret: dict[str, Any] = {}
    for k, v in input_.items():
        type_ = v["__type"]
        if k in SPECIAL_CASES:
            ret[k] = SPECIAL_CASES[k]
            continue
        try:
            ret[k] = _resolve_type(type_)
        except KeyError as err:
            msg = f"Key {k!r} has an unknown type(s): {', '.join(map(repr, err.args))}"
            raise KeyError(msg) from err

    return "{" + "\n".join([f'"{k}": {v},' for k, v in ret.items()]) + "}"


def main() -> None:
    json = create_json()
    type_ = TEMPLATE.format_map({"keyvalmap": parse_json(json)})
    with pathlib.Path("yurei/types_/save.py").open("w", encoding="utf-8") as fp:
        fp.write(type_)

    sys.exit(subprocess.Popen("ruff format yurei/types_/save.py", shell=True).returncode)  # noqa: S602, S607 # this is used as preflight on trusted input


if __name__ == "__main__":
    main()
