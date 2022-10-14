"""Test doit_tasks/test.py."""

from calcipy.doit_tasks.test import (
    task_check_types, task_coverage, task_open_test_docs, task_ptw_current, task_ptw_ff, task_ptw_marker,
    task_ptw_not_interactive, task_test, task_test_all, task_test_keyword, task_test_marker,
)


def test_task_test(assert_against_cache):
    """Test task_test."""
    result = task_test()

    assert_against_cache(result)


def test_task_test_all(assert_against_cache):
    """Test task_test_all."""
    result = task_test_all()

    assert_against_cache(result)


def test_task_test_marker(assert_against_cache):
    """Test task_test_marker."""
    result = task_test_marker()

    assert_against_cache(result)


def test_task_test_keyword(assert_against_cache):
    """Test task_test_keyword."""
    result = task_test_keyword()

    assert_against_cache(result)


def test_task_coverage(assert_against_cache):
    """Test task_coverage."""
    result = task_coverage()

    assert_against_cache(result)


def test_task_check_types(assert_against_cache):
    """Test task_check_types."""
    result = task_check_types()

    # assert 2 <= len(actions) > 1
    # assert str(actions[0]).startswitch('poetry run ')
    assert_against_cache(result)  # FIXME: Revisit. Seems unstable


def test_task_open_test_docs(assert_against_cache):
    """Test task_open_test_docs."""
    result = task_open_test_docs()

    # assert 3 <= len(actions) > 2
    assert_against_cache(result)  # FIXME: Revisit. Seems unstable


def test_task_ptw_not_interactive(assert_against_cache):
    """Test task_ptw_not_interactive."""
    result = task_ptw_not_interactive()

    assert_against_cache(result)


def test_task_ptw_ff(assert_against_cache):
    """Test task_ptw_ff."""
    result = task_ptw_ff()

    assert_against_cache(result)


def test_task_ptw_current(assert_against_cache):
    """Test task_ptw_current."""
    result = task_ptw_current()

    assert_against_cache(result)


def test_task_ptw_marker(assert_against_cache):
    """Test task_ptw_marker."""
    result = task_ptw_marker()

    assert_against_cache(result)
