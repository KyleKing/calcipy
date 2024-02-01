"""Code Tag Collector CLI."""

from pathlib import Path

from beartype.typing import Optional
from invoke.context import Context

from ..cli import task
from ..code_tag_collector import write_code_tag_file
from ..file_search import find_project_files
from ..invoke_helpers import get_doc_subdir
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
    },
)
def collect_code_tags(  # noqa: PLR0913,PLR0917
    ctx: Context,
    base_dir: str = '.',
    doc_sub_dir: str = '',
    filename: Optional[str] = None,
    tag_order: str = '',
    regex: str = '',
    ignore_patterns: str = '',
) -> None:
    """Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments."""
    pth_base_dir = Path(base_dir).resolve()
    pth_docs = pth_base_dir / doc_sub_dir if doc_sub_dir else get_doc_subdir()
    if filename and '/' in filename:
        raise RuntimeError('Unexpected slash in filename. You should consider setting `--doc-sub-dir` instead')
    path_tag_summary = pth_docs / (filename or from_ctx(ctx, 'tags', 'filename'))
    patterns = (ignore_patterns or from_ctx(ctx, 'tags', 'ignore_patterns')).split(',')
    paths_source = find_project_files(pth_base_dir, ignore_patterns=[*filter(lambda item: item, patterns)])

    write_code_tag_file(
        path_tag_summary=path_tag_summary,
        paths_source=paths_source,
        base_dir=pth_base_dir,
        regex=regex,
        tags=tag_order,
        header='# Collected Code Tags',
    )
