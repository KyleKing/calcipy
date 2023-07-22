"""Dotted dictionary for consistent interface.

Consider moving to Corallium, but I don't have any uses for it yet.

"""

from beartype import beartype
from beartype.typing import Any, Dict, Union
from box import Box

DdictType = Union[Dict[str, Any], Box]
"""Return type from `ddict()`."""


@beartype
def ddict(**kwargs: Dict[str, Any]) -> DdictType:
    """Return a dotted dictionary that can also be accessed normally.

    - Currently uses `python-box`
    - Could consider `cleverdict` which had updates as recently as 2022
    - There are numerous other variations that haven't been updated since 2020, such as `munch`, `bunch`, `ddict`

    Args:
        **kwargs: keyword arguments formatted into dictionary

    Returns:
        DdictType: dotted dictionary

    """
    return Box(kwargs)
