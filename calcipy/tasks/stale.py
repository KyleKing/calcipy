"""Stale Packages CLI."""

from invoke import Context
from shoal.cli import task
from shoal.invoke_helpers import run

from ..check_for_stale_packages import check_for_stale_packages as cfsp


@task(  # type: ignore[misc]
    default=True,
    help={
        'stale_months': 'Cutoff in months for when a package may be stale enough to be a risk',
    },
)
def check_for_stale_packages(ctx: Context, *, stale_months: int = 48) -> None:
    """Identify stale dependencies."""
    cfsp(stale_months=stale_months)
    run(ctx, 'poetry run pip-check --cmd="poetry run pip" --hide-unchanged')
