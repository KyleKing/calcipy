"""Test backward compatibility shim for sync_package_dependencies.

Functional tests are in the corallium repository.
"""

import importlib
import warnings

import calcipy.experiments.sync_package_dependencies


def test_sync_package_dependencies_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(calcipy.experiments.sync_package_dependencies)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any('corallium.sync_dependencies' in str(x.message) for x in deprecation_warnings)


def test_sync_package_dependencies_reexports():
    assert callable(calcipy.experiments.sync_package_dependencies.replace_versions)
    assert callable(calcipy.experiments.sync_package_dependencies._extract_base_version)  # noqa: SLF001
