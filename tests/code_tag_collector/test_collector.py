"""Test backward compatibility shim for code_tag_collector.

Functional tests are in the corallium repository.
"""

import importlib
import warnings

import calcipy.code_tag_collector


def test_code_tag_collector_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(calcipy.code_tag_collector)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any('corallium.code_tag_collector' in str(x.message) for x in deprecation_warnings)


def test_code_tag_collector_reexports():
    assert callable(calcipy.code_tag_collector.write_code_tag_file)
    assert isinstance(calcipy.code_tag_collector.CODE_TAG_RE, str)


def test_code_tag_collector_submodule_import_emits_deprecation_warning():
    import calcipy.code_tag_collector._collector  # noqa: PLC0415

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(calcipy.code_tag_collector._collector)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any('corallium.code_tag_collector._collector' in str(x.message) for x in deprecation_warnings)


def test_code_tag_collector_submodule_reexports():
    import calcipy.code_tag_collector._collector as collector  # noqa: PLC0415

    assert callable(collector.write_code_tag_file)
    assert callable(collector._search_files)
    assert callable(collector._format_from_blame)


# calcipy_skip_tags
