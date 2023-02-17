"""Invoke Defaults."""

from contextlib import suppress

from beartype import beartype
from invoke import Context

# Docs: https://docs.pyinvoke.org/en/stable/concepts/configuration.html#configuring-via-task-collection
# 	Can be overriden in `invoke.yaml`: https://docs.pyinvoke.org/en/stable/concepts/configuration.html#config-hierarchy

# FYI: reference with `ctx.tests.out_dir` or `from_ctx(ctx, 'tests', 'out_dir')`
DEFAULTS = {
	'tags': {
		'filename': 'docs/docs/CODE_TAG_SUMMARY.md',
	},
	'tests': {
		'out_dir': 'releases/tests',
	},
	'types': {
		'out_dir': 'releases/tests/mypy_html',
	},
}


@beartype
def from_ctx(ctx: Context, group: str, key: str) -> str:
	"""Safely extract the value from the context or the defaults."""
	with suppress(Exception):
		return str(ctx.getattr(group).getattr(key))
	return str(DEFAULTS[group][key])
