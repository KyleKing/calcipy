"""Start the command line program."""

from types import ModuleType

from beartype.typing import List
from corallium.log import LOGGER

from . import __pkg_name__, __version__
from .cli import start_program
from .collection import Collection


def start() -> None:  # pragma: no cover
    """Run the customized Invoke Program."""
    try:
        from .tasks import all_tasks  # noqa: PLC0415

        start_program(__pkg_name__, __version__, all_tasks)
    except (ImportError, RuntimeError) as error:
        from .tasks import most_tasks  # noqa: PLC0415

        LOGGER.error(str(error))  # Must be first
        print()  # noqa: T201
        start_program(__pkg_name__, __version__, most_tasks)


def _start_subset(modules: List[ModuleType]) -> None:  # pragma: no cover
    """Run the specified subset."""
    from .tasks.defaults import new_collection  # noqa: PLC0415

    ns = new_collection()
    for module in modules:
        ns.add_collection(Collection.from_module(module))

    start_program(__pkg_name__, __version__, collection=ns)


def start_docs() -> None:  # pragma: no cover
    """Run CLI with only the cl and doc namespaces."""
    from .tasks import cl, doc  # noqa: PLC0415

    _start_subset([cl, doc])


def start_lint() -> None:  # pragma: no cover
    """Run CLI with only the lint namespace."""
    from .tasks import lint  # noqa: PLC0415

    _start_subset([lint])


def start_pack() -> None:  # pragma: no cover
    """Run CLI with only the pack namespace."""
    from .tasks import pack  # noqa: PLC0415

    _start_subset([pack])


def start_tags() -> None:  # pragma: no cover
    """Run CLI with only the tags namespace."""
    from .tasks import tags  # noqa: PLC0415

    _start_subset([tags])


def start_test() -> None:  # pragma: no cover
    """Run CLI with only the test namespace."""
    from .tasks import test  # noqa: PLC0415

    _start_subset([test])


def start_types() -> None:  # pragma: no cover
    """Run CLI with only the types namespace."""
    from .tasks import types  # noqa: PLC0415

    _start_subset([types])
