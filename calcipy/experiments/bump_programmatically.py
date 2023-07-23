"""Experiment with bumping the git tag using `griffe`."""

import griffe
import semver
from beartype import beartype
from corallium.log import logger
from griffe.exceptions import BuiltinModuleError


@beartype
def bump_tag(*, pkg_name: str, tag: str, tag_prefix: str) -> str:
    """Make a SemVer minor bump using `griffe` if there were any breaking changes.

    Major versions must be bumped manually

    """
    previous = griffe.load_git(pkg_name, ref=tag)
    current = griffe.load(pkg_name)

    breakages = [*griffe.find_breaking_changes(previous, current)]
    for breakage in breakages:
        try:
            logger.text(breakage._explain_oneline())  # noqa: SLF001
        except BuiltinModuleError:  # noqa: PERF203
            logger.warning(str(breakage))
        except Exception:
            logger.exception(str(breakage))

    try:
        ver = semver.Version.parse(tag.replace(tag_prefix, ''))
    except ValueError:
        logger.exception('Failed to parse tag', tag=tag)
        return ''
    new_ver = ver.bump_minor() if any(breakages) else ver.bump_patch()
    return f'{tag_prefix}{new_ver}'
