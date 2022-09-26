"""Test that the wildcard import works as expected."""

from calcipy.doit_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks). # skipcq: PYL-W0614


def test_doit_tasks_imports():
    """Test that the wildcard import for doit tasks only imports tasks."""
    suppress = ['@py_builtins', '@pytest_ar', 'test_doit_tasks_imports']
    constants = ['DOIT_CONFIG_RECOMMENDED', 'TASKS_FULL']

    wc_imports = [_g for _g in globals() if not _g.startswith('_') and _g not in suppress]  # act

    assert all(imp.startswith('task_') or imp in constants for imp in wc_imports)
    assert len(wc_imports) == 39  # FYI: Update if the number of tasks change
