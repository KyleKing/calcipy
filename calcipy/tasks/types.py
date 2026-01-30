"""Types CLI."""

from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import PYRIGHT_MESSAGE, check_installed, python_m


@task()
def pyright(ctx: Context) -> None:
    """Run pyright using the config in `pyproject.toml`."""
    check_installed(ctx, executable='pyright', message=PYRIGHT_MESSAGE)
    run(ctx, 'pyright')


@task()
def mypy(ctx: Context) -> None:
    """Run mypy."""
    run(ctx, f'{python_m()} mypy')


@task()
def ty(ctx: Context) -> None:
    """Run ty type checker."""
    run(ctx, 'ty check calcipy tests')
