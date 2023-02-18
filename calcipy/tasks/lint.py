"""Lint CLI."""

from beartype import beartype
from beartype.typing import Optional
from invoke import Context
from shoal import get_logger
from shoal.cli import task

from ..file_helpers import read_package_name

logger = get_logger()

# ==============================================================================
# Ruff


@beartype
def _inner_task(
    ctx: Context,
    *,
    cli_args: str,
    # PLANNED: Consider `f'poetry run absolufy-imports {pkg_name} --never'`
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


# ==============================================================================
# Security


@task()  # type: ignore[misc]
def security(ctx: Context) -> None:
    """Attempt to identify possible security vulnerabilities, but use `# nosec` to selectively override checks."""
    pkg_name = read_package_name()
    ctx.run(f'poetry run bandit --recursive {pkg_name}')

    # PLANNED: Extend semgrep
    #   https://github.com/returntocorp/semgrep-rules/tree/develop/python
    #   https://awesomeopensource.com/project/returntocorp/semgrep-rules?categorypage=45
    semgrep_configs = ' '.join([
        # See more at: https://semgrep.dev/explore
        '--config=p/ci',
        '--config=p/security-audit',
        '--config=r/python.airflow',
        '--config=r/python.attr',
        '--config=r/python.click',
        '--config=r/python.cryptography',
        '--config=r/python.distributed',
        '--config=r/python.docker',
        '--config=r/python.flask',
        '--config=r/python.jinja2',
        '--config=r/python.jwt',
        '--config=r/python.lang',
        '--config=r/python.pycryptodome',
        '--config=r/python.requests',
        '--config=r/python.security',
        '--config=r/python.sh',
        '--config=r/python.sqlalchemy',
        # > dlukeomalley:unchecked-subprocess-call
        # > dlukeomalley:use-assertEqual-for-equality
        # > dlukeomalley:flask-set-cookie
        # > clintgibler:no-exec
    ])
    ctx.run(f'poetry run semgrep ci {semgrep_configs}')


# ==============================================================================
# Pre-Commit


@task(  # type: ignore[misc]
    help={
        'no_update': 'Skip updating the pre-commit hooks',
    },
)
def pre_commit(ctx: Context, *, no_update: bool = False) -> None:
    """Run pre-commit."""
    ctx.run('pre-commit install')
    if not no_update:
        ctx.run('pre-commit autoupdate')
    # PLANNED: get hook stages from `.pre-commit-config.yaml`
    ctx.run('poetry run pre-commit run --all-files --hook-stage commit --hook-stage push')
