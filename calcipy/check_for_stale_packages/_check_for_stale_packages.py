"""Check for stale packages."""

import asyncio
import json
from pathlib import Path

import arrow
import httpx
import numpy as np
from arrow import Arrow
from beartype import beartype
from beartype.typing import Dict, List, Optional, Union
from bidict import bidict
from corallium.file_helpers import LOCK
from corallium.log import logger
from corallium.tomllib import tomllib
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from pyrate_limiter import Duration, Limiter, RequestRate

from .. import can_skip  # Required for mocking can_skip.can_skip

CALCIPY_CACHE = Path('.calcipy_packaging.lock')
"""Path to the packaging lock file."""


class _HostedPythonPackage(BaseModel):
    """Representative information for a python package hosted on some domain."""

    # Note: "releases" was removed from the versioned URL: https://warehouse.pypa.io/api-reference/json.html#release
    domain: str = Field(default='https://pypi.org/pypi/{name}/json')
    name: str
    version: str
    datetime: Optional[Arrow] = Field(default=None)
    latest_version: str = Field(default='')
    latest_datetime: Optional[Arrow] = Field(default=None)  # noqa: CCE001
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer('datetime', 'latest_datetime')
    def serialize_datetime(self, value: Optional[Arrow]) -> Optional[str]:  # noqa: RBT002
        return str(value) if value else None

    @field_validator('datetime', 'latest_datetime', mode='before')
    @classmethod
    def date_validator(cls, value: Union[str, Arrow]) -> Arrow:  # noqa: N805,RBT002
        return arrow.get(value)


# Configure rate-limiter
#   https://pypi.org/project/pyrate-limiter/
_RATE = RequestRate(3, 5 * Duration.SECOND)
_LIMITER = Limiter(_RATE)


@beartype
@_LIMITER.ratelimit('pypi', delay=True, max_delay=10)  # type: ignore[misc]
async def _get_release_date(package: _HostedPythonPackage) -> _HostedPythonPackage:
    """Retrieve release date metadata for the specified package.

    Args:
        package: `_HostedPythonPackage`

    Returns:
        _HostedPythonPackage: updated with release date metadata from API

    """
    # Retrieve the JSON summary for the specified package
    json_url = package.domain.format(name=package.name)
    async with httpx.AsyncClient() as client:
        res = await client.get(json_url, timeout=30)   # nosem
        res.raise_for_status()
        res_json = res.json()
        if not (releases := res_json['releases']):
            msg = f'Failed to locate "releases" or "urls" from {json_url}: {res_json}'
            raise RuntimeError(msg)

    # Also retrieve the latest release date of the package looking through all releases
    release_dates = bidict({
        arrow.get(release_data[0]['upload_time_iso_8601']): version
        for version, release_data in releases.items()
        if release_data
    })
    try:
        package.datetime = release_dates.inverse[package.version]
    except KeyError:  # pragma: no cover
        msg = f'Could not locate {package} in {res_json}. Please wait and try again later'
        raise RuntimeError(msg) from None
    package.latest_datetime = max([*release_dates])
    package.latest_version = release_dates[package.latest_datetime]
    return package


@beartype
def _read_cache(path_pack_lock: Path = CALCIPY_CACHE) -> Dict[str, _HostedPythonPackage]:
    """Read the cached packaging information.

    Args:
        path_pack_lock: Path to the lock file. Default is `CALCIPY_CACHE`

    Returns:
        Dict[str, _HostedPythonPackage]: the cached packages

    """
    if not path_pack_lock.is_file():
        path_pack_lock.write_text('{}', encoding='utf-8')  # noqa: P103
    old_cache: Dict[str, Dict[str, str]] = json.loads(path_pack_lock.read_text(encoding='utf-8'))
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
                updated_packages.append(asyncio.run(_get_release_date(package)))
            elif cached_package:
                updated_packages.append(cached_package)
        except httpx.HTTPError as exc:  # noqa: PERF203
            logger.warning('Could not lock package', package=package, error=str(exc))
    return updated_packages


@beartype
def _write_cache(updated_packages: List[_HostedPythonPackage], path_pack_lock: Path = CALCIPY_CACHE) -> None:
    """Read the cached packaging information.

    Args:
        updated_packages: updated packages to store
        path_pack_lock: Path to the lock file. Default is `CALCIPY_CACHE`

    """
    new_cache = {pack.name: json.loads(pack.json()) for pack in updated_packages}
    pretty_json = json.dumps(new_cache, indent=4, separators=(',', ': '), sort_keys=True)
    path_pack_lock.write_text(pretty_json + '\n', encoding='utf-8')


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
    if path_lock.name != LOCK.name:
        msg = f'"{path_lock.name}" is not a currently supported lock type. Try "{LOCK.name}" instead'
        raise NotImplementedError(msg)

    lock = tomllib.loads(path_lock.read_text(errors='ignore'))
    return [
        _HostedPythonPackage(
            name=dependency['name'], version=dependency['version'],
        ) for dependency in lock['package']
    ]


@beartype
def _packages_are_stale(packages: List[_HostedPythonPackage], *, stale_months: int) -> bool:
    """Check for stale packages. Raise error and log all stale versions found.

    Args:
        packages: List of packages
        stale_months: cutoff in months for when a package might be stale enough to be a risk

    """
    @beartype
    def format_package(pack: _HostedPythonPackage) -> str:
        delta = pack.datetime.humanize()  # type: ignore[union-attr]
        latest = '' if pack.version == pack.latest_version else f' (*New version available: {pack.latest_version}*)'
        return f'- {delta}: {pack.name} {pack.version}{latest}'

    now = arrow.utcnow()
    stale_cutoff = now.shift(months=-1 * stale_months)
    stale_packages = [pack for pack in packages if not pack.datetime or pack.datetime < stale_cutoff]
    # TODO: If no stale, write out five oldest?
    if stale_packages:
        pkgs = sorted(stale_packages, key=lambda x: x.datetime or stale_cutoff)
        stale_list = '\n'.join([format_package(_p) for _p in pkgs])
        logger.warning('Found stale packages that may be a dependency risk', stale_list=stale_list)
        return True
    if packages:
        oldest_date = np.amin([pack.datetime for pack in packages])  # pyright: ignore[reportGeneralTypeIssues]
        logger.text('No stale packages found', oldest=oldest_date.humanize(), stale_threshold=stale_months)
    return False


@beartype
def check_for_stale_packages(*, stale_months: int, path_lock: Path = LOCK, path_cache: Path = CALCIPY_CACHE) -> bool:
    """Read the cached packaging information.

    Args:
        stale_months: cutoff in months for when a package might be stale enough to be a risk

    """
    packages = _read_packages(path_lock)
    cached_packages = _read_cache(path_cache)
    if cached_packages and can_skip.can_skip(prerequisites=[path_lock], targets=[path_cache]):
        packages = [*cached_packages.values()]
    else:
        packages = _collect_release_dates(packages, cached_packages)
        _write_cache(packages, path_cache)
    return _packages_are_stale(packages, stale_months=stale_months)
