"""Test CLI."""

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

_STEPWISE_ARGS = ' --failed-first --new-first --exitfirst -vv --no-cov'


@beartype
def _inner_task(
    ctx: Context,
    *,
    cli_args: str,
    keyword: str = '',
    marker: str = '',
    command: str = 'python -m pytest',
) -> None:
    """Shared task logic."""
    if keyword:
        cli_args += f' -k "{keyword}"'
    if marker:
        cli_args += f' -m "{marker}"'
    ctx.run(
        f'poetry run {command} ./tests{cli_args}',
        echo=True, pty=True,
    )


@task(  # type: ignore[misc]
    default=True,
    help={
        # See: https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests
        'keyword': 'Only run tests that match the string pattern',
        'marker': 'Only run tests matching given mark expression',
    },
)
def pytest(ctx: Context, *, keyword: str = '', marker: str = '') -> None:
    """Run pytest with default arguments."""
    pkg_name = read_package_name()
    _inner_task(ctx, cli_args=f' --cov={pkg_name} --cov-report=term-missing', keyword=keyword, marker=marker)


@task(help=pytest.help)  # type: ignore[misc]
def step(ctx: Context, *, keyword: str = '', marker: str = '') -> None:
    """Run pytest optimized to stop on first error."""
    _inner_task(ctx, cli_args=_STEPWISE_ARGS, keyword=keyword, marker=marker)


@task(help=pytest.help)  # type: ignore[misc]
def watch(ctx: Context, *, keyword: str = '', marker: str = '') -> None:
    """Run pytest with polling and optimized to stop on first error."""
    _inner_task(ctx, cli_args=_STEPWISE_ARGS, keyword=keyword, marker=marker, command='ptw . --now')


@task(  # type: ignore[misc]
    help={
        'min_cover': 'Fail if coverage less than threshold',
        'out_dir': 'Optional path to coverage directory. Typically ".cover" or "releases/tests"',
        'view': 'If True, open the created files',
    },
)
def write_json(ctx: Context, *, min_cover: int = 0, out_dir: Optional[str] = None, view: bool = False) -> None:
    """Create json coverage file."""
    cover_args = f' --cov-fail-under={min_cover}'  if min_cover else ''

    pkg_name = read_package_name()
    ctx.run(
        f'poetry run coverage run --source={pkg_name} --module pytest ./tests{cover_args}',
        echo=True, pty=True,
    )

    cov_dir = Path(out_dir or from_ctx(ctx, 'tests', 'out_dir'))
    cov_dir.mkdir(exist_ok=True, parents=True)
    for cmd in [
        'poetry run python -m coverage report --show-missing',  # Write to STDOUT
        f'poetry run python -m coverage html --directory={cov_dir}',  # Write to HTML
        'poetry run python -m coverage json',  # Create coverage.json file for "_write_coverage_to_md"
    ]:
        ctx.run(cmd)

    if view:  # pragma: no cover
        open_in_browser(cov_dir / 'index.html')
