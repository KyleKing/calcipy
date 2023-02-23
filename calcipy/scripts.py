"""Start the command line program."""

from beartype import beartype

from . import __pkg_name__, __version__


@beartype
def start() -> None:
    """Run the customized Invoke Program."""
    from .cli import start_program
    from .tasks import all_tasks
    start_program(__pkg_name__, __version__, all_tasks)
