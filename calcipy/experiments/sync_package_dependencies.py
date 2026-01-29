"""Backward compatibility shim for sync_package_dependencies.

DEPRECATED: Use `corallium.sync_dependencies` instead.
"""

from calcipy._compat import deprecated_import

deprecated_import(
    'calcipy.experiments.sync_package_dependencies',
    'corallium.sync_dependencies',
)

from corallium.sync_dependencies import (  # noqa: E402
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
