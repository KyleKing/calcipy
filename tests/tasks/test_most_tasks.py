import sys
from importlib import reload

import calcipy.tasks
from calcipy.tasks import most_tasks


def test_most_tasks_skips_a_namespace_with_uninstalled_extras(monkeypatch):
    """A `None` entry in sys.modules makes the import raise ImportError, as a missing extra does."""
    monkeypatch.setitem(sys.modules, 'corallium.code_tag_collector', None)
    monkeypatch.delitem(sys.modules, 'calcipy.tasks.tags', raising=False)
    monkeypatch.delattr(calcipy.tasks, 'tags', raising=False)

    try:
        namespaces = reload(most_tasks).ns.collections

        assert 'tags' not in namespaces
        assert 'lint' in namespaces
    finally:
        monkeypatch.undo()
        reload(most_tasks)

    assert 'tags' in most_tasks.ns.collections
