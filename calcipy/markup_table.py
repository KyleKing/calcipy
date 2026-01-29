"""Backward compatibility shim for markup_table.

DEPRECATED: Use `corallium.markup_table` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.markup_table', 'corallium.markup_table')

from corallium.markup_table import format_table  # noqa: E402

__all__ = ('format_table',)
