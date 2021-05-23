"""File Helpers."""

import string

from beartype import beartype

ALLOWED_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits + '-_.'
"""Default string of acceptable characters in a filename."""


@beartype
def sanitize_filename(filename: str, repl_char: str = '_', allowed_chars: str = ALLOWED_CHARS) -> str:
    """Replace all characters not in the `allow_chars` with `repl_char`.

    Args:
        filename: string filename (stem and suffix only)
        repl_char: replacement character. Default is `_`
        allowed_chars: all allowed characters. Default is `ALLOWED_CHARS`

    Returns:
        str: sanitized filename

    """
    return ''.join((char if char in allowed_chars else repl_char) for char in filename)
