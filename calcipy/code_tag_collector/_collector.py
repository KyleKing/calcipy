"""Backward compatibility shim for code_tag_collector._collector.

DEPRECATED: Use `corallium.code_tag_collector._collector` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import(
    'calcipy.code_tag_collector._collector',
    'corallium.code_tag_collector._collector',
)

from corallium.code_tag_collector._collector import (  # noqa: E402
    CODE_TAG_RE,
    COMMON_CODE_TAGS,
    SKIP_PHRASE,
    _CodeTag,
    _CollectorRow,
    _format_from_blame,
    _format_record,
    _format_report,
    _search_files,
    _search_lines,
    _Tags,
    write_code_tag_file,
)

__all__ = (
    'CODE_TAG_RE',
    'COMMON_CODE_TAGS',
    'SKIP_PHRASE',
    '_CodeTag',
    '_CollectorRow',
    '_Tags',
    '_format_from_blame',
    '_format_record',
    '_format_report',
    '_search_files',
    '_search_lines',
    'write_code_tag_file',
)
