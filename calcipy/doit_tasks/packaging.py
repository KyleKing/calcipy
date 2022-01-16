"""doit Packaging Utilities."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import attr
import numpy as np
import pendulum
import requests
import tomli
from attrs_strict import type_validator
from beartype import beartype
from doit.tools import Interactive
from loguru import logger
from pendulum import DateTime
from pyrate_limiter import Duration, Limiter, RequestRate

from .base import debug_task
from .doit_globals import DG, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Publish releases


@beartype
def task_check_license() -> DoitTask:
    """Check licenses for compatibility.

    Returns:
        DoitTask: doit task

    """
    return debug_task(['poetry run licensecheck --zero'])


@beartype
def task_lock() -> DoitTask:
    """Ensure poetry.lock and requirements.txt are up-to-date.

    Returns:
        DoitTask: doit task

    """
    path_req = DG.meta.path_project / 'requirements.txt'
    # Ensure that extras are exported as well
    toml_data = tomli.loads(DG.meta.path_toml.read_text())
    # FYI: poetry 'groups' appear to be properly exported with "--dev"
    extras = [*toml_data['tool']['poetry'].get('extras', {}).keys()]
    extras_arg = ' -E '.join([''] + extras) if extras else ''
    task = debug_task([
        'poetry lock --no-update',
        f'poetry export -f {path_req.name} -o {path_req.name}{extras_arg} --dev',
    ])
    task['file_dep'].append(DG.meta.path_toml)
    task['targets'].extend([DG.meta.path_project / 'poetry.lock', path_req])
    return task


@beartype
def _publish_task(publish_args: str = '') -> DoitTask:
    """Create the task with specified options for building and publishing.

    Args:
        publish_args: optional string arguments to pass to `poetry publish`

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run nox --session build_dist build_check'),
        f'poetry publish {publish_args}',
    ])


@beartype
def task_publish() -> DoitTask:
    """Build the distributable format(s) and publish.

    > See the Developer Guide for configuring pypi token
    > Use in conjunction with `task_cl_bump`

    Returns:
        DoitTask: doit task

    """
    return _publish_task()


@beartype
def task_publish_test_pypi() -> DoitTask:
    """Build the distributable format(s) and publish to the TestPyPi repository.

    Returns:
        DoitTask: doit task

    """
    return _publish_task('--repository testpypi')


# ----------------------------------------------------------------------------------------------------------------------
# Check for stale packages


def _auto_convert(_cls, fields):  # type: ignore # noqa: ANN001, ANN202, CCR001
    """Auto convert datetime attributes from string.

    Based on: https://www.attrs.org/en/stable/extending.html#automatic-field-transformation-and-modification

    Args:
        _cls: unused class argument
        fields: `_HostedPythonPackageAttribtues`

    Returns:
        results

    """
    results = []
    for field in fields:
        if field.converter is not None:  # pragma: no cover
            results.append(field)
            continue

        converter: Optional[DateTime] = None
        if field.type in {Optional[DateTime], DateTime, 'datetime'}:
            converter = (lambda d: pendulum.parse(d) if isinstance(d, str) else d)
        results.append(field.evolve(converter=converter))

    return results


@attr.s(auto_attribs=True, kw_only=True, field_transformer=_auto_convert)
class _HostedPythonPackage():  # noqa: H601
    """Representative information for a python package hosted on some domain."""

    domain: str = attr.ib(validator=type_validator(), default='https://pypi.org/pypi/{name}/{version}/json')
    name: str = attr.ib(validator=type_validator())
    version: str = attr.ib(validator=type_validator())
    datetime: Optional[DateTime] = attr.ib(validator=type_validator(), default=None)
    latest_version: str = attr.ib(validator=type_validator(), default='')
    latest_datetime: Optional[DateTime] = attr.ib(validator=type_validator(), default=None)


_PATH_PACK_LOCK = DG.meta.path_project / '.calcipy_packaging.lock'
"""Path to the packaging lock file."""

# HACK: Check that this works then refactor (shouldn't be global)
#   https://pypi.org/project/pyrate-limiter/
#   https://learn.vonage.com/blog/2020/10/22/respect-api-rate-limits-with-a-backoff-dr/
_RATE = RequestRate(3, 5 * Duration.SECOND)
_LIMITER = Limiter(_RATE)
_ITEM = 'pypi'


@beartype
@_LIMITER.ratelimit(_ITEM, delay=True, max_delay=10)
def _get_release_date(package: _HostedPythonPackage) -> _HostedPythonPackage:
    """Retrieve release date metadata for the specified package.

    Args:
        package: `_HostedPythonPackage`

    Returns:
        _HostedPythonPackage: updated with release date metadata from API

    """
    # Retrieve the JSON summary for the specified package
    json_url = package.domain.format(name=package.name, version=package.version)
    res = requests.get(json_url, timeout=30)
    res.raise_for_status()
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


@beartype
def _read_cache(path_pack_lock: Path = _PATH_PACK_LOCK) -> Dict[str, _HostedPythonPackage]:
    """Read the cached packaging information.

    Args:
        path_pack_lock: Path to the lock file. Default is `_PATH_PACK_LOCK`

    Returns:
        Dict[str, _HostedPythonPackage]: the cached packages

    """
    if not path_pack_lock.is_file():
        path_pack_lock.write_text('{}')  # noqa: P103
    old_cache: Dict[str, Dict[str, str]] = json.loads(path_pack_lock.read_text())
    return {
        package_name: _HostedPythonPackage(**meta_data)
        for package_name, meta_data in old_cache.items()
    }


