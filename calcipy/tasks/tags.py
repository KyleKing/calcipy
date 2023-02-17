"""Code Tag Collector CLI."""

import re
from pathlib import Path

from beartype.typing import Optional
from invoke import Context
from shoal import get_logger
from shoal.cli import task

from ..code_tag_collector import CODE_TAG_RE, COMMON_CODE_TAGS, write_code_tag_file
from ..file_search import find_project_files
from .defaults import from_ctx

logger = get_logger()

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
        regex: str = CODE_TAG_RE,
        ignore_patterns: str = '',
    ) -> None:
    """Create a `CODE_TAG_SUMMARY.md` with a table for TODO- and FIXME-style code comments."""
    pth_base_dir = Path(base_dir).resolve()
    path_tag_summary = Path(filename or from_ctx(ctx, 'tags', 'filename')).resolve()
    patterns = ignore_patterns.split(',') if ignore_patterns else []
    paths_source = find_project_files(pth_base_dir, ignore_patterns=patterns)
    regex_compiled = re.compile(regex.format(tag='|'.join(tag_order)))

    write_code_tag_file(
        path_tag_summary=path_tag_summary,
        paths_source=paths_source,
        base_dir=pth_base_dir,
        regex_compiled=regex_compiled,
        tag_order=tag_order.split(',') or COMMON_CODE_TAGS,
        header='# Collected Code Tags',
    )
    logger.info('Created Code Tag Summary', path_tag_summary=path_tag_summary)
