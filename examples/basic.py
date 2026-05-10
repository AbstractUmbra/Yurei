# preface: it is *highly* recommended you use the `Save` class as a context manager
# as it handles both backups and writing the file edits for you.
# nevertheless I will document how to use it without that here.

import pathlib

import yurei


def get_save_file(*, create_backup: bool = True) -> yurei.Save:
    # our `create_backup` parameter exists because by default `yurei`
    # will back up save files before making any edits. We can turn this behaviour off
    # as it is enabled by default

    # we use pathlib around these parts, because it removes a lot of ambiguity.
    file = pathlib.Path("/path/to/your/save-file")
    save = yurei.Save.from_path(file, create_backup=create_backup)

    # alternatively, since the save location is static on windows we can also use the builtin
    # `Save.from_default_path()` method to skip this part
    save = yurei.Save.from_default_path(create_backup=create_backup)

    return save  # noqa: RET504 # going for more verbose for example purposes.


def unlock_all_tier_2_equipment() -> None:
    save = get_save_file()

    # now we "enter" here to utilise the writing and backup mechanism
    with save:
        # `unlock_equipment` can take an argument for a specific piece of equipment
        # but if not given, it will unlock *all* pieces of equipment
        save.unlock_equipment(tier=2)

    # when we get to this print we'll have "exited" the context manager
    # this means that we'll create a backup of our save, and then write our edits in.
    print("Unlocked all equipment at tier 2.")  # noqa: T201
