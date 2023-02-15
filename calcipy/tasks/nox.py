"""Testing CLI."""

import logging

from beartype import beartype
from beartype.typing import List
from invoke import Context, task
from shoal import get_logger
from shoal._log import configure_logger

logger = get_logger()

@beartype
def _inner_task(ctx: Context, *, cli_args: List[str]) -> None:
    """Shared task logic."""

    # FIXME: Move the log configuration logic to shoal
    gto = ctx.config.gto
    print(f'Starting nox with: {gto}')
    print(f'file_args {gto.file_args}')
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(gto.verbose) or logging.ERROR)

    with ctx.cd('.'):  # FYI: can change directory like this
        ctx.run(
            f'poetry run nox --error-on-missing-interpreters {" ".join(cli_args)}',
            # TODO: Is echo always True?
            echo=True,
            # TODO: How to set pty to False for GHA?
            pty=True,
        )


@task(
    default=True,
    help={},
)
# @beartype # FIXME: Make beartype part of my custom "task/tang" wrapper in shoal
def default(ctx: Context) -> None:
    """Run all nox steps from the local noxfile."""
    _inner_task(ctx, cli_args=[])


@beartype
def _gen_task(task_name: str) -> None:
    """Dynamically generate common nox tasks."""

    @task(help=default.help)
    def _task(ctx: Context) -> None:
        _inner_task(ctx, cli_args=[task_name])

    _task.__name__ = task_name
    _task.__doc__ = f"""Run {task_name} from the local noxfile."""

    globals()[task_name] = _task


for name in ['build_check', 'test', 'coverage']:
    _gen_task(name)
