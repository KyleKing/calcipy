"""Experiment with bumping the git tag using `griffe`."""

import sys

import griffe
import semver
from beartype import beartype
from corallium.log import logger


@beartype
def bump_tag(*, pkg_name: str, tag: str, tag_prefix: str, debug: bool = True) -> str:
    """Make a SemVer minor bump using `griffe` if there were any breaking changes.

    Major versions must be bumped manually

    """
    previous = griffe.load_git(pkg_name, ref=tag)
    current = griffe.load(pkg_name)

    breakages = [*griffe.find_breaking_changes(previous, current)]

    if debug:
        for breakage in breakages:
            logger.debug(breakage._explain_oneline())  # noqa: SLF001

    ver = semver.Version.parse(current_tag.replace(tag_prefix, ''))
    new_ver = ver.bump_minor() if any(breakages) else ver.bump_patch()
    return f'{tag_prefix}{new_ver}'


if __name__ == '__main__':
    """Run as a standalone file without calcipy:

    ```sh
    poetry run python bump_programmatically.py "3.0.7" | tail -n 1
    ```

    """
    current_tag = sys.argv[1]
    new_tag = bump_tag(pkg_name='pytest_cache_assert', tag=current_tag, tag_prefix='v')
    logger.warning('')
    logger.warning(new_tag)
