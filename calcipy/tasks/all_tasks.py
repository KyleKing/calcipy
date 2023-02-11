"""Tasks can be imported piecemeal or imported in their entirety from here."""

from . import ctc, nox, pytest, mypy, pyright
from invoke import Collection

# "ns" will be recognized by Collection.from_module(all_tasks)
# https://docs.pyinvoke.org/en/stable/api/collection.html#invoke.collection.Collection.from_module
ns = Collection('')
ns.add_collection(Collection.from_module(ctc))
ns.add_collection(mypy)
ns.add_collection(nox)
ns.add_collection(pyright)
ns.add_collection(pytest)
