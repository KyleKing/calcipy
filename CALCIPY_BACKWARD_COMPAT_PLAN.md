# Calcipy Backward Compatibility Plan

This plan enables calcipy to provide pass-through imports with deprecation warnings for modules that have been migrated to corallium.

## Overview

Several modules in calcipy have been migrated to corallium:
- `calcipy.can_skip` -> `corallium.can_skip`
- `calcipy.file_search` -> `corallium.file_search`
- `calcipy.markup_table` -> `corallium.markup_table`
- `calcipy.code_tag_collector` -> `corallium.code_tag_collector`
- `calcipy.experiments.sync_package_dependencies` -> `corallium.sync_dependencies`

The goal is to maintain backward compatibility by providing shim modules in calcipy that:
1. Import from corallium
2. Emit deprecation warnings when used
3. Re-export all public symbols

## Implementation Steps

### Step 1: Create a Deprecation Warning Helper

Create `calcipy/_compat.py`:

```python
"""Backward compatibility utilities."""

import warnings
from functools import wraps
from typing import Any


def deprecated_module_warning(old_module: str, new_module: str) -> None:
    """Emit a deprecation warning for module migration."""
    warnings.warn(
        f"'{old_module}' is deprecated and will be removed in a future version. "
        f"Use '{new_module}' instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def deprecated_import(old_path: str, new_path: str) -> None:
    """Emit deprecation warning at import time."""
    warnings.warn(
        f"Importing from '{old_path}' is deprecated. "
        f"Import from '{new_path}' instead.",
        DeprecationWarning,
        stacklevel=4,
    )
```

### Step 2: Update `calcipy/can_skip.py`

Replace the current content with:

```python
"""Backward compatibility shim for can_skip.

DEPRECATED: Use `corallium.can_skip` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.can_skip', 'corallium.can_skip')

from corallium.can_skip import can_skip, dont_skip

__all__ = ('can_skip', 'dont_skip')
```

### Step 3: Update `calcipy/file_search.py`

Replace the current content with:

```python
"""Backward compatibility shim for file_search.

DEPRECATED: Use `corallium.file_search` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.file_search', 'corallium.file_search')

from corallium.file_search import (
    find_project_files,
    find_project_files_by_suffix,
)

__all__ = ('find_project_files', 'find_project_files_by_suffix')
```

### Step 4: Update `calcipy/markup_table.py`

Replace the current content with:

```python
"""Backward compatibility shim for markup_table.

DEPRECATED: Use `corallium.markup_table` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import('calcipy.markup_table', 'corallium.markup_table')

from corallium.markup_table import format_table

__all__ = ('format_table',)
```

### Step 5: Update `calcipy/code_tag_collector/__init__.py`

Replace the current content with:

```python
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
except ImportError as exc:
    msg = "The 'arrow' package is required for code_tag_collector. Install with: pip install arrow"
    raise ImportError(msg) from exc

__all__ = ('CODE_TAG_RE', 'COMMON_CODE_TAGS', 'SKIP_PHRASE', 'write_code_tag_file')
```

### Step 6: Update `calcipy/code_tag_collector/_collector.py`

Replace the current content with:

```python
"""Backward compatibility shim for code_tag_collector._collector.

DEPRECATED: Use `corallium.code_tag_collector._collector` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import(
    'calcipy.code_tag_collector._collector',
    'corallium.code_tag_collector._collector'
)

from corallium.code_tag_collector._collector import (
    CODE_TAG_RE,
    COMMON_CODE_TAGS,
    SKIP_PHRASE,
    _CodeTag,
    _CollectorRow,
    _Tags,
    _format_from_blame,
    _format_record,
    _format_report,
    _git_info,
    _search_files,
    _search_lines,
    github_blame_url,
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
    '_git_info',
    '_search_files',
    '_search_lines',
    'github_blame_url',
    'write_code_tag_file',
)
```

### Step 7: Update `calcipy/experiments/sync_package_dependencies.py`

Replace the current content with:

