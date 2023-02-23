"""Start the command line program."""

from beartype import beartype

from . import __pkg_name__, __version__
from .cli import start_program


@beartype
def start() -> None:
    """Run the customized Invoke Program."""
    from .tasks import all_tasks
    start_program(__pkg_name__, __version__, all_tasks)


@beartype
def start_lint() -> None:
    """Run the specified subset of tasks."""
    from .tasks import only_lint
    start_program(__pkg_name__, __version__, only_lint)


@beartype
def start_tags() -> None:
    """Run the specified subset of tasks."""
    from .tasks import only_tags
    start_program(__pkg_name__, __version__, only_tags)


@beartype
def start_types() -> None:
    """Run the specified subset of tasks."""
    from .tasks import only_types
    start_program(__pkg_name__, __version__, only_types)
