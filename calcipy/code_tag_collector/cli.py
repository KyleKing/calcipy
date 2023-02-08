"""Code Tag Collector CLI."""

import re
from pathlib import Path
from typing import Dict, List, Tuple

from beartype import beartype
from shoal import get_logger, register_fun
from ._collector import CODE_TAG_RE, COMMON_CODE_TAGS, write_code_tag_file
from ..file_search import find_project_files

logger = get_logger()


@beartype
def collect_code_tags(argv: List[str]) -> None:
    """Create a `CODE_TAG_SUMMARY.md` with a table for TODO and FIXME comments."""
    base_dir = Path()
    path_tag_summary = Path('CODE_TAG_SUMMARY.md').resolve()
    paths_source = find_project_files(base_dir, ignore_patterns=[])
    tag_order = COMMON_CODE_TAGS
    regex_compiled = re.compile(CODE_TAG_RE.format(tag='|'.join(tag_order)))

    write_code_tag_file(
        path_tag_summary=path_tag_summary,
        paths_source=paths_source,
        base_dir=base_dir,
        regex_compiled=regex_compiled,
        tag_order=tag_order,
        header='# Collected Code Tags',
    )
    logger.info(f'Created: {path_tag_summary}')


@beartype
def load() -> None:
	register_fun(collect_code_tags)
