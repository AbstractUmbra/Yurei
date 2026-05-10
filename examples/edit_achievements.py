import yurei


def handle_achievement_unlocks() -> None:
    # see `basic.py` for context manager explanation
    with yurei.Save.from_default_path() as save:
        # each Save has an `unlockable_manager` attribute which binds to a wrapper.
        # To keep it simple, it does most of the heavy lifting.

        # let's edit the Nell's Diner achievement unlocks
        save.unlockable_manager.nells_diner.completed = False
        save.unlockable_manager.nells_diner.received = False
        save.unlockable_manager.nells_diner.progression = 49

        # above we set the achievement progress as such:-
        # Completed 49/50 of the required runs to get the badge/icon
        # We have NOT received the reward
        # We have NOT completed the achievement

    # there are achievement handles for each of the current ones, and they are updated when needed.
