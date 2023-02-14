"""Test CLI."""

from contextlib import suppress
from pathlib import Path
from beartype.typing import Dict, List, Tuple, Optional, Callable
from functools import partial
from invoke import task, Context
from beartype import beartype
import logging
from shoal import get_logger
from shoal._log import configure_logger
from .cached_utilities import read_package_name

logger = get_logger()

_STEPWISE_ARGS = ' --failed-first --new-first --exitfirst -vv --no-cov'


@beartype
def _inner_task(ctx: Context, *, cli_args: str, keyword: str = '', marker: str = '', target: str = 'python -m pytest') -> None:
    """Shared task logic."""
    verbose = 2
    with suppress(AttributeError):
        verbose = ctx.config.gto.verbose
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(verbose) or logging.ERROR)

    if keyword:
        cli_args += f' -k "{keyword}"'
    if marker:
        cli_args += f' -m "{marker}"'
    ctx.run(
        f'poetry run {target} ./tests{cli_args}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )


@task(
    default=True,
    help={
        # See: https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests
        'keyword': 'Only run tests that match the string pattern',
        'marker': 'Only run tests matching given mark expression',
    },
)
def default(ctx: Context, keyword: str = '', marker: str = '') -> None:
    """Run pytest with default arguments."""
    _inner_task(ctx, cli_args='', keyword=keyword, marker=marker)


@task(help=default.help)
def step(ctx: Context, keyword: str = '', marker: str = '') -> None:
    """Run pytest optimized to stop on first error."""
    _inner_task(ctx, cli_args=_STEPWISE_ARGS, keyword=keyword, marker=marker)


@task(help=default.help)
def watch(ctx: Context, keyword: str = '', marker: str = '') -> None:
    """Run pytest with polling and optimized to stop on first error."""
    _inner_task(ctx, cli_args=_STEPWISE_ARGS, keyword=keyword, marker=marker, target='ptw . --now')


@task(
    help={
        'min_cover': 'Fail if coverage less than threshold',
    },
)
def write_json(ctx: Context, min_cover: int = 0) -> None:
    """Create json coverage file."""
    pkg_name = read_package_name()
    cover_args = f'--cov-fail-under={min_cover}'  if min_cover else ''
    # FYI: Support .cover vs. releases/tests
    cov_dir = Path('.cover')
    cov_dir = cov_dir.mkdir(exist_ok=True, parents=True)
    html_args = f'--cov-report=html:{cov_dir} --html={cov_dir}/test_report.html --self-contained-html'
    ctx.run(
        f'poetry run coverage run --source={pkg_name} --module=pytest ./tests {html_args} {cover_args}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )
    for cmd in [
        'poetry run python -m coverage report --show-missing',
        f'poetry run python -m coverage html --directory={cov_dir}',
        'poetry run python -m coverage json',  # Create coverage.json file for "_write_coverage_to_md"
    ]:
        ctx.run(cmd, echo=True, pty=True)
