"""Calcipy-Invoke Defaults."""

from contextlib import suppress

from beartype import beartype
from invoke import Context

DEFAULTS = {
    'tags': {
        'filename': 'CODE_TAG_SUMMARY.md',
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

    Reference with `ctx.tests.out_dir` or `from_ctx(ctx, 'test', 'out_dir')`

    """
    with suppress(KeyError):
        return str(ctx.config[group][key])
    return str(DEFAULTS[group][key])
