__title__ = "Yurei"
__author__ = "AbstractUmbra"
__license__ = "AGPL-v3"
__copyright__ = "Copyright 2025-present AbstractUmbra"
__version__ = "0.0.1"

import logging

from . import utils
from .enums import *
from .save import Save
from .tui import *

CURRENT_SAVE_KEY: str = "t36gref9u84y7f43g"

__all__ = ("CURRENT_SAVE_KEY", "Save", "utils")

logging.getLogger(__name__).addHandler(logging.NullHandler())
