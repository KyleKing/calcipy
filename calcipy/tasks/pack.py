"""Packaging CLI."""

from os import getenv
from pathlib import Path

import keyring
from corallium import file_helpers  # Required for mocking read_pyproject
from corallium.file_helpers import PROJECT_TOML, get_lock, if_found_unlink
from corallium.log import LOGGER
from invoke.context import Context

from calcipy import can_skip  # Required for mocking can_skip.can_skip
from calcipy.cli import task
from calcipy.invoke_helpers import run


@task()
def lock(ctx: Context) -> None:
    """Update package manager lock file."""
    if can_skip.can_skip(prerequisites=[PROJECT_TOML], targets=[get_lock()]):
        return  # Exit early

    run(ctx, 'uv lock')


@task(pre=[lock])
def install_extras(ctx: Context) -> None:
    """Run uv install with all extras."""
    run(ctx, 'uv sync --all-extras')


def _configure_uv_env_credentials(*, index_name: str, interactive: bool) -> dict[str, str]:
    username = getenv('UV_PUBLISH_USERNAME')
    password = getenv('UV_PUBLISH_PASSWORD')
    if username and password:
        return {
            'UV_PUBLISH_USERNAME': username,
            'UV_PUBLISH_PASSWORD': password,
        }

    def _get_token() -> str:
        """Return token stored in keyring."""
        kwargs = {'service_name': 'calcipy', 'username': f'uv-{index_name}-token'}
        if token := keyring.get_password(**kwargs):
            return token
        if interactive and (new_token := input('PyPi Publish Token: ')):
            keyring.set_password(**kwargs, password=new_token)
            return new_token
        raise RuntimeError("No Token for PyPi in 'UV_PUBLISH_TOKEN' or keyring")

    token = getenv('UV_PUBLISH_TOKEN')
    return {'UV_PUBLISH_USERNAME': '__token__', 'UV_PUBLISH_TOKEN': token or _get_token()}


@task(
    help={
        'to_test_pypi': 'Publish to the TestPyPi repository',
        'no_interactive': 'Do not prompt for credentials when not found',
    },
)
def publish(ctx: Context, *, to_test_pypi: bool = False, no_interactive: bool = False) -> None:
    """Build the distributed format(s) and publish.

    Alternatively, configure Github Actions to use 'Trusted Publisher'
    https://docs.pypi.org/trusted-publishers/adding-a-publisher

    """
    if_found_unlink(Path('dist'))
    run(ctx, 'uv build --no-sources')

    keyring.set_password('system', 'username', 'password')
    keyring.get_password('system', 'username')

    cmd = 'uv publish'
    index_name = 'PyPi'
    if to_test_pypi:
        cmd += ' --publish-url https://test.pypi.org/legacy/'
        index_name = 'Test PyPi'
    env = _configure_uv_env_credentials(index_name=index_name, interactive=not no_interactive)
    run(ctx, cmd, env=env)


# TODO: Add unit test
@task(
    help={
        'tag': 'Last tag, can be provided with `--tag="$(git tag -l "v*" | sort | tail -n 1)"`',
        'tag_prefix': 'Optional tag prefix, such as "v"',
        'pkg_name': 'Optional package name. If not provided, will read the uv pyproject.toml file',
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
        uv_config = file_helpers.read_pyproject()['tool']['uv']
        pkg_name = uv_config['name']

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
    """Experiment with setting the pyproject.toml dependencies to the version from uv.lock (experimental).

    Uses the current working directory and should be run after `uv update`.

    """
    from calcipy.experiments import sync_package_dependencies  # noqa: PLC0415

    sync_package_dependencies.replace_versions(path_lock=get_lock())
