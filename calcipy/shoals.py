"""Main CLI Entrypoint."""

from beartype import beartype
from . import code_tag_collector
from shoal import shoalling

@beartype
def _load_all() -> None:
	"""Load all tasks for shoal."""
	code_tag_collector.cli.load()


@beartype
def run() -> None:
	"""Main CLI Entrypoint."""
	_load_all()
	shoalling()
