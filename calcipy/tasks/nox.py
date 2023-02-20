"""Nox CLI."""

from invoke import Context
from shoal.cli import task

from ..noxfile._noxfile import BASE_NOX_COMMAND


@task(  # type: ignore[misc]
    default=True,
    help={
        'session': 'Optional session to run',
    },
)
def noxfile(ctx: Context, *, session: str = '') -> None:
    """Run nox from the local noxfile."""
    cli_args = ['--session', session] if session else []
    ctx.run(f'{BASE_NOX_COMMAND} {" ".join(cli_args)}')
