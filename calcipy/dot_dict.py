"""Dotted dictionary for consistent interface."""

from typing import Any, Dict, Union

from beartype import beartype
from box import Box

DDICT_TYPE = Union[Dict[str, Any], Box]
"""Return type from `ddict()`."""


@beartype
def ddict(**kwargs: Dict[str, Any]) -> DDICT_TYPE:
    """Return a dotted dictionary that can also be accessed normally.

    Currently uses `python-box` because there is a more recent release, but could also use `munch`

    Other variations are no longer supported, such as `bunch` and `ddict` among others

    Args:
        kwargs: keyword arguments formatted into dictionary

    Returns:
        DDICT_TYPE: dotted dictionary

    """
    return Box(kwargs)
