"""Test doit_tasks/packaging.py."""

import json

import pendulum
import pytest

from calcipy.doit_tasks.packaging import (
    _PATH_PACK_LOCK, _get_release_date, _HostedPythonPackage, _read_packages,
    find_stale_packages, task_check_for_stale_packages, task_publish,
)

from ..configuration import PATH_TEST_PROJECT


def test_task_publish():
    """Test task_publish."""
    result = task_publish()

    actions = result['actions']
    assert len(actions) == 2
    assert 'poetry run nox -k "build_dist and build_check"' in str(actions[0])
    pytest.skip('Not yet implemented, this is a placeholder test')


def test_read_packages():
    """Test _read_packages."""
    path_lock = PATH_TEST_PROJECT / 'poetry.lock'

    result = _read_packages(path_lock)

    assert len(result) > 20
    assert all(isinstance(pkg, _HostedPythonPackage) for pkg in result)
    assert len(result[0].name) > 3
    assert '.' in result[0].version
    assert result[0].datetime is None
    assert result[0].latest_version == ''
    assert result[0].latest_datetime is None


@pytest.mark.vcr()
def test_get_release_date():
    """Test _get_release_date."""
    package = _HostedPythonPackage(
        domain='https://test.pypi.org/pypi/{name}/{version}/json',
        name='twine', version='1.11.0rc1',
    )

    result = _get_release_date(package)

    assert isinstance(result, _HostedPythonPackage)
    assert result.domain == package.domain
    assert result.name == package.name
    assert result.version == package.version
    assert result.latest_version != package.version
    assert result.datetime.year == 2018
    assert result.latest_datetime.year >= 2018


@pytest.mark.vcr()
def test_find_stale_packages(fix_test_cache):
    """Test find_stale_packages."""
    fake_lock = """
[[package]]
name = "twine"
version = "2.0.0"

[package.dependencies]
tokenize-rt = ">=3.0.1"

[[package]]
name = "z_package"
version = "1.2.3"
"""
    fake_pack_lock = {
        'z_package': {'name': 'z_package', 'version': '1.2.3',
                      'datetime': pendulum.now().to_iso8601_string()},
    }
    path_lock = fix_test_cache / 'poetry.lock'
    path_lock.write_text(fake_lock)
    path_pack_lock = fix_test_cache / _PATH_PACK_LOCK.name
    path_pack_lock.write_text(json.dumps(fake_pack_lock))
    expected_err = r'Found stale packages that may be a dependency risk:\s+- twine 2.0.0[^\n]+\s+'

    with pytest.raises(RuntimeError, match=expected_err):
        find_stale_packages(path_lock, path_pack_lock, stale_months=18)

    assert [*json.loads(path_pack_lock.read_text()).keys()] == ['twine', 'z_package']


def test_task_check_for_stale_packages():
    """Test task_check_for_stale_packages."""
    result = task_check_for_stale_packages()

    actions = result['actions']
    assert len(actions) == 1
    assert isinstance(actions[0][0], type(find_stale_packages))
    assert len(actions[0][1]) == 1
    assert actions[0][1][0].name == 'poetry.lock'
