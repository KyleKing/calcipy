"""Test CLI."""

from pathlib import Path

from beartype.typing import Optional
from corallium.file_helpers import open_in_browser, read_package_name
from invoke.context import Context

from calcipy.cli import task
from calcipy.experiments import check_duplicate_test_names
from calcipy.invoke_helpers import run

from .defaults import from_ctx
from .executable_utils import python_dir, python_m


def _inner_task(
    ctx: Context,
    *,
    command: str = 'pytest',
    cli_args: str = '',
    keyword: str = '',
    marker: str = '',
    min_cover: int = 0,
    run_as_module: bool = True,
) -> None:
    """Shared task logic."""
    if keyword:
        cli_args += f' -k "{keyword}"'
    if marker:
        cli_args += f' -m "{marker}"'
    if fail_under := min_cover or int(from_ctx(ctx, 'test', 'min_cover')):
        cli_args += f' --cov-fail-under={fail_under}'
    cmd = f'{python_m()} {command}' if run_as_module else str(python_dir() / command).replace('\\', '/')
    run(ctx, f'{cmd} ./tests{cli_args}')


@task()
def check(_ctx: Context) -> None:
    """Run pytest checks, such as identifying.

    Raises:
        RuntimeError: if duplicate tests

    """
    if duplciates := check_duplicate_test_names.run(Path('tests')):
        raise RuntimeError(f'Duplicate test names found ({duplciates}). See above for details.')  # noqa: EM102


KM_HELP = {
    # See: https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests
    'keyword': 'Only run tests that match the string pattern',
    'marker': 'Only run tests matching given mark expression',
}


@task(
    default=True,
    help={
        'min_cover': 'Fail if coverage less than threshold',
        **KM_HELP,
    },
)
def pytest(ctx: Context, *, keyword: str = '', marker: str = '', min_cover: int = 0) -> None:
    """Run pytest with default arguments.

    Additional arguments can be set in the environment variable 'PYTEST_ADDOPTS'

    """
    pkg_name = read_package_name()
    durations = '--durations=25 --durations-min="0.1"'
    _inner_task(
        ctx,
        cli_args=f' --cov={pkg_name} --cov-branch --cov-report=term-missing {durations}',
        keyword=keyword,
        marker=marker,
        min_cover=min_cover,
    )


@task(help=KM_HELP)
def watch(ctx: Context, *, keyword: str = '', marker: str = '') -> None:
    """Run pytest with polling and optimized to stop on first error."""
    _inner_task(
        ctx,
        cli_args=' --failed-first --new-first --exitfirst -vv --no-cov',
        keyword=keyword,
        marker=marker,
        command='ptw . --now',
        run_as_module=False,
    )


@task(
    help={
        'min_cover': 'Fail if coverage less than threshold',
        'out_dir': 'Optional path to coverage directory. Typically ".cover" or "releases/tests"',
        'view': 'If True, open the created files',
    },
)
def coverage(ctx: Context, *, min_cover: int = 0, out_dir: Optional[str] = None, view: bool = False) -> None:
    """Generate useful coverage outputs after running pytest.

    Creates `coverage.json` used in `doc.build`

    """
    pkg_name = read_package_name()
    run(ctx, f'{python_m()} coverage run --branch --source={pkg_name} --module pytest ./tests')

    cov_dir = Path(out_dir or from_ctx(ctx, 'test', 'out_dir'))
    cov_dir.mkdir(exist_ok=True, parents=True)
    print()  # noqa: T201

    fail_under = f' --fail-under={min_cover}' if min_cover > 0 else ''
    for cli_args in (
        f'report --show-missing{fail_under}',  # Write to STDOUT
        f'html --directory={cov_dir}',  # Write to HTML
        'json',  # Create coverage.json file for "_handle_coverage"
    ):
        run(ctx, f'{python_m()} coverage {cli_args}')

    if view:  # pragma: no cover
        open_in_browser(cov_dir / 'index.html')
