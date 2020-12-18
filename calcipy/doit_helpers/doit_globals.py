"""Global Variables for DoIt."""

from pathlib import Path
from typing import Callable, Dict, NewType, Optional, Sequence, Tuple, Union

import toml
from loguru import logger

from ..log_helpers import log_fun

# ----------------------------------------------------------------------------------------------------------------------
# Global Variables

DoItTask = NewType('DoItTask', Dict[str, Union[str, Tuple[Callable, Sequence]]])  # noqa: ECE001
"""DoIt task type for annotations."""


DIG = DoItGlobals()
"""Global DoIt Globals class used to manage global variables."""
