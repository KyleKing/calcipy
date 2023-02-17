"""Start the command line program."""

from beartype import beartype
from shoal.cli import start_program

from . import __pkg_name__, __version__
from .tasks import all_tasks


@beartype
def start() -> None:
    """Run the customized Invoke Program."""
    start_program(__pkg_name__, __version__, all_tasks)
