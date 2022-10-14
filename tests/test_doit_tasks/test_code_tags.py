"""Test code_tags.py."""

from calcipy.doit_tasks.code_tags import task_collect_code_tags


def test_task_collect_code_tags(assert_against_cache):
    """Test task_collect_code_tags."""
    result = task_collect_code_tags()

    assert_against_cache(result['actions'])
