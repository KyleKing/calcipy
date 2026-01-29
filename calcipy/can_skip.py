"""Backward compatibility shim for can_skip.

DEPRECATED: Use `corallium.can_skip` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.can_skip', 'corallium.can_skip')

from corallium.can_skip import can_skip, dont_skip  # noqa: E402

__all__ = ('can_skip', 'dont_skip')
