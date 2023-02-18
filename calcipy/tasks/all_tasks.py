"""Tasks can be imported piecemeal or imported in their entirety from here."""

from invoke import Collection, Context
from shoal.cli import task

from . import lint, nox, stale, tags, test, types
from .defaults import DEFAULTS
from .lint import fix
from .nox import default as nox_default
from .stale import check_for_stale_packages
from .tags import collect_code_tags
from .types import mypy as types_mypy

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = Collection('')
ns.add_collection(lint)
ns.add_collection(nox)
ns.add_collection(stale)
ns.add_collection(tags)
ns.add_collection(test)
ns.add_collection(types)


@task(  # type: ignore[misc]
    pre=[
        collect_code_tags,
        # cl_write,
        # lock,
        nox_default,
        fix,
        # document,
        check_for_stale_packages,
        # pre_commit_hooks,
        # lint_project,
        # static_checks,
        # security_checks,
        types_mypy,
    ],
)
def main(_ctx: Context) -> None:
    """Main task for the core workflow."""
    ...

ns.add_task(main)

ns.configure(DEFAULTS)

# TODO: Reference Below Examples
# Great Expectations: https://github.com/great-expectations/great_expectations/blob/ddcd2da2689f13d82ccb88f7e9670b1c82e01765/tasks.py#L216-L218
# Official: https://github.com/pyinvoke/invocations/blob/main/invocations/testing.py
# Getting git top-level directory: https://github.com/Neoxelox/superinvoke/blob/c0b96dab095e260cd3cb2d492183f1a6d64321b4/superinvoke/extensions/context.py#LL75-L77C60
# Another: https://github.com/neozenith/invoke-common-tasks
