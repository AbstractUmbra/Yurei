import logging
import pathlib

from yurei import Save

logging.basicConfig(level=logging.INFO)


def main() -> None:
    file = pathlib.Path("test_files/SaveFile-no-unlockable.txt")
    with Save.from_path(file) as save:
        backup = save.create_backup()
        print(backup.resolve().expanduser())


if __name__ == "__main__":
    main()
