"""Test doit_tasks/packaging.py."""

import json
import re
from collections import defaultdict

import arrow
import loguru
import pytest

from calcipy.doit_tasks.packaging import (
    _PATH_PACK_LOCK, _check_for_stale_packages, _get_release_date, _HostedPythonPackage, _read_packages,
    find_stale_packages, task_check_for_stale_packages, task_publish, task_publish_test_pypi,
)

from ..configuration import PATH_TEST_PROJECT


class MockLogger:  # noqa: D101, D102
    # FIXME: Replace MockLogger with a more generic alternative. See:
    #   https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/

    logs = defaultdict(list)

    def warning(self, message: str, **kwargs):
        self.logs['warnings'].append({'message': message, 'kwargs': kwargs})


def test_task_publish(assert_against_cache):
    """Test task_publish."""
    result = task_publish()

    assert_against_cache(result)


def test_task_publish_test_pypi(assert_against_cache):
    """Test task_publish_test_pypi."""
    result = task_publish_test_pypi()

    assert_against_cache(result)


def test_read_packages(assert_against_cache):
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
        domain='https://test.pypi.org/pypi/{name}/json',
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
            'datetime': str(arrow.now()),
        },
    }
    path_lock = fix_test_cache / 'poetry.lock'
    path_lock.write_text(fake_lock)
    path_pack_lock = fix_test_cache / _PATH_PACK_LOCK.name
    path_pack_lock.write_text(json.dumps(fake_pack_lock))
    expected_err = r'Found stale packages that may be a dependency risk:\s+- \d+ [^:]+ ago: twine 2\.0\.0[^\n]+'
    mock_logger = MockLogger()
    monkeypatch.setattr(loguru.logger, 'warning', mock_logger.warning)

    find_stale_packages(path_lock, path_pack_lock, stale_months=18)  # act

    assert len(mock_logger.logs['warnings']) == 1
    assert re.match(expected_err, mock_logger.logs['warnings'][-1]['message'])
    assert mock_logger.logs['warnings'][-1]['kwargs'] == {}
    assert [*json.loads(path_pack_lock.read_text()).keys()] == ['twine', 'z_package']


def test_check_for_stale_packages():
    """Test check_for_stale_packages."""
    packages = [
        _HostedPythonPackage(
            name='twine',
            datetime=arrow.now(), version='1.11.0rc1',
            latest_datetime=arrow.now(), latest_version='1.11.0rc1',
        ),
    ]

    result = _check_for_stale_packages(packages, stale_months=1)

    # TODO: Capture logging output and check...
    assert result is None
    # Also check if not stale
    assert _check_for_stale_packages(packages, stale_months=999) is None


def test_task_check_for_stale_packages(assert_against_cache):
    """Test task_check_for_stale_packages."""
    result = task_check_for_stale_packages()

    assert_against_cache(result)
