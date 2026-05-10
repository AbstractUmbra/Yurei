import logging
import pathlib

from yurei import Save

logging.basicConfig(level=logging.INFO)


def main() -> None:
    file = pathlib.Path("test_files/SaveFile-post-avatar.txt")
    with Save.from_path(file) as save:
        save.unlockable_manager.tanglewood.progression = 49
        save.unlockable_manager.tanglewood.received = 0
        save.unlockable_manager.tanglewood.completed = 0
        save.level = 100
        save.unlock_equipment(tier=3)


if __name__ == "__main__":
    main()
