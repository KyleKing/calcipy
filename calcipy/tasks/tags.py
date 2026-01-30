"""Code Tag Collector CLI."""

from pathlib import Path

from beartype.typing import Optional
from corallium.code_tag_collector import write_code_tag_file
from corallium.file_search import find_project_files
from corallium.log import LOGGER
from corallium.vcs import find_repo_root
from invoke.context import Context

from calcipy.cli import task
from calcipy.invoke_helpers import get_doc_subdir

from .defaults import from_ctx


@task(
    default=True,
    help={
        'base_dir': 'Working Directory',
        'doc_sub_dir': 'Subdirectory for output of the code tag summary file',
        'filename': 'Code Tag Summary Filename',
        'tag_order': 'Ordered list of code tags to locate (Comma-separated)',
        'regex': 'Custom Code Tag Regex. Must contain "{tag}"',
        'ignore_patterns': 'Glob patterns to ignore files and directories when searching (Comma-separated). '
        'When outside git repo, defaults to common build/cache directories.',
        'ignore_repo_root': 'Ignore repository root check and use current directory as base',
    },
)
def collect_code_tags(
    ctx: Context,
    *,
    base_dir: str = '.',
    doc_sub_dir: str = '',
    filename: Optional[str] = None,
    tag_order: str = '',
    regex: str = '',
    ignore_patterns: str = '',
    ignore_repo_root: bool = False,
) -> None:
    """Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments.

    Works in git/jj repositories (preferred) or standalone directories.
    Git blame links and timestamps available only in git repositories.
    """
    pth_base_dir = Path(base_dir).resolve()

    # Find repository root (git or jj-vcs)
    repo_root = find_repo_root(pth_base_dir)
    if not repo_root:
        LOGGER.warning(
            'Not in a repository. Using current directory as base. Git blame links will not be available.',
            base_dir=pth_base_dir,
        )
        repo_root = pth_base_dir

    # Use repo root as base directory unless ignore_repo_root flag is set
    if not ignore_repo_root:
        cwd = Path.cwd().resolve()
        if cwd != repo_root:
            LOGGER.warning(
                'Running collect_code_tags from subdirectory. Output will be relative to repository root.',
                cwd=cwd,
                repo_root=repo_root,
            )
        pth_base_dir = repo_root

    pth_docs = pth_base_dir / doc_sub_dir if doc_sub_dir else get_doc_subdir(pth_base_dir)
    if filename and '/' in filename:
        raise RuntimeError('Unexpected slash in filename. You should consider setting `--doc-sub-dir` instead')
    path_tag_summary = pth_docs / (filename or from_ctx(ctx, 'tags', 'filename'))
    patterns = (ignore_patterns or from_ctx(ctx, 'tags', 'ignore_patterns')).split(',')
    paths_source = find_project_files(pth_base_dir, ignore_patterns=[pattern for pattern in patterns if pattern])

    write_code_tag_file(
        path_tag_summary=path_tag_summary,
        paths_source=paths_source,
        base_dir=pth_base_dir,
        regex=regex,
        tags=tag_order,
        header='# Collected Code Tags',
    )
