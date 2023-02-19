"""Changelog CLI."""

from beartype import beartype
from beartype.typing import Literal, Optional
from invoke import Context
from shoal.cli import task

from .._temp_dg import dg
from ..file_helpers import get_project_path

SuffixT = Optional[Literal['alpha', 'beta', 'rc']]
"""Prerelease Suffix Type."""


@task()  # type: ignore[misc]
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
    ctx.run('poetry run cz changelog')
    path_cl = get_project_path() / 'CHANGELOG.md'
    if not path_cl.is_file():
        msg = f'Could not locate the changelog at: {path_cl}'
        raise FileNotFoundError(msg)
    path_cl.replace(dg.doc.doc_sub_dir / path_cl.name)


@beartype
def bumpz(ctx: Context, *, suffix: SuffixT = None) -> None:
    """Bumps project version based on commits & settings in pyproject.toml."""
    get_last_tag = 'git tag --list --sort=-creatordate | head -n 1'
    opt_cz_args = f' --prerelease={suffix}' if suffix else ''
    opt_gh_args = ' --prerelease' if suffix else ''
    ctx.run(f'poetry run cz bump{opt_cz_args} --annotated-tag --no-verify --gpg-sign')
    # Catch issues when commitizen breaks versions indirectly
    ctx.run('poetry lock --check')
    ctx.run('git push origin --tags --no-verify')
    # TODO: Make "which $(..) >> /dev/null && " a function?
    ctx.run(f'which gh >> /dev/null && gh release create --generate-notes $({get_last_tag}){opt_gh_args}')


@task(  # type: ignore[misc]
    pre=[write],
    help={
        'suffix': 'Specify prerelease suffix for version bump (alpha, beta, rc)',
    },
)
def bump(ctx: Context, *, suffix: SuffixT = None) -> None:
    """Bumps project version based on commits & settings in pyproject.toml."""
    bumpz(ctx, suffix=suffix)