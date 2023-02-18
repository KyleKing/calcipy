"""Lint CLI."""


from beartype import beartype
from beartype.typing import Optional
from invoke import Context
from shoal import get_logger
from shoal.cli import task

from ..file_helpers import read_package_name

logger = get_logger()


@beartype
def _inner_task(
    ctx: Context,
    *,
    cli_args: str,
    command: str = 'python -m ruff check',
    target: Optional[str] = None,
) -> None:
    """Shared task logic."""
    target = f' ./{read_package_name()} ./tests' if target is None else f' {target}'
    ctx.run(
        f'poetry run {command}{target}{cli_args}',
        echo=True, pty=True,
    )


@task(  # type: ignore[misc]
    default=True,
    help={
        # TODO: use file_args! 'ctx.config.gto.file_args'
        'target': 'Optional path to directory or file to watch',
    },
)
def check(ctx: Context, *, target: Optional[str] = None) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, cli_args='', target=target)


@task(help=check.help)  # type: ignore[misc]
def fix(ctx: Context, *, target: Optional[str] = None) -> None:
    """Run ruff and apply fixes."""
    _inner_task(ctx, cli_args=' --fix', target=target)


@task(help=check.help)  # type: ignore[misc]
def watch(ctx: Context, *, target: Optional[str] = None) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, cli_args=' --watch --show-source', target=target)
