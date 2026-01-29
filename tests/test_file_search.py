"""Test backward compatibility shim for file_search.

Functional tests are in the corallium repository.
"""

import importlib
import warnings

import calcipy.file_search


def test_file_search_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(calcipy.file_search)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any('corallium.file_search' in str(x.message) for x in deprecation_warnings)


def test_file_search_reexports():
    assert callable(calcipy.file_search.find_project_files)
    assert callable(calcipy.file_search.find_project_files_by_suffix)
