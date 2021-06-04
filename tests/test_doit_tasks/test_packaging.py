"""Test doit_tasks/packaging.py."""

import json
import re
from collections import defaultdict

import loguru
import pendulum
import pytest

from calcipy.doit_tasks.packaging import (
    _PATH_PACK_LOCK, _get_release_date, _HostedPythonPackage, _read_packages,
    find_stale_packages, task_check_for_stale_packages, task_publish, task_publish_test_pypi,
)

from ..configuration import PATH_TEST_PROJECT


class MockLogger:  # noqa: H601

    logs = defaultdict(list)

    def warning(self, message: str, **kwargs):
        self.logs['warnings'].append({'message': message, 'kwargs': kwargs})


def test_task_publish():
    """Test task_publish."""
    result = task_publish()

    actions = result['actions']
    assert len(actions) == 2
    assert 'poetry run nox --session build_dist build_check' in str(actions[0])
    assert 'poetry publish' in str(actions[1])


def test_task_publish_test_pypi():
    """Test task_publish_test_pypi."""
    result = task_publish_test_pypi()

    actions = result['actions']
    assert len(actions) == 2
    assert 'poetry run nox --session build_dist build_check' in str(actions[0])
    assert 'poetry publish --repository testpypi' in str(actions[1])


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
def test_find_stale_packages(fix_test_cache, monkeypatch):
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
        'z_package': {
            'name': 'z_package', 'version': '1.2.3',
            'datetime': pendulum.now().to_iso8601_string(),
        },
    }
    path_lock = fix_test_cache / 'poetry.lock'
    path_lock.write_text(fake_lock)
    path_pack_lock = fix_test_cache / _PATH_PACK_LOCK.name
    path_pack_lock.write_text(json.dumps(fake_pack_lock))
    expected_err = r'Found stale packages that may be a dependency risk:\s+- \d+ months ago: twine 2\.0\.0[^\n]+'
    mock_logger = MockLogger()
    monkeypatch.setattr(loguru.logger, 'warning', mock_logger.warning)

    find_stale_packages(path_lock, path_pack_lock, stale_months=18)

    assert len(mock_logger.logs['warnings']) == 1
    assert re.match(expected_err, mock_logger.logs['warnings'][-1]['message'])
    assert mock_logger.logs['warnings'][-1]['kwargs'] == {}
    assert [*json.loads(path_pack_lock.read_text()).keys()] == ['twine', 'z_package']


def test_task_check_for_stale_packages():
    """Test task_check_for_stale_packages."""
    result = task_check_for_stale_packages()

    actions = result['actions']
    assert len(actions) == 2
    assert isinstance(actions[0][0], type(find_stale_packages))
    assert len(actions[0][1]) == 2
    assert actions[0][1][0].name == 'poetry.lock'
    assert actions[0][1][1].name == _PATH_PACK_LOCK.name
    assert actions[0][2] == {'stale_months': 48}
    assert 'poetry run pip list --outdated' in str(actions[1])
