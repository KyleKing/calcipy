"""doit Packaging Utilities."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import attr
import pendulum
import requests
import toml
from beartype import beartype
from doit.tools import Interactive
from pendulum import DateTime
from pyrate_limiter import Duration, Limiter, RequestRate

from .base import debug_task, echo
from .doit_globals import DG, DoitTask


def _auto_convert(cls, fields):  # noqa: ANN001, ANN202, CCR001 # type: ignore
    """Auto convert datetime attributes from string.

    https://www.attrs.org/en/stable/extending.html#automatic-field-transformation-and-modification

    Args:
        cls: type?
        fields: `_HostedPythonPackageAttribtues`

    Returns:
        results

    """
    results = []
    for field in fields:
        if field.converter is not None:
            results.append(field)
            continue

        if field.type in {Optional[DateTime], DateTime, 'datetime'}:
            converter = (lambda d: pendulum.parse(d) if isinstance(d, str) else d)
        else:
            converter = None
        results.append(field.evolve(converter=converter))

    return results


@attr.s(auto_attribs=True, kw_only=True, field_transformer=_auto_convert)
class _HostedPythonPackage():  # noqa: H601
    """Representative information for a python package hosted on some domain."""

    domain: str = 'https://pypi.org/pypi/{name}/{version}/json'
    name: str
    version: str
    datetime: Optional[DateTime] = None
    latest_version: str = ''
    latest_datetime: Optional[DateTime] = None


_PATH_PACK_LOCK = DG.meta.path_project / '.calcipy_packaging.lock'
"""Path to the packaging lock file."""

# PLANNED: Prevent excess requests to PyPi
#   https://pypi.org/project/pyrate-limiter/
#   https://learn.vonage.com/blog/2020/10/22/respect-api-rate-limits-with-a-backoff-dr/
rate = RequestRate(3, 5 * Duration.SECOND)
limiter = Limiter(rate)
item = 'pypi'


@limiter.ratelimit(item, delay=True, max_delay=10)
def _get_release_date(package: _HostedPythonPackage) -> _HostedPythonPackage:
    """Retrieve release date metadata for the specified package.

    Args:
        package: `_HostedPythonPackage`

    Returns:
        _HostedPythonPackage: updated with release date metadata from API

    """
    # Retrieve the JSON summary for the specified package
    json_url = package.domain.format(name=package.name, version=package.version)
    res = requests.get(json_url)
    releases = res.json()['releases']
    package.datetime = pendulum.parse(releases[package.version][0]['upload_time_iso_8601'])

    # Also retrieve the latest release date of the package looking through all releases
    release_dates = {
        pendulum.parse(release_data[0]['upload_time_iso_8601']): version
        for version, release_data in releases.items()
        if release_data and release_data[0].get('upload_time_iso_8601')
    }
    package.latest_datetime = max([*release_dates.keys()])
    package.latest_version = release_dates[package.latest_datetime]

    return package


def cache_release_dates(packages: List[_HostedPythonPackage], *, stale_years: float) -> None:
    """Store the most recent release dates per package.

    Args:
        packages: list of `_HostedPythonPackage`
        stale_years: float number of years to consider a package "stale"

    """
    # TODO: Refactor - pull out read/write

    # Read the cached packaging information
    if not _PATH_PACK_LOCK.is_file():
        _PATH_PACK_LOCK.write_text('{}')
    old_cache: Dict[str, Dict[str, str]] = json.loads(_PATH_PACK_LOCK.read_text())

    def serialize(inst, field, value):
        if isinstance(value, DateTime):
            return value.to_iso8601_string()
        return value

    # If new or stale, make request to retrieve the latest released version
    stale_cutoff = pendulum.now().subtract(years=stale_years)
    new_cache = {}
    for package in packages:
        meta_data = old_cache.get(package.name)
        if meta_data:
            cached_package = _HostedPythonPackage(**meta_data)
            is_stale = cached_package.datetime and cached_package.datetime < stale_cutoff
            if package.version != cached_package.version or is_stale:
                package = _get_release_date(package)
        else:
            package = _get_release_date(package)
        new_cache[package.name] = attr.asdict(package, value_serializer=serialize)
        new_cache[package.name]['is_stale'] = package.datetime < stale_cutoff

    _PATH_PACK_LOCK.write_text(json.dumps(new_cache, indent=4, separators=(',', ': '), sort_keys=True))

    # TODO: Raise error if stale packages were found!


# def write_cache():


def _read_packages(path_lock: Path) -> List[_HostedPythonPackage]:
    """Read packages from lock file. Currently only support `poetry.lock`, but could support more in the future.

    Args:
        path_lock: Path to the lock file to parse

    Returns:
        List[_HostedPythonPackage]: packages found in the lock file

    """
    if path_lock.name != 'poetry.lock':
        raise NotImplementedError(f'{path_lock.name} is not a currently supported lock type. Try "poetry.lock" instead')

    lock = toml.loads(path_lock.read_text())
    # TBD: Handle non-pypi domains and format the URL accordingly (i.e. TestPyPi, etc.)
    #   domain=dependency['source']['url'] + '{name}/{version}/json'
    return [_HostedPythonPackage(
        name=dependency['name'], version=dependency['version'],
    ) for dependency in lock['package']]


@beartype
def task_publish() -> DoitTask:
    """Build the distributable format(s) and publish.

    > Note: use in conjunction with `task_cl_bump`

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run nox -k "build_dist and build_check"'),
        (echo, ('WARNING: Not implemented yet!', )),  # FIXME: Add upload feature here
    ])