@beartype
def _collect_release_dates(
    packages: List[_HostedPythonPackage],
    old_cache: Optional[Dict[str, _HostedPythonPackage]] = None,
) -> List[_HostedPythonPackage]:
    """Use the cache to retrieve only metadata that needs to be updated.

    Args:
        packages: list of `_HostedPythonPackage`
        old_cache: cache data to compare against to limit network requests

    Returns:
        List[_HostedPythonPackage]: packages with updated release dates

    """
    if old_cache is None:
        old_cache = {}

    updated_packages = []
    for package in packages:
        cached_package = old_cache.get(package.name)
        cached_version = '' if cached_package is None else cached_package.version
        if package.version != cached_version:
            package = _get_release_date(package)
        else:
            package = cached_package
        updated_packages.append(package)
    return updated_packages


@beartype
def _write_cache(updated_packages: List[_HostedPythonPackage], path_pack_lock: Path = _PATH_PACK_LOCK) -> None:
    """Read the cached packaging information.

    Args:
        updated_packages: updated packages to store
        path_pack_lock: Path to the lock file. Default is `_PATH_PACK_LOCK`

    """
    def serialize(_inst, _field, value):  # noqa: ANN001, ANN201
        return value.to_iso8601_string() if isinstance(value, DateTime) else value

    new_cache = {pack.name: attr.asdict(pack, value_serializer=serialize) for pack in updated_packages}
    pretty_json = json.dumps(new_cache, indent=4, separators=(',', ': '), sort_keys=True)
    path_pack_lock.write_text(pretty_json + '\n')


@beartype
def _read_packages(path_lock: Path) -> List[_HostedPythonPackage]:
    """Read packages from lock file. Currently only support `poetry.lock`, but could support more in the future.

    Args:
        path_lock: Path to the lock file to parse

    Returns:
        List[_HostedPythonPackage]: packages found in the lock file

    Raises:
        NotImplementedError: if a lock file other that the poetry lock file is used

    """
    if path_lock.name != 'poetry.lock':
        raise NotImplementedError(f'{path_lock.name} is not a currently supported lock type. Try "poetry.lock" instead')

    lock = tomli.loads(path_lock.read_text())
    # TBD: Handle non-pypi domains and format the URL accordingly (i.e. TestPyPi, etc.)
    # > domain=dependency['source']['url'] + '{name}/{version}/json'
    return [
        _HostedPythonPackage(
            name=dependency['name'], version=dependency['version'],
        ) for dependency in lock['package']
    ]


@beartype
def _check_for_stale_packages(packages: List[_HostedPythonPackage], *, stale_months: int) -> None:
    """Check for stale packages. Raise error and log all stale versions found.

    Args:
        packages: List of packages
        stale_months: cutoff in months for when a package might be stale enough to be a risk

    """
    def format_package(pack: _HostedPythonPackage) -> str:
        delta = f'{now.diff(pack.datetime).in_months()} months ago:'
        latest = '' if pack.version == pack.latest_version else f' (*New version available: {pack.latest_version}*)'
        return f'- {delta} {pack.name} {pack.version}{latest}'

    now = pendulum.now()
    stale_cutoff = now.subtract(months=stale_months)
    stale_packages = [pack for pack in packages if pack.datetime < stale_cutoff]
    if stale_packages:
        stale_list = '\n'.join(map(format_package, sorted(stale_packages, key=lambda x: x.datetime)))
        logger.warning(f'Found stale packages that may be a dependency risk:\n\n{stale_list}\n\n')
    else:
        max_months = np.amax([now.diff(pack.datetime).in_months() for pack in packages])
        logger.warning(f'The oldest package was released {max_months} months ago (stale is >{stale_months} months)\n')


@beartype
def find_stale_packages(
    path_lock: Path, path_pack_lock: Path = _PATH_PACK_LOCK,
    *, stale_months: int = 48,
) -> None:
    """Read the cached packaging information.

    Args:
        path_lock: Path to the lock file to parse
        path_pack_lock: Path to the lock file. Default is `_PATH_PACK_LOCK`
        stale_months: cutoff in months for when a package might be stale enough to be a risk. Default is 48

    """
    packages = _read_packages(path_lock)
    old_cache = _read_cache(path_pack_lock)
    updated_packages = _collect_release_dates(packages, old_cache)
    _write_cache(updated_packages, path_pack_lock)
    _check_for_stale_packages(updated_packages, stale_months=stale_months)


@beartype
def task_check_for_stale_packages() -> DoitTask:
    """Check for stale packages.

    Returns:
        DoitTask: doit task

    """
    path_lock = DG.meta.path_project / 'poetry.lock'
    path_pack_lock = _PATH_PACK_LOCK
    task = debug_task([
        (find_stale_packages, (path_lock, path_pack_lock), {'stale_months': 48}),
        Interactive('poetry run pip-check --cmd="poetry run pip" --hide-unchanged'),
    ])
    task['file_dep'].append(path_lock)
    task['targets'].append(path_pack_lock)
    return task
