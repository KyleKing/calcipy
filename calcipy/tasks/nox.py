"""Nox CLI."""

from invoke.context import Context

from ..cli import task
from ..invoke_helpers import run
from ..noxfile._noxfile import BASE_NOX_COMMAND


@task(
    default=True,
    help={
        'session': 'Optional session to run',
    },
)
def noxfile(ctx: Context, *, session: str = '') -> None:
    """Run nox from the local noxfile."""
    cli_args = ['--session', session] if session else []
    run(ctx, f'{BASE_NOX_COMMAND} {" ".join(cli_args)}')
