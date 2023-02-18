"""Tasks can be imported piecemeal or imported in their entirety from here."""

from beartype import beartype
from beartype.typing import List, Union
from invoke import Call, Collection, Context, Task, call
from shoal.cli import task

from calcipy.log import logger

from . import lint, nox, pack, stale, tags, test, types
from .defaults import DEFAULTS

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = Collection('')
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
def with_progress(items: List[Union[Call, Task]]) -> List[Union[Call, Task]]:
    """Inject intermediary 'progress' tasks."""
    tasks = []
    total = len(items)
    for ix, item in enumerate(items):
        tasks.extend([call(progress, index=ix, total=total), item])
    return tasks


@task(  # type: ignore[misc]
    pre=with_progress(
        [
            tags.collect_code_tags,
            # cl_write,
            pack.lock,
            nox.noxfile,
            lint.fix,
            # > docs.document,
            stale.check_for_stale_packages,
            call(lint.pre_commit, no_update=True),
            lint.security,
            types.mypy,
        ],
    ),  # TODO: Make the list of pipeline tasks interchangeable (support add/remove)
)
def main(_ctx: Context) -> None:
    """Main task pipeline."""
    ...


@task(  # type: ignore[misc]
    pre=with_progress(
        [
            # > cl_bump,  # TODO: Support pre-release: "cl_bump_pre -p rc"
            pack.lock,
            # > docs.document,
            # > docs.deploy_docs,
            pack.publish,
        ],
    ),
)
def release(_ctx: Context) -> None:
    """Release pipeline."""
    ...


ns.add_task(main)
ns.add_task(release)

ns.configure(DEFAULTS)

# PLANNED: Review below examples for additional ideas
# Great Expectations: https://github.com/great-expectations/great_expectations/blob/ddcd2da2689f13d82ccb88f7e9670b1c82e01765/tasks.py#L216-L218
# Official: https://github.com/pyinvoke/invocations/blob/main/invocations/testing.py
# Getting git top-level directory: https://github.com/Neoxelox/superinvoke/blob/c0b96dab095e260cd3cb2d492183f1a6d64321b4/superinvoke/extensions/context.py#LL75-L77C60
# Another: https://github.com/neozenith/invoke-common-tasks
