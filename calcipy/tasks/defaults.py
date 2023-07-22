"""Calcipy-Invoke Defaults."""

import json
from contextlib import suppress
from pathlib import Path

from beartype import beartype
from invoke.collection import Collection
from invoke.context import Context

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


@beartype
def from_ctx(ctx: Context, group: str, key: str) -> str:
    """Safely extract the value from the context or the defaults.

    Instead of `ctx.tests.out_dir` use `from_ctx(ctx, 'test', 'out_dir')`

    """
    with suppress(KeyError):
        return str(ctx.config[group][key])
    return str(DEFAULTS[group][key])


@beartype
def new_collection() -> Collection:
    """Initialize a collection with the combination of merged and project-specific defaults."""
    ns = Collection('')

    # Merge default and user configuration
    ns.configure(DEFAULTS)
    config_path = Path('.calcipy.json')
    if config_path.is_file():
        ns.configure(json.loads(config_path.read_text(encoding='utf-8')))

    return ns
