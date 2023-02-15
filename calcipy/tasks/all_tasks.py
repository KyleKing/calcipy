"""Tasks can be imported piecemeal or imported in their entirety from here."""

from invoke import Collection

from . import ctc, lint, nox, stale, test, types
from .defaults import DEFAULTS

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = Collection('')
ns.add_collection(Collection.from_module(ctc))
ns.add_collection(lint)
ns.add_collection(nox)
ns.add_collection(stale)
ns.add_collection(test)
ns.add_collection(types)

ns.configure(DEFAULTS)

# TODO: Reference Below Examples
# Great Expectations: https://github.com/great-expectations/great_expectations/blob/ddcd2da2689f13d82ccb88f7e9670b1c82e01765/tasks.py#L216-L218
# Official: https://github.com/pyinvoke/invocations/blob/main/invocations/testing.py
# Getting git top-level directory: https://github.com/Neoxelox/superinvoke/blob/c0b96dab095e260cd3cb2d492183f1a6d64321b4/superinvoke/extensions/context.py#LL75-L77C60
# Another: https://github.com/neozenith/invoke-common-tasks
