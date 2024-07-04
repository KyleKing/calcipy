"""Check that all imports work as expected in the built package."""

from pprint import pprint

from calcipy.invoke_helpers import get_doc_subdir, get_project_path

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
    from calcipy.md_writer import write_template_formatted_md_sections
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.noxfile import build_check, build_dist, tests
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise

try:
    from calcipy.tasks.all_tasks import ns
except RuntimeError as exc:
    if 'extras' not in str(exc):
        raise


pprint(locals())  # noqa: T203
