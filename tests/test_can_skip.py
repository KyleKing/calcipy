"""Test backward compatibility shim for can_skip.

Functional tests are in the corallium repository.
"""

import importlib
import warnings

import calcipy.can_skip


def test_can_skip_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(calcipy.can_skip)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any('corallium.can_skip' in str(x.message) for x in deprecation_warnings)


def test_can_skip_reexports():
    assert callable(calcipy.can_skip.can_skip)
    assert callable(calcipy.can_skip.dont_skip)
