"""Stale Packages CLI."""

from pathlib import Path

from invoke import Context
from shoal.cli import task

from ..check_for_stale_packages import PACK_LOCK_PATH
from ..check_for_stale_packages import check_for_stale_packages as cfsp


@task(  # type: ignore[misc]
    default=True,
    help={
        'stale_months': 'Cutoff in months for when a package may be stale enough to be a risk',
    },
)
def check_for_stale_packages(_ctx: Context, *, stale_months: int = 48) -> None:
    """Maintain `PACK_LOCK_PATH` based on `poetry.lock` to identify stale dependencies."""
    path_lock = Path('poetry.lock')
    cfsp(path_lock=path_lock, path_pack_lock=PACK_LOCK_PATH, stale_months=stale_months)

    # PLANNED: Also run pip-check (below)
    #   poetry run pip-check --cmd="poetry run pip" --hide-unchanged
