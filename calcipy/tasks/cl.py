"""Changelog CLI."""

from beartype import beartype
from beartype.typing import Literal, Optional
from invoke.context import Context

from ..cli import task
from ..invoke_helpers import get_doc_subdir, get_project_path, run
from .executable_utils import GH_MESSAGE, check_installed, python_dir

SuffixT = Optional[Literal['alpha', 'beta', 'rc']]
"""Prerelease Suffix Type."""


@task()
def write(ctx: Context) -> None:
    """Write a Changelog file with the raw Git history.

    Resources:

    - https://keepachangelog.com/en/1.0.0/
    - https://www.conventionalcommits.org/en/v1.0.0/
    - https://writingfordevelopers.substack.com/p/how-to-write-a-commit-message
    - https://chris.beams.io/posts/git-commit/
    - https://semver.org/
    - https://calver.org/

    Returns:
        List[DoitAction]: doit actions

    """
    run(ctx, f'{python_dir()}/cz changelog')
    path_cl = get_project_path() / 'CHANGELOG.md'
    if not path_cl.is_file():
        msg = f'Could not locate the changelog at: {path_cl}'
        raise FileNotFoundError(msg)
    path_cl.replace(get_doc_subdir() / path_cl.name)


@beartype
def bumpz(ctx: Context, *, suffix: SuffixT = None) -> None:
    """Bumps project version based on commits & settings in pyproject.toml."""
    check_installed(ctx, executable='gh', message=GH_MESSAGE)

    opt_cz_args = f' --prerelease={suffix}' if suffix else ''
    run(ctx, f'{python_dir()}/cz bump{opt_cz_args} --annotated-tag --no-verify --gpg-sign')

    run(ctx, 'git push origin --tags --no-verify')

    get_last_tag = 'git tag --list --sort=-creatordate | head -n 1'
    opt_gh_args = ' --prerelease' if suffix else ''
    run(ctx, f'gh release create --generate-notes $({get_last_tag}){opt_gh_args}')


@task(
    pre=[write],
    help={
        'suffix': 'Specify prerelease suffix for version bump (alpha, beta, rc)',
    },
)
def bump(ctx: Context, *, suffix: SuffixT = None) -> None:
    """Bumps project version based on commits & settings in pyproject.toml."""
    bumpz(ctx, suffix=suffix)
