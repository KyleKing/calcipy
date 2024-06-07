"""Support can-skip logic from Make."""

from pathlib import Path

from beartype import beartype
from beartype.typing import List
from corallium.log import LOGGER


@beartype
def can_skip(*, prerequisites: List[Path], targets: List[Path]) -> bool:
    """Return true if the prerequisite files are have newer `mtime` than targets.

    Example use with Invoke, but can be used anywhere:

    ```py
    @task()
    def test(ctx: Context) -> None:
        if can_skip(prerequisites=[*Path('src').rglob('*.py')], targets=[Path('.coverage.xml')]):
            return  # Exit early

        ...  # Task code
    ```

    """
    if not (ts_prerequisites := [pth.stat().st_mtime for pth in prerequisites]):
        raise ValueError('Required files do not exist', prerequisites)

    ts_targets = [pth.stat().st_mtime for pth in targets]
    if ts_targets and min(ts_targets) > max(ts_prerequisites):
        LOGGER.warning('Skipping because targets are newer', targets=targets)
        return True
    return False


@beartype
def dont_skip(*, prerequisites: List[Path], targets: List[Path]) -> bool:
    """To use for testing with mock; always returns False."""
    LOGGER.debug('Mocking can_skip', prerequisites=prerequisites, targets=targets)
    return False
