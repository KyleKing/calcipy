"""Stale Packages CLI."""

from invoke.context import Context

from ..check_for_stale_packages import check_for_stale_packages as cfsp
from ..cli import task
from ..invoke_helpers import run
from .executable_utils import python_dir


@task(
    default=True,
    help={
        'stale_months': 'Cutoff in months for when a package may be stale enough to be a risk',
    },
)
def check_for_stale_packages(ctx: Context, *, stale_months: int = 48) -> None:
    """Identify stale dependencies."""
    cfsp(stale_months=stale_months)
    run(ctx, f'{python_dir()}/pip-check --cmd="poetry run pip" --hide-unchanged')
