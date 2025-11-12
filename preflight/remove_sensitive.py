# pyright: reportPrivateUsage=false

import argparse
import pathlib

import yurei


class ProgramNamespace(argparse.Namespace):
    file: pathlib.Path


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=pathlib.Path, required=True, dest="file")

args = parser.parse_args(namespace=ProgramNamespace())

if not args.file.exists():
    msg_ = f"Provided file {args.file} could not be found."
    raise FileNotFoundError(msg_)

save = yurei.Save.from_path(args.file)

with save:
    save._data["recentPlayerIDS"]["value"] = []
    save._data["recentPlayerNames"]["value"] = []
    save._data["recentPlayerPlatformIDS"]["value"] = []
    save._data["recentPlayerPlatforms"]["value"] = []
