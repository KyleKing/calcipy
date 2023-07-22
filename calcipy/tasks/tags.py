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
        'filename': 'Code Tag Summary Filename',
        'tag_order': 'Ordered list of code tags to locate (Comma-separated)',
        'regex': 'Custom Code Tag Regex. Must contain "{tag}"',
        'ignore_patterns': 'Glob patterns to ignore files and directories when searching (Comma-separated)',
    },
)
def collect_code_tags(
    ctx: Context,
    base_dir: str = '.',
    filename: Optional[str] = None,
    tag_order: str = '',
    regex: str = '',
    ignore_patterns: str = '',
) -> None:
    """Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments."""
    pth_base_dir = Path(base_dir).resolve()
    path_tag_summary = get_doc_subdir() / (filename or from_ctx(ctx, 'tags', 'filename'))
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
