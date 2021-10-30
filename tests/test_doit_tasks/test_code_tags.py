"""Test code_tags.py."""

from calcipy.code_tag_collector import write_code_tag_file
from calcipy.doit_tasks.code_tags import task_collect_code_tags


def test_task_collect_code_tags():
    """Test task_collect_code_tags."""
    result = task_collect_code_tags()

    actions = result['actions']
    assert len(actions) == 1
    assert isinstance(actions[0][0], type(write_code_tag_file))
