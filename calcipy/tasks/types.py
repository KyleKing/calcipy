"""Types CLI."""

from beartype import beartype
from invoke import Context
from shoal.cli import task

from ..file_helpers import read_package_name
from ..invoke_helpers import use_pty


@beartype
def _inner_task(ctx: Context, *, cli_args: str, command: str) -> None:
    """Shared task logic."""
    pkg_name = read_package_name()
    ctx.run(
        f'poetry run {command} {pkg_name}{cli_args}',
        echo=True, pty=use_pty(),
    )


@task()  # type: ignore[misc]
def pyright(ctx: Context) -> None:
    """Run pyright."""
    _inner_task(ctx, cli_args='', command='pyright')


@task()  # type: ignore[misc]
def mypy(ctx: Context) -> None:
    """Run mypy."""
    _inner_task(ctx, cli_args='', command='python -m mypy')
