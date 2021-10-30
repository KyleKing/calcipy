"""Collect code tags and output for review in a single location."""

from beartype import beartype

from ..code_tag_collector import write_code_tag_file
from ..file_helpers import get_relative
from .base import debug_task
from .doit_globals import DG, DoitTask


@beartype
def task_collect_code_tags() -> DoitTask:
    """Create a summary file with all of the found code tags.

    Returns:
        DoitTask: doit task

    """
    # Filter out any files that are auto-generated and would have duplicate code tags, such as the documentation
    user_files = [pth for pth in DG.meta.paths if not get_relative(pth, DG.doc.doc_sub_dir)]
    kwargs = {
        'path_tag_summary': DG.tags.path_code_tag_summary,
        'paths_source': user_files,
        'base_dir': DG.meta.path_project,
        'regex_compiled': DG.tags.compile_issue_regex(),
        'header': f'# Task Summary\n\nAuto-Generated by `{DG.meta.pkg_name}`',
        'tag_order': DG.tags.tags,
    }
    return debug_task([(write_code_tag_file, (), kwargs)])
