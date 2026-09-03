"""Experimental features CLI."""

from pathlib import Path

from corallium import file_helpers
from corallium.file_helpers import get_lock
from corallium.log import LOGGER
from invoke.context import Context

from calcipy.cli import task


@task(
    help={
        'tag': 'Last tag, can be provided with `--tag="$(git tag -l "v*" | sort | tail -n 1)"`',
        'tag_prefix': 'Optional tag prefix, such as "v"',
        'pkg_name': 'Optional package name. If not provided, will read the pyproject.toml file',
    },
)
def bump_tag(ctx: Context, *, tag: str, tag_prefix: str = '', pkg_name: str = '') -> None:  # noqa: ARG001
    """Experiment with bumping the git tag using `griffe` (experimental).

    Example for `calcipy`:

    ```sh
    calcipy-experiments bump-tag --tag="$(git tag -l "*" | sort | head -n 5 | tail -n 1)" --tag-prefix=""
    ```

    """
    if not tag:
        raise ValueError('tag must not be empty')
    if not pkg_name:
        pkg_name = file_helpers.read_pyproject()['project']['name']

    from calcipy.experiments import bump_programmatically  # noqa: PLC0415

    new_version = bump_programmatically.bump_tag(
        pkg_name=pkg_name,
        tag=tag,
        tag_prefix=tag_prefix,
    )
    LOGGER.text(new_version)


@task()
def sync_pyproject_versions(ctx: Context) -> None:  # noqa: ARG001
    """Experiment with setting the pyproject.toml dependencies to the version from uv.lock (experimental).

    Uses the current working directory and should be run after `uv update`.

    """
    from corallium import sync_dependencies  # noqa: PLC0415

    sync_dependencies.replace_versions(path_lock=get_lock())


@task(
    help={
        'test_path': 'Path to test directory (default: ./tests)',
    },
)
def check_duplicate_tests(ctx: Context, *, test_path: str = 'tests') -> None:  # noqa: ARG001
    """Check for duplicate test names in test suite.

    Raises:
        RuntimeError: if duplicate tests found

    """
    from calcipy.experiments import check_duplicate_test_names  # noqa: PLC0415

    if duplicates := check_duplicate_test_names.run(Path(test_path)):
        raise RuntimeError(f'Duplicate test names found ({duplicates}). See log output above for details.')  # noqa: EM102
