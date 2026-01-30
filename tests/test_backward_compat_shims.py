"""Test backward compatibility shims.

Functional tests are in the corallium repository.
"""

import importlib
import warnings

import pytest

_SHIM_PARAMS = [
    pytest.param(
        'calcipy.can_skip',
        'corallium.can_skip',
        [('can_skip', None), ('dont_skip', None)],
        id='can_skip',
    ),
    pytest.param(
        'calcipy.code_tag_collector',
        'corallium.code_tag_collector',
        [('write_code_tag_file', None), ('CODE_TAG_RE', str)],
        id='code_tag_collector',
    ),
    pytest.param(
        'calcipy.code_tag_collector._collector',
        'corallium.code_tag_collector._collector',
        [('write_code_tag_file', None), ('_search_files', None), ('_format_from_blame', None)],
        id='code_tag_collector._collector',
    ),
    pytest.param(
        'calcipy.experiments.sync_package_dependencies',
        'corallium.sync_dependencies',
        [('replace_versions', None), ('_extract_base_version', None)],
        id='sync_package_dependencies',
    ),
    pytest.param(
        'calcipy.file_search',
        'corallium.file_search',
        [('find_project_files', None), ('find_project_files_by_suffix', None)],
        id='file_search',
    ),
    pytest.param(
        'calcipy.markup_table',
        'corallium.markup_table',
        [('format_table', None)],
        id='markup_table',
    ),
]


def _assert_deprecation_warning(module, target):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(module)
        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any(target in str(x.message) for x in deprecation_warnings)


def _assert_reexports(module, reexports):
    for attr, expected_type in reexports:
        obj = getattr(module, attr)
        if expected_type is None:
            assert callable(obj)
        else:
            assert isinstance(obj, expected_type)


@pytest.mark.parametrize(('module_path', 'target', 'reexports'), _SHIM_PARAMS)
def test_backward_compat_shim(module_path, target, reexports):
    module = importlib.import_module(module_path)
    _assert_deprecation_warning(module, target)
    _assert_reexports(module, reexports)


# calcipy_skip_tags
