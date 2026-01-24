"""Calcipy-Invoke Defaults."""

import json
from contextlib import suppress
from pathlib import Path

from invoke.context import Context

from calcipy.collection import Collection

DEFAULTS = {
    'tags': {
        'filename': 'CODE_TAG_SUMMARY.md',
        'ignore_patterns': '',
    },
    'test': {
        'min_cover': '0',
        'out_dir': 'releases/tests',
    },
    'type': {
        'out_dir': 'releases/tests/mypy_html',
    },
}


def from_ctx(ctx: Context, group: str, key: str) -> str:
    """Safely extract the value from the context or the defaults.

    Instead of `ctx.tests.out_dir` use `from_ctx(ctx, 'test', 'out_dir')`

    Returns:
        The configuration value as a string.

    """
    with suppress(KeyError):
        return str(ctx.config[group][key])
    return str(DEFAULTS[group][key])


def new_collection() -> Collection:
    """Initialize a collection with the combination of merged and project-specific defaults.

    Returns:
        Configured Collection instance.

    """
    ns = Collection('')

    # Merge default and user configuration
    ns.configure(DEFAULTS)
    config_path = Path('.calcipy.json')
    if config_path.is_file():
        ns.configure(json.loads(config_path.read_text(encoding='utf-8')))

    return ns
