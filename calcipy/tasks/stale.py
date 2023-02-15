"""Stale Packages CLI."""

import logging
from contextlib import suppress
from pathlib import Path

from invoke import Context, task
from shoal._log import configure_logger

from ..check_for_stale_packages import PACK_LOCK_PATH
from ..check_for_stale_packages import check_for_stale_packages as cfsp


@task(
    default=True,
    help={
        'stale_months': 'Cutoff in months for when a package may be stale enough to be a risk',
    },
)
def check_for_stale_packages(ctx: Context, *, stale_months: int = 48) -> None:
    """Maintain `PACK_LOCK_PATH` based on `poetry.lock` to identify stale dependencies."""
    verbose = 2
    with suppress(AttributeError):
        verbose = ctx.config.gto.verbose
    log_lookup = {3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}
    configure_logger(log_level=log_lookup.get(verbose) or logging.ERROR)

    # FIXME: Use can_skip() for poetry.lock vs. PACK_LOCK_PATH

    path_lock = Path('poetry.lock')
    cfsp(path_lock=path_lock, path_pack_lock=PACK_LOCK_PATH, stale_months=stale_months)

    # PLANNED: Also run pip-check (below)
    #   poetry run pip-check --cmd="poetry run pip" --hide-unchanged
