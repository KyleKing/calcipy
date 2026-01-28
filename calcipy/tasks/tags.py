"""Code Tag Collector CLI."""

from pathlib import Path

from beartype.typing import Optional
from corallium.log import LOGGER
from corallium.shell import capture_shell
from invoke.context import Context

from calcipy.cli import task
from calcipy.code_tag_collector import write_code_tag_file
from calcipy.file_search import find_project_files
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
        'ignore_patterns': 'Glob patterns to ignore files and directories when searching (Comma-separated)',
        'ignore_git_root': 'Ignore git root check and use current directory as base',
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
    ignore_git_root: bool = False,
) -> None:
    """Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments."""
    pth_base_dir = Path(base_dir).resolve()

    # Check if we're in a git repository
    try:
        git_root = Path(capture_shell('git rev-parse --show-toplevel', cwd=pth_base_dir).strip()).resolve()
    except Exception as err:
        raise RuntimeError('Not in a git repository. collect_code_tags requires git.') from err

    # Use git root as base directory unless ignore_git_root flag is set
    if not ignore_git_root:
        cwd = Path.cwd().resolve()
        if cwd != git_root:
            LOGGER.warning(
                'Running collect_code_tags from subdirectory. Output will be relative to git root.',
                cwd=cwd,
                git_root=git_root,
            )
        pth_base_dir = git_root

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
