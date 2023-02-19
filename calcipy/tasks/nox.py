"""Nox CLI."""

from beartype import beartype
from beartype.typing import List
from invoke import Context
from shoal.cli import task

from .invoke_helpers import use_pty


@beartype
def _inner_task(ctx: Context, *, cli_args: List[str]) -> None:
    """Shared task logic."""
    with ctx.cd('.'):  # FYI: can change directory like this
        ctx.run(
            f'poetry run nox --error-on-missing-interpreters {" ".join(cli_args)}',
            echo=True, pty=use_pty(),
        )


@task(  # type: ignore[misc]
    default=True,
    help={
        'session': 'Optional session to run',
    },
)
def noxfile(ctx: Context, *, session: str = '') -> None:
    """Run nox from the local noxfile."""
    _inner_task(ctx, cli_args=['--session', session] if session else [])
