"""Start the command line program."""

from types import ModuleType

from beartype.typing import List

from . import __pkg_name__, __version__
from .cli import start_program
from .tasks._invoke import Collection


def start() -> None:  # pragma: no cover
    """Run the customized Invoke Program."""
    from .tasks import all_tasks
    start_program(__pkg_name__, __version__, all_tasks)


def _start_subset(modules: List[ModuleType]) -> None:  # pragma: no cover
    """Run the specified subset."""
    from .tasks.defaults import new_collection

    ns = new_collection()
    for module in modules:
        ns.add_collection(Collection.from_module(module))

    start_program(__pkg_name__, __version__, collection=ns)


def start_lint() -> None:  # pragma: no cover
    """Run CLI with only the lint namespace."""
    from .tasks import lint
    _start_subset([lint])


def start_pack() -> None:  # pragma: no cover
    """Run CLI with only the pack namespace."""
    from .tasks import pack
    _start_subset([pack])


def start_tags() -> None:  # pragma: no cover
    """Run CLI with only the tags namespace."""
    from .tasks import tags
    _start_subset([tags])


def start_types() -> None:  # pragma: no cover
    """Run CLI with only the types namespace."""
    from .tasks import types
    _start_subset([types])
