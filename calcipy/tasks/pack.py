"""Packaging CLI."""

from invoke import Context
from shoal import can_skip  # Required for mocking can_skip.can_skip
from shoal.cli import task

from .._log import logger
from ..file_helpers import LOCK, PROJECT_TOML
from ..invoke_helpers import use_pty
from ..noxfile._noxfile import BASE_NOX_COMMAND


@task()  # type: ignore[misc]
def lock(ctx: Context) -> None:
    """Ensure poetry.lock is  up-to-date."""
    if can_skip.can_skip(prerequisites=[PROJECT_TOML], targets=[LOCK]):
        return  # Exit early

    ctx.run('poetry lock --no-update')


@task(  # type: ignore[misc]
    help={
        'to_test_pypi': 'Publish to the TestPyPi repository',
    },
)
def publish(ctx: Context, *, to_test_pypi: bool = False) -> None:
    """Build the distributed format(s) and publish."""
    ctx.run(f'{BASE_NOX_COMMAND} --session build_dist build_check', echo=True, pty=use_pty())

    cmd = 'poetry publish'
    if to_test_pypi:
        cmd += ' --repository testpypi'
    ctx.run(cmd, echo=True, pty=use_pty())


@task()  # type: ignore[misc]
def check_licenses(ctx: Context) -> None:
    """Check licenses for compatibility with `licensecheck`."""
    res = ctx.run('which licensecheck', warn=True, hide=True)
    if res.exited == 1:
        logger.warning('`licensecheck` not found. installing with pipx')
        ctx.run('pipx install licensecheck', echo=True, pty=use_pty())
    ctx.run('licensecheck', echo=True, pty=use_pty())
