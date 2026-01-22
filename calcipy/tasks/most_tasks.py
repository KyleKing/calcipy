"""Create a namespace with all tasks that can be imported."""

from contextlib import suppress

from calcipy.collection import Collection

from .defaults import new_collection

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = new_collection()
with suppress(RuntimeError):
    from . import cl

    ns.add_collection(Collection.from_module(cl))
with suppress(RuntimeError):
    from . import doc

    ns.add_collection(Collection.from_module(doc))
with suppress(RuntimeError):
    from . import lint

    ns.add_collection(Collection.from_module(lint))
with suppress(RuntimeError):
    from . import nox

    ns.add_collection(Collection.from_module(nox))
with suppress(RuntimeError):
    from . import pack

    ns.add_collection(Collection.from_module(pack))
with suppress(RuntimeError):
    from . import tags

    ns.add_collection(Collection.from_module(tags))
with suppress(RuntimeError):
    from . import test

    ns.add_collection(Collection.from_module(test))
with suppress(RuntimeError):
    from . import types

    ns.add_collection(Collection.from_module(types))

__all__ = ('ns',)
