from unittest.mock import call

import pytest


@pytest.fixture
def assert_run_commands():
    def _check(ctx, commands):
        ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])

    return _check
