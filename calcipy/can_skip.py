# FIXME: Move to shoal

from beartype import beartype

@beartype
def can_skip(*, depends: List[Path], targets: List[Path]) -> bool:
    """Generic make-style task skipping logic based on file mtime.

    Example use with Invoke, but can be used anywhere:

    ```py
    @task
    def test(ctx: Context) -> None:
        if can_skip(depends=[*Path('src').rglob('*.py')], targets=[Path('.coverage.xml')]):
            return  # Exit early

        ...  # Task code
    ```

    """
    ts_depends = [pth.getmtime() for pth in depends]
    if not ts_depends:
        raise ValueError('Required files do not exist', depends)

    # TODO: Triple check this logic (https://stackoverflow.com/a/22960700/3219667)
    ts_targets = [pth.getmtime() for pth in targets]
    if ts_targets and max(ts_depends) >= min(ts_targets):
        logger.info('Skipping because targets are newer', targets=targets)
        return False
    return True
