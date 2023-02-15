"""Stale Packages CLI."""

import re
from pathlib import Path
from beartype.typing import Dict, List, Tuple
from contextlib import suppress

from invoke import task, Context
from beartype import beartype
from ..check_for_stale_packages import check_for_stale_packages as cfsp
from ..check_for_stale_packages import PACK_LOCK_PATH
from shoal._log import configure_logger
import logging


@task(
    default=True,
    help={
        'stale_months': 'Cutoff in months for when a package may be stale enough to be a risk',
    },
)
def check_for_stale_packages(ctx: Context, stale_months: int = 48) -> None:
    """Maintain `PACK_LOCK_PATH` based on `poetry.lock` to identify stale dependencies."""
    verbose = 2
    with suppress(AttributeError):
        verbose = ctx.config.gto.verbose
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(verbose) or logging.ERROR)

    # FIXME: Use can_skip() for poetry.lock vs. PACK_LOCK_PATH

    path_lock = Path('poetry.lock')
    cfsp(path_lock=path_lock, path_pack_lock=PACK_LOCK_PATH, stale_months=stale_months)

    # PLANNED: Also run pip-check (below)
    #   poetry run pip-check --cmd="poetry run pip" --hide-unchanged
