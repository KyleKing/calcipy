"""Lint CLI."""

from contextlib import suppress

from beartype.typing import Optional
from corallium.file_helpers import read_package_name
from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import PRE_COMMIT_MESSAGE, check_installed, python_dir, python_m

# ==============================================================================
# Linting


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
        target = ' '.join([f'"{_a}"' for _a in file_args])
    elif target is None:
        target = f'"./{read_package_name()}" ./tests'

    cmd = f'{python_m()} {command}' if run_as_module else f'{python_dir()}/{command}'
    run(ctx, f'{cmd} {target} {cli_args}'.strip())


@task(default=True)
def check(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, command='ruff check')


@task(
    help={
        'unsafe': 'if provided, attempt even fixes considered unsafe',
    },
)
def fix(ctx: Context, *, unsafe: bool = False) -> None:
    """Run ruff and apply fixes."""
    cli_args = '--fix'
    if unsafe:
        cli_args += ' --unsafe-fixes'
    _inner_task(ctx, command='ruff check', cli_args=cli_args)


@task()
def watch(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, command='ruff check', cli_args='--watch')


# ==============================================================================
# Pre-Commit

ALL_PRE_COMMIT_HOOK_STAGES = [
    'commit',
    'merge-commit',
    'push',
    'prepare-commit-msg',
    'commit-msg',
    'post-checkout',
    'post-commit',
    'post-merge',
    'post-rewrite',
    'manual',
]


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

    stages_cli = ' '.join(f'--hook-stage {stg}' for stg in ALL_PRE_COMMIT_HOOK_STAGES)
    run(ctx, f'pre-commit run --all-files {stages_cli}')
