"""Tasks can be imported piecemeal or imported in their entirety from here."""

from beartype import beartype
from beartype.typing import List, Union
from corallium.log import logger
from invoke import Call, Context, Task, call

from ..cli import task
from . import cl, doc, lint, nox, pack, stale, tags, test, types
from .defaults import new_collection

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = new_collection()
ns.add_collection(cl)
ns.add_collection(doc)
ns.add_collection(lint)
ns.add_collection(nox)
ns.add_collection(pack)
ns.add_collection(stale)
ns.add_collection(tags)
ns.add_collection(test)
ns.add_collection(types)


@task(
    help={
        'message': 'String message to display',
    },
)
def summary(_ctx: Context, *, message: str) -> None:
    """Summary Task."""
    print('')  # noqa: T201
    logger.text(message, is_header=True)
    print('')  # noqa: T201


@task(
    help={
        'index': 'Current index (0-indexed)',
        'total': 'Total steps',
    },
)
def progress(_ctx: Context, *, index: int, total: int) -> None:
    """Progress Task."""
    print('')  # noqa: T201
    logger.text('Progress', is_header=True, index=index + 1, total=total)
    print('')  # noqa: T201


@beartype
def with_progress(
    items: List[Union[Call, Task]],
    offset: int = 0,
) -> List[Union[Call, Task]]:
    """Inject intermediary 'progress' tasks.

    Args:
        items: list of tasks
        offset: Optional offset to shift counters

    """
    message = 'Running tasks: ' + ', '.join([str(_t.__name__) for _t in items])
    tasks = [call(summary, message=message)]
    total = len(items) + offset
    for ix, item in enumerate(items):
        tasks.extend([call(progress, index=ix + offset, total=total), item])  # pyright: ignore[reportGeneralTypeIssues]
    return tasks  # pyright: ignore[reportGeneralTypeIssues]


_MAIN_TASKS = [
    lint.fix,
    types.mypy,
    call(nox.noxfile, session='tests'),  # pyright: ignore[reportGeneralTypeIssues]
    call(lint.pre_commit, no_update=True),  # pyright: ignore[reportGeneralTypeIssues]
    lint.security,
    tags.collect_code_tags,
    cl.write,
    pack.lock,
    test.coverage,
    doc.build,
    stale.check_for_stale_packages,
]

# TODO: Can the main tasks be extended? Maybe by adding a new 'main' task?'


@task(
    post=with_progress(_MAIN_TASKS),
)
def main(_ctx: Context) -> None:
    """Main task pipeline."""
    logger.text('Starting', tasks=[_t.__name__ for _t in _MAIN_TASKS])


_OTHER_TASKS = [
    lint.flake8,
    lint.pylint,
    pack.check_licenses,
    test.step,
    types.pyright,
]


@task(
    post=with_progress(_OTHER_TASKS),  # pyright: ignore[reportGeneralTypeIssues]
)
def other(_ctx: Context) -> None:
    """Run tasks that are otherwise not exercised in main."""
    logger.text('Starting', tasks=[_t.__name__ for _t in _OTHER_TASKS])


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

# PLANNED: Review below examples for additional ideas
# Great Expectations: https://github.com/great-expectations/great_expectations/blob/ddcd2da2689f13d82ccb88f7e9670b1c82e01765/tasks.py#L216-L218
# Official: https://github.com/pyinvoke/invocations/blob/main/invocations/testing.py
# Getting git top-level directory: https://github.com/Neoxelox/superinvoke/blob/c0b96dab095e260cd3cb2d492183f1a6d64321b4/superinvoke/extensions/context.py#LL75-L77C60
# Another: https://github.com/neozenith/invoke-common-tasks
