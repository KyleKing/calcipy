"""Nox CLI."""

from beartype import beartype
from beartype.typing import List
from invoke import Context
from shoal import get_logger
from shoal.cli import task

logger = get_logger()


@beartype
def _inner_task(ctx: Context, *, cli_args: List[str]) -> None:
    """Shared task logic."""
    with ctx.cd('.'):  # FYI: can change directory like this
        ctx.run(
            f'poetry run nox --error-on-missing-interpreters {" ".join(cli_args)}',
            echo=True, pty=True,
        )


@task(  # type: ignore[misc]
    default=True,
    help={},
)
def noxfile(ctx: Context) -> None:
    """Run all nox steps from the local noxfile."""
    _inner_task(ctx, cli_args=[])


@beartype
def _gen_task(task_name: str) -> None:
    """Dynamically generate common nox tasks."""

    @task(help=noxfile.help)  # type: ignore[misc]
    def _task(ctx: Context) -> None:
        _inner_task(ctx, cli_args=['--session', task_name])

    _task.__name__ = task_name
    _task.__doc__ = f"""Run {task_name} from the local noxfile."""

    globals()[task_name] = _task


for name in ['test', 'coverage', 'build_check', 'build_dist']:
    _gen_task(name)
