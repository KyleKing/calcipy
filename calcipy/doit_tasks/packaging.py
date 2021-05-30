"""doit Packaging Utilities."""

import json
from pathlib import Path
from typing import List, Optional, Dict

import attr
import pendulum
import requests
import toml
from beartype import beartype
from doit.tools import Interactive
from pendulum import DateTime

from .base import debug_task, echo
from .doit_globals import DG, DoitTask


@attr.s(auto_attribs=True, kw_only=True)
class _HostedPythonPackage():  # noqa: H601
    """Representative information for a python package hosted on some domain."""

    domain: str = 'https://pypi.org/pypi/{name}/{version}/json'
    name: str
    version: str
    datetime: Optional[DateTime] = None
    latest_version: str = ''
    latest_datetime: str = ''


_REL_DATE_LOCK = DG.meta.path_project / '.pypi_cache.lock'


def _get_release_date(package: _HostedPythonPackage) -> _HostedPythonPackage:
    res = requests.get(package.domain.format(name=package.name, version=package.version))
    releases = res.json()['releases']
    package.datetime = pendulum.parse(releases[package.version][0]['upload_time_iso_8601'])

    # TODO: Maybe also get latest version?
    package.latest_version = [*releases.keys()][-1]
    package.latest_datetime = pendulum.parse(releases[package.latest_version][0]['upload_time_iso_8601'])
    return package


def cache_release_dates(packages: List[_HostedPythonPackage], stale_years: float) -> None:
    """Store the most recent release dates per package."""

    # TODO: Read dictionary from last lock {name: {version: ..., date: ...}}
    old_cache: Dict[str, Dict[str, str]] = json.loads(_REL_DATE_LOCK.read_text())

    # TODO: Iterate packages, if old date is beyond stale or the version (!=) changed, make request
    stale_cutoff = pendulum.now().subtract(years=stale_years)
    new_cache = {}
    for package in packages:
        meta_data = old_cache[package.name]
        cached_package = _HostedPythonPackage(name=package.name, **meta_data)
        if package.version != cached_package.datetime < stale_cutoff:
            new_cache[package.name] = _get_release_date(package)

    # TODO: This new dictionary will not have any packages that have been uninstalled
    _REL_DATE_LOCK.write_text(json.dumps(new_cache))

    # TODO: Raise error if stale packages were found!


def _read_packages(path_lock: Path) -> List[_HostedPythonPackage]:
    lock = toml.loads(path_lock.read_text())
    for dependency in lock['dep?']:  # TODO: Also check dev - see cb
        _HostedPythonPackage(domain=dependency['url?'], name=dependency['name'], version=dependency['version'])

# # TODO: tests
# packages = [_HostedPythonPackage(name='twine', version='3.4.1')]
# cache_release_dates(packages)


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
