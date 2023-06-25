"""Nox CLI."""

from invoke.context import Context

from ..cli import task
from ..invoke_helpers import run
from .executable_utils import python_dir


@task(
    default=True,
    help={
        'session': 'Optional session to run',
    },
)
def noxfile(ctx: Context, *, session: str = '') -> None:
    """Run nox from the local noxfile."""
    cli_args = ['--session', session] if session else []
    run(ctx, f'{python_dir()}/nox --error-on-missing-interpreters {" ".join(cli_args)}')
