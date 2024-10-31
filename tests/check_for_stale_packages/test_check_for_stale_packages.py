import json

import arrow
import pytest
from corallium.file_helpers import LOCK

from calcipy.check_for_stale_packages import check_for_stale_packages
from calcipy.check_for_stale_packages._check_for_stale_packages import (
    CALCIPY_CACHE,
    _get_release_date,
    _HostedPythonPackage,
    _packages_are_stale,
)


@pytest.mark.asyncio
@pytest.mark.vcr
async def test__get_release_date():
    release_year = 2018
    package = _HostedPythonPackage.from_data(
        domain='https://test.pypi.org/pypi/{name}/json',
        name='twine', version='1.11.0rc1',
    )

    result = await _get_release_date(package)

    assert isinstance(result, _HostedPythonPackage)
    assert result.domain == package.domain
    assert result.name == package.name
    assert result.version == package.version
    assert result.latest_version != package.version
    assert result.datetime
    assert result.datetime.year == release_year
    assert result.latest_datetime
    assert result.latest_datetime.year >= release_year


@pytest.mark.vcr
def test__check_for_stale_packages(fix_test_cache):
    path_pack_lock = fix_test_cache / CALCIPY_CACHE.name
    path_pack_lock.write_text(json.dumps({
        'z_package': {
            'name': 'z_package', 'version': '1.2.3',
            'datetime': str(arrow.now()),
        },
    }))
    # Note: write the lock file second because of can_skip
    path_lock = fix_test_cache / LOCK.name
    path_lock.write_text("""
[[package]]
name = "twine"
version = "2.0.0"

[package.dependencies]
tokenize-rt = ">=3.0.1"

[[package]]
name = "z_package"
version = "1.2.3"
""")

    check_for_stale_packages(stale_months=18, path_lock=path_lock, path_cache=path_pack_lock)

    # TODO: Capture logging output and check...
    # ^ Found stale packages that may be a dependency risk:\s+- \d+ [^:]+ ago: twine 2\.0\.0[^\n]+
    assert [*json.loads(path_pack_lock.read_text()).keys()] == ['twine', 'z_package']


@pytest.mark.parametrize(
    ('stale_months', 'expected'),
    [
        (1, True),
        (9999, False),
    ],
)
def test__packages_are_stale(stale_months, expected):
    datetime = arrow.now().shift(months=-2)
    packages = [
        _HostedPythonPackage.from_data(
            name='twine',
            datetime=datetime, version='1.11.0rc1',
            latest_datetime=datetime, latest_version='1.11.0rc1',
        ),
    ]

    result = _packages_are_stale(packages, stale_months=stale_months)

    # TODO: Capture logging output and check...
    assert result is expected
