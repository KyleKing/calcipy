"""Test doit_tasks/packaging.py."""

import pytest

from calcipy.doit_tasks.packaging import _HostedPythonPackage, _read_packages, task_publish, _get_release_date, cache_release_dates

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
def test_cache_release_dates():
    """Test cache_release_dates."""
    packages = [_HostedPythonPackage(name='twine', version='2.0.0')]

    result = cache_release_dates(packages, stale_years=2)

    assert len(result) > 20

# --record-mode=rewrite
# TBD: Check for all stale packages and print summary! Maybe plot too?
