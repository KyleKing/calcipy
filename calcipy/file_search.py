"""Backward compatibility shim for file_search.

DEPRECATED: Use `corallium.file_search` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.file_search', 'corallium.file_search')

from corallium.file_search import (  # noqa: E402
    _filter_files,
    _get_all_files,
    _get_default_ignore_patterns,
    _walk_files,
    find_project_files,
    find_project_files_by_suffix,
)

__all__ = (
    '_filter_files',
    '_get_all_files',
    '_get_default_ignore_patterns',
    '_walk_files',
    'find_project_files',
    'find_project_files_by_suffix',
)
