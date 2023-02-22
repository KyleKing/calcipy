"""Types CLI."""

from beartype import beartype
from corallium.file_helpers import read_package_name
from invoke import Context

from ..cli import task
from ..invoke_helpers import run


@beartype
def _inner_task(ctx: Context, *, cli_args: str, command: str) -> None:
    """Shared task logic."""
    pkg_name = read_package_name()
    run(ctx, f'poetry run {command} {pkg_name}{cli_args}')


@task()
def pyright(ctx: Context) -> None:
    """Run pyright."""
    _inner_task(ctx, cli_args='', command='pyright')


@task()
def mypy(ctx: Context) -> None:
    """Run mypy."""
    _inner_task(ctx, cli_args='', command='python -m mypy')
