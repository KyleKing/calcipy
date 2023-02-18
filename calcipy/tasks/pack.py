"""Packaging CLI."""

from pathlib import Path

from invoke import Context
from shoal.can_skip import can_skip
from shoal.cli import task

from calcipy.log import logger


@task()  # type: ignore[misc]
def lock(ctx: Context) -> None:
    """Ensure poetry.lock is  up-to-date."""
    if can_skip(prerequisites=[Path('pyproject.toml')], targets=[Path('poetry.lock')]):
        return  # Exit early

    ctx.run('poetry lock --no-update')


@task(  # type: ignore[misc]
    help={
        'to_test_pypi': 'Publish to the TestPyPi repository',
    },
)
def publish(ctx: Context, *, to_test_pypi: bool = False) -> None:
    """Build the distributed format(s) and publish."""
    ctx.run('poetry run nox --session build_dist build_check', echo=True, pty=True)

    cmd = 'poetry publish'
    if to_test_pypi:
        cmd += ' --repository testpypi'
    ctx.run(cmd, echo=True, pty=True)


@task()  # type: ignore[misc]
def check_licenses(ctx: Context) -> None:
    """Check licenses for compatibility with `licensecheck`."""
    res = ctx.run('which licensecheck', warn=True, hide=True)
    if res.exited == 1:
        logger.warning('`licensecheck` not found. installing with pipx')
        ctx.run('pipx install licensecheck', echo=True, pty=True)
    ctx.run('licensecheck --zero', echo=True, pty=True)
