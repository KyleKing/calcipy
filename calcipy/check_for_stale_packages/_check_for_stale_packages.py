"""Check for stale packages."""

import json
from pathlib import Path

import arrow
import numpy as np
import requests
from arrow import Arrow
from beartype import beartype
from beartype.typing import Dict, List, Optional, Union
from bidict import bidict
from pydantic import BaseModel, Field, validator
from pyrate_limiter import Duration, Limiter, RequestRate
from shoal import get_logger


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


logger = get_logger()


class _HostedPythonPackage(BaseModel):
    """Representative information for a python package hosted on some domain."""

    # Note: "releases" was removed from the versioned URL: https://warehouse.pypa.io/api-reference/json.html#release
    domain: str = Field(default='https://pypi.org/pypi/{name}/json')
    name: str
    version: str
    datetime: Optional[Arrow] = Field(default=None)
    latest_version: str = Field(default='')
    latest_datetime: Optional[Arrow] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Arrow: str}

    @validator('datetime', 'latest_datetime', pre=True)
    def date_validator(cls, value: Union[str, Arrow]) -> Arrow:  # noqa: F841
        return arrow.get(value)


PACK_LOCK_PATH = Path('.calcipy_packaging.lock')
"""Path to the packaging lock file."""

# HACK: Check that this works then refactor (shouldn't be global)
#   https://pypi.org/project/pyrate-limiter/
#   https://learn.vonage.com/blog/2020/10/22/respect-api-rate-limits-with-a-backoff-dr/
_RATE = RequestRate(3, 5 * Duration.SECOND)
_LIMITER = Limiter(_RATE)
_ITEM = 'pypi'


@beartype
@_LIMITER.ratelimit(_ITEM, delay=True, max_delay=10)  # type: ignore[misc]
def _get_release_date(package: _HostedPythonPackage) -> _HostedPythonPackage:
    """Retrieve release date metadata for the specified package.

    Args:
        package: `_HostedPythonPackage`

    Returns:
        _HostedPythonPackage: updated with release date metadata from API

    """
    # Retrieve the JSON summary for the specified package
    json_url = package.domain.format(name=package.name)
    res = requests.get(json_url, timeout=30)
    res.raise_for_status()
    res_json = res.json()
    releases = res_json['releases']
    if not releases:
        raise RuntimeError(f'Failed to locate "releases" or "urls" from {json_url}: {res_json}')

    # Also retrieve the latest release date of the package looking through all releases
    release_dates = bidict({
        arrow.get(release_data[0]['upload_time_iso_8601']): version
        for version, release_data in releases.items()
        if release_data
    })
    package.datetime = release_dates.inverse[package.version]
    package.latest_datetime = max([*release_dates])
    package.latest_version = release_dates[package.latest_datetime]
    return package


@beartype
def _read_cache(path_pack_lock: Path = PACK_LOCK_PATH) -> Dict[str, _HostedPythonPackage]:
    """Read the cached packaging information.

    Args:
        path_pack_lock: Path to the lock file. Default is `PACK_LOCK_PATH`

    Returns:
        Dict[str, _HostedPythonPackage]: the cached packages

    """
    if not path_pack_lock.is_file():
        path_pack_lock.write_text('{}')  # noqa: P103
    old_cache: Dict[str, Dict[str, str]] = json.loads(path_pack_lock.read_text())
    return {
        package_name: _HostedPythonPackage(**meta_data)  # type: ignore[arg-type]
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
        try:
            cached_package = old_cache.get(package.name)
            cached_version = '' if cached_package is None else cached_package.version
            if package.version != cached_version:
                package = _get_release_date(package)
                updated_packages.append(package)
            elif cached_package:
                updated_packages.append(cached_package)
        except requests.exceptions.HTTPError as err:
            logger.warning(f'Could not resolve {package} with error {err}')
    return updated_packages


@beartype
def _write_cache(updated_packages: List[_HostedPythonPackage], path_pack_lock: Path = PACK_LOCK_PATH) -> None:
    """Read the cached packaging information.

    Args:
        updated_packages: updated packages to store
        path_pack_lock: Path to the lock file. Default is `PACK_LOCK_PATH`

    """
    new_cache = {pack.name: json.loads(pack.json()) for pack in updated_packages}
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

    lock = tomllib.loads(path_lock.read_text(errors='ignore'))
    # TBD: Handle non-pypi domains and format the URL accordingly (i.e. TestPyPi, etc.)
    # > domain=dependency['source']['url'] + '{name}/json'
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
        delta = pack.datetime.humanize()  # type: ignore[union-attr]
        latest = '' if pack.version == pack.latest_version else f' (*New version available: {pack.latest_version}*)'
        return f'- {delta}: {pack.name} {pack.version}{latest}'

    now = arrow.utcnow()
    stale_cutoff = now.shift(months=-1 * stale_months)
    stale_packages = [pack for pack in packages if not pack.datetime or pack.datetime < stale_cutoff]
    if stale_packages:
        pkgs = sorted(stale_packages, key=lambda x: x.datetime or stale_cutoff)
        stale_list = '\n'.join(map(format_package, pkgs))
        logger.warning(f'Found stale packages that may be a dependency risk:\n\n{stale_list}\n\n')
    else:
        oldest_date = np.amin([pack.datetime for pack in packages])
        logger.warning(f'The oldest package was released {oldest_date.humanize()} (stale is >{stale_months} months)\n')



@beartype
def check_for_stale_packages(
    path_lock: Path, *, stale_months: int, path_pack_lock: Path = PACK_LOCK_PATH,
) -> None:
    """Read the cached packaging information.

    Args:
        path_lock: Path to the lock file to parse
        path_pack_lock: Path to the lock file. Default is `PACK_LOCK_PATH`
        stale_months: cutoff in months for when a package might be stale enough to be a risk

    """
    packages = _read_packages(path_lock)
    old_cache = _read_cache(path_pack_lock)
    updated_packages = _collect_release_dates(packages, old_cache)
    _write_cache(updated_packages, path_pack_lock)
    _check_for_stale_packages(updated_packages, stale_months=stale_months)
