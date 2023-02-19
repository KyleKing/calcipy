import arrow
import pytest

from calcipy.check_for_stale_packages._check_for_stale_packages import _HostedPythonPackage, _packages_are_stale


@pytest.mark.parametrize(
    ('stale_months', 'expected'),
    [
        (1, True),
        (9999, False),
    ],
)
def test__check_for_stale_packages(stale_months, expected):
    datetime = arrow.now().shift(months=-2)
    packages = [
        _HostedPythonPackage(
            name='twine',
            datetime=datetime, version='1.11.0rc1',
            latest_datetime=datetime, latest_version='1.11.0rc1',
        ),
    ]

    result = _packages_are_stale(packages, stale_months=stale_months)

    # TODO: Capture logging output and check...
    assert result is expected
