"""Packaging CLI."""

from corallium.file_helpers import LOCK, PROJECT_TOML
from corallium.log import logger
from invoke import Context

from .. import can_skip  # Required for mocking can_skip.can_skip
from ..cli import task
from ..invoke_helpers import run
from ..noxfile._noxfile import BASE_NOX_COMMAND


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
    run(ctx, f'{BASE_NOX_COMMAND} --session build_dist build_check')

    cmd = 'poetry publish'
    if to_test_pypi:
        cmd += ' --repository testpypi'
    run(ctx, cmd)


@task()
def check_licenses(ctx: Context) -> None:
    """Check licenses for compatibility with `licensecheck`."""
    res = run(ctx, 'which licensecheck', warn=True, hide=True)
    if res.exited == 1:
        logger.warning('`licensecheck` not found. installing with pipx')
        run(ctx, 'pipx install licensecheck')
    run(ctx, 'licensecheck')
