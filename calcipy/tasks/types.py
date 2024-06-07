"""Types CLI."""

from beartype import beartype
from corallium.file_helpers import read_package_name
from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import PYRIGHT_MESSAGE, check_installed, python_dir


@beartype
def _inner_task(ctx: Context, *, command: str, cli_args: str = '') -> None:
    """Shared task logic."""
    pkg_name = read_package_name()
    run(ctx, f'{command} {pkg_name} {cli_args}'.strip())


@task()
def basedpyright(ctx: Context) -> None:
    """Run basedpyright."""
    _inner_task(ctx, command=f'{python_dir()}/basedpyright')


@task()
def pyright(ctx: Context) -> None:
    """Run pyright."""
    check_installed(ctx, executable='pyright', message=PYRIGHT_MESSAGE)
    _inner_task(ctx, command='pyright')


@task()
def mypy(ctx: Context) -> None:
    """Run mypy."""
    _inner_task(ctx, command=f'{python_dir()}/mypy')
