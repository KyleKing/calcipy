"""Check for stale packages."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable
from dataclasses import asdict, dataclass, field
from datetime import timezone
from functools import partial
from itertools import starmap
from pathlib import Path
from typing import Any

import arrow
import httpx
from arrow import Arrow
from beartype.typing import Callable, TypeVar
from corallium.file_helpers import LOCK
from corallium.log import LOGGER
from corallium.tomllib import tomllib

from calcipy import can_skip  # Required for mocking can_skip.can_skip

CALCIPY_CACHE = Path('.calcipy_packaging.lock')
"""Path to the packaging lock file."""


def arrow_as_string_factory(data: list[tuple[str, Any]]) -> dict[str, Any]:
    """`asdict.dict_factory` to serialize Arrow types.

    Note: if `dict_factory` composition is needed, use functools.reduce and see:
    <https://cucumbersome.hashnode.dev/combine-multiple-dict-factories-in-asdict>

    """
    return {key: str(value) if isinstance(value, Arrow) else value for key, value in data}


@dataclass
class _HostedPythonPackage:
    """Representative information for a python package hosted on some domain."""

    # Note: "releases" was removed from the versioned URL: https://warehouse.pypa.io/api-reference/json.html#release
    name: str
    version: str
    domain: str = field(default='https://pypi.org/pypi/{name}/json')
    datetime: Arrow | None = field(default=None)
    latest_version: str = field(default='')
    latest_datetime: Arrow | None = field(default=None)

    @classmethod
    def from_data(cls, **kwargs) -> _HostedPythonPackage:
        for date_key in ('datetime', 'latest_datetime'):
            if value := kwargs.get(date_key):
                kwargs[date_key] = arrow.get(value)
        return cls(**kwargs)

    def model_dump_json(self) -> str:
        data = asdict(self, dict_factory=arrow_as_string_factory)
        return json.dumps(data)


async def _get_release_date(package: _HostedPythonPackage) -> _HostedPythonPackage:
    """Retrieve release date metadata for the specified package.

    Args:
        package: `_HostedPythonPackage`

    Returns:
        _HostedPythonPackage: updated with release date metadata from API

    """
    # Retrieve the JSON summary for the specified package
    json_url = package.domain.format(name=package.name)
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(json_url, timeout=30)  # nosem
        res.raise_for_status()
        res_json = res.json()
        if not (releases := res_json['releases']):
            msg = f'Failed to locate "releases" or "urls" from {json_url}: {res_json}'
            raise RuntimeError(msg)

    # Also retrieve the latest release date of the package looking through all releases
    release_dates = {
        arrow.get(release_data[0]['upload_time_iso_8601']): version
        for version, release_data in releases.items()
        if release_data
    }
    inverse_release_dates = {_v: key for key, _v in release_dates.items()}
    try:
        package.datetime = inverse_release_dates[package.version]
    except KeyError:  # pragma: no cover
        msg = f'Could not locate {package} in {res_json}. Please wait and try again later'
        raise RuntimeError(msg) from None
    package.latest_datetime = max([*release_dates])
    package.latest_version = release_dates[package.latest_datetime]
    return package


def _read_cache(path_pack_lock: Path = CALCIPY_CACHE) -> dict[str, _HostedPythonPackage]:
    """Read the cached packaging information.

    Args:
        path_pack_lock: Path to the lock file. Default is `CALCIPY_CACHE`

    Returns:
        Dict[str, _HostedPythonPackage]: the cached packages

    """
    if not path_pack_lock.is_file():
        path_pack_lock.write_text('{}', encoding='utf-8')
    old_cache: dict[str, dict[str, str]] = json.loads(path_pack_lock.read_text(encoding='utf-8'))
    return {package_name: _HostedPythonPackage.from_data(**meta_data) for package_name, meta_data in old_cache.items()}


_OpReturnT = TypeVar('_OpReturnT')


async def _rate_limited(
    operations: list[Callable[[], Awaitable[_OpReturnT]]],
    max_per_interval: int,
    interval_sec: int,
    max_delay: int | None = None,
) -> list[_OpReturnT]:
    """Naive semaphore-based rate limiting.

    For more performant and flexible limiting, see: <https://pypi.org/project/pyrate-limiter>

    Args:
        operations: list of no-argument callable functions to run
        max_per_interval: maximum number of concurrent operations per interval
        interval_sec: length of interval in seconds
        max_delay: maximum runtime before quietly stopping

    Returns:
        List[_OpReturnT]: list of return values from operations up to max_delay time, if set

    """
    if not operations:
        return []

    initial_start = time.monotonic()
    sem = asyncio.BoundedSemaphore(value=max_per_interval)

    async def task(idx: int, op: Callable[[], Awaitable[_OpReturnT]]) -> tuple[_OpReturnT | None, float]:
        """Return result. Rudimentary rate limiting by waiting to acquire the semaphore, then sleeping if necessary."""
        if max_delay and (time.monotonic() - initial_start) > max_delay:
            return (None, 0.0)
        max_idle = interval_sec if (count_input - idx) >= max_per_interval else 0
        async with sem:
            start = time.monotonic()
            result = await op()
            if (idle := max_idle - (time.monotonic() - start)) > 0:
                await asyncio.sleep(idle)
            return (result, idle)

    count_input = len(operations)
    tasks = await asyncio.gather(*starmap(task, enumerate(operations)))
    results = [out[0] for out in tasks if out[0]]
    total_idle = sum(max([out[1], 0]) for out in tasks)
    count_output = len(results)
    LOGGER.info(
        'Completed rate limited operations',
        count_input=count_input,
        count_output=count_output,
        avg_idle_time=round(total_idle / count_output, 2),
        total=round(time.monotonic() - initial_start, 2),
    )
    return results


async def _collect_release_dates(
    packages: list[_HostedPythonPackage],
    old_cache: dict[str, _HostedPythonPackage] | None = None,
) -> list[_HostedPythonPackage]:
    """Use the cache to retrieve only metadata that needs to be updated.

    Args:
        packages: list of `_HostedPythonPackage`
        old_cache: cache data to compare against to limit network requests

    Returns:
        List[_HostedPythonPackage]: packages with updated release dates

    """
    if old_cache is None:
        old_cache = {}

    updated_packages: list[_HostedPythonPackage] = []
    missing_packages: list[_HostedPythonPackage] = []
    for package in packages:
        cached_package = old_cache.get(package.name)
        cached_version = '' if cached_package is None else cached_package.version
        if package.version != cached_version:
            missing_packages.append(package)
        elif cached_package:
            updated_packages.append(cached_package)

    async def fetch(package: _HostedPythonPackage) -> _HostedPythonPackage | None:
        try:
            return await _get_release_date(package)
        except httpx.HTTPError as exc:
            LOGGER.warning('Could not lock package', package=package, error=str(exc))
        return None

    updated_packages.extend(
        [
            result
            for result in await _rate_limited(
                [partial(fetch, pkg) for pkg in missing_packages],
                max_per_interval=3,
                interval_sec=3,
                max_delay=600,
            )
            if result
        ],
    )
    return updated_packages


def _write_cache(updated_packages: list[_HostedPythonPackage], path_pack_lock: Path = CALCIPY_CACHE) -> None:
    """Read the cached packaging information.

    Args:
        updated_packages: updated packages to store
        path_pack_lock: Path to the lock file. Default is `CALCIPY_CACHE`

    """
    new_cache = {pack.name: json.loads(pack.model_dump_json()) for pack in updated_packages}
    pretty_json = json.dumps(new_cache, indent=4, separators=(',', ': '), sort_keys=True)
    path_pack_lock.write_text(pretty_json + '\n', encoding='utf-8')


def _read_packages(path_lock: Path) -> list[_HostedPythonPackage]:
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
        _HostedPythonPackage.from_data(
            name=dependency['name'],
            version=dependency['version'],
        )
        for dependency in lock['package']
    ]


def _packages_are_stale(packages: list[_HostedPythonPackage], *, stale_months: int) -> bool:
    """Check for stale packages. Raise error and log all stale versions found.

    Args:
        packages: List of packages
        stale_months: cutoff in months for when a package might be stale enough to be a risk

    """

    def format_package(pack: _HostedPythonPackage) -> str:
        delta = pack.datetime.humanize()  # type: ignore[union-attr]
        latest = '' if pack.version == pack.latest_version else f' (*New version available: {pack.latest_version}*)'
        return f'{delta}: {pack.name} {pack.version}{latest}'

    stale_cutoff = arrow.now(timezone.utc).shift(months=-1 * stale_months)
    sorted_packages = sorted(packages, key=lambda x: x.datetime or stale_cutoff, reverse=True)
    stale_packages = [pack for pack in sorted_packages if not pack.datetime or pack.datetime < stale_cutoff]
    if stale_packages:
        LOGGER.warning(
            f'Found stale packages older than {stale_months} months',
            stale_packages=[format_package(_p) for _p in stale_packages],
        )
    LOGGER.text('Oldest packages:\n\t' + '\n\t'.join([format_package(_p) for _p in sorted_packages[-5:]]))
    return bool(stale_packages)


def check_for_stale_packages(*, stale_months: int, path_lock: Path = LOCK, path_cache: Path = CALCIPY_CACHE) -> bool:
    """Check for stale packages by reading from the cache, and updating if necessary.

    Args:
        stale_months: cutoff in months for when a package might be stale enough to be a risk
        path_lock: path to poetry lock file
        path_cache: path to calcipy package cache file

    """
    cached_packages = _read_cache(path_cache)
    if cached_packages and can_skip.can_skip(prerequisites=[path_lock], targets=[path_cache]):
        packages = [*cached_packages.values()]
    else:
        packages = asyncio.run(_collect_release_dates(_read_packages(path_lock), cached_packages))
        _write_cache(packages, path_cache)
    return _packages_are_stale(packages, stale_months=stale_months)