```python
"""Backward compatibility shim for sync_package_dependencies.

DEPRECATED: Use `corallium.sync_dependencies` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import(
    'calcipy.experiments.sync_package_dependencies',
    'corallium.sync_dependencies'
)

from corallium.sync_dependencies import (
    _collect_poetry_dependencies,
    _collect_pyproject_versions,
    _collect_uv_dependencies,
    _extract_base_version,
    _handle_single_line_list,
    _is_dependency_section,
    _parse_lock_file,
    _parse_pep621_dependency,
    _replace_pep621_versions,
    _replace_poetry_versions,
    _replace_pyproject_versions,
    _try_replace_poetry_line,
    replace_versions,
)

__all__ = (
    '_collect_poetry_dependencies',
    '_collect_pyproject_versions',
    '_collect_uv_dependencies',
    '_extract_base_version',
    '_handle_single_line_list',
    '_is_dependency_section',
    '_parse_lock_file',
    '_parse_pep621_dependency',
    '_replace_pep621_versions',
    '_replace_poetry_versions',
    '_replace_pyproject_versions',
    '_try_replace_poetry_line',
    'replace_versions',
)
```

### Step 8: Update Tests

Update any calcipy tests that use the deprecated imports to verify the deprecation warnings are emitted:

```python
"""Test backward compatibility shims."""

import warnings

import pytest


def test_can_skip_deprecation_warning():
    """Verify deprecation warning is emitted for calcipy.can_skip."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from calcipy import can_skip  # noqa: F401

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "corallium.can_skip" in str(w[0].message)


def test_file_search_deprecation_warning():
    """Verify deprecation warning is emitted for calcipy.file_search."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from calcipy import file_search  # noqa: F401

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "corallium.file_search" in str(w[0].message)


# Add similar tests for other deprecated modules
```

### Step 9: Update Documentation

Add a migration guide section to calcipy's documentation:

```markdown
## Migration Guide: Calcipy to Corallium

The following modules have been migrated from `calcipy` to `corallium`:

| Old Import | New Import |
|------------|------------|
| `from calcipy.can_skip import can_skip` | `from corallium.can_skip import can_skip` |
| `from calcipy.file_search import find_project_files` | `from corallium.file_search import find_project_files` |
| `from calcipy.markup_table import format_table` | `from corallium.markup_table import format_table` |
| `from calcipy.code_tag_collector import write_code_tag_file` | `from corallium.code_tag_collector import write_code_tag_file` |
| `from calcipy.experiments.sync_package_dependencies import replace_versions` | `from corallium.sync_dependencies import replace_versions` |

The old imports will continue to work but will emit deprecation warnings.
These compatibility shims will be removed in a future major version.
```

### Step 10: Update CHANGELOG

Add to calcipy's CHANGELOG.md:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Deprecated

- `calcipy.can_skip` - Use `corallium.can_skip` instead
- `calcipy.file_search` - Use `corallium.file_search` instead
- `calcipy.markup_table` - Use `corallium.markup_table` instead
- `calcipy.code_tag_collector` - Use `corallium.code_tag_collector` instead
- `calcipy.experiments.sync_package_dependencies` - Use `corallium.sync_dependencies` instead
```

## Removal Timeline

1. **Current Release**: Add deprecation warnings (this plan)
2. **Next Minor Release**: Keep deprecation warnings, update documentation prominently
3. **Next Major Release**: Remove compatibility shims entirely

## Verification Checklist

After implementing:

- [ ] All deprecated imports emit `DeprecationWarning`
- [ ] All public symbols are re-exported correctly
- [ ] Existing calcipy tests pass (may need to suppress deprecation warnings in tests)
- [ ] New tests verify deprecation warnings are emitted
- [ ] Documentation updated with migration guide
- [ ] CHANGELOG updated

## Notes for LLM Implementation

When implementing this plan:

1. Create `calcipy/_compat.py` first
2. Update each module file one at a time
3. Run tests after each module update to ensure nothing breaks
4. The `stacklevel` parameter in warnings may need adjustment based on import depth
5. Consider using `warnings.filterwarnings` in `pytest.ini` to not fail on deprecation warnings during the transition period
