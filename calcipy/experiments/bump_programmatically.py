"""Experiment with bumping the git tag using `griffe`."""

import griffe
import semver
from corallium.log import LOGGER
from griffe import BuiltinModuleError


def bump_tag(*, pkg_name: str, tag: str, tag_prefix: str) -> str:  # pragma: no cover
    """Return either minor or patch change based on `griffe`.

    Note: major versions must be bumped manually

    """
    previous = griffe.load_git(pkg_name, ref=tag)
    current = griffe.load(pkg_name)

    breakages = [*griffe.find_breaking_changes(previous, current)]
    for breakage in breakages:
        try:
            LOGGER.text(breakage._explain_oneline())  # noqa: SLF001
        except BuiltinModuleError:  # noqa: PERF203
            LOGGER.warning(str(breakage))
        except Exception:
            LOGGER.exception(str(breakage))

    try:
        ver = semver.Version.parse(tag.replace(tag_prefix, ''))
    except ValueError:
        LOGGER.exception('Failed to parse tag', tag=tag)
        return ''
    new_ver = ver.bump_minor() if any(breakages) else ver.bump_patch()
    return f'{tag_prefix}{new_ver}'
