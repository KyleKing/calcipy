"""Packaging CLI."""

from corallium import file_helpers  # Required for mocking read_pyproject
from corallium.file_helpers import LOCK, PROJECT_TOML
from corallium.log import logger
from invoke.context import Context

from .. import can_skip  # Required for mocking can_skip.can_skip
from ..cli import task
from ..invoke_helpers import run
from .executable_utils import python_dir


@task()
def install_extras(ctx: Context) -> None:
    """Run poetry install with all extras."""
    poetry_config = file_helpers.read_pyproject()['tool']['poetry']
    extras = (poetry_config.get('extras') or {}).keys()
    run(ctx, ' '.join(['poetry install --sync', *[f'--extras={ex}' for ex in extras]]))


@task()
def lock(ctx: Context) -> None:
    """Ensure poetry.lock is  up-to-date."""
    if can_skip.can_skip(prerequisites=[PROJECT_TOML], targets=[LOCK]):
        return  # Exit early

    run(ctx, 'poetry lock --no-update')


@task(
    help={
        'to_test_pypi': 'Publish to the TestPyPi repository',
    },
)
def publish(ctx: Context, *, to_test_pypi: bool = False) -> None:
    """Build the distributed format(s) and publish."""
    run(ctx, f'{python_dir()}/nox --error-on-missing-interpreters --session build_dist build_check')

    cmd = 'poetry publish'
    if to_test_pypi:
        cmd += ' --repository testpypi'
    run(ctx, cmd)


@task()
def check_licenses(ctx: Context) -> None:
    """Check licenses for compatibility with `licensecheck`."""
    res = run(ctx, 'which licensecheck', warn=True, hide=True)
    if not res or res.exited == 1:
        logger.warning('`licensecheck` not found. installing with pipx')
        run(ctx, 'pipx install licensecheck')
    run(ctx, 'licensecheck')
