"""Backward compatibility utilities."""

import warnings


def deprecated_import(old_module: str, new_module: str) -> None:
    """Emit deprecation warning at import time."""
    warnings.warn(
        f"Importing from '{old_module}' is deprecated. "
        f"Import from '{new_module}' instead.",
        DeprecationWarning,
        stacklevel=3,
    )
