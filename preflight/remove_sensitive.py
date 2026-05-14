# pyright: reportPrivateUsage=false

import argparse
import pathlib

import yurei


class ProgramNamespace(argparse.Namespace):
    file: pathlib.Path | None


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=pathlib.Path, required=False, dest="file")

args = parser.parse_args(namespace=ProgramNamespace())


def do_removal(save: yurei.Save) -> None:
    with save:
        save._data["recentPlayerIDS"]["value"] = []
        save._data["recentPlayerNames"]["value"] = []
        save._data["recentPlayerPlatformIDS"]["value"] = []
        save._data["recentPlayerPlatforms"]["value"] = []


def main() -> None:
    if args.file:
        save = yurei.Save.from_path(args.file)
        do_removal(save)
    else:
        save_files = (pathlib.Path(__file__).parent.parent / "test_files").glob("*.txt")
        for save in save_files:
            do_removal(yurei.Save.from_path(save))


if __name__ == "__main__":
    main()
