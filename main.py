import logging
import pathlib

from yurei import Save

logging.basicConfig(level=logging.INFO)


def main() -> None:
    file = pathlib.Path("test_files/SaveFile.txt")
    with Save.from_path(file) as save:
        save.level = 100
        save.unlock_equipment(tier=3)


if __name__ == "__main__":
    main()
