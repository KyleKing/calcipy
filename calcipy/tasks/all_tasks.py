"""Tasks can be imported piecemeal or imported in their entirety from here."""

from beartype import beartype
from beartype.typing import Any, List, Union
from corallium.log import logger
from invoke.context import Context
from invoke.tasks import Call

from ..cli import task
from . import cl, doc, lint, nox, pack, stale, tags, test, types
from ._invoke import Collection, DeferedTask, _build_task
from .defaults import new_collection

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = new_collection()
ns.add_collection(Collection.from_module(cl))
ns.add_collection(Collection.from_module(doc))
ns.add_collection(Collection.from_module(lint))
ns.add_collection(Collection.from_module(nox))
ns.add_collection(Collection.from_module(pack))
ns.add_collection(Collection.from_module(stale))
ns.add_collection(Collection.from_module(tags))
ns.add_collection(Collection.from_module(test))
ns.add_collection(Collection.from_module(types))


@task(
    help={
        'message': 'String message to display',
    },
    show_task_info=False,
)
def summary(_ctx: Context, *, message: str) -> None:
    """Summary Task."""
    logger.text(message, is_header=True)


@task(
    help={
        'index': 'Current index (0-indexed)',
        'total': 'Total steps',
    },
    show_task_info=False,
)
def progress(_ctx: Context, *, index: int, total: int) -> None:
    """Progress Task."""
    logger.text('Progress', is_header=True, index=index + 1, total=total)


TaskList = List[Union[Call, DeferedTask]]
"""List of wrapped or normal task functions."""


@beartype
def with_progress(
    items: Any,  # PLANNED: TaskList,
    offset: int = 0,
) -> TaskList:
    """Inject intermediary 'progress' tasks.

    Args:
        items: list of tasks
        offset: Optional offset to shift counters

    """
    task_items = [_build_task(_t) for _t in items]
    message = 'Running tasks: ' + ', '.join([str(_t.__name__) for _t in task_items])
    tasks: TaskList = [summary.with_kwargs(message=message)]

    total = len(task_items) + offset
    for idx, item in enumerate(task_items):
        tasks.extend([progress.with_kwargs(index=idx + offset, total=total), item])
    return tasks


_MAIN_TASKS = [
    lint.fix,
    types.mypy,
    types.pyright,
    nox.noxfile.with_kwargs(session='tests'),  # pyright: ignore[reportGeneralTypeIssues]
    lint.pre_commit.with_kwargs(no_update=True),  # pyright: ignore[reportGeneralTypeIssues]
    lint.security,
    tags.collect_code_tags,
    cl.write,
    pack.lock,
    test.coverage,
    doc.build,
    stale.check_for_stale_packages,
]
_OTHER_TASKS = [
    test.check,
    lint.flake8,
    lint.pylint,
    pack.check_licenses,
    test.step,
]


@task(post=with_progress(_MAIN_TASKS))
def main(_ctx: Context) -> None:
    """Main task pipeline."""


@task(post=with_progress(_OTHER_TASKS))  # pyright: ignore[reportGeneralTypeIssues]
def other(_ctx: Context) -> None:
    """Run tasks that are otherwise not exercised in main."""


@task(
    help=cl.bump.help,
    post=with_progress(
        [  # pyright: ignore[reportGeneralTypeIssues]
            pack.lock,
            doc.build,
            doc.deploy,
            pack.publish,
        ],
        offset=1,
    ),
)
def release(ctx: Context, *, suffix: cl.SuffixT = None) -> None:
    """Release pipeline."""
    cl.bumpz(ctx, suffix=suffix)


ns.add_task(main)
ns.add_task(other)
ns.add_task(release)
