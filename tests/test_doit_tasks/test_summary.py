"""Test summary."""

from calcipy.doit_tasks.summary_reporter import _format_task_summary, _TaskExitCode, _TaskSumary


def test_format_task_summary():
    """Test _format_task_summary."""
    task_summary = _TaskSumary(name='a_task', exit_code=_TaskExitCode.PASS)

    result = _format_task_summary(task_summary)

    assert task_summary.name in result
    assert 'success' in result
