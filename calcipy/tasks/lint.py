"""Lint CLI."""

from contextlib import suppress

from beartype import beartype
from beartype.typing import Optional
from corallium.file_helpers import read_package_name
from corallium.log import logger
from invoke.context import Context

from ..cli import task
from ..invoke_helpers import run
from .executable_utils import PRE_COMMIT_MESSAGE, check_installed, python_dir, python_m

# ==============================================================================
# Linting


@beartype
def _inner_task(
    ctx: Context,
    *,
    command: str,
    cli_args: str = '',
    run_as_module: bool = True,
    target: Optional[str] = None,
) -> None:
    """Shared task logic."""
    file_args = []
    with suppress(AttributeError):
        file_args = ctx.config.gto.file_args
    if file_args:
        target = ' '.join([str(_a) for _a in file_args])
    elif target is None:
        target = f'./{read_package_name()} ./tests'

    cmd = f'{python_m()} {command}' if run_as_module else f'{python_dir()}/{command}'
    run(ctx, f'{cmd} {target} {cli_args}'.strip())


@task(default=True)
def check(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, command='ruff check')


@task()
def autopep8(ctx: Context) -> None:
    """Run autopep8.

    FYI: This is temporary until ruff implements white space rules
    https://github.com/charliermarsh/ruff/issues/970

    """
    cli_args = '--aggressive --recursive --in-place --max-line-length=120'
    _inner_task(ctx, command='autopep8', cli_args=cli_args)


@task(pre=[autopep8])
def fix(ctx: Context) -> None:
    """Run ruff and apply fixes."""
    _inner_task(ctx, command='ruff check', cli_args='--fix')


@task()
def watch(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, command='ruff check', cli_args='--watch --show-source')


@task()
def flake8(ctx: Context) -> None:
    """Run flake8."""
    _inner_task(ctx, command='flake8', run_as_module=False)


@task(
    help={
        'report': 'if provided, show the pylint summary report',
    },
)
def pylint(ctx: Context, *, report: bool = False) -> None:
    """Run pylint."""
    cli_args = '--report=y' if report else ''
    _inner_task(ctx, command='pylint', cli_args=cli_args)


# ==============================================================================
# Security


@task()
def security(ctx: Context) -> None:
    """Attempt to identify possible security vulnerabilities."""
    logger.text('Note: Selectively override bandit with "# nosec"', is_header=True)
    pkg_name = read_package_name()
    run(ctx, f'{python_dir()}/bandit --recursive {pkg_name} -s B101')

    # See additional semgrep rules at:
    #   https://semgrep.dev/explore
    #   https://github.com/returntocorp/semgrep-rules/tree/develop/python
    #   https://awesomeopensource.com/project/returntocorp/semgrep-rules?categorypage=45
    semgrep_configs = ' '.join([  # noqa: FLY002
        '--config=p/ci',
        '--config=p/default',
        '--config=p/security-audit',
        '--config=r/bash',
        '--config=r/contrib',
        '--config=r/fingerprints',
        '--config=r/generic',
        '--config=r/json',
        '--config=r/python',
        '--config=r/terraform',
        '--config=r/yaml',
        '--exclude-rule=yaml.github-actions.security.third-party-action-not-pinned-to-commit-sha.third-party-action-not-pinned-to-commit-sha',
    ])
    logger.text('Note: Selectively override semgrep with "# nosem"', is_header=True)
    run(ctx, f'{python_dir()}/semgrep ci --autofix {semgrep_configs}')


# ==============================================================================
# Pre-Commit


@task(
    help={
        'no_update': 'Skip updating the pre-commit hooks',
    },
)
def pre_commit(ctx: Context, *, no_update: bool = False) -> None:
    """Run pre-commit."""
    check_installed(ctx, executable='pre-commit', message=PRE_COMMIT_MESSAGE)

    run(ctx, 'pre-commit install')
    if not no_update:
        run(ctx, 'pre-commit autoupdate')

    all_hook_stages = [
        'commit', 'merge-commit', 'push', 'prepare-commit-msg', 'commit-msg', 'post-checkout',
        'post-commit', 'post-merge', 'post-rewrite', 'manual',
    ]
    stages_cli = ' '.join(f'--hook-stage {stg}' for stg in all_hook_stages)
    run(ctx, f'pre-commit run --all-files {stages_cli}')
