"""Packaging CLI."""

from corallium import file_helpers  # Required for mocking read_pyproject
from corallium.file_helpers import LOCK, PROJECT_TOML
from corallium.log import LOGGER
from invoke.context import Context

from calcipy import can_skip  # Required for mocking can_skip.can_skip
from calcipy.cli import task
from calcipy.invoke_helpers import run

from .executable_utils import python_dir


@task()
def lock(ctx: Context) -> None:
    """Ensure poetry.lock is  up-to-date."""
    if can_skip.can_skip(prerequisites=[PROJECT_TOML], targets=[LOCK]):
        return  # Exit early

    run(ctx, 'poetry lock --no-update')


@task(pre=[lock])
def install_extras(ctx: Context) -> None:
    """Run poetry install with all extras."""
    poetry_config = file_helpers.read_pyproject()['tool']['poetry']
    extras = (poetry_config.get('extras') or {}).keys()
    run(ctx, ' '.join(['poetry install --sync', *[f'--extras={ex}' for ex in extras]]))


@task(
    help={
        'to_test_pypi': 'Publish to the TestPyPi repository',
    },
)
def publish(ctx: Context, *, to_test_pypi: bool = False) -> None:
    """Build the distributed format(s) and publish."""
    run(ctx, f'{python_dir()}/nox --error-on-missing-interpreters --session build_dist build_check')

    cmd = 'poetry publish'
    if to_test_pypi:
        cmd += ' --repository testpypi'
    run(ctx, cmd)


@task()
def check_licenses(ctx: Context) -> None:
    """Check licenses for compatibility with `licensecheck`."""
    res = run(ctx, 'which licensecheck', warn=True, hide=True)
    if not res or res.exited == 1:
        uvx_res = run(ctx, 'uvx licensecheck', warn=True)
        if not uvx_res or uvx_res.exited == 1:
            LOGGER.error('Failed to use `uv` to run licensecheck. See: https://docs.astral.sh/uv')
    else:
        run(ctx, 'licensecheck')


# TODO: Add unit test
@task(
    help={
        'tag': 'Last tag, can be provided with `--tag="$(git tag -l "v*" | sort | tail -n 1)"`',
        'tag_prefix': 'Optional tag prefix, such as "v"',
        'pkg_name': 'Optional package name. If not provided, will read the poetry pyproject.toml file',
    },
)
def bump_tag(ctx: Context, *, tag: str, tag_prefix: str = '', pkg_name: str = '') -> None:  # noqa: ARG001
    """Experiment with bumping the git tag using `griffe` (experimental).

    Example for `calcipy`:

    ```sh
    ./run pack.bump-tag --tag="$(git tag -l "*" | sort | head -n 5 | tail -n 1)" --tag-prefix=""
    ```

    """
    if not tag:
        raise ValueError('tag must not be empty')
    if not pkg_name:
        poetry_config = file_helpers.read_pyproject()['tool']['poetry']
        pkg_name = poetry_config['name']

    from calcipy.experiments import bump_programmatically  # noqa: PLC0415

    new_version = bump_programmatically.bump_tag(
        pkg_name=pkg_name,
        tag=tag,
        tag_prefix=tag_prefix,
    )
    LOGGER.text(new_version)


# TODO: Add unit test
@task(post=[lock])
def sync_pyproject_versions(ctx: Context) -> None:  # noqa: ARG001
    """Experiment with setting the pyproject.toml dependencies to the version from poetry.lock (experimental).

    Uses the current working directory and should be run after `poetry update`.

    """
    from calcipy.experiments import sync_package_dependencies  # noqa: PLC0415

    sync_package_dependencies.replace_versions(path_lock=LOCK)
