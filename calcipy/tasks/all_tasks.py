"""Tasks can be imported piecemeal or imported in their entirety from here."""

from beartype.typing import Any, List, Union
from corallium.log import LOGGER
from invoke.context import Context
from invoke.tasks import Call

from calcipy.cli import task
from calcipy.collection import DeferredTask, _build_task

from . import cl, doc, lint, nox, pack, tags, test, types
from .most_tasks import ns


@task(
    help={
        'message': 'String message to display',
    },
    show_task_info=False,
)
def summary(_ctx: Context, *, message: str) -> None:
    """Summary Task."""
    LOGGER.text(message, is_header=True)


@task(
    help={
        'index': 'Current index (0-indexed)',
        'total': 'Total steps',
    },
    show_task_info=False,
)
def progress(_ctx: Context, *, index: int, total: int) -> None:
    """Progress Task."""
    LOGGER.text('Progress', is_header=True, index=index + 1, total=total)


TaskList = List[Union[Call, DeferredTask]]
"""List of wrapped or normal task functions."""


def with_progress(items: Any, offset: int = 0) -> TaskList:
    """Inject intermediary 'progress' tasks.

    Args:
        items: list of tasks
        offset: Optional offset to shift counters

    Returns:
        List of tasks with progress indicators interspersed.

    """
    task_items = [_build_task(t_) for t_ in items]
    message = 'Running tasks: ' + ', '.join([str(t_.__name__) for t_ in task_items])
    tasks: TaskList = [summary.with_kwargs(message=message)]  # pyright: ignore[reportFunctionMemberAccess]

    total = len(task_items) + offset
    for idx, item in enumerate(task_items):
        tasks += [
            progress.with_kwargs(index=idx + offset, total=total),  # pyright: ignore[reportFunctionMemberAccess]
            item,
        ]
    return tasks


_MAIN_TASKS = [
    lint.fix,
    types.mypy,
    types.pyright,
    test.coverage,
    cl.write,
    doc.build,
]
_OTHER_TASKS = [
    lint.pre_commit.with_kwargs(no_update=True),  # pyright: ignore[reportFunctionMemberAccess]
    nox.noxfile.with_kwargs(session='tests'),  # pyright: ignore[reportFunctionMemberAccess]
    pack.lock,
    tags.collect_code_tags,
    test.check,  # Expected to fail for calcipy
]


@task(post=with_progress(_MAIN_TASKS))
def main(_ctx: Context) -> None:
    """Run main task pipeline."""


@task(post=with_progress(_OTHER_TASKS))
def other(_ctx: Context) -> None:
    """Run tasks that are otherwise not exercised in main."""


@task(
    help=cl.bump.help,  # pyright: ignore[reportFunctionMemberAccess]
    post=with_progress(
        [
            pack.lock,
            doc.build,
            doc.deploy,
        ],
        offset=1,
    ),
)
def release(ctx: Context, *, suffix: cl.SuffixT = None) -> None:
    """Run release pipeline."""
    cl.bumpz(ctx, suffix=suffix)


ns.add_task(main)
ns.add_task(other)
ns.add_task(release)

__all__ = ('ns',)
