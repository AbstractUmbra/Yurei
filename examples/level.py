import yurei


def handle_prestige_and_levels() -> None:
    # see `basic.py` for context manager explanation
    with yurei.Save.from_default_path() as save:
        # We can edit our prestige and level here
        # NOTE: I have never attempted to force a new prestige this way, not via the game.
        # I do not know if you'll receive the rewards (cards/badges) if you do it this way.
        save.prestige = 8
        save.level = 50
