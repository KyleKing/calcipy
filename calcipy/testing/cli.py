"""Testing CLI."""

from pathlib import Path
from beartype.typing import Dict, List, Tuple, Optional
from functools import partial
from invoke import task, Context
from beartype import beartype
import logging
from shoal import get_logger
from shoal._log import configure_logger

logger = get_logger()

# FIXME: Make this a decorator to handle configure_logger internally
# 	^ possibly consider pairing with a global Config
tang = partial(task, incrementable=['verbose'])


@tang(
	iterable=['nox_tasks'],
    help={
        'nox_tasks': 'nox-args',
        'install_types': 'TBD',
    }
)
@beartype
def nox(
		ctx: Context,
		verbose: int = 0,
		nox_tasks: Optional[List[str]] = None,
		install_types: bool = False,
	) -> None:
    """Run the local noxfile."""
    configure_logger(log_level=logging.INFO if verbose else logging.DEBUG)
    logger.info(f'Starting nox with: {nox_tasks} and {ctx.config}')
    logger.info(f'file_args {ctx.config.file_args}')


    ctx.run(f'poetry run nox --error-on-missing-interpreters {" ".join(nox_tasks or [])}')
