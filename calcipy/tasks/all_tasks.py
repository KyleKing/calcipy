"""Tasks can be imported piecemeal or imported in their entirety from here."""

from beartype import beartype
from beartype.typing import List, Union
from invoke import Call, Collection, Context, Task, call
from shoal.cli import task

from ..log import logger
from . import cl, doc, lint, nox, pack, stale, tags, test, types
from .defaults import DEFAULTS

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = Collection('')
ns.add_collection(cl)
ns.add_collection(doc)
ns.add_collection(lint)
ns.add_collection(nox)
ns.add_collection(pack)
ns.add_collection(stale)
ns.add_collection(tags)
ns.add_collection(test)
ns.add_collection(types)


@task(  # type: ignore[misc]
    help={
        'index': 'Current index (0-indexed)',
        'total': 'Total steps',
    },
)
def progress(_ctx: Context, *, index: int, total: int) -> None:
    """Main task pipeline."""
    if index > 0:
        print('')  # noqa: T201
    logger.info('Progress', index=index + 1, total=total)


@beartype
def with_progress(items: List[Union[Call, Task]],
                  offset: int = 0) -> List[Union[Call, Task]]:
    """Inject intermediary 'progress' tasks.

    Args:
        items: list of tasks
        offset: Optional offset to shift counters

    """
    tasks = []
    total = len(items) + offset
    for ix, item in enumerate(items):
        tasks.extend([call(progress, index=ix + offset, total=total), item])
    return tasks


_MAIN_TASKS = [
    lint.fix,
    types.mypy,
    call(nox.noxfile, session='tests'),
    call(lint.pre_commit, no_update=True),
    lint.security,
    tags.collect_code_tags,
    cl.write,
    pack.lock,
    test.write_json,
    doc.build,
    stale.check_for_stale_packages,
]

# TODO: Can the main tasks be extended? Maybe by adding a new 'main' task?'


@task(  # type: ignore[misc]
    post=with_progress(_MAIN_TASKS),
)
def main(_ctx: Context) -> None:
    """Main task pipeline."""
    logger.info('Starting', tasks=[_t.__name__ for _t in _MAIN_TASKS])


_OTHER_TASKS = [
    lint.flake8,
    lint.pylint,
    pack.check_licenses,
    test.step,
    types.pyright,
]


@task(  # type: ignore[misc]
    post=with_progress(_OTHER_TASKS),
)
def other(_ctx: Context) -> None:
    """Run tasks that are otherwise not exercised in main."""
    logger.info('Starting', tasks=[_t.__name__ for _t in _OTHER_TASKS])


@task(  # type: ignore[misc]
    help=cl.bump.help,
    post=with_progress(
        [
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

ns.configure(DEFAULTS)

# PLANNED: Review below examples for additional ideas
# Great Expectations: https://github.com/great-expectations/great_expectations/blob/ddcd2da2689f13d82ccb88f7e9670b1c82e01765/tasks.py#L216-L218
# Official: https://github.com/pyinvoke/invocations/blob/main/invocations/testing.py
# Getting git top-level directory: https://github.com/Neoxelox/superinvoke/blob/c0b96dab095e260cd3cb2d492183f1a6d64321b4/superinvoke/extensions/context.py#LL75-L77C60
# Another: https://github.com/neozenith/invoke-common-tasks
