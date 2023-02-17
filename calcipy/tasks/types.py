"""Types CLI."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Optional
from invoke import Context
from shoal import get_logger
from shoal.cli import task

from ..file_helpers import open_in_browser
from .cached_utilities import read_package_name
from .defaults import from_ctx

logger = get_logger()


@beartype
def _inner_task(ctx: Context, *, cli_args: str, command: str) -> None:
    """Shared task logic."""
    pkg_name = read_package_name()
    ctx.run(
        f'poetry run {command} {pkg_name}{cli_args}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )


@task(
    default=True,
    help={},
)
def pyright(ctx: Context) -> None:
    """Default task to run pyright."""
    _inner_task(ctx, cli_args='', command='pyright')

@task(
    help={
        'out_dir': 'Optional path to the report directory. Typically "releases/tests/mypy_html"',
        'view': 'If True, open the created file',
    },
)
def mypy(ctx: Context, *, out_dir: Optional[str] = None, view: bool = False) -> None:
    """Alternatie task to run mypy."""
    # PLANNED: If `out_dir == ''`, then do not create an HTML report
    report_dir = Path(out_dir or from_ctx(ctx, 'types', 'out_dir'))
    _inner_task(ctx, cli_args=f' --html-report={report_dir}', command='python -m mypy')

    if view:
        open_in_browser(report_dir / 'index.html')
