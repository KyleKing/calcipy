"""Nox CLI."""

from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import python_m


@task(
    default=True,
    help={
        'session': 'Optional session to run',
    },
)
def noxfile(ctx: Context, *, session: str = '') -> None:
    """Run nox from the local noxfile."""
    cli_args = ['--session', session] if session else []
    run(ctx, f'{python_m()} nox --error-on-missing-interpreters {" ".join(cli_args)}')
