"""Lint CLI."""

from contextlib import suppress
from pathlib import Path

from beartype.typing import Optional
from corallium.file_helpers import read_package_name
from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import PRE_COMMIT_MESSAGE, check_installed, python_dir, python_m

# ==============================================================================
# Linting


def _resolve_package_target() -> str:
    """Resolve package directory for src or flat layouts."""
    pkg = read_package_name()
    src_path = Path(f'./src/{pkg}')
    flat_path = Path(f'./{pkg}')
    if src_path.is_dir():
        return f'"{src_path}"'
    if flat_path.is_dir():
        return f'"{flat_path}"'
    return '.'


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
        target = ' '.join([f'"{a_}"' for a_ in file_args])
    elif target is None:
        target = f'{_resolve_package_target()} ./tests'

    cmd = f'{python_m()} {command}' if run_as_module else f'{python_dir() / command}'
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
# prek

ALL_PRE_COMMIT_HOOK_STAGES = [
    'commit-msg',
    'manual',
    'post-checkout',
    'post-commit',
    'post-merge',
    'post-rewrite',
    'pre-commit',
    'pre-merge-commit',
    'pre-push',
    'pre-rebase',
    'prepare-commit-msg',
]


@task(
    help={
        'no_update': 'Skip updating the prek hooks',
    },
)
def pre_commit(ctx: Context, *, no_update: bool = False) -> None:
    """Run prek."""
    check_installed(ctx, executable='prek', message=PRE_COMMIT_MESSAGE)

    run(ctx, 'prek install')
    if not no_update:
        run(ctx, 'prek autoupdate')

    stages_cli = ' '.join(f'--hook-stage {stg}' for stg in ALL_PRE_COMMIT_HOOK_STAGES)
    run(ctx, f'prek run --all-files {stages_cli}')
