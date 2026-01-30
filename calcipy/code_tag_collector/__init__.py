"""Backward compatibility shim for code_tag_collector.

DEPRECATED: Use `corallium.code_tag_collector` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.code_tag_collector', 'corallium.code_tag_collector')

try:
    from corallium.code_tag_collector import (
        CODE_TAG_RE,
        COMMON_CODE_TAGS,
        SKIP_PHRASE,
        write_code_tag_file,
    )
except ImportError as exc:  # pragma: no cover
    msg = "The 'arrow' package is required for code_tag_collector. Install with: pip install arrow"
    raise ImportError(msg) from exc

__all__ = ('CODE_TAG_RE', 'COMMON_CODE_TAGS', 'SKIP_PHRASE', 'write_code_tag_file')
