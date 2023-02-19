# noqa: INP001
"""Check that all imports work as expected in the built package."""

from pprint import pprint

from calcipy.file_helpers import (
    COPIER_ANSWERS,
    LOCK,
    MKDOCS_CONFIG,
    PROJECT_TOML,
    delete_dir,
    delete_old_files,
    ensure_dir,
    get_doc_dir,
    get_project_path,
    get_relative,
    get_tool_versions,
    if_found_unlink,
    open_in_browser,
    read_lines,
    read_package_name,
    read_pyproject,
    read_yaml_file,
    sanitize_filename,
    tail_lines,
    trim_trailing_whitespace,
)
from calcipy.invoke_helpers import use_pty

try:
    from calcipy.check_for_stale_packages import check_for_stale_packages
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.code_tag_collector import write_code_tag_file
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.dot_dict import ddict
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.file_search import find_project_files, find_project_files_by_suffix
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.md_writer import write_autoformatted_md_sections
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.noxfile import build_check, build_dist, coverage, tests
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.tasks.all_tasks import ns
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise


pprint(locals())  # noqa: T203
