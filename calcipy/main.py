import logging
from invoke import Program, Collection
from shoal._log import configure_logger
from beartype import beartype
from . import __version__, __pkg_name__
from . import tasks

@beartype
def run() -> None:
    configure_logger(log_level=logging.INFO)  # FIXME: Add parser and pop '--verbose'?
    Program(name=__pkg_name__, version=__version__, namespace=Collection.from_module(tasks)).run()
