"""Subset of tasks for `pre-commit`."""

from . import lint
from .defaults import new_collection

ns = new_collection()
ns.add_collection(lint)
