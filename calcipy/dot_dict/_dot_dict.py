"""Dotted dictionary for consistent interface."""

from beartype import beartype
from beartype.typing import Any, Dict, Union
from box import Box

DDICT_TYPE = Union[Dict[str, Any], Box]
"""Return type from `ddict()`."""


@beartype
def ddict(**kwargs: Dict[str, Any]) -> DDICT_TYPE:
    """Return a dotted dictionary that can also be accessed normally.

    - Currently uses `python-box`
    - Could consider `cleveridct` which had updates as recently as 2022
    - There are numerous other variations that haven't been updated since 2020, such as `munch`, `bunch`, `ddict`

    Args:
        **kwargs: keyword arguments formatted into dictionary

    Returns:
        DDICT_TYPE: dotted dictionary

    """
    return Box(kwargs)
