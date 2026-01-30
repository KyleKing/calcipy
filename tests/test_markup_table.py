import importlib
import warnings

import calcipy.markup_table


def test_markup_table_import_emits_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        importlib.reload(calcipy.markup_table)

        deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert any('corallium.markup_table' in str(x.message) for x in deprecation_warnings)


def test_markup_table_reexports():
    assert callable(calcipy.markup_table.format_table)
