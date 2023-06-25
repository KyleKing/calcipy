"""Types CLI."""

from beartype import beartype
from corallium.file_helpers import read_package_name
from invoke.context import Context
from invoke.exceptions import UnexpectedExit

from ..cli import task
from ..invoke_helpers import run
from .executable_utils import python_dir


@beartype
def _inner_task(ctx: Context, *, command: str, cli_args: str = '') -> None:
    """Shared task logic."""
    pkg_name = read_package_name()
    run(ctx, f'{command} {pkg_name} {cli_args}'.strip())


@task()
def pyright(ctx: Context) -> None:
    """Run pyright."""
    try:
        _inner_task(ctx, command='pyright')
    except UnexpectedExit as exc:
        raise RuntimeError(
            "pyright must be installed separately, such as 'brew install pyright' on Mac."
            ' See the online documentation for your system: https://microsoft.github.io/pyright/#/installation',
        ) from exc


@task()
def mypy(ctx: Context) -> None:
    """Run mypy."""
    _inner_task(ctx, command=f'{python_dir()}/mypy')
