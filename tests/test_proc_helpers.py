"""Test proc_helpers."""

from subprocess import CalledProcessError  # nosec

import pytest
from calcipy.proc_helpers import run_cmd


def test_run_cmd():
    """Test run_cmd."""
    with pytest.raises(CalledProcessError):
        run_cmd('gibberish')
